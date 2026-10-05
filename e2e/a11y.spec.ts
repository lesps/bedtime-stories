import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

const pages = [
  { name: 'Aesop fable (image + moral)', path: '#/s/aesop--the-heron', expect: '.moral' },
  {
    name: 'Kipling story (verse)',
    path: '#/s/kipling-justso--how-the-whale-got-his-throat',
    expect: '.verse',
  },
  { name: 'Library', path: '#/', expect: '.collection-card' },
  { name: 'Surprise', path: '#/surprise', expect: '.chip' },
  { name: 'Settings', path: '#/settings', expect: '.card' },
];

for (const theme of ['light', 'sepia', 'dark'] as const) {
  for (const p of pages) {
    test(`${p.name} has no serious a11y violations (${theme})`, async ({ page }) => {
      await page.addInitScript((t) => {
        localStorage.setItem(
          'storybook:v1',
          JSON.stringify({ version: 1, settings: { theme: t } }),
        );
      }, theme);
      await page.goto(p.path);
      await expect(page.locator(p.expect).first()).toBeVisible();
      await expect(page.locator('html')).toHaveAttribute('data-theme', theme);
      const { violations } = await new AxeBuilder({ page }).analyze();
      const serious = violations.filter((v) => v.impact === 'serious' || v.impact === 'critical');
      expect(
        serious,
        JSON.stringify(
          serious.map((v) => [v.id, v.nodes.map((n) => n.target)]),
          null,
          1,
        ),
      ).toEqual([]);
    });
  }
}

test('reader renders image and moral for an Aesop fable', async ({ page }) => {
  await page.goto('#/s/aesop--the-heron');
  await expect(page.getByRole('article')).toBeVisible();
  await expect(page.getByRole('img', { name: 'THE HERON' })).toBeVisible();
  await expect(page.getByRole('complementary', { name: 'Moral' })).toContainText(
    'Do not be too hard to suit',
  );
});

test('verse keeps its line breaks', async ({ page }) => {
  await page.goto('#/s/kipling-justso--how-the-whale-got-his-throat');
  const verse = page.locator('.verse').first();
  await expect(verse).toHaveCSS('white-space', 'pre-wrap');
  expect(await verse.textContent()).toContain('\n');
});
