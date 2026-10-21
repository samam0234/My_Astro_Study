# Astro 학습 저장소

콘텐츠가 기본인 Astro를 이론부터 작은 웹사이트까지 단계별로 실습한 기록입니다.
정적인 HTML을 먼저 만들고, 클릭이나 입력이 필요한 자리만 React, Vue, Svelte 섬으로 붙입니다.

학습 목표의 기준은 [Notion: Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f)입니다.
설명은 한 진도에 한 가지를 코드로 확인하고, 확인한 결과를 `studyN.md`에 남기는 방식입니다.

- `demo/`는 study1부터 study10까지 한 단계씩 쌓인 실습 앱입니다. 주소는 http://127.0.0.1:4321
- `project/`는 `studyFinal.md`의 메모 데스크입니다. 게시판·방명록이 없고, 폴더와 주소도 `demo/`와 다릅니다. 주소는 http://127.0.0.1:4322
- 섬 소스는 Astro 앱 밖에 둡니다. `react/`, `vue/`, `svelte/` 안에서 각자 고칩니다.
  - `*/demo`는 `demo/`가 불러 씁니다.
  - `*/project`는 `project/`가 불러 씁니다.

## 사전 준비

```powershell
node -v   # v22.22 이상. 이 실습은 v24.14.0
npm -v    # 11.x
```

## 기술 스택

Astro 7, `@astrojs/node` standalone. 기본 출력은 정적입니다. 요청마다 렌더하는 페이지만 `export const prerender = false`입니다.

### demo/ (study1 ~ study10)

- 파일 라우트, Astro 컴포넌트, props와 slot
- React `client:load`, Svelte `client:idle`, Vue `client:visible`
- 콘텐츠 컬렉션과 MDX
- 정적 GET `/api/posts.json`
- 방명록 POST, 방문 쿠키 `/now`
- `PUBLIC_SITE_NAME`, SVG, `ClientRouter`
- `npm start`로 프로덕션 서버. Dockerfile은 있으나 이미지 빌드는 엔진이 꺼져 있어 하지 않음

### project/ (studyFinal)

- 레이아웃은 `src/ui/Shell.astro`
- 메모 콘텐츠 컬렉션, React 검색, Vue 고정 버튼, Svelte 테마
- 방문 쿠키 `/visit`
- 포트 4322

## 프로젝트 실행

```powershell
cd demo
npm install
npm run dev      # http://127.0.0.1:4321
npm run build
npm start        # dist/server/entry.mjs
```

메모 데스크:

```powershell
cd project
npm install
npm run dev      # http://127.0.0.1:4322
npm run build
npm start
```

정적 HTML은 어댑터를 켠 뒤 `dist/client/`에 있습니다. `dist/` 바로 아래에는 없습니다.

## 학습 문서 목차

| 문서 | 주제 | 핵심 내용 |
|---|---|---|
| [study0.md](study0.md) | Astro 기초 이론 | 콘텐츠 기본, Next·Rails와 차이, 섬과 정적 경계 |
| [study1.md](study1.md) | 만드는 방법과 명령어, 실습 1 | `create-astro`, 첫 정적 페이지 |
| [study2.md](study2.md) | 실습 2 | 파일 라우트, `getStaticPaths` |
| [study3.md](study3.md) | 실습 3 | props, slot, 레이아웃 |
| [study4.md](study4.md) | 실습 4 | React / Vue / Svelte 섬과 client 지시어 |
| [study5.md](study5.md) | 실습 5 | 콘텐츠 컬렉션, MDX, 정적 글 목록 |
| [study6.md](study6.md) | 고급 1 | 정적 GET `/api/posts.json` |
| [study7.md](study7.md) | 고급 2 | Node 어댑터, 방명록 POST |
| [study8.md](study8.md) | 고급 3 | 방문 쿠키, 정적과 온디맨드 경계 |
| [study9.md](study9.md) | 고급 4 | 환경 변수, 이미지, 메타, ClientRouter |
| [study10.md](study10.md) | 고급 5 | `npm start`, Dockerfile |
| [studyFinal.md](studyFinal.md) | 종합 프로젝트 | 메모 데스크. demo와 다른 구조 |

## 저장소 구조

```text
demo/                 study1~10 Astro 앱
project/              studyFinal 메모 데스크
react/demo            demo용 React 섬
react/project         메모 검색
vue/demo              demo용 Vue 섬
vue/project           메모 고정 버튼
svelte/demo           demo용 Svelte 섬
svelte/project        테마 토글
study0.md ~ studyFinal.md
```

`node_modules`, `.astro`, `dist`, `.env`, `demo/data/guestbook.json`은 커밋하지 않습니다. `.env.example`만 저장소에 있습니다.
