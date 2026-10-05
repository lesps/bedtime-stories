import { expect, test, type Locator, type Page } from '@playwright/test';

/** Touch-drag a range thumb from its current value to `toIndex` (of 0..10 stops). */
async function dragThumb(page: Page, slider: Locator, toIndex: number) {
  const box = (await slider.boundingBox())!;
  const value = Number(await slider.inputValue());
  const thumb = 28;
  const xAt = (i: number) => box.x + thumb / 2 + ((box.width - thumb) * i) / 10;
  const y = box.y + box.height / 2;
  const cdp = await page.context().newCDPSession(page);
  const touch = (type: 'touchStart' | 'touchMove' | 'touchEnd', x: number) =>
    cdp.send('Input.dispatchTouchEvent', {
      type,
      touchPoints: type === 'touchEnd' ? [] : [{ x, y }],
    });
  await touch('touchStart', xAt(value));
  for (let s = 1; s <= 10; s++)
    await touch('touchMove', xAt(value) + ((xAt(toIndex) - xAt(value)) * s) / 10);
  await touch('touchEnd', xAt(toIndex));
}

test('touch-drag the length slider to pick only long stories', async ({ page }) => {
  await page.goto('#/surprise');
  const group = page.getByRole('group', { name: 'Length' });
  await expect(group).toContainText('Up to 5 min');

  await dragThumb(page, page.getByRole('slider', { name: 'Longest' }), 10);
  await expect(group).toContainText('Any length');
  await dragThumb(page, page.getByRole('slider', { name: 'Shortest' }), 6);
  await expect(group).toContainText('15 min or longer');

  await page.getByRole('button', { name: 'Pick a story' }).click();
  const card = page.getByRole('region', { name: 'Your story' });
  await expect(card).toBeVisible();
  const minutes = Number((await card.textContent())!.match(/(\d+) min/)![1]);
  expect(minutes).toBeGreaterThanOrEqual(15);

  // Choice persists across reload.
  await page.reload();
  await expect(page.getByRole('group', { name: 'Length' })).toContainText('15 min or longer');
});

test('handles that meet at 60+ can still be pulled apart', async ({ page }) => {
  await page.goto('#/surprise');
  const longest = page.getByRole('slider', { name: 'Longest' });
  const shortest = page.getByRole('slider', { name: 'Shortest' });
  await dragThumb(page, longest, 10);
  await dragThumb(page, shortest, 10);
  await expect(page.getByRole('group', { name: 'Length' })).toContainText('60 min or longer');
  await dragThumb(page, shortest, 7);
  await expect(page.getByRole('group', { name: 'Length' })).toContainText('20 min or longer');
});

test('keyboard: arrow keys move a handle one stop', async ({ page }) => {
  await page.goto('#/');
  await page.getByRole('slider', { name: 'Longest' }).focus();
  await page.keyboard.press('ArrowLeft');
  await expect(page.getByRole('group', { name: 'Length' })).toContainText('Up to 45 min');
  await expect(page.getByRole('list', { name: 'Results' })).toBeVisible();
});
