import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import mdx from '@astrojs/mdx';

export default defineConfig({
  site: process.env.SITE_URL || 'http://127.0.0.1:4323',
  adapter: node({ mode: 'standalone' }),
  integrations: [mdx()],
  server: { host: '127.0.0.1', port: 4323 },
});
