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
