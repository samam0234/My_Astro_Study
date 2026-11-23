import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests/browser', workers: 1,
  use: { baseURL: 'http://127.0.0.1:4394', browserName: 'chromium', headless: true },
  webServer: { command: 'node scripts/test-server.mjs', url: 'http://127.0.0.1:4394/health', reuseExistingServer: false },
});
