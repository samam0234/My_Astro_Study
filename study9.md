# study9 · 테스트·디버깅

## ① 목표 한 줄

단위·요청·브라우저 테스트와 mock으로 경계를 검증한다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

단위 테스트는 한 규칙을 빠르게 확인하고, HTTP 테스트는 실제 요청·쿠키·헤더·직렬화를 확인한다. 브라우저 테스트는 폼 이벤트와 화면 표시까지 확인한다. 단위 테스트만으로 DOM 버튼이 작동한다고 말할 수 없고, 화면만으로 DB에 저장됐다고 말할 수도 없다.

mock은 연습용 대역이다. AI·메일에는 fetcher/전송 함수를 주입하고, DB는 fakeStore로 바꾼다. 통합 검사는 메모리 SQLite와 실제 파일 DB로 별도 실행해 mock이 숨기는 오류를 줄인다. 이번 테스트가 잡은 사례는 PATCH에서 tags 기본값이 기존 태그를 덮는 오류다. 부분수정 스키마에서 tags의 default를 제거해 고쳤다.

## ③ 🛠️ 실기

`course/`에서 실행한다.

```powershell
npm test
npm run build
npm run test:http
npx playwright install chromium
npx playwright test
```

1행은 도메인 규칙과 mock, 2행은 실제 배포 산출물, 3행은 임시 DB·포트 4393의 실제 서버, 4행은 브라우저 설치, 5행은 포트 4394의 실제 사용자 흐름이다. 테스트 서버는 사용자의 기본 DB를 재사용하지 않는다. HTTP 검증은 임시 디렉터리를 만들고 종료 시 지운다. 브라우저 테스트 DB는 무시되는 `course/data/e2e.sqlite`다.

VS Code JavaScript Debug Terminal에서 `npm start`를 실행하고 서버 handler에 breakpoint를 건다. 브라우저 Sources에서는 script 모듈과 fetch 지점을 확인한다. 401은 세션, 403은 권한/Origin, 400은 입력, 500은 서버 로그로 범위를 줄인다.

### `course/tests/fake-store.mjs` 전체 코드

[fake-store.mjs](course/tests/fake-store.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
export function fakeStore() {
  const records = new Map(); let sequence = 0;
  return {
    async create(kind, value) { const row = structuredClone({ ...value, id: ++sequence }); records.set(`${kind}:${row.id}`, row); return structuredClone(row); },
    async list(kind) { return [...records.entries()].filter(([key]) => key.startsWith(`${kind}:`)).map(([, value]) => structuredClone(value)); },
    async get(kind, id) { return structuredClone(records.get(`${kind}:${id}`) || null); },
    async replace(kind, id, value) { records.set(`${kind}:${id}`, structuredClone({ ...value, id })); },
    async remove(kind, id) { records.delete(`${kind}:${id}`); },
    async close() {},
  };
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 재사용 함수 `fakeStore`를 정의한다. |
| 2 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const records`. |
| 3 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 4 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `async create(kind, value) { const row = structuredClone({ ...value, id: ++sequence }); records.set(${kind}:${r`. |
| 5 | 목록의 각 항목을 화면 또는 응답에 필요한 모양으로 변환한다. |
| 6 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `async get(kind, id) { return structuredClone(records.get(${kind}:${id}) &#124;&#124; null); },`. |
| 7 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `async replace(kind, id, value) { records.set(${kind}:${id}, structuredClone({ ...value, id })); },`. |
| 8 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `async remove(kind, id) { records.delete(${kind}:${id}); },`. |
| 9 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `async close() {},`. |
| 10 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 11 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/tests/domain.test.mjs` 전체 코드

[domain.test.mjs](course/tests/domain.test.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
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
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'node:test'`의 기능을 이 파일에서 사용한다. |
| 2 | `'node:assert/strict'`의 기능을 이 파일에서 사용한다. |
| 3 | `'../src/lib/store.mjs'`의 기능을 이 파일에서 사용한다. |
| 4 | `'../src/lib/auth.mjs'`의 기능을 이 파일에서 사용한다. |
| 5 | `'../src/lib/posts.mjs'`의 기능을 이 파일에서 사용한다. |
| 6 | `'../src/lib/validation.mjs'`의 기능을 이 파일에서 사용한다. |
| 7 | `'../src/lib/cache.mjs'`의 기능을 이 파일에서 사용한다. |
| 8 | `'../src/lib/ai.mjs'`의 기능을 이 파일에서 사용한다. |
| 9 | `'../src/lib/jobs.mjs'`의 기능을 이 파일에서 사용한다. |
| 10 | `'../src/lib/integrations.mjs'`의 기능을 이 파일에서 사용한다. |
| 11 | `'./fake-store.mjs'`의 기능을 이 파일에서 사용한다. |
| 12 | 코드 구간을 나누는 빈 줄이다. |
| 13 | 독립적으로 확인할 테스트 시나리오를 정의한다. |
| 14 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const store`. |
| 15 | 저장소 계약으로 새 레코드를 생성하며 생성 id를 받는다. |
| 16 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const post`. |
| 17 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 18 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 19 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 20 | 코드 구간을 나누는 빈 줄이다. |
| 21 | 독립적으로 확인할 테스트 시나리오를 정의한다. |
| 22 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const a`. |
| 23 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 24 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 25 | 독립적으로 확인할 테스트 시나리오를 정의한다. |
| 26 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const store`. |
| 27 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `try {`. |
| 28 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const mina`. |
| 29 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const other`. |
| 30 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 31 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const session`. |
| 32 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 33 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 34 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const post`. |
| 35 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 36 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const changed`. |
| 37 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 38 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 39 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 40 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 41 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 42 | 성공·실패에 관계없이 연결/잠금 등 정리 작업을 실행한다. |
| 43 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 44 | 독립적으로 확인할 테스트 시나리오를 정의한다. |
| 45 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 46 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 47 | 독립적으로 확인할 테스트 시나리오를 정의한다. |
| 48 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const store`. |
| 49 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `try {`. |
| 50 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const u`. |
| 51 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const loginResult`. |
| 52 | 검증한 변경 값을 지정 레코드에 저장한다. |
| 53 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 54 | 성공·실패에 관계없이 연결/잠금 등 정리 작업을 실행한다. |
| 55 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 56 | 독립적으로 확인할 테스트 시나리오를 정의한다. |
| 57 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const cache`. |
| 58 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const load`. |
| 59 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `(await cache.get('key', load)).number = 99;`. |
| 60 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 61 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 62 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 63 | 독립적으로 확인할 테스트 시나리오를 정의한다. |
| 64 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const fetcher`. |
| 65 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 66 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 67 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 68 | 독립적으로 확인할 테스트 시나리오를 정의한다. |
| 69 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let requested;`. |
| 70 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 71 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await sendMail({ email: 'a@b.com' }, { INTEGRATIONS_MODE: 'live', RESEND_API_KEY: 'fake', MAIL_FROM: 'a@b.com'`. |
| 72 | JSON 문자열을 객체로 해석한다. 잘못된 입력은 상위 오류 처리로 넘긴다. |
| 73 | 응답 본문·상태·헤더 또는 스트림을 담은 HTTP Response를 만든다. |
| 74 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 75 | 독립적으로 확인할 테스트 시나리오를 정의한다. |
| 76 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const store`. |
| 77 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `try {`. |
| 78 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await enqueueMail(store, { id: 1 });`. |
| 79 | 목록 또는 스트림의 남은 항목을 순서대로 처리한다. |
| 80 | 검증한 변경 값을 지정 레코드에 저장한다. |
| 81 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await workOnce(store, async () => { throw new Error('모의 장애'); });`. |
| 82 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 83 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 84 | 성공·실패에 관계없이 연결/잠금 등 정리 작업을 실행한다. |
| 85 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 86 | 독립적으로 확인할 테스트 시나리오를 정의한다. |
| 87 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 88 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let text`. |
| 89 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 90 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 91 | 독립적으로 확인할 테스트 시나리오를 정의한다. |
| 92 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const bytes`. |
| 93 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let i`. |
| 94 | 응답 본문·상태·헤더 또는 스트림을 담은 HTTP Response를 만든다. |
| 95 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let text`. |
| 96 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 97 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/scripts/smoke.mjs` 전체 코드

[smoke.mjs](course/scripts/smoke.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve, sep } from 'node:path';
const directory = await mkdtemp(join(tmpdir(), 'astro-contract-'));
assert.ok(resolve(directory).startsWith(resolve(tmpdir()) + sep) && directory.includes('astro-contract-'));
const base = 'http://127.0.0.1:4393'; let token = '', other = '', count = 0, logs = '';
const child = spawn(process.execPath, ['dist/server/entry.mjs'], { env: { ...process.env, HOST: '127.0.0.1', PORT: '4393', SITE_URL: base, CORS_ORIGIN: base, DATABASE_URL: join(directory, 'test.sqlite'), DB_DRIVER: 'sqlite', AI_MODE: 'mock', INTEGRATIONS_MODE: 'mock', RELEASE_SHA: 'smoke-revision' }, stdio: ['ignore', 'pipe', 'pipe'] });
child.stdout.on('data', b => { logs += b; }); child.stderr.on('data', b => { logs += b; });
async function call(path, method = 'GET', value, status = 200, auth = token, headers = {}) {
  const response = await fetch(base + path, { method, headers: { 'Content-Type': 'application/json', ...(auth ? { Authorization: `Bearer ${auth}` } : {}), ...headers }, ...(value !== undefined ? { body: typeof value === 'string' ? value : JSON.stringify(value) } : {}) });
  assert.equal(response.status, status, `${method} ${path}: ${await response.clone().text()}`);
  const result = status === 204 ? null : await response.json();
  if (status >= 400) { assert.ok(result.error.code); assert.equal(result.error.requestId, response.headers.get('x-request-id')); }
  count++; return { result, response };
}
try {
  let ready = false;
  for (let i = 0; i < 80; i++) { try { const r = await fetch(base + '/health'); if (r.ok) { ready = true; break; } } catch {} await new Promise(r => setTimeout(r, 100)); }
  assert.ok(ready, logs);
  assert.equal((await call('/health')).response.headers.get('x-release-sha'), 'smoke-revision');
  await call('/api/missing', 'GET', undefined, 404);
  const signup = { email: 'mina@example.com', password: 'study-password', nickname: '미나' };
  await call('/api/auth/signup', 'POST', signup, 201);
  await call('/api/auth/signup', 'POST', signup, 409);
  await call('/api/auth/login', 'POST', { email: signup.email, password: 'bad-password' }, 401);
  const logged = await call('/api/auth/login', 'POST', { email: signup.email, password: signup.password }); token = logged.result.data.accessToken;
  assert.match(logged.response.headers.get('set-cookie'), /HttpOnly/i);
  await call('/api/auth/me');
  const cookieResult = await call('/api/auth/me', 'GET', undefined, 200, '', { Cookie: `desk_session=${token}` });
  assert.equal(cookieResult.result.data.email, signup.email);
  await call('/api/posts', 'POST', { title: '', body: 'x' }, 400);
  await call('/api/posts', 'POST', '{', 400);
  await call('/api/posts', 'POST', { title: 'x', body: 'y' }, 401, '');
  await call('/api/posts', 'POST', { title: 'x', body: 'y' }, 403, token, { Origin: 'https://evil.example' });
  const created = await call('/api/posts', 'POST', { title: 'Astro XSS <script>', body: '한글 본문', tags: ['astro'] }, 201);
  const id = created.result.data.id; assert.equal(created.response.headers.get('location'), `/api/posts/${id}`);
  const listing = (await call('/api/posts?q=astro&page=1&limit=100')).result;
  assert.equal(listing.meta.total, 1); assert.equal(listing.meta.limit, 50); assert.equal(listing.meta.totalPages, 1);
  await call('/api/posts?page=0', 'GET', undefined, 400);
  await call(`/api/posts/${id}`); await call('/api/posts/no-number', 'GET', undefined, 400);
  await call(`/api/posts/${id}`, 'PATCH', { body: '변경' });
  await call('/api/auth/signup', 'POST', { ...signup, email: 'other@example.com' }, 201);
  other = (await call('/api/auth/login', 'POST', { email: 'other@example.com', password: signup.password })).result.data.accessToken;
  await call(`/api/posts/${id}`, 'PATCH', { title: '탈취' }, 403, other);
  const comment = (await call(`/api/posts/${id}/comments`, 'POST', { body: '댓글' }, 201)).result.data;
  assert.equal((await call('/api/posts')).result.data[0].commentCount, 1);
  await call(`/api/comments/${comment.id}`, 'DELETE', undefined, 403, other);
  await call(`/api/comments/${comment.id}`, 'DELETE', undefined, 204);
  const doc = (await call('/api/documents', 'POST', { name: 'study.md', text: 'Astro 콘텐츠를 배웁니다.' }, 201)).result.data;
  await call(`/api/documents/${doc.id}/download`, 'GET', undefined, 403, other);
  const stream = await fetch(base + '/api/ai', { method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ documentId: doc.id, question: 'Astro' }) });
  assert.equal(stream.status, 200); assert.match(await stream.text(), /delta/); count++;
  await call('/api/mail', 'POST', {}, 202);
  assert.equal((await call('/api/checkout', 'POST', { key: crypto.randomUUID() })).result.data.paid, false);
  await call(`/api/posts/${id}`, 'DELETE', undefined, 204);
  await call(`/api/posts/${id}`, 'GET', undefined, 404);
  await call('/api/auth/logout', 'POST', {}, 204); await call('/api/auth/me', 'GET', undefined, 401);
  console.log(`HTTP 계약 ${count}개 통과`);
} catch (error) { console.error(logs); throw error; }
finally { child.kill(); await new Promise(r => child.once('exit', r)); await rm(directory, { recursive: true, force: true }); }
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'node:assert/strict'`의 기능을 이 파일에서 사용한다. |
| 2 | `'node:child_process'`의 기능을 이 파일에서 사용한다. |
| 3 | `'node:fs/promises'`의 기능을 이 파일에서 사용한다. |
| 4 | `'node:os'`의 기능을 이 파일에서 사용한다. |
| 5 | `'node:path'`의 기능을 이 파일에서 사용한다. |
| 6 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const directory`. |
| 7 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 8 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const base`. |
| 9 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 10 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `child.stdout.on('data', b => { logs += b; }); child.stderr.on('data', b => { logs += b; });`. |
| 11 | 비동기 함수 `call`의 입력과 처리 범위를 정의한다. |
| 12 | HTTP 요청을 보내 응답을 기다린다. 주입된 fetcher는 테스트에서 대체할 수 있다. |
| 13 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 14 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const result`. |
| 15 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 16 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `count++; return { result, response };`. |
| 17 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 18 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `try {`. |
| 19 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let ready`. |
| 20 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 21 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 22 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 23 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call('/api/missing', 'GET', undefined, 404);`. |
| 24 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const signup`. |
| 25 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call('/api/auth/signup', 'POST', signup, 201);`. |
| 26 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call('/api/auth/signup', 'POST', signup, 409);`. |
| 27 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call('/api/auth/login', 'POST', { email: signup.email, password: 'bad-password' }, 401);`. |
| 28 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const logged`. |
| 29 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 30 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call('/api/auth/me');`. |
| 31 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const cookieResult`. |
| 32 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 33 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call('/api/posts', 'POST', { title: '', body: 'x' }, 400);`. |
| 34 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call('/api/posts', 'POST', '{', 400);`. |
| 35 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call('/api/posts', 'POST', { title: 'x', body: 'y' }, 401, '');`. |
| 36 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call('/api/posts', 'POST', { title: 'x', body: 'y' }, 403, token, { Origin: 'https://evil.example' });`. |
| 37 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const created`. |
| 38 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 39 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const listing`. |
| 40 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 41 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call('/api/posts?page=0', 'GET', undefined, 400);`. |
| 42 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call(/api/posts/${id}); await call('/api/posts/no-number', 'GET', undefined, 400);`. |
| 43 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call(/api/posts/${id}, 'PATCH', { body: '변경' });`. |
| 44 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call('/api/auth/signup', 'POST', { ...signup, email: 'other@example.com' }, 201);`. |
| 45 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `other = (await call('/api/auth/login', 'POST', { email: 'other@example.com', password: signup.password })).res`. |
| 46 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call(/api/posts/${id}, 'PATCH', { title: '탈취' }, 403, other);`. |
| 47 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const comment`. |
| 48 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 49 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call(/api/comments/${comment.id}, 'DELETE', undefined, 403, other);`. |
| 50 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call(/api/comments/${comment.id}, 'DELETE', undefined, 204);`. |
| 51 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const doc`. |
| 52 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call(/api/documents/${doc.id}/download, 'GET', undefined, 403, other);`. |
| 53 | HTTP 요청을 보내 응답을 기다린다. 주입된 fetcher는 테스트에서 대체할 수 있다. |
| 54 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 55 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call('/api/mail', 'POST', {}, 202);`. |
| 56 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 57 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call(/api/posts/${id}, 'DELETE', undefined, 204);`. |
| 58 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call(/api/posts/${id}, 'GET', undefined, 404);`. |
| 59 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await call('/api/auth/logout', 'POST', {}, 204); await call('/api/auth/me', 'GET', undefined, 401);`. |
| 60 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `console.log(HTTP 계약 ${count}개 통과);`. |
| 61 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 62 | 성공·실패에 관계없이 연결/잠금 등 정리 작업을 실행한다. |

### `course/playwright.config.mjs` 전체 코드

[playwright.config.mjs](course/playwright.config.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests/browser', workers: 1,
  use: { baseURL: 'http://127.0.0.1:4394', browserName: 'chromium', headless: true },
  webServer: { command: 'node scripts/test-server.mjs', url: 'http://127.0.0.1:4394/health', reuseExistingServer: false },
});
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'@playwright/test'`의 기능을 이 파일에서 사용한다. |
| 2 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `export default defineConfig({`. |
| 3 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `testDir: './tests/browser', workers: 1,`. |
| 4 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `use: { baseURL: 'http://127.0.0.1:4394', browserName: 'chromium', headless: true },`. |
| 5 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `webServer: { command: 'node scripts/test-server.mjs', url: 'http://127.0.0.1:4394/health', reuseExistingServer`. |
| 6 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/tests/browser/flow.spec.mjs` 전체 코드

[flow.spec.mjs](course/tests/browser/flow.spec.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { test, expect } from '@playwright/test';
test('브라우저 → 가입/쿠키 로그인 → CRUD → 문서/AI → 로그아웃', async ({ page }) => {
  const errors = []; page.on('pageerror', e => errors.push(e.message));
  const email = `browser-${Date.now()}@example.com`;
  await page.goto('/auth');
  await page.locator('#signup [name=email]').fill(email);
  await page.locator('#signup [name=password]').fill('browser-password');
  await page.locator('#signup [name=nickname]').fill('브라우저');
  await page.locator('#signup button').click(); await expect(page.locator('#message')).toContainText('가입했습니다');
  await page.locator('#login [name=email]').fill(email);
  await page.locator('#login [name=password]').fill('browser-password');
  await page.locator('#login button').click(); await expect(page.locator('#message')).toContainText('로그인했습니다');
  const cookies = await page.context().cookies(); expect(cookies.find(c => c.name === 'desk_session').httpOnly).toBe(true);
  await page.goto('/board');
  await page.locator('#editor [name=title]').fill('<img src=x onerror=alert(1)>');
  await page.locator('#editor [name=body]').fill('Astro 브라우저 테스트');
  await page.locator('#editor [name=tags]').fill('test');
  await page.locator('#editor button').click();
  await expect(page.locator('#posts')).toContainText('<img src=x onerror=alert(1)>');
  await expect(page.locator('#posts img')).toHaveCount(0);
  await page.locator('#posts button', { hasText: '편집' }).first().click();
  const id = await page.locator('#editor [name=id]').inputValue();
  await page.locator('#editor [name=title]').fill('수정한 글'); await page.locator('#editor button').click();
  await expect(page.locator('#posts')).toContainText('수정한 글');
  await page.locator('#comment-form [name=postId]').fill(id); await page.locator('#comment-form [name=body]').fill('댓글 테스트');
  await page.locator('#comment-form button', { hasText: '댓글 작성' }).click();
  await expect(page.locator('#comments')).toContainText('댓글 테스트');
  await page.goto('/documents');
  await page.locator('#upload [name=text]').fill('Astro는 콘텐츠를 HTML로 만듭니다.');
  await page.locator('#upload button').click(); await expect(page.locator('#message')).toContainText('저장했습니다');
  await page.locator('#ask [name=question]').fill('Astro'); await page.locator('#ask button', { hasText: '생성' }).click();
  await expect(page.locator('#answer')).toContainText('발췌 1');
  await page.screenshot({ path: 'test-results/document-flow.png', fullPage: true });
  await page.goto('/auth'); await page.locator('#logout').click(); await expect(page.locator('#message')).toContainText('로그아웃했습니다');
  await page.locator('#me').click(); await expect(page.locator('#message')).toContainText('401');
  expect(errors).toEqual([]);
});
test('로컬 저장소 복구와 422 화면 처리', async ({ page }) => {
  await page.goto('/lessons'); await page.locator('#draft').fill('새로고침 후 복구'); await page.reload();
  await expect(page.locator('#draft')).toHaveValue('새로고침 후 복구');
  await page.route('**/api/auth/login', route => route.fulfill({ status: 422, contentType: 'application/json', body: JSON.stringify({ error: { message: '모의 검증', fields: { email: ['오류'] } } }) }));
  await page.goto('/auth'); await page.locator('#login [name=email]').fill('mock@example.com'); await page.locator('#login [name=password]').fill('mock-password');
  await page.locator('#login button').click(); await expect(page.locator('#message')).toContainText('422 입력 형식');
});
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'@playwright/test'`의 기능을 이 파일에서 사용한다. |
| 2 | 독립적으로 확인할 테스트 시나리오를 정의한다. |
| 3 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const errors`. |
| 4 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const email`. |
| 5 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.goto('/auth');`. |
| 6 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.locator('#signup [name=email]').fill(email);`. |
| 7 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.locator('#signup [name=password]').fill('browser-password');`. |
| 8 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.locator('#signup [name=nickname]').fill('브라우저');`. |
| 9 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 10 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.locator('#login [name=email]').fill(email);`. |
| 11 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.locator('#login [name=password]').fill('browser-password');`. |
| 12 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 13 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 14 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.goto('/board');`. |
| 15 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.locator('#editor [name=title]').fill('<img src=x onerror=alert(1)>');`. |
| 16 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.locator('#editor [name=body]').fill('Astro 브라우저 테스트');`. |
| 17 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.locator('#editor [name=tags]').fill('test');`. |
| 18 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.locator('#editor button').click();`. |
| 19 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 20 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 21 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.locator('#posts button', { hasText: '편집' }).first().click();`. |
| 22 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const id`. |
| 23 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.locator('#editor [name=title]').fill('수정한 글'); await page.locator('#editor button').click();`. |
| 24 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 25 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.locator('#comment-form [name=postId]').fill(id); await page.locator('#comment-form [name=body]').fi`. |
| 26 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.locator('#comment-form button', { hasText: '댓글 작성' }).click();`. |
| 27 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 28 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.goto('/documents');`. |
| 29 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.locator('#upload [name=text]').fill('Astro는 콘텐츠를 HTML로 만듭니다.');`. |
| 30 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 31 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.locator('#ask [name=question]').fill('Astro'); await page.locator('#ask button', { hasText: '생성' })`. |
| 32 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 33 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.screenshot({ path: 'test-results/document-flow.png', fullPage: true });`. |
| 34 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 35 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 36 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 37 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 38 | 독립적으로 확인할 테스트 시나리오를 정의한다. |
| 39 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.goto('/lessons'); await page.locator('#draft').fill('새로고침 후 복구'); await page.reload();`. |
| 40 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 41 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 42 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await page.goto('/auth'); await page.locator('#login [name=email]').fill('mock@example.com'); await page.locat`. |
| 43 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 44 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

## ④ 🔗 연동 포인트

단위 테스트→실제 빌드→HTTP 서버→브라우저 순으로 검증한다. X-Request-Id를 브라우저 Network와 서버 JSON 로그에서 대조한다. 다음 단계 배포 전에도 같은 검사를 실행한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| Node 명령 없음 | 런타임/PATH | Node 설치·새 터미널 |
| 포트 충돌 | 서버 중복 실행 | 기존 프로세스 확인 |
| 정적 경로 실패 | getStaticPaths 누락 | 생성 경로 반환 |
| window 오류 | 서버에서 DOM 접근 | script로 이동 |
| API 404 | 주소 불일치 | src/pages와 fetch 대조 |
| 400 검증 | 필드/JSON 오류 | error.fields 확인 |
| 401 인증 | 쿠키 없음·만료 | host·Secure·세션 확인 |
| 403 권한 | 작성자·Origin 불일치 | 계정·허용 출처 확인 |
| PATCH 태그 손실 | default 적용 | 부분 스키마 default 제거 |
| DB/외부 500·502 | 저장소·제공자 실패 | requestId로 서버 로그 확인 |

## ⑥ 직접 해보기

1. 태그 보존 테스트가 tags 기본값을 잘못 넣었을 때 실패하는지 확인한다.
2. 가짜 메일 응답을 500으로 바꿔 502 변환을 확인한다.
3. 브라우저 422 mock에서 오류 문구를 읽는다.

## ⑦ ☐ 체크리스트

- [ ] 단위 테스트와 실제 HTTP 요청 테스트를 실행했다.
- [ ] DB·외부 API를 테스트 대역으로 바꿨다.
- [ ] Network·Console·서버 로그와 requestId로 디버깅했다.
- [ ] 자주 나는 오류 TOP 10을 기록했다.

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study10.md](study10.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
