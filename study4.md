# study4 · 라우팅과 요청 처리

## ① 목표 한 줄

파일 라우트·동적 경로·쿼리·404를 연결한다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

`src/pages/index.astro`는 `/`, `board.astro`는 `/board`, `notes/[id].astro`는 `/notes/값`이다. 동적이라는 말이 항상 요청마다 렌더한다는 뜻은 아니다. 정적 동적 경로는 `getStaticPaths()`가 빌드할 값들을 반환한다. 요청 시 엔드포인트는 `prerender = false`로 실행한다.

URL은 도서관의 서가 주소다. pathname은 책 위치, query는 검색·정렬 조건이다. `URLSearchParams`로 값을 인코딩하면 공백·한글이 포함돼도 안전하다. 링크는 `<a href>`로 이동하고, 검색 상태만 바꿀 때 `history.replaceState`를 사용할 수 있다. 없는 화면은 404 페이지로, 없는 API는 공통 JSON 404로 응답한다.

## ③ 🛠️ 실기

콘텐츠 컬렉션은 파일을 DB처럼 수정하는 도구가 아니다. `glob()`이 MD·MDX를 읽고 zod 스키마가 title·description을 검증한다. MDX의 컴포넌트도 빌드 시 HTML이 된다. 콘텐츠를 바꾸면 다시 빌드한다. API catch-all은 HTTP 메소드와 경로를 공통 dispatcher에 넘긴다. 정적 콘텐츠와 DB 게시글 경로를 `/notes`와 `/api/posts`로 분리한다.

### `course/src/pages/notes/[id].astro` 전체 코드

[[id].astro](course/src/pages/notes/[id].astro)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```astro
---
import { getCollection, render } from 'astro:content';
import Desk from '../../layouts/Desk.astro';
export async function getStaticPaths() {
  return (await getCollection('notes')).map(note => ({ params: { id: note.id }, props: { note } }));
}
const { note } = Astro.props;
const { Content } = await render(note);
---
<Desk title={note.data.title}><Content /></Desk>
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 2 | `'astro:content'`의 기능을 이 파일에서 사용한다. |
| 3 | `'../../layouts/Desk.astro'`의 기능을 이 파일에서 사용한다. |
| 4 | 정적 생성에서 빌드할 동적 URL 목록을 정의한다. |
| 5 | 목록의 각 항목을 화면 또는 응답에 필요한 모양으로 변환한다. |
| 6 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 7 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { note }`. |
| 8 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { Content }`. |
| 9 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 10 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |

### `course/src/content.config.ts` 전체 코드

[content.config.ts](course/src/content.config.ts)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```typescript
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const notes = defineCollection({
  loader: glob({ base: './src/content/notes', pattern: '**/*.{md,mdx}' }),
  schema: z.object({ title: z.string(), description: z.string() }),
});
export const collections = { notes };
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'astro:content'`의 기능을 이 파일에서 사용한다. |
| 2 | `'astro/loaders'`의 기능을 이 파일에서 사용한다. |
| 3 | `'astro/zod'`의 기능을 이 파일에서 사용한다. |
| 4 | 코드 구간을 나누는 빈 줄이다. |
| 5 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const notes`. |
| 6 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `loader: glob({ base: './src/content/notes', pattern: '**/*.{md,mdx}' }),`. |
| 7 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 8 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 9 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `export const collections`. |

### `course/src/content/notes/welcome.mdx` 전체 코드

[welcome.mdx](course/src/content/notes/welcome.mdx)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```mdx
---
title: Astro 콘텐츠 노트
description: 빌드 시 콘텐츠와 실행 중 DB 데이터의 경계
---
import NoteCard from '../../components/NoteCard.astro';

# 파일은 빌드 전에 준비합니다

이 본문은 콘텐츠 컬렉션에서 읽어 정적 HTML로 만듭니다.

<NoteCard title="실시간 게시판" href="/board">
  <p>방문자가 쓰는 글은 API와 DB에 저장합니다.</p>
</NoteCard>
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 2 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `title: Astro 콘텐츠 노트`. |
| 3 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `description: 빌드 시 콘텐츠와 실행 중 DB 데이터의 경계`. |
| 4 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 5 | `'../../components/NoteCard.astro'`의 기능을 이 파일에서 사용한다. |
| 6 | 코드 구간을 나누는 빈 줄이다. |
| 7 | 파일은 빌드 전에 준비합니다 |
| 8 | 코드 구간을 나누는 빈 줄이다. |
| 9 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `이 본문은 콘텐츠 컬렉션에서 읽어 정적 HTML로 만듭니다.`. |
| 10 | 코드 구간을 나누는 빈 줄이다. |
| 11 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 12 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 13 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |

### `course/src/pages/404.astro` 전체 코드

[404.astro](course/src/pages/404.astro)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```astro
---
import Desk from '../layouts/Desk.astro';
---
<Desk title="페이지 없음"><h1>404 · 페이지가 없습니다</h1><a href="/">홈으로</a></Desk>
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 2 | `'../layouts/Desk.astro'`의 기능을 이 파일에서 사용한다. |
| 3 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 4 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |

### `course/src/pages/api/[...path].js` 전체 코드

[[...path].js](course/src/pages/api/[...path].js)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { dispatch } from '../../lib/api.mjs';
import { getStore } from '../../lib/store.mjs';

export const prerender = false;
export const ALL = async context => dispatch(context, await getStore());
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'../../lib/api.mjs'`의 기능을 이 파일에서 사용한다. |
| 2 | `'../../lib/store.mjs'`의 기능을 이 파일에서 사용한다. |
| 3 | 코드 구간을 나누는 빈 줄이다. |
| 4 | 이 경로를 빌드 시 고정하지 않고 요청마다 실행한다. |
| 5 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `export const ALL`. |

## ④ 🔗 연동 포인트

화면 `/board?q=astro&page=1`의 검색 조건을 `/api/posts?q=astro&page=1&limit=5`로 그대로 전달한다. 파일 이름과 호출 주소가 같은 계약인지 확인한다. 다음 단계에서 이 요청 경로에 폼 입력을 보낸다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 정적 경로 빌드 실패 | getStaticPaths 없음 | 생성할 id 반환 |
| API 404 | 파일 경로·호출 주소 불일치 | /api 경로 대조 |
| 콘텐츠 동기화 실패 | frontmatter 필드 누락 | title·description 수정 |

## ⑥ 직접 해보기

1. `/notes/welcome`, `/없는주소`의 상태 코드를 확인한다.
2. 쿼리 `q`에 한글·공백을 넣고 새로고침한다.
3. 콘텐츠 노트 파일 하나를 추가하고 빌드해 새 경로를 만든다.

## ⑦ ☐ 체크리스트

- [ ] 파일 이름에서 URL을 찾을 수 있다.
- [ ] `getStaticPaths`와 `prerender = false`의 차이를 설명했다.
- [ ] query 인코딩·404·페이지 이동을 확인했다.

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study5.md](study5.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
