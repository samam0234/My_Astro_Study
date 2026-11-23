# study5 · 폼·입력·검증

## ① 목표 한 줄

브라우저 검증과 서버 검증을 연결하고 중복 제출을 막는다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

HTML의 `required`, `minlength`, `maxlength`, `type=email`은 사용자가 빠르게 실수를 고치도록 돕는다. 네트워크 요청을 직접 만드는 사람은 이를 우회할 수 있으므로 서버에서 zod로 다시 검증한다. strict 스키마는 예상하지 않은 필드를 거절한다.

클라이언트 검증은 접수 창구의 안내, 서버 검증은 실제 심사다. 제출 중 busy 플래그와 버튼 비활성화로 같은 폼의 연속 클릭을 막는다. 재시도에 따른 서버 중복 결제까지 이 방식으로 보장되는 것은 아니므로 study13에서 idempotency key를 추가한다. 오류는 `textContent`로 표시해 HTML로 실행하지 않는다.

## ③ 🛠️ 실기

`/auth`의 가입·로그인 폼 또는 `/board`의 editor 폼에 값을 넣는다. API와 인증은 다음 두 단계에서 완성한다. 이번 진도는 폼 연결과 입력 계약을 먼저 읽는다. 제출 중에는 submit 버튼만 잠그므로 AI 화면의 중단 버튼 같은 일반 버튼은 계속 사용할 수 있다. HTTP 204는 JSON 파싱하지 않는다.

### `course/src/client/api.mjs` 전체 코드

[api.mjs](course/src/client/api.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { formSchemas } from './schemas.mjs';
export function show(value) {
  const target = document.querySelector('#message');
  if (target) target.textContent = value instanceof Error ? value.message : String(value);
}
export async function api(path, options = {}) {
  const response = await fetch(path, { credentials: 'same-origin', ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers } });
  if (response.status === 204) return null;
  const result = await response.json();
  if (!response.ok) {
    const fields = result.error?.fields || {};
    const detail = Object.entries(fields).map(([name, errors]) => `${name}: ${errors.join(', ')}`).join(' / ');
    const message = [200, 201].includes(response.status) ? '완료' : response.status === 422 ? '입력 형식을 확인하세요.' : result.error?.message || '요청 실패';
    throw new Error(`${response.status} ${message}${detail ? ` (${detail})` : ''}`);
  }
  return result;
}
export function formAction(selector, action) {
  const form = document.querySelector(selector);
  let busy = false;
  form.addEventListener('submit', async event => {
    event.preventDefault(); if (busy || !form.reportValidity()) return;
    busy = true; const buttons = [...form.querySelectorAll('button:not([type=button])')]; buttons.forEach(b => b.disabled = true);
    try {
      const values = Object.fromEntries(new FormData(form)), schema = formSchemas[selector];
      const checked = schema?.safeParse(values);
      if (checked && !checked.success) throw new Error(checked.error.issues.map(issue => `${issue.path.join('.')}: ${issue.message}`).join(' / '));
      await action(checked ? checked.data : values);
    }
    catch (error) { show(error); }
    finally { busy = false; buttons.forEach(b => b.disabled = false); }
  });
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'./schemas.mjs'`의 기능을 이 파일에서 사용한다. |
| 2 | 재사용 함수 `show`를 정의한다. |
| 3 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const target`. |
| 4 | 문자열을 HTML로 실행하지 않고 텍스트로 표시해 XSS 표면을 줄인다. |
| 5 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 6 | 비동기 함수 `api`의 입력과 처리 범위를 정의한다. |
| 7 | HTTP 요청을 보내 응답을 기다린다. 주입된 fetcher는 테스트에서 대체할 수 있다. |
| 8 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `headers: { 'Content-Type': 'application/json', ...options.headers } });`. |
| 9 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 10 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const result`. |
| 11 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 12 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const fields`. |
| 13 | 목록의 각 항목을 화면 또는 응답에 필요한 모양으로 변환한다. |
| 14 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const message`. |
| 15 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `throw new Error(${response.status} ${message}${detail ?  (${detail}) : ''});`. |
| 16 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 17 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 18 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 19 | 재사용 함수 `formAction`를 정의한다. |
| 20 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const form`. |
| 21 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let busy`. |
| 22 | 브라우저 이벤트가 발생했을 때 실행할 함수를 연결한다. |
| 23 | 기본 폼 이동을 막고 비동기 요청 흐름을 사용한다. |
| 24 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `busy = true; const buttons = [...form.querySelectorAll('button:not([type=button])')]; buttons.forEach(b => b.d`. |
| 25 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `try {`. |
| 26 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const values`. |
| 27 | 정해진 스키마로 입력을 검사하고 허용된 값만 다음 계층으로 보낸다. |
| 28 | 목록의 각 항목을 화면 또는 응답에 필요한 모양으로 변환한다. |
| 29 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await action(checked ? checked.data : values);`. |
| 30 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 31 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 32 | 성공·실패에 관계없이 연결/잠금 등 정리 작업을 실행한다. |
| 33 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 34 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/src/lib/validation.mjs` 전체 코드

[validation.mjs](course/src/lib/validation.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { z } from 'zod';
import { fail } from './http.mjs';

export const postSchema = z.object({
  title: z.string().trim().min(1).max(200),
  body: z.string().trim().min(1).max(20000),
  tags: z.array(z.string().trim().min(1).max(30)).max(10).default([]),
}).strict();
export const signupSchema = z.object({
  email: z.email().max(254).transform(value => value.toLowerCase()),
  password: z.string().min(10).max(128), nickname: z.string().trim().min(1).max(40),
}).strict();
export const loginSchema = signupSchema.pick({ email: true, password: true });
export function validate(schema, input) {
  const result = schema.safeParse(input);
  if (!result.success) {
    const fields = {};
    for (const issue of result.error.issues) (fields[issue.path.join('.') || '_form'] ??= []).push(issue.message);
    fail(400, 'VALIDATION_ERROR', '입력값을 확인하세요.', fields);
  }
  return result.data;
}
export function listQuery(url) {
  const pageText = url.searchParams.get('page') ?? '1';
  const limitText = url.searchParams.get('limit') ?? '10';
  if (!/^\d+$/.test(pageText) || !/^\d+$/.test(limitText)) fail(400, 'VALIDATION_ERROR', 'page와 limit은 정수입니다.');
  const page = Number(pageText), limit = Math.min(50, Number(limitText));
  const sort = url.searchParams.get('sort') || '-createdAt';
  if (!Number.isSafeInteger(page) || page < 1 || limit < 1 || !Number.isSafeInteger(Number(limitText)) || !['createdAt', '-createdAt', '-commentCount'].includes(sort)) fail(400, 'VALIDATION_ERROR', '페이지 또는 정렬을 확인하세요.');
  return { page, limit, sort, q: (url.searchParams.get('q') || '').slice(0, 200) };
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'zod'`의 기능을 이 파일에서 사용한다. |
| 2 | `'./http.mjs'`의 기능을 이 파일에서 사용한다. |
| 3 | 코드 구간을 나누는 빈 줄이다. |
| 4 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `export const postSchema`. |
| 5 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `title: z.string().trim().min(1).max(200),`. |
| 6 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `body: z.string().trim().min(1).max(20000),`. |
| 7 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `tags: z.array(z.string().trim().min(1).max(30)).max(10).default([]),`. |
| 8 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `}).strict();`. |
| 9 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `export const signupSchema`. |
| 10 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `email: z.email().max(254).transform(value => value.toLowerCase()),`. |
| 11 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `password: z.string().min(10).max(128), nickname: z.string().trim().min(1).max(40),`. |
| 12 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `}).strict();`. |
| 13 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `export const loginSchema`. |
| 14 | 정해진 스키마로 입력을 검사하고 허용된 값만 다음 계층으로 보낸다. |
| 15 | 정해진 스키마로 입력을 검사하고 허용된 값만 다음 계층으로 보낸다. |
| 16 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 17 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const fields`. |
| 18 | 목록 또는 스트림의 남은 항목을 순서대로 처리한다. |
| 19 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 20 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 21 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 22 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 23 | 재사용 함수 `listQuery`를 정의한다. |
| 24 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const pageText`. |
| 25 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const limitText`. |
| 26 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 27 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const page`. |
| 28 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const sort`. |
| 29 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 30 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 31 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

## ④ 🔗 연동 포인트

formAction → JSON fetch → 서버 schema → 공통 응답 → status 메시지의 순서다. 공통 명세 v1은 검증 실패 400을 사용한다. 200은 로그인/수정, 201은 등록, 204는 본문 없는 성공이다. 422도 클라이언트에서 처리하고 브라우저 mock으로 확인하지만 자체 API가 422를 내지는 않는다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 204 JSON 파싱 오류 | 빈 응답을 json() 처리 | 204일 때 즉시 반환 |
| 중복 저장 | submit 기본 동작/중복 클릭 | preventDefault와 busy |
| 422 화면 이상 | 서버별 코드 차이 | 클라이언트 오류 분기와 mock 검사 |

## ⑥ 직접 해보기

1. 빈 제목·200자 초과 제목을 서버에 직접 보내 400 fields를 확인한다.
2. 버튼을 빠르게 연속 클릭해 요청이 하나인지 확인한다.
3. 브라우저 테스트의 422 mock을 500으로 바꿔 오류 메시지를 확인한다.

## ⑦ ☐ 체크리스트

- [ ] HTML과 서버 검증을 둘 다 사용했다.
- [ ] 400·422·200·201·204를 구분했다.
- [ ] 중복 제출 방지와 오류 표시를 구현했다.

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study6.md](study6.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
