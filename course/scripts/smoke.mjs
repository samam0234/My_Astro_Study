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
