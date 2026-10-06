import { expect, test } from '@playwright/test';

test('Reading tab returns to the open story at its place; Close shows the shelf', async ({
  page,
}) => {
  await page.goto('#/s/grimm--iron-hans');
  await expect(page.getByRole('heading', { level: 1, name: 'Iron Hans' })).toBeVisible();
  await page.locator('[data-block="6"]').scrollIntoViewIfNeeded();
  await page.waitForFunction(() => {
    const s = JSON.parse(localStorage.getItem('storybook:v1') ?? '{}');
    return (s.progress?.['grimm--iron-hans']?.blockIndex ?? 0) >= 3;
  });

  await page.getByRole('link', { name: 'Library' }).click();
  await expect(page.getByRole('heading', { name: 'Browse by' })).toBeVisible();

  await page.getByRole('link', { name: 'Reading' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Iron Hans' })).toBeVisible();
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBeGreaterThan(500);
  await expect(page.getByRole('link', { name: 'Reading' })).toHaveAttribute('aria-current', 'page');

  await page.getByRole('button', { name: 'Close book' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Reading' })).toBeVisible();
  const hero = page.getByRole('region', { name: 'Pick up where you left off' });
  await expect(hero).toContainText('Iron Hans');
  await expect(hero).toContainText(/\d+% · about \d+ min left/);

  await hero.getByRole('link', { name: 'Keep reading' }).click();
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBeGreaterThan(500);
});

test('five tabs fit on a small phone', async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 640 });
  await page.goto('#/');
  const tabs = page.getByRole('navigation', { name: 'Main' }).getByRole('link');
  await expect(tabs).toHaveCount(5);
  for (const t of await tabs.all()) {
    const box = (await t.boundingBox())!;
    expect(box.width).toBeGreaterThanOrEqual(44);
    expect(box.x + box.width).toBeLessThanOrEqual(320);
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(320);
});
