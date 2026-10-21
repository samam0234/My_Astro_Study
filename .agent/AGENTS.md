# 에이전트 공통 가이드라인 (인수인계 문서)

이 문서는 이 저장소에서 작업하는 모든 AI 에이전트(Claude, Grok, Codex 등)가 **공통으로** 지켜야 할 규칙을 정리한 인수인계 문서입니다.
`.claude/`, `.grok/`, `.codex/` 폴더의 에이전트별 문서는 이 문서를 기본으로 삼고, 도구별 특이사항만 추가로 기술합니다.

## 1. 저장소 개요

- Astro 학습 기록 저장소입니다. 순서는 이론 → 기초 실습 → 고급 기술 → 응용 프로젝트입니다.
- 학습 목표의 기준은 Notion 페이지 [Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f)입니다. 콘텐츠가 기본이고, 필요한 화면만 React / Vue / Svelte 섬으로 붙입니다.
- 설명의 결은 [Ruby on Rails](https://app.notion.com/p/3fcd7dec5e2e816dba83e4c93c0a011c) 학습과 같습니다. 한 진도에 한 가지를 코드로 확인하고, 검증 결과를 문서에 남깁니다. Rails의 MVC·스캐폴드·ORM을 Astro에 그대로 옮기지는 않습니다.
- 루트의 학습 문서는 `study0.md` ~ `study10.md`, `studyFinal.md` 순서로 진행됩니다.
  - `study0.md`: Astro 기초 이론
  - `study1.md`: 프로젝트 생성 방법 및 명령어, 실습1
  - `study2.md` ~ `study5.md`: 실습2 ~ 실습5
  - `study6.md` ~ `study10.md`: 고급 기술 구현 1 ~ 5
  - `studyFinal.md`: 지금까지 배운 것을 응용한 작은 웹사이트
- Astro 앱이 페이지, 콘텐츠, 엔드포인트를 담당합니다.
  - `demo/`: study1~study10. 한 단계씩 쌓이는 Astro 앱입니다. 주소는 http://127.0.0.1:4321
  - `project/`: `studyFinal.md`의 작은 웹사이트입니다. 주소는 http://127.0.0.1:4322
- React, Vue, Svelte는 각자 폴더에서만 작업합니다. Astro 페이지를 수정하지 않고 섬 컴포넌트만 고칩니다.
  - `react/demo`, `vue/demo`, `svelte/demo`: demo가 불러 쓰는 섬
  - `react/project`, `vue/project`, `svelte/project`: project가 불러 쓰는 섬

## 2. 작업 전 확인 사항

- 새 작업을 시작하기 전에 `studyN.md` 파일들을 번호 순서대로 확인하여 지금까지의 학습 진도와 맥락을 파악합니다.
- 실습 코드가 study 문서 설명과 어긋나지 않는지 확인합니다. study1~10은 `demo/`와, 섬이 있는 진도는 `react/demo`·`vue/demo`·`svelte/demo`입니다. studyFinal은 `project/`와 `react/project`·`vue/project`·`svelte/project`입니다.
- 새 studyN.md 문서를 추가/수정할 때는 이전 study 문서와 이어지는 흐름을 유지합니다.
- 기본 출력은 정적입니다. 요청마다 렌더하는 페이지에만 `export const prerender = false`를 둡니다. 어댑터는 `@astrojs/node` standalone입니다.
- 세 프론트 폴더는 **같은 호스트 페이지 안에서 서로 다른 섬**입니다. 한 프레임워크 파일을 고칠 때 다른 프레임워크 파일을 같이 고치지 않습니다.

## 3. 커밋 규칙

- 커밋 관련 규칙은 [COMMIT_GUIDE.md](./COMMIT_GUIDE.md) 문서를 따릅니다.

## 4. 언어 규칙

- 문서 내용, 커밋 설명: 한글
- 커밋 타입(prefix), 코드, 식별자, 파일명: 영어

## 5. 에이전트별 문서

- Claude: [.claude/CLAUDE.md](../.claude/CLAUDE.md)
- Grok: [.grok/GROK.md](../.grok/GROK.md)
- Codex: [.codex/AGENTS.md](../.codex/AGENTS.md)

## 6. 인수인계 원칙

- 작업을 마칠 때는 다음 에이전트/세션이 이어받을 수 있도록 변경 내용과 다음 단계 후보를 간단히 남깁니다.
- 불확실한 결정은 추측하지 말고 study 문서 내용을 근거로 삼습니다.
- 이 문서나 커밋 가이드에 없는 새로운 컨벤션이 필요해지면, 추측해서 각자 다르게 처리하지 말고 이 문서를 먼저 갱신합니다.

## 7. 현재 진행 현황

- 학습 문서와 실습 코드 작성 전입니다.
- `node_modules`, `.astro`, `dist`, `.env`, `data/guestbook.json`은 커밋하지 않습니다.

### 다음 단계 후보

- `study0.md`부터 이론을 적고, `demo/`를 `npm create astro`로 만듭니다.
