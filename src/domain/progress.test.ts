import { describe, expect, it } from 'vitest';
import { isInProgress, progressInfo } from './progress';

describe('progressInfo', () => {
  it.each([
    // [blockIndex, blockCount, readingMinutes, fraction, minutesLeft]
    [0, 10, 20, 0, 20],
    [5, 10, 20, 0.5, 10],
    [9, 10, 20, 0.9, 2],
    [9, 10, 3, 0.9, 1],
  ] as const)('%i/%i of %i min → %s, %i min left', (b, n, m, fraction, left) => {
    expect(progressInfo({ blockIndex: b, blockCount: n, updatedAt: 0 }, m)).toEqual({
      fraction,
      minutesLeft: left,
    });
  });

  it('reports finished stories as complete', () => {
    expect(
      progressInfo({ blockIndex: 9, blockCount: 10, finished: true, updatedAt: 0 }, 20),
    ).toEqual({
      fraction: 1,
      minutesLeft: 0,
    });
  });

  it('says which saved positions are still in progress', () => {
    expect(isInProgress({ blockIndex: 3, updatedAt: 0 })).toBe(true);
    expect(isInProgress({ blockIndex: 9, blockCount: 10, finished: true, updatedAt: 0 })).toBe(
      false,
    );
    expect(isInProgress(undefined)).toBe(false);
  });

  it('is unknown without a block count (older saved progress)', () => {
    expect(progressInfo({ blockIndex: 3, updatedAt: 0 }, 10)).toBeNull();
  });
});
