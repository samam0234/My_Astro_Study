---
title: 파일이 주소다
description: src/pages 아래 경로가 URL이고, 글 파일은 콘텐츠 컬렉션이 모읍니다.
pubDate: 2026-10-19
---

study2에서는 같은 주소를 `src/data/notes.js` 배열로 만들었습니다. 지금은 그 배열을 지우고, 이 폴더의 파일이 목록의 출처입니다.

글이 늘어도 페이지 파일을 추가하지 않습니다. `[slug].astro` 하나가 `getStaticPaths`로 주소를 만듭니다.
