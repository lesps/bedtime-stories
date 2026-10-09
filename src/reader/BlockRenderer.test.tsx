import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { BlockRenderer } from './BlockRenderer';

describe('BlockRenderer', () => {
  it('renders a paragraph', () => {
    render(<BlockRenderer index={0} block={{ type: 'p', text: 'Once upon a time.' }} />);
    expect(screen.getByText('Once upon a time.').tagName).toBe('P');
  });

  it('renders verse preserving newlines and leading spaces', () => {
    const text = 'This is the way\n  of the Whale';
    const { container } = render(<BlockRenderer index={1} block={{ type: 'verse', text }} />);
    const el = container.querySelector('.verse')!;
    expect(el.textContent).toBe(text);
    expect(el).toHaveAttribute('data-block', '1');
  });

  it('renders a moral as a labelled card', () => {
    render(<BlockRenderer index={2} block={{ type: 'moral', text: 'Slow and steady.' }} />);
    expect(screen.getByRole('complementary', { name: 'Moral' })).toHaveTextContent(
      'Slow and steady.',
    );
  });

  it('renders a heading as h2', () => {
    render(<BlockRenderer index={3} block={{ type: 'heading', text: 'Chapter I' }} />);
    expect(screen.getByRole('heading', { level: 2, name: 'Chapter I' })).toBeInTheDocument();
  });

  it('renders a note as a small aside', () => {
    render(<BlockRenderer index={4} block={{ type: 'note', text: 'A footnote.' }} />);
    const note = screen.getByRole('complementary', { name: 'Note' });
    expect(note.querySelector('small')).toHaveTextContent('A footnote.');
  });

  it('renders an image as a lazy figure with alt, relative to the compendium', () => {
    render(
      <BlockRenderer
        index={5}
        block={{ type: 'image', src: 'images/aesop/i001.jpg', alt: 'THE HERON' }}
      />,
    );
    const img = screen.getByRole('img', { name: 'THE HERON' });
    expect(img).toHaveAttribute('loading', 'lazy');
    expect(img.getAttribute('src')).toMatch(/compendium\/images\/aesop\/i001\.jpg$/);
    expect(img.closest('figure')).not.toBeNull();
    // Intrinsic size reserves space before the image loads (no layout shift).
    expect(img).toHaveAttribute('width', '679');
    expect(img).toHaveAttribute('height', '977');
    // Lets CSS cap the height (70vh) while keeping the box sized before the image loads.
    expect(img.style.getPropertyValue('--ar')).toBe(String(679 / 977));
    expect(img.style.getPropertyValue('--w')).toBe('679px');
  });

  it('loads a priority image eagerly so it can be the fast first paint', () => {
    render(
      <BlockRenderer
        index={0}
        priority
        block={{ type: 'image', src: 'images/aesop/i001.jpg', alt: 'THE HERON' }}
      />,
    );
    const img = screen.getByRole('img', { name: 'THE HERON' });
    expect(img).toHaveAttribute('loading', 'eager');
    expect(img).toHaveAttribute('fetchpriority', 'high');
  });
});
