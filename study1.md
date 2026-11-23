# study1 · Hello World와 기본 문법

## ① 목표 한 줄

frontmatter와 템플릿 표현식으로 첫 정적 화면을 만든다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

`.astro`의 `---` 사이 JavaScript는 서버 또는 빌드에서 실행된다. 아래 HTML의 `{title}`은 그 값을 출력한다. 배열은 `map()`으로 반복하고, 조건은 `조건 && <태그>` 또는 삼항식으로 표현한다. `class` 속성은 HTML과 같이 쓴다. 변수는 브라우저 반응형 상태가 아니므로 클릭으로 값을 바꿀 때에는 별도 `<script>`가 필요하다.

템플릿은 편지 양식, frontmatter는 편지에 넣을 주소와 문구다. 값의 계산과 HTML의 표시 위치를 구분하면 서버 비밀값을 템플릿에 실수로 출력하는 일도 줄어든다. 기본 출력은 HTML이며 공통 CSS는 자바스크립트 상태 관리와 별개다.

## ③ 🛠️ 실기

`course/src/pages/index.astro` 전체를 아래 코드와 맞춘다. `npm run dev`로 홈을 연 뒤 제목을 바꿔 저장한다. 개발 서버에서 보이는 Vite 도구 스크립트와 배포 번들을 혼동하지 않는다. `npm run build` 후 `dist/client/index.html`을 열어 출력 문구를 찾는다. 원본 템플릿에 있는 표현식은 빌드 결과에서 실제 문자열로 바뀐다.

### `course/src/pages/index.astro` 전체 코드

[index.astro](course/src/pages/index.astro)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```astro
---
import Desk from '../layouts/Desk.astro';
const title = import.meta.env.PUBLIC_SITE_NAME || 'Astro 학습 데스크';
const topics = ['정적 HTML', '컴포넌트와 데이터', '게시판 API', '문서 요약'];
---
<Desk title={title}>
  <h1>{title}</h1>
  <p>정적 랜딩 페이지에서 시작해 로그인·게시판·문서 도우미로 이어집니다.</p>
  <ul>{topics.map((topic, index) => <li>{index + 1}. {topic}</li>)}</ul>
  <p><a role="button" href="/board">게시판 열기</a></p>
</Desk>
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 2 | `'../layouts/Desk.astro'`의 기능을 이 파일에서 사용한다. |
| 3 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 4 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const topics`. |
| 5 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 6 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 7 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 8 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 9 | 목록의 각 항목을 화면 또는 응답에 필요한 모양으로 변환한다. |
| 10 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 11 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |

## ④ 🔗 연동 포인트

개발 서버의 파일 감시가 저장한 템플릿을 반영한다. 브라우저 개발자도구 Network에서 Document 응답, Elements에서 결과 DOM, Console에서 오류를 확인한다. 다음 단계에서 반복되는 화면을 컴포넌트로 분리한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 화면이 안 바뀜 | 빌드 서버만 실행 | 개발 중 dev 사용, 배포는 재빌드 |
| 표현식 문법 오류 | 중괄호/태그 닫기 누락 | 터미널의 파일·줄 위치 확인 |

## ⑥ 직접 해보기

1. 홈 제목과 배열 항목을 바꿔 자동 새로고침을 확인한다.
2. 배열이 비었을 때 안내 문구가 보이는 조건부 출력을 만든다.

## ⑦ ☐ 체크리스트

- [ ] frontmatter와 HTML을 구별했다.
- [ ] `{표현식}`과 `map()`을 사용했다.
- [ ] 개발자도구와 개발 서버 변경 반영을 확인했다.

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study2.md](study2.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
