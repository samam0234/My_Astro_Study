import { performance } from 'node:perf_hooks';
const base = process.env.API_BASE_URL || 'http://127.0.0.1:4323';
for (const path of ['/', '/api/posts']) {
  const samples = [];
  for (let i = 0; i < 20; i++) {
    const started = performance.now(), response = await fetch(base + path);
    await response.text(); if (!response.ok) throw new Error(`HTTP ${response.status}`);
    samples.push(performance.now() - started);
  }
  samples.sort((a, b) => a - b);
  console.log(JSON.stringify({ path, samples: 20, medianMs: samples[10], p95Ms: samples[18] }));
}
