import { sendMail } from './integrations.mjs';

export async function enqueueMail(store, user) {
  return store.create('jobs', { type: 'mail', userId: user.id, status: 'queued', attempts: 0, nextAt: 0, createdAt: new Date().toISOString() });
}
export async function workOnce(store, deliver = sendMail) {
  // 단일 worker 전용. 다중 worker는 원자적 claim + lease가 필요하다.
  const job = (await store.list('jobs')).find(j => j.status === 'queued' && j.nextAt <= Date.now());
  if (!job) return false;
  const next = { ...job, attempts: job.attempts + 1 };
  try {
    await deliver(await store.get('users', job.userId), process.env, fetch, `job-${job.id}`);
    Object.assign(next, { status: 'done', finishedAt: new Date().toISOString() });
  } catch {
    Object.assign(next, { status: next.attempts >= 3 ? 'failed' : 'queued', nextAt: Date.now() + 1000 * 2 ** next.attempts });
  }
  await store.replace('jobs', job.id, next); return true;
}
