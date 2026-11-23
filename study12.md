# study12 · 프론트·UI 연동

## ① 목표 한 줄

Astro 템플릿에 CSS UI·상태·폼 검증 라이브러리를 연결한다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

UI 라이브러리가 반드시 별도 화면 프레임워크일 필요는 없다. Pico CSS는 의미 있는 HTML 태그에 스타일을 주며 Astro 레이아웃에서 한 번 import한다. Nano Stores atom은 작은 브라우저 상태를 보관하고 subscribe로 DOM 표시를 갱신한다. zod는 서버와 폼에서 쓸 수 있는 스키마 검증 라이브러리다.

화면은 게시판, atom은 포스트잇 숫자판, zod는 접수 규칙에 비유할 수 있다. 서버 모듈의 전역 atom에 사용자 데이터를 넣으면 요청 사이에서 공유될 수 있으므로 상태 저장은 client 파일에서만 한다. formAction은 제출 제어, HTML은 기본 유효성, 서버 zod는 최종 검증을 담당한다.

Astro의 `client:load/idle/visible/media/only`는 지원되는 UI 컴포넌트를 하이드레이션하는 지시어다. 이 과정은 단독 Astro 조건을 지키므로 외부 화면 프레임워크 섬을 추가하지 않는다. `.astro`에는 client 지시어를 붙이지 않고 `<script>`로 이벤트를 연결한다.

## ③ 🛠️ 실기

설치는 package-lock에 포함되어 있어 `npm ci`만 실행한다. `/documents`에서 로그인한 사용자의 문서 목록이 로드되면 documentCount.set(data.length)가 실행된다. subscribe는 count 텍스트를 갱신한다. 이 페이지의 전체 구현은 study18에서 설명한다. 브라우저 상태가 곧 DB라고 가정하지 않고 목록을 다시 조회해 원본과 맞춘다.

### `course/src/client/state.mjs` 전체 코드

[state.mjs](course/src/client/state.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { atom } from 'nanostores';
export const documentCount = atom(0);
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'nanostores'`의 기능을 이 파일에서 사용한다. |
| 2 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `export const documentCount`. |

### `course/src/client/schemas.mjs` 전체 코드

[schemas.mjs](course/src/client/schemas.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { z } from 'zod';

const credentials = z.object({ email: z.email(), password: z.string().min(10).max(128) });
export const formSchemas = {
  '#login': credentials,
  '#signup': credentials.extend({ nickname: z.string().trim().min(1).max(40) }),
  '#editor': z.object({
    id: z.string().regex(/^$|^[1-9]\d*$/), title: z.string().trim().min(1).max(200),
    body: z.string().trim().min(1).max(20000), tags: z.string(),
  }),
};
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'zod'`의 기능을 이 파일에서 사용한다. |
| 2 | 코드 구간을 나누는 빈 줄이다. |
| 3 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const credentials`. |
| 4 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `export const formSchemas`. |
| 5 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 6 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 7 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 8 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `id: z.string().regex(/^$&#124;^[1-9]\d*$/), title: z.string().trim().min(1).max(200),`. |
| 9 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `body: z.string().trim().min(1).max(20000), tags: z.string(),`. |
| 10 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `}),`. |
| 11 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

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

### `course/src/layouts/Desk.astro` 전체 코드

[Desk.astro](course/src/layouts/Desk.astro)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```astro
---
import '@picocss/pico/css/pico.min.css';
const { title = 'Astro 학습 데스크' } = Astro.props;
const basic = import.meta.env.COURSE_STAGE === 'midpoint';
---
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width" />
    <meta name="description" content="Astro 하나로 만드는 학습 게시판과 문서 도우미" />
    <title>{title}</title>
    <style is:global>
      main { max-width: 960px; } nav { flex-wrap: wrap; } textarea { min-height: 8rem; }
      pre { white-space: pre-wrap; overflow-wrap: anywhere; padding: 1rem; }
      .muted { color: var(--pico-muted-color); } [role=status] { min-height: 1.5rem; }
      .actions { display: flex; gap: .6rem; flex-wrap: wrap; } article h2 { font-size: 1.4rem; }
    </style>
  </head>
  <body>
    <header class="container"><nav aria-label="주 메뉴">
      <ul><li><a href="/">Astro 데스크</a></li></ul>
      <ul>
        <li><a href="/lessons">기초</a></li><li><a href="/notes/welcome">콘텐츠</a></li>
        <li><a href="/board">게시판</a></li><li><a href="/auth">계정</a></li>
        {!basic && <><li><a href="/services">서비스</a></li><li><a href="/documents">문서 AI</a></li></>}
        <li><a href="/api-docs">API</a></li>
      </ul>
    </nav></header>
    <main class="container"><slot /></main>
    <footer class="container"><small>정적 콘텐츠와 요청 시 실행되는 API를 Astro로 연결합니다.</small></footer>
  </body>
</html>
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 2 | `import '@picocss/pico/css/pico.min.css'`의 기능을 이 파일에서 사용한다. |
| 3 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { title`. |
| 4 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 5 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 6 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 7 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 8 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 9 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 10 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 11 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 12 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 13 | 이 화면에 적용할 스타일 구간을 정한다. |
| 14 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `main { max-width: 960px; } nav { flex-wrap: wrap; } textarea { min-height: 8rem; }`. |
| 15 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `pre { white-space: pre-wrap; overflow-wrap: anywhere; padding: 1rem; }`. |
| 16 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `.muted { color: var(--pico-muted-color); } [role=status] { min-height: 1.5rem; }`. |
| 17 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `.actions { display: flex; gap: .6rem; flex-wrap: wrap; } article h2 { font-size: 1.4rem; }`. |
| 18 | 이 화면에 적용할 스타일 구간을 정한다. |
| 19 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 20 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 21 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 22 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 23 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 24 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 25 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 26 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 27 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 28 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 29 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 30 | 부모가 전달한 HTML을 이 slot 위치에 삽입한다. |
| 31 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 32 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 33 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |

## ④ 🔗 연동 포인트

Desk에서 Pico CSS → documents에서 DOM 이벤트 → state의 atom → count 표시로 이어진다. 폼 데이터는 공통 api 함수를 거쳐 서버 zod 검증으로 간다. 다음 단계는 외부 서비스의 실패·재시도를 처리한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 문서 수가 안 바뀜 | atom set 또는 subscribe 누락 | 서버 목록 후 set 확인 |
| client 지시어 오류 | .astro에 hydration 지시어 사용 | script 이벤트로 구현 |

## ⑥ 직접 해보기

1. Pico CSS를 제외한 빌드와 포함한 빌드의 화면을 확인한다.
2. atom을 구독하는 표시를 다른 컴포넌트에 하나 더 만든다.
3. 폼 입력에 zod safeParse를 추가해 서버와 같은 필드 규칙을 사전 안내한다.

## ⑦ ☐ 체크리스트

- [ ] UI CSS·브라우저 상태·폼 검증 라이브러리를 연결했다.
- [ ] 서버 전역 상태에 개인 데이터를 보관하지 않는다.
- [ ] client 지시어 개념과 이번 코드의 script 방식 차이를 이해했다.

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study13.md](study13.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
