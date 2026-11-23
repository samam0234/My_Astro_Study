import { randomBytes, scrypt as scryptCallback, timingSafeEqual, createHash } from 'node:crypto';
import { promisify } from 'node:util';
import { fail } from './http.mjs';
import { duplicate } from './store.mjs';

const scrypt = promisify(scryptCallback);
export const digest = value => createHash('sha256').update(value).digest('hex');
export const publicUser = user => ({ id: user.id, email: user.email, nickname: user.nickname });
export async function hashPassword(password) {
  const salt = randomBytes(16).toString('hex');
  const key = await scrypt(password, salt, 64);
  return `${salt}:${key.toString('hex')}`;
}
export async function checkPassword(password, encoded) {
  if (!encoded?.includes(':')) return false;
  const [salt, hash] = encoded.split(':');
  const actual = await scrypt(password, salt, 64), expected = Buffer.from(hash, 'hex');
  return expected.length === actual.length && timingSafeEqual(expected, actual);
}
export async function signup(store, input) {
  try { return await store.create('users', { email: input.email, nickname: input.nickname, passwordHash: await hashPassword(input.password) }, `email:${input.email}`); }
  catch (error) { if (duplicate(error)) fail(409, 'EMAIL_TAKEN', '이미 등록된 이메일입니다.'); throw error; }
}
export async function issueSession(store, user) {
  const token = randomBytes(32).toString('base64url');
  await store.create('sessions', { userId: user.id, digest: digest(token), expiresAt: Date.now() + 3600000 });
  return { user: publicUser(user), accessToken: token };
}
export async function login(store, input) {
  const user = (await store.list('users')).find(u => u.email === input.email);
  // 없는 계정도 scrypt를 실행해 응답시간 차이를 줄인다.
  const encoded = user?.passwordHash || `${'0'.repeat(32)}:${'0'.repeat(128)}`;
  if (!(await checkPassword(input.password, encoded)) || !user) fail(401, 'INVALID_CREDENTIALS', '이메일 또는 비밀번호를 확인하세요.');
  return issueSession(store, user);
}
export async function authenticate(store, token) {
  if (!token || token.length > 128) return null;
  const session = (await store.list('sessions')).find(s => s.digest === digest(token) && s.expiresAt > Date.now());
  return session ? publicUser(await store.get('users', session.userId)) : null;
}
export function requireUser(user) { if (!user) fail(401, 'UNAUTHORIZED', '로그인이 필요합니다.'); return user; }
export function owned(record, user) {
  requireUser(user);
  if (!record) fail(404, 'NOT_FOUND', '자원이 없습니다.');
  if (record.authorId !== user.id) fail(403, 'FORBIDDEN', '작성자만 변경할 수 있습니다.');
  return record;
}
