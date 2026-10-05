import type { Collection } from '../data/types';

/** Surname of the first person credited: "Retold by Grace James, illustrated by …" → "James". */
const creditSurname = (contributor: string | null) =>
  contributor
    ?.match(/\bby ([^,]+)/)?.[1]
    ?.trim()
    .split(/\s+/)
    .at(-1);

/** Display label per collection id, adding the credited surname where titles collide. */
export function collectionLabels(collections: Collection[]): Map<string, string> {
  const counts = new Map<string, number>();
  for (const c of collections) counts.set(c.title, (counts.get(c.title) ?? 0) + 1);
  return new Map(
    collections.map((c) => [
      c.id,
      counts.get(c.title)! > 1 ? `${c.title} (${creditSurname(c.contributor) ?? c.id})` : c.title,
    ]),
  );
}
