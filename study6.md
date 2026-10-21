# study6. 고급 기술 구현 1 — 글 목록 엔드포인트

[study5.md](study5.md)의 컬렉션을 HTTP JSON으로도 내보냅니다. Rails의 `namespace :api`에 해당하는 파일은 `src/pages/api/posts.json.js`이고, 주소는 파일 경로 그대로 `/api/posts.json`입니다.

## 1. 한 함수를 페이지와 엔드포인트가 같이 쓴다

`src/lib/posts.js`의 `listPosts()`가 컬렉션을 날짜 내림차순의 평범한 객체 배열로 바꿉니다.

```js
export async function GET() {
  return Response.json(await listPosts());
}
```

`/posts`와 `/feed`도 이 함수를 부릅니다. 화면용 필드와 JSON 필드가 어긋나지 않습니다. 본문 HTML이 필요한 `[slug].astro`만 `render()`를 계속 씁니다.

이 엔드포인트에는 `prerender = false`가 없습니다. 글은 빌드 전에 확정되므로 JSON 파일로 구워 둡니다.

## 2. 검증 결과

`npm run build` 로그에 `/api/posts.json`이 정적 라우트로 찍혔습니다. `dist/api/posts.json`은 배열 3개입니다.

| id | pubDate |
|---|---|
| `compare` | 2026-10-21 |
| `file-is-url` | 2026-10-19 |
| `static-html` | 2026-10-18 |

`/feed`도 같은 세 제목을 링크로 찍습니다. 아직 서버 프로세스는 필요 없습니다. 파일을 추가하는 POST는 다음 진도입니다.
