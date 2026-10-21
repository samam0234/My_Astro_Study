---
title: 정적과 요청의 경계
summary: 메모는 빌드 때 만들고, 다시 온 횟수만 요청마다 센다.
minutes: 10
---

`/memos`는 정적 HTML입니다. `/visit`만 `prerender = false`이고 HttpOnly 쿠키 `memo_visits`를 씁니다.

방명록은 이 사이트에 없습니다. demo에서 이미 확인했으므로, 여기서는 같은 경계를 더 작은 화면으로 다시 씁니다.
