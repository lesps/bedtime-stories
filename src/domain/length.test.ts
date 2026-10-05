import { describe, expect, it } from 'vitest';
import { FULL_RANGE, LENGTH_STOPS, formatRange, inRange, isFullRange, stopLabel } from './length';

describe('length range', () => {
  it('uses a stepped scale that is dense where most stories are', () => {
    expect(LENGTH_STOPS).toEqual([1, 2, 3, 5, 7, 10, 15, 20, 30, 45, 60]);
  });

  it.each([
    // [min, max, minutes, expected]  max null = no upper bound ("60+")
    [1, 5, 1, true],
    [1, 5, 5, true],
    [1, 5, 6, false],
    [6, 15, 5, false],
    [7, 15, 10, true],
    [15, null, 70, true],
    [15, null, 14, false],
    [1, null, 70, true],
  ] as const)('min %s max %s: %s min → %s', (min, max, minutes, expected) => {
    expect(inRange(minutes, { min, max })).toBe(expected);
  });

  it('labels stops and ranges for humans', () => {
    expect(stopLabel(60)).toBe('60+ min');
    expect(stopLabel(5)).toBe('5 min');
    expect(formatRange({ min: 1, max: 5 })).toBe('Up to 5 min');
    expect(formatRange({ min: 7, max: 15 })).toBe('7–15 min');
    expect(formatRange({ min: 20, max: null })).toBe('20 min or longer');
    expect(formatRange({ min: 5, max: 5 })).toBe('About 5 min');
    expect(formatRange(FULL_RANGE)).toBe('Any length');
  });

  it('knows the full range means no filter', () => {
    expect(isFullRange(FULL_RANGE)).toBe(true);
    expect(isFullRange({ min: 1, max: 60 })).toBe(true);
    expect(isFullRange({ min: 2, max: null })).toBe(false);
  });
});
