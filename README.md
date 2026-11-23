# Astro 학습 데스크

[Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f)를 기준으로 **Astro 하나**를 학습하는 21개 문서와 실행 코드입니다. 기존 study0~10·studyFinal은 갱신했고 study11~18·studyMidpoint를 추가했습니다.

현재 학습 앱은 **`course/`**, 주소는 **http://127.0.0.1:4323**입니다. Astro 템플릿·브라우저 스크립트와 Node adapter를 사용하며 다른 화면/서버 프레임워크를 호출하지 않습니다.

## 실행

Node 24.14.0 이상과 npm을 준비합니다. 잠금 파일 기준 Astro 7.4.13, Node adapter 11.1.14입니다.

```powershell
cd course
npm ci
Copy-Item .env.example .env
npm run dev
```

기존 `.env`가 있으면 필요한 설정만 편집합니다. 기본 DB는 `course/data/desk.sqlite`, 외부 서비스와 AI는 mock입니다. `/auth`에서 가입·로그인하고 `/board`에서 글·댓글을 관리합니다. `/documents`는 개인 TXT·MD 문서 저장·요약·질문, `/services`는 메일 작업·테스트 결제·알림입니다. `/api-docs`와 `/openapi.json`은 API 문서입니다.

배포 산출물은 `npm run build`, `npm start`로 확인합니다. 별도 터미널의 `npm run worker`로 메일 작업을 처리합니다. `npm run mcp:client`는 실제 SDK stdio 서버를 띄워 모의 요약 도구를 호출합니다. `COURSE_STAGE=midpoint`로 빌드·실행하면 기초 게시판 API만 열립니다.

## 문서 순서

모든 문서는 목표·이론·전체 코드와 줄별 설명·연동·오류·직접 해보기·체크리스트·다음 단계의 8개 구성을 따릅니다.

| 문서 | 주제 |
|---|---|
| [study0](study0.md) | 환경·설치·버전·Git·환경변수 |
| [study1](study1.md) | Hello World·문법·개발자도구 |
| [study2](study2.md) | 컴포넌트·레이아웃·props·slot |
| [study3](study3.md) | 서버 변수·브라우저 상태·localStorage |
| [study4](study4.md) | 라우팅·동적 경로·컬렉션·MDX·404 |
| [study5](study5.md) | 폼·검증·응답 코드·중복 제출 |
| [study6](study6.md) | SQLite·공통 API v1·게시글/댓글 CRUD |
| [study7](study7.md) | 가입·로그인·세션·권한·보안 |
| [study8](study8.md) | 모듈·설정·개발/운영 분리 |
| [study9](study9.md) | 단위·HTTP·브라우저·mock·오류 TOP 10 |
| [study10](study10.md) | 빌드·Node 배포·HTTPS·기초 정리 |
| [studyMidpoint](studyMidpoint.md) | 기초만으로 만드는 게시판 서비스 |
| [study11](study11.md) | PostgreSQL·MariaDB·MongoDB·ORM |
| [study12](study12.md) | UI CSS·상태·폼 라이브러리 |
| [study13](study13.md) | 결제·메일·파일·OAuth |
| [study14](study14.md) | REST·OpenAPI·버전·페이지·오류 |
| [study15](study15.md) | 측정·캐시·배경 작업·재시도 |
| [study16](study16.md) | Docker·Actions·배포·로그·백업 |
| [study17](study17.md) | SSE·WebSocket·파일 다운로드 |
| [study18](study18.md) | 문서 AI·근거 검색·스트리밍·MCP |
| [studyFinal](studyFinal.md) | 심화 서비스·배포·보안·회고 |

## 검증

```powershell
cd course
npm test
npm run build
npm run test:http
npx playwright install chromium
npx playwright test
npm run mcp:client
cd ..
python scripts/check_docs.py
```

학습자 체크는 비워 두고 실제 결과를 [검증 기록](docs/verification.md)에 적었습니다. 외부 DB·live 제공자·Docker 실행·호스팅 배포는 별도 환경 검증이 필요합니다.

## 원문 반영

추가 체크 항목 **3개 모두**를 study6·10·11에 원문대로 넣었습니다. [요구사항 매핑](docs/requirements.md)에 반영 위치·제약을 적었습니다. 별도 백엔드와 다른 화면 프레임워크 섬 실습은 이번 단독 Astro 조건과 충돌해 실행하지 않았습니다.

기존 `demo/`, `project/`, `react/`, `vue/`, `svelte/`는 이전 이력입니다. 새 `course/`의 의존성·별칭·엔드포인트는 이 폴더들에 의존하지 않습니다.

소스 변경 후 `python scripts/build_docs.py`로 코드 블록을 갱신합니다. `scripts/check_docs.py`는 21개 문서 구성·원문 체크·링크·코드 일치를 검사합니다.
