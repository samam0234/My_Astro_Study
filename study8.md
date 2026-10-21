# study8. 고급 기술 구현 3 — 쿠키와 정적 경계

[study7.md](study7.md)에서 방명록만 서버로 남겼습니다. 이 진도는 그 경계에 쿠키를 올립니다. Rails의 세션 쿠키와 역할은 같고, 범위는 한 페이지입니다.

## 1. `/now`

`src/pages/now.astro`는 `prerender = false`입니다. `Astro.cookies`로 `visits`를 읽고 1을 더해 다시 심습니다.

```js
Astro.cookies.set('visits', String(visits), {
  path: '/',
  httpOnly: true,
  sameSite: 'lax',
});
```

`httpOnly`라서 페이지의 JavaScript는 이 값을 읽지 못합니다. 서버가 HTML에 숫자만 찍습니다. 로그인이 아닙니다. 방문 횟수만 세어, 쿠키가 요청마다 서버에 돌아온다는 것을 확인합니다.

같은 파일은 응답을 만든 시각도 찍습니다. 정적 페이지는 빌드 시각이 고정이지만, 이 주소는 요청마다 시각이 달라집니다.

## 2. 무엇이 파일이고 무엇이 서버인가

`output`은 여전히 `'static'`입니다. 빌드 로그의 정적 라우트는 아래뿐입니다.

- `/`, `/about`, `/components`, `/feed`, `/islands`
- `/posts`, `/posts/compare`, `/posts/file-is-url`, `/posts/static-html`
- `/api/posts.json`, `/404.html`

`/guestbook`, `/api/guestbook`, `/now`는 이 목록에 없습니다. Node 프로세스가 요청을 받을 때만 HTML을 만듭니다.

## 3. 검증 결과

서버를 `127.0.0.1:4321`에 띄우고 쿠키 단지를 유지한 채 `/now`를 두 번 호출했습니다.

| 순서 | Set-Cookie | 화면의 횟수 | 시각 |
|---|---|---|---|
| 첫 요청 | `visits=1; Path=/; HttpOnly; SameSite=Lax` | 1 | `2026-10-21T04:09:19.665Z` |
| 같은 쿠키로 다시 | `visits=2; ...` | 2 | `2026-10-21T04:09:19.700Z` |

두 시각이 다릅니다. 정적 홈을 새로고침해도 본문은 빌드 결과와 같습니다.
