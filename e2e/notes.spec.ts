import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Page } from '@playwright/test';

async function selectWords(page: Page, block: number, words: string) {
  await page.evaluate(
    ([b, w]) => {
      const el = document.querySelector(`[data-block="${b}"]`)!;
      const node = document.createTreeWalker(el, NodeFilter.SHOW_TEXT).nextNode() as Text;
      const i = node.data.indexOf(w as string);
      const r = document.createRange();
      r.setStart(node, i);
      r.setEnd(node, i + (w as string).length);
      const s = getSelection()!;
      s.removeAllRanges();
      s.addRange(r);
    },
    [block, words] as const,
  );
}

test('highlight, note, story note, notebook and export on a phone', async ({ page }) => {
  await page.goto('#/s/aesop--the-heron');
  await expect(page.getByRole('complementary', { name: 'Moral' })).toBeVisible();

  // A real double-click word selection shows the toolbar below the selection, on screen.
  const para = page.locator('[data-block="1"]');
  // Near the top of the screen, so there's room for the toolbar below the selection.
  await page.evaluate(() => {
    const el = document.querySelector('[data-block="1"]')!;
    window.scrollBy(0, el.getBoundingClientRect().top - 120);
  });
  await para.dblclick({ position: { x: 30, y: 10 } });
  const bar = page.getByRole('toolbar', { name: 'Highlight' });
  await expect(bar).toBeVisible();
  const sel = await page.evaluate(() => {
    const r = getSelection()!.getRangeAt(0).getBoundingClientRect();
    return { bottom: r.bottom, text: getSelection()!.toString() };
  });
  const box = (await bar.boundingBox())!;
  const vp = page.viewportSize()!;
  expect(box.y).toBeGreaterThanOrEqual(sel.bottom);
  expect(box.x).toBeGreaterThanOrEqual(0);
  expect(box.x + box.width).toBeLessThanOrEqual(vp.width);
  await bar.getByRole('button', { name: 'Highlight green' }).click();
  const mark = page.locator('mark.hl[data-color="green"]');
  await expect(mark).toHaveText(sel.text.trim());

  // Multi-word selection → note.
  await selectWords(page, 2, 'No small fry for me');
  await page.getByRole('button', { name: 'Add note' }).click();
  const sheet = page.getByRole('dialog', { name: /Highlight: No small fry for me/ });
  await sheet.getByRole('textbox', { name: 'Note' }).fill('Ada did the Heron voice');
  await sheet.getByRole('button', { name: 'Done' }).click();
  await expect(page.locator('mark.hl[data-note]')).toHaveText('No small fry for me');

  // Persist across reload, then add a story note in the Notes panel.
  await page.reload();
  await expect(page.locator('mark.hl')).toHaveCount(2);
  await page.getByRole('button', { name: 'Notes' }).click();
  const panel = page.getByRole('dialog', { name: 'Notes' });
  await panel.getByRole('textbox', { name: 'Note on this story' }).fill('Bedtime favourite');
  await expect(panel.getByRole('button', { name: /No small fry/ })).toContainText(
    'Ada did the Heron voice',
  );
  await panel.getByRole('button', { name: 'Close' }).click();

  // Notebook on the shelf, and the export downloads Markdown.
  await page.getByRole('button', { name: 'Close book' }).click();
  const book = page.getByRole('list', { name: 'Notebook' });
  await expect(book).toContainText('The Heron');
  await expect(book).toContainText('2 highlights · 2 notes');
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.getByRole('button', { name: 'Export notes' }).click(),
  ]);
  expect(download.suggestedFilename()).toMatch(/^storybook-notes-\d{4}-\d{2}-\d{2}\.md$/);
});

for (const theme of ['light', 'sepia', 'dark'] as const) {
  test(`highlights, sheet and notes panel have no serious a11y violations (${theme})`, async ({
    page,
  }) => {
    await page.addInitScript((t) => {
      const h = (id: string, block: number, quote: string, color: string, note?: string) => ({
        id,
        block,
        start: 0,
        end: quote.length,
        quote,
        color,
        ...(note ? { note } : {}),
        createdAt: 1,
        updatedAt: 1,
      });
      localStorage.setItem(
        'storybook:v1',
        JSON.stringify({
          version: 1,
          settings: { theme: t },
          annotations: {
            'aesop--the-heron': [
              h('a', 1, 'A Heron', 'yellow'),
              h('b', 2, '“No small fry', 'green', 'voice'),
              h('c', 3, 'Now a fine', 'blue'),
              h('d', 6, 'Do not be too hard', 'pink'),
            ],
          },
        }),
      );
    }, theme);
    await page.goto('#/s/aesop--the-heron');
    await expect(page.locator('mark.hl')).not.toHaveCount(0);
    const check = async () => {
      const { violations } = await new AxeBuilder({ page }).analyze();
      const serious = violations.filter((v) => v.impact === 'serious' || v.impact === 'critical');
      expect(
        serious,
        JSON.stringify(serious.map((v) => [v.id, v.nodes.map((n) => n.target)])),
      ).toEqual([]);
    };
    await check();
    await page.locator('mark.hl').first().click();
    await expect(page.getByRole('dialog', { name: /Highlight/ })).toBeVisible();
    await check();
    await page.getByRole('button', { name: 'Done' }).click();
    await page.getByRole('button', { name: 'Notes' }).click();
    await expect(page.getByRole('dialog', { name: 'Notes' })).toBeVisible();
    await check();
  });
}

test('header fits on one row, and a low selection gets the toolbar above it', async ({ page }) => {
  await page.goto('#/s/aesop--the-heron');
  const close = (await page.getByRole('button', { name: 'Close book' }).boundingBox())!;
  const aa = (await page.getByRole('button', { name: 'Reading settings' }).boundingBox())!;
  expect(Math.abs(close.y - aa.y)).toBeLessThan(4);

  // Put block 3 near the bottom of the screen, just above the tab bar, and select in it.
  await page.evaluate(() => {
    const el = document.querySelector('[data-block="3"]')!;
    window.scrollBy(0, el.getBoundingClientRect().top - (innerHeight - 130));
  });
  await selectWords(page, 3, 'young Perch');
  const bar = page.getByRole('toolbar', { name: 'Highlight' });
  await expect(bar).toBeVisible();
  const sel = await page.evaluate(() => getSelection()!.getRangeAt(0).getBoundingClientRect().top);
  const box = (await bar.boundingBox())!;
  expect(box.y + box.height).toBeLessThanOrEqual(sel);
  const tabs = (await page.getByRole('navigation', { name: 'Main' }).boundingBox())!;
  expect(box.y + box.height).toBeLessThanOrEqual(tabs.y);
});
