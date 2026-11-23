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
