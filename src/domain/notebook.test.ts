import { describe, expect, it } from 'vitest';
import { entry } from '../test/fixtures';
import { notebookMarkdown, notebookStories } from './notebook';

const stories = [
  entry({ id: 'aesop--heron', title: 'The Heron', collectionId: 'aesop' }),
  entry({ id: 'grimm--frog', title: 'The Frog-King', collectionId: 'grimm' }),
  entry({ id: 'grimm--none', title: 'Nothing Here', collectionId: 'grimm' }),
];
const hl = (id: string, block: number, quote: string, note?: string, updatedAt = 1) => ({
  id,
  block,
  start: 0,
  end: quote.length,
  quote,
  color: 'yellow' as const,
  ...(note ? { note } : {}),
  createdAt: 1,
  updatedAt,
});
const annotations = {
  'grimm--frog': [
    hl('b', 7, 'the ball fell', 'Ada gasped'),
    hl('a', 2, 'golden ball', undefined, 5),
  ],
};
const storyNotes = { 'aesop--heron': { text: 'Short and sweet.', updatedAt: 9 } };

describe('notebook', () => {
  it('lists stories with notes or highlights, most recently touched first', () => {
    expect(
      notebookStories(stories, annotations, storyNotes).map((s) => [
        s.entry.id,
        s.highlights,
        s.notes,
      ]),
    ).toEqual([
      ['aesop--heron', 0, 1],
      ['grimm--frog', 2, 1],
    ]);
  });

  it('exports Markdown in reading order, quoting highlights with their notes', () => {
    const md = notebookMarkdown(
      notebookStories(stories, annotations, storyNotes),
      annotations,
      storyNotes,
      (id) => ({ aesop: 'The Aesop for Children', grimm: "Grimms' Fairy Tales" })[id] ?? id,
      new Date('2026-10-06T12:00:00Z'),
    );
    expect(md).toBe(
      [
        '# Storybook notebook',
        '',
        '_Exported 2026-10-06_',
        '',
        '## The Heron',
        '_The Aesop for Children_',
        '',
        'Short and sweet.',
        '',
        '## The Frog-King',
        "_Grimms' Fairy Tales_",
        '',
        '> golden ball',
        '',
        '> the ball fell',
        '',
        'Ada gasped',
        '',
      ].join('\n'),
    );
  });
});
