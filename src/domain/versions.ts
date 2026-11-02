import type { IndexEntry } from '../data/types';
import { isVisible, type VisibilitySettings } from './visibility';

export type ListingSettings = VisibilitySettings & { showOriginals: boolean };

/**
 * Ids left out of listings because another version of the same myth is listed instead: by
 * default an original gives way to its simplified retelling; with `showOriginals`, a retelling
 * gives way to its originals. A version only gives way to one that content settings show.
 */
export function hiddenVersions(stories: IndexEntry[], settings: ListingSettings): Set<string> {
  const byId = new Map(stories.map((s) => [s.id, s]));
  const hidden = new Set<string>();
  for (const o of stories) {
    const r = o.simplifiedId ? byId.get(o.simplifiedId) : undefined;
    if (!r) continue;
    if (!settings.showOriginals) {
      if (isVisible(r, settings)) hidden.add(o.id);
    } else if (isVisible(o, settings)) hidden.add(r.id);
  }
  return hidden;
}

/** Shown in the library, search, collections, tag pages, prev/next and Surprise me. */
export function isListed(
  entry: IndexEntry,
  settings: VisibilitySettings,
  hidden: ReadonlySet<string>,
): boolean {
  return isVisible(entry, settings) && !hidden.has(entry.id);
}

export type Counterpart = { kind: 'original' | 'retelling'; entry: IndexEntry };

/** The other version of a retold myth: a retelling's original, or an original's retelling. */
export function counterpart(
  entry: IndexEntry,
  byId: ReadonlyMap<string, IndexEntry>,
): Counterpart | null {
  const original = entry.adaptedFrom ? byId.get(entry.adaptedFrom) : undefined;
  if (original) return { kind: 'original', entry: original };
  const retelling = entry.simplifiedId ? byId.get(entry.simplifiedId) : undefined;
  return retelling ? { kind: 'retelling', entry: retelling } : null;
}
