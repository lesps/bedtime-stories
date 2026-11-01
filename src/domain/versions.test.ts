import { describe, expect, it } from 'vitest';
import { entry } from '../test/fixtures';
import { counterpart, hiddenVersions, isListed } from './versions';

// o = original, r = its simplified retelling
const o = entry({ id: 'book--lir', simplifiedId: 'myths-irish--lir', workId: 'lir' });
const r = entry({ id: 'myths-irish--lir', adaptedFrom: 'book--lir', workId: 'lir' });
const mo = entry({
  id: 'book--usna',
  simplifiedId: 'myths-irish--usna',
  workId: 'usna',
  flags: ['mature-themes'],
});
const mr = entry({ id: 'myths-irish--usna', adaptedFrom: 'book--usna', workId: 'usna' });
// Two originals sharing one retelling (alsoSimplifies)
const p1 = entry({ id: 'kingsley--perseus', simplifiedId: 'myths-greek--perseus', workId: 'p' });
const p2 = entry({ id: 'hawthorne--perseus', simplifiedId: 'myths-greek--perseus', workId: 'p' });
const pr = entry({ id: 'myths-greek--perseus', adaptedFrom: 'kingsley--perseus', workId: 'p' });
// A retelling with no original (‡), an original whose retelling is missing, a plain story
const untold = entry({ id: 'myths-irish--tuan', workId: 'tuan' });
const dangling = entry({ id: 'book--ys', simplifiedId: 'myths-celtic--ys' });
const plain = entry({ id: 'aesop--fox' });
// A mature retelling of a mature original
const bo = entry({ id: 'book--b', simplifiedId: 'myths-x--b', flags: ['mature-themes'] });
const br = entry({ id: 'myths-x--b', adaptedFrom: 'book--b', flags: ['mature-themes'] });

const all = [o, r, mo, mr, p1, p2, pr, untold, dangling, plain, bo, br];
const base = { showMature: false, showExcluded: false, showOriginals: false };

describe('hiddenVersions', () => {
  it.each([
    // settings, ids left out of listings
    [base, ['book--lir', 'book--usna', 'kingsley--perseus', 'hawthorne--perseus']],
    [
      { ...base, showMature: true },
      ['book--lir', 'book--usna', 'kingsley--perseus', 'hawthorne--perseus', 'book--b'],
    ],
    // Originals instead: a retelling goes only if one of its originals can be shown
    [{ ...base, showOriginals: true }, ['myths-irish--lir', 'myths-greek--perseus']],
    [
      { ...base, showOriginals: true, showMature: true },
      ['myths-irish--lir', 'myths-irish--usna', 'myths-greek--perseus', 'myths-x--b'],
    ],
  ] as const)('%#: %o', (settings, expected) => {
    expect([...hiddenVersions(all, settings)].sort()).toEqual([...expected].sort());
  });

  it('keeps a retelling with no original, and an original whose retelling is missing', () => {
    const hidden = hiddenVersions(all, base);
    expect(hidden.has('myths-irish--tuan')).toBe(false);
    expect(hidden.has('book--ys')).toBe(false);
    expect(hiddenVersions(all, { ...base, showOriginals: true }).has('book--ys')).toBe(false);
  });
});

describe('isListed', () => {
  const hidden = hiddenVersions(all, base);
  it.each([
    [r, true],
    [o, false],
    [mr, true],
    [mo, false], // hidden by content settings anyway
    [untold, true],
    [plain, true],
    [br, false], // mature
  ])('%#: %s → %s', (e, expected) => {
    expect(isListed(e, base, hidden)).toBe(expected);
  });
});

describe('counterpart', () => {
  const byId = new Map(all.map((s) => [s.id, s]));
  it('points a retelling to its original and an original to its retelling', () => {
    expect(counterpart(r, byId)).toEqual({ kind: 'original', entry: o });
    expect(counterpart(o, byId)).toEqual({ kind: 'retelling', entry: r });
    expect(counterpart(p2, byId)).toEqual({ kind: 'retelling', entry: pr });
  });
  it('has none for a story without one', () => {
    expect(counterpart(untold, byId)).toBeNull();
    expect(counterpart(plain, byId)).toBeNull();
    expect(counterpart(dangling, byId)).toBeNull();
  });
});
