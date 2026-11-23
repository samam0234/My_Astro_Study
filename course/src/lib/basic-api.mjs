import { z } from 'zod';
import { body, fail, json, positiveId } from './http.mjs';
import { signupSchema, loginSchema, validate } from './validation.mjs';
import { signup, login, publicUser, requireUser, owned, digest } from './auth.mjs';
import { listPosts, serializePost, createPost, updatePost, deletePost } from './posts.mjs';
import { postCache } from './cache.mjs';
import { settings } from './config.mjs';

export function sessionCookie(context, token) {
  context.cookies.set('desk_session', token, { path: '/', httpOnly: true, sameSite: 'lax', secure: settings().site.startsWith('https:'), maxAge: 3600 });
}
export async function dispatchBasic(context, store) {
  const { request, url, locals } = context, method = request.method;
  const path = url.pathname.replace(/\/$/, ''), user = locals.user;
  if (path === '/api/auth/signup' && method === 'POST') {
    const created = await signup(store, validate(signupSchema, await body(request)));
    return json({ data: publicUser(created) }, 201);
  }
  if (path === '/api/auth/login' && method === 'POST') {
    const data = await login(store, validate(loginSchema, await body(request)));
    sessionCookie(context, data.accessToken); return json({ data });
  }
  if (path === '/api/auth/me' && method === 'GET') return json({ data: requireUser(user) });
  if (path === '/api/auth/logout' && method === 'POST') {
    requireUser(user);
    for (const session of await store.list('sessions')) if (session.digest === digest(locals.token)) await store.remove('sessions', session.id);
    context.cookies.delete('desk_session', { path: '/' }); return new Response(null, { status: 204 });
  }
  if (path === '/api/posts') {
    if (method === 'GET') return json(process.env.COURSE_STAGE === 'midpoint' ? await listPosts(store, url) : await postCache.get(url.search, () => listPosts(store, url)));
    if (method === 'POST') {
      const data = await createPost(store, user, await body(request)); postCache.clear();
      return json({ data }, 201, { Location: `/api/posts/${data.id}` });
    }
    fail(405, 'METHOD_NOT_ALLOWED', 'GET 또는 POST를 사용하세요.');
  }
  let match = path.match(/^\/api\/posts\/([^/]+)$/);
  if (match) {
    const id = positiveId(match[1]);
    if (method === 'GET') return json({ data: await serializePost(store, await store.get('posts', id)) });
    if (method === 'PATCH') { const data = await updatePost(store, user, id, await body(request)); postCache.clear(); return json({ data }); }
    if (method === 'DELETE') { await deletePost(store, user, id); postCache.clear(); return new Response(null, { status: 204 }); }
    fail(405, 'METHOD_NOT_ALLOWED', 'GET/PATCH/DELETE를 사용하세요.');
  }
  match = path.match(/^\/api\/posts\/([^/]+)\/comments$/);
  if (match) {
    const postId = positiveId(match[1]);
    if (!(await store.get('posts', postId))) fail(404, 'NOT_FOUND', '글이 없습니다.');
    if (method === 'GET') {
      const comments = (await store.list('comments')).filter(c => c.postId === postId);
      const data = await Promise.all(comments.map(async c => ({ id: c.id, body: c.body, postId, createdAt: c.createdAt,
        author: { id: c.authorId, nickname: (await store.get('users', c.authorId)).nickname } })));
      return json({ data });
    }
    if (method === 'POST') {
      requireUser(user);
      const input = validate(z.object({ body: z.string().trim().min(1).max(2000) }).strict(), await body(request));
      const c = await store.create('comments', { ...input, postId, authorId: user.id, createdAt: new Date().toISOString() });
      postCache.clear();
      return json({ data: { id: c.id, body: c.body, postId, author: { id: user.id, nickname: user.nickname }, createdAt: c.createdAt } }, 201);
    }
  }
  match = path.match(/^\/api\/comments\/([^/]+)$/);
  if (match && method === 'DELETE') {
    const id = positiveId(match[1]); owned(await store.get('comments', id), user);
    await store.remove('comments', id); postCache.clear(); return new Response(null, { status: 204 });
  }
  return null;
}
