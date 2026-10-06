import { expect, test } from '@playwright/test';

const tab = (page: import('@playwright/test').Page, name: string) =>
  page.getByRole('navigation', { name: 'Main' }).getByRole('link', { name });

test('tab re-taps: close the book, back to root, scroll to top, then reset', async ({ page }) => {
  // In a story: Reading is current; tapping it again closes the book.
  await page.goto('#/s/grimm--iron-hans');
  await expect(page.getByRole('heading', { level: 1, name: 'Iron Hans' })).toBeVisible();
  await expect(tab(page, 'Reading')).toHaveAttribute('aria-current', 'page');
  await tab(page, 'Reading').click();
  await expect(page.getByRole('heading', { level: 1, name: 'Reading' })).toBeVisible();

  // Inside the library (a collection): Library is current; tapping it goes back to the library.
  await page.goto('#/c/grimm');
  await expect(tab(page, 'Library')).toHaveAttribute('aria-current', 'page');
  await tab(page, 'Library').click();
  await expect(page.getByRole('heading', { name: 'Browse by' })).toBeVisible();

  // On the library, scrolled down with a search: first tap scrolls up, second clears.
  await page.getByRole('searchbox').fill('fox');
  await page.evaluate(() => window.scrollTo(0, 800));
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBeGreaterThan(300);
  await tab(page, 'Library').click();
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBe(0);
  await expect(page.getByRole('searchbox')).toHaveValue('fox');
  await tab(page, 'Library').click();
  await expect(page.getByRole('searchbox')).toHaveValue('');
});

test('finished stories reopen at the top; rereads resume', async ({ page }) => {
  await page.goto('#/s/aesop--the-heron');
  await page.getByRole('complementary', { name: 'Moral' }).scrollIntoViewIfNeeded();
  await page.waitForFunction(() => {
    const s = JSON.parse(localStorage.getItem('storybook:v1') ?? '{}');
    return s.progress?.['aesop--the-heron']?.finished === true;
  });
  await page.goto('#/');
  await page.goto('#/s/aesop--the-heron');
  await expect(page.getByRole('heading', { level: 1, name: 'The Heron' })).toBeVisible();
  await expect(page.getByRole('status', { name: 'Resumed' })).toHaveCount(0);
  expect(await page.evaluate(() => window.scrollY)).toBeLessThan(50);
});
