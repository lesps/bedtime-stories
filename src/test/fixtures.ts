import type { Collection, Index, IndexEntry, Story } from '../data/types';

export function entry(over: Partial<IndexEntry> & { id: string }): IndexEntry {
  const [collectionId = 'aesop'] = over.id.split('--');
  return {
    collectionId,
    order: 1,
    title: over.id,
    wordCount: 100,
    readingMinutes: 1,
    excluded: false,
    flags: [],
    hasImages: false,
    ...over,
  };
}

export function collection(over: Partial<Collection> & { id: string }): Collection {
  return {
    title: over.id,
    author: 'Someone',
    contributor: null,
    firstPublished: 1900,
    source: `https://example.org/${over.id}`,
    license: 'Public domain in the USA',
    storyCount: 0,
    ...over,
  };
}

export function makeIndex(stories: IndexEntry[], collections?: Collection[]): Index {
  const cols =
    collections ??
    [...new Set(stories.map((s) => s.collectionId))].map((id) => collection({ id, title: id }));
  return {
    schemaVersion: 1,
    collections: cols.map((c) => ({
      ...c,
      storyCount: stories.filter((s) => s.collectionId === c.id).length,
    })),
    stories,
  };
}

export function storyOf(e: IndexEntry, over: Partial<Story> = {}): Story {
  const { hasImages: _h, ...rest } = e;
  void _h;
  return {
    ...rest,
    origin: null,
    moral: null,
    blocks: [{ type: 'p', text: 'Once upon a time.' }],
    ...over,
  };
}

/** Deterministic PRNG for tests. */
export function mulberry32(seed: number) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
