# study3. 실습3 — 컴포넌트, props, slot

[study2.md](study2.md)의 헤더 마크업을 컴포넌트로 꺼내고, 글 목록을 카드로 바꿉니다. 아직 브라우저 JavaScript는 없습니다. `.astro` 컴포넌트는 빌드 때 HTML로 합쳐집니다.

## 1. 파일

| 파일 | 역할 |
|---|---|
| `src/components/Header.astro` | 현재 경로와 링크를 비교해 `aria-current="page"` |
| `src/components/Footer.astro` | `note` prop. 기본 문구가 있습니다 |
| `src/components/Card.astro` | `title`, `href` prop. 기본 slot과 `meta` slot |
| `src/layouts/Base.astro` | Header, `<slot />`, Footer를 조립 |
| `src/pages/components.astro` | props와 slot을 한 화면에서 보여주는 페이지. URL `/components` |

`Card`는 레이아웃이 아닙니다. 목록의 한 칸입니다. `Base`는 모든 페이지가 직접 import합니다.

```astro
<Card title={note.title} href={`/posts/${note.slug}`}>
  <Fragment slot="meta">임시 데이터</Fragment>
  <p>{note.summary}</p>
</Card>
```

이름 있는 slot은 `<Fragment slot="meta">`로 넘깁니다. 이름 없는 자식은 기본 `<slot />`으로 들어갑니다.

`Footer`의 문구는 평소에는 기본값입니다. `/components`만 `footer` prop으로 다른 문장을 넘깁니다.

## 2. Rails 뷰와의 차이

Rails 파셜은 `render 'shared/header'`처럼 컨트롤러와 별도 파일입니다. Astro도 파일을 나누지만, props는 함수 인자처럼 템플릿 쪽에서 넘깁니다. 인스턴스 변수를 뷰 전체에 암시적으로 공유하지 않습니다.

## 3. 검증 결과

| 요청 | 상태 | 확인 |
|---|---|---|
| `GET /components` | 200 | 제목 `이름이 있는 칸`, 바닥 문구 `이 페이지만 바닥 문구를 props로 바꿨습니다.` |
| `GET /posts` | 200 | 카드 메타 `임시 데이터`, 바닥은 기본 문구 |
| `GET /` | 200 | 헤더 링크에 부품, 글이 포함 |

세 응답 모두 컴포넌트 출처가 `Header.astro`입니다. 개발 툴바 스크립트를 빼면 이 페이지들에 프레임워크 런타임은 없습니다.
