import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { complete } from '../src/lib/ai.mjs';

const server = new McpServer({ name: 'astro-document-tools', version: '1.0.0' });
server.registerTool('summarize_document', {
  description: '주어진 문서 텍스트를 근거와 함께 요약합니다. 파일·DB에는 접근하지 않습니다.',
  inputSchema: { text: z.string().min(1).max(6000) },
}, async ({ text }) => ({ content: [{ type: 'text', text: await complete(text, '') }] }));
await server.connect(new StdioServerTransport());
// stdout은 JSON-RPC 전용이다. 진단 로그는 stderr로만 쓴다.
