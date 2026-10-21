# study0. Astro 기초이론

Notion 페이지 [Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f)의 방향은 이렇습니다. 콘텐츠 중심 메타 프레임워크이고, 정적 사이트가 기본입니다. 필요한 부분만 React, Vue, Svelte 섬을 붙입니다.

[Ruby on Rails](https://app.notion.com/p/3fcd7dec5e2e816dba83e4c93c0a011c) 학습과 결은 같습니다. 한 진도에 한 가지를 코드로 확인하고, 마지막에 작은 웹사이트로 다시 조립합니다. 옮기는 대상은 다릅니다. Rails는 약속으로 CRUD를 빨리 만드는 서버 프레임워크이고, Astro는 글을 먼저 HTML로 구워 두고 상호작용만 골라 붙이는 사이트 프레임워크입니다.

이 문서는 명령을 치기 전에 지도를 그리는 단계입니다. 코드는 다음 문서부터 `demo/`에 쌓입니다.

## 1. Astro란?

Astro는 콘텐츠 사이트를 만드는 웹 프레임워크입니다. 페이지, 레이아웃, 마크다운, 이미지, 엔드포인트가 한 프로젝트에 있습니다. 브라우저로 내려가는 JavaScript는 기본이 0입니다. 버튼이나 입력처럼 브라우저가 필요한 조각만 섬(island)으로 남깁니다.

한 문장이 설계의 중심입니다.

- **필요한 곳만 하이드레이션한다.** 본문, 목록, 레이아웃은 서버(또는 빌드)에서 HTML로 끝납니다. `client:` 지시어가 붙은 컴포넌트만 React, Vue, Svelte 런타임을 받습니다.

Rails의 "Convention over Configuration"에 대응하면, Astro의 약속은 **파일 위치**입니다. `src/pages` 아래 파일이 URL이 되고, `src/content` 아래 글이 컬렉션이 됩니다. 컨트롤러 클래스와 라우트 파일을 따로 맞출 필요가 없습니다.

### 다른 프레임워크와 비교

| 관심사 | Astro | Next.js | Rails |
|---|---|---|---|
| 기본 결과물 | 빌드 때 만든 정적 HTML | 요청마다 또는 빌드 때 만든 React 트리 | 요청마다 렌더하는 MVC 앱 |
| 화면 언어 | `.astro` (앞부분 스크립트 + HTML 템플릿) | React JSX | ERB 템플릿 |
| 상호작용 | 섬. React/Vue/Svelte를 골라 붙임 | 클라이언트 컴포넌트 | Turbo/Stimulus 또는 별도 JS/TS 화면 |
| 글 목록 | 콘텐츠 컬렉션 (Markdown, MDX) | 서버에서 DB/파일을 읽음 | Active Record + `resources` |
| 데이터 변경 | 엔드포인트 또는 온디맨드 페이지 | Route Handler, Server Action | 컨트롤러 액션 |
| JS 기본량 | 0. 섬만 추가 | React 런타임이 기본 | 템플릿이면 거의 0 |

Next.js, Nuxt, SvelteKit은 **앱 엔진**입니다. 페이지 대부분이 서버와 클라이언트를 오갑니다. Astro는 **정적 사이트가 본업**입니다. 블로그, 문서, 마케팅 페이지, 학습 노트처럼 읽기가 많은 곳에 맞습니다. 로그인 세션과 작성 화면이 사이트 전부인 서비스는 Next나 Rails가 더 짧습니다. 이 저장소는 그 경계를 코드로 확인하는 것이 목표입니다.

## 2. `.astro` 파일 하나의 모양

컴포넌트 파일은 두 칸입니다. `---`로 감싼 앞부분(frontmatter)은 빌드 또는 요청 때 서버에서 실행됩니다. 그 아래는 HTML 템플릿입니다.

```astro
---
const title = "학습 메모";
const items = ["정적 HTML", "섬", "콘텐츠 컬렉션"];
---
<h1>{title}</h1>
<ul>
  {items.map((item) => <li>{item}</li>)}
</ul>
```

앞부분에서 `fs`로 파일을 읽거나 비밀 환경 변수를 써도, 그 코드는 브라우저 번들에 들어가지 않습니다. Rails 컨트롤러의 인스턴스 변수가 뷰로 넘어가는 흐름과 비슷하고, 차이는 컨트롤러와 뷰가 **한 파일**이라는 점입니다.

템플릿의 `{표현식}`은 JavaScript입니다. HTML 태그는 JSX처럼 소문자가 아니라 그냥 HTML입니다. 컴포넌트만 대문자로 가져옵니다.

## 3. 페이지, 레이아웃, 라우팅

| 파일 | URL |
|---|---|
| `src/pages/index.astro` | `/` |
| `src/pages/about.astro` | `/about` |
| `src/pages/posts/index.astro` | `/posts` |
| `src/pages/posts/[slug].astro` | `/posts/어떤-값` |
| `src/pages/api/posts.json.js` | `/api/posts.json` |
| `src/pages/404.astro` | 없는 주소 |

Next의 `app/` 라우터와 달리 레이아웃은 폴더에 자동으로 감싸이지 않습니다. 페이지가 `import Base from '../layouts/Base.astro'` 하고 `<Base>…</Base>`로 감쌉니다. 레이아웃의 빈칸은 `<slot />`입니다.

`public/`에 둔 파일은 가공 없이 그대로 URL이 됩니다. `src/` 안에서 import한 이미지는 빌드가 처리합니다.

## 4. 정적 생성과 하이드레이션

기본 `output`은 `'static'`입니다. `astro build`가 페이지마다 HTML 파일을 만듭니다. 서버가 요청마다 템플릿을 돌리지 않습니다.

브라우저 JavaScript가 필요한 컴포넌트만 지시어를 붙입니다.

| 지시어 | 언제 섬이 깨어나나 |
|---|---|
| `client:load` | 페이지 로드 직후 |
| `client:idle` | 브라우저가 한가할 때 |
| `client:visible` | 화면에 들어올 때 |
| `client:media` | CSS 미디어 쿼리가 맞을 때 |
| `client:only` | 서버 HTML 없이 브라우저에서만 |

지시어가 없으면 그 컴포넌트는 HTML만 남고 이벤트 핸들러는 동작하지 않습니다. 이것이 Rails 화면의 "그냥 템플릿"과 같고, 지시어를 붙인 순간 Next의 클라이언트 컴포넌트에 가까워집니다.

요청마다 다른 HTML이 필요하면 어댑터를 설치하고 그 파일에만 `export const prerender = false`를 둡니다. 나머지 페이지는 계속 정적입니다. 사이트 전체가 동적일 때만 `output: 'server'`를 씁니다. Notion의 "정적 vs 동적 경계"는 이 한 줄로 가릅니다.

## 5. 섬은 프레임워크를 고른다

Astro 템플릿만으로 클릭 카운터를 만들 수는 있습니다. 다만 이미 익힌 React, Vue, Svelte 컴포넌트를 재사용하려면 공식 통합을 넣습니다.

```astro
<ReactCounter client:load label="React" />
<VueCounter client:visible label="Vue" />
<SvelteCounter client:idle label="Svelte" />
```

세 컴포넌트는 한 페이지에 같이 있을 수 있습니다. 런타임도 그 섬만 받습니다. 이 저장소에서는 소스를 Astro 폴더 안에 섞지 않습니다.

| 폴더 | 하는 일 |
|---|---|
| `react/demo`, `react/project` | React 섬만 |
| `vue/demo`, `vue/project` | Vue 섬만 |
| `svelte/demo`, `svelte/project` | Svelte 섬만 |

Rails 학습에서 `js/`, `ts/`가 API를 부르는 독립 화면이었던 자리에, 여기서는 **섬 소스 폴더**가 있습니다. 페이지와 라우트는 `demo/`와 `project/`만 수정합니다.

## 6. 콘텐츠 컬렉션

글이 여러 개이고 앞부분(frontmatter) 모양이 같으면 `src/content.config.ts`에 컬렉션을 정의합니다.

```ts
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const posts = defineCollection({
  loader: glob({ base: './src/content/posts', pattern: '**/*.{md,mdx}' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
  }),
});

export const collections = { posts };
```

페이지는 `getCollection('posts')`로 목록을 얻고, `render(entry)`가 돌려준 `<Content />`로 본문을 찍습니다. Markdown이 기본이고, MDX는 본문 안에 컴포넌트를 넣을 때 추가합니다.

Rails의 `Post` 모델 + 마이그레이션에 대응하면, 여기는 **스키마가 있는 마크다운 폴더**입니다. 데이터베이스가 아닙니다. 글이 빌드 전에 파일로 확정되는 사이트에 맞습니다. 방문할 때마다 바뀌는 방명록은 컬렉션이 아니라 엔드포인트와 JSON 파일로 둡니다.

## 7. 엔드포인트

`src/pages` 아래 `.js` 또는 `.ts` 파일이 `GET`, `POST`를 export하면 URL이 API가 됩니다. Rails의 `namespace :api`와 역할이 같습니다. 차이는 라우트 파일을 따로 열지 않고, 파일 경로가 주소라는 점입니다.

정적 엔드포인트는 빌드 때 JSON을 구워 둡니다. 폼으로 글을 추가하려면 그 파일에 `prerender = false`가 필요하고, Node 어댑터가 그 요청을 받습니다.

## 8. 이 커리큘럼의 로드맵

Notion 학습 목표를 진도에 이렇게 나눕니다.

| 문서 | 확인하는 것 | Notion 목표 |
|---|---|---|
| study0 | 이 문서. 코드 없음 | 방향 |
| study1 | `npm create astro`, 스크립트, 첫 HTML | Astro 프로젝트 |
| study2 | `src/pages` 라우트, 동적 세그먼트, 404 | 프로젝트 구조 |
| study3 | `.astro` props, slot, 레이아웃 | `.astro` 컴포넌트 / 레이아웃 |
| study4 | `client:` 지시어, React/Vue/Svelte 각 1개 | 정적 vs 하이드레이션, 섬 |
| study5 | 콘텐츠 컬렉션, Markdown, MDX 한 편 | 콘텐츠 컬렉션 / MDX |
| study6 | `GET` 엔드포인트로 목록 JSON | 서버 엔드포인트 |
| study7 | 폼 `POST`로 방명록 추가 | 엔드포인트로 데이터 받기 |
| study8 | 어댑터, `prerender = false`, 쿠키 | 정적 vs 동적 경계 |
| study9 | 환경 변수, 이미지, 문서 제목, 화면 전환 | 사이트 품질 |
| study10 | `astro build`, Node로 서빙, Docker | 빌드 |
| studyFinal | 위 내용을 다른 폴더 구조의 작은 사이트로 | 정적 랜딩 + 목록 |

demo의 소재는 **학습 글 목록 + 방명록**입니다. studyFinal은 같은 부품으로 **메모 데스크**를 다시 만듭니다. 주소와 폴더 이름이 demo와 다릅니다.

## 9. 실습을 시작하기 전에 기억할 것

- 페이지에 `client:`가 없으면 그 페이지의 프레임워크 런타임은 0입니다.
- 비밀값은 앞부분과 엔드포인트에만 둡니다. `PUBLIC_`으로 시작하는 환경 변수만 브라우저에 갑니다.
- React 파일을 Vue 폴더에 넣지 않습니다. 세 폴더는 서로 수정하지 않습니다.
- `node_modules`, `.astro`, `dist`, `.env`, 실행 중에 쌓이는 `data/guestbook.json`은 커밋하지 않습니다.
