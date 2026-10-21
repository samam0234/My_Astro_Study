import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const file = fileURLToPath(new URL('../../data/guestbook.json', import.meta.url));

export async function readEntries() {
  try {
    const text = await readFile(file, 'utf8');
    const entries = JSON.parse(text);
    return Array.isArray(entries) ? entries : [];
  } catch (error) {
    if (error && error.code === 'ENOENT') return [];
    throw error;
  }
}

export async function appendEntry({ name, message }) {
  const entries = await readEntries();
  entries.push({
    name,
    message,
    createdAt: new Date().toISOString(),
  });
  await mkdir(dirname(file), { recursive: true });
  await writeFile(file, `${JSON.stringify(entries, null, 2)}\n`);
  return entries;
}
