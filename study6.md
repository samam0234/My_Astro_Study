# study6 · DB·API 연동

## ① 목표 한 줄

SQLite 저장소로 공통 API v1 게시글 CRUD를 만든다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

API는 화면과 저장소 사이의 약속이다. DB는 메모장이 아니라 프로세스가 재시작되어도 남는 원본이다. 이번 과정은 Node 내장 SQLite의 파일 DB를 사용한다. `records` 테이블은 `id`, `kind`, `payload`, `unique_key`로 구성하고 users·posts·comments 등을 kind로 구분한다. payload는 JSON 문자열이며 대규모 서비스의 정규화 스키마를 대신하는 학습용 저장 모델이다.

저장소 계약은 `create/list/get/replace/remove/close` 여섯 함수다. SQL 값은 바인딩으로 전달해 사용자 입력을 SQL 문장으로 합치지 않는다. 날짜는 ISO 8601 UTC, API 필드는 camelCase다. 등록은 201과 Location, 부분수정은 PATCH 200, 삭제는 204다. 작성 API는 다음 진도의 로그인 사용자만 허용한다.

## ③ 🛠️ 실기

`cd course` 후 `.env`를 준비한다. 기본은 `DB_DRIVER=sqlite`, `DATABASE_URL=./data/desk.sqlite`다. 첫 요청 또는 `npm run test:db`가 파일과 records 테이블을 만든다. UI는 `/auth`에서 계정을 만든 다음 `/board`에서 글을 저장한다. 상태 401은 DB 실패가 아니라 로그인 요구다.

아래 store 파일의 다른 DB 분기는 study11에서 읽는다. 이 진도는 sqlite 분기와 공통 메소드만 사용한다. 정적 랜딩은 `/`, 요청 시 조회되는 목록은 `/api/posts`다. 위 원문 추가 체크 항목은 외부 서버를 지정하므로 이번 Astro 단독 범위에서는 체크하지 않는다. 동등한 v1 계약은 Astro 엔드포인트로 구현했다.

### `course/src/lib/store.mjs` 전체 코드

[store.mjs](course/src/lib/store.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { settings } from './config.mjs';

// 모든 DB가 같은 저장 계약을 제공한다. JSON payload는 학습용이며 큰 목록은 DB 쿼리로 옮긴다.
export async function openStore(config = settings()) {
  const decode = row => row ? { ...JSON.parse(row.payload), id: Number(row.id) } : null;
  if (config.driver === 'sqlite') {
    const { DatabaseSync } = await import('node:sqlite');
    if (config.database !== ':memory:') await mkdir(dirname(config.database), { recursive: true });
    const db = new DatabaseSync(config.database);
    db.exec('PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000; CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, payload TEXT NOT NULL, unique_key TEXT UNIQUE); CREATE INDEX IF NOT EXISTS records_kind ON records(kind);');
    return {
      create: async (kind, value, key = null) => {
        const r = db.prepare('INSERT INTO records(kind,payload,unique_key) VALUES (?,?,?)').run(kind, JSON.stringify(value), key);
        return { ...value, id: Number(r.lastInsertRowid) };
      },
      list: async kind => db.prepare('SELECT id,payload FROM records WHERE kind=?').all(kind).map(decode),
      get: async (kind, id) => decode(db.prepare('SELECT id,payload FROM records WHERE kind=? AND id=?').get(kind, id)),
      replace: async (kind, id, value) => db.prepare('UPDATE records SET payload=? WHERE kind=? AND id=?').run(JSON.stringify(value), kind, id),
      remove: async (kind, id) => db.prepare('DELETE FROM records WHERE kind=? AND id=?').run(kind, id),
      close: async () => db.close(),
    };
  }
  if (config.driver === 'postgres') {
    const { Pool } = await import('pg');
    const db = new Pool({ connectionString: config.database, max: 5 });
    await db.query('CREATE TABLE IF NOT EXISTS records (id SERIAL PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL, unique_key TEXT UNIQUE)');
    await db.query('CREATE INDEX IF NOT EXISTS records_kind ON records(kind)');
    return {
      create: async (kind, value, key = null) => decode((await db.query('INSERT INTO records(kind,payload,unique_key) VALUES ($1,$2,$3) RETURNING id,payload', [kind, JSON.stringify(value), key])).rows[0]),
      list: async kind => (await db.query('SELECT id,payload FROM records WHERE kind=$1', [kind])).rows.map(decode),
      get: async (kind, id) => decode((await db.query('SELECT id,payload FROM records WHERE kind=$1 AND id=$2', [kind, id])).rows[0]),
      replace: async (kind, id, value) => db.query('UPDATE records SET payload=$1 WHERE kind=$2 AND id=$3', [JSON.stringify(value), kind, id]),
      remove: async (kind, id) => db.query('DELETE FROM records WHERE kind=$1 AND id=$2', [kind, id]),
      close: async () => db.end(),
    };
  }
  if (config.driver === 'mariadb') {
    const mysql = await import('mysql2/promise');
    const db = mysql.createPool(config.database);
    await db.query('CREATE TABLE IF NOT EXISTS records (id INT PRIMARY KEY AUTO_INCREMENT, kind VARCHAR(32) NOT NULL, payload LONGTEXT NOT NULL, unique_key VARCHAR(255) UNIQUE, INDEX records_kind(kind))');
    return {
      create: async (kind, value, key = null) => { const [r] = await db.execute('INSERT INTO records(kind,payload,unique_key) VALUES (?,?,?)', [kind, JSON.stringify(value), key]); return { ...value, id: Number(r.insertId) }; },
      list: async kind => { const [rows] = await db.execute('SELECT id,payload FROM records WHERE kind=?', [kind]); return rows.map(decode); },
      get: async (kind, id) => { const [rows] = await db.execute('SELECT id,payload FROM records WHERE kind=? AND id=?', [kind, id]); return decode(rows[0]); },
      replace: async (kind, id, value) => db.execute('UPDATE records SET payload=? WHERE kind=? AND id=?', [JSON.stringify(value), kind, id]),
      remove: async (kind, id) => db.execute('DELETE FROM records WHERE kind=? AND id=?', [kind, id]),
      close: async () => db.end(),
    };
  }
  if (config.driver === 'mongodb') {
    const { MongoClient } = await import('mongodb');
    const db = await new MongoClient(config.database).connect();
    const records = db.db().collection('records'), counters = db.db().collection('counters');
    await records.createIndex({ unique_key: 1 }, { unique: true, partialFilterExpression: { unique_key: { $type: 'string' } } });
    await records.createIndex({ kind: 1 });
    return {
      create: async (kind, value, key = null) => {
        const counter = await counters.findOneAndUpdate({ _id: 'records' }, { $inc: { seq: 1 } }, { upsert: true, returnDocument: 'after' });
        const row = { _id: counter.seq, id: counter.seq, kind, payload: JSON.stringify(value), ...(key ? { unique_key: key } : {}) };
        await records.insertOne(row); return decode(row);
      },
      list: async kind => (await records.find({ kind }).toArray()).map(decode),
      get: async (kind, id) => decode(await records.findOne({ kind, id })),
      replace: async (kind, id, value) => records.updateOne({ kind, id }, { $set: { payload: JSON.stringify(value) } }),
      remove: async (kind, id) => records.deleteOne({ kind, id }),
      close: async () => db.close(),
    };
  }
  throw new Error(`지원하지 않는 DB_DRIVER: ${config.driver}`);
}
let singleton;
export function getStore() { return singleton ??= openStore(); }
export function duplicate(error) { return ['23505', 'ER_DUP_ENTRY', 11000].includes(error?.code) || /UNIQUE constraint failed/.test(String(error)); }
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'node:fs/promises'`의 기능을 이 파일에서 사용한다. |
| 2 | `'node:path'`의 기능을 이 파일에서 사용한다. |
| 3 | `'./config.mjs'`의 기능을 이 파일에서 사용한다. |
| 4 | 코드 구간을 나누는 빈 줄이다. |
| 5 | 모든 DB가 같은 저장 계약을 제공한다. JSON payload는 학습용이며 큰 목록은 DB 쿼리로 옮긴다. |
| 6 | 비동기 함수 `openStore`의 입력과 처리 범위를 정의한다. |
| 7 | JSON 문자열을 객체로 해석한다. 잘못된 입력은 상위 오류 처리로 넘긴다. |
| 8 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 9 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { DatabaseSync }`. |
| 10 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 11 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const db`. |
| 12 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `db.exec('PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000; CREATE TABLE IF NOT EXISTS records (id INTEGER PRI`. |
| 13 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 14 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `create: async (kind, value, key = null) => {`. |
| 15 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 16 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 17 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 18 | DB 드라이버에 SQL과 바인딩 값을 전달해 이 저장 작업을 수행한다. |
| 19 | DB 드라이버에 SQL과 바인딩 값을 전달해 이 저장 작업을 수행한다. |
| 20 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 21 | DB 드라이버에 SQL과 바인딩 값을 전달해 이 저장 작업을 수행한다. |
| 22 | 사용이 끝난 스트림·소켓·DB 자원을 종료하거나 잠금을 해제한다. |
| 23 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 24 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 25 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 26 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { Pool }`. |
| 27 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const db`. |
| 28 | DB 드라이버에 SQL과 바인딩 값을 전달해 이 저장 작업을 수행한다. |
| 29 | DB 드라이버에 SQL과 바인딩 값을 전달해 이 저장 작업을 수행한다. |
| 30 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 31 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 32 | DB 드라이버에 SQL과 바인딩 값을 전달해 이 저장 작업을 수행한다. |
| 33 | DB 드라이버에 SQL과 바인딩 값을 전달해 이 저장 작업을 수행한다. |
| 34 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 35 | DB 드라이버에 SQL과 바인딩 값을 전달해 이 저장 작업을 수행한다. |
| 36 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `close: async () => db.end(),`. |
| 37 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 38 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 39 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 40 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const mysql`. |
| 41 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const db`. |
| 42 | DB 드라이버에 SQL과 바인딩 값을 전달해 이 저장 작업을 수행한다. |
| 43 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 44 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 45 | DB 드라이버에 SQL과 바인딩 값을 전달해 이 저장 작업을 수행한다. |
| 46 | DB 드라이버에 SQL과 바인딩 값을 전달해 이 저장 작업을 수행한다. |
| 47 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 48 | DB 드라이버에 SQL과 바인딩 값을 전달해 이 저장 작업을 수행한다. |
| 49 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `close: async () => db.end(),`. |
| 50 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 51 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 52 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 53 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { MongoClient }`. |
| 54 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const db`. |
| 55 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const records`. |
| 56 | 조회 또는 고유성 보장을 위한 인덱스를 만든다. |
| 57 | 조회 또는 고유성 보장을 위한 인덱스를 만든다. |
| 58 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 59 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `create: async (kind, value, key = null) => {`. |
| 60 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const counter`. |
| 61 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 62 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `await records.insertOne(row); return decode(row);`. |
| 63 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 64 | 목록의 각 항목을 화면 또는 응답에 필요한 모양으로 변환한다. |
| 65 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `get: async (kind, id) => decode(await records.findOne({ kind, id })),`. |
| 66 | 객체를 JSON 문자열로 직렬화해 HTTP 또는 저장소에 전달한다. |
| 67 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `remove: async (kind, id) => records.deleteOne({ kind, id }),`. |
| 68 | 사용이 끝난 스트림·소켓·DB 자원을 종료하거나 잠금을 해제한다. |
| 69 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 70 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 71 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `throw new Error(지원하지 않는 DB_DRIVER: ${config.driver});`. |
| 72 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 73 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let singleton;`. |
| 74 | 재사용 함수 `getStore`를 정의한다. |
| 75 | 재사용 함수 `duplicate`를 정의한다. |

### `course/src/lib/posts.mjs` 전체 코드

[posts.mjs](course/src/lib/posts.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { fail } from './http.mjs';
import { owned, requireUser } from './auth.mjs';
import { postSchema, validate, listQuery } from './validation.mjs';

export async function serializePost(store, post) {
  if (!post) fail(404, 'NOT_FOUND', '글이 없습니다.');
  const author = await store.get('users', post.authorId);
  const comments = (await store.list('comments')).filter(c => c.postId === post.id);
  return { id: post.id, title: post.title, body: post.body, tags: post.tags,
    author: { id: author.id, nickname: author.nickname }, commentCount: comments.length,
    createdAt: post.createdAt, updatedAt: post.updatedAt };
}
export async function listPosts(store, url) {
  const { page, limit, q, sort } = listQuery(url), needle = q.toLowerCase();
  const posts = (await store.list('posts')).filter(p => `${p.title} ${p.body}`.toLowerCase().includes(needle));
  const data = await Promise.all(posts.map(post => serializePost(store, post)));
  data.sort((a, b) => sort === '-commentCount' ? b.commentCount - a.commentCount || b.id - a.id : (sort === 'createdAt' ? 1 : -1) * (a.createdAt.localeCompare(b.createdAt) || a.id - b.id));
  return { data: data.slice((page - 1) * limit, page * limit), meta: { page, limit, total: data.length, totalPages: Math.ceil(data.length / limit), q } };
}
export async function createPost(store, user, input) {
  requireUser(user);
  const values = validate(postSchema, input), now = new Date().toISOString();
  return serializePost(store, await store.create('posts', { ...values, authorId: user.id, createdAt: now, updatedAt: now }));
}
export async function updatePost(store, user, id, input) {
  const old = owned(await store.get('posts', id), user);
  const patch = validate(postSchema.partial().extend({ tags: postSchema.shape.tags.unwrap().optional() }), input);
  if (!Object.keys(patch).length) fail(400, 'VALIDATION_ERROR', '수정할 필드가 필요합니다.');
  const next = { ...old, ...patch, updatedAt: new Date().toISOString() };
  await store.replace('posts', id, next); return serializePost(store, next);
}
export async function deletePost(store, user, id) {
  owned(await store.get('posts', id), user);
  // 학습용 단일 인스턴스. 운영에서는 FK cascade/트랜잭션으로 이 경계를 묶는다.
  for (const c of await store.list('comments')) if (c.postId === id) await store.remove('comments', c.id);
  await store.remove('posts', id);
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'./http.mjs'`의 기능을 이 파일에서 사용한다. |
| 2 | `'./auth.mjs'`의 기능을 이 파일에서 사용한다. |
| 3 | `'./validation.mjs'`의 기능을 이 파일에서 사용한다. |
| 4 | 코드 구간을 나누는 빈 줄이다. |
| 5 | 비동기 함수 `serializePost`의 입력과 처리 범위를 정의한다. |
| 6 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 7 | 종류와 id가 일치하는 단일 레코드를 조회한다. |
| 8 | 저장소에서 해당 종류의 레코드를 읽어 필터·검증·응답에 사용한다. |
| 9 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 10 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `author: { id: author.id, nickname: author.nickname }, commentCount: comments.length,`. |
| 11 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `createdAt: post.createdAt, updatedAt: post.updatedAt };`. |
| 12 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 13 | 비동기 함수 `listPosts`의 입력과 처리 범위를 정의한다. |
| 14 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { page, limit, q, sort }`. |
| 15 | 저장소에서 해당 종류의 레코드를 읽어 필터·검증·응답에 사용한다. |
| 16 | 목록의 각 항목을 화면 또는 응답에 필요한 모양으로 변환한다. |
| 17 | 정해진 비교 규칙에 따라 결과 순서를 맞춘다. |
| 18 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 19 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 20 | 비동기 함수 `createPost`의 입력과 처리 범위를 정의한다. |
| 21 | 미인증 사용자를 401로 거절하고 인증 사용자만 다음 처리를 허용한다. |
| 22 | 정해진 스키마로 입력을 검사하고 허용된 값만 다음 계층으로 보낸다. |
| 23 | 저장소 계약으로 새 레코드를 생성하며 생성 id를 받는다. |
| 24 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 25 | 비동기 함수 `updatePost`의 입력과 처리 범위를 정의한다. |
| 26 | 자원 존재와 작성자 일치를 확인해 다른 사람의 데이터 접근을 막는다. |
| 27 | 정해진 스키마로 입력을 검사하고 허용된 값만 다음 계층으로 보낸다. |
| 28 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 29 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const next`. |
| 30 | 검증한 변경 값을 지정 레코드에 저장한다. |
| 31 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 32 | 비동기 함수 `deletePost`의 입력과 처리 범위를 정의한다. |
| 33 | 자원 존재와 작성자 일치를 확인해 다른 사람의 데이터 접근을 막는다. |
| 34 | 학습용 단일 인스턴스. 운영에서는 FK cascade/트랜잭션으로 이 경계를 묶는다. |
| 35 | 지정 kind와 id의 레코드를 삭제한다. |
| 36 | 지정 kind와 id의 레코드를 삭제한다. |
| 37 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/src/lib/basic-api.mjs` 전체 코드

[basic-api.mjs](course/src/lib/basic-api.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { z } from 'zod';
import { body, fail, json, positiveId } from './http.mjs';
import { signupSchema, loginSchema, validate } from './validation.mjs';
import { signup, login, publicUser, requireUser, owned, digest } from './auth.mjs';
import { listPosts, serializePost, createPost, updatePost, deletePost } from './posts.mjs';
import { postCache } from './cache.mjs';
import { settings } from './config.mjs';

export function sessionCookie(context, token) {
  context.cookies.set('desk_session', token, { path: '/', httpOnly: true, sameSite: 'lax', secure: settings().site.startsWith('https:'), maxAge: 3600 });
}
export async function dispatchBasic(context, store) {
  const { request, url, locals } = context, method = request.method;
  const path = url.pathname.replace(/\/$/, ''), user = locals.user;
  if (path === '/api/auth/signup' && method === 'POST') {
    const created = await signup(store, validate(signupSchema, await body(request)));
    return json({ data: publicUser(created) }, 201);
  }
  if (path === '/api/auth/login' && method === 'POST') {
    const data = await login(store, validate(loginSchema, await body(request)));
    sessionCookie(context, data.accessToken); return json({ data });
  }
  if (path === '/api/auth/me' && method === 'GET') return json({ data: requireUser(user) });
  if (path === '/api/auth/logout' && method === 'POST') {
    requireUser(user);
    for (const session of await store.list('sessions')) if (session.digest === digest(locals.token)) await store.remove('sessions', session.id);
    context.cookies.delete('desk_session', { path: '/' }); return new Response(null, { status: 204 });
  }
  if (path === '/api/posts') {
    if (method === 'GET') return json(process.env.COURSE_STAGE === 'midpoint' ? await listPosts(store, url) : await postCache.get(url.search, () => listPosts(store, url)));
    if (method === 'POST') {
      const data = await createPost(store, user, await body(request)); postCache.clear();
      return json({ data }, 201, { Location: `/api/posts/${data.id}` });
    }
    fail(405, 'METHOD_NOT_ALLOWED', 'GET 또는 POST를 사용하세요.');
  }
  let match = path.match(/^\/api\/posts\/([^/]+)$/);
  if (match) {
    const id = positiveId(match[1]);
    if (method === 'GET') return json({ data: await serializePost(store, await store.get('posts', id)) });
    if (method === 'PATCH') { const data = await updatePost(store, user, id, await body(request)); postCache.clear(); return json({ data }); }
    if (method === 'DELETE') { await deletePost(store, user, id); postCache.clear(); return new Response(null, { status: 204 }); }
    fail(405, 'METHOD_NOT_ALLOWED', 'GET/PATCH/DELETE를 사용하세요.');
  }
  match = path.match(/^\/api\/posts\/([^/]+)\/comments$/);
  if (match) {
    const postId = positiveId(match[1]);
    if (!(await store.get('posts', postId))) fail(404, 'NOT_FOUND', '글이 없습니다.');
    if (method === 'GET') {
      const comments = (await store.list('comments')).filter(c => c.postId === postId);
      const data = await Promise.all(comments.map(async c => ({ id: c.id, body: c.body, postId, createdAt: c.createdAt,
        author: { id: c.authorId, nickname: (await store.get('users', c.authorId)).nickname } })));
      return json({ data });
    }
    if (method === 'POST') {
      requireUser(user);
      const input = validate(z.object({ body: z.string().trim().min(1).max(2000) }).strict(), await body(request));
      const c = await store.create('comments', { ...input, postId, authorId: user.id, createdAt: new Date().toISOString() });
      postCache.clear();
      return json({ data: { id: c.id, body: c.body, postId, author: { id: user.id, nickname: user.nickname }, createdAt: c.createdAt } }, 201);
    }
  }
  match = path.match(/^\/api\/comments\/([^/]+)$/);
  if (match && method === 'DELETE') {
    const id = positiveId(match[1]); owned(await store.get('comments', id), user);
    await store.remove('comments', id); postCache.clear(); return new Response(null, { status: 204 });
  }
  return null;
}
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'zod'`의 기능을 이 파일에서 사용한다. |
| 2 | `'./http.mjs'`의 기능을 이 파일에서 사용한다. |
| 3 | `'./validation.mjs'`의 기능을 이 파일에서 사용한다. |
| 4 | `'./auth.mjs'`의 기능을 이 파일에서 사용한다. |
| 5 | `'./posts.mjs'`의 기능을 이 파일에서 사용한다. |
| 6 | `'./cache.mjs'`의 기능을 이 파일에서 사용한다. |
| 7 | `'./config.mjs'`의 기능을 이 파일에서 사용한다. |
| 8 | 코드 구간을 나누는 빈 줄이다. |
| 9 | 재사용 함수 `sessionCookie`를 정의한다. |
| 10 | 서버가 쿠키와 보안 속성을 응답에 설정한다. |
| 11 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 12 | 비동기 함수 `dispatchBasic`의 입력과 처리 범위를 정의한다. |
| 13 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { request, url, locals }`. |
| 14 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const path`. |
| 15 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 16 | 정해진 스키마로 입력을 검사하고 허용된 값만 다음 계층으로 보낸다. |
| 17 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 18 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 19 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 20 | 정해진 스키마로 입력을 검사하고 허용된 값만 다음 계층으로 보낸다. |
| 21 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 22 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 23 | 미인증 사용자를 401로 거절하고 인증 사용자만 다음 처리를 허용한다. |
| 24 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 25 | 미인증 사용자를 401로 거절하고 인증 사용자만 다음 처리를 허용한다. |
| 26 | 지정 kind와 id의 레코드를 삭제한다. |
| 27 | 같은 경로의 쿠키를 만료시켜 브라우저 출입증을 지운다. |
| 28 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 29 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 30 | 실행/빌드 환경에서 설정을 읽어 기본값 또는 분기를 결정한다. |
| 31 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 32 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const data`. |
| 33 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 34 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 35 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 36 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 37 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `let match`. |
| 38 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 39 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const id`. |
| 40 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 41 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 42 | 응답 본문·상태·헤더 또는 스트림을 담은 HTTP Response를 만든다. |
| 43 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 44 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 45 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `match = path.match(/^\/api\/posts\/([^/]+)\/comments$/);`. |
| 46 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 47 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const postId`. |
| 48 | 조건에 맞지 않는 요청은 명시한 상태 코드와 공통 오류로 중단한다. |
| 49 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 50 | 저장소에서 해당 종류의 레코드를 읽어 필터·검증·응답에 사용한다. |
| 51 | 목록의 각 항목을 화면 또는 응답에 필요한 모양으로 변환한다. |
| 52 | 종류와 id가 일치하는 단일 레코드를 조회한다. |
| 53 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 54 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 55 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 56 | 미인증 사용자를 401로 거절하고 인증 사용자만 다음 처리를 허용한다. |
| 57 | 정해진 스키마로 입력을 검사하고 허용된 값만 다음 계층으로 보낸다. |
| 58 | 저장소 계약으로 새 레코드를 생성하며 생성 id를 받는다. |
| 59 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `postCache.clear();`. |
| 60 | 명시한 상태와 JSON 응답 본문을 HTTP 계약에 맞춰 반환한다. |
| 61 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 62 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 63 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `match = path.match(/^\/api\/comments\/([^/]+)$/);`. |
| 64 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 65 | 자원 존재와 작성자 일치를 확인해 다른 사람의 데이터 접근을 막는다. |
| 66 | 응답 본문·상태·헤더 또는 스트림을 담은 HTTP Response를 만든다. |
| 67 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 68 | 이 함수의 처리 결과를 호출자에게 반환하고 실행을 끝낸다. |
| 69 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

## ④ 🔗 연동 포인트

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e)의 `/api/posts`·`data/meta`·`error.fields/requestId`를 따른다. UI가 같은 Astro 앱의 API를 호출하며 별도 서버 프레임워크는 실행하지 않는다. DATABASE_URL과 DB_DRIVER를 바꾸는 경계는 study11에서 확장한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| DB 파일 열기 실패 | 경로·쓰기 권한 | 상위 디렉터리와 영속 경로 확인 |
| 등록 401 | 세션 없음 | 가입 후 로그인 |
| SQL 오류 | 문자열로 SQL 조합 | 파라미터 바인딩 사용 |

## ⑥ 직접 해보기

1. 가입·로그인 후 글을 등록하고 반환한 id로 상세·수정·삭제한다.
2. 서버를 재시작해 DB의 글이 유지되는지 확인한다.
3. 검색·정렬·limit=100을 호출해 50으로 제한되는지 확인한다.

## ⑦ ☐ 체크리스트

- [ ] 연결 설정→모델→목록→상세→등록→수정→삭제 순서로 확인했다.
- [ ] DB 연결 정보를 환경변수로 분리했다.
- [ ] data/meta와 공통 오류 형식을 구현했다.
- [ ] 학습 목표의 예제 "정적 랜딩 + 게시판 목록 하나"를 스펙 v1 API(Express 또는 FastAPI)로 목록 읽기

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study7.md](study7.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
