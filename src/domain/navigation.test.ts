import { describe, expect, it } from 'vitest';
import { entry } from '../test/fixtures';
import { neighbors, visibleInCollection } from './navigation';

const stories = [
  entry({ id: 'a--3', order: 3 }),
  entry({ id: 'a--1', order: 1 }),
  entry({ id: 'a--2', order: 2, flags: ['mature-themes'] }),
  entry({ id: 'a--4', order: 4, excluded: true }),
  entry({ id: 'a--5', order: 5 }),
  entry({ id: 'b--1', order: 1 }),
];
const hide = { showMature: false, showExcluded: false };

describe('visibleInCollection', () => {
  it('sorts by order and drops hidden stories', () => {
    expect(visibleInCollection(stories, 'a', hide).map((s) => s.id)).toEqual([
      'a--1',
      'a--3',
      'a--5',
    ]);
  });
});

describe('neighbors', () => {
  it('skips hidden stories', () => {
    const n = neighbors(stories, 'a--3', hide);
    expect(n.prev?.id).toBe('a--1');
    expect(n.next?.id).toBe('a--5');
  });
  it('has no prev at the start or next at the end', () => {
    expect(neighbors(stories, 'a--1', hide).prev).toBeNull();
    expect(neighbors(stories, 'a--5', hide).next).toBeNull();
  });
  it('includes revealed stories when settings allow', () => {
    const n = neighbors(stories, 'a--3', { showMature: true, showExcluded: true });
    expect([n.prev?.id, n.next?.id]).toEqual(['a--2', 'a--4']);
  });
  it('still finds neighbours for a story that is itself hidden', () => {
    const n = neighbors(stories, 'a--2', hide);
    expect([n.prev?.id, n.next?.id]).toEqual(['a--1', 'a--3']);
  });
});
