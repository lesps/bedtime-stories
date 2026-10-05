import { expect, test, type Page } from '@playwright/test';

/** Real touch swipe via CDP (Playwright's touchscreen API only taps). */
async function touchSwipe(page: Page, selector: string, dx: number) {
  await page.locator(selector).scrollIntoViewIfNeeded();
  const box = (await page.locator(selector).boundingBox())!;
  const y = box.y + box.height / 2;
  const x0 = box.x + box.width - 40;
  const cdp = await page.context().newCDPSession(page);
  const touch = (type: 'touchStart' | 'touchMove' | 'touchEnd', x: number) =>
    cdp.send('Input.dispatchTouchEvent', {
      type,
      touchPoints: type === 'touchEnd' ? [] : [{ x, y }],
    });
  await touch('touchStart', x0);
  for (let i = 1; i <= 8; i++) await touch('touchMove', x0 + (dx * i) / 8);
  await touch('touchEnd', x0 + dx);
}

test('swipe a read story to mark it unread', async ({ page }) => {
  await page.addInitScript(() => {
    if (localStorage.getItem('storybook:v1')) return;
    localStorage.setItem(
      'storybook:v1',
      JSON.stringify({ version: 1, history: [{ id: 'aesop--the-heron', readAt: 1 }] }),
    );
  });
  await page.goto('#/c/aesop');
  const row = page.locator('li', { has: page.getByText('The Heron', { exact: true }) });
  await expect(row).toContainText('read');

  await touchSwipe(page, 'li[data-open]:has(.story-title:text-is("The Heron")) .row-content', -150);
  await expect(row).toHaveAttribute('data-open', 'true');
  await expect(
    page.getByRole('heading', { level: 1, name: 'The Aesop for Children' }),
  ).toBeVisible();

  await row.getByRole('button', { name: 'Mark The Heron unread' }).click();
  await expect(row).not.toContainText(/·\s*read/);
  await page.reload();
  await expect(row).not.toContainText(/·\s*read/);
});
