import { getStore } from '../src/lib/store.mjs';
import { workOnce } from '../src/lib/jobs.mjs';
const store = await getStore();
let stopped = false;
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => { stopped = true; });
try {
  do {
    const worked = await workOnce(store);
    if (process.argv.includes('--once')) break;
    if (!worked) await new Promise(resolve => setTimeout(resolve, 1000));
  } while (!stopped);
} finally { await store.close(); }
