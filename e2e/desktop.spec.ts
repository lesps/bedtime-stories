import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Page } from '@playwright/test';

test.use({
  viewport: { width: 1280, height: 800 },
  isMobile: false,
  hasTouch: false,
  deviceScaleFactor: 1,
});

const nav = (page: Page) => page.getByRole('navigation', { name: 'Main' });

test('the tab bar is a sidebar and content sits beside it, at every desktop width', async ({
  page,
}) => {
  for (const width of [1024, 1280, 1920]) {
    await page.setViewportSize({ width, height: 800 });
    await page.goto('#/c/grimm');
    await expect(page.locator('.story-row').first()).toBeVisible();
    const bar = (await nav(page).boundingBox())!;
    expect(bar.x).toBe(0);
    expect(bar.height).toBe(800);
    const list = (await page.getByRole('list', { name: /Stories in/ }).boundingBox())!;
    expect(list.x).toBeGreaterThanOrEqual(bar.width);
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
      width,
    );
  }
});

test('with a mouse, hovering a story row offers Mark read', async ({ page }) => {
  await page.goto('#/c/aesop');
  const row = page.locator('.story-row').first();
  const action = row.getByRole('button', { name: /^Mark .* read$/ });
  await expect(action).toHaveCSS('opacity', '0');
  await row.hover();
  await expect(action).toHaveCSS('opacity', '1');
  await action.click();
  await expect(row).toContainText('read');
});

test('notes dock on the right and close on Escape', async ({ page }) => {
  await page.goto('#/s/aesop--the-heron?notes=1');
  const notes = page.getByRole('dialog', { name: 'Notes' });
  const box = (await notes.boundingBox())!;
  expect(Math.round(box.x + box.width)).toBe(1280);
  expect(box.height).toBe(800);
  await page.keyboard.press('Escape');
  await expect(notes).toHaveCount(0);
});

test('an illustration fits on screen', async ({ page }) => {
  await page.goto('#/s/aesop--the-fox-and-the-grapes');
  const img = page.locator('figure img').first();
  await expect(img).toBeVisible();
  expect((await img.boundingBox())!.height).toBeLessThanOrEqual(800 * 0.7 + 1);
});

for (const path of ['#/', '#/c/aesop', '#/s/aesop--the-heron', '#/settings', '#/reading']) {
  test(`${path} has no serious a11y violations on desktop`, async ({ page }) => {
    await page.goto(path);
    await expect(page.locator('h1').first()).toBeVisible();
    const { violations } = await new AxeBuilder({ page }).analyze();
    const serious = violations.filter((v) => v.impact === 'serious' || v.impact === 'critical');
    expect(
      serious,
      JSON.stringify(serious.map((v) => [v.id, v.nodes.map((n) => n.target)])),
    ).toEqual([]);
  });
}
