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

export function matchesQuery(entry: Pick<IndexEntry, 'title'>, query: string): boolean {
  const words = normalize(query).split(' ').filter(Boolean);
  if (words.length === 0) return true;
  const title = normalize(entry.title);
  return words.every((w) => title.includes(w));
}
