# study9. 고급 기술 구현 4 — 이름, 이미지, 화면 전환

[study8.md](study8.md)까지 페이지 제목만 `<title>`에 있었습니다. 여기서 설명 문구, 환경 변수, 빌드가 처리하는 이미지, 페이지 이동을 넣습니다.

## 1. 환경 변수

`demo/.env.example`입니다.

```
PUBLIC_SITE_NAME=Astro 실습
```

`PUBLIC_`로 시작하는 값만 클라이언트 번들에 들어갈 수 있습니다. 비밀키는 이 접두사를 붙이지 않습니다. 로컬 파일 `.env`는 Git에 넣지 않습니다.

헤더와 홈은 이렇게 읽습니다.

```js
const siteName = import.meta.env.PUBLIC_SITE_NAME || 'Astro 실습';
```

검증용 `.env`에는 `PUBLIC_SITE_NAME=별빛 실습`을 넣었습니다. 빌드된 `dist/client/index.html`의 헤더와 본문에 `별빛 실습`이 있습니다. 변수가 없으면 화면은 `Astro 실습`입니다. 정적 페이지는 **빌드 시점의 값**이 HTML에 박힙니다. 서버를 다시 시작해도, 다시 빌드하기 전에는 이름이 안 바뀝니다.

## 2. 이미지

`src/assets/mark.svg`를 홈에서 컴포넌트처럼 불러 씁니다. `public/favicon.svg`와 다릅니다. `public` 파일은 주소 그대로이고, `src/assets` 파일은 빌드가 해시를 붙입니다. 결과 파일은 `dist/client/_astro/mark.*.svg`입니다.

## 3. 문서 정보와 ClientRouter

`Base.astro`가 `description` prop으로 `<meta name="description">`을 넣습니다. 홈의 설명은 `정적 페이지가 기본인 Astro 실습입니다.`

`<ClientRouter />`는 링크 클릭을 가로채 다음 HTML을 갈아끼웁니다. 헤더에는 `transition:persist`를 붙여 이동해도 같은 헤더 DOM을 유지합니다.

이 라우터 스크립트는 **모든 페이지**에 하나 붙습니다. study1에서 `dist/index.html`에 `<script`가 없다고 적은 것은 그때 기준입니다. 지금은 홈에도 스크립트가 1개 있습니다. React, Vue, Svelte 파일은 여전히 `/islands`에만 있습니다. 화면 전환이 필요 없는 사이트라면 `ClientRouter`를 빼는 쪽이 Astro의 기본 취지에 맞습니다.

## 4. 검증 결과

`npm run build` 후 `dist/client/index.html` 기준입니다.

- `별빛 실습` 포함
- meta description 문구 포함
- svg 참조 포함
- `<script` 1개, `ClientRouter` 포함

어댑터를 넣은 뒤부터 정적 HTML은 `dist/` 바로 아래가 아니라 `dist/client/`에 있습니다.
