// Scripted Lighthouse check: serves dist/ with `vite preview`, audits the library and an Aesop
// story on mobile settings, and fails if performance or accessibility drops below the target.
import { spawn } from 'node:child_process';
import { chromium } from '@playwright/test';
import * as chromeLauncher from 'chrome-launcher';
import lighthouse from 'lighthouse';

const TARGET = 90;
const PORT = 4175;
const BASE = `http://localhost:${PORT}/bedtime-stories/`;
const PAGES = { library: `${BASE}#/`, 'aesop story': `${BASE}#/s/aesop--the-heron` };

const server = spawn('npx', ['vite', 'preview', '--port', String(PORT), '--strictPort'], {
  stdio: 'ignore',
  detached: true,
});
const stop = () => {
  try {
    process.kill(-server.pid);
  } catch {
    /* already gone */
  }
};

let failed = false;
try {
  for (let i = 0; i < 50; i++) {
    if (
      await fetch(BASE).then(
        (r) => r.ok,
        () => false,
      )
    )
      break;
    await new Promise((r) => setTimeout(r, 200));
  }
  const chrome = await chromeLauncher.launch({
    chromePath: process.env.CHROME_PATH ?? chromium.executablePath(),
    chromeFlags: ['--headless=new', '--no-sandbox', '--disable-gpu'],
  });
  try {
    for (const [name, url] of Object.entries(PAGES)) {
      const { lhr } = await lighthouse(url, {
        port: chrome.port,
        onlyCategories: ['performance', 'accessibility'],
        logLevel: 'error',
      });
      const scores = Object.fromEntries(
        Object.entries(lhr.categories).map(([k, c]) => [k, Math.round((c.score ?? 0) * 100)]),
      );
      const ok = Object.values(scores).every((s) => s >= TARGET);
      failed ||= !ok;
      console.log(`${ok ? '✓' : '✗'} ${name}: ${JSON.stringify(scores)}`);
    }
  } finally {
    await chrome.kill();
  }
} finally {
  stop();
}
process.exit(failed ? 1 : 0);
