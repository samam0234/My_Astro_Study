# study13 · 외부 서비스 연동

## ① 목표 한 줄

결제·메일·파일·OAuth의 설정과 안전한 호출 경계를 구현한다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

외부 서비스 호출은 성공·실패·지연·중복이 생길 수 있는 네트워크 작업이다. 결제 화면으로 이동했다고 결제가 확정된 것은 아니다. 서버가 서명된 웹훅을 검증하고 이벤트 id로 중복을 막아야 한다. 이 학습 코드는 Stripe 테스트 키만 허용하고 결제 이벤트를 기록한다. 상품 권한 부여·환불·실결제 운영은 별도 업무 규칙이 필요하다.

메일은 서버에서 Resend API를 호출하며 키를 브라우저로 보내지 않는다. 기본 mock 응답은 delivered=false다. 파일은 TXT·MD UTF-8 텍스트만 받고 크기를 제한하며 무작위 이름으로 public 밖에 저장한다. 다운로드에도 소유권을 확인한다.

OAuth는 외부 출입증을 일회용 code로 교환하는 흐름이다. state는 요청 위조를, PKCE verifier/challenge는 code 가로채기 위험을 줄인다. callback URL은 등록된 SITE_URL과 일치해야 한다. 제공자 이메일을 검증 없이 기존 계정에 합치지 않는다.

## ③ 🛠️ 실기

기본 `.env`의 INTEGRATIONS_MODE=mock을 유지하면 유료 요청은 일어나지 않는다. `/auth` 로그인 후 `/services`에서 메일 작업 등록과 테스트 결제 응답을 확인한다. 메일 worker는 study15에서 실행한다.

실제 테스트 계정 연결 시 INTEGRATIONS_MODE=live, RESEND_API_KEY·검증된 MAIL_FROM, STRIPE_SECRET_KEY=sk_test_...·STRIPE_PRICE_ID·STRIPE_WEBHOOK_SECRET을 서버 환경에 둔다. Stripe webhook은 `/api/stripe/webhook`이며 프록시도 원문 바이트를 바꾸면 안 된다. GitHub OAuth 앱은 `/api/oauth/callback`을 callback으로 등록하고 GITHUB_CLIENT_ID·GITHUB_CLIENT_SECRET을 설정한다. OAuth는 mock 로그인으로 대체하지 않고 키가 없으면 503을 반환한다. 이 저장소 작업에서는 실제 메일·결제·OAuth 계정 호출을 하지 않았다.

### `course/src/lib/integrations.mjs` 전체 코드

[integrations.mjs](course/src/lib/integrations.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { randomBytes, createHash } from 'node:crypto';
import { fail } from './http.mjs';
import { signup, issueSession } from './auth.mjs';
import { duplicate } from './store.mjs';

export async function sendMail(user, env = process.env, fetcher = fetch, key) {
  if ((env.INTEGRATIONS_MODE || 'mock') === 'mock') return { mode: 'mock', to: user.email, delivered: false };
  if (!env.RESEND_API_KEY || !env.MAIL_FROM) fail(503, 'SERVICE_UNAVAILABLE', '메일 설정이 필요합니다.');
  const response = await fetcher('https://api.resend.com/emails', { method: 'POST',
    headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json', ...(key ? { 'Idempotency-Key': key } : {}) },
    body: JSON.stringify({ from: env.MAIL_FROM, to: [user.email], subject: 'Astro 학습 알림', text: '학습 메모가 준비되었습니다.' }), signal: AbortSignal.timeout(10000) });
  if (!response.ok) fail(502, 'MAIL_UPSTREAM', '메일 전송 실패');
  return { mode: 'live', ...(await response.json()) };
}
export async function checkout(user, site, env = process.env, idempotencyKey) {
  if ((env.INTEGRATIONS_MODE || 'mock') === 'mock') return { mode: 'mock', url: `${site}/services?checkout=mock`, paid: false };
  if (!env.STRIPE_SECRET_KEY?.startsWith('sk_test_') || !env.STRIPE_PRICE_ID) fail(503, 'SERVICE_UNAVAILABLE', 'Stripe 테스트 키와 가격 ID가 필요합니다.');
  const { default: Stripe } = await import('stripe');
  const stripe = new Stripe(env.STRIPE_SECRET_KEY);
  const session = await stripe.checkout.sessions.create({ mode: 'payment', line_items: [{ price: env.STRIPE_PRICE_ID, quantity: 1 }],
    client_reference_id: String(user.id), success_url: `${site}/services?checkout=success`, cancel_url: `${site}/services?checkout=cancel` }, { idempotencyKey });
  return { mode: 'test', url: session.url };
}
export async function stripeWebhook(store, raw, signature, env = process.env) {
  if (!env.STRIPE_WEBHOOK_SECRET) fail(503, 'SERVICE_UNAVAILABLE', '웹훅 설정이 필요합니다.');
  const { default: Stripe } = await import('stripe');
  let event;
  try { event = new Stripe(env.STRIPE_SECRET_KEY).webhooks.constructEvent(raw, signature, env.STRIPE_WEBHOOK_SECRET); }
  catch { fail(400, 'BAD_REQUEST', '웹훅 서명이 올바르지 않습니다.'); }
  try { await store.create('paymentEvents', { eventId: event.id, type: event.type, paid: event.data.object.payment_status === 'paid', userId: event.data.object.client_reference_id, createdAt: new Date().toISOString() }, `stripe:${event.id}`); }
  catch (error) { if (!duplicate(error)) throw error; }
  return { received: true };
}
export function oauthStart(cookies, site, env = process.env) {
  if (!env.GITHUB_CLIENT_ID || !env.GITHUB_CLIENT_SECRET) fail(503, 'SERVICE_UNAVAILABLE', 'GitHub OAuth 앱을 설정하세요.');
  const state = randomBytes(32).toString('base64url'), verifier = randomBytes(32).toString('base64url');
  const options = { path: '/api/oauth', httpOnly: true, sameSite: 'lax', secure: site.startsWith('https:'), maxAge: 600 };
  cookies.set('oauth_state', state, options); cookies.set('oauth_verifier', verifier, options);
  const url = new URL('https://github.com/login/oauth/authorize');
  url.search = new URLSearchParams({ client_id: env.GITHUB_CLIENT_ID, redirect_uri: `${site}/api/oauth/callback`, state, scope: 'read:user',
    code_challenge: createHash('sha256').update(verifier).digest('base64url'), code_challenge_method: 'S256' }).toString();
  return Response.redirect(url, 302);
}
export async function oauthCallback(store, context, site, env = process.env, fetcher = fetch) {
  const state = context.cookies.get('oauth_state')?.value, verifier = context.cookies.get('oauth_verifier')?.value;
  context.cookies.delete('oauth_state', { path: '/api/oauth' }); context.cookies.delete('oauth_verifier', { path: '/api/oauth' });
  if (!state || state !== context.url.searchParams.get('state') || !verifier || !context.url.searchParams.get('code')) fail(400, 'BAD_REQUEST', 'OAuth state가 일치하지 않습니다.');
  const response = await fetcher('https://github.com/login/oauth/access_token', { method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ client_id: env.GITHUB_CLIENT_ID, client_secret: env.GITHUB_CLIENT_SECRET, code: context.url.searchParams.get('code'), code_verifier: verifier, redirect_uri: `${site}/api/oauth/callback` }), signal: AbortSignal.timeout(10000) });
  const result = await response.json();
  if (!response.ok || !result.access_token) fail(502, 'OAUTH_UPSTREAM', 'OAuth 토큰 교환 실패');
  const profile = await fetcher('https://api.github.com/user', { headers: { Authorization: `Bearer ${result.access_token}`, 'User-Agent': 'astro-study-desk' }, signal: AbortSignal.timeout(10000) });
  const info = await profile.json();
  if (!profile.ok || !Number.isSafeInteger(info.id)) fail(502, 'OAUTH_UPSTREAM', 'OAuth 사용자 조회 실패');
  // 이메일 자동 병합은 하지 않는다. 검증되지 않은 이메일로 기존 계정을 탈취할 수 있다.
  const email = `github-${info.id}@oauth.invalid`;
  let user = (await store.list('users')).find(u => u.email === email);
  if (!user) user = await signup(store, { email, nickname: String(info.login).slice(0, 40), password: randomBytes(48).toString('hex') });
  return issueSession(store, user);
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'node:crypto'`의 기능을 이 파일에서 사용한다. |
| 2 | `'./http.mjs'`의 기능을 이 파일에서 사용한다. |
| 3 | `'./auth.mjs'`의 기능을 이 파일에서 사용한다. |
| 4 | `'./store.mjs'`의 기능을 이 파일에서 사용한다. |
| 5 | 코드 구간을 나누는 빈 줄이다. |
| 6 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 7 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 8 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 9 | HTTP 요청을 보내 응답을 기다린다. 주입된 fetcher는 테스트에서 대체할 수 있다. |
| 10 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `headers: { Authorization: Bearer ${env.RESEND_API_KEY}, 'Content-Type': 'application/json', ...(key ? { 'Idemp`. |
| 11 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 12 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 13 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 14 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 15 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 16 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 17 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 18 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { default: Stripe }`. |
| 19 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const stripe`. |
| 20 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const session`. |
| 21 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `client_reference_id: String(user.id), success_url: ${site}/services?checkout=success, cancel_url: ${site}/serv`. |
| 22 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 23 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 24 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 25 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 26 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { default: Stripe }`. |
| 27 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let event;`. |
| 28 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `try { event = new Stripe(env.STRIPE_SECRET_KEY).webhooks.constructEvent(raw, signature, env.STRIPE_WEBHOOK_SEC`. |
| 29 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 30 | 저장소 계약으로 새 레코드를 생성하며 생성 id를 받는다. |
| 31 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 32 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 33 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 34 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 35 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 36 | 예측하기 어려운 식별자·토큰·salt를 생성한다. |
| 37 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const options`. |
| 38 | 서버가 쿠키와 보안 속성을 응답에 설정한다. |
| 39 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const url`. |
| 40 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `url.search = new URLSearchParams({ client_id: env.GITHUB_CLIENT_ID, redirect_uri: ${site}/api/oauth/callback, `. |
| 41 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `code_challenge: createHash('sha256').update(verifier).digest('base64url'), code_challenge_method: 'S256' }).to`. |
| 42 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 43 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 44 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 45 | 요청 쿠키 값을 서버에서 읽는다. |
| 46 | 같은 경로의 쿠키를 만료시켜 브라우저 출입증을 지운다. |
| 47 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 48 | HTTP 요청을 보내 응답을 기다린다. 주입된 fetcher는 테스트에서 대체할 수 있다. |
| 49 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 50 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const result`. |
| 51 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 52 | HTTP 요청을 보내 응답을 기다린다. 주입된 fetcher는 테스트에서 대체할 수 있다. |
| 53 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const info`. |
| 54 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 55 | 이메일 자동 병합은 하지 않는다. 검증되지 않은 이메일로 기존 계정을 탈취할 수 있다. |
| 56 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const email`. |
| 57 | 저장소에서 해당 종류의 레코드를 읽어 필터·검증·응답에 사용한다. |
| 58 | 예측하기 어려운 식별자·토큰·salt를 생성한다. |
| 59 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 60 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/src/lib/files.mjs` 전체 코드

[files.mjs](course/src/lib/files.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { randomUUID } from 'node:crypto';
import { join } from 'node:path';
import { fail } from './http.mjs';

export async function saveDocument(store, user, input, directory = './data/uploads') {
  if (typeof input.text !== 'string' || !input.text.trim() || Buffer.byteLength(input.text, 'utf8') > 100000) fail(400, 'VALIDATION_ERROR', 'UTF-8 텍스트 1~100000바이트가 필요합니다.');
  const name = String(input.name || 'document.txt').replace(/[\r\n"\\/]/g, '_').slice(0, 100);
  if (!/\.(txt|md)$/i.test(name)) fail(400, 'VALIDATION_ERROR', 'TXT 또는 MD만 지원합니다.');
  const key = `${randomUUID()}.txt`;
  await mkdir(directory, { recursive: true });
  await writeFile(join(directory, key), input.text, { flag: 'wx', encoding: 'utf8', mode: 0o600 });
  return store.create('documents', { authorId: user.id, name, key, text: input.text, createdAt: new Date().toISOString() });
}
export async function downloadDocument(document, directory = './data/uploads') {
  return new Response(await readFile(join(directory, document.key)), { headers: {
    'Content-Type': 'text/plain; charset=utf-8', 'Content-Disposition': `attachment; filename*=UTF-8''${encodeURIComponent(document.name)}`, 'X-Content-Type-Options': 'nosniff',
  } });
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'node:fs/promises'`의 기능을 이 파일에서 사용한다. |
| 2 | `'node:crypto'`의 기능을 이 파일에서 사용한다. |
| 3 | `'node:path'`의 기능을 이 파일에서 사용한다. |
| 4 | `'./http.mjs'`의 기능을 이 파일에서 사용한다. |
| 5 | 코드 구간을 나누는 빈 줄이다. |
| 6 | 비동기 함수 `saveDocument`의 입력과 처리 범위를 정의한다. |
| 7 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 8 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const name`. |
| 9 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 10 | 예측하기 어려운 식별자·토큰·salt를 생성한다. |
| 11 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await mkdir(directory, { recursive: true });`. |
| 12 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await writeFile(join(directory, key), input.text, { flag: 'wx', encoding: 'utf8', mode: 0o600 });`. |
| 13 | 저장소 계약으로 새 레코드를 생성하며 생성 id를 받는다. |
| 14 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 15 | 비동기 함수 `downloadDocument`의 입력과 처리 범위를 정의한다. |
| 16 | 응답 본문·상태·헤더 또는 스트림을 담은 HTTP Response를 만든다. |
| 17 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 18 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `} });`. |
| 19 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/src/pages/services.astro` 전체 코드

[services.astro](course/src/pages/services.astro)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```astro
---
import Desk from '../layouts/Desk.astro';
---
<Desk title="외부 서비스">
  <h1>외부 서비스 연습</h1><p>기본 설정은 mock입니다. 실제 결제나 메일 발송은 발생하지 않습니다.</p>
  <p id="message" role="status" aria-live="polite"></p>
  <button id="mail" type="button">내 이메일로 알림 작업 등록</button>
  <button id="checkout" type="button">테스트 결제 세션 만들기</button>
  <button id="events" type="button">작업 알림 연결</button><pre id="jobs"></pre>
</Desk>
<script>
  import { api, show } from '../client/api.mjs';
  for (const [id, path] of [['mail', '/api/mail'], ['checkout', '/api/checkout']]) {
    const button = document.getElementById(id) as HTMLButtonElement;
    button.onclick = async () => { button.disabled = true; try { const { data } = await api(path, { method: 'POST', body: JSON.stringify({ key: crypto.randomUUID() }) });
      show(JSON.stringify(data)); if (data.url) { const a = document.createElement('a'); a.textContent = '테스트 결제 화면 열기'; a.href = data.url; document.querySelector('#message')!.append(a); }
    } catch (e) { show(e); } finally { button.disabled = false; } };
  }
  let events: EventSource | undefined;
  document.getElementById('events')!.onclick = () => {
    events?.close(); events = new EventSource('/api/events');
    events.addEventListener('jobs', event => { document.getElementById('jobs')!.textContent = (event as MessageEvent).data; });
    events.onerror = () => show('알림 연결을 확인하세요. 로그인 만료 시 다시 로그인하세요.');
  };
  window.addEventListener('pagehide', () => events?.close());
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
| 11 | 브라우저에서 실행할 이벤트·DOM 코드의 경계를 정한다. |
| 12 | `'../client/api.mjs'`의 기능을 이 파일에서 사용한다. |
| 13 | 목록 또는 스트림의 남은 항목을 순서대로 처리한다. |
| 14 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const button`. |
| 15 | 브라우저 이벤트가 발생했을 때 실행할 함수를 연결한다. |
| 16 | 문자열을 HTML로 실행하지 않고 텍스트로 표시해 XSS 표면을 줄인다. |
| 17 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 18 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 19 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let events: EventSource &#124; undefined;`. |
| 20 | 브라우저 이벤트가 발생했을 때 실행할 함수를 연결한다. |
| 21 | 사용이 끝난 스트림·소켓·DB 자원을 종료하거나 잠금을 해제한다. |
| 22 | 문자열을 HTML로 실행하지 않고 텍스트로 표시해 XSS 표면을 줄인다. |
| 23 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `events.onerror = () => show('알림 연결을 확인하세요. 로그인 만료 시 다시 로그인하세요.');`. |
| 24 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 25 | 브라우저 이벤트가 발생했을 때 실행할 함수를 연결한다. |
| 26 | 브라우저에서 실행할 이벤트·DOM 코드의 경계를 정한다. |

## ④ 🔗 연동 포인트

브라우저→Astro API→메일/Stripe/GitHub의 서버 호출로 이어진다. 파일→개인 문서 레코드→study18의 AI 입력으로 연결한다. 외부 키 없이 mock으로 로컬 전체 흐름을 확인하고 live는 별도 테스트 계정에서 검증한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| OAuth 400 | state/callback/쿠키 host 불일치 | 등록 URL과 실제 호스트 맞추기 |
| Stripe 400 | 웹훅 원문 변형·서명 불일치 | raw body와 webhook secret 확인 |
| 메일 502 | 발신 도메인/제공자 실패 | 서버 설정과 제공자 로그 확인 |

## ⑥ 직접 해보기

1. mock 메일 작업과 checkout 응답에서 완료 여부가 false인지 확인한다.
2. 100000바이트를 넘는 파일과 다른 계정 문서 다운로드가 거절되는지 확인한다.
3. OAuth callback의 state를 바꿔 400이 되는지 확인한다.

## ⑦ ☐ 체크리스트

- [ ] 메일·결제·파일·OAuth 호출 코드를 읽고 mock/live를 구분했다.
- [ ] OAuth state·PKCE와 다운로드 소유권을 검증한다.
- [ ] 웹훅 서명·원문·이벤트 중복과 결제 요청 key를 확인했다.
- [ ] 서비스 키·콜백·발신 도메인 설정 후 실제 테스트 계정 검증을 수행한다.

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study14.md](study14.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
