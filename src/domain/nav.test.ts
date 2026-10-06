import { describe, expect, it } from 'vitest';
import { sectionOf, tabTap } from './nav';

describe('sectionOf', () => {
  it.each([
    ['/', 'library'],
    ['/c/aesop', 'library'],
    ['/tags/themes/gentle', 'library'],
    ['/surprise', 'surprise'],
    ['/reading', 'reading'],
    ['/s/aesop--the-heron', 'reading'],
    ['/favorites', 'favorites'],
    ['/settings', 'settings'],
    ['/about', 'settings'],
    ['/nope', null],
  ] as const)('%s → %s', (path, section) => expect(sectionOf(path)).toBe(section));
});

describe('tabTap', () => {
  it.each([
    // [tab, pathname, scrolled, expected]
    ['library', '/surprise', false, { type: 'navigate', to: '/' }],
    ['reading', '/', true, { type: 'navigate', to: '/reading' }],
    ['library', '/c/aesop', true, { type: 'navigate', to: '/' }],
    ['library', '/tags/themes/gentle', false, { type: 'navigate', to: '/' }],
    ['library', '/', true, { type: 'scrollTop' }],
    ['library', '/', false, { type: 'reset' }],
    ['reading', '/s/aesop--the-heron', true, { type: 'closeBook', storyId: 'aesop--the-heron' }],
    ['reading', '/s/aesop--the-heron', false, { type: 'closeBook', storyId: 'aesop--the-heron' }],
    ['reading', '/reading', true, { type: 'scrollTop' }],
    ['reading', '/reading', false, { type: 'none' }],
    ['settings', '/about', false, { type: 'navigate', to: '/settings' }],
    ['surprise', '/surprise', true, { type: 'scrollTop' }],
    ['favorites', '/favorites', false, { type: 'none' }],
  ] as const)('tap %s on %s (scrolled %s) → %o', (tab, path, scrolled, expected) => {
    expect(tabTap(tab, path, scrolled)).toEqual(expected);
  });
});
