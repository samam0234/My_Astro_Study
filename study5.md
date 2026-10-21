# study5. 실습5 — 콘텐츠 컬렉션과 MDX

[study2.md](study2.md)의 글 목록은 `src/data/notes.js` 배열이었습니다. 그 파일을 지우고, 같은 URL을 콘텐츠 컬렉션으로 바꿉니다. Notion 예제인 **정적 랜딩 + 게시판 목록**의 목록이 여기입니다. 랜딩은 `/`, 목록은 `/posts`입니다.

## 1. 컬렉션 정의

`src/content.config.ts`입니다.

```ts
const posts = defineCollection({
  loader: glob({ base: './src/content/posts', pattern: '**/*.{md,mdx}' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
  }),
});
```

| 파일 | id | 형식 |
|---|---|---|
| `static-html.md` | `static-html` | Markdown |
| `file-is-url.md` | `file-is-url` | Markdown |
| `compare.mdx` | `compare` | MDX |

스키마에 없는 앞부분 키를 넣거나 필수 키를 빼면 빌드가 실패합니다. Rails 모델의 검증에 가깝고, 테이블은 아닙니다.

## 2. 목록과 본문

`src/pages/posts/index.astro`는 `getCollection('posts')` 후 `pubDate` 내림차순입니다.

`src/pages/posts/[slug].astro`는 컬렉션으로 `getStaticPaths`를 만들고, `render(post)`가 돌려준 `<Content />`로 본문을 찍습니다. 글이 늘어도 이 페이지 파일은 추가하지 않습니다.

MDX를 위해 `@astrojs/mdx` 8.1을 `astro.config.mjs` 통합에 넣었습니다. `compare.mdx`는 본문에서 `Callout.astro`를 import합니다. 그 컴포넌트도 빌드 때 HTML로 합쳐지고, 섬이 아닙니다.

## 3. 검증 결과

`npm run build`가 콘텐츠를 동기화한 뒤 페이지 9개를 만들었습니다. 글 주소는 다음 세 개입니다.

- `/posts/compare`
- `/posts/file-is-url`
- `/posts/static-html`

`dist/posts/compare/index.html` 본문에 `이 문단까지 HTML입니다`와 `class="callout"`이 있습니다. 홈 `dist/index.html`에는 여전히 `<script`가 없습니다.
