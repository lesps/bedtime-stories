import type { IndexEntry, StoryTags } from '../data/types';
import { isVisible, type VisibilitySettings } from './visibility';

export const RECENT_WINDOW = 10;

/** Include: any of these (empty = no constraint). Exclude: none of these. Exclude wins. */
export type TagFilter = { include: string[]; exclude: string[] };

export type PickOptions = {
  collections?: string[];
  minMinutes?: number;
  maxMinutes?: number;
  unreadOnly?: boolean;
  favoritesOnly?: boolean;
  cultures?: TagFilter;
  themes?: TagFilter;
  recent: string[];
};

export type PickContext = {
  visibility: VisibilitySettings;
  readIds: ReadonlySet<string>;
  favoriteIds: ReadonlySet<string>;
  tagsOf?: (id: string) => StoryTags;
};

export type PickResult =
  { story: IndexEntry; relaxed: boolean } | { story: null; reason: 'no-matches' };

export type PickManyResult =
  { stories: IndexEntry[]; relaxed: boolean } | { stories: []; reason: 'no-matches' };

const NO_TAGS: StoryTags = { cultures: [], themes: [] };

function passesTags(tags: string[], f: TagFilter | undefined) {
  if (!f) return true;
  if (f.exclude.some((t) => tags.includes(t))) return false;
  return f.include.length === 0 || f.include.some((t) => tags.includes(t));
}

/** Every visible story that satisfies the filters, ignoring recency. */
export function candidates(entries: IndexEntry[], opts: PickOptions, ctx: PickContext) {
  const cols = opts.collections?.length ? new Set(opts.collections) : null;
  const tagsOf = ctx.tagsOf ?? (() => NO_TAGS);
  return entries.filter((e) => {
    if (!isVisible(e, ctx.visibility)) return false;
    if (cols && !cols.has(e.collectionId)) return false;
    if (opts.minMinutes != null && e.readingMinutes < opts.minMinutes) return false;
    if (opts.maxMinutes != null && e.readingMinutes > opts.maxMinutes) return false;
    if (opts.unreadOnly && ctx.readIds.has(e.id)) return false;
    if (opts.favoritesOnly && !ctx.favoriteIds.has(e.id)) return false;
    const t = tagsOf(e.id);
    return passesTags(t.cultures, opts.cultures) && passesTags(t.themes, opts.themes);
  });
}

/**
 * Up to `n` distinct stories, never two translations of one tale. Recent picks (and other
 * translations of them) are avoided unless that leaves too few; then they top up the rest.
 */
export function pickMany(
  entries: IndexEntry[],
  opts: PickOptions,
  n: number,
  rng: () => number,
  ctx: PickContext,
): PickManyResult {
  const pool = candidates(entries, opts, ctx);
  if (pool.length === 0) return { stories: [], reason: 'no-matches' };

  const recent = new Set(opts.recent.slice(-RECENT_WINDOW));
  const recentWorks = new Set(
    entries.filter((e) => e.workId && recent.has(e.id)).map((e) => e.workId),
  );
  const isRecent = (e: IndexEntry) => recent.has(e.id) || !!(e.workId && recentWorks.has(e.workId));

  const chosen: IndexEntry[] = [];
  const works = new Set<string>();
  const draw = (from: IndexEntry[]) => {
    const left = from.filter((e) => !chosen.includes(e) && !(e.workId && works.has(e.workId)));
    while (chosen.length < n && left.length) {
      const [e] = left.splice(Math.min(left.length - 1, Math.floor(rng() * left.length)), 1);
      if (e!.workId && works.has(e!.workId)) continue;
      chosen.push(e!);
      if (e!.workId) works.add(e!.workId);
    }
  };
  draw(pool.filter((e) => !isRecent(e)));
  const fresh = chosen.length;
  draw(pool);
  return { stories: chosen, relaxed: chosen.length > fresh };
}

export function pick(
  entries: IndexEntry[],
  opts: PickOptions,
  rng: () => number,
  ctx: PickContext,
): PickResult {
  const r = pickMany(entries, opts, 1, rng, ctx);
  if ('reason' in r) return { story: null, reason: r.reason };
  return { story: r.stories[0]!, relaxed: r.relaxed };
}
