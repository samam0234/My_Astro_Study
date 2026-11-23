import { fail } from './http.mjs';
import { owned, requireUser } from './auth.mjs';
import { postSchema, validate, listQuery } from './validation.mjs';

export async function serializePost(store, post) {
  if (!post) fail(404, 'NOT_FOUND', '글이 없습니다.');
  const author = await store.get('users', post.authorId);
  const comments = (await store.list('comments')).filter(c => c.postId === post.id);
  return { id: post.id, title: post.title, body: post.body, tags: post.tags,
    author: { id: author.id, nickname: author.nickname }, commentCount: comments.length,
    createdAt: post.createdAt, updatedAt: post.updatedAt };
}
export async function listPosts(store, url) {
  const { page, limit, q, sort } = listQuery(url), needle = q.toLowerCase();
  const posts = (await store.list('posts')).filter(p => `${p.title} ${p.body}`.toLowerCase().includes(needle));
  const data = await Promise.all(posts.map(post => serializePost(store, post)));
  data.sort((a, b) => sort === '-commentCount' ? b.commentCount - a.commentCount || b.id - a.id : (sort === 'createdAt' ? 1 : -1) * (a.createdAt.localeCompare(b.createdAt) || a.id - b.id));
  return { data: data.slice((page - 1) * limit, page * limit), meta: { page, limit, total: data.length, totalPages: Math.ceil(data.length / limit), q } };
}
export async function createPost(store, user, input) {
  requireUser(user);
  const values = validate(postSchema, input), now = new Date().toISOString();
  return serializePost(store, await store.create('posts', { ...values, authorId: user.id, createdAt: now, updatedAt: now }));
}
export async function updatePost(store, user, id, input) {
  const old = owned(await store.get('posts', id), user);
  const patch = validate(postSchema.partial().extend({ tags: postSchema.shape.tags.unwrap().optional() }), input);
  if (!Object.keys(patch).length) fail(400, 'VALIDATION_ERROR', '수정할 필드가 필요합니다.');
  const next = { ...old, ...patch, updatedAt: new Date().toISOString() };
  await store.replace('posts', id, next); return serializePost(store, next);
}
export async function deletePost(store, user, id) {
  owned(await store.get('posts', id), user);
  // 학습용 단일 인스턴스. 운영에서는 FK cascade/트랜잭션으로 이 경계를 묶는다.
  for (const c of await store.list('comments')) if (c.postId === id) await store.remove('comments', c.id);
  await store.remove('posts', id);
}
