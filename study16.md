# study16 · 운영·CI/CD

## ① 목표 한 줄

Docker·자동 검증·이미지 배포·모니터링·백업 절차를 만든다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

컨테이너는 실행 환경과 산출물을 함께 포장한다. build 단계는 npm ci와 build를 실행하고 runtime 단계는 비루트 사용자로 서버를 실행한다. DB·업로드는 이미지 밖 볼륨에 보관한다. 비밀값을 Dockerfile·이미지·Git에 넣지 않는다.

CI는 제출된 변경을 자동 검증하는 검사대다. GitHub Actions가 단위·HTTP·브라우저·MCP·문서 검사를 실행하고 Docker 이미지를 GHCR에 커밋 SHA 태그로 게시한다. DEPLOY_ENABLED=true와 배포 훅/헬스 URL을 설정하면 검증 후 자동 배포 훅을 호출한다. 설정되지 않은 실제 운영 서버를 배포했다고 기록하지 않는다.

로그는 요청 ID·경로·상태·시간을 구조화해 남긴다. 오류율·지연 p95·작업 실패·DB 용량·디스크 용량을 모니터링한다. 백업은 복사 성공보다 복구 성공이 중요하다. SQLite는 실행 중 WAL 파일을 단순 복사하지 않고 backup API로 스냅샷을 만든다.

## ③ 🛠️ 실기

`course/`에서 `.env`를 만든 후 실행한다.

```powershell
docker compose config --quiet
docker compose up -d --build
docker compose logs --tail 50 web worker
Invoke-RestMethod 'http://127.0.0.1:4323/health'
npm run backup
```

1행은 설정 문법, 2행은 web·worker 실행, 3행은 로그, 4행은 준비 상태, 5행은 로컬 SQLite 백업이다. 컨테이너 DB를 백업하려면 `docker compose exec web node scripts/backup.mjs`로 볼륨 안에서 실행하고 스냅샷과 uploads를 별도 저장소로 복사한다.

GitHub 설정: DEPLOY_ENABLED 변수, DEPLOY_HOOK secret, HEALTH_URL 변수를 준비한다. 배포 훅은 JSON의 image·revision을 받아 GHCR SHA 이미지를 pull하고 런타임 RELEASE_SHA를 revision으로 설정해야 한다. 영속 볼륨을 유지하고 `/health`의 X-Release-Sha가 요청한 SHA인지 확인한다. 예전 서버의 200을 새 버전 배포 성공으로 판단하지 않는다. 미설정이면 이미지 게시까지만 진행한다. 도메인은 HTTPS reverse proxy로 연결하며 프록시에서 업로드/요청 크기와 연결 시간을 제한한다.

PostgreSQL은 pg_dump/pg_restore, MariaDB는 mariadb-dump, MongoDB는 mongodump/mongorestore를 사용한다. 복구는 쓰기를 중지하고 새 볼륨에 복구한 뒤 건수·로그인·문서 다운로드를 확인한다. 실패하면 기존 볼륨과 이전 이미지로 돌아간다. 현재 Docker 엔진이 없어 컨테이너 실행은 미검증이며 CI 실행 결과·외부 배포도 푸시 이후 확인 대상이다.

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

### `course/.dockerignore` 전체 코드

[.dockerignore](course/.dockerignore)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```text
node_modules
dist
.astro
.env
.env.*
data
test-results
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `node_modules`. |
| 2 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `dist`. |
| 3 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `.astro`. |
| 4 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `.env`. |
| 5 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `.env.*`. |
| 6 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `data`. |
| 7 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `test-results`. |

### `course/compose.yml` 전체 코드

[compose.yml](course/compose.yml)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```yaml
services:
  web:
    build: .
    ports: ["127.0.0.1:4323:4323"]
    env_file: .env
    environment:
      HOST: 0.0.0.0
      PORT: 4323
    volumes: ["desk-data:/app/data"]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://127.0.0.1:4323/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
      interval: 30s
      timeout: 5s
      retries: 3
  worker:
    build: .
    command: ["node", "scripts/worker.mjs"]
    env_file: .env
    volumes: ["desk-data:/app/data"]
    restart: unless-stopped
volumes:
  desk-data:
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 2 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `web:`. |
| 3 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `build: .`. |
| 4 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `ports: ["127.0.0.1:4323:4323"]`. |
| 5 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `env_file: .env`. |
| 6 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `environment:`. |
| 7 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `HOST: 0.0.0.0`. |
| 8 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `PORT: 4323`. |
| 9 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 10 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `restart: unless-stopped`. |
| 11 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `healthcheck:`. |
| 12 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 13 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `interval: 30s`. |
| 14 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `timeout: 5s`. |
| 15 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `retries: 3`. |
| 16 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `worker:`. |
| 17 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `build: .`. |
| 18 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `command: ["node", "scripts/worker.mjs"]`. |
| 19 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `env_file: .env`. |
| 20 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 21 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `restart: unless-stopped`. |
| 22 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 23 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `desk-data:`. |

### `.github/workflows/ci.yml` 전체 코드

[ci.yml](.github/workflows/ci.yml)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```yaml
name: Astro 학습 검증과 이미지 배포
on:
  push:
    branches: [master]
  pull_request:
permissions:
  contents: read
jobs:
  verify:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: course
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '24.14.0'
          cache: npm
          cache-dependency-path: course/package-lock.json
      - run: npm ci
      - run: npm test
      - run: npm run build
      - run: npm run test:http
      - run: npm run test:extensions
      - run: npm run mcp:client
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test
      - run: python ../scripts/check_docs.py
      - run: docker build -t astro-study-check .
  publish:
    needs: verify
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: image
        env:
          REPOSITORY: ${{ github.repository }}
        run: echo "name=ghcr.io/${REPOSITORY,,}" >> "$GITHUB_OUTPUT"
      - uses: docker/build-push-action@v6
        with:
          context: course
          push: true
          tags: ${{ steps.image.outputs.name }}:${{ github.sha }}
  deploy:
    needs: publish
    if: github.event_name == 'push' && vars.DEPLOY_ENABLED == 'true'
    runs-on: ubuntu-latest
    environment: production
    permissions:
      contents: read
    steps:
      - name: 배포 훅 호출과 HTTPS 상태 확인
        env:
          DEPLOY_HOOK: ${{ secrets.DEPLOY_HOOK }}
          HEALTH_URL: ${{ vars.HEALTH_URL }}
          DEPLOY_IMAGE: ghcr.io/${{ github.repository }}:${{ github.sha }}
          REVISION: ${{ github.sha }}
        run: |
          test -n "$DEPLOY_HOOK" && test -n "$HEALTH_URL"
          curl --fail --silent --show-error --json "{\"image\":\"${DEPLOY_IMAGE,,}\",\"revision\":\"$REVISION\"}" "$DEPLOY_HOOK"
          for attempt in $(seq 1 30); do
            if curl --fail --silent --show-error --dump-header health-headers.txt --output health.json "$HEALTH_URL" && grep -Eiq "^x-release-sha: ${REVISION}[[:space:]]*$" health-headers.txt; then exit 0; fi
            sleep 5
          done
          exit 1
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `name: Astro 학습 검증과 이미지 배포`. |
| 2 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `on:`. |
| 3 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `push:`. |
| 4 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `branches: [master]`. |
| 5 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `pull_request:`. |
| 6 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `permissions:`. |
| 7 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `contents: read`. |
| 8 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `jobs:`. |
| 9 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `verify:`. |
| 10 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `runs-on: ubuntu-latest`. |
| 11 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `defaults:`. |
| 12 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `run:`. |
| 13 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `working-directory: course`. |
| 14 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 15 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 16 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 17 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `with:`. |
| 18 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `node-version: '24.14.0'`. |
| 19 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `cache: npm`. |
| 20 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `cache-dependency-path: course/package-lock.json`. |
| 21 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 22 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 23 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 24 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 25 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 26 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 27 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 28 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 29 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 30 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 31 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `publish:`. |
| 32 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `needs: verify`. |
| 33 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `if: github.event_name == 'push'`. |
| 34 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `runs-on: ubuntu-latest`. |
| 35 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `permissions:`. |
| 36 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `contents: read`. |
| 37 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `packages: write`. |
| 38 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 39 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 40 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 41 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `with:`. |
| 42 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `registry: ghcr.io`. |
| 43 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `username: ${{ github.actor }}`. |
| 44 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `password: ${{ secrets.GITHUB_TOKEN }}`. |
| 45 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `- id: image`. |
| 46 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `env:`. |
| 47 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `REPOSITORY: ${{ github.repository }}`. |
| 48 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `run: echo "name=ghcr.io/${REPOSITORY,,}" >> "$GITHUB_OUTPUT"`. |
| 49 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 50 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `with:`. |
| 51 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `context: course`. |
| 52 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `push: true`. |
| 53 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `tags: ${{ steps.image.outputs.name }}:${{ github.sha }}`. |
| 54 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `deploy:`. |
| 55 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `needs: publish`. |
| 56 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `if: github.event_name == 'push' && vars.DEPLOY_ENABLED == 'true'`. |
| 57 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `runs-on: ubuntu-latest`. |
| 58 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `environment: production`. |
| 59 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `permissions:`. |
| 60 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `contents: read`. |
| 61 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 62 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `- name: 배포 훅 호출과 HTTPS 상태 확인`. |
| 63 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `env:`. |
| 64 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `DEPLOY_HOOK: ${{ secrets.DEPLOY_HOOK }}`. |
| 65 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `HEALTH_URL: ${{ vars.HEALTH_URL }}`. |
| 66 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `DEPLOY_IMAGE: ghcr.io/${{ github.repository }}:${{ github.sha }}`. |
| 67 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `REVISION: ${{ github.sha }}`. |
| 68 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `run: &#124;`. |
| 69 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `test -n "$DEPLOY_HOOK" && test -n "$HEALTH_URL"`. |
| 70 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `curl --fail --silent --show-error --json "{\"image\":\"${DEPLOY_IMAGE,,}\",\"revision\":\"$REVISION\"}" "$DEPL`. |
| 71 | 목록 또는 스트림의 남은 항목을 순서대로 처리한다. |
| 72 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 73 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `sleep 5`. |
| 74 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `done`. |
| 75 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `exit 1`. |

### `course/scripts/backup.mjs` 전체 코드

[backup.mjs](course/scripts/backup.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { DatabaseSync, backup } from 'node:sqlite';
import { mkdir } from 'node:fs/promises';
import { settings } from '../src/lib/config.mjs';
const config = settings();
if (config.driver !== 'sqlite') throw new Error('PostgreSQL은 pg_dump, MariaDB는 mariadb-dump, MongoDB는 mongodump를 사용하세요.');
await mkdir('./data/backups', { recursive: true });
const file = `./data/backups/desk-${new Date().toISOString().replace(/[:.]/g, '-')}.sqlite`;
const db = new DatabaseSync(config.database);
try { await backup(db, file); console.log(file); }
finally { db.close(); }
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'node:sqlite'`의 기능을 이 파일에서 사용한다. |
| 2 | `'node:fs/promises'`의 기능을 이 파일에서 사용한다. |
| 3 | `'../src/lib/config.mjs'`의 기능을 이 파일에서 사용한다. |
| 4 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const config`. |
| 5 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 6 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await mkdir('./data/backups', { recursive: true });`. |
| 7 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const file`. |
| 8 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const db`. |
| 9 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `try { await backup(db, file); console.log(file); }`. |
| 10 | 성공·실패에 관계없이 연결/잠금 등 정리 작업을 실행한다. |

## ④ 🔗 연동 포인트

push→CI→GHCR 이미지→호스팅 배포 훅→HTTPS health 확인으로 잇는다. DB와 업로드 볼륨을 함께 백업하고, 이전 SHA 이미지로 롤백한다. 다음 단계는 장시간 연결과 파일 처리를 점검한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 컨테이너 DB 권한 오류 | 볼륨 소유자 불일치 | node 사용자 쓰기 권한 |
| 이미지 게시 403 | packages 권한 부족 | workflow packages:write와 저장소 설정 |
| 배포가 건너뜀 | DEPLOY_ENABLED 미설정 | 필요 환경에서 변수·secret 구성 |

## ⑥ 직접 해보기

1. Docker 엔진이 켜진 환경에서 compose config·build·up·health를 확인한다.
2. npm run backup 후 별도 DB 파일로 열어 records 건수를 비교한다.
3. GitHub repository 변수·secret을 설정하고 성공·실패 배포를 연습한다.

## ⑦ ☐ 체크리스트

- [ ] Docker 비루트 실행·영속 볼륨·비밀 제외를 확인했다.
- [ ] Actions 검증→이미지 게시→조건부 자동 배포를 구성했다.
- [ ] 로그·오류율·지연·디스크·작업 실패 모니터링 항목을 적었다.
- [ ] DB·업로드 백업과 별도 복구·롤백 절차를 마련했다.
- [ ] Docker 이미지 실행과 실제 호스팅 배포를 해당 환경에서 검증한다.

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study17.md](study17.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
