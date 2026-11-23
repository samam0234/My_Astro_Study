# study2 · 핵심 구조

## ① 목표 한 줄

페이지·레이아웃·컴포넌트를 props와 slot으로 조립한다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

Astro의 화면 기본 단위는 `.astro` 컴포넌트다. `src/pages` 파일은 URL이 되지만 `components` 파일은 import해서 사용해야 나타난다. 레이아웃도 자동 적용되지 않으므로 페이지에서 `<Desk>...</Desk>`로 감싼다.

props는 부품을 주문할 때 적는 규격이고 slot은 부품 안에 남겨 둔 빈칸이다. `Astro.props`로 제목과 링크를 받고, 기본 `<slot />`으로 본문을 받는다. 이름 있는 slot은 부모의 `slot="meta"`와 자식의 `<slot name="meta" />`가 연결된다. 서버에서 props를 바꿔도 이미 전달된 브라우저 HTML이 스스로 바뀌지는 않는다.

## ③ 🛠️ 실기

`/lessons`를 연다. 부모 배열 `items`의 `title`, `href`가 카드 속성이 되고 본문의 `<p>`가 기본 slot으로 들어간다. 레이아웃의 `<slot />` 자리에 페이지 전체가 들어간다. 이 진도에서는 `Draft`의 내부 동작은 다음 진도의 부품으로만 읽는다. 자식에서 부모의 서버 변수를 직접 수정하는 구조를 만들지 않는다.

### `course/src/components/NoteCard.astro` 전체 코드

[NoteCard.astro](course/src/components/NoteCard.astro)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```astro
---
interface Props { title: string; href: string; }
const { title, href } = Astro.props;
---
<article>
  <h2><a href={href}>{title}</a></h2>
  <slot name="meta" />
  <slot />
</article>
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 2 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `interface Props { title: string; href: string; }`. |
| 3 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { title, href }`. |
| 4 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 5 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 6 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 7 | 부모가 전달한 HTML을 이 slot 위치에 삽입한다. |
| 8 | 부모가 전달한 HTML을 이 slot 위치에 삽입한다. |
| 9 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |

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

### `course/src/pages/lessons.astro` 전체 코드

[lessons.astro](course/src/pages/lessons.astro)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```astro
---
import Desk from '../layouts/Desk.astro';
import NoteCard from '../components/NoteCard.astro';
import Draft from '../components/Draft.astro';
const items = [{ title: '첫 글', href: '/notes/welcome', body: 'props로 데이터를 보냅니다.' }];
---
<Desk title="기초 실습">
  <h1>컴포넌트와 데이터</h1>
  {items.map(item => <NoteCard title={item.title} href={item.href}>
    <small slot="meta">콘텐츠 컬렉션으로 연결</small><p>{item.body}</p>
  </NoteCard>)}
  <Draft />
</Desk>
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 2 | `'../layouts/Desk.astro'`의 기능을 이 파일에서 사용한다. |
| 3 | `'../components/NoteCard.astro'`의 기능을 이 파일에서 사용한다. |
| 4 | `'../components/Draft.astro'`의 기능을 이 파일에서 사용한다. |
| 5 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const items`. |
| 6 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 7 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 8 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 9 | 목록의 각 항목을 화면 또는 응답에 필요한 모양으로 변환한다. |
| 10 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 11 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 12 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 13 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |

## ④ 🔗 연동 포인트

페이지 배열 → NoteCard props → HTML의 순서로 값을 전달한다. 브라우저 동작 간 통신은 DOM 이벤트 또는 공유 모듈을 사용하며, 서버 데이터 갱신은 API 요청을 거친다. 다음 단계에서 브라우저 상태와 저장을 다룬다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 카드 내용 없음 | slot 이름 불일치 | 부모 slot과 자식 name 맞추기 |
| props가 undefined | 필수 값 누락 | Props와 전달부 확인 |

## ⑥ 직접 해보기

1. NoteCard에 `description` prop을 추가하고 기본값을 둔다.
2. meta slot을 빼거나 다른 문구로 바꿔 출력 위치를 확인한다.
3. 다른 카드 두 개를 같은 페이지에 재사용한다.

## ⑦ ☐ 체크리스트

- [ ] 페이지와 일반 컴포넌트의 차이를 설명했다.
- [ ] props·기본 slot·이름 있는 slot을 연결했다.
- [ ] 반복 마크업을 재사용 파일로 분리했다.

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study3.md](study3.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
