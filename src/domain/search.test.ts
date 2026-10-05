import { describe, expect, it } from 'vitest';
import { entry } from '../test/fixtures';
import { matchesQuery, normalize } from './search';

describe('search', () => {
  it('normalizes case, accents, apostrophes and punctuation', () => {
    expect(normalize('The Elephant’s Child!')).toBe('the elephants child');
    expect(normalize('  Rapunzel —  Ölaf ')).toBe('rapunzel olaf');
  });
  it('matches when every word appears in the title, in any order', () => {
    const e = entry({ id: 'k--e', title: 'The Elephant’s Child' });
    expect(matchesQuery(e, 'elephants')).toBe(true);
    expect(matchesQuery(e, "child elephant's")).toBe(true);
    expect(matchesQuery(e, 'elephant tiger')).toBe(false);
    expect(matchesQuery(e, '   ')).toBe(true);
  });
});
