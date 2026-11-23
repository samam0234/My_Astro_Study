# study14 · API 설계

## ① 목표 한 줄

REST 경로·OpenAPI·버전·페이지네이션·공통 오류를 명세로 고정한다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

REST 경로는 리소스를 나타낸다. `/api/posts`의 GET은 목록, POST는 등록이며 `/api/posts/{id}`의 GET·PATCH·DELETE는 상세·부분수정·삭제다. 공통 API v1의 경로를 그대로 사용하므로 URL에 임의로 /v1을 추가하지 않는다. 버전은 현재 문서 계약 1.0.0이며 호환성을 깨는 후속 계약에 새 경로 또는 협상 정책을 따로 정한다.

페이지네이션은 도서관 목록의 쪽 번호다. page는 1부터, limit은 기본 10·최대 50, q는 제목/본문 대소문자 무시 부분 검색, sort는 createdAt·-createdAt·-commentCount다. 목록은 data 배열과 meta를 갖고 오류는 error 객체 안에 code/message/fields/requestId를 갖는다.

OpenAPI는 요청·응답 계약의 기계가 읽는 지도다. `/api-docs`에 경로를 표시하고 `/openapi.json`을 Swagger Editor 등에 가져올 수 있다. 코드와 문서를 함께 바꾸고 HTTP 계약 테스트로 상태·헤더·응답 모양을 확인한다.

## ③ 🛠️ 실기

서버 실행 후 `/api-docs`에서 엔드포인트를 확인한다. 전체 OpenAPI 파일은 `course/public/openapi.json`이며 학습 예제의 추가 API(문서·AI·메일·결제·OAuth·SSE)도 함께 명시한다. 추가 API는 공통 게시판 계약의 필수 경로를 바꾸지 않는다.

```powershell
Invoke-RestMethod 'http://127.0.0.1:4323/api/posts?q=Astro&page=1&limit=10&sort=-createdAt'
Invoke-WebRequest 'http://127.0.0.1:4323/health'
```

첫 줄은 목록 data/meta, 둘째 줄은 준비 상태와 헤더를 확인한다. 스트리밍은 예외적으로 NDJSON/SSE 미디어 타입이며 스트림 도중 발생한 오류는 이미 보낸 200 상태를 바꿀 수 없어 프레임 안에 오류를 보낸다.

### `course/src/lib/basic-api.mjs` 전체 코드

[basic-api.mjs](course/src/lib/basic-api.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { z } from 'zod';
import { body, fail, json, positiveId } from './http.mjs';
import { signupSchema, loginSchema, validate } from './validation.mjs';
import { signup, login, publicUser, requireUser, owned, digest } from './auth.mjs';
import { listPosts, serializePost, createPost, updatePost, deletePost } from './posts.mjs';
import { postCache } from './cache.mjs';
import { settings } from './config.mjs';

export function sessionCookie(context, token) {
  context.cookies.set('desk_session', token, { path: '/', httpOnly: true, sameSite: 'lax', secure: settings().site.startsWith('https:'), maxAge: 3600 });
}
export async function dispatchBasic(context, store) {
  const { request, url, locals } = context, method = request.method;
  const path = url.pathname.replace(/\/$/, ''), user = locals.user;
  if (path === '/api/auth/signup' && method === 'POST') {
    const created = await signup(store, validate(signupSchema, await body(request)));
    return json({ data: publicUser(created) }, 201);
  }
  if (path === '/api/auth/login' && method === 'POST') {
    const data = await login(store, validate(loginSchema, await body(request)));
    sessionCookie(context, data.accessToken); return json({ data });
  }
  if (path === '/api/auth/me' && method === 'GET') return json({ data: requireUser(user) });
  if (path === '/api/auth/logout' && method === 'POST') {
    requireUser(user);
    for (const session of await store.list('sessions')) if (session.digest === digest(locals.token)) await store.remove('sessions', session.id);
    context.cookies.delete('desk_session', { path: '/' }); return new Response(null, { status: 204 });
  }
  if (path === '/api/posts') {
    if (method === 'GET') return json(process.env.COURSE_STAGE === 'midpoint' ? await listPosts(store, url) : await postCache.get(url.search, () => listPosts(store, url)));
    if (method === 'POST') {
      const data = await createPost(store, user, await body(request)); postCache.clear();
      return json({ data }, 201, { Location: `/api/posts/${data.id}` });
    }
    fail(405, 'METHOD_NOT_ALLOWED', 'GET 또는 POST를 사용하세요.');
  }
  let match = path.match(/^\/api\/posts\/([^/]+)$/);
  if (match) {
    const id = positiveId(match[1]);
    if (method === 'GET') return json({ data: await serializePost(store, await store.get('posts', id)) });
    if (method === 'PATCH') { const data = await updatePost(store, user, id, await body(request)); postCache.clear(); return json({ data }); }
    if (method === 'DELETE') { await deletePost(store, user, id); postCache.clear(); return new Response(null, { status: 204 }); }
    fail(405, 'METHOD_NOT_ALLOWED', 'GET/PATCH/DELETE를 사용하세요.');
  }
  match = path.match(/^\/api\/posts\/([^/]+)\/comments$/);
  if (match) {
    const postId = positiveId(match[1]);
    if (!(await store.get('posts', postId))) fail(404, 'NOT_FOUND', '글이 없습니다.');
    if (method === 'GET') {
      const comments = (await store.list('comments')).filter(c => c.postId === postId);
      const data = await Promise.all(comments.map(async c => ({ id: c.id, body: c.body, postId, createdAt: c.createdAt,
        author: { id: c.authorId, nickname: (await store.get('users', c.authorId)).nickname } })));
      return json({ data });
    }
    if (method === 'POST') {
      requireUser(user);
      const input = validate(z.object({ body: z.string().trim().min(1).max(2000) }).strict(), await body(request));
      const c = await store.create('comments', { ...input, postId, authorId: user.id, createdAt: new Date().toISOString() });
      postCache.clear();
      return json({ data: { id: c.id, body: c.body, postId, author: { id: user.id, nickname: user.nickname }, createdAt: c.createdAt } }, 201);
    }
  }
  match = path.match(/^\/api\/comments\/([^/]+)$/);
  if (match && method === 'DELETE') {
    const id = positiveId(match[1]); owned(await store.get('comments', id), user);
    await store.remove('comments', id); postCache.clear(); return new Response(null, { status: 204 });
  }
  return null;
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'zod'`의 기능을 이 파일에서 사용한다. |
| 2 | `'./http.mjs'`의 기능을 이 파일에서 사용한다. |
| 3 | `'./validation.mjs'`의 기능을 이 파일에서 사용한다. |
| 4 | `'./auth.mjs'`의 기능을 이 파일에서 사용한다. |
| 5 | `'./posts.mjs'`의 기능을 이 파일에서 사용한다. |
| 6 | `'./cache.mjs'`의 기능을 이 파일에서 사용한다. |
| 7 | `'./config.mjs'`의 기능을 이 파일에서 사용한다. |
| 8 | 코드 구간을 나누는 빈 줄이다. |
| 9 | 재사용 함수 `sessionCookie`를 정의한다. |
| 10 | 서버가 쿠키와 보안 속성을 응답에 설정한다. |
| 11 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 12 | 비동기 함수 `dispatchBasic`의 입력과 처리 범위를 정의한다. |
| 13 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { request, url, locals }`. |
| 14 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const path`. |
| 15 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 16 | 정해진 스키마로 입력을 검사하고 허용된 값만 다음 계층으로 보낸다. |
| 17 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 18 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 19 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 20 | 정해진 스키마로 입력을 검사하고 허용된 값만 다음 계층으로 보낸다. |
| 21 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 22 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 23 | 미인증 사용자를 401로 거절하고 인증 사용자만 다음 처리를 허용한다. |
| 24 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 25 | 미인증 사용자를 401로 거절하고 인증 사용자만 다음 처리를 허용한다. |
| 26 | 지정 kind와 id의 레코드를 삭제한다. |
| 27 | 같은 경로의 쿠키를 만료시켜 브라우저 출입증을 지운다. |
| 28 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 29 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 30 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 31 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 32 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const data`. |
| 33 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 34 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 35 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 36 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 37 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let match`. |
| 38 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 39 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const id`. |
| 40 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 41 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 42 | 응답 본문·상태·헤더 또는 스트림을 담은 HTTP Response를 만든다. |
| 43 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 44 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 45 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `match = path.match(/^\/api\/posts\/([^/]+)\/comments$/);`. |
| 46 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 47 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const postId`. |
| 48 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 49 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 50 | 저장소에서 해당 종류의 레코드를 읽어 필터·검증·응답에 사용한다. |
| 51 | 목록의 각 항목을 화면 또는 응답에 필요한 모양으로 변환한다. |
| 52 | 종류와 id가 일치하는 단일 레코드를 조회한다. |
| 53 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 54 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 55 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 56 | 미인증 사용자를 401로 거절하고 인증 사용자만 다음 처리를 허용한다. |
| 57 | 정해진 스키마로 입력을 검사하고 허용된 값만 다음 계층으로 보낸다. |
| 58 | 저장소 계약으로 새 레코드를 생성하며 생성 id를 받는다. |
| 59 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `postCache.clear();`. |
| 60 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 61 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 62 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 63 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `match = path.match(/^\/api\/comments\/([^/]+)$/);`. |
| 64 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 65 | 자원 존재와 작성자 일치를 확인해 다른 사람의 데이터 접근을 막는다. |
| 66 | 응답 본문·상태·헤더 또는 스트림을 담은 HTTP Response를 만든다. |
| 67 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 68 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 69 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/src/lib/api.mjs` 전체 코드

[api.mjs](course/src/lib/api.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { dispatchBasic, sessionCookie } from './basic-api.mjs';
import { z } from 'zod';
import { body, fail, json, positiveId } from './http.mjs';
import { validate } from './validation.mjs';
import { requireUser, owned } from './auth.mjs';
import { checkout, stripeWebhook, oauthStart, oauthCallback } from './integrations.mjs';
import { saveDocument, downloadDocument } from './files.mjs';
import { enqueueMail } from './jobs.mjs';
import { generate, retrieve } from './ai.mjs';
import { settings } from './config.mjs';

export async function dispatch(context, store) {
  const { request, url, locals } = context, method = request.method;
  const path = url.pathname.replace(/\/$/, ''), user = locals.user;
  const basic = await dispatchBasic(context, store);
  if (basic) return basic;
  if (process.env.COURSE_STAGE === 'midpoint') fail(404, 'NOT_FOUND', 'Midpoint mode exposes only auth and board APIs.');
  let match;
  if (path === '/api/mail' && method === 'POST') {
    requireUser(user); const job = await enqueueMail(store, user); return json({ data: job }, 202);
  }
  if (path === '/api/checkout' && method === 'POST') {
    requireUser(user);
    const { key } = validate(z.object({ key: z.uuid() }), await body(request));
    return json({ data: await checkout(user, settings().site, process.env, `checkout-${user.id}-${key}`) });
  }
  if (path === '/api/stripe/webhook' && method === 'POST') {
    // 외부에서 서명한 원문. 일반 JSON 파싱 전에 그대로 검증한다.
    const length = Number(request.headers.get('content-length'));
    if (!Number.isSafeInteger(length) || length < 1 || length > 65536) fail(413, 'PAYLOAD_TOO_LARGE', '웹훅 크기를 확인하세요.');
    const raw = await request.text();
    if (Buffer.byteLength(raw) > 65536) fail(413, 'PAYLOAD_TOO_LARGE', '웹훅이 너무 큽니다.');
    return json(await stripeWebhook(store, raw, request.headers.get('stripe-signature')));
  }
  if (path === '/api/oauth/start' && method === 'GET') return oauthStart(context.cookies, settings().site);
  if (path === '/api/oauth/callback' && method === 'GET') {
    const session = await oauthCallback(store, context, settings().site); sessionCookie(context, session.accessToken);
    return Response.redirect(`${settings().site}/board`, 302);
  }
  if (path === '/api/documents') {
    requireUser(user);
    if (method === 'GET') return json({ data: (await store.list('documents')).filter(d => d.authorId === user.id).map(({ key, text, ...d }) => d) });
    if (method === 'POST') { const d = await saveDocument(store, user, await body(request, 150000)); return json({ data: { id: d.id, name: d.name } }, 201); }
  }
  match = path.match(/^\/api\/documents\/([^/]+)\/download$/);
  if (match && method === 'GET') return downloadDocument(owned(await store.get('documents', positiveId(match[1])), user));
  if (path === '/api/ai' && method === 'POST') {
    requireUser(user);
    const input = validate(z.object({ documentId: z.number().int().positive(), question: z.string().trim().max(500).default('') }).strict(), await body(request));
    const doc = owned(await store.get('documents', input.documentId), user);
    const iterator = generate(doc.text, input.question, { signal: request.signal });
    // 첫 토큰까지 읽어 upstream HTTP 오류를 공통 JSON 오류로 반환한다.
    const first = await iterator.next(); let initial = true, answer = '', finished = false;
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async pull(controller) {
        try {
          const item = initial ? first : await iterator.next(); initial = false;
          if (item.done) {
            if (!finished) await store.create('questions', { documentId: doc.id, authorId: user.id, question: input.question, answer,
              sources: input.question ? retrieve(doc.text, input.question) : [{ index: 1 }], createdAt: new Date().toISOString() });
            finished = true; controller.close();
          } else { answer += item.value; controller.enqueue(encoder.encode(JSON.stringify({ delta: item.value }) + '\n')); }
        } catch { controller.enqueue(encoder.encode(JSON.stringify({ error: '생성이 중단되었습니다.' }) + '\n')); controller.close(); await iterator.return(); }
      },
      async cancel() { await iterator.return(); },
    });
    return new Response(stream, { headers: { 'Content-Type': 'application/x-ndjson; charset=utf-8', 'Cache-Control': 'no-store' } });
  }
  if (path === '/api/events' && method === 'GET') {
    requireUser(user);
    const encoder = new TextEncoder(); let timer, stop, count = 0, busy = false;
    const stream = new ReadableStream({
      start(controller) {
        stop = () => { clearInterval(timer); request.signal.removeEventListener('abort', stop); try { controller.close(); } catch {} };
        request.signal.addEventListener('abort', stop, { once: true });
        controller.enqueue(encoder.encode('retry: 3000\n\n'));
        timer = setInterval(async () => {
          if (busy) return; busy = true;
          try {
            const jobs = (await store.list('jobs')).filter(j => j.userId === user.id);
            controller.enqueue(encoder.encode(`event: jobs\ndata: ${JSON.stringify(jobs.map(j => ({ id: j.id, status: j.status })))}\n\n`));
            if (++count >= 30) stop();
          } catch { stop(); } finally { busy = false; }
        }, 1000);
      }, cancel() { stop(); },
    });
    return new Response(stream, { headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no' } });
  }
  fail(404, 'NOT_FOUND', 'API 경로가 없습니다.');
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'./basic-api.mjs'`의 기능을 이 파일에서 사용한다. |
| 2 | `'zod'`의 기능을 이 파일에서 사용한다. |
| 3 | `'./http.mjs'`의 기능을 이 파일에서 사용한다. |
| 4 | `'./validation.mjs'`의 기능을 이 파일에서 사용한다. |
| 5 | `'./auth.mjs'`의 기능을 이 파일에서 사용한다. |
| 6 | `'./integrations.mjs'`의 기능을 이 파일에서 사용한다. |
| 7 | `'./files.mjs'`의 기능을 이 파일에서 사용한다. |
| 8 | `'./jobs.mjs'`의 기능을 이 파일에서 사용한다. |
| 9 | `'./ai.mjs'`의 기능을 이 파일에서 사용한다. |
| 10 | `'./config.mjs'`의 기능을 이 파일에서 사용한다. |
| 11 | 코드 구간을 나누는 빈 줄이다. |
| 12 | 비동기 함수 `dispatch`의 입력과 처리 범위를 정의한다. |
| 13 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { request, url, locals }`. |
| 14 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const path`. |
| 15 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const basic`. |
| 16 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 17 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 18 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let match;`. |
| 19 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 20 | 미인증 사용자를 401로 거절하고 인증 사용자만 다음 처리를 허용한다. |
| 21 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 22 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 23 | 미인증 사용자를 401로 거절하고 인증 사용자만 다음 처리를 허용한다. |
| 24 | 정해진 스키마로 입력을 검사하고 허용된 값만 다음 계층으로 보낸다. |
| 25 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 26 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 27 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 28 | 외부에서 서명한 원문. 일반 JSON 파싱 전에 그대로 검증한다. |
| 29 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const length`. |
| 30 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 31 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const raw`. |
| 32 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 33 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 34 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 35 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 36 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 37 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const session`. |
| 38 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 39 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 40 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 41 | 미인증 사용자를 401로 거절하고 인증 사용자만 다음 처리를 허용한다. |
| 42 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 43 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 44 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 45 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `match = path.match(/^\/api\/documents\/([^/]+)\/download$/);`. |
| 46 | 자원 존재와 작성자 일치를 확인해 다른 사람의 데이터 접근을 막는다. |
| 47 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 48 | 미인증 사용자를 401로 거절하고 인증 사용자만 다음 처리를 허용한다. |
| 49 | 정해진 스키마로 입력을 검사하고 허용된 값만 다음 계층으로 보낸다. |
| 50 | 자원 존재와 작성자 일치를 확인해 다른 사람의 데이터 접근을 막는다. |
| 51 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const iterator`. |
| 52 | 첫 토큰까지 읽어 upstream HTTP 오류를 공통 JSON 오류로 반환한다. |
| 53 | 다음 스트림 조각 또는 생성 토큰을 비동기로 읽는다. |
| 54 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const encoder`. |
| 55 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const stream`. |
| 56 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `async pull(controller) {`. |
| 57 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `try {`. |
| 58 | 다음 스트림 조각 또는 생성 토큰을 비동기로 읽는다. |
| 59 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 60 | 저장소 계약으로 새 레코드를 생성하며 생성 id를 받는다. |
| 61 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `sources: input.question ? retrieve(doc.text, input.question) : [{ index: 1 }], createdAt: new Date().toISOStri`. |
| 62 | 사용이 끝난 스트림·소켓·DB 자원을 종료하거나 잠금을 해제한다. |
| 63 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 64 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 65 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 66 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `async cancel() { await iterator.return(); },`. |
| 67 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 68 | 응답 본문·상태·헤더 또는 스트림을 담은 HTTP Response를 만든다. |
| 69 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 70 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 71 | 미인증 사용자를 401로 거절하고 인증 사용자만 다음 처리를 허용한다. |
| 72 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const encoder`. |
| 73 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const stream`. |
| 74 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `start(controller) {`. |
| 75 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 76 | 브라우저 이벤트가 발생했을 때 실행할 함수를 연결한다. |
| 77 | 스트림 소비자가 다음 조각을 받을 수 있도록 데이터를 내보낸다. |
| 78 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `timer = setInterval(async () => {`. |
| 79 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 80 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `try {`. |
| 81 | 저장소에서 해당 종류의 레코드를 읽어 필터·검증·응답에 사용한다. |
| 82 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 83 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 84 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 85 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `}, 1000);`. |
| 86 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `}, cancel() { stop(); },`. |
| 87 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 88 | 응답 본문·상태·헤더 또는 스트림을 담은 HTTP Response를 만든다. |
| 89 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 90 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 91 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/src/pages/api-docs.astro` 전체 코드

[api-docs.astro](course/src/pages/api-docs.astro)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```astro
---
import Desk from '../layouts/Desk.astro';
import spec from '../../public/openapi.json';
---
<Desk title="공통 API v1">
  <h1>공통 API v1 · OpenAPI 3.1</h1>
  <p><a href="/openapi.json">OpenAPI JSON 다운로드</a> · Swagger Editor에 가져와 요청을 실행할 수 있습니다.</p>
  <p>같은 출처에서는 HttpOnly 세션 쿠키를 쓰고, API 클라이언트는 Bearer 토큰을 사용합니다.</p>
  <table><thead><tr><th>경로</th><th>메소드</th></tr></thead><tbody>
    {Object.entries(spec.paths).map(([path, operations]) => <tr><td><code>{path}</code></td><td>{Object.keys(operations).join(', ').toUpperCase()}</td></tr>)}
  </tbody></table>
</Desk>
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 2 | `'../layouts/Desk.astro'`의 기능을 이 파일에서 사용한다. |
| 3 | `'../../public/openapi.json'`의 기능을 이 파일에서 사용한다. |
| 4 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 5 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 6 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 7 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 8 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 9 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 10 | 목록의 각 항목을 화면 또는 응답에 필요한 모양으로 변환한다. |
| 11 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 12 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |

## ④ 🔗 연동 포인트

[기준 명세](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e)→OpenAPI→Astro dispatcher→저장소→브라우저 api 함수 순서로 연결한다. 204는 본문이 없고 201은 Location을 보낸다. HTTP X-Request-Id와 오류 본문의 requestId를 맞춘다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 등록 상태가 200 | 생성 계약 누락 | 201과 Location 사용 |
| requestId 불일치 | 예외 handler 경로 분산 | 공통 middleware 사용 |
| 204 파싱 오류 | 응답 본문 기대 | 본문 없이 종료 |

## ⑥ 직접 해보기

1. limit=100·page=0·잘못된 id를 각각 호출한다.
2. X-Request-Id를 지정해 응답 헤더·오류 본문에서 같은 값인지 확인한다.
3. OpenAPI JSON을 Swagger Editor에 가져와 경로와 입력 필드를 확인한다.

## ⑦ ☐ 체크리스트

- [ ] 공통 v1의 모든 인증·게시글·댓글 경로를 구현했다.
- [ ] 페이지·정렬·검색·공통 오류와 요청 ID를 명세에 맞췄다.
- [ ] OpenAPI 3.1 문서와 /api-docs를 제공한다.

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study15.md](study15.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
