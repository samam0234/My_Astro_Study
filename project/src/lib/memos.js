import { getCollection } from 'astro:content';

export async function listMemos() {
  const memos = await getCollection('memos');
  return memos
    .sort((a, b) => a.data.title.localeCompare(b.data.title, 'ko'))
    .map((memo) => ({
      id: memo.id,
      title: memo.data.title,
      summary: memo.data.summary,
      minutes: memo.data.minutes,
    }));
}
