# study1. 만드는 방법 및 명령어, 실습1

[study0.md](study0.md)의 지도를 코드로 확인합니다. 이 단계의 결과물은 **정적 HTML 한 장**입니다. 섬, 글 목록, API는 아직 없습니다.

대응하는 코드:

- Astro 앱: [`demo/`](demo)
- 섬을 둘 빈 폴더: [`react/demo`](react/demo), [`vue/demo`](vue/demo), [`svelte/demo`](svelte/demo)

## 1. 개발 환경

```powershell
node -v   # v24.14.0
npm -v    # 11.9.0
```

Astro 7.4는 `package.json`의 `engines`에 Node.js 22.22.0 이상을 적습니다. 이 저장소의 Node는 v24라서 그 조건을 만족합니다.

## 2. 프로젝트 생성 명령어

저장소 루트는 이미 Git입니다. 프로젝트 안에 또 `.git`이 생기지 않도록 `--no-git`을 붙입니다.

```powershell
npm create astro@latest -- demo --template minimal --install --no-git --yes --no-ai --skip-houston
```

| 옵션 | 의미 |
|---|---|
| `demo` | 만들 폴더 이름 |
| `--template minimal` | 페이지 하나만 있는 빈 템플릿. 블로그 스타터를 쓰지 않음 |
| `--install` | 생성 직후 `npm install` |
| `--no-git` | 하위 `.git`을 만들지 않음 |
| `--yes` | 나머지 질문을 기본값으로 |
| `--no-ai` | 에이전트용 규칙 파일을 템플릿이 추가하지 않음 |
| `--skip-houston` | 설치 애니메이션 생략 |

사용한 도구 버전은 `create-astro` 5.3.0, 설치된 프레임워크는 Astro 7.4.1입니다.

이미 이 저장소를 받은 사람은 생성 명령을 다시 실행하지 않습니다.

```powershell
cd demo
npm install
npm run dev
```

## 3. 자주 쓰는 명령어

명령은 `demo/` 안에서 실행합니다.

| 명령 | 하는 일 |
|---|---|
| `npm run dev` | 개발 서버. 저장하면 새로고침. http://127.0.0.1:4321 |
| `npm run build` | 정적 사이트를 `dist/`에 생성 |
| `npm run preview` | 빌드 결과를 로컬에서 다시 서빙. `build` 이후 |
| `npm run astro -- --help` | Astro CLI 도움말 |

`astro.config.mjs`에서 주소와 포트를 고정했습니다.

```js
export default defineConfig({
  site: 'http://127.0.0.1:4321',
  server: { host: '127.0.0.1', port: 4321 },
});
```

## 4. 만들어진 구조

```
demo/
├─ astro.config.mjs
├─ package.json
├─ tsconfig.json          ← astro/tsconfigs/strict. 콘텐츠 컬렉션 타입용
├─ public/favicon.svg     ← 가공 없이 /favicon.svg
└─ src/
   ├─ layouts/Base.astro  ← html, head, 공통 CSS
   ├─ pages/index.astro   ← URL /
   └─ styles/global.css
```

`index.astro`는 레이아웃을 import해서 감쌉니다. Next처럼 폴더 레이아웃이 자동으로 붙지 않습니다.

```astro
---
import Base from '../layouts/Base.astro';
---
<Base title="Astro 실습 — 첫 화면">
  <h1>정적 HTML이 먼저 도착합니다</h1>
</Base>
```

`---` 위는 비어 있습니다. 이 페이지는 요청 데이터도, 데이터베이스도 읽지 않습니다.

## 5. React, Vue, Svelte 폴더

세 폴더는 지금 README만 있습니다. 섬 컴포넌트는 study4에서 각자 폴더에 추가합니다. Astro 페이지는 `demo/src`만 수정하고, 프레임워크 파일은 해당 폴더 안에서만 수정합니다.

| 폴더 | 나중에 들어가는 것 |
|---|---|
| `react/demo` | `.jsx` 섬 |
| `vue/demo` | `.vue` 섬 |
| `svelte/demo` | `.svelte` 섬 |

## 6. 검증 결과

개발 서버 `npm run dev` 응답:

- `GET http://127.0.0.1:4321/` → 200
- `<title>`은 `Astro 실습 — 첫 화면`
- `<meta name="generator" content="Astro v7.4.1">`
- 본문에 `정적 HTML이 먼저 도착합니다`
- 개발 서버 HTML에는 Vite 클라이언트와 개발 툴바 `<script>`가 있습니다. 이건 개발용이고 빌드 결과에는 없습니다.

`npm run build` 결과:

- `output: "static"`, 페이지 1개, `dist/index.html`
- `dist/index.html`에는 `<script`가 없습니다.

## 7. 이 단계에서 일부러 안 한 것

- React, Vue, Svelte 통합 설치
- 두 번째 페이지
- 콘텐츠 컬렉션과 엔드포인트
- Node 어댑터. 전부 정적이므로 서버 프로세스가 필요 없습니다.
