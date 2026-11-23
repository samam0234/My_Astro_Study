// study11: 실행 중 저장소와 같은 records 테이블을 표현하는 Drizzle 스키마.
import { pgTable, serial, text as pgText } from 'drizzle-orm/pg-core';
import { mysqlTable, int, longtext, varchar } from 'drizzle-orm/mysql-core';
export const pgRecords = pgTable('records', {
  id: serial('id').primaryKey(), kind: pgText('kind').notNull(), payload: pgText('payload').notNull(), uniqueKey: pgText('unique_key').unique(),
});
export const mariaRecords = mysqlTable('records', {
  id: int('id').autoincrement().primaryKey(), kind: varchar('kind', { length: 32 }).notNull(), payload: longtext('payload').notNull(), uniqueKey: varchar('unique_key', { length: 255 }).unique(),
});
