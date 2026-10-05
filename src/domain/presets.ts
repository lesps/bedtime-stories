import type { StoryTags } from '../data/types';
import type { PickerSettings } from '../storage/store';

export type PresetId = 'quick-gentle' | 'something-new' | 'old-favorite';

export const PRESETS: { id: PresetId; label: string; hint: string }[] = [
  { id: 'quick-gentle', label: 'Quick & gentle', hint: 'Up to 5 min, nothing scary' },
  { id: 'something-new', label: 'Something new', hint: 'Unread, from a culture you haven’t tried' },
  { id: 'old-favorite', label: 'Old favorite', hint: 'One of your hearts, any length' },
];

type Ctx = {
  readIds: ReadonlySet<string>;
  tagsOf: (id: string) => StoryTags;
  /** All culture ids, in display order. */
  cultures: string[];
};

const NONE = { include: [], exclude: [] };

/** Returns full picker settings for a preset, keeping only the chosen count. */
export function applyPreset(id: PresetId, current: PickerSettings, ctx: Ctx): PickerSettings {
  const clean: PickerSettings = {
    ...current,
    collections: [],
    minMinutes: 1,
    maxMinutes: null,
    unreadOnly: false,
    favoritesOnly: false,
    cultures: NONE,
    themes: NONE,
  };
  switch (id) {
    case 'quick-gentle':
      return { ...clean, maxMinutes: 5, themes: { include: ['gentle'], exclude: [] } };
    case 'something-new': {
      const read = new Set([...ctx.readIds].flatMap((r) => ctx.tagsOf(r).cultures));
      const fresh = ctx.cultures.filter((c) => !read.has(c));
      return { ...clean, unreadOnly: true, cultures: { include: fresh, exclude: [] } };
    }
    case 'old-favorite':
      return { ...clean, favoritesOnly: true };
  }
}
