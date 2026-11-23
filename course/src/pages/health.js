import { json } from '../lib/http.mjs';
import { getStore } from '../lib/store.mjs';
export const prerender = false;
export async function GET() {
  await (await getStore()).list('health');
  return json({ status: 'ok' }, 200, process.env.RELEASE_SHA ? { 'X-Release-Sha': process.env.RELEASE_SHA } : {});
}
