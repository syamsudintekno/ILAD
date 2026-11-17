import { defineConfig } from '@playwright/test';

const baseURL = 'http://127.0.0.1:5173';

export default defineConfig({
  testDir: './e2e',
  use: { baseURL, browserName: 'chromium' },
  webServer: {
    command: 'node node_modules/vite/bin/vite.js --mode emulator --host 127.0.0.1 --port 5173 --strictPort',
    url: baseURL,
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
