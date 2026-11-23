import { z } from 'zod';
import { fail } from './http.mjs';

export const postSchema = z.object({
  title: z.string().trim().min(1).max(200),
  body: z.string().trim().min(1).max(20000),
  tags: z.array(z.string().trim().min(1).max(30)).max(10).default([]),
}).strict();
export const signupSchema = z.object({
  email: z.email().max(254).transform(value => value.toLowerCase()),
  password: z.string().min(10).max(128), nickname: z.string().trim().min(1).max(40),
}).strict();
export const loginSchema = signupSchema.pick({ email: true, password: true });
export function validate(schema, input) {
  const result = schema.safeParse(input);
  if (!result.success) {
    const fields = {};
    for (const issue of result.error.issues) (fields[issue.path.join('.') || '_form'] ??= []).push(issue.message);
    fail(400, 'VALIDATION_ERROR', '입력값을 확인하세요.', fields);
  }
  return result.data;
}
export function listQuery(url) {
  const pageText = url.searchParams.get('page') ?? '1';
  const limitText = url.searchParams.get('limit') ?? '10';
  if (!/^\d+$/.test(pageText) || !/^\d+$/.test(limitText)) fail(400, 'VALIDATION_ERROR', 'page와 limit은 정수입니다.');
  const page = Number(pageText), limit = Math.min(50, Number(limitText));
  const sort = url.searchParams.get('sort') || '-createdAt';
  if (!Number.isSafeInteger(page) || page < 1 || limit < 1 || !Number.isSafeInteger(Number(limitText)) || !['createdAt', '-createdAt', '-commentCount'].includes(sort)) fail(400, 'VALIDATION_ERROR', '페이지 또는 정렬을 확인하세요.');
  return { page, limit, sort, q: (url.searchParams.get('q') || '').slice(0, 200) };
}
