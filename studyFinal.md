# studyFinal. 메모 데스크

[study10.md](study10.md)까지의 `demo/`는 진도를 그대로 보여주는 실습 앱입니다. 메뉴에 부품, 섬, 피드, 방명록이 남아 있습니다. 이 문서는 그 부품을 **다른 주소와 다른 폴더**로 다시 조립한 작은 사이트입니다.

Notion 예제인 정적 랜딩 + 목록이 여기의 홈과 `/memos`입니다.

## 1. demo와 다른 점

| | demo | project |
|---|---|---|
| 패키지 이름 | `demo` | `memo-desk` |
| 주소 | http://127.0.0.1:4321 | http://127.0.0.1:4322 |
| 레이아웃 | `src/layouts/Base.astro` | `src/ui/Shell.astro` |
| 콘텐츠 | `posts` (Markdown + MDX) | `memos` (Markdown 3편) |
| 동적 페이지 | 방명록, `/now` | `/visit` 방문 횟수만 |
| 화면 전환 | `ClientRouter` | 없음. 테마 섬만 공통 |
| 섬 폴더 | `react/demo` 등 | `react/project` 등 |

방명록과 MDX, 실습용 메뉴는 넣지 않았습니다. 이미 demo에서 확인한 것을 한 번 더 복사하지 않기 위해서입니다.

## 2. 페이지

| 파일 | URL | 렌더 |
|---|---|---|
| `src/pages/index.astro` | `/` | 정적. 편수와 총 시간 |
| `src/pages/memos/index.astro` | `/memos` | 정적 HTML + React 검색 섬 |
| `src/pages/memos/[id].astro` | `/memos/routing` 등 | 정적 본문 + Vue 고정 버튼 |
| `src/pages/about.astro` | `/about` | 정적 |
| `src/pages/visit.astro` | `/visit` | 요청마다. 쿠키 `memo_visits` |
| `src/pages/404.astro` | 없는 주소 | 404 |

메모 세 편은 `src/content/memos`입니다. 제목 가나다순입니다.

| id | 분 |
|---|---|
| `boundary` | 10 |
| `islands` | 20 |
| `routing` | 15 |

홈은 이 합을 45분으로 찍습니다.

## 3. 세 섬은 하는 일이 다르다

| 폴더 | 컴포넌트 | 하는 일 |
|---|---|---|
| `react/project` | `MemoSearch.jsx` | 제목·요약 필터. 서버 저장 없음 |
| `vue/project` | `PinButton.vue` | 상세에서 고정 문구만 토글 |
| `svelte/project` | `ThemeToggle.svelte` | `data-theme`로 밝기 전환 |

테마 버튼은 셸에 있으므로 모든 페이지에 Svelte 런타임이 조금 실립니다. 검색 React와 고정 Vue는 그 페이지에만 있습니다. demo처럼 한 페이지에 세 카운터를 모아 두지 않습니다.

## 4. 실행

```powershell
cd project
npm install
npm run dev
```

프로덕션:

```powershell
npm run build
npm start
```

`HOST=127.0.0.1`, `PORT=4322`로 확인했습니다. Docker 파일은 demo와 같고 포트만 4322입니다. Docker 엔진은 꺼져 있어 이미지는 만들지 않았습니다.

## 5. 검증 결과

`npm run build`의 정적 라우트는 `/`, `/about`, `/memos`, `/memos/boundary`, `/memos/islands`, `/memos/routing`, `/404.html`입니다. `/visit`는 목록에 없습니다.

`npm start` 후:

| 요청 | 상태 | 확인 |
|---|---|---|
| `GET /` | 200 | 테마 버튼 `어둡게`, 총 시간 문구 |
| `GET /memos` | 200 | 검색 입력 `메모 검색`, React 섬 |
| `GET /memos/islands` | 200 | Vue 문구 `이 메모 고정` |
| `GET /about` | 200 | |
| `GET /missing` | 404 | 없는 페이지 셸 |
| `GET /visit` 첫 번 | 200 | `memo_visits=1`, 화면 1 |
| 같은 쿠키로 다시 | 200 | `memo_visits=2`, 화면 2 |

검색 입력과 테마 버튼, 고정 버튼의 클릭은 브라우저에서 직접 누르지 못했습니다. HTML에 섬이 있고 초기 문구가 서버 HTML에 있는 것까지 확인했습니다.
