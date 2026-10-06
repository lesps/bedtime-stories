import { describe, expect, it } from 'vitest';
import { progressInfo } from './progress';

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

  it('is unknown without a block count (older saved progress)', () => {
    expect(progressInfo({ blockIndex: 3, updatedAt: 0 }, 10)).toBeNull();
  });
});
