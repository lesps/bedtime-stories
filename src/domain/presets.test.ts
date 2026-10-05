import { describe, expect, it } from 'vitest';
import { DEFAULT_STATE } from '../storage/store';
import { PRESETS, applyPreset } from './presets';

const base = DEFAULT_STATE.settings.picker;
const ctx = {
  readIds: new Set(['a--1', 'b--1']),
  tagsOf: (id: string) => ({
    cultures: [id.startsWith('a') ? 'greek' : id.startsWith('b') ? 'german' : 'japanese'],
    themes: [],
  }),
  cultures: ['greek', 'german', 'japanese', 'french'],
};

describe('presets', () => {
  it('has the three named presets', () => {
    expect(PRESETS.map((p) => p.label)).toEqual([
      'Quick & gentle',
      'Something new',
      'Old favorite',
    ]);
  });

  it('Quick & gentle: up to 5 min, gentle theme, nothing else constrained', () => {
    expect(applyPreset('quick-gentle', base, ctx)).toEqual({
      ...base,
      minMinutes: 1,
      maxMinutes: 5,
      collections: [],
      unreadOnly: false,
      favoritesOnly: false,
      cultures: { include: [], exclude: [] },
      themes: { include: ['gentle'], exclude: [] },
    });
  });

  it('Something new: unread only, from cultures not read yet', () => {
    const r = applyPreset('something-new', base, ctx);
    expect(r.unreadOnly).toBe(true);
    expect(r.favoritesOnly).toBe(false);
    expect(r.cultures).toEqual({ include: ['japanese', 'french'], exclude: [] });
  });

  it('Something new falls back to any culture once every culture has been read', () => {
    const r = applyPreset('something-new', base, { ...ctx, cultures: ['greek', 'german'] });
    expect(r.cultures).toEqual({ include: [], exclude: [] });
  });

  it('Old favorite: favorites only, any length, no other filters', () => {
    expect(applyPreset('old-favorite', base, ctx)).toMatchObject({
      favoritesOnly: true,
      unreadOnly: false,
      minMinutes: 1,
      maxMinutes: null,
      collections: [],
      themes: { include: [], exclude: [] },
    });
  });

  it('keeps the chosen count', () => {
    expect(applyPreset('old-favorite', { ...base, count: 3 }, ctx).count).toBe(3);
  });
});
