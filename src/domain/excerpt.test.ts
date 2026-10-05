import { describe, expect, it } from 'vitest';
import { excerpt } from './excerpt';

describe('excerpt', () => {
  it('takes the first ~25 words of prose, skipping images and headings', () => {
    const words = Array.from({ length: 40 }, (_, i) => `w${i}`).join(' ');
    const text = excerpt([
      { type: 'image', src: 'x', alt: 'x' },
      { type: 'heading', text: 'Chapter I' },
      { type: 'p', text: words },
    ]);
    expect(text.split(' ')).toHaveLength(25);
    expect(text.endsWith('…')).toBe(true);
  });
  it('spans paragraphs and does not add an ellipsis when short', () => {
    expect(
      excerpt([
        { type: 'p', text: 'One two.' },
        { type: 'verse', text: 'Three\nfour' },
      ]),
    ).toBe('One two. Three four');
  });
});
