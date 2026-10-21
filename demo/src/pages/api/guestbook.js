import { appendEntry, readEntries } from '../../lib/guestbook.js';

function text(message, status) {
  return new Response(message, {
    status,
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
}

export const prerender = false;

export async function GET() {
  return Response.json(await readEntries());
}

export async function POST({ request, redirect }) {
  let form;
  try {
    form = await request.formData();
  } catch {
    return text('폼 형식이 아닙니다.', 400);
  }
  const name = String(form.get('name') || '').trim();
  const message = String(form.get('message') || '').trim();
  if (!name || !message || name.length > 40 || message.length > 280) {
    return text('이름과 내용을 확인하세요. 이름은 40자, 내용은 280자까지입니다.', 400);
  }
  await appendEntry({ name, message });
  return redirect('/guestbook');
}
