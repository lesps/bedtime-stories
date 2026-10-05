// Writes src/data/imageSizes.json: { "<src relative to compendium/>": [width, height] } for every
// JPEG or WebP in public/compendium/images, so the reader can reserve space and avoid layout shift.
// Re-run after regenerating the compendium; src/data/integrity.test.ts fails if it drifts.
import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

export function jpegSize(buf) {
  let i = 2;
  while (i < buf.length) {
    if (buf[i] !== 0xff) throw new Error('Bad JPEG marker');
    const marker = buf[i + 1];
    const len = buf.readUInt16BE(i + 2);
    // SOF0–SOF15 except DHT (C4), JPG (C8), DAC (CC)
    if (marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker)) {
      return [buf.readUInt16BE(i + 7), buf.readUInt16BE(i + 5)];
    }
    i += 2 + len;
  }
  throw new Error('No SOF marker');
}

export function webpSize(buf) {
  if (buf.toString('ascii', 0, 4) !== 'RIFF' || buf.toString('ascii', 8, 12) !== 'WEBP') {
    throw new Error('Not a WebP file');
  }
  const chunk = buf.toString('ascii', 12, 16);
  if (chunk === 'VP8 ') return [buf.readUInt16LE(26) & 0x3fff, buf.readUInt16LE(28) & 0x3fff];
  if (chunk === 'VP8L') {
    const b = buf.readUInt32LE(21);
    return [(b & 0x3fff) + 1, ((b >> 14) & 0x3fff) + 1];
  }
  if (chunk === 'VP8X') return [buf.readUIntLE(24, 3) + 1, buf.readUIntLE(27, 3) + 1];
  throw new Error(`Unknown WebP chunk ${chunk}`);
}

const sizeOf = (buf) => (buf[0] === 0xff && buf[1] === 0xd8 ? jpegSize(buf) : webpSize(buf));

const root = 'public/compendium';
const sizes = {};
for (const dir of readdirSync(join(root, 'images')).sort()) {
  for (const f of readdirSync(join(root, 'images', dir)).sort()) {
    sizes[`images/${dir}/${f}`] = sizeOf(readFileSync(join(root, 'images', dir, f)));
  }
}
writeFileSync('src/data/imageSizes.json', JSON.stringify(sizes, null, 1) + '\n');
console.log(`wrote ${Object.keys(sizes).length} sizes`);
