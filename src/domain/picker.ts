import type { IndexEntry } from '../data/types';
import { isVisible, type VisibilitySettings } from './visibility';

export const RECENT_WINDOW = 10;

export type PickOptions = {
  collections?: string[];
  maxMinutes?: number;
  unreadOnly?: boolean;
  favoritesOnly?: boolean;
  recent: string[];
};

export type PickContext = {
  visibility: VisibilitySettings;
  readIds: ReadonlySet<string>;
  favoriteIds: ReadonlySet<string>;
};

export type PickResult =
  { story: IndexEntry; relaxed: boolean } | { story: null; reason: 'no-matches' };

export function pick(
  entries: IndexEntry[],
  opts: PickOptions,
  rng: () => number,
  ctx: PickContext,
): PickResult {
  const cols = opts.collections?.length ? new Set(opts.collections) : null;
  const pool = entries.filter(
    (e) =>
      isVisible(e, ctx.visibility) &&
      (!cols || cols.has(e.collectionId)) &&
      (opts.maxMinutes == null || e.readingMinutes <= opts.maxMinutes) &&
      (!opts.unreadOnly || !ctx.readIds.has(e.id)) &&
      (!opts.favoritesOnly || ctx.favoriteIds.has(e.id)),
  );
  if (pool.length === 0) return { story: null, reason: 'no-matches' };

  const recent = new Set(opts.recent.slice(-RECENT_WINDOW));
  const fresh = pool.filter((e) => !recent.has(e.id));
  const relaxed = fresh.length === 0;
  const from = relaxed ? pool : fresh;
  const story = from[Math.min(from.length - 1, Math.floor(rng() * from.length))]!;
  return { story, relaxed };
}
