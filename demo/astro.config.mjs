// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  site: 'http://127.0.0.1:4321',
  server: {
    host: '127.0.0.1',
    port: 4321,
  },
});
