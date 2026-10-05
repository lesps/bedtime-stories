import type { IndexEntry } from '../data/types';
import { isVisible, type VisibilitySettings } from './visibility';

export function visibleInCollection(
  stories: IndexEntry[],
  collectionId: string,
  settings: VisibilitySettings,
): IndexEntry[] {
  return stories
    .filter((s) => s.collectionId === collectionId && isVisible(s, settings))
    .sort((a, b) => a.order - b.order);
}

export function neighbors(
  stories: IndexEntry[],
  storyId: string,
  settings: VisibilitySettings,
): { prev: IndexEntry | null; next: IndexEntry | null } {
  const current = stories.find((s) => s.id === storyId);
  if (!current) return { prev: null, next: null };
  const list = visibleInCollection(stories, current.collectionId, settings);
  const prev = list.filter((s) => s.order < current.order).at(-1) ?? null;
  const next = list.find((s) => s.order > current.order) ?? null;
  return { prev, next };
}
