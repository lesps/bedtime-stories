import { spawn, type ChildProcess } from 'node:child_process';
import { expect, test, type BrowserContext } from '@playwright/test';

// Chromium's offline emulation doesn't reach service-worker fetches, so each test gets its own
// preview server and "going offline" really means killing it (plus emulation for navigator.onLine).
const PORT = 4174;
const BASE = `http://localhost:${PORT}/bedtime-stories/`;
let server: ChildProcess | null = null;

test.use({ baseURL: BASE });
test.describe.configure({ mode: 'serial' });

test.beforeEach(async () => {
  server = spawn('npx', ['vite', 'preview', '--port', String(PORT), '--strictPort'], {
    stdio: 'ignore',
    detached: true,
  });
  await expect
    .poll(
      () =>
        fetch(BASE).then(
          (r) => r.ok,
          () => false,
        ),
      { timeout: 15_000 },
    )
    .toBe(true);
});

test.afterEach(() => stopServer());

function stopServer() {
  if (server?.pid) {
    try {
      process.kill(-server.pid);
    } catch {
      /* already gone */
    }
  }
  server = null;
}

async function goOffline(context: BrowserContext) {
  stopServer();
  await expect
    .poll(() =>
      fetch(BASE).then(
        () => true,
        () => false,
      ),
    )
    .toBe(false);
  await context.setOffline(true);
}

test('works offline for cached stories and explains uncached ones', async ({ page, context }) => {
  await page.goto('./');
  await page.evaluate(() => navigator.serviceWorker.ready);
  // First load isn't controlled by the new worker; reload so fetches go through it.
  await page.reload();
  await expect.poll(() => page.evaluate(() => !!navigator.serviceWorker.controller)).toBe(true);

  await page.goto('#/s/aesop--the-heron');
  await expect(page.getByRole('complementary', { name: 'Moral' })).toBeVisible();
  await expect(page.getByRole('img', { name: 'THE HERON' })).toBeVisible();
  await expect
    .poll(() => page.evaluate(async () => (await (await caches.open('stories')).keys()).length))
    .toBeGreaterThan(0);

  await goOffline(context);
  await page.goto('./');
  await page.reload();
  await expect(page.getByText('You’re offline')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Collections' })).toBeVisible();

  await page.goto('#/s/aesop--the-heron');
  await expect(page.getByRole('complementary', { name: 'Moral' })).toBeVisible();

  await page.goto('#/s/grimm--iron-hans');
  await expect(page.getByText('This story isn’t saved for offline reading yet.')).toBeVisible();
});

test('"Make all stories available offline" downloads everything', async ({ page, context }) => {
  test.setTimeout(90_000);
  await page.goto('#/settings');
  await page.evaluate(() => navigator.serviceWorker.ready);
  await page.reload();
  await page.getByRole('button', { name: /Make all stories available offline/ }).click();
  await expect(page.getByText(/All \d+ stories and \d+ illustrations are saved/)).toBeVisible({
    timeout: 60_000,
  });
  await expect(page.getByText(/(\d+) of \1 saved on this device/)).toBeVisible();

  await goOffline(context);
  await page.goto('#/s/grimm--iron-hans');
  await expect(page.getByRole('heading', { level: 1, name: 'Iron Hans' })).toBeVisible();
  await expect(page.locator('[data-block="0"]')).toBeVisible();
});
