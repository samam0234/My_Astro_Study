# study10 · 배포·정리

## ① 목표 한 줄

정적 파일과 Node 서버를 빌드·실행하고 배포 후 점검한다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

빌드는 개발 코드를 배포 산출물로 바꾸는 단계다. Node adapter가 있으면 정적 페이지는 `dist/client`, 동적 API는 `dist/server/entry.mjs`로 나뉜다. 정적 파일만 호스팅하면 로그인·CRUD 요청을 실행할 서버가 없어진다.

도메인은 서버를 찾는 이름, DNS는 이름을 주소로 바꾸는 안내, HTTPS는 브라우저와 서버 사이 암호화와 서버 신원 확인이다. 일반적인 Node 서버 앞에 HTTPS reverse proxy를 두고 쿠키의 Secure 설정과 SITE_URL을 실제 공개 URL에 맞춘다. DB 파일은 배포 이미지 밖의 영속 볼륨에 둔다. PUBLIC 값은 정적 HTML에 들어가므로 바뀌면 다시 빌드해야 한다.

## ③ 🛠️ 실기

개발 서버를 종료한 다음 `course/`에서 실행한다.

```powershell
npm ci
npm run build
$env:HOST='127.0.0.1'
$env:PORT='4323'
npm start
```

1행은 의존성을 고정하고 2행은 산출물을 만든다. 3~4행은 바인딩 주소와 포트이고 5행이 배포용 서버다. `/`, `/notes/welcome`, `/board`, `/health`, `/api/posts`, `/없는주소`를 확인한다. `/board` 껍데기는 정적이지만 목록 데이터는 `prerender = false` API를 매번 조회한다. 따라서 새 글에 UI 재빌드는 필요하지 않다. 정적 MDX 원본 변경에는 재빌드가 필요하다.

기초 총정리: study0 환경 → 1 템플릿 → 2 부품 → 3 상태 → 4 URL → 5 폼 → 6 DB/API → 7 인증 → 8 구조 → 9 검증 → 10 배포다. Docker 상세·자동화는 study16에서 다룬다. 현재 로컬 Docker 엔진이 실행되지 않아 이미지 실행 검증은 별도 미완료 항목이다.

### `course/astro.config.mjs` 전체 코드

[astro.config.mjs](course/astro.config.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import mdx from '@astrojs/mdx';

export default defineConfig({
  site: process.env.SITE_URL || 'http://127.0.0.1:4323',
  adapter: node({ mode: 'standalone' }),
  integrations: [mdx()],
  server: { host: '127.0.0.1', port: 4323 },
});
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'astro/config'`의 기능을 이 파일에서 사용한다. |
| 2 | `'@astrojs/node'`의 기능을 이 파일에서 사용한다. |
| 3 | `'@astrojs/mdx'`의 기능을 이 파일에서 사용한다. |
| 4 | 코드 구간을 나누는 빈 줄이다. |
| 5 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `export default defineConfig({`. |
| 6 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 7 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `adapter: node({ mode: 'standalone' }),`. |
| 8 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `integrations: [mdx()],`. |
| 9 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `server: { host: '127.0.0.1', port: 4323 },`. |
| 10 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/src/pages/health.js` 전체 코드

[health.js](course/src/pages/health.js)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { json } from '../lib/http.mjs';
import { getStore } from '../lib/store.mjs';
export const prerender = false;
export async function GET() {
  await (await getStore()).list('health');
  return json({ status: 'ok' }, 200, process.env.RELEASE_SHA ? { 'X-Release-Sha': process.env.RELEASE_SHA } : {});
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'../lib/http.mjs'`의 기능을 이 파일에서 사용한다. |
| 2 | `'../lib/store.mjs'`의 기능을 이 파일에서 사용한다. |
| 3 | 이 경로를 빌드 시 고정하지 않고 요청마다 실행한다. |
| 4 | 비동기 함수 `GET`의 입력과 처리 범위를 정의한다. |
| 5 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await (await getStore()).list('health');`. |
| 6 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 7 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/Dockerfile` 전체 코드

[Dockerfile](course/Dockerfile)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```dockerfile
FROM node:24.14.0-bookworm-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build && npm prune --omit=dev

FROM node:24.14.0-bookworm-slim
WORKDIR /app
ENV NODE_ENV=production HOST=0.0.0.0 PORT=4323
COPY --from=build --chown=node:node /app/dist ./dist
COPY --from=build --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/package.json ./package.json
COPY --from=build --chown=node:node /app/scripts ./scripts
COPY --from=build --chown=node:node /app/src/lib ./src/lib
RUN mkdir data && chown node:node data
USER node
EXPOSE 4323
CMD ["node", "dist/server/entry.mjs"]
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 2 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 3 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 4 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 5 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 6 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 7 | 코드 구간을 나누는 빈 줄이다. |
| 8 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 9 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 10 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 11 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 12 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 13 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 14 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 15 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 16 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 17 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 18 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |
| 19 | 컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다. |

## ④ 🔗 연동 포인트

로컬에서 npm start로 검증한 산출물을 서버에서 실행한다. 운영은 HOST=0.0.0.0·PORT·SITE_URL·DATABASE_URL·CORS_ORIGIN을 맞춘다. 다음 문서는 기초 구간만 조합한 midpoint 서비스다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 정적 홈만 동작 | Node 서버 미실행 | dist/server/entry.mjs 실행 |
| DB가 배포 때 초기화 | 컨테이너 내부 임시 경로 | 영속 볼륨 마운트 |
| Docker 연결 실패 | Desktop 엔진 없음 | 엔진 준비 후 별도 검증 |

## ⑥ 직접 해보기

1. 빌드 후 홈과 API를 각각 요청하고 출력 위치를 확인한다.
2. DB 경로를 별도 디렉터리로 바꾸고 서버 재시작 후 글이 남는지 확인한다.
3. HTTPS 프록시 뒤의 쿠키 Secure·Origin 설정을 점검한다.

## ⑦ ☐ 체크리스트

- [ ] npm ci·build·start 순서로 실행했다.
- [ ] 도메인·DNS·HTTPS·Secure 쿠키를 설명했다.
- [ ] 환경변수·DB 영속 경로·헬스체크를 점검했다.
- [ ] 정적 빌드의 한계 기록: 글 작성 후 목록이 바뀌려면 재빌드 또는 <code>prerender = false</code>

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [studyMidpoint.md](studyMidpoint.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
