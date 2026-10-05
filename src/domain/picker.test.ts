import { describe, expect, it } from 'vitest';
import { entry, mulberry32 } from '../test/fixtures';
import { pick, pickMany, type PickContext } from './picker';

const pool = [
  entry({ id: 'aesop--a', readingMinutes: 1 }),
  entry({ id: 'aesop--b', readingMinutes: 3 }),
  entry({ id: 'grimm--c', readingMinutes: 8 }),
  entry({ id: 'grimm--d', readingMinutes: 20 }),
  entry({ id: 'grimm--mature', readingMinutes: 2, flags: ['mature-themes'] }),
  entry({ id: 'aesop--excluded', readingMinutes: 2, excluded: true }),
];
const ctx: PickContext = {
  visibility: { showMature: false, showExcluded: false },
  readIds: new Set(['aesop--a']),
  favoriteIds: new Set(['grimm--c', 'aesop--b']),
};

const ids = (opts: Parameters<typeof pick>[1], n = 300, c = ctx) => {
  const rng = mulberry32(42);
  const seen = new Set<string>();
  for (let i = 0; i < n; i++) {
    const r = pick(pool, opts, rng, c);
    if (r.story) seen.add(r.story.id);
  }
  return [...seen].sort();
};

describe('pick', () => {
  it('never returns hidden stories', () => {
    expect(ids({ recent: [] })).toEqual(['aesop--a', 'aesop--b', 'grimm--c', 'grimm--d']);
  });

  it('includes revealed stories when visibility allows', () => {
    const c = { ...ctx, visibility: { showMature: true, showExcluded: true } };
    expect(ids({ recent: [] }, 500, c)).toHaveLength(6);
  });

  it('filters by collection', () => {
    expect(ids({ recent: [], collections: ['grimm'] })).toEqual(['grimm--c', 'grimm--d']);
  });

  it('treats an empty collection list as all collections', () => {
    expect(ids({ recent: [], collections: [] })).toHaveLength(4);
  });

  it('filters by maxMinutes', () => {
    expect(ids({ recent: [], maxMinutes: 5 })).toEqual(['aesop--a', 'aesop--b']);
  });

  it('filters by a minimum length (medium or long only)', () => {
    expect(ids({ recent: [], minMinutes: 6, maxMinutes: 15 })).toEqual(['grimm--c']);
    expect(ids({ recent: [], minMinutes: 15 })).toEqual(['grimm--d']);
  });

  it('filters unread only', () => {
    expect(ids({ recent: [], unreadOnly: true })).toEqual(['aesop--b', 'grimm--c', 'grimm--d']);
  });

  it('filters favorites only', () => {
    expect(ids({ recent: [], favoritesOnly: true })).toEqual(['aesop--b', 'grimm--c']);
  });

  it('combines filters', () => {
    expect(
      ids({
        recent: [],
        collections: ['aesop', 'grimm'],
        maxMinutes: 10,
        unreadOnly: true,
        favoritesOnly: true,
      }),
    ).toEqual(['aesop--b', 'grimm--c']);
  });

  it('avoids recent picks', () => {
    expect(ids({ recent: ['aesop--a', 'aesop--b', 'grimm--c'] })).toEqual(['grimm--d']);
  });

  it('treats other translations of a recent pick as recent too (shared workId)', () => {
    const tales = [
      entry({ id: 'grimm--frog', workId: 'grimm-khm-001' }),
      entry({ id: 'hunt--frog', workId: 'grimm-khm-001' }),
      entry({ id: 'hunt--other', workId: 'grimm-khm-002' }),
    ];
    const seen = new Set<string>();
    const rng = mulberry32(3);
    for (let i = 0; i < 200; i++) {
      const r = pick(tales, { recent: ['grimm--frog'] }, rng, ctx);
      if (r.story) seen.add(r.story.id);
    }
    expect([...seen]).toEqual(['hunt--other']);
  });

  it('only considers the last 10 recent picks', () => {
    const recent = ['aesop--a', ...Array.from({ length: 10 }, (_, i) => `x--${i}`)];
    expect(ids({ recent })).toContain('aesop--a');
  });

  it('relaxes repeat avoidance only when it would empty the pool', () => {
    const r = pick(pool, { recent: ['aesop--a', 'aesop--b'], maxMinutes: 5 }, mulberry32(1), ctx);
    expect(r.story && ['aesop--a', 'aesop--b']).toContain(r.story?.id);
    expect(r).toMatchObject({ relaxed: true });
    // relaxing recency must not relax other filters
    expect(ids({ recent: ['aesop--a', 'aesop--b'], maxMinutes: 5 })).toEqual([
      'aesop--a',
      'aesop--b',
    ]);
  });

  it('returns null with a reason when nothing qualifies', () => {
    expect(pick(pool, { recent: [], collections: ['nope'] }, Math.random, ctx)).toEqual({
      story: null,
      reason: 'no-matches',
    });
  });

  it('is uniform over the pool (10k picks)', () => {
    const rng = mulberry32(7);
    const counts = new Map<string, number>();
    const N = 10_000;
    for (let i = 0; i < N; i++) {
      const r = pick(pool, { recent: [] }, rng, ctx);
      counts.set(r.story!.id, (counts.get(r.story!.id) ?? 0) + 1);
    }
    expect(counts.size).toBe(4);
    for (const c of counts.values()) expect(Math.abs(c - N / 4)).toBeLessThan(N * 0.03);
  });

  describe('culture and theme filters', () => {
    const tags: Record<string, { cultures: string[]; themes: string[] }> = {
      'aesop--a': { cultures: ['greek'], themes: ['animals', 'gentle'] },
      'aesop--b': { cultures: ['greek'], themes: ['animals', 'tricksters'] },
      'grimm--c': { cultures: ['german'], themes: ['monsters', 'royalty'] },
      'grimm--d': { cultures: ['german'], themes: ['gentle', 'royalty'] },
    };
    const tctx: PickContext = { ...ctx, tagsOf: (id) => tags[id] ?? { cultures: [], themes: [] } };
    const run = (opts: Parameters<typeof pick>[1]) => ids(opts, 300, tctx);

    it('includes any of the chosen cultures', () => {
      expect(run({ recent: [], cultures: { include: ['german'], exclude: [] } })).toEqual([
        'grimm--c',
        'grimm--d',
      ]);
    });

    it('includes stories having any of the chosen themes', () => {
      expect(
        run({ recent: [], themes: { include: ['gentle', 'tricksters'], exclude: [] } }),
      ).toEqual(['aesop--a', 'aesop--b', 'grimm--d']);
    });

    it('excludes stories having any excluded theme ("no monsters tonight")', () => {
      expect(run({ recent: [], themes: { include: [], exclude: ['monsters'] } })).toEqual([
        'aesop--a',
        'aesop--b',
        'grimm--d',
      ]);
    });

    it('lets exclude win over include', () => {
      expect(run({ recent: [], themes: { include: ['royalty'], exclude: ['monsters'] } })).toEqual([
        'grimm--d',
      ]);
    });

    it('treats a story with no tags as matching no include, but surviving excludes', () => {
      const bare = { ...ctx };
      expect(ids({ recent: [], themes: { include: ['gentle'], exclude: [] } }, 50, bare)).toEqual(
        [],
      );
      expect(
        ids({ recent: [], themes: { include: [], exclude: ['gentle'] } }, 300, bare),
      ).toHaveLength(4);
    });
  });

  describe('pickMany', () => {
    it('returns n distinct stories, avoiding recent ones', () => {
      const r = pickMany(pool, { recent: ['aesop--a'] }, 3, mulberry32(9), ctx);
      expect(r.stories).toHaveLength(3);
      expect(new Set(r.stories.map((s) => s.id)).size).toBe(3);
      expect(r.stories.map((s) => s.id)).not.toContain('aesop--a');
      expect(r).toMatchObject({ relaxed: false });
    });

    it('never offers two translations of the same tale together', () => {
      const tales = [
        entry({ id: 'grimm--frog', workId: 'w1' }),
        entry({ id: 'hunt--frog', workId: 'w1' }),
        entry({ id: 'hunt--other', workId: 'w2' }),
        entry({ id: 'aesop--x' }),
      ];
      for (let seed = 0; seed < 50; seed++) {
        const r = pickMany(tales, { recent: [] }, 3, mulberry32(seed), ctx);
        const works = r.stories.map((s) => s.workId).filter(Boolean);
        expect(new Set(works).size).toBe(works.length);
        expect(r.stories).toHaveLength(3);
      }
    });

    it('tops up from recent picks only when fresh ones run out, and says so', () => {
      const r = pickMany(
        pool,
        { recent: ['aesop--a', 'aesop--b', 'grimm--c'] },
        3,
        mulberry32(1),
        ctx,
      );
      expect(r.stories).toHaveLength(3);
      expect(r.stories[0]?.id).toBe('grimm--d');
      expect(r).toMatchObject({ relaxed: true });
    });

    it('returns fewer when fewer qualify, and no-matches when none do', () => {
      expect(
        pickMany(pool, { recent: [], maxMinutes: 1 }, 3, Math.random, ctx).stories,
      ).toHaveLength(1);
      expect(pickMany(pool, { recent: [], collections: ['x'] }, 3, Math.random, ctx)).toEqual({
        stories: [],
        reason: 'no-matches',
      });
    });
  });
});
