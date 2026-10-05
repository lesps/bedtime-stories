// Renders public/favicon.svg to the PNG icons the manifest needs, using Playwright's Chromium.
import { readFileSync } from 'node:fs';
import { chromium } from '@playwright/test';

const svg = readFileSync('public/favicon.svg', 'utf8');
const targets = [
  ['public/icon-192.png', 192, 0],
  ['public/icon-512.png', 512, 0],
  ['public/apple-touch-icon.png', 180, 0],
  // Maskable icons need the artwork inside the central 80% safe zone.
  ['public/icon-maskable-512.png', 512, 0.12],
];
const browser = await chromium.launch();
for (const [out, size, pad] of targets) {
  const page = await browser.newPage({ viewport: { width: size, height: size } });
  const inset = Math.round(size * pad);
  await page.setContent(
    `<body style="margin:0;background:#2b2140"><div style="padding:${inset}px;width:${size}px;height:${size}px;box-sizing:border-box">${svg.replace('<svg', `<svg width="${size - 2 * inset}" height="${size - 2 * inset}"`)}</div></body>`,
  );
  await page.screenshot({ path: out, omitBackground: false });
  console.log('wrote', out);
}
await browser.close();
