# study10. 고급 기술 구현 5 — 빌드와 서버 실행

[study9.md](study9.md)까지 `demo/` 기능은 끝났습니다. 이 진도는 그 결과를 프로세스 하나로 띄우는 방법입니다.

## 1. 빌드

`demo/`에서 실행합니다.

```powershell
npm run build
npm start
```

`npm start`는 `node ./dist/server/entry.mjs`입니다. 개발 서버 `npm run dev`와 다릅니다. 개발 서버는 저장할 때마다 다시 만들고, `start`는 이미 만들어진 `dist/`만 읽습니다.

Astro 7.4는 `npx astro build --timings`로 빌드 시간 요약을 보여 줍니다. 느린 페이지를 찾을 때 씁니다.

어댑터가 있으므로 결과 폴더는 둘로 나뉩니다.

| 경로 | 내용 |
|---|---|
| `dist/client/` | 미리 만든 HTML, CSS, 섬 스크립트, `/api/posts.json` |
| `dist/server/entry.mjs` | `/guestbook`, `/api/guestbook`, `/now`를 요청 때 만드는 Node 서버 |

`HOST`와 `PORT`로 주소를 바꿉니다. 이 저장소의 확인은 `127.0.0.1:4321`이었습니다.

## 2. Docker

`demo/Dockerfile`은 Node 22 이미지에서 `npm ci`, `npm run build`, 그다음 `entry.mjs`를 실행합니다. 컨테이너 안에서는 `HOST=0.0.0.0`, `PORT=4321`입니다.

```powershell
docker build -t astro-demo .
docker run --rm -p 4321:4321 astro-demo
```

`.dockerignore`가 `node_modules`, `dist`, `.env`, `data/guestbook.json`을 빼므로 이미지 안에서 의존성을 다시 설치하고 빌드합니다. `.env`가 없으면 사이트 이름은 코드의 기본값 `Astro 실습`입니다.

이번 환경에서는 Docker CLI는 있었지만 Docker Desktop 엔진이 꺼져 있어 이미지는 만들지 못했습니다. 같은 빌드 결과를 `npm start`로 확인했습니다.

## 3. 검증 결과

`npm start` 후:

| 요청 | 상태 |
|---|---|
| `GET /` | 200 |
| `GET /posts` | 200 |
| `GET /api/posts.json` | 200 |
| `GET /now` | 200 |
| `GET /missing` | 404 |

`dist/`와 `node_modules`는 커밋하지 않습니다. 받은 사람은 `demo/`에서 `npm install` 다음 `npm run build`를 다시 합니다.
