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
