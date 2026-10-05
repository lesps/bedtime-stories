import { describe, expect, it } from 'vitest';
import { lengthOf } from './length';

describe('lengthOf', () => {
  it.each([
    [1, 'short'],
    [5, 'short'],
    [6, 'medium'],
    [15, 'medium'],
    [16, 'long'],
    [60, 'long'],
  ] as const)('%i min → %s', (m, bucket) => expect(lengthOf(m)).toBe(bucket));
});
