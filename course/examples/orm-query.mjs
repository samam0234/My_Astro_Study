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
