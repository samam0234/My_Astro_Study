# study2. 실습2 — 파일 경로가 주소

[study1.md](study1.md)의 첫 화면에 페이지를 더합니다. 라우터 패키지는 설치하지 않습니다. `src/pages` 파일 경로가 URL입니다.

## 1. 추가한 파일

| 파일 | URL |
|---|---|
| `src/pages/index.astro` | `/` |
| `src/pages/about.astro` | `/about` |
| `src/pages/posts/index.astro` | `/posts` |
| `src/pages/posts/[slug].astro` | `/posts/static-html`, `/posts/file-is-url` |
| `src/pages/404.astro` | 없는 주소. 상태 코드 404 |

레이아웃 `Base.astro`에 홈, 소개, 글 링크를 넣었습니다. 컴포넌트로 나누는 작업은 study3입니다.

## 2. 동적 주소는 미리 알려 줘야 한다

출력 모드가 `static`이면 `[slug].astro`는 빌드 때 만들 주소를 `getStaticPaths`로 반환해야 합니다. Rails의 `resources :posts`가 패턴 하나로 모든 id를 받는 것과 다릅니다. 정적 사이트는 **존재하는 글의 목록을 빌드 전에** 알아야 HTML 파일을 구울 수 있습니다.

```js
export function getStaticPaths() {
  return notes.map((note) => ({ params: { slug: note.slug } }));
}
```

목록 데이터는 `src/data/notes.js`의 배열입니다. 데이터베이스가 아니라, 경로가 파일에서 온다는 것을 보기 위한 임시 데이터입니다. study5에서 같은 URL을 콘텐츠 컬렉션으로 바꿉니다.

`getStaticPaths`에 없는 `/posts/missing`은 404입니다.

## 3. 검증 결과

개발 서버 기준입니다.

| 요청 | 상태 |
|---|---|
| `GET /` | 200 |
| `GET /about` | 200 |
| `GET /posts` | 200 |
| `GET /posts/static-html` | 200 |
| `GET /posts/missing` | 404 |
| `GET /nope` | 404. 본문 출처는 `src/pages/404.astro` |

`npm run build`도 같은 페이지를 `dist/`에 정적 파일로 만들었습니다. `/posts/static-html/index.html`, `/posts/file-is-url/index.html`이 생깁니다.
