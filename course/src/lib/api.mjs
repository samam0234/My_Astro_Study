import { dispatchBasic, sessionCookie } from './basic-api.mjs';
import { z } from 'zod';
import { body, fail, json, positiveId } from './http.mjs';
import { validate } from './validation.mjs';
import { requireUser, owned } from './auth.mjs';
import { checkout, stripeWebhook, oauthStart, oauthCallback } from './integrations.mjs';
import { saveDocument, downloadDocument } from './files.mjs';
import { enqueueMail } from './jobs.mjs';
import { generate, retrieve } from './ai.mjs';
import { settings } from './config.mjs';

export async function dispatch(context, store) {
  const { request, url, locals } = context, method = request.method;
  const path = url.pathname.replace(/\/$/, ''), user = locals.user;
  const basic = await dispatchBasic(context, store);
  if (basic) return basic;
  if (process.env.COURSE_STAGE === 'midpoint') fail(404, 'NOT_FOUND', 'Midpoint mode exposes only auth and board APIs.');
  let match;
  if (path === '/api/mail' && method === 'POST') {
    requireUser(user); const job = await enqueueMail(store, user); return json({ data: job }, 202);
  }
  if (path === '/api/checkout' && method === 'POST') {
    requireUser(user);
    const { key } = validate(z.object({ key: z.uuid() }), await body(request));
    return json({ data: await checkout(user, settings().site, process.env, `checkout-${user.id}-${key}`) });
  }
  if (path === '/api/stripe/webhook' && method === 'POST') {
    // 외부에서 서명한 원문. 일반 JSON 파싱 전에 그대로 검증한다.
    const length = Number(request.headers.get('content-length'));
    if (!Number.isSafeInteger(length) || length < 1 || length > 65536) fail(413, 'PAYLOAD_TOO_LARGE', '웹훅 크기를 확인하세요.');
    const raw = await request.text();
    if (Buffer.byteLength(raw) > 65536) fail(413, 'PAYLOAD_TOO_LARGE', '웹훅이 너무 큽니다.');
    return json(await stripeWebhook(store, raw, request.headers.get('stripe-signature')));
  }
  if (path === '/api/oauth/start' && method === 'GET') return oauthStart(context.cookies, settings().site);
  if (path === '/api/oauth/callback' && method === 'GET') {
    const session = await oauthCallback(store, context, settings().site); sessionCookie(context, session.accessToken);
    return Response.redirect(`${settings().site}/board`, 302);
  }
  if (path === '/api/documents') {
    requireUser(user);
    if (method === 'GET') return json({ data: (await store.list('documents')).filter(d => d.authorId === user.id).map(({ key, text, ...d }) => d) });
    if (method === 'POST') { const d = await saveDocument(store, user, await body(request, 150000)); return json({ data: { id: d.id, name: d.name } }, 201); }
  }
  match = path.match(/^\/api\/documents\/([^/]+)\/download$/);
  if (match && method === 'GET') return downloadDocument(owned(await store.get('documents', positiveId(match[1])), user));
  if (path === '/api/ai' && method === 'POST') {
    requireUser(user);
    const input = validate(z.object({ documentId: z.number().int().positive(), question: z.string().trim().max(500).default('') }).strict(), await body(request));
    const doc = owned(await store.get('documents', input.documentId), user);
    const iterator = generate(doc.text, input.question, { signal: request.signal });
    // 첫 토큰까지 읽어 upstream HTTP 오류를 공통 JSON 오류로 반환한다.
    const first = await iterator.next(); let initial = true, answer = '', finished = false;
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async pull(controller) {
        try {
          const item = initial ? first : await iterator.next(); initial = false;
          if (item.done) {
            if (!finished) await store.create('questions', { documentId: doc.id, authorId: user.id, question: input.question, answer,
              sources: input.question ? retrieve(doc.text, input.question) : [{ index: 1 }], createdAt: new Date().toISOString() });
            finished = true; controller.close();
          } else { answer += item.value; controller.enqueue(encoder.encode(JSON.stringify({ delta: item.value }) + '\n')); }
        } catch { controller.enqueue(encoder.encode(JSON.stringify({ error: '생성이 중단되었습니다.' }) + '\n')); controller.close(); await iterator.return(); }
      },
      async cancel() { await iterator.return(); },
    });
    return new Response(stream, { headers: { 'Content-Type': 'application/x-ndjson; charset=utf-8', 'Cache-Control': 'no-store' } });
  }
  if (path === '/api/events' && method === 'GET') {
    requireUser(user);
    const encoder = new TextEncoder(); let timer, stop, count = 0, busy = false;
    const stream = new ReadableStream({
      start(controller) {
        stop = () => { clearInterval(timer); request.signal.removeEventListener('abort', stop); try { controller.close(); } catch {} };
        request.signal.addEventListener('abort', stop, { once: true });
        controller.enqueue(encoder.encode('retry: 3000\n\n'));
        timer = setInterval(async () => {
          if (busy) return; busy = true;
          try {
            const jobs = (await store.list('jobs')).filter(j => j.userId === user.id);
            controller.enqueue(encoder.encode(`event: jobs\ndata: ${JSON.stringify(jobs.map(j => ({ id: j.id, status: j.status })))}\n\n`));
            if (++count >= 30) stop();
          } catch { stop(); } finally { busy = false; }
        }, 1000);
      }, cancel() { stop(); },
    });
    return new Response(stream, { headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no' } });
  }
  fail(404, 'NOT_FOUND', 'API 경로가 없습니다.');
}
