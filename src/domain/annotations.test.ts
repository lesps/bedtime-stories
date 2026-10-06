import { describe, expect, it } from 'vitest';
import { resolveAnchor, segments } from './annotations';

const text = 'Once upon a time there lived a king who had three sons.';

describe('resolveAnchor', () => {
  it('keeps an anchor whose offsets still match the quote', () => {
    expect(resolveAnchor(text, { start: 5, end: 16, quote: 'upon a time' })).toEqual({
      start: 5,
      end: 16,
    });
  });

  it('relocates by quote when the offsets drifted', () => {
    expect(resolveAnchor(`Long ago. ${text}`, { start: 5, end: 16, quote: 'upon a time' })).toEqual(
      {
        start: 15,
        end: 26,
      },
    );
  });

  it('picks the occurrence nearest the old offset when the quote repeats', () => {
    const t = 'the cat and the dog and the bird';
    expect(resolveAnchor(t, { start: 25, end: 28, quote: 'the' })).toEqual({ start: 24, end: 27 });
  });

  it('is detached (null) when the quote is gone', () => {
    expect(resolveAnchor(text, { start: 0, end: 5, quote: 'Twice' })).toBeNull();
  });
});

describe('segments', () => {
  it('splits text into plain and marked runs', () => {
    expect(
      segments('abcdefghij', [
        { id: 'b', start: 6, end: 8 },
        { id: 'a', start: 1, end: 3 },
      ]),
    ).toEqual([
      { text: 'a' },
      { text: 'bc', id: 'a' },
      { text: 'def' },
      { text: 'gh', id: 'b' },
      { text: 'ij' },
    ]);
  });

  it('lets an earlier mark win where two overlap, and clamps to the text', () => {
    expect(
      segments('abcdef', [
        { id: 'a', start: 1, end: 4 },
        { id: 'b', start: 3, end: 99 },
      ]),
    ).toEqual([{ text: 'a' }, { text: 'bcd', id: 'a' }, { text: 'ef', id: 'b' }]);
  });

  it('returns the whole text when there are no marks', () => {
    expect(segments('abc', [])).toEqual([{ text: 'abc' }]);
  });
});
