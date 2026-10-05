// @vitest-environment node
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { indexSchema, storySchema } from './schema';

const root = join(__dirname, '../../public/compendium');
const story = (id: string) =>
  storySchema.parse(JSON.parse(readFileSync(join(root, 'stories', `${id}.json`), 'utf8')));

describe('schema additions from compendium patches 001–003', () => {
  it('validates a Potter story with its per-book source and first-publication year', () => {
    const s = story('potter--the-tale-of-peter-rabbit');
    expect(s.firstPublished).toBe(1902);
    expect(s.source).toMatch(/^https:\/\/www\.gutenberg\.org\//);
  });

  it('validates a Hunt story with workId and originalTitle', () => {
    const s = story('grimm-hunt--hansel-and-grethel');
    expect(s.workId).toBe('grimm-khm-015');
    expect(s.originalTitle).toBeTruthy();
  });

  it('validates Max and Maurice (verse and woodcuts)', () => {
    const s = story('busch-max-maurice--max-and-maurice');
    expect(s.blocks.some((b) => b.type === 'verse')).toBe(true);
    expect(s.blocks.some((b) => b.type === 'image')).toBe(true);
  });

  it('requires language and originalLanguage on collections, and knows the new flag', () => {
    const index = indexSchema.parse(JSON.parse(readFileSync(join(root, 'index.json'), 'utf8')));
    expect(
      index.collections.every((c) => c.language === 'en' && /^[a-z]{2}$/.test(c.originalLanguage)),
    ).toBe(true);
    expect(index.stories.some((s) => s.flags.includes('antisemitic-caricature'))).toBe(true);
    const bad = {
      ...index,
      collections: [{ ...index.collections[0], originalLanguage: undefined }],
    };
    expect(indexSchema.safeParse(bad).success).toBe(false);
  });
});
