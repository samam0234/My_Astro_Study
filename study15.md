# study15 · 성능·캐시

## ① 목표 한 줄

측정 후 짧은 캐시와 영속 배경 작업으로 요청 비용을 나눈다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

성능 최적화는 먼저 시간을 재고 병목을 찾는 일이다. 정적 콘텐츠는 빌드 시 계산하고 공개 게시글 목록은 프로세스 내부 TTL 캐시에 잠깐 보관한다. 개인 정보 응답과 인증 응답은 HTTP no-store다. 캐시된 객체를 복사해 반환하면 호출자가 값을 바꿔 원본 캐시를 손상시키지 않는다.

캐시는 잠시 보는 복사본, DB는 원본이다. 글·댓글을 변경하면 관련 캐시를 지운다. 현재 캐시는 단일 web 프로세스 기준이며 다중 프로세스에서는 Redis 같은 공유 캐시와 공통 무효화가 필요하다. 최대 100개 키와 2초 TTL을 둔다.

메일은 요청에서 실제 발송을 기다리지 않고 DB job을 등록해 worker가 처리한다. 실패는 지수 간격으로 3회까지 재시도한다. 작업 id를 제공자 idempotency key로 써 재전송 중복을 줄인다. 현재 worker는 1개만 실행한다. 여러 worker에는 원자적 claim·lease·dead letter 정책이 필요하다.

## ③ 🛠️ 실기

터미널 두 개를 사용한다. 첫 번째는 npm start, 두 번째는 npm run worker를 실행한다. `/services`에서 메일 작업을 등록하고 SSE 연결 후 done을 확인한다. 한 작업만 처리하려면 `npm run worker -- --once`다. 서버가 실행 중일 때 `npm run measure`로 20회 요청의 중앙값과 p95를 측정한다. 이는 로컬 TTFB 유사 HTTP 총시간이며 실제 사용자 Core Web Vitals를 대신하지 않는다. 브라우저 Performance·Network에서도 번들 크기와 긴 작업을 확인한다.

### `course/src/lib/cache.mjs` 전체 코드

[cache.mjs](course/src/lib/cache.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
export function ttlCache(ttl = 2000, max = 100) {
  const entries = new Map();
  return {
    async get(key, load) {
      const cached = entries.get(key);
      if (cached && cached.expires > Date.now()) return structuredClone(cached.value);
      const value = await load();
      if (entries.size >= max) entries.delete(entries.keys().next().value);
      entries.set(key, { value: structuredClone(value), expires: Date.now() + ttl });
      return value;
    },
    clear() { entries.clear(); },
  };
}
export const postCache = ttlCache();
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 재사용 함수 `ttlCache`를 정의한다. |
| 2 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const entries`. |
| 3 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 4 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `async get(key, load) {`. |
| 5 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const cached`. |
| 6 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 7 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const value`. |
| 8 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 9 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `entries.set(key, { value: structuredClone(value), expires: Date.now() + ttl });`. |
| 10 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 11 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 12 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `clear() { entries.clear(); },`. |
| 13 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 14 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 15 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `export const postCache`. |

### `course/src/lib/jobs.mjs` 전체 코드

[jobs.mjs](course/src/lib/jobs.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { sendMail } from './integrations.mjs';

export async function enqueueMail(store, user) {
  return store.create('jobs', { type: 'mail', userId: user.id, status: 'queued', attempts: 0, nextAt: 0, createdAt: new Date().toISOString() });
}
export async function workOnce(store, deliver = sendMail) {
  // 단일 worker 전용. 다중 worker는 원자적 claim + lease가 필요하다.
  const job = (await store.list('jobs')).find(j => j.status === 'queued' && j.nextAt <= Date.now());
  if (!job) return false;
  const next = { ...job, attempts: job.attempts + 1 };
  try {
    await deliver(await store.get('users', job.userId), process.env, fetch, `job-${job.id}`);
    Object.assign(next, { status: 'done', finishedAt: new Date().toISOString() });
  } catch {
    Object.assign(next, { status: next.attempts >= 3 ? 'failed' : 'queued', nextAt: Date.now() + 1000 * 2 ** next.attempts });
  }
  await store.replace('jobs', job.id, next); return true;
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'./integrations.mjs'`의 기능을 이 파일에서 사용한다. |
| 2 | 코드 구간을 나누는 빈 줄이다. |
| 3 | 비동기 함수 `enqueueMail`의 입력과 처리 범위를 정의한다. |
| 4 | 저장소 계약으로 새 레코드를 생성하며 생성 id를 받는다. |
| 5 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 6 | 비동기 함수 `workOnce`의 입력과 처리 범위를 정의한다. |
| 7 | 단일 worker 전용. 다중 worker는 원자적 claim + lease가 필요하다. |
| 8 | 저장소에서 해당 종류의 레코드를 읽어 필터·검증·응답에 사용한다. |
| 9 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 10 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const next`. |
| 11 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `try {`. |
| 12 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 13 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `Object.assign(next, { status: 'done', finishedAt: new Date().toISOString() });`. |
| 14 | 실패 경로를 받아 사용자 오류 또는 내부 오류로 처리한다. |
| 15 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `Object.assign(next, { status: next.attempts >= 3 ? 'failed' : 'queued', nextAt: Date.now() + 1000 * 2 ** next.`. |
| 16 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 17 | 검증한 변경 값을 지정 레코드에 저장한다. |
| 18 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/scripts/worker.mjs` 전체 코드

[worker.mjs](course/scripts/worker.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { getStore } from '../src/lib/store.mjs';
import { workOnce } from '../src/lib/jobs.mjs';
const store = await getStore();
let stopped = false;
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => { stopped = true; });
try {
  do {
    const worked = await workOnce(store);
    if (process.argv.includes('--once')) break;
    if (!worked) await new Promise(resolve => setTimeout(resolve, 1000));
  } while (!stopped);
} finally { await store.close(); }
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'../src/lib/store.mjs'`의 기능을 이 파일에서 사용한다. |
| 2 | `'../src/lib/jobs.mjs'`의 기능을 이 파일에서 사용한다. |
| 3 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const store`. |
| 4 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let stopped`. |
| 5 | 목록 또는 스트림의 남은 항목을 순서대로 처리한다. |
| 6 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `try {`. |
| 7 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `do {`. |
| 8 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const worked`. |
| 9 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 10 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 11 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `} while (!stopped);`. |
| 12 | 성공·실패에 관계없이 연결/잠금 등 정리 작업을 실행한다. |

### `course/scripts/measure.mjs` 전체 코드

[measure.mjs](course/scripts/measure.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { performance } from 'node:perf_hooks';
const base = process.env.API_BASE_URL || 'http://127.0.0.1:4323';
for (const path of ['/', '/api/posts']) {
  const samples = [];
  for (let i = 0; i < 20; i++) {
    const started = performance.now(), response = await fetch(base + path);
    await response.text(); if (!response.ok) throw new Error(`HTTP ${response.status}`);
    samples.push(performance.now() - started);
  }
  samples.sort((a, b) => a - b);
  console.log(JSON.stringify({ path, samples: 20, medianMs: samples[10], p95Ms: samples[18] }));
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'node:perf_hooks'`의 기능을 이 파일에서 사용한다. |
| 2 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 3 | 목록 또는 스트림의 남은 항목을 순서대로 처리한다. |
| 4 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const samples`. |
| 5 | 목록 또는 스트림의 남은 항목을 순서대로 처리한다. |
| 6 | HTTP 요청을 보내 응답을 기다린다. 주입된 fetcher는 테스트에서 대체할 수 있다. |
| 7 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await response.text(); if (!response.ok) throw new Error(HTTP ${response.status});`. |
| 8 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `samples.push(performance.now() - started);`. |
| 9 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 10 | 정해진 비교 규칙에 따라 결과 순서를 맞춘다. |
| 11 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 12 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

## ④ 🔗 연동 포인트

HTTP POST /api/mail → jobs 저장 → 별도 Node worker → 외부 메일 응답 → SSE 알림으로 연결된다. 다음 단계 CI는 이 경계를 테스트하고 이미지로 묶는다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 변경 글이 이전 값 | 캐시 무효화 누락 | 글·댓글 변경 후 clear |
| 메일 중복 | 여러 worker 또는 비멱등 전송 | 단일 worker·제공자 key |
| 작업 계속 queued | worker 미실행 | worker 프로세스 로그 확인 |

## ⑥ 직접 해보기

1. npm run measure로 홈·API의 median/p95를 기록한다.
2. 목록 조회 직후 글을 바꿔 캐시가 무효화되는지 확인한다.
3. 실패하는 가짜 메일 전송으로 세 번째 실패 뒤 failed가 되는지 확인한다.

## ⑦ ☐ 체크리스트

- [ ] 측정값 없이 최적화 효과를 단정하지 않는다.
- [ ] 캐시 TTL·용량·무효화·개인정보 경계를 확인했다.
- [ ] 비동기 작업·재시도·중복 방지·단일 worker 제약을 설명했다.

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study16.md](study16.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
