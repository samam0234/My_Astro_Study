# Notion 원문과 요청 반영표

기준일: 2026-11-23(Asia/Seoul). [Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f) 전체와 연결된 [공통 API v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e), [미니 프로젝트 명단](https://app.notion.com/p/40bd7dec5e2e81dab88fda4b558aa498), DocuForge·SocialForge 페이지를 읽었다. 본문 잘림 경고나 확인 불가 하위 블록은 없었다. 관련 페이지는 요구 이해용이며 갱신 대상은 지정 Astro 페이지다.

## 원문 섹션별 대응

| 원문 | 새 과정 반영 |
|---|---|
| 콘텐츠 중심·정적 기본·사용 시점 | study0·1, 정적 홈 |
| Astro 프로젝트 | study0 설치·버전·폴더·Git·env |
| .astro 컴포넌트/레이아웃 | study2 Desk·NoteCard·props·slot |
| 정적 생성·하이드레이션/client 지시어 | study0·4·10·12 실행 경계·지시어 설명 |
| 외부 화면 프레임워크 섬 실습 | 단독 Astro 조건과 충돌: 개념 설명, 신규 통합 없음 |
| 콘텐츠 컬렉션/MDX | study4 스키마·glob·welcome.mdx·정적 상세 |
| 서버 endpoint/API | study6 DB·CRUD·공통 v1 |
| 정적 랜딩 + 게시판 목록 | course `/`와 `/board`→`/api/posts` |
| 기존 client load/idle/visible 섬 구조 | 지시어 원리로 반영, 기존 코드 이력 보존 |
| static·prerender=false·adapter | study4·6·10, 실제 API 설정 |
| 방문 쿠키·요청별 값 | study7에서 세션 쿠키·만료·로그아웃으로 확장 |
| PUBLIC 빌드 시 고정 | study0·8·10, .env.example |
| 타 프레임워크 비교 | 새 비교 표 없이 Astro 자체 실행 경계 설명 |
| 메모 컬렉션·정적 상세 코드 | study4 notes·getStaticPaths·render |
| 기존 demo/project·메모 데스크 | README에 이전 이력으로 표시 |
| 공통 v1·미니 프로젝트 링크 | study6·14·midpoint·final |
| DB 없음 기록 | study11 원문 체크 보존, 현재 SQLite 설명 |
| SocialForge 익명 ID 사례 | study18 검증→생성→저장, 새 앱은 인증·소유권 적용 |
| DocuForge 등 AI 미니 프로젝트 | study18·final 문서→검색→근거 답변 |

## 추가 체크 항목 원문 보존

원문에 진도 번호가 없어 기능을 다루는 진도에 배치했다. 문구를 변경하지 않고 학습자 체크는 미체크로 두었다.

| 위치 | 원문 항목 | 처리 |
|---|---|---|
| study6 §⑦ | 학습 목표의 예제 "정적 랜딩 + 게시판 목록 하나"를 스펙 v1 API(Express 또는 FastAPI)로 목록 읽기 | 그대로 수록. 별도 서버 지정은 단독 조건과 충돌. 동일 v1은 Astro로 구현 |
| study10 §⑦ | 정적 빌드의 한계 기록: 글 작성 후 목록이 바뀌려면 재빌드 또는 `<code>prerender = false</code>` | 그대로 수록. 정적 콘텐츠/동적 API 경계 구현 |
| study11 §⑦ | DB 칸이 정리 영역에 없다 → 저장소를 확인해 이 페이지에 기록 (DB 없음, 아래 저장 방식과 코드 스니펫) | 그대로 수록. 과거 기록이며 현재 course는 SQLite |

**체크리스트에 넣지 못한 추가 항목: 없음(3/3 반영).**

## 사용자 요청 반영

| 요청 | 결과 |
|---|---|
| study0~10, midpoint, study11~18, final | study 접두사 root 문서 21개 |
| 기존 study 덮어쓰기 | study0~10·studyFinal 갱신 |
| 공통 8개 구성 | 모든 문서 ①~⑧ |
| 전체 코드·줄별 설명 | 실제 소스와 일치하는 코드·1행부터 설명표 |
| 직접 해보기 2~3개 | 모든 문서에 반영 |
| 단계별 주제·프로젝트 | 지정 기능·순서·구성도·체크·회고 |
| 코드·README | 실제 course 앱·테스트·실행 목차 |
| 코드·md 후 노션 | 검증 후 지정 페이지 최신 기록 갱신 |
| 커밋·푸시 | COMMIT_GUIDE 진도별 커밋·origin/master |

## 충돌·미검증 항목

1. 별도 백엔드 호출·다른 화면 프레임워크 섬은 최신 요청의 단독 Astro·비교/통합 금지를 우선했다. 원문 문구를 삭제하거나 완료 처리하지 않았다.
2. 과거 DB 없음·방문 쿠키·메모 데스크 설명은 이력으로 보존하고 현재 SQLite·세션·게시판·문서 AI와 구분한다.
3. DocuForge의 PDF·DOCX·PPTX·OCR·임베딩은 미니 예제 범위 밖이다. TXT·MD와 단어 검색으로 같은 학습 주제를 구현했다.
4. 외부 DB 3종·live 모델/메일/결제/OAuth·Docker 실행·실제 배포는 코드·설정·절차를 제공했고 환경·계정 검증이 필요하다. [검증 기록](verification.md)을 참고한다.

## 공식 근거

정적/요청 시 실행은 [Astro on-demand rendering](https://docs.astro.build/en/guides/on-demand-rendering/), 요청 경계는 [middleware](https://docs.astro.build/en/guides/middleware/), 이벤트는 [scripts](https://docs.astro.build/en/guides/client-side-scripts/), 상태는 [Nano Stores 안내](https://docs.astro.build/en/recipes/sharing-state-islands/)를 확인했다.

저장·백업은 [Node SQLite](https://nodejs.org/docs/latest-v24.x/api/sqlite.html), ORM은 [Drizzle](https://orm.drizzle.team/docs/overview), MCP는 설치한 1.x의 [서버](https://ts.sdk.modelcontextprotocol.io/server)·[클라이언트](https://ts.sdk.modelcontextprotocol.io/client)를 기준으로 했다. 외부 서비스는 [GitHub OAuth](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps), [Stripe SDK](https://github.com/stripe/stripe-node), [Resend API](https://resend.com/docs/api-reference/emails/send-email)를 확인했다.
