# study8 · 구조화·재사용

## ① 목표 한 줄

서버·브라우저·설정·저장소의 역할을 나누고 실행 환경을 분리한다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

모든 파일을 pages에 넣으면 URL 처리·검증·SQL·화면 로직이 섞인다. pages는 요청 진입점, lib는 서버 기능, client는 브라우저 기능, layouts/components는 화면 부품으로 나눈다. 설정은 settings 함수 한 곳에서 기본값과 환경변수 우선순위를 정한다.

이 구조는 주방의 주문 접수·조리·창고를 나누는 것과 비슷하다. HTTP handler가 실제 DB 종류를 몰라도 저장 계약으로 일하고, 테스트가 가짜 저장소를 주입할 수 있다. 서버 전용 모듈을 client에서 import하면 비밀이나 Node 의존성이 브라우저로 넘어갈 수 있으므로 파일 경계를 지킨다.

## ③ 🛠️ 실기

기본 폴더 구조는 아래와 같다.

```text
course/
  src/pages/       화면·API URL
  src/layouts/     공통 HTML
  src/components/  props·slot 부품
  src/client/      DOM·fetch·상태
  src/lib/         검증·인증·저장소·서비스
  src/content/     MD·MDX 원본
  public/          OpenAPI 문서
  scripts/         worker·백업·MCP·측정
  tests/           도메인·브라우저 검증
```

HTTP 오류는 HttpError로만 사용자 메시지를 드러내며 예상하지 못한 오류는 requestId와 서버 로그를 남긴다. 호출자가 준 요청 ID는 문자·숫자·하이픈 등 제한된 100자만 허용한다. 비밀번호·토큰·문서 본문은 로그에 쓰지 않는다.

### `course/src/lib/config.mjs` 전체 코드

[config.mjs](course/src/lib/config.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
export function settings(env = process.env) {
  return {
    site: env.SITE_URL || 'http://127.0.0.1:4323',
    driver: env.DB_DRIVER || 'sqlite',
    database: env.DATABASE_URL || './data/desk.sqlite',
    cors: env.CORS_ORIGIN || 'http://127.0.0.1:4323',
    production: env.NODE_ENV === 'production',
  };
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 2 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 3 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `site: env.SITE_URL &#124;&#124; 'http://127.0.0.1:4323',`. |
| 4 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `driver: env.DB_DRIVER &#124;&#124; 'sqlite',`. |
| 5 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `database: env.DATABASE_URL &#124;&#124; './data/desk.sqlite',`. |
| 6 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `cors: env.CORS_ORIGIN &#124;&#124; 'http://127.0.0.1:4323',`. |
| 7 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `production: env.NODE_ENV === 'production',`. |
| 8 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 9 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/src/lib/http.mjs` 전체 코드

[http.mjs](course/src/lib/http.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { randomUUID } from 'node:crypto';

export class HttpError extends Error {
  constructor(status, code, message, fields = {}) {
    super(message);
    Object.assign(this, { status, code, fields });
  }
}
export const fail = (status, code, message, fields) => { throw new HttpError(status, code, message, fields); };
export const json = (value, status = 200, headers = {}) => new Response(JSON.stringify(value), {
  status, headers: { 'Content-Type': 'application/json; charset=utf-8', ...headers },
});
export async function body(request, max = 65536) {
  if (!request.headers.get('content-type')?.includes('application/json')) fail(400, 'BAD_REQUEST', 'JSON 본문을 보내세요.');
  const reader = request.body?.getReader();
  if (!reader) fail(400, 'BAD_REQUEST', '본문이 없습니다.');
  let size = 0;
  const chunks = [];
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > max) { await reader.cancel(); fail(413, 'PAYLOAD_TOO_LARGE', '본문이 너무 큽니다.'); }
    chunks.push(value);
  }
  try { return JSON.parse(Buffer.concat(chunks).toString('utf8')); }
  catch { fail(400, 'BAD_REQUEST', 'JSON 문법을 확인하세요.'); }
}
export function errorResponse(error, requestId = randomUUID()) {
  const known = error instanceof HttpError;
  if (!known) console.error(JSON.stringify({ level: 'error', requestId, message: String(error) }));
  return json({ error: {
    code: known ? error.code : 'INTERNAL', message: known ? error.message : '서버 오류입니다.',
    fields: known ? error.fields : {}, requestId,
  } }, known ? error.status : 500, { 'X-Request-Id': requestId });
}
export function positiveId(value) {
  if (!/^\d+$/.test(value || '') || !Number.isSafeInteger(Number(value)) || Number(value) < 1) fail(400, 'BAD_REQUEST', '양의 정수 id가 필요합니다.');
  return Number(value);
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'node:crypto'`의 기능을 이 파일에서 사용한다. |
| 2 | 코드 구간을 나누는 빈 줄이다. |
| 3 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `export class HttpError extends Error {`. |
| 4 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `constructor(status, code, message, fields = {}) {`. |
| 5 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `super(message);`. |
| 6 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `Object.assign(this, { status, code, fields });`. |
| 7 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 8 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 9 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `export const fail`. |
| 10 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 11 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `status, headers: { 'Content-Type': 'application/json; charset=utf-8', ...headers },`. |
| 12 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 13 | 비동기 함수 `body`의 입력과 처리 범위를 정의한다. |
| 14 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 15 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const reader`. |
| 16 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 17 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let size`. |
| 18 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const chunks`. |
| 19 | 목록 또는 스트림의 남은 항목을 순서대로 처리한다. |
| 20 | 다음 스트림 조각 또는 생성 토큰을 비동기로 읽는다. |
| 21 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 22 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `size += value.byteLength;`. |
| 23 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 24 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `chunks.push(value);`. |
| 25 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 26 | JSON 문자열을 객체로 해석한다. 잘못된 입력은 상위 오류 처리로 넘긴다. |
| 27 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 28 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 29 | 예측하기 어려운 식별자·토큰·salt를 생성한다. |
| 30 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const known`. |
| 31 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 32 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 33 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `code: known ? error.code : 'INTERNAL', message: known ? error.message : '서버 오류입니다.',`. |
| 34 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `fields: known ? error.fields : {}, requestId,`. |
| 35 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `} }, known ? error.status : 500, { 'X-Request-Id': requestId });`. |
| 36 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 37 | 재사용 함수 `positiveId`를 정의한다. |
| 38 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 39 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 40 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

## ④ 🔗 연동 포인트

개발은 `.env`, 운영은 호스팅 환경변수 또는 compose env_file로 설정한다. `npm start`는 Node의 env-file 옵션으로 .env를 읽고, 빌드용 PUBLIC 값은 빌드 시 확정된다. 다음 단계는 이 모듈 경계를 이용해 테스트를 작성한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 서버에서 비밀값 없음 | 런타임 env 미주입 | npm start env-file/호스팅 설정 확인 |
| 브라우저에 Node 모듈 오류 | client에서 서버 모듈 import | 파일 경계 분리 |

## ⑥ 직접 해보기

1. 다른 포트용 SITE_URL·PORT·CORS_ORIGIN을 함께 바꾼다.
2. 서버 비밀값을 PUBLIC_로 만들면 어떤 위험이 있는지 기록한다.
3. settings에 새 설정을 추가하고 호출부에서 직접 process.env 접근을 줄여 본다.

## ⑦ ☐ 체크리스트

- [ ] pages/lib/client/components/layouts/content/scripts/tests의 책임을 구분했다.
- [ ] 공통 HTTP·검증·설정 모듈을 재사용했다.
- [ ] 개발·운영 환경과 빌드·런타임 환경변수를 구분했다.

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study9.md](study9.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
