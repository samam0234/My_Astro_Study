# study7 · 인증·보안 기초

## ① 목표 한 줄

회원가입·로그인·세션·권한과 기본 공격 방어를 구현한다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

인증은 누군지 확인하는 일, 인가는 그 사람이 이 글을 바꿀 수 있는지 확인하는 일이다. 비밀번호는 scrypt와 무작위 salt로 해시한다. 같은 비밀번호도 해시가 달라지며 로그인 때 timingSafeEqual로 비교한다. 비밀번호 원문과 해시는 응답에 포함하지 않는다.

세션은 출입증이다. 32바이트 무작위 토큰을 발급하고 DB에는 SHA-256 digest만 저장한다. 브라우저는 HttpOnly·SameSite=Lax 쿠키로, API 클라이언트는 Bearer 헤더로 같은 세션을 보낸다. 유효시간은 1시간이다. 로그아웃은 현재 토큰의 세션 레코드와 쿠키를 함께 폐기한다.

CORS는 브라우저가 다른 출처의 응답을 읽는 규칙이지 인증이 아니다. 변경 요청의 Origin을 허용 출처와 비교하고 JSON Content-Type을 요구해 CSRF 표면을 줄인다. 응답은 textContent와 Astro 기본 이스케이프를 사용해 XSS를 줄인다. raw HTML 출력은 사용하지 않는다. 운영에서는 HTTPS와 정확한 SITE_URL을 필수로 맞춘다.

## ③ 🛠️ 실기

`/auth`에서 가입→로그인→내 정보→로그아웃을 순서대로 실행한다. 개발자도구 Application의 쿠키에서 HttpOnly·SameSite를 확인한다. API 응답에는 accessToken도 있지만 이 화면은 저장하지 않고 쿠키를 사용한다. `SITE_URL=https://...`일 때 Secure 쿠키가 켜지므로 로컬 HTTP와 운영 HTTPS 설정을 섞지 않는다. 인증 실패의 메시지는 이메일 존재 여부를 구분하지 않는다.

### `course/src/lib/auth.mjs` 전체 코드

[auth.mjs](course/src/lib/auth.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { randomBytes, scrypt as scryptCallback, timingSafeEqual, createHash } from 'node:crypto';
import { promisify } from 'node:util';
import { fail } from './http.mjs';
import { duplicate } from './store.mjs';

const scrypt = promisify(scryptCallback);
export const digest = value => createHash('sha256').update(value).digest('hex');
export const publicUser = user => ({ id: user.id, email: user.email, nickname: user.nickname });
export async function hashPassword(password) {
  const salt = randomBytes(16).toString('hex');
  const key = await scrypt(password, salt, 64);
  return `${salt}:${key.toString('hex')}`;
}
export async function checkPassword(password, encoded) {
  if (!encoded?.includes(':')) return false;
  const [salt, hash] = encoded.split(':');
  const actual = await scrypt(password, salt, 64), expected = Buffer.from(hash, 'hex');
  return expected.length === actual.length && timingSafeEqual(expected, actual);
}
export async function signup(store, input) {
  try { return await store.create('users', { email: input.email, nickname: input.nickname, passwordHash: await hashPassword(input.password) }, `email:${input.email}`); }
  catch (error) { if (duplicate(error)) fail(409, 'EMAIL_TAKEN', '이미 등록된 이메일입니다.'); throw error; }
}
export async function issueSession(store, user) {
  const token = randomBytes(32).toString('base64url');
  await store.create('sessions', { userId: user.id, digest: digest(token), expiresAt: Date.now() + 3600000 });
  return { user: publicUser(user), accessToken: token };
}
export async function login(store, input) {
  const user = (await store.list('users')).find(u => u.email === input.email);
  // 없는 계정도 scrypt를 실행해 응답시간 차이를 줄인다.
  const encoded = user?.passwordHash || `${'0'.repeat(32)}:${'0'.repeat(128)}`;
  if (!(await checkPassword(input.password, encoded)) || !user) fail(401, 'INVALID_CREDENTIALS', '이메일 또는 비밀번호를 확인하세요.');
  return issueSession(store, user);
}
export async function authenticate(store, token) {
  if (!token || token.length > 128) return null;
  const session = (await store.list('sessions')).find(s => s.digest === digest(token) && s.expiresAt > Date.now());
  return session ? publicUser(await store.get('users', session.userId)) : null;
}
export function requireUser(user) { if (!user) fail(401, 'UNAUTHORIZED', '로그인이 필요합니다.'); return user; }
export function owned(record, user) {
  requireUser(user);
  if (!record) fail(404, 'NOT_FOUND', '자원이 없습니다.');
  if (record.authorId !== user.id) fail(403, 'FORBIDDEN', '작성자만 변경할 수 있습니다.');
  return record;
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'node:crypto'`의 기능을 이 파일에서 사용한다. |
| 2 | `'node:util'`의 기능을 이 파일에서 사용한다. |
| 3 | `'./http.mjs'`의 기능을 이 파일에서 사용한다. |
| 4 | `'./store.mjs'`의 기능을 이 파일에서 사용한다. |
| 5 | 코드 구간을 나누는 빈 줄이다. |
| 6 | salt를 포함한 비밀번호 파생 키 계산으로 원문 저장을 피한다. |
| 7 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `export const digest`. |
| 8 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `export const publicUser`. |
| 9 | 비동기 함수 `hashPassword`의 입력과 처리 범위를 정의한다. |
| 10 | 예측하기 어려운 식별자·토큰·salt를 생성한다. |
| 11 | salt를 포함한 비밀번호 파생 키 계산으로 원문 저장을 피한다. |
| 12 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 13 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 14 | 비동기 함수 `checkPassword`의 입력과 처리 범위를 정의한다. |
| 15 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 16 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const [salt, hash]`. |
| 17 | salt를 포함한 비밀번호 파생 키 계산으로 원문 저장을 피한다. |
| 18 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 19 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 20 | 비동기 함수 `signup`의 입력과 처리 범위를 정의한다. |
| 21 | 저장소 계약으로 새 레코드를 생성하며 생성 id를 받는다. |
| 22 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 23 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 24 | 비동기 함수 `issueSession`의 입력과 처리 범위를 정의한다. |
| 25 | 예측하기 어려운 식별자·토큰·salt를 생성한다. |
| 26 | 저장소 계약으로 새 레코드를 생성하며 생성 id를 받는다. |
| 27 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 28 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 29 | 비동기 함수 `login`의 입력과 처리 범위를 정의한다. |
| 30 | 저장소에서 해당 종류의 레코드를 읽어 필터·검증·응답에 사용한다. |
| 31 | 없는 계정도 scrypt를 실행해 응답시간 차이를 줄인다. |
| 32 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const encoded`. |
| 33 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 34 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 35 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 36 | 비동기 함수 `authenticate`의 입력과 처리 범위를 정의한다. |
| 37 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 38 | 저장소에서 해당 종류의 레코드를 읽어 필터·검증·응답에 사용한다. |
| 39 | 종류와 id가 일치하는 단일 레코드를 조회한다. |
| 40 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 41 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 42 | 자원 존재와 작성자 일치를 확인해 다른 사람의 데이터 접근을 막는다. |
| 43 | 미인증 사용자를 401로 거절하고 인증 사용자만 다음 처리를 허용한다. |
| 44 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 45 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 46 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 47 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/src/middleware.js` 전체 코드

[middleware.js](course/src/middleware.js)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { defineMiddleware } from 'astro:middleware';
import { randomUUID } from 'node:crypto';
import { getStore } from './lib/store.mjs';
import { authenticate } from './lib/auth.mjs';
import { errorResponse, fail } from './lib/http.mjs';
import { settings } from './lib/config.mjs';

const hits = new Map();
export const onRequest = defineMiddleware(async (context, next) => {
  if (!context.url.pathname.startsWith('/api/') && context.url.pathname !== '/health') return next();
  const started = performance.now(), supplied = context.request.headers.get('x-request-id');
  const requestId = supplied && /^[\w-]{1,100}$/.test(supplied) ? supplied : randomUUID();
  let response;
  const config = settings(), origin = context.request.headers.get('origin');
  try {
    context.locals.requestId = requestId;
    if (origin && origin !== new URL(config.site).origin && origin !== config.cors) fail(403, 'FORBIDDEN', '허용하지 않은 Origin입니다.');
    if (context.request.method === 'OPTIONS') response = new Response(null, { status: 204 });
    else {
      const token = context.request.headers.get('authorization')?.replace(/^Bearer\s+/i, '') || context.cookies.get('desk_session')?.value;
      context.locals.token = token;
      context.locals.user = token ? await authenticate(await getStore(), token) : null;
      if (context.request.method !== 'GET' && context.url.pathname !== '/api/stripe/webhook') {
        const key = `${context.clientAddress}:${context.url.pathname}`, now = Date.now();
        if (hits.size > 10000) for (const [k, v] of hits) if (v.until < now) hits.delete(k);
        const entry = hits.get(key);
        if (entry && entry.until > now) { if (++entry.count > 60) fail(429, 'RATE_LIMITED', '잠시 후 다시 시도하세요.'); }
        else hits.set(key, { count: 1, until: now + 60000 });
        if (hits.size > 10000) hits.delete(hits.keys().next().value);
      }
      response = await next();
    }
  } catch (error) { response = errorResponse(error, requestId); }
  response.headers.set('X-Request-Id', requestId);
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Cache-Control', 'no-store');
  response.headers.set('Vary', 'Origin');
  if (origin && (origin === config.cors || origin === new URL(config.site).origin)) {
    response.headers.set('Access-Control-Allow-Origin', origin);
    response.headers.set('Access-Control-Allow-Credentials', 'true');
    response.headers.set('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS');
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Request-Id');
  }
  console.info(JSON.stringify({ requestId, method: context.request.method, path: context.url.pathname, status: response.status, durationMs: Math.round(performance.now() - started) }));
  return response;
});
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'astro:middleware'`의 기능을 이 파일에서 사용한다. |
| 2 | `'node:crypto'`의 기능을 이 파일에서 사용한다. |
| 3 | `'./lib/store.mjs'`의 기능을 이 파일에서 사용한다. |
| 4 | `'./lib/auth.mjs'`의 기능을 이 파일에서 사용한다. |
| 5 | `'./lib/http.mjs'`의 기능을 이 파일에서 사용한다. |
| 6 | `'./lib/config.mjs'`의 기능을 이 파일에서 사용한다. |
| 7 | 코드 구간을 나누는 빈 줄이다. |
| 8 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const hits`. |
| 9 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `export const onRequest`. |
| 10 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 11 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const started`. |
| 12 | 예측하기 어려운 식별자·토큰·salt를 생성한다. |
| 13 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let response;`. |
| 14 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const config`. |
| 15 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `try {`. |
| 16 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `context.locals.requestId = requestId;`. |
| 17 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 18 | 응답 본문·상태·헤더 또는 스트림을 담은 HTTP Response를 만든다. |
| 19 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 20 | 요청 쿠키 값을 서버에서 읽는다. |
| 21 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `context.locals.token = token;`. |
| 22 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `context.locals.user = token ? await authenticate(await getStore(), token) : null;`. |
| 23 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 24 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const key`. |
| 25 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 26 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const entry`. |
| 27 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 28 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 29 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 30 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 31 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `response = await next();`. |
| 32 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 33 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 34 | 응답 헤더에 보안·요청 추적·CORS 또는 캐시 정책을 설정한다. |
| 35 | 응답 헤더에 보안·요청 추적·CORS 또는 캐시 정책을 설정한다. |
| 36 | 응답 헤더에 보안·요청 추적·CORS 또는 캐시 정책을 설정한다. |
| 37 | 응답 헤더에 보안·요청 추적·CORS 또는 캐시 정책을 설정한다. |
| 38 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 39 | 응답 헤더에 보안·요청 추적·CORS 또는 캐시 정책을 설정한다. |
| 40 | 응답 헤더에 보안·요청 추적·CORS 또는 캐시 정책을 설정한다. |
| 41 | 응답 헤더에 보안·요청 추적·CORS 또는 캐시 정책을 설정한다. |
| 42 | 응답 헤더에 보안·요청 추적·CORS 또는 캐시 정책을 설정한다. |
| 43 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 44 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 45 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 46 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/src/pages/auth.astro` 전체 코드

[auth.astro](course/src/pages/auth.astro)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```astro
---
import Desk from '../layouts/Desk.astro';
---
<Desk title="계정">
  <h1>계정</h1><p id="message" role="status" aria-live="polite"></p>
  <form id="signup"><h2>회원가입</h2>
    <label>이메일<input name="email" type="email" required autocomplete="email" /></label>
    <label>비밀번호<input name="password" type="password" minlength="10" maxlength="128" required autocomplete="new-password" /></label>
    <label>별명<input name="nickname" maxlength="40" required /></label><button>가입</button>
  </form>
  <form id="login"><h2>로그인</h2>
    <label>이메일<input name="email" type="email" required autocomplete="username" /></label>
    <label>비밀번호<input name="password" type="password" minlength="10" maxlength="128" required autocomplete="current-password" /></label><button>로그인</button>
  </form>
  <div class="actions"><button id="me" type="button">내 정보</button><button id="logout" type="button">로그아웃</button><a href="/api/oauth/start">GitHub 로그인 (설정 후)</a></div>
</Desk>
<script>
  import { api, formAction, show } from '../client/api.mjs';
  formAction('#signup', async values => { await api('/api/auth/signup', { method: 'POST', body: JSON.stringify(values) }); show('가입했습니다. 로그인하세요.'); });
  formAction('#login', async values => { const { data } = await api('/api/auth/login', { method: 'POST', body: JSON.stringify(values) }); show(`${data.user.nickname}님 로그인했습니다.`); });
  document.querySelector('#me')!.addEventListener('click', async () => { try { show(JSON.stringify((await api('/api/auth/me')).data)); } catch (e) { show(e); } });
  document.querySelector('#logout')!.addEventListener('click', async () => { try { await api('/api/auth/logout', { method: 'POST', body: '{}' }); show('로그아웃했습니다.'); } catch (e) { show(e); } });
</script>
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 2 | `'../layouts/Desk.astro'`의 기능을 이 파일에서 사용한다. |
| 3 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 4 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 5 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 6 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 7 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 8 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 9 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 10 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 11 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 12 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 13 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 14 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 15 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 16 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 17 | 브라우저에서 실행할 이벤트·DOM 코드의 경계를 정한다. |
| 18 | `'../client/api.mjs'`의 기능을 이 파일에서 사용한다. |
| 19 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 20 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 21 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 22 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 23 | 브라우저에서 실행할 이벤트·DOM 코드의 경계를 정한다. |

## ④ 🔗 연동 포인트

middleware가 쿠키/Bearer → digest 조회 → locals.user를 만들고 handler가 requireUser/owned로 검사한다. 브라우저는 토큰을 localStorage에 저장하지 않는다. 프론트의 로그인 상태 확인은 `/api/auth/me` 응답으로 한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 로그인 뒤 401 | Secure 쿠키와 HTTP 불일치 | SITE_URL·접속 host 확인 |
| 다른 계정 수정 403 | 작성자 불일치 | 정상 인가 동작인지 확인 |
| 403 Origin | 허용 출처 불일치 | SITE_URL·CORS_ORIGIN 정확히 지정 |

## ⑥ 직접 해보기

1. 두 계정을 만들어 서로의 글 수정이 403인지 확인한다.
2. 로그아웃한 토큰과 만료 토큰으로 401을 확인한다.
3. 악성 HTML 문자열과 허용하지 않은 Origin을 테스트한다.

## ⑦ ☐ 체크리스트

- [ ] 비밀번호 해시와 세션 만료를 구현했다.
- [ ] 미인증 401과 작성자 불일치 403을 구분했다.
- [ ] CORS·XSS·CSRF와 HTTPS 쿠키 설정을 설명했다.

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study8.md](study8.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
