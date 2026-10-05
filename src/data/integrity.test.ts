// @vitest-environment node
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { statSync } from 'node:fs';
import { OFFLINE_MB } from '../offline/download';
import imageSizes from './imageSizes.json';
import { indexSchema, storySchema } from './schema';

const root = join(__dirname, '../../public/compendium');
const index = indexSchema.parse(JSON.parse(readFileSync(join(root, 'index.json'), 'utf8')));

describe('compendium integrity', () => {
  it('has unique story ids and at least one story per collection', () => {
    expect(new Set(index.stories.map((s) => s.id)).size).toBe(index.stories.length);
    for (const c of index.collections) expect(c.storyCount, c.id).toBeGreaterThan(0);
  });

  it('never shares a workId between two stories of one collection', () => {
    const seen = new Set<string>();
    for (const s of index.stories) {
      if (!s.workId) continue;
      const key = `${s.collectionId}|${s.workId}`;
      expect(seen.has(key), key).toBe(false);
      seen.add(key);
    }
  });

  it('advertises offline download sizes within 25% of the data on disk', () => {
    const mb = (dir: string): number =>
      readdirSync(dir, { withFileTypes: true }).reduce(
        (sum, d) =>
          sum + (d.isDirectory() ? mb(join(dir, d.name)) : statSync(join(dir, d.name)).size / 1e6),
        0,
      );
    for (const [k, advertised] of Object.entries(OFFLINE_MB)) {
      const actual = mb(join(root, k));
      expect(Math.abs(actual - advertised) / actual, `${k}: ${actual.toFixed(1)} MB`).toBeLessThan(
        0.25,
      );
    }
  });

  it('uses well-formed workIds', () => {
    for (const s of index.stories) if (s.workId) expect(s.workId).toMatch(/^[a-z]+(-[a-z0-9]+)+$/);
  });

  it('has no orphan story files', () => {
    const files = readdirSync(join(root, 'stories')).map((f) => f.replace(/\.json$/, ''));
    expect(files.sort()).toEqual(index.stories.map((s) => s.id).sort());
  });

  it('storyCount matches per collection, and every story belongs to a known collection', () => {
    const ids = new Set(index.collections.map((c) => c.id));
    for (const s of index.stories) expect(ids.has(s.collectionId)).toBe(true);
    for (const c of index.collections) {
      expect(index.stories.filter((s) => s.collectionId === c.id)).toHaveLength(c.storyCount);
    }
  });

  it('has a size for exactly the images on disk (run `npm run image-sizes` if not)', () => {
    const onDisk = readdirSync(join(root, 'images')).flatMap((d) =>
      readdirSync(join(root, 'images', d)).map((f) => `images/${d}/${f}`),
    );
    expect(Object.keys(imageSizes).sort()).toEqual(onDisk.sort());
  });

  it.each(index.stories.map((s) => [s.id, s] as const))(
    '%s matches its story file',
    (id, entry) => {
      const story = storySchema.parse(
        JSON.parse(readFileSync(join(root, 'stories', `${id}.json`), 'utf8')),
      );
      const { hasImages, ...fields } = entry;
      for (const [k, v] of Object.entries(fields)) {
        expect(story[k as keyof typeof story], k).toEqual(v);
      }
      expect(story.workId, 'workId in story file vs index').toEqual(entry.workId);
      const images = story.blocks.filter((b) => b.type === 'image');
      expect(images.length > 0).toBe(hasImages);
      for (const img of images) expect(existsSync(join(root, img.src)), img.src).toBe(true);
    },
  );
});
