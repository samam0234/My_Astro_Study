# study0 · 환경 설정

## ① 목표 한 줄

Astro 개발 환경과 Git·환경변수 경계를 준비한다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

Astro는 콘텐츠를 HTML로 만드는 웹 프레임워크다. 정적 생성은 주문 전에 책을 인쇄하는 것, 요청 시 렌더링은 주문받은 다음 개인별 안내장을 만드는 것에 비유할 수 있다. 처음에는 정적 페이지를 만들고, 회원·DB처럼 요청 데이터가 필요한 경로에만 서버 실행을 연다.

핵심 용어는 `.astro`(템플릿 파일), frontmatter(`---` 안 서버 코드), props(부모가 전달하는 값), slot(자식 HTML 자리), endpoint(HTTP 처리 함수), adapter(배포 런타임 연결), prerender(빌드 시 HTML 생성), hydration(서버 HTML에 브라우저 동작 연결), content collection(스키마로 검증하는 콘텐츠 묶음)이다.

이 저장소의 실행 기준은 Node 24.14.0, npm 11.9.0, Astro 7.4.13, Node adapter 11.1.14다. 라이브러리의 재현 기준은 `course/package-lock.json`이다. `npm ci`는 잠금 파일과 다른 의존성 선언을 허용하지 않는다.

## ③ 🛠️ 실기

새 폴더에서 처음 생성하는 방법과 이미 받은 저장소를 실행하는 방법을 구분한다. 이 저장소 안의 `course/`를 다시 생성하지 않는다.

```powershell
# 새 연습 폴더를 만드는 경우에만 실행
npm create astro@latest -- scratch-astro --template minimal --no-git
cd scratch-astro
npm install
git init
```

기존 저장소에서는 루트에서 아래 순서로 실행한다.

```powershell
node -v
npm -v
git status --short
cd course
npm ci
npm ls astro @astrojs/node
Copy-Item .env.example .env
npm run dev
```

첫 줄과 둘째 줄은 런타임 버전을 출력한다. 셋째 줄은 사용자 변경을 확인한다. 넷째 줄은 앱 작업 폴더로 이동한다. 다섯째 줄은 잠금 파일대로 설치한다. 여섯째 줄은 실제 설치 버전을 출력한다. 일곱째 줄은 서버 설정을 복사하며 기존 `.env`가 있다면 편집만 한다. 마지막 줄은 `http://127.0.0.1:4323`에서 개발 서버를 실행한다.

VS Code 확장은 `astro-build.astro-vscode`와 `esbenp.prettier-vscode`를 권장한다. `.astro` 언어 지원과 포맷팅을 제공한다. `src/pages`는 URL, `src/components`는 재사용 화면, `src/layouts`는 공통 HTML, `src/lib`는 서버 로직, `src/client`는 브라우저 로직, `src/content`는 콘텐츠, `public`은 그대로 제공할 파일, `scripts`는 운영 도구, `tests`는 검증이다. 생성되는 `node_modules`, `.astro`, `dist`, `data`는 커밋하지 않는다.

### `course/package.json` 전체 코드

[package.json](course/package.json)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```json
{
  "name": "astro-study-desk",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "engines": {
    "node": ">=24.14.0"
  },
  "scripts": {
    "dev": "node --env-file-if-exists=.env ./node_modules/astro/bin/astro.mjs dev",
    "build": "node --env-file-if-exists=.env ./node_modules/astro/bin/astro.mjs build",
    "start": "node --env-file-if-exists=.env dist/server/entry.mjs",
    "test": "node --test tests/*.test.mjs",
    "test:http": "node scripts/smoke.mjs",
    "test:extensions": "node scripts/extensions.mjs",
    "test:db": "node --env-file-if-exists=.env scripts/db-contract.mjs",
    "worker": "node --env-file-if-exists=.env scripts/worker.mjs",
    "backup": "node --env-file-if-exists=.env scripts/backup.mjs",
    "mcp:server": "node --env-file-if-exists=.env scripts/mcp-server.mjs",
    "mcp:client": "node scripts/mcp-client.mjs",
    "measure": "node --env-file-if-exists=.env scripts/measure.mjs"
  },
  "dependencies": {
    "@astrojs/mdx": "8.1.0",
    "@astrojs/node": "11.1.14",
    "@modelcontextprotocol/sdk": "1.32.2",
    "@picocss/pico": "^2.1.1",
    "astro": "7.4.13",
    "drizzle-orm": "0.45.4",
    "mongodb": "^6.20.0",
    "mysql2": "^3.15.3",
    "nanostores": "^1.1.1",
    "pg": "^8.16.3",
    "stripe": "^20.0.0",
    "ws": "^8.23.0",
    "zod": "4.6.7"
  },
  "devDependencies": {
    "@playwright/test": "^1.65.1"
  }
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `{`. |
| 2 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 3 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 4 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 5 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 6 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 7 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 8 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 9 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 10 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 11 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 12 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 13 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 14 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 15 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 16 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 17 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 18 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 19 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 20 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 21 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 22 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 23 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 24 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 25 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 26 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 27 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 28 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 29 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 30 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 31 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 32 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 33 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 34 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 35 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 36 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 37 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 38 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 39 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 40 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 41 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

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

### `course/.env.example` 전체 코드

[.env.example](course/.env.example)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```text
SITE_URL=http://127.0.0.1:4323
PUBLIC_SITE_NAME=Astro 학습 데스크
HOST=127.0.0.1
PORT=4323
DB_DRIVER=sqlite
DATABASE_URL=./data/desk.sqlite
CORS_ORIGIN=http://127.0.0.1:4323
INTEGRATIONS_MODE=mock
AI_MODE=mock
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini
AI_API_KEY=
RESEND_API_KEY=
MAIL_FROM=Study <study@example.com>
STRIPE_SECRET_KEY=
STRIPE_PRICE_ID=
STRIPE_WEBHOOK_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
API_BASE_URL=http://127.0.0.1:4323
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `SITE_URL=http://127.0.0.1:4323`. |
| 2 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `PUBLIC_SITE_NAME=Astro 학습 데스크`. |
| 3 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `HOST=127.0.0.1`. |
| 4 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `PORT=4323`. |
| 5 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `DB_DRIVER=sqlite`. |
| 6 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `DATABASE_URL=./data/desk.sqlite`. |
| 7 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `CORS_ORIGIN=http://127.0.0.1:4323`. |
| 8 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `INTEGRATIONS_MODE=mock`. |
| 9 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `AI_MODE=mock`. |
| 10 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `AI_BASE_URL=https://api.openai.com/v1`. |
| 11 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `AI_MODEL=gpt-4o-mini`. |
| 12 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `AI_API_KEY=`. |
| 13 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `RESEND_API_KEY=`. |
| 14 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `MAIL_FROM=Study <study@example.com>`. |
| 15 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `STRIPE_SECRET_KEY=`. |
| 16 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `STRIPE_PRICE_ID=`. |
| 17 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `STRIPE_WEBHOOK_SECRET=`. |
| 18 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `GITHUB_CLIENT_ID=`. |
| 19 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `GITHUB_CLIENT_SECRET=`. |
| 20 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `API_BASE_URL=http://127.0.0.1:4323`. |

## ④ 🔗 연동 포인트

Git은 코드와 예제 설정을 저장하고, `.env`는 로컬 실행 환경을 제공한다. DB 비밀번호와 API 키는 서버 환경변수이며 브라우저용 `PUBLIC_` 접두사를 붙이지 않는다. 다음 단계는 이 환경에서 `/` 페이지를 출력한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| node 명령 없음 | 런타임 미설치 또는 PATH | Node 설치 후 새 터미널에서 버전 확인 |
| npm ci 실패 | package와 lock 불일치 | 정당한 의존성 변경 후 lock 갱신, 일반 실행은 ci |
| 포트 사용 중 | 기존 개발 서버 | 기존 서버 종료 또는 포트·SITE_URL 함께 변경 |

## ⑥ 직접 해보기

1. `node -v`, `npm -v`, `npm ls astro @astrojs/node` 결과를 기록한다.
2. `.env`의 공개 사이트 이름을 바꾸고 개발 서버를 재시작한다.
3. `git check-ignore course/.env`로 비밀 파일이 무시되는지 확인한다.

## ⑦ ☐ 체크리스트

- [ ] Node·npm·Astro 버전을 확인했다.
- [ ] 폴더별 역할과 정적/요청 시 실행을 설명할 수 있다.
- [ ] 개발 서버와 에디터 확장을 준비했다.
- [ ] Git 저장소·.gitignore·.env.example·.env를 구분했다.

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study1.md](study1.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
