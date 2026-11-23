# 실행 검증 기록

2026-11-23(Asia/Seoul), Windows·PowerShell·Node 24.14.0·npm 11.9.0에서 확인했다. 외부 유료 API·메일 발송·실결제는 실행하지 않았다.

## 검증 대상 흐름

브라우저 폼 → Astro 엔드포인트 → 검증·세션·작성자 검사 → SQLite → 공통 JSON → 화면 표시를 확인한다. 문서 기능은 개인 TXT/MD 저장 → 발췌 검색 → mock AI 스트리밍 → 근거 표시 → 질문 이력 저장을 확인한다.

| 경계 | 확인 방법 | 결과 |
|---|---|---|
| 코드 빌드 | npm run build | 정적 화면·MDX와 Node 서버 빌드 통과 |
| 도메인·실패·mock | npm test | 11개 테스트 통과 |
| 실제 HTTP 서버·DB | npm run test:http | 계약 요청 34개 통과 |
| UI→쿠키→API→DB→UI | npx playwright test | 브라우저 시나리오 2개 통과, pageerror 없음 |
| localStorage·422 | 브라우저 별도 시나리오 | 복구·상태 메시지 확인 |
| MCP SDK 프로세스 | npm run mcp:client | tools/list와 summarize_document 호출 통과 |
| worker·SSE·WebSocket·백업·모드 | npm run test:extensions | 작업 done, 소켓 인증/왕복/거절, 백업 복구, midpoint API 제한 통과 |
| Compose 설정 문법 | docker compose config --quiet | web/worker·외부 DB compose 모두 통과 |
| 의존성·ORM 스키마 | npm audit --omit=dev·스키마 import | 알려진 취약점 0개, Drizzle 두 스키마 import 통과 |
| 문서 구성·원문·소스·링크 | python scripts/check_docs.py | 21개·8개 구성·코드 블록 72개·원문 3개·로컬 링크 통과 |

## 실제 확인한 조건

- 가입 201·중복 이메일 409·로그인 200·잘못된 자격증명 401.
- HttpOnly 세션 쿠키와 Bearer 인증, 로그아웃 후 이전 토큰 401, 세션 만료 거절.
- 게시글 등록 201과 Location, 목록 data/meta·limit 최대 50·검색, 상세·PATCH·삭제 204.
- PATCH에서 body만 수정할 때 기존 tags·title 유지.
- 미인증 작성 401, 다른 작성자의 수정·댓글 삭제 403.
- 잘못된 JSON·빈 제목·page=0·잘못된 id의 공통 오류, 헤더와 오류 requestId 일치.
- 댓글 작성·집계·삭제와 목록 캐시 무효화.
- 타 Origin의 변경 요청 거절, 악성 HTML 문자열을 텍스트로 출력하고 img 요소를 만들지 않음.
- 개인 문서 저장과 다른 계정의 다운로드 거절, AI NDJSON 응답.
- AI upstream SSE를 바이트 하나씩 쪼개도 한글이 올바르게 복원됨.
- mock 메일은 delivered=false, mock 결제는 paid=false, 가짜 메일 HTTP 실패는 502.
- 배경 작업 세 번째 실패 후 failed, 캐시 복사본 격리·무효화.
- 단일 worker 실제 프로세스의 done 전환, 인증된 SSE가 자기 작업 상태 전송, WebSocket ready/pong과 무인증 401.
- Node backup API로 만든 SQLite 파일을 새 연결로 열어 사용자 건수 확인.
- COURSE_STAGE=midpoint에서 기본 API 200·심화 문서 API 404.
- 배포 health의 X-Release-Sha가 실행 환경의 릴리스와 일치하며 본문은 공통 v1 형식 유지.
- 브라우저 문서 화면 스크린샷을 열어 한글·폼·응답 표시를 육안 확인.

## 발견하고 수정한 문제

첫 도메인 검사에서 zod partial 스키마가 tags 기본값을 적용해 기존 태그를 비웠다. PATCH 스키마의 tags에서 default를 제거하고 회귀 테스트를 통과시켰다. AI 중단 버튼은 submit 버튼만 비활성화하도록 처리해 생성 중에도 취소할 수 있게 했다.

## 추가 환경이 필요한 검증

- Docker CLI는 있지만 Linux 엔진 pipe가 없어 이미지 build/run은 실행하지 못했다. compose·Dockerfile·Actions를 제공하며 실제 컨테이너 검증은 엔진이 있는 환경에서 수행한다.
- PostgreSQL·MariaDB·MongoDB 드라이버·스키마·compose·동일 CRUD 검사 코드는 제공했다. 외부 DB 서버에 연결한 실행 결과는 없다.
- 실제 모델 품질·비용, Resend 전달, Stripe 테스트 계정 checkout/웹훅, GitHub OAuth callback은 키·계정 설정 후 별도 검증한다.
- GitHub Actions 실행·GHCR 게시·호스팅 배포는 푸시 이후의 외부 실행이다. 파일이 있다고 실행 성공으로 표시하지 않는다.

현재 학습 저장 모델은 JSON payload·전체 목록 조회를 사용한다. 큰 서비스로 확장하기 전 DB 조건 조회·정규화·트랜잭션·인덱스·공유 캐시·작업 원자적 claim을 보강한다.
