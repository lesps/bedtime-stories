import { expect, test } from '@playwright/test';

test('search → read → favorite → reload → resume → surprise', async ({ page }) => {
  await page.goto('./');
  await page.getByRole('searchbox', { name: 'Search titles' }).fill('iron hans');
  await page.getByRole('link', { name: /Iron Hans/ }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Iron Hans' })).toBeVisible();

  await page.getByRole('button', { name: 'Favorite Iron Hans' }).click();
  await expect(page.getByRole('button', { name: 'Favorite Iron Hans' })).toHaveAttribute(
    'aria-pressed',
    'true',
  );

  // Read a while: scroll a third of the way down and let the throttled write land.
  await page.locator('[data-block="6"]').scrollIntoViewIfNeeded();
  await page.waitForFunction(() => {
    const s = JSON.parse(localStorage.getItem('storybook:v1') ?? '{}');
    return (s.progress?.['grimm--iron-hans']?.blockIndex ?? 0) >= 3;
  });

  await page.reload();
  await expect(page.getByRole('button', { name: 'Favorite Iron Hans' })).toHaveAttribute(
    'aria-pressed',
    'true',
  );
  // Reopening jumps straight back to the saved place and says so.
  await expect(page.getByRole('status', { name: 'Resumed' })).toContainText(
    'Picked up where you left off',
  );
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBeGreaterThan(500);

  await page.getByRole('link', { name: 'Library' }).click();
  await expect(page.getByRole('list', { name: 'Continue reading' })).toContainText('Iron Hans');

  await page.getByRole('link', { name: 'Favorites' }).click();
  await expect(page.getByRole('list', { name: 'Favorites' })).toContainText('Iron Hans');

  await page.getByRole('link', { name: 'Surprise' }).click();
  await page.getByRole('button', { name: 'Pick a story' }).click();
  const card = page.getByRole('region', { name: 'Your story' });
  await expect(card).toBeVisible();
  await expect(card).toContainText(/\d+ min/);
  await card.getByRole('link', { name: 'Read it' }).click();
  await expect(page.getByRole('article')).toBeVisible();
});

test('reader settings survive reload and dark mode follows the OS', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.goto('#/s/aesop--the-heron');
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await page.emulateMedia({ colorScheme: 'light' });
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'sepia');

  await page.getByRole('button', { name: 'Reading settings' }).click();
  await page.getByRole('radio', { name: 'Light' }).click();
  await page.getByRole('button', { name: 'Larger text' }).click();
  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
  await expect(page.locator('meta[name="theme-color"]')).toHaveAttribute('content', '#ffffff');
  await expect(page.getByRole('article')).toHaveCSS('font-size', '22px');
});

test('corrupt storage cannot crash the app', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('storybook:v1', '{oops'));
  await page.goto('./');
  await expect(page.getByRole('heading', { name: 'Browse by' })).toBeVisible();
});
