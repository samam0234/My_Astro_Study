# Astro 학습 앱

루트 [README](../README.md)와 [study0](../study0.md)부터 진행합니다.

```powershell
npm ci
Copy-Item .env.example .env
npm run dev
```

주소는 http://127.0.0.1:4323, 기본 DB는 SQLite, 외부 서비스와 AI는 mock입니다. 가입·로그인 후 게시판과 문서 AI를 사용합니다. 별도 터미널에서 `npm run worker`로 작업을 처리합니다.

빌드/실행은 `npm run build`, `npm start`, 검증은 `npm test`, `npm run test:http`, `npx playwright test`, `npm run mcp:client`입니다.

DB 3종·ORM은 [study11](../study11.md), 외부 서비스는 [study13](../study13.md), Docker·자동 배포·백업은 [study16](../study16.md), AI·MCP는 [study18](../study18.md)에 있습니다.
