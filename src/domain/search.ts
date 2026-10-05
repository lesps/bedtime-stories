import type { IndexEntry } from '../data/types';

export function normalize(s: string): string {
  return s
    .normalize('NFD')
    .replace(/\p{M}/gu, '')
    .toLowerCase()
    .replace(/['’‘`]/g, '')
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim();
}

/** Every query word must appear in the title or in one of the extra labels (e.g. tag names). */
export function matchesQuery(
  entry: Pick<IndexEntry, 'title'>,
  query: string,
  labels: string[] = [],
): boolean {
  const words = normalize(query).split(' ').filter(Boolean);
  if (words.length === 0) return true;
  const haystack = [entry.title, ...labels].map(normalize).join(' | ');
  return words.every((w) => haystack.includes(w));
}
