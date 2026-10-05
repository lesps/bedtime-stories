import { describe, expect, it } from 'vitest';
import { entry } from '../test/fixtures';
import { isVisible } from './visibility';

describe('isVisible', () => {
  const plain = entry({ id: 'a--plain' });
  const mature = entry({ id: 'a--mature', flags: ['mature-themes'] });
  const excluded = entry({ id: 'a--excl', excluded: true });
  const both = entry({ id: 'a--both', excluded: true, flags: ['mature-themes'] });
  const slurOnly = entry({ id: 'a--slur', flags: ['racial-slur'] });

  it.each([
    // entry, showMature, showExcluded, expected
    [plain, false, false, true],
    [plain, true, false, true],
    [plain, false, true, true],
    [plain, true, true, true],
    [mature, false, false, false],
    [mature, true, false, true],
    [mature, false, true, false],
    [mature, true, true, true],
    [excluded, false, false, false],
    [excluded, true, false, false],
    [excluded, false, true, true],
    [excluded, true, true, true],
    [both, false, false, false],
    [both, true, false, false],
    [both, false, true, false],
    [both, true, true, true],
    [slurOnly, false, false, true],
  ] as const)('%#: %o mature=%s excluded=%s → %s', (e, showMature, showExcluded, expected) => {
    expect(isVisible(e, { showMature, showExcluded })).toBe(expected);
  });
});
