import type { IndexEntry } from '../data/types';

export type VisibilitySettings = { showMature: boolean; showExcluded: boolean };

export function isVisible(
  entry: Pick<IndexEntry, 'excluded' | 'flags'>,
  settings: VisibilitySettings,
): boolean {
  if (entry.excluded && !settings.showExcluded) return false;
  if (entry.flags.includes('mature-themes') && !settings.showMature) return false;
  return true;
}
