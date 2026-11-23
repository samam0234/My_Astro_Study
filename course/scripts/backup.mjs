import { DatabaseSync, backup } from 'node:sqlite';
import { mkdir } from 'node:fs/promises';
import { settings } from '../src/lib/config.mjs';
const config = settings();
if (config.driver !== 'sqlite') throw new Error('PostgreSQL은 pg_dump, MariaDB는 mariadb-dump, MongoDB는 mongodump를 사용하세요.');
await mkdir('./data/backups', { recursive: true });
const file = `./data/backups/desk-${new Date().toISOString().replace(/[:.]/g, '-')}.sqlite`;
const db = new DatabaseSync(config.database);
try { await backup(db, file); console.log(file); }
finally { db.close(); }
