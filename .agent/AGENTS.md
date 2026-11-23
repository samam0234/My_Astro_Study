# Astro 학습 저장소 인수인계

## 범위와 기준

- 기준은 [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f)와 사용자의 최신 요청이다.
- 현재 과정은 Astro 하나만 다룬다. 다른 화면/서버 프레임워크 비교·통합을 추가하지 않는다.
- 순서는 study0~10 → studyMidpoint → study11~18 → studyFinal, 루트 학습 파일은 모두 study 접두사다.
- 앱은 `course/`, 로컬 주소는 http://127.0.0.1:4323 이다. `demo/`, `project/`, 기존 섬 폴더는 이전 이력이다.
- 기본 출력은 static이며 요청 시 API는 prerender=false와 Node adapter standalone으로 실행한다.

## 작업 규칙

- 작업 전 README·해당 진도 문서·요구사항 매핑을 읽고 코드와 문서의 연결을 확인한다.
- 각 문서는 목표·이론·전체 코드/줄별 설명·연동·오류·연습·체크·다음 단계의 8개 구성을 유지한다.
- 소스 변경 뒤 `python scripts/build_docs.py`로 코드 블록을 갱신하고 `python scripts/check_docs.py`로 확인한다. 해설 변경은 generator의 해당 진도에 함께 반영한다.
- 노션 추가 체크 원문 3개는 study6·10·11에서 문구를 바꾸지 않는다. 충돌·미검증은 docs/requirements.md에 명시한다.
- 문서·커밋 설명은 한국어, 코드·식별자·파일명과 커밋 타입은 영어다.
- 커밋은 [COMMIT_GUIDE.md](COMMIT_GUIDE.md)에 따라 진도 순서·진도별로 나눈다.
- .env·DB·업로드·로그·node_modules·dist·.astro·브라우저 테스트 산출물은 커밋하지 않는다.
- 사용자 지시대로 코드와 md 작업·검증을 끝낸 다음 지정 노션을 갱신한다.

## 검증과 현재 상태

- Node 24.14.0·Astro 7.4.13 기준이다.
- `course/`에서 npm test·build·test:http·test:extensions·MCP client·Playwright로 검증한다.
- 단위 11개·HTTP 34개·브라우저 2개, worker/SSE/WebSocket·백업 복구·midpoint 제한·MCP 호출을 확인했다.
- Docker 엔진과 외부 DB·실제 제공자 계정·호스팅은 별도 환경 검증 대상이다. mock 통과를 live 성공으로 적지 않는다.
- 구현 제약과 실행 증거는 docs/requirements.md, docs/verification.md를 기준으로 이어간다.

## 다음 작업 후보

Docker 실행 환경·외부 DB 3종·제공자 테스트 계정·호스팅에서 남은 검증을 수행한다. 고부하 운영 전 JSON 저장 모델을 조건 쿼리·정규화·트랜잭션으로 개선하고 캐시·worker의 다중 프로세스 정책을 마련한다.
