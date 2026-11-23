"""검증한 course 소스와 학습 해설을 root study 문서에 동기화한다."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f'
API_SPEC = 'https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e'
DOCU = 'https://app.notion.com/p/40bd7dec5e2e818d9c91c6fb26dccc4c'
SOCIAL = 'https://app.notion.com/p/40bd7dec5e2e81cb8c76d6d66962619a'

# title, goal, theory, integration, exercises, checklist, files, detailed lab.
LESSONS = [
('환경 설정', 'Astro 개발 환경과 Git·환경변수 경계를 준비한다.',
'''Astro는 콘텐츠를 HTML로 만드는 웹 프레임워크다. 정적 생성은 주문 전에 책을 인쇄하는 것, 요청 시 렌더링은 주문받은 다음 개인별 안내장을 만드는 것에 비유할 수 있다. 처음에는 정적 페이지를 만들고, 회원·DB처럼 요청 데이터가 필요한 경로에만 서버 실행을 연다.

핵심 용어는 `.astro`(템플릿 파일), frontmatter(`---` 안 서버 코드), props(부모가 전달하는 값), slot(자식 HTML 자리), endpoint(HTTP 처리 함수), adapter(배포 런타임 연결), prerender(빌드 시 HTML 생성), hydration(서버 HTML에 브라우저 동작 연결), content collection(스키마로 검증하는 콘텐츠 묶음)이다.

이 저장소의 실행 기준은 Node 24.14.0, npm 11.9.0, Astro 7.4.13, Node adapter 11.1.14다. 라이브러리의 재현 기준은 `course/package-lock.json`이다. `npm ci`는 잠금 파일과 다른 의존성 선언을 허용하지 않는다.''',
'Git은 코드와 예제 설정을 저장하고, `.env`는 로컬 실행 환경을 제공한다. DB 비밀번호와 API 키는 서버 환경변수이며 브라우저용 `PUBLIC_` 접두사를 붙이지 않는다. 다음 단계는 이 환경에서 `/` 페이지를 출력한다.',
['`node -v`, `npm -v`, `npm ls astro @astrojs/node` 결과를 기록한다.', '`.env`의 공개 사이트 이름을 바꾸고 개발 서버를 재시작한다.', '`git check-ignore course/.env`로 비밀 파일이 무시되는지 확인한다.'],
['Node·npm·Astro 버전을 확인했다.', '폴더별 역할과 정적/요청 시 실행을 설명할 수 있다.', '개발 서버와 에디터 확장을 준비했다.', 'Git 저장소·.gitignore·.env.example·.env를 구분했다.'],
['course/package.json','course/astro.config.mjs','course/.env.example'],
'''새 폴더에서 처음 생성하는 방법과 이미 받은 저장소를 실행하는 방법을 구분한다. 이 저장소 안의 `course/`를 다시 생성하지 않는다.

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

VS Code 확장은 `astro-build.astro-vscode`와 `esbenp.prettier-vscode`를 권장한다. `.astro` 언어 지원과 포맷팅을 제공한다. `src/pages`는 URL, `src/components`는 재사용 화면, `src/layouts`는 공통 HTML, `src/lib`는 서버 로직, `src/client`는 브라우저 로직, `src/content`는 콘텐츠, `public`은 그대로 제공할 파일, `scripts`는 운영 도구, `tests`는 검증이다. 생성되는 `node_modules`, `.astro`, `dist`, `data`는 커밋하지 않는다.'''),
('Hello World와 기본 문법', 'frontmatter와 템플릿 표현식으로 첫 정적 화면을 만든다.',
'''`.astro`의 `---` 사이 JavaScript는 서버 또는 빌드에서 실행된다. 아래 HTML의 `{title}`은 그 값을 출력한다. 배열은 `map()`으로 반복하고, 조건은 `조건 && <태그>` 또는 삼항식으로 표현한다. `class` 속성은 HTML과 같이 쓴다. 변수는 브라우저 반응형 상태가 아니므로 클릭으로 값을 바꿀 때에는 별도 `<script>`가 필요하다.

템플릿은 편지 양식, frontmatter는 편지에 넣을 주소와 문구다. 값의 계산과 HTML의 표시 위치를 구분하면 서버 비밀값을 템플릿에 실수로 출력하는 일도 줄어든다. 기본 출력은 HTML이며 공통 CSS는 자바스크립트 상태 관리와 별개다.''',
'개발 서버의 파일 감시가 저장한 템플릿을 반영한다. 브라우저 개발자도구 Network에서 Document 응답, Elements에서 결과 DOM, Console에서 오류를 확인한다. 다음 단계에서 반복되는 화면을 컴포넌트로 분리한다.',
['홈 제목과 배열 항목을 바꿔 자동 새로고침을 확인한다.', '배열이 비었을 때 안내 문구가 보이는 조건부 출력을 만든다.'],
['frontmatter와 HTML을 구별했다.', '`{표현식}`과 `map()`을 사용했다.', '개발자도구와 개발 서버 변경 반영을 확인했다.'],
['course/src/pages/index.astro'],
'''`course/src/pages/index.astro` 전체를 아래 코드와 맞춘다. `npm run dev`로 홈을 연 뒤 제목을 바꿔 저장한다. 개발 서버에서 보이는 Vite 도구 스크립트와 배포 번들을 혼동하지 않는다. `npm run build` 후 `dist/client/index.html`을 열어 출력 문구를 찾는다. 원본 템플릿에 있는 표현식은 빌드 결과에서 실제 문자열로 바뀐다.'''),
('핵심 구조', '페이지·레이아웃·컴포넌트를 props와 slot으로 조립한다.',
'''Astro의 화면 기본 단위는 `.astro` 컴포넌트다. `src/pages` 파일은 URL이 되지만 `components` 파일은 import해서 사용해야 나타난다. 레이아웃도 자동 적용되지 않으므로 페이지에서 `<Desk>...</Desk>`로 감싼다.

props는 부품을 주문할 때 적는 규격이고 slot은 부품 안에 남겨 둔 빈칸이다. `Astro.props`로 제목과 링크를 받고, 기본 `<slot />`으로 본문을 받는다. 이름 있는 slot은 부모의 `slot="meta"`와 자식의 `<slot name="meta" />`가 연결된다. 서버에서 props를 바꿔도 이미 전달된 브라우저 HTML이 스스로 바뀌지는 않는다.''',
'페이지 배열 → NoteCard props → HTML의 순서로 값을 전달한다. 브라우저 동작 간 통신은 DOM 이벤트 또는 공유 모듈을 사용하며, 서버 데이터 갱신은 API 요청을 거친다. 다음 단계에서 브라우저 상태와 저장을 다룬다.',
['NoteCard에 `description` prop을 추가하고 기본값을 둔다.', 'meta slot을 빼거나 다른 문구로 바꿔 출력 위치를 확인한다.', '다른 카드 두 개를 같은 페이지에 재사용한다.'],
['페이지와 일반 컴포넌트의 차이를 설명했다.', 'props·기본 slot·이름 있는 slot을 연결했다.', '반복 마크업을 재사용 파일로 분리했다.'],
['course/src/components/NoteCard.astro','course/src/layouts/Desk.astro','course/src/pages/lessons.astro'],
'''`/lessons`를 연다. 부모 배열 `items`의 `title`, `href`가 카드 속성이 되고 본문의 `<p>`가 기본 slot으로 들어간다. 레이아웃의 `<slot />` 자리에 페이지 전체가 들어간다. 이 진도에서는 `Draft`의 내부 동작은 다음 진도의 부품으로만 읽는다. 자식에서 부모의 서버 변수를 직접 수정하는 구조를 만들지 않는다.'''),
('데이터 다루기', '서버 변수와 브라우저 상태를 구분하고 로컬 메모를 저장한다.',
'''서버의 `const items`는 HTML을 만들 때만 읽힌다. 브라우저에서 입력 중인 값은 `textarea.value`이며 이벤트 핸들러가 이를 저장한다. 이것이 이번 과정의 바인딩이다. 입력 → input 이벤트 → localStorage → 다음 방문 시 value 복구의 연결을 직접 작성한다.

서버 변수는 인쇄소의 원고, 브라우저 상태는 독자가 책에 붙인 메모에 가깝다. localStorage는 같은 출처·같은 브라우저에서만 유지된다. 로그인 비밀 토큰을 넣지 않으며, 여러 기기에서 공유할 데이터는 다음 DB API에 저장한다. 브라우저의 사생활 보호 설정이나 저장 용량 때문에 저장이 실패할 수 있어 try/catch가 필요하다.''',
'`Draft.astro`의 `<script>`만 브라우저로 전달된다. localStorage 키 `astro-draft`는 서버에서 읽지 않는다. 다음 단계는 URL 쿼리에도 상태를 담아 공유 가능한 화면 주소를 만든다.',
['메모를 작성하고 새로고침해 복구되는지 확인한다.', '개발자도구 Application에서 키를 지운 뒤 다시 연다.', '글자 수를 별도 `<output>`에 실시간 표시한다.'],
['서버 변수와 DOM 상태를 구분했다.', 'input 이벤트로 화면과 저장소를 연결했다.', '저장 실패 메시지와 복구 흐름을 만들었다.'],
['course/src/components/Draft.astro'],
'''`/lessons`에서 입력하고 새로고침한다. 입력 중 서버 요청은 발생하지 않는다. Network 탭에서 이를 확인한다. 문서 전체를 서버 파일로 저장하는 방법은 study6의 SQLite 파일 저장으로 확장한다. 이 단계의 데이터는 개인 초안이며 영구 DB의 원본이 아니다.'''),
('라우팅과 요청 처리', '파일 라우트·동적 경로·쿼리·404를 연결한다.',
'''`src/pages/index.astro`는 `/`, `board.astro`는 `/board`, `notes/[id].astro`는 `/notes/값`이다. 동적이라는 말이 항상 요청마다 렌더한다는 뜻은 아니다. 정적 동적 경로는 `getStaticPaths()`가 빌드할 값들을 반환한다. 요청 시 엔드포인트는 `prerender = false`로 실행한다.

URL은 도서관의 서가 주소다. pathname은 책 위치, query는 검색·정렬 조건이다. `URLSearchParams`로 값을 인코딩하면 공백·한글이 포함돼도 안전하다. 링크는 `<a href>`로 이동하고, 검색 상태만 바꿀 때 `history.replaceState`를 사용할 수 있다. 없는 화면은 404 페이지로, 없는 API는 공통 JSON 404로 응답한다.''',
'화면 `/board?q=astro&page=1`의 검색 조건을 `/api/posts?q=astro&page=1&limit=5`로 그대로 전달한다. 파일 이름과 호출 주소가 같은 계약인지 확인한다. 다음 단계에서 이 요청 경로에 폼 입력을 보낸다.',
['`/notes/welcome`, `/없는주소`의 상태 코드를 확인한다.', '쿼리 `q`에 한글·공백을 넣고 새로고침한다.', '콘텐츠 노트 파일 하나를 추가하고 빌드해 새 경로를 만든다.'],
['파일 이름에서 URL을 찾을 수 있다.', '`getStaticPaths`와 `prerender = false`의 차이를 설명했다.', 'query 인코딩·404·페이지 이동을 확인했다.'],
['course/src/pages/notes/[id].astro','course/src/content.config.ts','course/src/content/notes/welcome.mdx','course/src/pages/404.astro','course/src/pages/api/[...path].js'],
'''콘텐츠 컬렉션은 파일을 DB처럼 수정하는 도구가 아니다. `glob()`이 MD·MDX를 읽고 zod 스키마가 title·description을 검증한다. MDX의 컴포넌트도 빌드 시 HTML이 된다. 콘텐츠를 바꾸면 다시 빌드한다. API catch-all은 HTTP 메소드와 경로를 공통 dispatcher에 넘긴다. 정적 콘텐츠와 DB 게시글 경로를 `/notes`와 `/api/posts`로 분리한다.'''),
('폼·입력·검증', '브라우저 검증과 서버 검증을 연결하고 중복 제출을 막는다.',
'''HTML의 `required`, `minlength`, `maxlength`, `type=email`은 사용자가 빠르게 실수를 고치도록 돕는다. 네트워크 요청을 직접 만드는 사람은 이를 우회할 수 있으므로 서버에서 zod로 다시 검증한다. strict 스키마는 예상하지 않은 필드를 거절한다.

클라이언트 검증은 접수 창구의 안내, 서버 검증은 실제 심사다. 제출 중 busy 플래그와 버튼 비활성화로 같은 폼의 연속 클릭을 막는다. 재시도에 따른 서버 중복 결제까지 이 방식으로 보장되는 것은 아니므로 study13에서 idempotency key를 추가한다. 오류는 `textContent`로 표시해 HTML로 실행하지 않는다.''',
'formAction → JSON fetch → 서버 schema → 공통 응답 → status 메시지의 순서다. 공통 명세 v1은 검증 실패 400을 사용한다. 200은 로그인/수정, 201은 등록, 204는 본문 없는 성공이다. 422도 클라이언트에서 처리하고 브라우저 mock으로 확인하지만 자체 API가 422를 내지는 않는다.',
['빈 제목·200자 초과 제목을 서버에 직접 보내 400 fields를 확인한다.', '버튼을 빠르게 연속 클릭해 요청이 하나인지 확인한다.', '브라우저 테스트의 422 mock을 500으로 바꿔 오류 메시지를 확인한다.'],
['HTML과 서버 검증을 둘 다 사용했다.', '400·422·200·201·204를 구분했다.', '중복 제출 방지와 오류 표시를 구현했다.'],
['course/src/client/api.mjs','course/src/lib/validation.mjs'],
'''`/auth`의 가입·로그인 폼 또는 `/board`의 editor 폼에 값을 넣는다. API와 인증은 다음 두 단계에서 완성한다. 이번 진도는 폼 연결과 입력 계약을 먼저 읽는다. 제출 중에는 submit 버튼만 잠그므로 AI 화면의 중단 버튼 같은 일반 버튼은 계속 사용할 수 있다. HTTP 204는 JSON 파싱하지 않는다.'''),
('DB·API 연동', 'SQLite 저장소로 공통 API v1 게시글 CRUD를 만든다.',
'''API는 화면과 저장소 사이의 약속이다. DB는 메모장이 아니라 프로세스가 재시작되어도 남는 원본이다. 이번 과정은 Node 내장 SQLite의 파일 DB를 사용한다. `records` 테이블은 `id`, `kind`, `payload`, `unique_key`로 구성하고 users·posts·comments 등을 kind로 구분한다. payload는 JSON 문자열이며 대규모 서비스의 정규화 스키마를 대신하는 학습용 저장 모델이다.

저장소 계약은 `create/list/get/replace/remove/close` 여섯 함수다. SQL 값은 바인딩으로 전달해 사용자 입력을 SQL 문장으로 합치지 않는다. 날짜는 ISO 8601 UTC, API 필드는 camelCase다. 등록은 201과 Location, 부분수정은 PATCH 200, 삭제는 204다. 작성 API는 다음 진도의 로그인 사용자만 허용한다.''',
f'[공통 API 스펙 v1]({API_SPEC})의 `/api/posts`·`data/meta`·`error.fields/requestId`를 따른다. UI가 같은 Astro 앱의 API를 호출하며 별도 서버 프레임워크는 실행하지 않는다. DATABASE_URL과 DB_DRIVER를 바꾸는 경계는 study11에서 확장한다.',
['가입·로그인 후 글을 등록하고 반환한 id로 상세·수정·삭제한다.', '서버를 재시작해 DB의 글이 유지되는지 확인한다.', '검색·정렬·limit=100을 호출해 50으로 제한되는지 확인한다.'],
['연결 설정→모델→목록→상세→등록→수정→삭제 순서로 확인했다.', 'DB 연결 정보를 환경변수로 분리했다.', 'data/meta와 공통 오류 형식을 구현했다.', '학습 목표의 예제 "정적 랜딩 + 게시판 목록 하나"를 스펙 v1 API(Express 또는 FastAPI)로 목록 읽기'],
['course/src/lib/store.mjs','course/src/lib/posts.mjs','course/src/lib/basic-api.mjs'],
'''`cd course` 후 `.env`를 준비한다. 기본은 `DB_DRIVER=sqlite`, `DATABASE_URL=./data/desk.sqlite`다. 첫 요청 또는 `npm run test:db`가 파일과 records 테이블을 만든다. UI는 `/auth`에서 계정을 만든 다음 `/board`에서 글을 저장한다. 상태 401은 DB 실패가 아니라 로그인 요구다.

아래 store 파일의 다른 DB 분기는 study11에서 읽는다. 이 진도는 sqlite 분기와 공통 메소드만 사용한다. 정적 랜딩은 `/`, 요청 시 조회되는 목록은 `/api/posts`다. 위 원문 추가 체크 항목은 외부 서버를 지정하므로 이번 Astro 단독 범위에서는 체크하지 않는다. 동등한 v1 계약은 Astro 엔드포인트로 구현했다.'''),
('인증·보안 기초', '회원가입·로그인·세션·권한과 기본 공격 방어를 구현한다.',
'''인증은 누군지 확인하는 일, 인가는 그 사람이 이 글을 바꿀 수 있는지 확인하는 일이다. 비밀번호는 scrypt와 무작위 salt로 해시한다. 같은 비밀번호도 해시가 달라지며 로그인 때 timingSafeEqual로 비교한다. 비밀번호 원문과 해시는 응답에 포함하지 않는다.

세션은 출입증이다. 32바이트 무작위 토큰을 발급하고 DB에는 SHA-256 digest만 저장한다. 브라우저는 HttpOnly·SameSite=Lax 쿠키로, API 클라이언트는 Bearer 헤더로 같은 세션을 보낸다. 유효시간은 1시간이다. 로그아웃은 현재 토큰의 세션 레코드와 쿠키를 함께 폐기한다.

CORS는 브라우저가 다른 출처의 응답을 읽는 규칙이지 인증이 아니다. 변경 요청의 Origin을 허용 출처와 비교하고 JSON Content-Type을 요구해 CSRF 표면을 줄인다. 응답은 textContent와 Astro 기본 이스케이프를 사용해 XSS를 줄인다. raw HTML 출력은 사용하지 않는다. 운영에서는 HTTPS와 정확한 SITE_URL을 필수로 맞춘다.''',
'middleware가 쿠키/Bearer → digest 조회 → locals.user를 만들고 handler가 requireUser/owned로 검사한다. 브라우저는 토큰을 localStorage에 저장하지 않는다. 프론트의 로그인 상태 확인은 `/api/auth/me` 응답으로 한다.',
['두 계정을 만들어 서로의 글 수정이 403인지 확인한다.', '로그아웃한 토큰과 만료 토큰으로 401을 확인한다.', '악성 HTML 문자열과 허용하지 않은 Origin을 테스트한다.'],
['비밀번호 해시와 세션 만료를 구현했다.', '미인증 401과 작성자 불일치 403을 구분했다.', 'CORS·XSS·CSRF와 HTTPS 쿠키 설정을 설명했다.'],
['course/src/lib/auth.mjs','course/src/middleware.js','course/src/pages/auth.astro'],
'''`/auth`에서 가입→로그인→내 정보→로그아웃을 순서대로 실행한다. 개발자도구 Application의 쿠키에서 HttpOnly·SameSite를 확인한다. API 응답에는 accessToken도 있지만 이 화면은 저장하지 않고 쿠키를 사용한다. `SITE_URL=https://...`일 때 Secure 쿠키가 켜지므로 로컬 HTTP와 운영 HTTPS 설정을 섞지 않는다. 인증 실패의 메시지는 이메일 존재 여부를 구분하지 않는다.'''),
('구조화·재사용', '서버·브라우저·설정·저장소의 역할을 나누고 실행 환경을 분리한다.',
'''모든 파일을 pages에 넣으면 URL 처리·검증·SQL·화면 로직이 섞인다. pages는 요청 진입점, lib는 서버 기능, client는 브라우저 기능, layouts/components는 화면 부품으로 나눈다. 설정은 settings 함수 한 곳에서 기본값과 환경변수 우선순위를 정한다.

이 구조는 주방의 주문 접수·조리·창고를 나누는 것과 비슷하다. HTTP handler가 실제 DB 종류를 몰라도 저장 계약으로 일하고, 테스트가 가짜 저장소를 주입할 수 있다. 서버 전용 모듈을 client에서 import하면 비밀이나 Node 의존성이 브라우저로 넘어갈 수 있으므로 파일 경계를 지킨다.''',
'개발은 `.env`, 운영은 호스팅 환경변수 또는 compose env_file로 설정한다. `npm start`는 Node의 env-file 옵션으로 .env를 읽고, 빌드용 PUBLIC 값은 빌드 시 확정된다. 다음 단계는 이 모듈 경계를 이용해 테스트를 작성한다.',
['다른 포트용 SITE_URL·PORT·CORS_ORIGIN을 함께 바꾼다.', '서버 비밀값을 PUBLIC_로 만들면 어떤 위험이 있는지 기록한다.', 'settings에 새 설정을 추가하고 호출부에서 직접 process.env 접근을 줄여 본다.'],
['pages/lib/client/components/layouts/content/scripts/tests의 책임을 구분했다.', '공통 HTTP·검증·설정 모듈을 재사용했다.', '개발·운영 환경과 빌드·런타임 환경변수를 구분했다.'],
['course/src/lib/config.mjs','course/src/lib/http.mjs'],
'''기본 폴더 구조는 아래와 같다.

```text
course/
  src/pages/       화면·API URL
  src/layouts/     공통 HTML
  src/components/  props·slot 부품
  src/client/      DOM·fetch·상태
  src/lib/         검증·인증·저장소·서비스
  src/content/     MD·MDX 원본
  public/          OpenAPI 문서
  scripts/         worker·백업·MCP·측정
  tests/           도메인·브라우저 검증
```

HTTP 오류는 HttpError로만 사용자 메시지를 드러내며 예상하지 못한 오류는 requestId와 서버 로그를 남긴다. 호출자가 준 요청 ID는 문자·숫자·하이픈 등 제한된 100자만 허용한다. 비밀번호·토큰·문서 본문은 로그에 쓰지 않는다.'''),
('테스트·디버깅', '단위·요청·브라우저 테스트와 mock으로 경계를 검증한다.',
'''단위 테스트는 한 규칙을 빠르게 확인하고, HTTP 테스트는 실제 요청·쿠키·헤더·직렬화를 확인한다. 브라우저 테스트는 폼 이벤트와 화면 표시까지 확인한다. 단위 테스트만으로 DOM 버튼이 작동한다고 말할 수 없고, 화면만으로 DB에 저장됐다고 말할 수도 없다.

mock은 연습용 대역이다. AI·메일에는 fetcher/전송 함수를 주입하고, DB는 fakeStore로 바꾼다. 통합 검사는 메모리 SQLite와 실제 파일 DB로 별도 실행해 mock이 숨기는 오류를 줄인다. 이번 테스트가 잡은 사례는 PATCH에서 tags 기본값이 기존 태그를 덮는 오류다. 부분수정 스키마에서 tags의 default를 제거해 고쳤다.''',
'단위 테스트→실제 빌드→HTTP 서버→브라우저 순으로 검증한다. X-Request-Id를 브라우저 Network와 서버 JSON 로그에서 대조한다. 다음 단계 배포 전에도 같은 검사를 실행한다.',
['태그 보존 테스트가 tags 기본값을 잘못 넣었을 때 실패하는지 확인한다.', '가짜 메일 응답을 500으로 바꿔 502 변환을 확인한다.', '브라우저 422 mock에서 오류 문구를 읽는다.'],
['단위 테스트와 실제 HTTP 요청 테스트를 실행했다.', 'DB·외부 API를 테스트 대역으로 바꿨다.', 'Network·Console·서버 로그와 requestId로 디버깅했다.', '자주 나는 오류 TOP 10을 기록했다.'],
['course/tests/fake-store.mjs','course/tests/domain.test.mjs','course/scripts/smoke.mjs','course/playwright.config.mjs','course/tests/browser/flow.spec.mjs'],
'''`course/`에서 실행한다.

```powershell
npm test
npm run build
npm run test:http
npx playwright install chromium
npx playwright test
```

1행은 도메인 규칙과 mock, 2행은 실제 배포 산출물, 3행은 임시 DB·포트 4393의 실제 서버, 4행은 브라우저 설치, 5행은 포트 4394의 실제 사용자 흐름이다. 테스트 서버는 사용자의 기본 DB를 재사용하지 않는다. HTTP 검증은 임시 디렉터리를 만들고 종료 시 지운다. 브라우저 테스트 DB는 무시되는 `course/data/e2e.sqlite`다.

VS Code JavaScript Debug Terminal에서 `npm start`를 실행하고 서버 handler에 breakpoint를 건다. 브라우저 Sources에서는 script 모듈과 fetch 지점을 확인한다. 401은 세션, 403은 권한/Origin, 400은 입력, 500은 서버 로그로 범위를 줄인다.'''),
('배포·정리', '정적 파일과 Node 서버를 빌드·실행하고 배포 후 점검한다.',
'''빌드는 개발 코드를 배포 산출물로 바꾸는 단계다. Node adapter가 있으면 정적 페이지는 `dist/client`, 동적 API는 `dist/server/entry.mjs`로 나뉜다. 정적 파일만 호스팅하면 로그인·CRUD 요청을 실행할 서버가 없어진다.

도메인은 서버를 찾는 이름, DNS는 이름을 주소로 바꾸는 안내, HTTPS는 브라우저와 서버 사이 암호화와 서버 신원 확인이다. 일반적인 Node 서버 앞에 HTTPS reverse proxy를 두고 쿠키의 Secure 설정과 SITE_URL을 실제 공개 URL에 맞춘다. DB 파일은 배포 이미지 밖의 영속 볼륨에 둔다. PUBLIC 값은 정적 HTML에 들어가므로 바뀌면 다시 빌드해야 한다.''',
'로컬에서 npm start로 검증한 산출물을 서버에서 실행한다. 운영은 HOST=0.0.0.0·PORT·SITE_URL·DATABASE_URL·CORS_ORIGIN을 맞춘다. 다음 문서는 기초 구간만 조합한 midpoint 서비스다.',
['빌드 후 홈과 API를 각각 요청하고 출력 위치를 확인한다.', 'DB 경로를 별도 디렉터리로 바꾸고 서버 재시작 후 글이 남는지 확인한다.', 'HTTPS 프록시 뒤의 쿠키 Secure·Origin 설정을 점검한다.'],
['npm ci·build·start 순서로 실행했다.', '도메인·DNS·HTTPS·Secure 쿠키를 설명했다.', '환경변수·DB 영속 경로·헬스체크를 점검했다.', '정적 빌드의 한계 기록: 글 작성 후 목록이 바뀌려면 재빌드 또는 <code>prerender = false</code>'],
['course/astro.config.mjs','course/src/pages/health.js','course/Dockerfile'],
'''개발 서버를 종료한 다음 `course/`에서 실행한다.

```powershell
npm ci
npm run build
$env:HOST='127.0.0.1'
$env:PORT='4323'
npm start
```

1행은 의존성을 고정하고 2행은 산출물을 만든다. 3~4행은 바인딩 주소와 포트이고 5행이 배포용 서버다. `/`, `/notes/welcome`, `/board`, `/health`, `/api/posts`, `/없는주소`를 확인한다. `/board` 껍데기는 정적이지만 목록 데이터는 `prerender = false` API를 매번 조회한다. 따라서 새 글에 UI 재빌드는 필요하지 않다. 정적 MDX 원본 변경에는 재빌드가 필요하다.

기초 총정리: study0 환경 → 1 템플릿 → 2 부품 → 3 상태 → 4 URL → 5 폼 → 6 DB/API → 7 인증 → 8 구조 → 9 검증 → 10 배포다. Docker 상세·자동화는 study16에서 다룬다. 현재 로컬 Docker 엔진이 실행되지 않아 이미지 실행 검증은 별도 미완료 항목이다.'''),
('DB 확장', '저장소 계약을 유지하며 PostgreSQL·MariaDB·MongoDB로 연결을 바꾼다.',
'''DB 교체는 URL 한 줄만 바꾸는 일이 아니다. 드라이버, 키 생성, 바인딩 문법, 인덱스, 트랜잭션, 백업 방법이 달라진다. 저장소 계약을 지키면 API의 data/meta 모양은 그대로 유지할 수 있다. 기존 데이터는 새 연결로 자동 이동하지 않으므로 별도 이관 검증이 필요하다.

PostgreSQL은 pg Pool과 `$1` 바인딩·SERIAL을, MariaDB는 mysql2 pool과 `?` 바인딩·AUTO_INCREMENT를 사용한다. MongoDB는 collection과 원자적 counter를 사용해 공통 명세의 숫자 id를 유지한다. 고유 키는 SQL UNIQUE와 MongoDB partial unique index로 중복 이메일을 막는다.

ORM 예제는 Drizzle로 SQL 테이블을 표현한다. PostgreSQL 스키마는 pgTable·serial·text, MariaDB는 mysqlTable·int.autoincrement·longtext다. MongoDB는 이 SQL ORM 스키마를 공유하지 않고 공식 드라이버를 쓴다. 운영 API의 기본 구현은 명시적 드라이버이며 ORM 조회는 별도 실행 예제다.''',
'동일한 openStore 계약→test:db→API/브라우저 회귀 검사 순서로 교체한다. 생산 데이터 이관은 백업·스테이징·건수·참조·고유성 검증 후 전환한다. 다음 단계는 이 API와 UI 라이브러리의 연결을 다룬다.',
['DB 서비스 하나를 실행하고 DB_DRIVER·DATABASE_URL을 바꿔 test:db를 실행한다.', 'Drizzle 조회 예제를 같은 DB에 실행한다.', '중복 이메일과 재시작 후 데이터 보존을 각 DB에서 확인한다.'],
['DB별 연결·pool·id·바인딩·unique 인덱스를 구분했다.', '드라이버와 ORM의 책임·스키마 차이를 설명했다.', '기존 DB 백업과 별도 데이터 이관 절차를 정리했다.', 'DB 칸이 정리 영역에 없다 → 저장소를 확인해 이 페이지에 기록 (DB 없음, 아래 저장 방식과 코드 스니펫)'],
['course/src/lib/store.mjs','course/examples/orm-schema.mjs','course/examples/orm-query.mjs','course/compose.db.yml','course/scripts/db-contract.mjs'],
'''로컬 Docker 엔진이 켜져 있을 때만 `course/`에서 실행한다. 기본값은 학습 전용 비밀번호이며 공개 서버에 그대로 쓰지 않는다.

```powershell
docker compose -f compose.db.yml up -d postgres
$env:DB_DRIVER='postgres'
$env:DATABASE_URL='postgresql://astro:local-study-only@127.0.0.1:5438/astro'
npm run test:db
node examples/orm-query.mjs
```

1행은 PostgreSQL 컨테이너, 2~3행은 드라이버와 접속, 4행은 같은 저장 계약의 CRUD, 5행은 ORM 조회다. MariaDB는 `docker compose -f compose.db.yml up -d mariadb`, `DB_DRIVER=mariadb`, `DATABASE_URL=mysql://astro:local-study-only@127.0.0.1:3308/astro`로 바꾼다. MongoDB는 서비스 mongodb, 드라이버 mongodb, URL `mongodb://astro:local-study-only@127.0.0.1:27018/astro?authSource=admin`이다.

실습 후 `Remove-Item Env:DB_DRIVER,Env:DATABASE_URL`로 셸 설정을 되돌린다. `.env`에 저장한 값도 확인한다. 테이블은 openStore가 생성하므로 ORM 예제 실행 전에 test:db를 실행한다. 고도화 시 정규화 테이블과 버전 있는 migration을 도입하고, 이 JSON 저장 모델의 메모리 목록 조회를 SQL 조건·인덱스로 옮긴다. 위 원문 DB 없음 항목은 예전 저장 방식의 기록이며 새 course 앱에는 SQLite가 있다. 현재 환경에서는 외부 DB 3종 실행을 검증하지 않았다.'''),
('프론트·UI 연동', 'Astro 템플릿에 CSS UI·상태·폼 검증 라이브러리를 연결한다.',
'''UI 라이브러리가 반드시 별도 화면 프레임워크일 필요는 없다. Pico CSS는 의미 있는 HTML 태그에 스타일을 주며 Astro 레이아웃에서 한 번 import한다. Nano Stores atom은 작은 브라우저 상태를 보관하고 subscribe로 DOM 표시를 갱신한다. zod는 서버와 폼에서 쓸 수 있는 스키마 검증 라이브러리다.

화면은 게시판, atom은 포스트잇 숫자판, zod는 접수 규칙에 비유할 수 있다. 서버 모듈의 전역 atom에 사용자 데이터를 넣으면 요청 사이에서 공유될 수 있으므로 상태 저장은 client 파일에서만 한다. formAction은 제출 제어, HTML은 기본 유효성, 서버 zod는 최종 검증을 담당한다.

Astro의 `client:load/idle/visible/media/only`는 지원되는 UI 컴포넌트를 하이드레이션하는 지시어다. 이 과정은 단독 Astro 조건을 지키므로 외부 화면 프레임워크 섬을 추가하지 않는다. `.astro`에는 client 지시어를 붙이지 않고 `<script>`로 이벤트를 연결한다.''',
'Desk에서 Pico CSS → documents에서 DOM 이벤트 → state의 atom → count 표시로 이어진다. 폼 데이터는 공통 api 함수를 거쳐 서버 zod 검증으로 간다. 다음 단계는 외부 서비스의 실패·재시도를 처리한다.',
['Pico CSS를 제외한 빌드와 포함한 빌드의 화면을 확인한다.', 'atom을 구독하는 표시를 다른 컴포넌트에 하나 더 만든다.', '폼 입력에 zod safeParse를 추가해 서버와 같은 필드 규칙을 사전 안내한다.'],
['UI CSS·브라우저 상태·폼 검증 라이브러리를 연결했다.', '서버 전역 상태에 개인 데이터를 보관하지 않는다.', 'client 지시어 개념과 이번 코드의 script 방식 차이를 이해했다.'],
['course/src/client/state.mjs','course/src/client/schemas.mjs','course/src/client/api.mjs','course/src/lib/validation.mjs','course/src/layouts/Desk.astro'],
'''설치는 package-lock에 포함되어 있어 `npm ci`만 실행한다. `/documents`에서 로그인한 사용자의 문서 목록이 로드되면 documentCount.set(data.length)가 실행된다. subscribe는 count 텍스트를 갱신한다. 이 페이지의 전체 구현은 study18에서 설명한다. 브라우저 상태가 곧 DB라고 가정하지 않고 목록을 다시 조회해 원본과 맞춘다.'''),
('외부 서비스 연동', '결제·메일·파일·OAuth의 설정과 안전한 호출 경계를 구현한다.',
'''외부 서비스 호출은 성공·실패·지연·중복이 생길 수 있는 네트워크 작업이다. 결제 화면으로 이동했다고 결제가 확정된 것은 아니다. 서버가 서명된 웹훅을 검증하고 이벤트 id로 중복을 막아야 한다. 이 학습 코드는 Stripe 테스트 키만 허용하고 결제 이벤트를 기록한다. 상품 권한 부여·환불·실결제 운영은 별도 업무 규칙이 필요하다.

메일은 서버에서 Resend API를 호출하며 키를 브라우저로 보내지 않는다. 기본 mock 응답은 delivered=false다. 파일은 TXT·MD UTF-8 텍스트만 받고 크기를 제한하며 무작위 이름으로 public 밖에 저장한다. 다운로드에도 소유권을 확인한다.

OAuth는 외부 출입증을 일회용 code로 교환하는 흐름이다. state는 요청 위조를, PKCE verifier/challenge는 code 가로채기 위험을 줄인다. callback URL은 등록된 SITE_URL과 일치해야 한다. 제공자 이메일을 검증 없이 기존 계정에 합치지 않는다.''',
'브라우저→Astro API→메일/Stripe/GitHub의 서버 호출로 이어진다. 파일→개인 문서 레코드→study18의 AI 입력으로 연결한다. 외부 키 없이 mock으로 로컬 전체 흐름을 확인하고 live는 별도 테스트 계정에서 검증한다.',
['mock 메일 작업과 checkout 응답에서 완료 여부가 false인지 확인한다.', '100000바이트를 넘는 파일과 다른 계정 문서 다운로드가 거절되는지 확인한다.', 'OAuth callback의 state를 바꿔 400이 되는지 확인한다.'],
['메일·결제·파일·OAuth 호출 코드를 읽고 mock/live를 구분했다.', 'OAuth state·PKCE와 다운로드 소유권을 검증한다.', '웹훅 서명·원문·이벤트 중복과 결제 요청 key를 확인했다.', '서비스 키·콜백·발신 도메인 설정 후 실제 테스트 계정 검증을 수행한다.'],
['course/src/lib/integrations.mjs','course/src/lib/files.mjs','course/src/pages/services.astro'],
'''기본 `.env`의 INTEGRATIONS_MODE=mock을 유지하면 유료 요청은 일어나지 않는다. `/auth` 로그인 후 `/services`에서 메일 작업 등록과 테스트 결제 응답을 확인한다. 메일 worker는 study15에서 실행한다.

실제 테스트 계정 연결 시 INTEGRATIONS_MODE=live, RESEND_API_KEY·검증된 MAIL_FROM, STRIPE_SECRET_KEY=sk_test_...·STRIPE_PRICE_ID·STRIPE_WEBHOOK_SECRET을 서버 환경에 둔다. Stripe webhook은 `/api/stripe/webhook`이며 프록시도 원문 바이트를 바꾸면 안 된다. GitHub OAuth 앱은 `/api/oauth/callback`을 callback으로 등록하고 GITHUB_CLIENT_ID·GITHUB_CLIENT_SECRET을 설정한다. OAuth는 mock 로그인으로 대체하지 않고 키가 없으면 503을 반환한다. 이 저장소 작업에서는 실제 메일·결제·OAuth 계정 호출을 하지 않았다.'''),
('API 설계', 'REST 경로·OpenAPI·버전·페이지네이션·공통 오류를 명세로 고정한다.',
'''REST 경로는 리소스를 나타낸다. `/api/posts`의 GET은 목록, POST는 등록이며 `/api/posts/{id}`의 GET·PATCH·DELETE는 상세·부분수정·삭제다. 공통 API v1의 경로를 그대로 사용하므로 URL에 임의로 /v1을 추가하지 않는다. 버전은 현재 문서 계약 1.0.0이며 호환성을 깨는 후속 계약에 새 경로 또는 협상 정책을 따로 정한다.

페이지네이션은 도서관 목록의 쪽 번호다. page는 1부터, limit은 기본 10·최대 50, q는 제목/본문 대소문자 무시 부분 검색, sort는 createdAt·-createdAt·-commentCount다. 목록은 data 배열과 meta를 갖고 오류는 error 객체 안에 code/message/fields/requestId를 갖는다.

OpenAPI는 요청·응답 계약의 기계가 읽는 지도다. `/api-docs`에 경로를 표시하고 `/openapi.json`을 Swagger Editor 등에 가져올 수 있다. 코드와 문서를 함께 바꾸고 HTTP 계약 테스트로 상태·헤더·응답 모양을 확인한다.''',
f'[기준 명세]({API_SPEC})→OpenAPI→Astro dispatcher→저장소→브라우저 api 함수 순서로 연결한다. 204는 본문이 없고 201은 Location을 보낸다. HTTP X-Request-Id와 오류 본문의 requestId를 맞춘다.',
['limit=100·page=0·잘못된 id를 각각 호출한다.', 'X-Request-Id를 지정해 응답 헤더·오류 본문에서 같은 값인지 확인한다.', 'OpenAPI JSON을 Swagger Editor에 가져와 경로와 입력 필드를 확인한다.'],
['공통 v1의 모든 인증·게시글·댓글 경로를 구현했다.', '페이지·정렬·검색·공통 오류와 요청 ID를 명세에 맞췄다.', 'OpenAPI 3.1 문서와 /api-docs를 제공한다.'],
['course/src/lib/basic-api.mjs','course/src/lib/api.mjs','course/src/pages/api-docs.astro'],
'''서버 실행 후 `/api-docs`에서 엔드포인트를 확인한다. 전체 OpenAPI 파일은 `course/public/openapi.json`이며 학습 예제의 추가 API(문서·AI·메일·결제·OAuth·SSE)도 함께 명시한다. 추가 API는 공통 게시판 계약의 필수 경로를 바꾸지 않는다.

```powershell
Invoke-RestMethod 'http://127.0.0.1:4323/api/posts?q=Astro&page=1&limit=10&sort=-createdAt'
Invoke-WebRequest 'http://127.0.0.1:4323/health'
```

첫 줄은 목록 data/meta, 둘째 줄은 준비 상태와 헤더를 확인한다. 스트리밍은 예외적으로 NDJSON/SSE 미디어 타입이며 스트림 도중 발생한 오류는 이미 보낸 200 상태를 바꿀 수 없어 프레임 안에 오류를 보낸다.'''),
('성능·캐시', '측정 후 짧은 캐시와 영속 배경 작업으로 요청 비용을 나눈다.',
'''성능 최적화는 먼저 시간을 재고 병목을 찾는 일이다. 정적 콘텐츠는 빌드 시 계산하고 공개 게시글 목록은 프로세스 내부 TTL 캐시에 잠깐 보관한다. 개인 정보 응답과 인증 응답은 HTTP no-store다. 캐시된 객체를 복사해 반환하면 호출자가 값을 바꿔 원본 캐시를 손상시키지 않는다.

캐시는 잠시 보는 복사본, DB는 원본이다. 글·댓글을 변경하면 관련 캐시를 지운다. 현재 캐시는 단일 web 프로세스 기준이며 다중 프로세스에서는 Redis 같은 공유 캐시와 공통 무효화가 필요하다. 최대 100개 키와 2초 TTL을 둔다.

메일은 요청에서 실제 발송을 기다리지 않고 DB job을 등록해 worker가 처리한다. 실패는 지수 간격으로 3회까지 재시도한다. 작업 id를 제공자 idempotency key로 써 재전송 중복을 줄인다. 현재 worker는 1개만 실행한다. 여러 worker에는 원자적 claim·lease·dead letter 정책이 필요하다.''',
'HTTP POST /api/mail → jobs 저장 → 별도 Node worker → 외부 메일 응답 → SSE 알림으로 연결된다. 다음 단계 CI는 이 경계를 테스트하고 이미지로 묶는다.',
['npm run measure로 홈·API의 median/p95를 기록한다.', '목록 조회 직후 글을 바꿔 캐시가 무효화되는지 확인한다.', '실패하는 가짜 메일 전송으로 세 번째 실패 뒤 failed가 되는지 확인한다.'],
['측정값 없이 최적화 효과를 단정하지 않는다.', '캐시 TTL·용량·무효화·개인정보 경계를 확인했다.', '비동기 작업·재시도·중복 방지·단일 worker 제약을 설명했다.'],
['course/src/lib/cache.mjs','course/src/lib/jobs.mjs','course/scripts/worker.mjs','course/scripts/measure.mjs'],
'''터미널 두 개를 사용한다. 첫 번째는 npm start, 두 번째는 npm run worker를 실행한다. `/services`에서 메일 작업을 등록하고 SSE 연결 후 done을 확인한다. 한 작업만 처리하려면 `npm run worker -- --once`다. 서버가 실행 중일 때 `npm run measure`로 20회 요청의 중앙값과 p95를 측정한다. 이는 로컬 TTFB 유사 HTTP 총시간이며 실제 사용자 Core Web Vitals를 대신하지 않는다. 브라우저 Performance·Network에서도 번들 크기와 긴 작업을 확인한다.'''),
('운영·CI/CD', 'Docker·자동 검증·이미지 배포·모니터링·백업 절차를 만든다.',
'''컨테이너는 실행 환경과 산출물을 함께 포장한다. build 단계는 npm ci와 build를 실행하고 runtime 단계는 비루트 사용자로 서버를 실행한다. DB·업로드는 이미지 밖 볼륨에 보관한다. 비밀값을 Dockerfile·이미지·Git에 넣지 않는다.

CI는 제출된 변경을 자동 검증하는 검사대다. GitHub Actions가 단위·HTTP·브라우저·MCP·문서 검사를 실행하고 Docker 이미지를 GHCR에 커밋 SHA 태그로 게시한다. DEPLOY_ENABLED=true와 배포 훅/헬스 URL을 설정하면 검증 후 자동 배포 훅을 호출한다. 설정되지 않은 실제 운영 서버를 배포했다고 기록하지 않는다.

로그는 요청 ID·경로·상태·시간을 구조화해 남긴다. 오류율·지연 p95·작업 실패·DB 용량·디스크 용량을 모니터링한다. 백업은 복사 성공보다 복구 성공이 중요하다. SQLite는 실행 중 WAL 파일을 단순 복사하지 않고 backup API로 스냅샷을 만든다.''',
'push→CI→GHCR 이미지→호스팅 배포 훅→HTTPS health 확인으로 잇는다. DB와 업로드 볼륨을 함께 백업하고, 이전 SHA 이미지로 롤백한다. 다음 단계는 장시간 연결과 파일 처리를 점검한다.',
['Docker 엔진이 켜진 환경에서 compose config·build·up·health를 확인한다.', 'npm run backup 후 별도 DB 파일로 열어 records 건수를 비교한다.', 'GitHub repository 변수·secret을 설정하고 성공·실패 배포를 연습한다.'],
['Docker 비루트 실행·영속 볼륨·비밀 제외를 확인했다.', 'Actions 검증→이미지 게시→조건부 자동 배포를 구성했다.', '로그·오류율·지연·디스크·작업 실패 모니터링 항목을 적었다.', 'DB·업로드 백업과 별도 복구·롤백 절차를 마련했다.', 'Docker 이미지 실행과 실제 호스팅 배포를 해당 환경에서 검증한다.'],
['course/Dockerfile','course/.dockerignore','course/compose.yml','.github/workflows/ci.yml','course/scripts/backup.mjs'],
'''`course/`에서 `.env`를 만든 후 실행한다.

```powershell
docker compose config --quiet
docker compose up -d --build
docker compose logs --tail 50 web worker
Invoke-RestMethod 'http://127.0.0.1:4323/health'
npm run backup
```

1행은 설정 문법, 2행은 web·worker 실행, 3행은 로그, 4행은 준비 상태, 5행은 로컬 SQLite 백업이다. 컨테이너 DB를 백업하려면 `docker compose exec web node scripts/backup.mjs`로 볼륨 안에서 실행하고 스냅샷과 uploads를 별도 저장소로 복사한다.

GitHub 설정: DEPLOY_ENABLED 변수, DEPLOY_HOOK secret, HEALTH_URL 변수를 준비한다. 배포 훅은 JSON의 image·revision을 받아 GHCR SHA 이미지를 pull하고 런타임 RELEASE_SHA를 revision으로 설정해야 한다. 영속 볼륨을 유지하고 `/health`의 X-Release-Sha가 요청한 SHA인지 확인한다. 예전 서버의 200을 새 버전 배포 성공으로 판단하지 않는다. 미설정이면 이미지 게시까지만 진행한다. 도메인은 HTTPS reverse proxy로 연결하며 프록시에서 업로드/요청 크기와 연결 시간을 제한한다.

PostgreSQL은 pg_dump/pg_restore, MariaDB는 mariadb-dump, MongoDB는 mongodump/mongorestore를 사용한다. 복구는 쓰기를 중지하고 새 볼륨에 복구한 뒤 건수·로그인·문서 다운로드를 확인한다. 실패하면 기존 볼륨과 이전 이미지로 돌아간다. 현재 Docker 엔진이 없어 컨테이너 실행은 미검증이며 CI 실행 결과·외부 배포도 푸시 이후 확인 대상이다.'''),
('실시간·확장', 'SSE 알림·인증된 WebSocket과 비공개 파일 다운로드를 연결한다.',
'''SSE는 서버가 브라우저에 알림을 보내는 단방향 연결이고 EventSource가 재연결한다. WebSocket은 서버와 브라우저가 양방향 메시지를 주고받는 연결이다. 알림판과 무전기의 차이로 생각하면 된다. HTTP 응답 객체를 쓰는 Astro Node 앱에는 SSE를 그대로 붙일 수 있다.

WebSocket 예제는 Node http upgrade와 ws를 사용하는 별도 로컬 프로세스다. 새로운 웹 프레임워크를 추가하지 않는다. Astro가 발급한 같은 호스트의 HttpOnly 쿠키를 공유하고 Origin·세션을 검사한다. `/events` 경로만 허용하며 4096바이트 최대 payload와 60초 재인증 경계를 둔다.

SSE는 사용자 소유 작업만 내보내고 연결 종료·abort 때 타이머를 해제한다. 파일은 공개 URL로 노출하지 않고 소유권 검사 후 attachment로 내려준다. 대용량 바이너리 파일은 이 학습의 UTF-8 텍스트 저장과 다르므로 객체 저장소·스트리밍 업로드·백신 검사 등을 별도 설계해야 한다.''',
'job 상태→SSE→services 화면, 로그인 쿠키→WebSocket upgrade→ready/pong으로 연결된다. 다음 단계 AI 스트리밍도 연결 취소·청크 경계·출력 이스케이프를 재사용한다.',
['services에서 알림을 켜고 worker가 queued를 done으로 바꾸는지 확인한다.', '로그인 후 WebSocket ready/pong과 로그아웃 후 연결 거절을 확인한다.', '다른 계정의 문서 다운로드가 403인지 확인한다.'],
['SSE 단방향·WebSocket 양방향을 구분했다.', 'Origin·세션·메시지 크기·연결 종료를 처리했다.', '파일 다운로드에도 소유권·nosniff·attachment를 적용했다.'],
['course/scripts/socket.mjs','course/src/lib/files.mjs','course/src/pages/services.astro'],
'''첫 터미널에서 npm start, 두 번째에서 `node --env-file-if-exists=.env scripts/socket.mjs`를 실행한다. 같은 호스트 `http://127.0.0.1:4323`에서 로그인한 다음 Console에서 실행한다.

```javascript
const socket = new WebSocket('ws://127.0.0.1:4324/events');
socket.onmessage = event => console.log(JSON.parse(event.data));
socket.onopen = () => socket.send('ping');
```

1행은 upgrade 연결, 2행은 수신 표시, 3행은 연결 후 메시지 전송이다. 쿠키는 포트로 분리되지 않지만 호스트가 localhost와 127.0.0.1로 다르면 공유되지 않는다. 운영은 같은 공개 origin의 `/socket`을 upgrade 프록시하고 wss를 사용해야 한다. 컨테이너 기본 compose는 SSE만 실행하며 socket 예제는 자동 노출하지 않는다.'''),
('AI 연동·MCP', '개인 문서를 근거로 AI 요약·질문 스트림과 MCP 도구를 구현한다.',
f'''AI 모델 호출은 브라우저가 아니라 Astro 서버에서 수행한다. 기본 AI_MODE=mock은 실제 모델 품질을 검증하지 않는 결정적 대역이다. live는 OpenAI 호환 Chat Completions SSE를 읽는다. 키·모델·기본 URL은 서버 환경변수로 분리하며 timeout과 브라우저 중단 신호를 전달한다.

프롬프트는 system의 행동 규칙과 user의 질문·발췌 데이터를 나눈다. 문서 안의 명령을 따르지 않도록 지시하고 근거가 없으면 찾을 수 없다고 답하도록 한다. 간단한 검색은 600자 청크에서 질문 단어가 일치하는 상위 3개를 고른다. 한국어 형태소·임베딩 검색의 품질까지 보장하지 않는 학습용 RAG다.

[DocuForge]({DOCU})에서 문서→청크 검색→근거 번호 응답이라는 학습 주제, [SocialForge]({SOCIAL})에서 입력 검증→모델 호출→결과 저장이라는 주제를 가져온다. 기존 프로젝트의 서버를 호출하거나 스택을 합치지 않고 같은 문제를 Astro 앱 내부에서 구현한다. TXT·MD만 지원하고 PDF·DOCX·PPTX 추출·OCR은 구현 범위 밖이다.

MCP는 AI 호스트가 도구·자원을 발견하고 호출하는 표준이다. 호스트가 클라이언트를 가지고 클라이언트가 서버의 tools/list·tools/call을 사용한다. 이번 예제는 SDK 1.32.2의 stdio transport로 summarize_document 하나를 노출한다. 새로운 SDK 계열과 import 경로를 섞지 않는다. MCP 도구 실행 자체가 모델 호출을 자동 결정하는 에이전트는 아니다.''',
'업로드→소유권 검사→청크/프롬프트→모델 SSE→Astro NDJSON→브라우저 textContent→질문 이력 DB로 잇는다. 별도 MCP 클라이언트는 같은 complete 함수를 도구로 호출한다. 최종 문서에서 이 기능과 운영 구성을 함께 점검한다.',
['mock과 live를 구분해 응답·timeout·키 누락 오류를 확인한다.', '근거 단어가 있는 질문과 없는 질문의 발췌를 비교한다.', 'npm run mcp:client로 도구 검색과 호출 응답을 확인한다.'],
['AI 키를 서버에만 두고 소유 문서만 입력했다.', '프롬프트 규칙·근거 검색·청크 경계·스트림 중단을 처리했다.', '질문 이력을 DB에 저장하고 응답을 HTML로 실행하지 않는다.', 'MCP stdio 서버·클라이언트의 실제 도구 호출을 실행했다.', '실제 모델 품질·비용·timeout은 키를 설정한 별도 환경에서 검증한다.'],
['course/src/lib/ai.mjs','course/src/pages/documents.astro','course/scripts/mcp-server.mjs','course/scripts/mcp-client.mjs'],
'''로그인 후 `/documents`에서 TXT·MD를 선택하거나 내용을 입력해 저장한다. 문서 id가 질문 폼에 자동 입력된다. 질문을 비우면 요약, 질문을 넣으면 근거 검색이다. 중단 버튼은 fetch를 abort한다. NDJSON은 한 네트워크 청크가 한 JSON이라는 가정을 하지 않고 TextDecoder와 줄 버퍼로 읽는다.

```powershell
npm run mcp:client
# 실제 모델 호출은 별도 테스트 계정에서 설정 후 실행
$env:AI_MODE='live'
$env:AI_BASE_URL='https://api.openai.com/v1'
$env:AI_MODEL='gpt-4o-mini'
# AI_API_KEY는 .env 또는 보안 설정에서 입력한다.
npm start
```

첫 줄은 자식 MCP 서버를 띄우고 도구 목록·호출을 확인한 뒤 닫는다. 이후 행은 서버의 live 제공자 설정이며 키를 로그/문서/커밋에 쓰지 않는다. MCP client 예제는 명시적으로 mock을 사용하므로 별도 API 비용이 없다. stdio 서버의 stdout에는 JSON-RPC만 쓰고 진단은 stderr로 보낸다. HTTP MCP 공개 서버·도구 쓰기 권한·OAuth 인증은 이 미니 예제의 범위 밖이다.'''),
]

ERRORS = {
0: [('node 명령 없음','런타임 미설치 또는 PATH','Node 설치 후 새 터미널에서 버전 확인'),('npm ci 실패','package와 lock 불일치','정당한 의존성 변경 후 lock 갱신, 일반 실행은 ci'),('포트 사용 중','기존 개발 서버','기존 서버 종료 또는 포트·SITE_URL 함께 변경')],
1: [('화면이 안 바뀜','빌드 서버만 실행','개발 중 dev 사용, 배포는 재빌드'),('표현식 문법 오류','중괄호/태그 닫기 누락','터미널의 파일·줄 위치 확인')],
2: [('카드 내용 없음','slot 이름 불일치','부모 slot과 자식 name 맞추기'),('props가 undefined','필수 값 누락','Props와 전달부 확인')],
3: [('window is not defined','서버에서 브라우저 API 사용','script 안으로 이동'),('로컬 저장 실패','저장소 차단·용량','예외 처리와 사용자 안내')],
4: [('정적 경로 빌드 실패','getStaticPaths 없음','생성할 id 반환'),('API 404','파일 경로·호출 주소 불일치','/api 경로 대조'),('콘텐츠 동기화 실패','frontmatter 필드 누락','title·description 수정')],
5: [('204 JSON 파싱 오류','빈 응답을 json() 처리','204일 때 즉시 반환'),('중복 저장','submit 기본 동작/중복 클릭','preventDefault와 busy'),('422 화면 이상','서버별 코드 차이','클라이언트 오류 분기와 mock 검사')],
6: [('DB 파일 열기 실패','경로·쓰기 권한','상위 디렉터리와 영속 경로 확인'),('등록 401','세션 없음','가입 후 로그인'),('SQL 오류','문자열로 SQL 조합','파라미터 바인딩 사용')],
7: [('로그인 뒤 401','Secure 쿠키와 HTTP 불일치','SITE_URL·접속 host 확인'),('다른 계정 수정 403','작성자 불일치','정상 인가 동작인지 확인'),('403 Origin','허용 출처 불일치','SITE_URL·CORS_ORIGIN 정확히 지정')],
8: [('서버에서 비밀값 없음','런타임 env 미주입','npm start env-file/호스팅 설정 확인'),('브라우저에 Node 모듈 오류','client에서 서버 모듈 import','파일 경계 분리')],
9: [('HTTP 테스트 서버 대기 실패','빌드 누락·포트 충돌','build 후 4393 포트 확인'),('브라우저 실행 실패','Chromium 미설치','playwright install chromium'),('PATCH에서 태그 삭제','부분 스키마에 default 잔존','partial tags에서 default 제거')],
10: [('정적 홈만 동작','Node 서버 미실행','dist/server/entry.mjs 실행'),('DB가 배포 때 초기화','컨테이너 내부 임시 경로','영속 볼륨 마운트'),('Docker 연결 실패','Desktop 엔진 없음','엔진 준비 후 별도 검증')],
11: [('connection refused','DB 서비스/포트 미준비','DB 서비스 준비 후 연결'),('Mongo 인증 실패','authSource 누락','admin 인증 DB 지정'),('새 DB에 데이터 없음','연결 교체만 수행','별도 이관·검증 실행')],
12: [('문서 수가 안 바뀜','atom set 또는 subscribe 누락','서버 목록 후 set 확인'),('client 지시어 오류','.astro에 hydration 지시어 사용','script 이벤트로 구현')],
13: [('OAuth 400','state/callback/쿠키 host 불일치','등록 URL과 실제 호스트 맞추기'),('Stripe 400','웹훅 원문 변형·서명 불일치','raw body와 webhook secret 확인'),('메일 502','발신 도메인/제공자 실패','서버 설정과 제공자 로그 확인')],
14: [('등록 상태가 200','생성 계약 누락','201과 Location 사용'),('requestId 불일치','예외 handler 경로 분산','공통 middleware 사용'),('204 파싱 오류','응답 본문 기대','본문 없이 종료')],
15: [('변경 글이 이전 값','캐시 무효화 누락','글·댓글 변경 후 clear'),('메일 중복','여러 worker 또는 비멱등 전송','단일 worker·제공자 key'),('작업 계속 queued','worker 미실행','worker 프로세스 로그 확인')],
16: [('컨테이너 DB 권한 오류','볼륨 소유자 불일치','node 사용자 쓰기 권한'),('이미지 게시 403','packages 권한 부족','workflow packages:write와 저장소 설정'),('배포가 건너뜀','DEPLOY_ENABLED 미설정','필요 환경에서 변수·secret 구성')],
17: [('WebSocket 401','쿠키·Origin·세션 없음','같은 host에서 로그인 후 연결'),('SSE가 몰려서 출력','프록시 버퍼링','SSE 경로 버퍼링 끄기'),('종료 후 타이머 남음','cancel 처리 누락','abort/cancel에서 clearInterval')],
18: [('한글 스트림 깨짐','청크마다 독립 decode','TextDecoder stream:true'),('MCP 파싱 오류','stdout에 일반 로그','stderr로 진단 분리'),('AI 503/502','키 없음·upstream 실패','서버 설정·timeout·제공자 로그 확인')],
}

def explanation(line, path):
    s = line.strip()
    if not s: return '코드 구간을 나누는 빈 줄이다.'
    if s.startswith(('//', '# ')): return s.lstrip('/# ').strip()
    if s == '---': return '서버 frontmatter와 HTML 템플릿의 경계를 표시한다.'
    if s.startswith('import '): return f'`{s.split(" from ")[-1].strip("; ")}`의 기능을 이 파일에서 사용한다.'
    if s.startswith(('export const prerender',)): return '이 경로를 빌드 시 고정하지 않고 요청마다 실행한다.'
    if 'getStaticPaths' in s: return '정적 생성에서 빌드할 동적 URL 목록을 정의한다.'
    if 'process.env' in s or 'import.meta.env' in s: return '실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다.'
    if 'fail(' in s: return '조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다.'
    if 'catch' in s: return '실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다.'
    if 'finally' in s: return '성공·실패에 관계없이 연결/잠금 등 정리 작업을 실행한다.'
    if 'requireUser' in s: return '미인증 사용자를 401로 거절하고 인증 사용자만 다음 처리를 허용한다.'
    if 'owned(' in s: return '자원 존재와 작성자 일치를 확인해 다른 사람의 데이터 접근을 막는다.'
    if 'validate(' in s or '.safeParse(' in s: return '정해진 스키마로 입력을 검사하고 허용된 값만 다음 계층으로 보낸다.'
    if 'cookies.set' in s: return '서버가 쿠키와 보안 속성을 응답에 설정한다.'
    if 'cookies.delete' in s: return '같은 경로의 쿠키를 만료시켜 브라우저 출입증을 지운다.'
    if 'cookies.get' in s: return '요청 쿠키 값을 서버에서 읽는다.'
    if 'textContent' in s: return '문자열을 HTML로 실행하지 않고 텍스트로 표시해 XSS 표면을 줄인다.'
    if 'localStorage.setItem' in s: return '같은 브라우저·출처의 로컬 저장소에 현재 입력값을 저장한다.'
    if 'localStorage.getItem' in s: return '이 브라우저에 이전에 저장한 초안을 읽어 입력값을 복구한다.'
    if 'addEventListener' in s or '.onclick' in s or '.onsubmit' in s: return '브라우저 이벤트가 발생했을 때 실행할 함수를 연결한다.'
    if 'preventDefault' in s: return '기본 폼 이동을 막고 비동기 요청 흐름을 사용한다.'
    if 'fetch(' in s or 'fetcher(' in s: return 'HTTP 요청을 보내 응답을 기다린다. 주입된 fetcher는 테스트에서 대체할 수 있다.'
    if 'JSON.stringify' in s: return '객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다.'
    if 'JSON.parse' in s: return 'JSON 문자열을 객체로 해석한다. 잘못된 입력은 상위 오류 처리로 넘긴다.'
    if 'return json(' in s or 'Response.json' in s: return '명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다.'
    if 'new Response' in s: return '응답 본문·상태·헤더 또는 스트림을 담은 HTTP Response를 만든다.'
    if 'response.headers.set' in s: return '응답 헤더에 보안·요청 추적·CORS 또는 캐시 정책을 설정한다.'
    if 'assert.' in s or 'expect(' in s: return '실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다.'
    if s.startswith(('test(', 'test.')): return '독립적으로 확인할 테스트 시나리오를 정의한다.'
    if 'store.create' in s: return '저장소 계약으로 새 레코드를 생성하며 생성 id를 받는다.'
    if 'store.replace' in s: return '검증한 변경 값을 지정 레코드에 저장한다.'
    if 'store.remove' in s: return '지정 kind와 id의 레코드를 삭제한다.'
    if 'store.list' in s: return '저장소에서 해당 종류의 레코드를 읽어 필터·검증·응답에 사용한다.'
    if 'store.get' in s: return '종류와 id가 일치하는 단일 레코드를 조회한다.'
    if 'db.prepare' in s or 'db.execute' in s or 'db.query' in s: return 'DB 드라이버에 SQL과 바인딩 값을 전달해 이 저장 작업을 수행한다.'
    if '.createIndex' in s: return '조회 또는 고유성 보장을 위한 인덱스를 만든다.'
    if '.map(' in s: return '목록의 각 항목을 화면 또는 응답에 필요한 모양으로 변환한다.'
    if '.filter(' in s: return '조건에 맞는 항목만 남겨 검색·소유권·근거 범위를 줄인다.'
    if '.sort(' in s: return '정해진 비교 규칙에 따라 결과 순서를 맞춘다.'
    if 'new TextDecoder' in s or '.decode(' in s: return '분리된 UTF-8 바이트를 문자 경계를 보존하며 문자열로 복원한다.'
    if 'controller.enqueue' in s or 'yield ' in s: return '스트림 소비자가 다음 조각을 받을 수 있도록 데이터를 내보낸다.'
    if 'reader.read' in s or 'iterator.next' in s: return '다음 스트림 조각 또는 생성 토큰을 비동기로 읽는다.'
    if '.cancel(' in s or '.close(' in s or '.releaseLock' in s: return '사용이 끝난 스트림·소켓·DB 자원을 종료하거나 잠금을 해제한다.'
    if 'scrypt' in s: return 'salt를 포함한 비밀번호 파생 키 계산으로 원문 저장을 피한다.'
    if 'randomBytes' in s or 'randomUUID' in s: return '예측하기 어려운 식별자·토큰·salt를 생성한다.'
    if s.startswith('export async function') or s.startswith('async function'): return f'비동기 함수 `{s.split("function",1)[1].split("(",1)[0].strip()}`의 입력과 처리 범위를 정의한다.'
    if s.startswith('export function') or s.startswith('function '): return f'재사용 함수 `{s.split("function",1)[1].split("(",1)[0].strip()}`를 정의한다.'
    if s.startswith(('const ', 'let ', 'export const ')): return '이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: ' + '`' + s.split('=')[0].strip() + '`.'
    if s.startswith(('if ', 'if(', '} else', 'else ')): return '조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다.'
    if s.startswith(('for ', 'for(', 'while ', 'while(')): return '목록 또는 스트림의 남은 항목을 순서대로 처리한다.'
    if s.startswith('return '): return '이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다.'
    if '<slot' in s: return '부모가 전달한 HTML을 이 slot 위치에 삽입한다.'
    if s.startswith(('<script', '</script')): return '브라우저에서 실행할 이벤트·DOM 코드의 경계를 정한다.'
    if s.startswith(('<style', '</style')): return '이 화면에 적용할 스타일 구간을 정한다.'
    if s.startswith(('<', '{')) and path.endswith(('.astro','.mdx')): return '이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다.'
    if s in ('}', '};', '});', '});', '];', '},', ');', ')', '})'): return '앞서 연 함수·객체·호출의 범위를 닫는다.'
    if s.startswith(('FROM ', 'COPY ', 'RUN ', 'ENV ', 'WORKDIR ', 'USER ', 'EXPOSE ', 'CMD ')): return '컨테이너 이미지의 실행 환경·복사·빌드 또는 시작 명령을 지정한다.'
    if s.startswith(('"', "'")) and ':' in s: return '이 설정 키에 대응하는 값·명령·의존성을 선언한다.'
    if s.startswith(('schema:', 'inputSchema:', 'properties:', 'services:', 'volumes:', 'steps:', '- uses:', '- run:')): return '이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다.'
    return '현재 처리 구간의 세부 값·호출·구조를 지정한다: `' + s.replace('`','')[:110] + '`.'

def source_section(path):
    code = (ROOT / path).read_text(encoding='utf-8').rstrip()
    ext = Path(path).suffix
    lang = {'.astro':'astro','.mjs':'javascript','.js':'javascript','.json':'json','.ts':'typescript','.yml':'yaml','.mdx':'mdx'}.get(ext, 'text')
    if path.endswith('Dockerfile'): lang='dockerfile'
    out = f'### `{path}` 전체 코드\n\n[{Path(path).name}]({path})를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.\n\n```{lang}\n{code}\n```\n\n줄별 설명:\n\n| 줄 | 설명 |\n|---|---|\n'
    for n, line in enumerate(code.splitlines(), 1):
        out += f'| {n} | {explanation(line,path).replace("|", "&#124;")} |\n'
    return out + '\n'

def errors_table(index):
    rows = ERRORS[index]
    if index==9:
        rows = [
            ('Node 명령 없음','런타임/PATH','Node 설치·새 터미널'),('포트 충돌','서버 중복 실행','기존 프로세스 확인'),
            ('정적 경로 실패','getStaticPaths 누락','생성 경로 반환'),('window 오류','서버에서 DOM 접근','script로 이동'),
            ('API 404','주소 불일치','src/pages와 fetch 대조'),('400 검증','필드/JSON 오류','error.fields 확인'),
            ('401 인증','쿠키 없음·만료','host·Secure·세션 확인'),('403 권한','작성자·Origin 불일치','계정·허용 출처 확인'),
            ('PATCH 태그 손실','default 적용','부분 스키마 default 제거'),('DB/외부 500·502','저장소·제공자 실패','requestId로 서버 로그 확인')]
    return '| 증상 | 원인 | 해결 |\n|---|---|---|\n'+'\n'.join(f'| {a} | {b} | {c} |' for a,b,c in rows)

def write_lessons():
    for index, (title, goal, theory, integration, exercises, checks, files, lab) in enumerate(LESSONS):
        nxt = 'studyMidpoint.md' if index==10 else ('studyFinal.md' if index==18 else f'study{index+1}.md')
        text=f'''# study{index} · {title}

## ① 목표 한 줄

{goal}

기준: [Notion Astro]({SOURCE}). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

{theory}

## ③ 🛠️ 실기

{lab}

'''
        text+=''.join(source_section(p) for p in files)
        text+=f'''## ④ 🔗 연동 포인트

{integration}

## ⑤ 오류 노트

{errors_table(index)}

## ⑥ 직접 해보기

'''+ '\n'.join(f'{n}. {value}' for n,value in enumerate(exercises,1))
        text+='\n\n## ⑦ ☐ 체크리스트\n\n'+'\n'.join('- [ ] '+value for value in checks)
        text+=f'\n\n## ⑧ 다음 단계 연결 문장\n\n이 단계의 결과를 [{nxt}]({nxt})에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.\n'
        (ROOT/f'study{index}.md').write_text(text,encoding='utf-8')

def write_projects():
    midpoint = f'''# studyMidpoint · Astro 학습 게시판

## ① 목표 한 줄

study0~10의 환경·템플릿·컴포넌트·폼·DB·인증·테스트·배포만으로 작은 게시판 서비스를 완성한다.

### 기능 목록

| 기능 | 화면·API | 배운 단계 |
|---|---|---|
| 정적 랜딩 | `/` | study1·2 |
| 콘텐츠 컬렉션·MDX 안내 | `/notes/welcome` | study4 |
| 검색·페이지·목록·상세 | `/board`, GET `/api/posts`, GET `/api/posts/{{id}}` | study4·6 |
| 회원가입·로그인·로그아웃·내 정보 | `/auth`, `/api/auth/*` | study5·7 |
| 작성·부분수정·삭제와 작성자 확인 | POST/PATCH/DELETE 게시글 API | study6·7 |
| 댓글 작성·조회·작성자 삭제 | 게시글 하위 댓글과 `/api/comments/{{id}}` | study6·7 |
| SQLite 파일 저장과 요청 테스트 | `data/desk.sqlite`, tests/scripts | study6·9 |
| Node 배포용 빌드 | `dist/client`, `dist/server` | study10 |

원문 기준은 [Notion Astro]({SOURCE}), API 기준은 [공통 API v1]({API_SPEC})다.

## ② 📖 이론

정적 페이지는 먼저 준비한 서비스 안내판이고, 로그인·쓰기·DB는 방문할 때 처리하는 접수 창구다. 정적 HTML에 개인 세션을 박지 않고 브라우저가 API에서 현재 데이터를 읽게 한다. 카드·레이아웃은 공통 부품, API는 같은 출처의 Astro 엔드포인트, SQLite는 재시작 뒤에도 남는 원본이다.

midpoint는 캐시·외부 서비스·worker·실시간·AI를 사용하지 않는다. 같은 앱을 `COURSE_STAGE=midpoint`로 실행하면 기본 API가 목록을 직접 조회하고 심화 API를 404로 막는다. 별도 서버 프레임워크 없이 화면과 API를 모두 Astro가 담당한다. 최종 코드가 누적된 저장소이므로 심화 모듈 파일은 있어도 이 모드에서 실행 경로를 사용하지 않는다.

## ③ 🛠️ 실기

### 폴더 구조

```text
course/
  astro.config.mjs
  .env.example
  src/layouts/Desk.astro
  src/components/NoteCard.astro
  src/components/Draft.astro
  src/pages/index.astro
  src/pages/auth.astro
  src/pages/board.astro
  src/pages/api/[...path].js
  src/lib/basic-api.mjs
  src/lib/auth.mjs
  src/lib/posts.mjs
  src/lib/store.mjs
  src/lib/validation.mjs
  src/middleware.js
  tests/domain.test.mjs
  scripts/smoke.mjs
```

### 단계별 구현 순서

1. study0처럼 의존성·Git·.env를 준비하고 개발 서버를 확인한다.
2. study1·2의 홈·Desk·NoteCard로 정적 랜딩을 조립한다.
3. study3·4처럼 localStorage 초안과 콘텐츠 동적 URL을 만든다.
4. study5에서 폼의 기본 유효성·서버 schema·상태 메시지·제출 잠금을 연결한다.
5. study6의 openStore SQLite 분기로 records 테이블을 만들고 게시글 CRUD를 연결한다.
6. study7의 가입·scrypt·세션·HttpOnly 쿠키·작성자 검사를 연결한다.
7. study8의 모듈 분리와 환경변수 기본값을 대조한다.
8. study9의 단위·HTTP·브라우저 검사를 실행한다. 아래 full code와 의존 파일은 각 진도 전체 코드와 동일하다.
9. study10의 build/start로 1차 운영 산출물을 확인한다.

```powershell
cd course
npm ci
Copy-Item .env.example .env
$env:COURSE_STAGE='midpoint'
npm run build
npm start
```

1행은 앱 이동, 2행은 고정 설치, 3행은 새 환경파일 생성(기존 파일이 있으면 편집), 4행은 기초 기능 모드, 5행은 정적/서버 빌드, 6행은 실행이다. 같은 셸의 COURSE_STAGE를 유지해야 API도 midpoint로 실행된다. 운영은 환경변수로 COURSE_STAGE=midpoint를 넣는다. `/auth`에서 가입하고 로그인한 다음 `/board`에서 등록·수정·댓글·삭제를 확인한다.

### 핵심 구현 전체 코드와 줄별 설명

'''
    for p in ['course/src/lib/basic-api.mjs','course/src/lib/posts.mjs','course/src/pages/board.astro','course/src/pages/auth.astro']:
        midpoint += source_section(p)
    midpoint += '''## ④ 🔗 연동 포인트

### DB·API 연동 구성도

```mermaid
flowchart LR
  A[브라우저 정적 HTML] --> B[폼과 fetch]
  B --> C[Astro API 엔드포인트]
  C --> D[Origin·세션 middleware]
  D --> E[basic-api·검증·작성자 검사]
  E --> F[저장소 계약]
  F --> G[(SQLite records)]
  G --> H[data/meta 또는 error]
  H --> I[textContent 화면 표시]
```

DB 모델은 users(email·nickname·passwordHash), sessions(userId·digest·expiresAt), posts(title·body·tags·authorId·시각), comments(postId·body·authorId·createdAt)다. records의 kind로 모델을 구분한다. 연결 경로와 종류는 환경변수이며 SQL은 바인딩한다. DB를 바꾸는 일은 study11부터다.

목록 응답은 data와 meta, 단건은 data, 오류는 error다. 세션은 쿠키와 Bearer가 같은 digest 저장소를 사용한다. 삭제·로그아웃의 204는 클라이언트에서 JSON으로 읽지 않는다. 다음 단계에서 이 계약을 유지하며 DB를 확장한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 글 작성 401 | 미로그인·쿠키 host 차이 | 같은 host에서 로그인 후 요청 |
| 남의 글 수정 403 | 작성자 권한 검사 | 정상 동작이며 내 계정 글로 시험 |
| 등록 후 목록에 없음 | 필터·페이지 또는 캐시 설정 혼동 | 검색 초기화·page=1·midpoint 모드 확인 |
| 심화 API 404 | COURSE_STAGE=midpoint | 기초 과정의 의도된 동작 |
| 재시작 후 글 없음 | 다른 DB 경로·작업 폴더 | DATABASE_URL과 현재 디렉터리 확인 |

## ⑥ 직접 해보기

1. 서로 다른 두 계정으로 등록·조회·수정·삭제 권한 시나리오를 기록한다.
2. 검색 결과가 없는 페이지·마지막 페이지·존재하지 않는 id의 응답을 확인한다.
3. 서버를 재시작한 뒤 글과 댓글이 유지되는지 확인하고 DB 사본을 만들어 본다.

## ⑦ ☐ 체크리스트

### 1차 배포 체크리스트

- [ ] 정적 랜딩·콘텐츠·게시판·로그인 화면이 열린다.
- [ ] 가입 201·로그인 200·목록/상세 200·등록 201/Location·수정 200·삭제 204를 확인했다.
- [ ] 400·401·403·404·409 오류와 requestId를 확인했다.
- [ ] 비밀번호 해시가 응답에 없고 쿠키는 HttpOnly·SameSite이며 HTTPS에서 Secure다.
- [ ] .env·DB 파일이 Git에 없고 DB 경로는 영속 디스크다.
- [ ] npm test·build·test:http·브라우저 검사를 통과했다.
- [ ] HTTPS 공개 주소·환경변수·DB 경로·헬스체크를 배포 환경에서 확인한다.

### 회고

확인한 점: 정적 HTML과 동적 API를 같은 Astro 앱에 놓고도 DB·인증 경계를 명확하게 나눌 수 있다. 공통 API를 먼저 정하면 폼과 서버가 같은 필드와 상태 코드를 사용한다. 어려웠던 점은 PATCH의 기본값으로 태그가 비는 오류였고, 회귀 테스트로 기존 태그 보존을 확인했다.

남은 제약: JSON payload 저장소는 큰 목록에서 전체 스캔과 N+1 조회가 발생한다. 댓글 삭제와 글 삭제는 단일 트랜잭션이 아니어서 고부하 운영 전에 FK·트랜잭션으로 개선해야 한다. 외부 호스팅 배포는 실제 공개 주소에서 추가 확인한다.

## ⑧ 다음 단계 연결 문장

[study11.md](study11.md)에서 같은 서비스의 API 계약을 유지하며 DB 드라이버·인덱스·ORM 설정을 바꾼다. 최종 모드로 돌아가려면 셸의 COURSE_STAGE를 지우고 다시 빌드·실행한다.
'''
    (ROOT/'studyMidpoint.md').write_text(midpoint,encoding='utf-8')
    final = f'''# studyFinal · Astro 문서 학습 데스크

## ① 목표 한 줄

midpoint 게시판에 DB 교체·외부 서비스·문서 AI·실시간·Docker·자동 배포를 연결해 Astro 하나의 학습 서비스를 완성한다.

### 기능 목록

| 기능 | 구현 위치 | 검증 구분 |
|---|---|---|
| 가입·쿠키/Bearer 세션·글/댓글 CRUD | basic-api/auth/posts | 로컬 HTTP·브라우저 확인 |
| SQLite·PostgreSQL·MariaDB·MongoDB 저장 계약 | store·DB compose·ORM 예제 | SQLite 확인, 외부 3종 실행 미검증 |
| UI·상태·폼 검증 | Pico CSS·Nano Stores·zod | 브라우저 확인 |
| 메일·결제·파일·OAuth | integrations/files | mock·파일 확인, 실제 계정 미검증 |
| 공개 목록 캐시·메일 작업 | cache/jobs/worker | 단위·로컬 작업 확인 |
| 실시간 알림·소켓 예제 | events·socket | 별도 검증 기록 참고 |
| 개인 문서 요약·근거 질문·이력 | documents·ai·questions | mock 스트리밍 확인, 실제 모델 품질 미검증 |
| MCP stdio 도구 검색·호출 | mcp-server/client | 실제 SDK 프로세스 호출 확인 |
| 이미지·CI·자동 배포 훅·백업 | Docker/Actions/backup | 파일 구성, Docker·외부 배포는 환경 필요 |

기준: [Notion Astro]({SOURCE})와 [공통 API v1]({API_SPEC}). AI 학습 연결은 [DocuForge]({DOCU})의 문서 근거 응답과 [SocialForge]({SOCIAL})의 생성·기록 흐름이다. 기존 프로젝트 서버를 연결하지 않고 Astro 내부 기능으로 구현한다.

## ② 📖 이론

완성 서비스는 기능을 많이 붙이는 것에 더해 실패 경계와 검증 범위를 설명할 수 있어야 한다. 화면은 정적 HTML, 개인 데이터는 인증 API, 원본은 DB, 파일은 비공개 저장소, 오래 걸리는 메일은 worker, 모델 출력은 취소 가능한 스트림이다. 각 경계는 연결 부위가 다른 배관처럼 입력·출력·실패 규칙이 정해져야 한다.

운영 배포의 완료와 학습 코드의 완성을 구분한다. 키 없는 mock이 실제 AI 품질·메일 전달·결제를 보장하지 않는다. 기본 설정은 외부 유료 호출을 만들지 않고 학습 흐름을 재현한다. 실제 운영 전에는 외부 DB 연결·제공자 테스트 계정·HTTPS·백업 복구·부하 검증이 추가로 필요하다.

## ③ 🛠️ 실기

### 연동 구성도

```mermaid
flowchart TB
  U[브라우저 정적 HTML·폼·상태] --> A[Astro API·세션·권한·검증]
  A --> B[기본 게시판 API v1]
  B --> R[저장소 계약]
  R --> S[(SQLite 또는 외부 DB)]
  A --> F[비공개 TXT·MD 문서]
  F --> G[발췌 검색·프롬프트]
  G --> H[모델 API 또는 mock]
  H --> N[NDJSON 스트림]
  N --> U
  A --> J[(영속 작업)]
  J --> W[단일 Node worker]
  W --> M[메일 API]
  J --> E[SSE 알림]
  E --> U
  A --> P[Stripe 테스트·GitHub OAuth]
  C[MCP client] --> T[MCP stdio tool]
  T --> G
  CI[GitHub Actions] --> I[GHCR SHA 이미지]
  I --> D[조건부 배포 훅·HTTPS health]
```

### 구현 순서

1. midpoint의 모든 인증·글·댓글 계약과 테스트를 먼저 통과시킨다.
2. study11의 DB_DRIVER/DATABASE_URL을 고르고 test:db를 수행한다. 기존 DB는 백업 후 별도 이관하며 연결만 바꿔 데이터가 이동한다고 가정하지 않는다.
3. study12의 Pico UI·Nano Stores·폼 zod를 연결한다.
4. study13의 TXT·MD 저장/소유권, mock 메일/테스트 checkout, 실제 키를 넣을 수 있는 OAuth·서명 웹훅 경계를 연결한다.
5. study14의 OpenAPI·requestId·오류·페이지 계약을 대조한다.
6. study15의 캐시 무효화·단일 worker·실패 재시도를 연결한다.
7. study16의 이미지·영속 볼륨·백업·CI·배포 훅을 구성한다.
8. study17의 SSE 알림과 소켓 예제를 확인한다.
9. study18의 문서 검색·AI 스트리밍·질문 이력·MCP 도구 호출을 확인한다.
10. 전체 테스트·보안 점검을 수행하고 실제 배포 환경의 미검증 항목을 별도로 닫는다.

```powershell
cd course
Remove-Item Env:COURSE_STAGE -ErrorAction SilentlyContinue
npm ci
npm test
npm run build
npm run test:http
npx playwright install chromium
npx playwright test
npm run mcp:client
npm start
```

1행은 앱으로 이동하고 2행은 midpoint 모드를 해제한다. 3행은 잠금 설치, 4행은 단위·저장소·mock 검사, 5행은 빌드, 6행은 실제 HTTP 계약, 7~8행은 브라우저 흐름, 9행은 MCP SDK 호출, 10행은 서비스 실행이다. `.env`도 COURSE_STAGE=midpoint로 고정돼 있지 않은지 확인한다. 별도 터미널의 npm run worker로 메일 작업을 처리한다.

### 최종 연결 코드 전체와 줄별 설명

기초 구현의 전체 파일은 studyMidpoint, DB와 ORM 전체는 study11, 결제·OAuth·파일 전체는 study13, 모델·화면·MCP 전체는 study18에 있다. 아래 파일은 최종 조립 경계를 생략 없이 보여 준다.

'''
    for p in ['course/src/lib/api.mjs','course/src/pages/api/[...path].js','course/src/lib/jobs.mjs','course/compose.yml','course/.env.example']:
        final += source_section(p)
    final += '''## ④ 🔗 연동 포인트

모든 개인 자원은 locals.user와 authorId로 연결한다. 문서 업로드 후 받은 id가 AI 요청의 documentId가 되고 질문 이력은 documentId·authorId·question·answer·sources를 DB에 저장한다. 다운로드도 같은 소유권 규칙을 따른다. 질문이 빈 문자열이면 요약, 값이 있으면 발췌 검색을 실행한다.

DB 교체 후에도 공통 게시판 API의 경로와 JSON 모양은 유지한다. 파일 저장 위치는 DB 연결과 별개이므로 백업·이관할 때 업로드 파일과 DB를 함께 보존한다. 프로세스 캐시는 공개 목록에만 쓰며 변경 시 지운다. 다중 web 프로세스나 worker 확장 전에 공유 캐시·트랜잭션·원자적 작업 claim을 설계한다.

배포 이미지는 비밀을 포함하지 않는다. 런타임 환경변수와 영속 볼륨으로 DB·외부 API를 연결하고 SITE_URL/CORS_ORIGIN은 공개 HTTPS 주소에 맞춘다. 실제 운영 모드로 전환할 때는 mock 표시와 test 키 제한을 이해하고 업무별 결제 권한·환불 정책을 별도로 마련한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 문서 403 | 소유자 불일치 | 로그인 계정과 문서 authorId 확인 |
| AI 503·502 | 키 없음·upstream 실패 | 서버 env·제공자 로그·timeout 확인 |
| 스트림 중단 | 취소·제공자 네트워크 | 출력 상태를 안내하고 재시도, HTML 실행 금지 |
| 메일 queued 유지 | worker 미실행 | 단일 worker 실행·실패 상태 확인 |
| 외부 DB 연결 실패 | 엔진·포트·자격증명 | test:db부터 성공시킨 뒤 전체 검증 |
| Docker·배포 실행 불가 | 로컬 엔진·호스팅 설정 없음 | 코드 검증과 실제 환경 검증을 구분해 기록 |

## ⑥ 직접 해보기

1. 새로운 DB에 이관한 뒤 사용자·글·댓글·문서·질문 이력의 건수와 관계를 확인한다.
2. 제공자 mock을 timeout·500으로 바꾸고 UI·작업 재시도·서버 로그가 어떻게 바뀌는지 기록한다.
3. 별도 스테이징에서 이미지 배포·HTTPS·백업 복구·이전 SHA 롤백을 끝까지 연습한다.

## ⑦ ☐ 체크리스트

### 최종 배포 체크리스트

- [ ] 단위·HTTP·브라우저·MCP·문서 검사를 통과했다.
- [ ] 공통 v1의 인증·게시글·댓글과 OpenAPI를 대조했다.
- [ ] DB 교체를 실제 대상 서버에서 검증하고 이관·백업·복구 결과를 기록했다.
- [ ] .env·토큰·해시·문서 원문이 Git·브라우저 번들·로그에 노출되지 않는다.
- [ ] 세션 만료·로그아웃·소유권·Origin·XSS·크기 제한을 확인했다.
- [ ] 실제 외부 서비스는 테스트 계정에서 callback·웹훅 서명·멱등성을 확인했다.
- [ ] AI live 품질·근거 표기·비용·timeout·중단을 실제 모델로 평가했다.
- [ ] 비루트 컨테이너·영속 DB/파일 볼륨·단일 worker·health를 확인했다.
- [ ] CI 성공·GHCR SHA 이미지·배포 훅·HTTPS·이전 버전 롤백을 확인했다.
- [ ] 오류율·p95·실패 작업·디스크 용량 알림과 백업 보존 정책을 준비했다.

### 최종 회고

만든 결과: Astro의 정적 HTML·콘텐츠 컬렉션·엔드포인트로 게시판과 개인 문서 도우미를 구성했다. 사용자 입력은 브라우저와 서버에서 검사하고, 저장·외부 호출·스트림·실시간을 구분했다. 학습 문서의 전체 코드는 실제 소스에서 동기화하며 줄별 설명을 붙였다.

검증 중 배운 점: 부분수정에서 기본값이 기존 데이터를 지울 수 있고, 스트림 청크 경계는 문자나 이벤트 경계와 같지 않다. 브라우저에서 안전하게 문자열을 표시하는지까지 확인해야 XSS 방어를 설명할 수 있다. MCP는 실제 SDK 서버/클라이언트를 연결해 도구를 발견하고 호출했다.

한계: 외부 DB 3종·실제 모델·메일·결제·OAuth·호스팅 배포는 환경과 계정이 필요한 별도 검증 항목이다. 현재 저장 모델의 목록 전체 스캔·N+1·비트랜잭션 삭제, 단일 worker·프로세스 캐시는 학습 규모 기준이다. PDF/DOCX/PPTX·OCR·벡터 임베딩·분산 캐시·공개 HTTP MCP·실결제 권한 부여는 확장 과제로 남긴다. 외부 프로젝트와 결합하는 코드는 추가하지 않았다.

## ⑧ 다음 단계 연결 문장

다음에는 새로운 프레임워크를 합치기 전에 이 앱의 실제 DB·제공자·배포 환경 검증을 마무리한다. 원문 요구 반영 위치와 충돌·미검증 항목은 [요구사항 매핑](docs/requirements.md), 실행 증거는 [검증 기록](docs/verification.md)을 기준으로 이어간다.
'''
    (ROOT/'studyFinal.md').write_text(final,encoding='utf-8')

if __name__=='__main__':
    write_lessons()
    write_projects()
