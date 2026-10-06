import type { IndexEntry } from '../data/types';
import type { Highlight, State } from '../storage/store';

type Annotations = State['annotations'];
type StoryNotes = State['storyNotes'];

export type NotebookStory = {
  entry: IndexEntry;
  highlights: number;
  notes: number;
  touchedAt: number;
};

/** Stories with any highlight or note, most recently touched first. */
export function notebookStories(
  stories: IndexEntry[],
  annotations: Annotations,
  storyNotes: StoryNotes,
): NotebookStory[] {
  return stories
    .flatMap((entry) => {
      const hs = annotations[entry.id] ?? [];
      const sn = storyNotes[entry.id];
      if (!hs.length && !sn) return [];
      const touchedAt = Math.max(sn?.updatedAt ?? 0, ...hs.map((h) => h.updatedAt));
      const notes = hs.filter((h) => h.note).length + (sn ? 1 : 0);
      return [{ entry, highlights: hs.length, notes, touchedAt }];
    })
    .sort((a, b) => b.touchedAt - a.touchedAt);
}

export const byReadingOrder = (a: Highlight, b: Highlight) =>
  a.block - b.block || a.start - b.start;

const quote = (text: string) =>
  text
    .split('\n')
    .map((l) => `> ${l}`)
    .join('\n');

export function notebookMarkdown(
  list: NotebookStory[],
  annotations: Annotations,
  storyNotes: StoryNotes,
  collectionLabel: (id: string) => string,
  date = new Date(),
): string {
  const out = ['# Storybook notebook', '', `_Exported ${date.toISOString().slice(0, 10)}_`, ''];
  for (const { entry } of list) {
    out.push(`## ${entry.title}`, `_${collectionLabel(entry.collectionId)}_`, '');
    const sn = storyNotes[entry.id];
    if (sn) out.push(sn.text.trim(), '');
    for (const h of [...(annotations[entry.id] ?? [])].sort(byReadingOrder)) {
      out.push(quote(h.quote), '');
      if (h.note) out.push(h.note.trim(), '');
    }
  }
  return out.join('\n');
}
