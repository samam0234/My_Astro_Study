# study17 · 실시간·확장

## ① 목표 한 줄

SSE 알림·인증된 WebSocket과 비공개 파일 다운로드를 연결한다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

SSE는 서버가 브라우저에 알림을 보내는 단방향 연결이고 EventSource가 재연결한다. WebSocket은 서버와 브라우저가 양방향 메시지를 주고받는 연결이다. 알림판과 무전기의 차이로 생각하면 된다. HTTP 응답 객체를 쓰는 Astro Node 앱에는 SSE를 그대로 붙일 수 있다.

WebSocket 예제는 Node http upgrade와 ws를 사용하는 별도 로컬 프로세스다. 새로운 웹 프레임워크를 추가하지 않는다. Astro가 발급한 같은 호스트의 HttpOnly 쿠키를 공유하고 Origin·세션을 검사한다. `/events` 경로만 허용하며 4096바이트 최대 payload와 60초 재인증 경계를 둔다.

SSE는 사용자 소유 작업만 내보내고 연결 종료·abort 때 타이머를 해제한다. 파일은 공개 URL로 노출하지 않고 소유권 검사 후 attachment로 내려준다. 대용량 바이너리 파일은 이 학습의 UTF-8 텍스트 저장과 다르므로 객체 저장소·스트리밍 업로드·백신 검사 등을 별도 설계해야 한다.

## ③ 🛠️ 실기

첫 터미널에서 npm start, 두 번째에서 `node --env-file-if-exists=.env scripts/socket.mjs`를 실행한다. 같은 호스트 `http://127.0.0.1:4323`에서 로그인한 다음 Console에서 실행한다.

```javascript
const socket = new WebSocket('ws://127.0.0.1:4324/events');
socket.onmessage = event => console.log(JSON.parse(event.data));
socket.onopen = () => socket.send('ping');
```

1행은 upgrade 연결, 2행은 수신 표시, 3행은 연결 후 메시지 전송이다. 쿠키는 포트로 분리되지 않지만 호스트가 localhost와 127.0.0.1로 다르면 공유되지 않는다. 운영은 같은 공개 origin의 `/socket`을 upgrade 프록시하고 wss를 사용해야 한다. 컨테이너 기본 compose는 SSE만 실행하며 socket 예제는 자동 노출하지 않는다.

### `course/scripts/socket.mjs` 전체 코드

[socket.mjs](course/scripts/socket.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { createServer } from 'node:http';
import { WebSocketServer } from 'ws';
import { getStore } from '../src/lib/store.mjs';
import { authenticate } from '../src/lib/auth.mjs';
import { settings } from '../src/lib/config.mjs';

const store = await getStore(), site = settings().site;
const server = createServer((_req, res) => { res.writeHead(404); res.end(); });
const sockets = new WebSocketServer({ noServer: true, maxPayload: 4096 });
server.on('upgrade', async (request, socket, head) => {
  try {
    if (request.url !== '/events' || request.headers.origin !== new URL(site).origin) throw new Error('origin/path');
    const token = request.headers.cookie?.split(';').map(c => c.trim()).find(c => c.startsWith('desk_session='))?.slice(13);
    const user = await authenticate(store, token); if (!user) throw new Error('auth');
    sockets.handleUpgrade(request, socket, head, ws => {
      ws.send(JSON.stringify({ type: 'ready', nickname: user.nickname }));
      ws.on('message', async () => {
        try {
          if (!(await authenticate(store, token))) { ws.close(1008, 'session expired'); return; }
          ws.send(JSON.stringify({ type: 'pong', at: new Date().toISOString() }));
        } catch { ws.close(1011, 'server error'); }
      });
      const expiry = setTimeout(() => ws.close(1008, 'reauthenticate'), 60000);
      ws.on('close', () => clearTimeout(expiry));
    });
  } catch { socket.write('HTTP/1.1 401 Unauthorized\r\nConnection: close\r\n\r\n'); socket.destroy(); }
});
server.listen(Number(process.env.WS_PORT || 4324), '127.0.0.1');
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'node:http'`의 기능을 이 파일에서 사용한다. |
| 2 | `'ws'`의 기능을 이 파일에서 사용한다. |
| 3 | `'../src/lib/store.mjs'`의 기능을 이 파일에서 사용한다. |
| 4 | `'../src/lib/auth.mjs'`의 기능을 이 파일에서 사용한다. |
| 5 | `'../src/lib/config.mjs'`의 기능을 이 파일에서 사용한다. |
| 6 | 코드 구간을 나누는 빈 줄이다. |
| 7 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const store`. |
| 8 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const server`. |
| 9 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const sockets`. |
| 10 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `server.on('upgrade', async (request, socket, head) => {`. |
| 11 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `try {`. |
| 12 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 13 | 목록의 각 항목을 화면 또는 응답에 필요한 모양으로 변환한다. |
| 14 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const user`. |
| 15 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `sockets.handleUpgrade(request, socket, head, ws => {`. |
| 16 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 17 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `ws.on('message', async () => {`. |
| 18 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `try {`. |
| 19 | 사용이 끝난 스트림·소켓·DB 자원을 종료하거나 잠금을 해제한다. |
| 20 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 21 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 22 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 23 | 사용이 끝난 스트림·소켓·DB 자원을 종료하거나 잠금을 해제한다. |
| 24 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `ws.on('close', () => clearTimeout(expiry));`. |
| 25 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 26 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 27 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 28 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |

### `course/src/lib/files.mjs` 전체 코드

[files.mjs](course/src/lib/files.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { randomUUID } from 'node:crypto';
import { join } from 'node:path';
import { fail } from './http.mjs';

export async function saveDocument(store, user, input, directory = './data/uploads') {
  if (typeof input.text !== 'string' || !input.text.trim() || Buffer.byteLength(input.text, 'utf8') > 100000) fail(400, 'VALIDATION_ERROR', 'UTF-8 텍스트 1~100000바이트가 필요합니다.');
  const name = String(input.name || 'document.txt').replace(/[\r\n"\\/]/g, '_').slice(0, 100);
  if (!/\.(txt|md)$/i.test(name)) fail(400, 'VALIDATION_ERROR', 'TXT 또는 MD만 지원합니다.');
  const key = `${randomUUID()}.txt`;
  await mkdir(directory, { recursive: true });
  await writeFile(join(directory, key), input.text, { flag: 'wx', encoding: 'utf8', mode: 0o600 });
  return store.create('documents', { authorId: user.id, name, key, text: input.text, createdAt: new Date().toISOString() });
}
export async function downloadDocument(document, directory = './data/uploads') {
  return new Response(await readFile(join(directory, document.key)), { headers: {
    'Content-Type': 'text/plain; charset=utf-8', 'Content-Disposition': `attachment; filename*=UTF-8''${encodeURIComponent(document.name)}`, 'X-Content-Type-Options': 'nosniff',
  } });
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'node:fs/promises'`의 기능을 이 파일에서 사용한다. |
| 2 | `'node:crypto'`의 기능을 이 파일에서 사용한다. |
| 3 | `'node:path'`의 기능을 이 파일에서 사용한다. |
| 4 | `'./http.mjs'`의 기능을 이 파일에서 사용한다. |
| 5 | 코드 구간을 나누는 빈 줄이다. |
| 6 | 비동기 함수 `saveDocument`의 입력과 처리 범위를 정의한다. |
| 7 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 8 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const name`. |
| 9 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 10 | 예측하기 어려운 식별자·토큰·salt를 생성한다. |
| 11 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await mkdir(directory, { recursive: true });`. |
| 12 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await writeFile(join(directory, key), input.text, { flag: 'wx', encoding: 'utf8', mode: 0o600 });`. |
| 13 | 저장소 계약으로 새 레코드를 생성하며 생성 id를 받는다. |
| 14 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 15 | 비동기 함수 `downloadDocument`의 입력과 처리 범위를 정의한다. |
| 16 | 응답 본문·상태·헤더 또는 스트림을 담은 HTTP Response를 만든다. |
| 17 | 이 설정 키에 대응하는 값·명령·의존성을 선언한다. |
| 18 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `} });`. |
| 19 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/src/pages/services.astro` 전체 코드

[services.astro](course/src/pages/services.astro)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```astro
---
import Desk from '../layouts/Desk.astro';
---
<Desk title="외부 서비스">
  <h1>외부 서비스 연습</h1><p>기본 설정은 mock입니다. 실제 결제나 메일 발송은 발생하지 않습니다.</p>
  <p id="message" role="status" aria-live="polite"></p>
  <button id="mail" type="button">내 이메일로 알림 작업 등록</button>
  <button id="checkout" type="button">테스트 결제 세션 만들기</button>
  <button id="events" type="button">작업 알림 연결</button><pre id="jobs"></pre>
</Desk>
<script>
  import { api, show } from '../client/api.mjs';
  for (const [id, path] of [['mail', '/api/mail'], ['checkout', '/api/checkout']]) {
    const button = document.getElementById(id) as HTMLButtonElement;
    button.onclick = async () => { button.disabled = true; try { const { data } = await api(path, { method: 'POST', body: JSON.stringify({ key: crypto.randomUUID() }) });
      show(JSON.stringify(data)); if (data.url) { const a = document.createElement('a'); a.textContent = '테스트 결제 화면 열기'; a.href = data.url; document.querySelector('#message')!.append(a); }
    } catch (e) { show(e); } finally { button.disabled = false; } };
  }
  let events: EventSource | undefined;
  document.getElementById('events')!.onclick = () => {
    events?.close(); events = new EventSource('/api/events');
    events.addEventListener('jobs', event => { document.getElementById('jobs')!.textContent = (event as MessageEvent).data; });
    events.onerror = () => show('알림 연결을 확인하세요. 로그인 만료 시 다시 로그인하세요.');
  };
  window.addEventListener('pagehide', () => events?.close());
</script>
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 2 | `'../layouts/Desk.astro'`의 기능을 이 파일에서 사용한다. |
| 3 | 서버 frontmatter와 HTML 템플릿의 경계를 표시한다. |
| 4 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 5 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 6 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 7 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 8 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 9 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 10 | 이 HTML·컴포넌트·템플릿 표현식을 현재 위치에 출력한다. |
| 11 | 브라우저에서 실행할 이벤트·DOM 코드의 경계를 정한다. |
| 12 | `'../client/api.mjs'`의 기능을 이 파일에서 사용한다. |
| 13 | 목록 또는 스트림의 남은 항목을 순서대로 처리한다. |
| 14 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const button`. |
| 15 | 브라우저 이벤트가 발생했을 때 실행할 함수를 연결한다. |
| 16 | 문자열을 HTML로 실행하지 않고 텍스트로 표시해 XSS 표면을 줄인다. |
| 17 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 18 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 19 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let events: EventSource &#124; undefined;`. |
| 20 | 브라우저 이벤트가 발생했을 때 실행할 함수를 연결한다. |
| 21 | 사용이 끝난 스트림·소켓·DB 자원을 종료하거나 잠금을 해제한다. |
| 22 | 문자열을 HTML로 실행하지 않고 텍스트로 표시해 XSS 표면을 줄인다. |
| 23 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `events.onerror = () => show('알림 연결을 확인하세요. 로그인 만료 시 다시 로그인하세요.');`. |
| 24 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 25 | 브라우저 이벤트가 발생했을 때 실행할 함수를 연결한다. |
| 26 | 브라우저에서 실행할 이벤트·DOM 코드의 경계를 정한다. |

## ④ 🔗 연동 포인트

job 상태→SSE→services 화면, 로그인 쿠키→WebSocket upgrade→ready/pong으로 연결된다. 다음 단계 AI 스트리밍도 연결 취소·청크 경계·출력 이스케이프를 재사용한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| WebSocket 401 | 쿠키·Origin·세션 없음 | 같은 host에서 로그인 후 연결 |
| SSE가 몰려서 출력 | 프록시 버퍼링 | SSE 경로 버퍼링 끄기 |
| 종료 후 타이머 남음 | cancel 처리 누락 | abort/cancel에서 clearInterval |

## ⑥ 직접 해보기

1. services에서 알림을 켜고 worker가 queued를 done으로 바꾸는지 확인한다.
2. 로그인 후 WebSocket ready/pong과 로그아웃 후 연결 거절을 확인한다.
3. 다른 계정의 문서 다운로드가 403인지 확인한다.

## ⑦ ☐ 체크리스트

- [ ] SSE 단방향·WebSocket 양방향을 구분했다.
- [ ] Origin·세션·메시지 크기·연결 종료를 처리했다.
- [ ] 파일 다운로드에도 소유권·nosniff·attachment를 적용했다.

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study18.md](study18.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
