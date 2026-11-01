import type { IndexEntry } from '../data/types';
import { isVisible, type VisibilitySettings } from './visibility';

const NONE: ReadonlySet<string> = new Set();

/** A collection's stories in book order, without hidden ones or versions left out of listings. */
export function visibleInCollection(
  stories: IndexEntry[],
  collectionId: string,
  settings: VisibilitySettings,
  hidden: ReadonlySet<string> = NONE,
): IndexEntry[] {
  return stories
    .filter((s) => s.collectionId === collectionId && isVisible(s, settings) && !hidden.has(s.id))
    .sort((a, b) => a.order - b.order);
}

/** A collection's versions that listings leave out (see `hiddenVersions`), in book order. */
export function hiddenInCollection(
  stories: IndexEntry[],
  collectionId: string,
  settings: VisibilitySettings,
  hidden: ReadonlySet<string>,
): IndexEntry[] {
  return stories
    .filter((s) => s.collectionId === collectionId && isVisible(s, settings) && hidden.has(s.id))
    .sort((a, b) => a.order - b.order);
}

/**
 * Previous and next in the list the story appears in on its collection page: the listed
 * stories, or, for a version that listings leave out, the other such versions.
 */
export function neighbors(
  stories: IndexEntry[],
  storyId: string,
  settings: VisibilitySettings,
  hidden: ReadonlySet<string> = NONE,
): { prev: IndexEntry | null; next: IndexEntry | null } {
  const current = stories.find((s) => s.id === storyId);
  if (!current) return { prev: null, next: null };
  const list = hidden.has(current.id)
    ? hiddenInCollection(stories, current.collectionId, settings, hidden)
    : visibleInCollection(stories, current.collectionId, settings, hidden);
  const prev = list.filter((s) => s.order < current.order).at(-1) ?? null;
  const next = list.find((s) => s.order > current.order) ?? null;
  return { prev, next };
}
