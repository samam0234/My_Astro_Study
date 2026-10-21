# study7. 고급 기술 구현 2 — 방명록 폼

[study6.md](study6.md)의 JSON은 빌드 때 구워 진 읽기 전용 파일입니다. 방명록은 방문자가 내용을 추가하므로, 그 요청만 서버가 받아야 합니다.

## 1. 어댑터

정적 파일만 있으면 서버 프로세스가 없습니다. `prerender = false`인 라우트를 만들려면 어댑터가 필요합니다.

```powershell
cd demo
npm install @astrojs/node
```

`@astrojs/node` 11.1입니다. `astro.config.mjs`에 `adapter: node({ mode: 'standalone' })`를 넣었습니다. `output`은 기본값 `'static'` 그대로입니다. 그래서 글과 홈은 계속 HTML 파일이고, 방명록만 서버 라우트입니다.

## 2. 폼과 엔드포인트

`src/pages/guestbook.astro`와 `src/pages/api/guestbook.js` 둘 다 `export const prerender = false`입니다.

폼은 JavaScript가 없습니다.

```html
<form method="post" action="/api/guestbook">
```

`POST`는 `name`, `message`를 확인합니다. 비었거나, 이름이 40자를 넘거나, 내용이 280자를 넘으면 400입니다. 본문이 폼이 아니면 400입니다. 통과하면 `demo/data/guestbook.json`에 한 줄 추가하고 `/guestbook`으로 302입니다.

`data/guestbook.json`은 실행 중 생기고 Git에는 넣지 않습니다. 파일이 없으면 빈 배열로 읽습니다.

## 3. 검증 결과

빌드 로그의 정적 라우트 목록에 `/guestbook`과 `/api/guestbook`은 없습니다. `/`, `/posts`, `/api/posts.json`은 그대로 정적입니다.

`node ./dist/server/entry.mjs`를 `HOST=127.0.0.1`, `PORT=4321`로 띄운 뒤:

| 요청 | 상태 |
|---|---|
| `POST /api/guestbook` 본문 없음 | 400 |
| `POST`에 빈 `name`, `message` | 400 |
| `POST name=mina&message=hello` | 302, `location: /guestbook` |
| `GET /api/guestbook` | 200, `mina` / `hello` 한 건 |
| `GET /` | 200. 정적 홈은 그대로 |

화면 `GET /guestbook`의 목록에 `hello`가 보였습니다. 검증 후 JSON 파일은 지웠습니다.
