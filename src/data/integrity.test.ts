// @vitest-environment node
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { indexSchema, storySchema } from './schema';

const root = join(__dirname, '../../public/compendium');
const index = indexSchema.parse(JSON.parse(readFileSync(join(root, 'index.json'), 'utf8')));

describe('compendium integrity', () => {
  it('has 319 stories with unique ids', () => {
    expect(index.stories).toHaveLength(319);
    expect(new Set(index.stories.map((s) => s.id)).size).toBe(319);
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
      const images = story.blocks.filter((b) => b.type === 'image');
      expect(images.length > 0).toBe(hasImages);
      for (const img of images) expect(existsSync(join(root, img.src)), img.src).toBe(true);
    },
  );
});
