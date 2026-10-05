import { expect, test } from '@playwright/test';

test('Give me 3 with a preset offers three distinct stories, then remembers them', async ({
  page,
}) => {
  await page.goto('#/surprise');
  await page.getByRole('button', { name: /Quick & gentle/ }).click();
  await page.getByRole('radio', { name: 'Give me 3' }).click();
  await page.getByRole('button', { name: 'Pick 3 stories' }).click();
  const cards = page.getByRole('region', { name: /^Choice \d$/ });
  await expect(cards).toHaveCount(3);
  const titles = await cards.locator('.pick-title').allTextContents();
  expect(new Set(titles).size).toBe(3);
  for (const t of await cards.allTextContents()) {
    expect(Number(t.match(/(\d+) min/)![1])).toBeLessThanOrEqual(5);
  }
  const recent = page.getByRole('list', { name: 'Recently picked' });
  await expect(recent.getByRole('link')).toHaveCount(3);
  await cards.first().getByRole('link', { name: 'Read it' }).click();
  await expect(page.getByRole('article')).toBeVisible();
});
