// @vitest-environment node
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { statSync } from 'node:fs';
import { OFFLINE_MB } from '../offline/download';
import imageSizes from './imageSizes.json';
import { indexSchema, storySchema, tagsSchema } from './schema';

const root = join(__dirname, '../../public/compendium');
const index = indexSchema.parse(JSON.parse(readFileSync(join(root, 'index.json'), 'utf8')));

const tags = tagsSchema.parse(JSON.parse(readFileSync(join(root, 'tags.json'), 'utf8')));

describe('compendium integrity', () => {
  it('tags exactly the stories in the index (run `python3 tools/tag_stories.py` if not)', () => {
    expect(Object.keys(tags.stories).sort()).toEqual(index.stories.map((s) => s.id).sort());
  });

  it('gives every story at least one known culture and one known theme', () => {
    const cultures = new Set(tags.cultures.map((c) => c.id));
    const themes = new Set(tags.themes.map((t) => t.id));
    for (const [id, t] of Object.entries(tags.stories)) {
      expect(t.cultures.length, id).toBeGreaterThan(0);
      expect(t.themes.length, id).toBeGreaterThan(0);
      for (const c of t.cultures) expect(cultures.has(c), `${id}: ${c}`).toBe(true);
      for (const th of t.themes) expect(themes.has(th), `${id}: ${th}`).toBe(true);
    }
  });

  it('uses every defined tag at least once', () => {
    const used = new Set(Object.values(tags.stories).flatMap((t) => [...t.cultures, ...t.themes]));
    for (const t of [...tags.cultures, ...tags.themes]) expect(used.has(t.id), t.id).toBe(true);
  });

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

// Text hygiene: regressions of the fixes in tools/fix_text.py (see docs/text-review.md).
describe('story text', () => {
  const stories = index.stories.map((e) =>
    storySchema.parse(JSON.parse(readFileSync(join(root, 'stories', `${e.id}.json`), 'utf8'))),
  );
  const offenders = (test: (text: string, type: string) => boolean) =>
    stories.flatMap((s) =>
      s.blocks
        .map((b, i) => [b, i] as const)
        .filter(([b]) => 'text' in b && test(b.text, b.type))
        .map(([b, i]) => `${s.id} [${i}]: ${'text' in b ? b.text.slice(0, 60) : ''}`),
    );

  it('has no footnote markers left in the body (footnotes are note blocks)', () => {
    expect(
      offenders(
        (t, type) => type !== 'note' && /\[\*\]|\[\d\]|[\w.,!?”’]\*(\s|$)|^\s*\*\s*\w/.test(t),
      ),
    ).toEqual([]);
  });

  it('has no words broken by line-wrap hyphenation ("Rose- red")', () => {
    expect(offenders((t) => /[A-Za-z]- [A-Za-z]/.test(t))).toEqual([]);
  });

  it('has no drop-cap capitals at the start of a paragraph ("THERE was once")', () => {
    expect(
      offenders(
        (t, type) =>
          (type === 'p' || type === 'verse') &&
          /^\s*[“‘"']?[A-Z]{2,}[\s,’']+[A-Za-z’']*[a-z]/.test(t),
      ),
    ).toEqual([]);
  });

  it('has no blank blocks or separator lines', () => {
    expect(offenders((t) => !t.trim() || (/^[-*_\s]{8,}$/.test(t) && !/\* \*/.test(t)))).toEqual(
      [],
    );
  });

  it('keeps short words lower case inside titles', () => {
    const small = /^(a|an|and|the|of|in|on|to|with|at|by|for|or)$/i;
    const bad = index.stories.filter((s) =>
      s.title
        .split(' ')
        .some(
          (w, i, ws) =>
            i > 0 &&
            small.test(w) &&
            /^[A-Z]/.test(w) &&
            !/[;:(]$|^or,$/.test(ws[i - 1]!) &&
            !/^A-/.test(w),
        ),
    );
    expect(bad.map((s) => s.title)).toEqual([]);
  });
});
