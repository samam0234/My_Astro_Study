import { randomUUID } from 'node:crypto';

export class HttpError extends Error {
  constructor(status, code, message, fields = {}) {
    super(message);
    Object.assign(this, { status, code, fields });
  }
}
export const fail = (status, code, message, fields) => { throw new HttpError(status, code, message, fields); };
export const json = (value, status = 200, headers = {}) => new Response(JSON.stringify(value), {
  status, headers: { 'Content-Type': 'application/json; charset=utf-8', ...headers },
});
export async function body(request, max = 65536) {
  if (!request.headers.get('content-type')?.includes('application/json')) fail(400, 'BAD_REQUEST', 'JSON 본문을 보내세요.');
  const reader = request.body?.getReader();
  if (!reader) fail(400, 'BAD_REQUEST', '본문이 없습니다.');
  let size = 0;
  const chunks = [];
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > max) { await reader.cancel(); fail(413, 'PAYLOAD_TOO_LARGE', '본문이 너무 큽니다.'); }
    chunks.push(value);
  }
  try { return JSON.parse(Buffer.concat(chunks).toString('utf8')); }
  catch { fail(400, 'BAD_REQUEST', 'JSON 문법을 확인하세요.'); }
}
export function errorResponse(error, requestId = randomUUID()) {
  const known = error instanceof HttpError;
  if (!known) console.error(JSON.stringify({ level: 'error', requestId, message: String(error) }));
  return json({ error: {
    code: known ? error.code : 'INTERNAL', message: known ? error.message : '서버 오류입니다.',
    fields: known ? error.fields : {}, requestId,
  } }, known ? error.status : 500, { 'X-Request-Id': requestId });
}
export function positiveId(value) {
  if (!/^\d+$/.test(value || '') || !Number.isSafeInteger(Number(value)) || Number(value) < 1) fail(400, 'BAD_REQUEST', '양의 정수 id가 필요합니다.');
  return Number(value);
}
