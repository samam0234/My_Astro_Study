import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
const transport = new StdioClientTransport({ command: process.execPath,
  args: [fileURLToPath(new URL('./mcp-server.mjs', import.meta.url))], env: { ...process.env, AI_MODE: 'mock' } });
const client = new Client({ name: 'astro-study-client', version: '1.0.0' });
try {
  await client.connect(transport);
  const tools = await client.listTools(); assert.ok(tools.tools.some(t => t.name === 'summarize_document'));
  const result = await client.callTool({ name: 'summarize_document', arguments: { text: 'Astro는 콘텐츠를 HTML로 만듭니다.' } });
  assert.equal(result.isError, undefined); console.log(JSON.stringify({ tools: tools.tools.map(t => t.name), result }));
} finally { await client.close(); }
