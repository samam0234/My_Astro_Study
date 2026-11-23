import { defineMiddleware } from 'astro:middleware';
import { randomUUID } from 'node:crypto';
import { getStore } from './lib/store.mjs';
import { authenticate } from './lib/auth.mjs';
import { errorResponse, fail } from './lib/http.mjs';
import { settings } from './lib/config.mjs';

const hits = new Map();
export const onRequest = defineMiddleware(async (context, next) => {
  if (!context.url.pathname.startsWith('/api/') && context.url.pathname !== '/health') return next();
  const started = performance.now(), supplied = context.request.headers.get('x-request-id');
  const requestId = supplied && /^[\w-]{1,100}$/.test(supplied) ? supplied : randomUUID();
  let response;
  const config = settings(), origin = context.request.headers.get('origin');
  try {
    context.locals.requestId = requestId;
    if (origin && origin !== new URL(config.site).origin && origin !== config.cors) fail(403, 'FORBIDDEN', '허용하지 않은 Origin입니다.');
    if (context.request.method === 'OPTIONS') response = new Response(null, { status: 204 });
    else {
      const token = context.request.headers.get('authorization')?.replace(/^Bearer\s+/i, '') || context.cookies.get('desk_session')?.value;
      context.locals.token = token;
      context.locals.user = token ? await authenticate(await getStore(), token) : null;
      if (context.request.method !== 'GET' && context.url.pathname !== '/api/stripe/webhook') {
        const key = `${context.clientAddress}:${context.url.pathname}`, now = Date.now();
        if (hits.size > 10000) for (const [k, v] of hits) if (v.until < now) hits.delete(k);
        const entry = hits.get(key);
        if (entry && entry.until > now) { if (++entry.count > 60) fail(429, 'RATE_LIMITED', '잠시 후 다시 시도하세요.'); }
        else hits.set(key, { count: 1, until: now + 60000 });
        if (hits.size > 10000) hits.delete(hits.keys().next().value);
      }
      response = await next();
    }
  } catch (error) { response = errorResponse(error, requestId); }
  response.headers.set('X-Request-Id', requestId);
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Cache-Control', 'no-store');
  response.headers.set('Vary', 'Origin');
  if (origin && (origin === config.cors || origin === new URL(config.site).origin)) {
    response.headers.set('Access-Control-Allow-Origin', origin);
    response.headers.set('Access-Control-Allow-Credentials', 'true');
    response.headers.set('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS');
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Request-Id');
  }
  console.info(JSON.stringify({ requestId, method: context.request.method, path: context.url.pathname, status: response.status, durationMs: Math.round(performance.now() - started) }));
  return response;
});
