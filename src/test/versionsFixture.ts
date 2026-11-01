import type { Tags } from '../data/types';
import { collection, entry, makeIndex } from './fixtures';
import { bodiesOf, type FixtureData } from './renderApp';

/**
 * A small mythology shelf: Joyce's book has two originals with retellings (one mature) and one
 * without; Hull's book is retold entirely; the retellings collection has one ‡ story of its own.
 */
const stories = [
  entry({ id: 'aesop--the-fox', title: 'The Fox' }),
  entry({
    id: 'joyce--lir',
    order: 1,
    title: 'The Fate of the Children of Lir',
    readingMinutes: 25,
    workId: 'irish-lir',
    simplifiedId: 'myths-irish--lir',
  }),
  entry({
    id: 'joyce--usna',
    order: 2,
    title: 'The Sons of Usna',
    workId: 'irish-usna',
    simplifiedId: 'myths-irish--usna',
    flags: ['mature-themes'],
  }),
  entry({ id: 'joyce--oisin', order: 3, title: 'Oisin in Tir na nOg', workId: 'irish-oisin' }),
  entry({
    id: 'hull--cuchulain',
    title: 'How Cuchulain Got His Name',
    workId: 'irish-cuchulain',
    simplifiedId: 'myths-irish--cuchulain',
  }),
  entry({
    id: 'myths-irish--lir',
    order: 1,
    title: 'The Children of Lir',
    workId: 'irish-lir',
    adaptedFrom: 'joyce--lir',
  }),
  entry({
    id: 'myths-irish--usna',
    order: 2,
    title: 'Deirdre and the Sons of Usna',
    workId: 'irish-usna',
    adaptedFrom: 'joyce--usna',
  }),
  entry({
    id: 'myths-irish--cuchulain',
    order: 3,
    title: 'The Hound of Culann',
    workId: 'irish-cuchulain',
    adaptedFrom: 'hull--cuchulain',
  }),
  entry({
    id: 'myths-irish--tuan',
    order: 4,
    title: 'Tuan the Shape-Changer',
    workId: 'irish-tuan',
  }),
];

const index = makeIndex(stories, [
  collection({ id: 'aesop', title: 'The Aesop for Children' }),
  collection({ id: 'joyce', title: 'Old Celtic Romances' }),
  collection({ id: 'hull', title: 'Cuchulain, the Hound of Ulster' }),
  collection({ id: 'myths-irish', title: 'Irish Legends, Simply Told' }),
]);

const tags: Tags = {
  schemaVersion: 1,
  cultures: [
    { id: 'greek', label: 'Ancient Greek' },
    { id: 'irish', label: 'Irish' },
  ],
  themes: [
    { id: 'animals', label: 'Animals' },
    { id: 'gods-heroes', label: 'Gods & heroes' },
  ],
  stories: Object.fromEntries(
    stories.map((s) => [
      s.id,
      s.id.startsWith('aesop')
        ? { cultures: ['greek'], themes: ['animals'] }
        : { cultures: ['irish'], themes: ['gods-heroes'] },
    ]),
  ),
};

export const versionsData: FixtureData = { index, tags, bodies: bodiesOf(index) };
