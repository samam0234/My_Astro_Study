# study11 · DB 확장

## ① 목표 한 줄

저장소 계약을 유지하며 PostgreSQL·MariaDB·MongoDB로 연결을 바꾼다.

기준: [Notion Astro](https://app.notion.com/p/3fdd7dec5e2e8136a3d7e7023440d36f). 실행 앱은 `course/` 하나다. 루트의 기존 study 문서를 이 과정으로 갱신했다.

## ② 📖 이론

DB 교체는 URL 한 줄만 바꾸는 일이 아니다. 드라이버, 키 생성, 바인딩 문법, 인덱스, 트랜잭션, 백업 방법이 달라진다. 저장소 계약을 지키면 API의 data/meta 모양은 그대로 유지할 수 있다. 기존 데이터는 새 연결로 자동 이동하지 않으므로 별도 이관 검증이 필요하다.

PostgreSQL은 pg Pool과 `$1` 바인딩·SERIAL을, MariaDB는 mysql2 pool과 `?` 바인딩·AUTO_INCREMENT를 사용한다. MongoDB는 collection과 원자적 counter를 사용해 공통 명세의 숫자 id를 유지한다. 고유 키는 SQL UNIQUE와 MongoDB partial unique index로 중복 이메일을 막는다.

ORM 예제는 Drizzle로 SQL 테이블을 표현한다. PostgreSQL 스키마는 pgTable·serial·text, MariaDB는 mysqlTable·int.autoincrement·longtext다. MongoDB는 이 SQL ORM 스키마를 공유하지 않고 공식 드라이버를 쓴다. 운영 API의 기본 구현은 명시적 드라이버이며 ORM 조회는 별도 실행 예제다.

## ③ 🛠️ 실기

로컬 Docker 엔진이 켜져 있을 때만 `course/`에서 실행한다. 기본값은 학습 전용 비밀번호이며 공개 서버에 그대로 쓰지 않는다.

```powershell
docker compose -f compose.db.yml up -d postgres
$env:DB_DRIVER='postgres'
$env:DATABASE_URL='postgresql://astro:local-study-only@127.0.0.1:5438/astro'
npm run test:db
node examples/orm-query.mjs
```

1행은 PostgreSQL 컨테이너, 2~3행은 드라이버와 접속, 4행은 같은 저장 계약의 CRUD, 5행은 ORM 조회다. MariaDB는 `docker compose -f compose.db.yml up -d mariadb`, `DB_DRIVER=mariadb`, `DATABASE_URL=mysql://astro:local-study-only@127.0.0.1:3308/astro`로 바꾼다. MongoDB는 서비스 mongodb, 드라이버 mongodb, URL `mongodb://astro:local-study-only@127.0.0.1:27018/astro?authSource=admin`이다.

실습 후 `Remove-Item Env:DB_DRIVER,Env:DATABASE_URL`로 셸 설정을 되돌린다. `.env`에 저장한 값도 확인한다. 테이블은 openStore가 생성하므로 ORM 예제 실행 전에 test:db를 실행한다. 고도화 시 정규화 테이블과 버전 있는 migration을 도입하고, 이 JSON 저장 모델의 메모리 목록 조회를 SQL 조건·인덱스로 옮긴다. 위 원문 DB 없음 항목은 예전 저장 방식의 기록이며 새 course 앱에는 SQLite가 있다. 현재 환경에서는 외부 DB 3종 실행을 검증하지 않았다.

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

### `course/examples/orm-schema.mjs` 전체 코드

[orm-schema.mjs](course/examples/orm-schema.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
// study11: 실행 중 저장소와 같은 records 테이블을 표현하는 Drizzle 스키마.
import { pgTable, serial, text as pgText } from 'drizzle-orm/pg-core';
import { mysqlTable, int, longtext, varchar } from 'drizzle-orm/mysql-core';
export const pgRecords = pgTable('records', {
  id: serial('id').primaryKey(), kind: pgText('kind').notNull(), payload: pgText('payload').notNull(), uniqueKey: pgText('unique_key').unique(),
});
export const mariaRecords = mysqlTable('records', {
  id: int('id').autoincrement().primaryKey(), kind: varchar('kind', { length: 32 }).notNull(), payload: longtext('payload').notNull(), uniqueKey: varchar('unique_key', { length: 255 }).unique(),
});
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | study11: 실행 중 저장소와 같은 records 테이블을 표현하는 Drizzle 스키마. |
| 2 | `'drizzle-orm/pg-core'`의 기능을 이 파일에서 사용한다. |
| 3 | `'drizzle-orm/mysql-core'`의 기능을 이 파일에서 사용한다. |
| 4 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `export const pgRecords`. |
| 5 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `id: serial('id').primaryKey(), kind: pgText('kind').notNull(), payload: pgText('payload').notNull(), uniqueKey`. |
| 6 | 앞서 연 함수·객체·호출의 범위를 닫는다. |
| 7 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `export const mariaRecords`. |
| 8 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `id: int('id').autoincrement().primaryKey(), kind: varchar('kind', { length: 32 }).notNull(), payload: longtext`. |
| 9 | 앞서 연 함수·객체·호출의 범위를 닫는다. |

### `course/examples/orm-query.mjs` 전체 코드

[orm-query.mjs](course/examples/orm-query.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import { settings } from '../src/lib/config.mjs';
import { pgRecords, mariaRecords } from './orm-schema.mjs';
const config = settings();
if (config.driver === 'postgres') {
  const { Pool } = await import('pg');
  const { drizzle } = await import('drizzle-orm/node-postgres');
  const pool = new Pool({ connectionString: config.database });
  try { console.log(await drizzle(pool).select().from(pgRecords).limit(3)); } finally { await pool.end(); }
} else if (config.driver === 'mariadb') {
  const mysql = await import('mysql2/promise');
  const { drizzle } = await import('drizzle-orm/mysql2');
  const pool = mysql.createPool(config.database);
  try { console.log(await drizzle(pool).select().from(mariaRecords).limit(3)); } finally { await pool.end(); }
} else throw new Error('DB_DRIVER=postgres 또는 mariadb를 지정하세요.');
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'../src/lib/config.mjs'`의 기능을 이 파일에서 사용한다. |
| 2 | `'./orm-schema.mjs'`의 기능을 이 파일에서 사용한다. |
| 3 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const config`. |
| 4 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 5 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { Pool }`. |
| 6 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { drizzle }`. |
| 7 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const pool`. |
| 8 | 성공·실패에 관계없이 연결/잠금 등 정리 작업을 실행한다. |
| 9 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |
| 10 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const mysql`. |
| 11 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const { drizzle }`. |
| 12 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const pool`. |
| 13 | 성공·실패에 관계없이 연결/잠금 등 정리 작업을 실행한다. |
| 14 | 조건에 따라 성공·오류 또는 실행 환경별 경로를 선택한다. |

### `course/compose.db.yml` 전체 코드

[compose.db.yml](course/compose.db.yml)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```yaml
services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_DB: astro
      POSTGRES_USER: astro
      POSTGRES_PASSWORD: local-study-only
    ports: ["127.0.0.1:5438:5432"]
    volumes: ["pg-data:/var/lib/postgresql/data"]
  mariadb:
    image: mariadb:11
    environment:
      MARIADB_DATABASE: astro
      MARIADB_USER: astro
      MARIADB_PASSWORD: local-study-only
      MARIADB_ROOT_PASSWORD: local-root-only
    ports: ["127.0.0.1:3308:3306"]
    volumes: ["maria-data:/var/lib/mysql"]
  mongodb:
    image: mongo:7
    environment:
      MONGO_INITDB_ROOT_USERNAME: astro
      MONGO_INITDB_ROOT_PASSWORD: local-study-only
    ports: ["127.0.0.1:27018:27017"]
    volumes: ["mongo-data:/data/db"]
volumes:
  pg-data:
  maria-data:
  mongo-data:
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 2 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `postgres:`. |
| 3 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `image: postgres:17`. |
| 4 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `environment:`. |
| 5 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `POSTGRES_DB: astro`. |
| 6 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `POSTGRES_USER: astro`. |
| 7 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `POSTGRES_PASSWORD: local-study-only`. |
| 8 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `ports: ["127.0.0.1:5438:5432"]`. |
| 9 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 10 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `mariadb:`. |
| 11 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `image: mariadb:11`. |
| 12 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `environment:`. |
| 13 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `MARIADB_DATABASE: astro`. |
| 14 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `MARIADB_USER: astro`. |
| 15 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `MARIADB_PASSWORD: local-study-only`. |
| 16 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `MARIADB_ROOT_PASSWORD: local-root-only`. |
| 17 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `ports: ["127.0.0.1:3308:3306"]`. |
| 18 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 19 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `mongodb:`. |
| 20 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `image: mongo:7`. |
| 21 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `environment:`. |
| 22 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `MONGO_INITDB_ROOT_USERNAME: astro`. |
| 23 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `MONGO_INITDB_ROOT_PASSWORD: local-study-only`. |
| 24 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `ports: ["127.0.0.1:27018:27017"]`. |
| 25 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 26 | 이 설정 블록에서 검증·실행 또는 배포 구성을 선언한다. |
| 27 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `pg-data:`. |
| 28 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `maria-data:`. |
| 29 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `mongo-data:`. |

### `course/scripts/db-contract.mjs` 전체 코드

[db-contract.mjs](course/scripts/db-contract.mjs)를 그대로 사용한다. 코드 블록의 줄 번호는 바로 아래 설명표와 일치한다.

```javascript
import assert from 'node:assert/strict';
import { openStore } from '../src/lib/store.mjs';
import { settings } from '../src/lib/config.mjs';
const store = await openStore(settings());
const kind = `contract-${Date.now()}`; let row;
try {
  row = await store.create(kind, { value: '처음' });
  assert.equal((await store.get(kind, row.id)).value, '처음');
  await store.replace(kind, row.id, { value: '변경' });
  assert.equal((await store.list(kind))[0].value, '변경');
  await store.remove(kind, row.id); assert.equal(await store.get(kind, row.id), null);
  console.log(`${settings().driver}: CRUD 계약 통과`);
} finally { if (row) await store.remove(kind, row.id); await store.close(); }
```

줄별 설명:

| 줄 | 설명 |
|---|---|
| 1 | `'node:assert/strict'`의 기능을 이 파일에서 사용한다. |
| 2 | `'../src/lib/store.mjs'`의 기능을 이 파일에서 사용한다. |
| 3 | `'../src/lib/config.mjs'`의 기능을 이 파일에서 사용한다. |
| 4 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const store`. |
| 5 | 이 이름의 값·객체·함수를 선언해 아래 처리에서 사용한다: `const kind`. |
| 6 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `try {`. |
| 7 | 저장소 계약으로 새 레코드를 생성하며 생성 id를 받는다. |
| 8 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 9 | 검증한 변경 값을 지정 레코드에 저장한다. |
| 10 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 11 | 실제 값과 기대한 계약이 같은지 검사하고 다르면 테스트를 실패시킨다. |
| 12 | 현재 처리 구간의 세부 값·호출·구조를 지정한다: `console.log(${settings().driver}: CRUD 계약 통과);`. |
| 13 | 성공·실패에 관계없이 연결/잠금 등 정리 작업을 실행한다. |

## ④ 🔗 연동 포인트

동일한 openStore 계약→test:db→API/브라우저 회귀 검사 순서로 교체한다. 생산 데이터 이관은 백업·스테이징·건수·참조·고유성 검증 후 전환한다. 다음 단계는 이 API와 UI 라이브러리의 연결을 다룬다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| connection refused | DB 서비스/포트 미준비 | DB 서비스 준비 후 연결 |
| Mongo 인증 실패 | authSource 누락 | admin 인증 DB 지정 |
| 새 DB에 데이터 없음 | 연결 교체만 수행 | 별도 이관·검증 실행 |

## ⑥ 직접 해보기

1. DB 서비스 하나를 실행하고 DB_DRIVER·DATABASE_URL을 바꿔 test:db를 실행한다.
2. Drizzle 조회 예제를 같은 DB에 실행한다.
3. 중복 이메일과 재시작 후 데이터 보존을 각 DB에서 확인한다.

## ⑦ ☐ 체크리스트

- [ ] DB별 연결·pool·id·바인딩·unique 인덱스를 구분했다.
- [ ] 드라이버와 ORM의 책임·스키마 차이를 설명했다.
- [ ] 기존 DB 백업과 별도 데이터 이관 절차를 정리했다.
- [ ] DB 칸이 정리 영역에 없다 → 저장소를 확인해 이 페이지에 기록 (DB 없음, 아래 저장 방식과 코드 스니펫)

## ⑧ 다음 단계 연결 문장

이 단계의 결과를 [study12.md](study12.md)에서 다음 기능과 연결한다. 학습자가 직접 확인할 체크는 의도적으로 비워 두며, 실제 실행 검증 결과는 [검증 기록](docs/verification.md)에 별도로 남긴다.
