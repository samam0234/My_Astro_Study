import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { mkdtemp, rm, readdir } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve, sep } from 'node:path';
import { once } from 'node:events';
import { WebSocket } from 'ws';
import { openStore } from '../src/lib/store.mjs';
import { signup, login } from '../src/lib/auth.mjs';
import { enqueueMail } from '../src/lib/jobs.mjs';

const directory = await mkdtemp(join(tmpdir(), 'astro-extensions-'));
assert.ok(resolve(directory).startsWith(resolve(tmpdir()) + sep) && directory.includes('astro-extensions-'));
const project = process.cwd(), base = 'http://127.0.0.1:4395';
const env = { ...process.env, SITE_URL: base, CORS_ORIGIN: base, PORT: '4395', HOST: '127.0.0.1', DB_DRIVER: 'sqlite', DATABASE_URL: join(directory, 'desk.sqlite'), AI_MODE: 'mock', INTEGRATIONS_MODE: 'mock', WS_PORT: '4396' };
const children = []; let store, socket; let logs = '';
function run(file, args = [], overrides = {}) {
  const child = spawn(process.execPath, [resolve(project, file), ...args], { env, stdio: ['ignore','pipe','pipe'], ...overrides });
  child.stdout.on('data', b => { logs += b; }); child.stderr.on('data', b => { logs += b; }); return child;
}
async function stopped(child) { if (child.exitCode !== null) return child.exitCode; const [code] = await once(child, 'exit'); return code; }
try {
  store = await openStore({ driver: 'sqlite', database: env.DATABASE_URL });
  const user = await signup(store, { email: 'extensions@example.com', nickname: '확장', password: 'study-password' });
  const session = await login(store, { email: user.email, password: 'study-password' });
  const job = await enqueueMail(store, user);
  assert.equal(await stopped(run('scripts/worker.mjs', ['--once'])), 0);
  assert.equal((await store.get('jobs', job.id)).status, 'done');
  const server = run('dist/server/entry.mjs'); children.push(server);
  let ready = false;
  for (let i=0;i<80;i++) { try { if ((await fetch(base+'/health')).ok) { ready=true; break; } } catch {} await new Promise(r=>setTimeout(r,100)); }
  assert.ok(ready,logs);
  const controller = new AbortController();
  const sse = await fetch(base+'/api/events', { headers: { Authorization: `Bearer ${session.accessToken}` }, signal: controller.signal });
  assert.equal(sse.headers.get('content-type'),'text/event-stream');
  const reader=sse.body.getReader(), decoder=new TextDecoder(); let stream='';
  const timeout=setTimeout(()=>controller.abort(),5000);
  while (!stream.includes('event: jobs')) { const part=await reader.read(); stream+=decoder.decode(part.value); }
  clearTimeout(timeout); await reader.cancel(); controller.abort(); assert.match(stream,/done/);
  const wsServer = run('scripts/socket.mjs'); children.push(wsServer);
  await new Promise(r=>setTimeout(r,500));
  socket = new WebSocket('ws://127.0.0.1:4396/events',{origin:base,headers:{Cookie:`desk_session=${session.accessToken}`}});
  const [message]=await once(socket,'message'); assert.equal(JSON.parse(message.toString()).type,'ready');
  socket.send('ping'); const [pong]=await once(socket,'message'); assert.equal(JSON.parse(pong.toString()).type,'pong');
  socket.close();
  const rejected = new WebSocket('ws://127.0.0.1:4396/events',{origin:base});
  const [error]=await once(rejected,'error'); assert.match(error.message,/401/);
  assert.equal(await stopped(run('scripts/backup.mjs', [], { cwd: directory })),0);
  const files=await readdir(join(directory,'data/backups'));assert.equal(files.length,1);
  const backupStore=await openStore({driver:'sqlite',database:join(directory,'data/backups',files[0])});
  assert.equal((await backupStore.list('users')).length,1);await backupStore.close();
  const midpointEnv={...env,PORT:'4397',SITE_URL:'http://127.0.0.1:4397',CORS_ORIGIN:'http://127.0.0.1:4397',COURSE_STAGE:'midpoint'};
  const midpoint=run('dist/server/entry.mjs',[],{env:midpointEnv});children.push(midpoint);
  for (let i=0;i<80;i++) { try { if ((await fetch(midpointEnv.SITE_URL+'/health')).ok) break; } catch {} await new Promise(r=>setTimeout(r,100)); }
  const disabled=await fetch(midpointEnv.SITE_URL+'/api/documents',{headers:{Authorization:`Bearer ${session.accessToken}`}});
  assert.equal(disabled.status,404);
  assert.equal((await fetch(midpointEnv.SITE_URL+'/api/posts')).status,200);
  console.log('worker 완료·SSE·WebSocket 인증/왕복/거절·SQLite 백업 복구·midpoint 제한 검증 통과');
} catch(error) { console.error(logs);throw error; }
finally {
  socket?.terminate();
  for (const child of children) { child.kill(); await stopped(child); }
  if(store) await store.close();
  await rm(directory,{recursive:true,force:true});
}
