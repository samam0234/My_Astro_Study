# study4. 실습4 — 섬과 client 지시어

[study3.md](study3.md)까지는 페이지가 HTML만 만들었습니다. 여기서 React, Vue, Svelte를 각각 한 컴포넌트씩 붙입니다. 통합은 `demo/`에 설치하고, 컴포넌트 파일은 프레임워크 폴더에만 둡니다.

## 1. 설치한 통합

`demo/`에서 실행한 명령입니다.

```powershell
npx astro add react --yes
npx astro add vue --yes
npx astro add svelte --yes
```

| 패키지 | 버전 |
|---|---|
| `@astrojs/react` | 7.1.x |
| `react`, `react-dom` | 19.3.x |
| `@astrojs/vue` | 7.1.x |
| `vue` | 3.5.x |
| `@astrojs/svelte` | 9.1.x |
| `svelte` | 5.57.x |

Vue를 추가할 때 `tsconfig.json`의 `jsx`가 `react-jsx`에서 `preserve`로 바뀝니다. 세 프레임워크를 같이 쓸 때의 생성 결과라 그대로 둡니다. 컴파일은 각 통합이 담당합니다.

## 2. 섬 파일은 Astro 폴더 밖에 있다

| 파일 | 페이지에서의 지시어 |
|---|---|
| `react/demo/Counter.jsx` | 하나는 지시어 없음, 하나는 `client:load` |
| `svelte/demo/Counter.svelte` | `client:idle` |
| `vue/demo/Counter.vue` | `client:visible` |

`demo/astro.config.mjs`의 `island-react`, `island-vue`, `island-svelte` 별칭으로 페이지가 이 파일을 불러옵니다. 별칭을 `@vue`처럼 패키지 범위와 겹치게 두면 `@vue/runtime-dom`까지 잘못된 폴더로 갑니다. 그래서 별칭 이름에 `@`를 쓰지 않습니다.

섬 파일은 `demo/node_modules`의 부모가 아니라 형제 폴더라, `import 'vue'`를 그 자리에서 못 찾습니다. 설정 안의 `islandResolve` 플러그인이 그 파일의 패키지 import만 `demo/package.json` 기준으로 다시 찾습니다.

## 3. 페이지

`src/pages/islands.astro`의 URL은 `/islands`입니다.

지시어가 없는 `<ReactCounter>`는 버튼 HTML만 남고 `astro-island`가 되지 않습니다. 숫자는 0에서 멈추고, 클릭 핸들러는 번들에 없습니다.

`client:visible`인 Vue 카운터는 긴 여백 아래에 두었습니다. 화면에 들어오기 전에는 하이드레이션을 미룹니다.

## 4. 검증 결과

`npm run build`는 페이지 8개를 만들었습니다. `dist/index.html`에는 `<script`가 없습니다. `dist/islands/index.html`만 섬 스크립트가 있습니다.

빌드된 섬 3개의 `client` 값:

| client | label |
|---|---|
| `load` | React |
| `idle` | Svelte |
| `visible` | Vue |

지시어 없는 버튼 문구 `React HTML만`은 `astro-island` 밖에 있습니다.
