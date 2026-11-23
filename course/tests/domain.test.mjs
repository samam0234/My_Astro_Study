import test from 'node:test';
import assert from 'node:assert/strict';
import { openStore } from '../src/lib/store.mjs';
import { signup, login, authenticate, hashPassword, checkPassword } from '../src/lib/auth.mjs';
import { createPost, updatePost, deletePost, listPosts } from '../src/lib/posts.mjs';
import { listQuery } from '../src/lib/validation.mjs';
import { ttlCache } from '../src/lib/cache.mjs';
import { generate, retrieve } from '../src/lib/ai.mjs';
import { enqueueMail, workOnce } from '../src/lib/jobs.mjs';
import { sendMail, checkout } from '../src/lib/integrations.mjs';
import { fakeStore } from './fake-store.mjs';

test('서비스는 DB 대신 fake 저장 계약을 주입할 수 있다', async () => {
  const store = fakeStore();
  const user = await store.create('users', { nickname: '가짜 사용자' });
  const post = await createPost(store, user, { title: '가짜 DB', body: '네트워크·파일 없음' });
  assert.equal(post.author.nickname, user.nickname);
  assert.equal((await listPosts(store, new URL('http://local/'))).meta.total, 1);
});

test('scrypt: 같은 비밀번호도 salt가 다르고 잘못된 비밀번호는 거절', async () => {
  const a = await hashPassword('study-password'), b = await hashPassword('study-password');
  assert.notEqual(a, b); assert.equal(await checkPassword('study-password', a), true); assert.equal(await checkPassword('wrong', a), false);
});
test('DB + 인증 + 작성자 권한 + 부분수정 + 검색/페이지 계약', async () => {
  const store = await openStore({ driver: 'sqlite', database: ':memory:' });
  try {
    const mina = await signup(store, { email: 'mina@example.com', nickname: '미나', password: 'study-password' });
    const other = await signup(store, { email: 'other@example.com', nickname: '다른 사람', password: 'study-password' });
    await assert.rejects(signup(store, { email: mina.email, nickname: '중복', password: 'study-password' }), e => e.status === 409);
    const session = await login(store, { email: mina.email, password: 'study-password' });
    assert.equal((await authenticate(store, session.accessToken)).id, mina.id);
    assert.equal(await authenticate(store, 'forged'), null);
    const post = await createPost(store, mina, { title: 'Astro', body: 'Hello', tags: ['keep'] });
    await assert.rejects(updatePost(store, other, post.id, { title: '탈취' }), e => e.status === 403);
    const changed = await updatePost(store, mina, post.id, { body: 'Changed' });
    assert.deepEqual(changed.tags, ['keep']); assert.equal(changed.title, 'Astro');
    assert.equal((await listPosts(store, new URL('http://local/?q=ASTRO&limit=99'))).meta.limit, 50);
    assert.equal((await listPosts(store, new URL('http://local/?q=absent'))).meta.total, 0);
    await assert.rejects(createPost(store, null, { title: 'x', body: 'y' }), e => e.status === 401);
    await deletePost(store, mina, post.id); assert.equal(await store.get('posts', post.id), null);
  } finally { await store.close(); }
});
test('목록 입력 검증: 음수/소수/잘못된 정렬 거절', () => {
  for (const query of ['page=0', 'page=1.5', 'limit=-1', 'limit=0', 'sort=sql']) assert.throws(() => listQuery(new URL(`http://local/?${query}`)));
});
test('세션 만료', async () => {
  const store = await openStore({ driver: 'sqlite', database: ':memory:' });
  try {
    const u = await signup(store, { email: 'expire@example.com', nickname: '만료', password: 'study-password' });
    const loginResult = await login(store, { email: u.email, password: 'study-password' });
    const [session] = await store.list('sessions'); await store.replace('sessions', session.id, { ...session, expiresAt: 0 });
    assert.equal(await authenticate(store, loginResult.accessToken), null);
  } finally { await store.close(); }
});
test('캐시 값 격리와 무효화', async () => {
  const cache = ttlCache(); let calls = 0;
  const load = async () => ({ number: ++calls });
  (await cache.get('key', load)).number = 99;
  assert.equal((await cache.get('key', load)).number, 1);
  cache.clear(); assert.equal((await cache.get('key', load)).number, 2);
});
test('외부 서비스 mock은 실제 결제/메일을 완료했다고 표시하지 않는다', async () => {
  const fetcher = () => { throw new Error('네트워크가 호출되면 실패'); };
  assert.equal((await sendMail({ email: 'a@b.com' }, { INTEGRATIONS_MODE: 'mock' }, fetcher)).delivered, false);
  assert.equal((await checkout({ id: 1 }, 'http://local', { INTEGRATIONS_MODE: 'mock' })).paid, false);
});
test('메일 API를 가짜 fetch로 바꾸고 HTTP 실패를 검출', async () => {
  let requested;
  const fake = async (url, init) => { requested = { url, init }; return Response.json({ id: 'test' }); };
  await sendMail({ email: 'a@b.com' }, { INTEGRATIONS_MODE: 'live', RESEND_API_KEY: 'fake', MAIL_FROM: 'a@b.com' }, fake);
  assert.equal(JSON.parse(requested.init.body).to[0], 'a@b.com');
  await assert.rejects(sendMail({ email: 'a@b.com' }, { INTEGRATIONS_MODE: 'live', RESEND_API_KEY: 'fake', MAIL_FROM: 'a@b.com' }, async () => new Response('', { status: 500 })), e => e.status === 502);
});
test('배경 작업 실패는 재시도하고 세 번째 실패 뒤 종료', async () => {
  const store = await openStore({ driver: 'sqlite', database: ':memory:' });
  try {
    await enqueueMail(store, { id: 1 });
    for (let n = 0; n < 3; n++) {
      const [job] = await store.list('jobs'); await store.replace('jobs', job.id, { ...job, nextAt: 0 });
      await workOnce(store, async () => { throw new Error('모의 장애'); });
    }
    assert.equal((await store.list('jobs'))[0].status, 'failed');
  } finally { await store.close(); }
});
test('검색 근거가 없으면 찾을 수 없음, 있으면 발췌 번호', async () => {
  assert.equal(retrieve('Astro 콘텐츠', 'database').length, 0);
  let text = ''; for await (const token of generate('Astro 콘텐츠', 'Astro', { env: { AI_MODE: 'mock' } })) text += token;
  assert.match(text, /발췌 1/);
});
test('AI upstream SSE는 한글 UTF-8/이벤트가 쪼개져도 합쳐진다', async () => {
  const bytes = new TextEncoder().encode('data: {"choices":[{"delta":{"content":"한글"}}]}\n\ndata: [DONE]\n\n');
  let i = 0;
  const fetcher = async () => new Response(new ReadableStream({ pull(c) { if (i === bytes.length) c.close(); else c.enqueue(bytes.slice(i, ++i)); } }));
  let text = ''; for await (const token of generate('text', '', { env: { AI_MODE: 'live', AI_API_KEY: 'fake' }, fetcher })) text += token;
  assert.equal(text, '한글');
});
