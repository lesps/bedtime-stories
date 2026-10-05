import { describe, expect, it } from 'vitest';
import { resolveTheme, THEME_COLORS } from './theme';

describe('resolveTheme', () => {
  it('follows the OS in system mode (sepia by day, dark by night)', () => {
    expect(resolveTheme('system', false)).toBe('sepia');
    expect(resolveTheme('system', true)).toBe('dark');
  });
  it('honours an explicit choice regardless of OS', () => {
    expect(resolveTheme('light', true)).toBe('light');
    expect(resolveTheme('dark', false)).toBe('dark');
    expect(resolveTheme('sepia', true)).toBe('sepia');
  });
  it('has a browser theme colour per theme', () => {
    expect(Object.keys(THEME_COLORS).sort()).toEqual(['dark', 'light', 'sepia']);
  });
});
