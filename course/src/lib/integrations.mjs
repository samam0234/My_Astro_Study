import { randomBytes, createHash } from 'node:crypto';
import { fail } from './http.mjs';
import { signup, issueSession } from './auth.mjs';
import { duplicate } from './store.mjs';

export async function sendMail(user, env = process.env, fetcher = fetch, key) {
  if ((env.INTEGRATIONS_MODE || 'mock') === 'mock') return { mode: 'mock', to: user.email, delivered: false };
  if (!env.RESEND_API_KEY || !env.MAIL_FROM) fail(503, 'SERVICE_UNAVAILABLE', '메일 설정이 필요합니다.');
  const response = await fetcher('https://api.resend.com/emails', { method: 'POST',
    headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json', ...(key ? { 'Idempotency-Key': key } : {}) },
    body: JSON.stringify({ from: env.MAIL_FROM, to: [user.email], subject: 'Astro 학습 알림', text: '학습 메모가 준비되었습니다.' }), signal: AbortSignal.timeout(10000) });
  if (!response.ok) fail(502, 'MAIL_UPSTREAM', '메일 전송 실패');
  return { mode: 'live', ...(await response.json()) };
}
export async function checkout(user, site, env = process.env, idempotencyKey) {
  if ((env.INTEGRATIONS_MODE || 'mock') === 'mock') return { mode: 'mock', url: `${site}/services?checkout=mock`, paid: false };
  if (!env.STRIPE_SECRET_KEY?.startsWith('sk_test_') || !env.STRIPE_PRICE_ID) fail(503, 'SERVICE_UNAVAILABLE', 'Stripe 테스트 키와 가격 ID가 필요합니다.');
  const { default: Stripe } = await import('stripe');
  const stripe = new Stripe(env.STRIPE_SECRET_KEY);
  const session = await stripe.checkout.sessions.create({ mode: 'payment', line_items: [{ price: env.STRIPE_PRICE_ID, quantity: 1 }],
    client_reference_id: String(user.id), success_url: `${site}/services?checkout=success`, cancel_url: `${site}/services?checkout=cancel` }, { idempotencyKey });
  return { mode: 'test', url: session.url };
}
export async function stripeWebhook(store, raw, signature, env = process.env) {
  if (!env.STRIPE_WEBHOOK_SECRET) fail(503, 'SERVICE_UNAVAILABLE', '웹훅 설정이 필요합니다.');
  const { default: Stripe } = await import('stripe');
  let event;
  try { event = new Stripe(env.STRIPE_SECRET_KEY).webhooks.constructEvent(raw, signature, env.STRIPE_WEBHOOK_SECRET); }
  catch { fail(400, 'BAD_REQUEST', '웹훅 서명이 올바르지 않습니다.'); }
  try { await store.create('paymentEvents', { eventId: event.id, type: event.type, paid: event.data.object.payment_status === 'paid', userId: event.data.object.client_reference_id, createdAt: new Date().toISOString() }, `stripe:${event.id}`); }
  catch (error) { if (!duplicate(error)) throw error; }
  return { received: true };
}
export function oauthStart(cookies, site, env = process.env) {
  if (!env.GITHUB_CLIENT_ID || !env.GITHUB_CLIENT_SECRET) fail(503, 'SERVICE_UNAVAILABLE', 'GitHub OAuth 앱을 설정하세요.');
  const state = randomBytes(32).toString('base64url'), verifier = randomBytes(32).toString('base64url');
  const options = { path: '/api/oauth', httpOnly: true, sameSite: 'lax', secure: site.startsWith('https:'), maxAge: 600 };
  cookies.set('oauth_state', state, options); cookies.set('oauth_verifier', verifier, options);
  const url = new URL('https://github.com/login/oauth/authorize');
  url.search = new URLSearchParams({ client_id: env.GITHUB_CLIENT_ID, redirect_uri: `${site}/api/oauth/callback`, state, scope: 'read:user',
    code_challenge: createHash('sha256').update(verifier).digest('base64url'), code_challenge_method: 'S256' }).toString();
  return Response.redirect(url, 302);
}
export async function oauthCallback(store, context, site, env = process.env, fetcher = fetch) {
  const state = context.cookies.get('oauth_state')?.value, verifier = context.cookies.get('oauth_verifier')?.value;
  context.cookies.delete('oauth_state', { path: '/api/oauth' }); context.cookies.delete('oauth_verifier', { path: '/api/oauth' });
  if (!state || state !== context.url.searchParams.get('state') || !verifier || !context.url.searchParams.get('code')) fail(400, 'BAD_REQUEST', 'OAuth state가 일치하지 않습니다.');
  const response = await fetcher('https://github.com/login/oauth/access_token', { method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ client_id: env.GITHUB_CLIENT_ID, client_secret: env.GITHUB_CLIENT_SECRET, code: context.url.searchParams.get('code'), code_verifier: verifier, redirect_uri: `${site}/api/oauth/callback` }), signal: AbortSignal.timeout(10000) });
  const result = await response.json();
  if (!response.ok || !result.access_token) fail(502, 'OAUTH_UPSTREAM', 'OAuth 토큰 교환 실패');
  const profile = await fetcher('https://api.github.com/user', { headers: { Authorization: `Bearer ${result.access_token}`, 'User-Agent': 'astro-study-desk' }, signal: AbortSignal.timeout(10000) });
  const info = await profile.json();
  if (!profile.ok || !Number.isSafeInteger(info.id)) fail(502, 'OAUTH_UPSTREAM', 'OAuth 사용자 조회 실패');
  // 이메일 자동 병합은 하지 않는다. 검증되지 않은 이메일로 기존 계정을 탈취할 수 있다.
  const email = `github-${info.id}@oauth.invalid`;
  let user = (await store.list('users')).find(u => u.email === email);
  if (!user) user = await signup(store, { email, nickname: String(info.login).slice(0, 40), password: randomBytes(48).toString('hex') });
  return issueSession(store, user);
}
