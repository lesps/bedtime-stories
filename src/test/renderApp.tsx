import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { vi } from 'vitest';
import { AppRoutes } from '../app/App';
import { resetDataCache } from '../data/client';
import type { Index, Story } from '../data/types';
import { StoreProvider } from '../storage/StoreProvider';
import { createStore } from '../storage/store';
import { collection, entry, makeIndex, storyOf } from './fixtures';

export const fixtureStories = [
  entry({ id: 'aesop--the-heron', order: 2, title: 'The Heron', readingMinutes: 1 }),
  entry({
    id: 'aesop--the-fox-and-the-grapes',
    order: 1,
    title: 'The Fox and the Grapes',
    readingMinutes: 2,
  }),
  entry({
    id: 'aesop--dark-fable',
    order: 3,
    title: 'A Dark Fable',
    readingMinutes: 2,
    flags: ['mature-themes'],
  }),
  entry({ id: 'aesop--the-lion', order: 4, title: 'The Lion', readingMinutes: 3 }),
  entry({
    id: 'grimm--rapunzel',
    order: 1,
    title: 'Rapunzel',
    readingMinutes: 9,
    workId: 'grimm-khm-012',
  }),
  entry({ id: 'grimm--the-long-one', order: 2, title: 'The Long One', readingMinutes: 25 }),
  entry({
    id: 'grimm--hidden-tale',
    order: 3,
    title: 'Hidden Tale',
    readingMinutes: 4,
    excluded: true,
  }),
  entry({
    id: 'hunt--rapunzel',
    order: 12,
    title: 'Rapunzel (Hunt)',
    readingMinutes: 8,
    workId: 'grimm-khm-012',
  }),
  entry({
    id: 'hunt--dark-rapunzel',
    order: 13,
    title: 'Rapunzel (dark)',
    readingMinutes: 8,
    workId: 'grimm-khm-012',
    flags: ['mature-themes'],
  }),
];

export const fixtureIndex: Index = makeIndex(fixtureStories, [
  collection({
    id: 'aesop',
    title: 'The Aesop for Children',
    contributor: 'Illustrated by Milo Winter',
  }),
  collection({ id: 'grimm', title: "Grimms' Fairy Tales", contributor: 'Translated by Taylor' }),
  collection({ id: 'hunt', title: 'Household Tales', contributor: 'Translated by Margaret Hunt' }),
]);

export const fixtureStoryBodies: Record<string, Story> = Object.fromEntries(
  fixtureStories.map((e) => [
    e.id,
    storyOf(e, {
      blocks: [
        { type: 'p', text: `${e.title} begins here.` },
        { type: 'p', text: 'Middle part.' },
        { type: 'p', text: 'More middle.' },
        { type: 'moral', text: 'The end.' },
      ],
    }),
  ]),
);

export function mockCompendiumFetch(overrides: Partial<Record<string, Story>> = {}) {
  resetDataCache();
  const bodies = { ...fixtureStoryBodies, ...overrides };
  const fetchMock = vi.fn(async (url: string) => {
    if (url.endsWith('index.json')) return new Response(JSON.stringify(fixtureIndex));
    const id = /stories\/([^/]+)\.json$/.exec(url)?.[1];
    const body = id && bodies[id];
    return body ? new Response(JSON.stringify(body)) : new Response('', { status: 404 });
  });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

export function renderApp(
  path = '/',
  store = createStore(localStorage),
  overrides: Partial<Record<string, Story>> = {},
) {
  mockCompendiumFetch(overrides);
  const utils = render(
    <StoreProvider store={store}>
      <MemoryRouter initialEntries={[path]}>
        <AppRoutes />
      </MemoryRouter>
    </StoreProvider>,
  );
  return { ...utils, store };
}
