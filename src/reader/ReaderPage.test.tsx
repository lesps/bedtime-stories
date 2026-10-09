import { act, fireEvent, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createStore } from '../storage/store';
import { installFakeIO } from '../test/fakeIntersectionObserver';
import { fixtureStoryBodies, renderApp } from '../test/renderApp';

let io: ReturnType<typeof installFakeIO>;
beforeEach(() => {
  io = installFakeIO();
  window.scrollTo = vi.fn() as typeof window.scrollTo;
  Element.prototype.scrollIntoView = vi.fn();
});

const settle = () => act(() => new Promise((r) => setTimeout(r, 900)));

describe('ReaderPage', () => {
  it('renders the header, blocks and an article', async () => {
    renderApp('/s/aesop--the-heron');
    expect(await screen.findByText('The Heron begins here.')).toBeInTheDocument();
    expect(screen.getByRole('article')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 1, name: 'The Heron' })).toBeInTheDocument();
    expect(screen.getByText(/Illustrated by Milo Winter/)).toHaveTextContent('1 min read');
    expect(screen.getByRole('complementary', { name: 'Moral' })).toHaveTextContent('The end.');
  });

  it('shows the origin when the story has one', async () => {
    renderApp('/s/grimm--rapunzel', createStore(localStorage), {
      'grimm--rapunzel': {
        id: 'grimm--rapunzel',
        collectionId: 'grimm',
        order: 1,
        title: 'Rapunzel',
        wordCount: 100,
        readingMinutes: 9,
        excluded: false,
        flags: [],
        origin: 'Asbjornsen and Moe.',
        moral: null,
        blocks: [{ type: 'p', text: 'Hi.' }],
      },
    });
    expect(await screen.findByText(/Asbjornsen and Moe\./)).toBeInTheDocument();
  });

  it('links previous/next within the collection, skipping hidden stories', async () => {
    renderApp('/s/aesop--the-heron');
    await screen.findByText('The Heron begins here.');
    expect(screen.getByRole('link', { name: /Previous/ })).toHaveAttribute(
      'href',
      '/s/aesop--the-fox-and-the-grapes',
    );
    // aesop--dark-fable (order 3) is mature → skipped
    expect(screen.getByRole('link', { name: /Next/ })).toHaveAttribute(
      'href',
      '/s/aesop--the-lion',
    );
  });

  it('holds back prev/next until the text has loaded, so it does not jump', async () => {
    renderApp('/s/aesop--the-heron');
    // Hold story responses until released; the index still loads normally.
    const real = globalThis.fetch;
    let release!: () => void;
    const gate = new Promise<void>((r) => (release = r));
    vi.stubGlobal('fetch', async (url: string) => {
      if (url.includes('/stories/')) await gate;
      return real(url);
    });
    expect(await screen.findByText('Opening the book…')).toBeInTheDocument();
    expect(screen.queryByRole('navigation', { name: 'More stories' })).not.toBeInTheDocument();
    release();
    await screen.findByText('The Heron begins here.');
    expect(screen.getByRole('navigation', { name: 'More stories' })).toBeInTheDocument();
  });

  it('links its culture and theme tags', async () => {
    renderApp('/s/aesop--the-heron');
    await screen.findByText('The Heron begins here.');
    const tags = screen.getByRole('list', { name: 'Tags' });
    expect(within(tags).getByRole('link', { name: 'Ancient Greek' })).toHaveAttribute(
      'href',
      '/tags/cultures/greek',
    );
    expect(within(tags).getByRole('link', { name: 'Animals' })).toHaveAttribute(
      'href',
      '/tags/themes/animals',
    );
  });

  it('links other visible versions of the same tale', async () => {
    renderApp('/s/grimm--rapunzel');
    await screen.findByText('Rapunzel begins here.');
    const nav = screen.getByRole('navigation', { name: 'Other versions' });
    const links = within(nav).getAllByRole('link');
    expect(links.map((a) => a.getAttribute('href'))).toEqual(['/s/hunt--rapunzel']);
    expect(nav).toHaveTextContent('Household Tales');
  });

  it('has no other-versions list for a tale with one version', async () => {
    renderApp('/s/aesop--the-heron');
    await screen.findByText('The Heron begins here.');
    expect(screen.queryByRole('navigation', { name: 'Other versions' })).not.toBeInTheDocument();
  });

  it('shows a per-book year and source link when the story has them (Potter)', async () => {
    renderApp('/s/aesop--the-lion', createStore(localStorage), {
      'aesop--the-lion': {
        ...fixtureStoryBodies['aesop--the-lion']!,
        firstPublished: 1902,
        source: 'https://www.gutenberg.org/ebooks/14838',
      },
    });
    await screen.findByText('The Lion begins here.');
    expect(screen.getByText(/1902/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Source' })).toHaveAttribute(
      'href',
      'https://www.gutenberg.org/ebooks/14838',
    );
  });

  it('refuses to render a hidden story', async () => {
    renderApp('/s/grimm--hidden-tale');
    expect(
      await screen.findByRole('heading', { name: 'This story is hidden' }),
    ).toBeInTheDocument();
    expect(screen.queryByText('Hidden Tale begins here.')).not.toBeInTheDocument();
  });

  it('persists reader settings', async () => {
    const { store } = renderApp('/s/aesop--the-heron');
    await screen.findByText('The Heron begins here.');
    await userEvent.click(screen.getByRole('button', { name: 'Reading settings' }));
    await userEvent.click(screen.getByRole('radio', { name: 'Dark' }));
    await userEvent.click(screen.getByRole('button', { name: 'Larger text' }));
    await userEvent.click(screen.getByRole('checkbox', { name: 'Relaxed line spacing' }));
    expect(store.get().settings).toMatchObject({
      theme: 'dark',
      fontSize: 3,
      lineHeight: 'relaxed',
    });
    expect(document.documentElement.dataset.theme).toBe('dark');
    expect(createStore(localStorage).get().settings.theme).toBe('dark');
    expect(screen.getByRole('article').style.getPropertyValue('--reader-size')).toBe('22px');
  });

  it('saves the topmost block and jumps straight back there on reopen, without asking', async () => {
    const first = renderApp('/s/aesop--the-heron');
    await screen.findByText('The Heron begins here.');
    act(() => io.show([2]));
    await settle();
    expect(first.store.get().progress['aesop--the-heron']?.blockIndex).toBe(2);
    first.unmount();

    renderApp('/s/aesop--the-heron', first.store);
    await screen.findByText('The Heron begins here.');
    expect(Element.prototype.scrollIntoView).toHaveBeenCalledTimes(1);
    expect(
      screen.queryByRole('button', { name: /Continue from|Start over/ }),
    ).not.toBeInTheDocument();
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  it('starts a finished story from the top, keeping it read', async () => {
    const store = createStore(localStorage);
    store.finishStory('aesop--the-heron', 4);
    renderApp('/s/aesop--the-heron', store);
    await screen.findByText('The Heron begins here.');
    expect(Element.prototype.scrollIntoView).not.toHaveBeenCalled();
    act(() => io.show([1]));
    await settle();
    expect(store.get().progress['aesop--the-heron']).toMatchObject({ blockIndex: 1 });
    expect(store.get().progress['aesop--the-heron']).not.toHaveProperty('finished');
    expect(store.get().history.map((h) => h.id)).toEqual(['aesop--the-heron']);
  });

  it('does not overwrite the saved place while the top of the story is on screen', async () => {
    const store = createStore(localStorage);
    store.setProgress('aesop--the-heron', 2);
    renderApp('/s/aesop--the-heron', store);
    await screen.findByText('The Heron begins here.');
    act(() => io.show([0, 1]));
    act(() => io.show([0]));
    await settle();
    expect(store.get().progress['aesop--the-heron']?.blockIndex).toBe(2);
  });

  it('marks read and records the position as finished when the final block is seen', async () => {
    const store = createStore(localStorage);
    store.setProgress('aesop--the-heron', 1);
    renderApp('/s/aesop--the-heron', store);
    await screen.findByText('The Heron begins here.');
    act(() => io.show([2, 3]));
    await settle();
    expect(store.get().progress['aesop--the-heron']).toMatchObject({
      finished: true,
      blockCount: 4,
    });
    expect(store.get().history.map((h) => h.id)).toEqual(['aesop--the-heron']);
  });

  it('closes the reading settings panel on Escape or a click elsewhere', async () => {
    renderApp('/s/aesop--the-heron');
    await screen.findByText('The Heron begins here.');
    const aa = screen.getByRole('button', { name: 'Reading settings' });
    await userEvent.click(aa);
    expect(screen.getByRole('radiogroup', { name: 'Theme' })).toBeInTheDocument();
    await userEvent.keyboard('{Escape}');
    expect(screen.queryByRole('radiogroup', { name: 'Theme' })).not.toBeInTheDocument();
    expect(aa).toHaveFocus();
    await userEvent.click(aa);
    await userEvent.click(screen.getByText('The Heron begins here.'));
    expect(screen.queryByRole('radiogroup', { name: 'Theme' })).not.toBeInTheDocument();
  });

  it('tucks the reader bar away while scrolling down and brings it back on scroll up', async () => {
    renderApp('/s/aesop--the-heron');
    await screen.findByText('The Heron begins here.');
    const bar = screen.getByRole('button', { name: 'Close book' }).closest('[data-hidden]')!;
    expect(bar).toHaveAttribute('data-hidden', 'false');
    const scrollTo = (y: number) => {
      window.scrollY = y;
      fireEvent.scroll(window);
    };
    act(() => scrollTo(400));
    expect(bar).toHaveAttribute('data-hidden', 'true');
    act(() => scrollTo(300));
    expect(bar).toHaveAttribute('data-hidden', 'false');
    act(() => scrollTo(600));
    expect(bar).toHaveAttribute('data-hidden', 'true');
    act(() => screen.getByRole('button', { name: 'Notes' }).focus());
    expect(bar).toHaveAttribute('data-hidden', 'false');
    act(() => scrollTo(0));
  });

  it('explains when a story is not available offline', async () => {
    renderApp('/s/aesop--the-heron');
    await screen.findByText('The Heron begins here.'); // index loaded
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        throw new TypeError('Failed to fetch');
      }),
    );
    await userEvent.click(screen.getByRole('link', { name: /Next/ }));
    expect(await screen.findByText(/isn’t saved for offline reading yet/)).toBeInTheDocument();
  });

  it('favorites from the reader header', async () => {
    const { store } = renderApp('/s/aesop--the-heron');
    await userEvent.click(await screen.findByRole('button', { name: 'Favorite The Heron' }));
    expect(store.get().favorites).toHaveProperty('aesop--the-heron');
  });

  describe('open story (Reading tab)', () => {
    it('marks a visible story as open, and saves progress with its block count', async () => {
      const { store } = renderApp('/s/aesop--the-heron');
      await screen.findByText('The Heron begins here.');
      expect(store.get().openStoryId).toBe('aesop--the-heron');
      act(() => io.show([2]));
      await settle();
      expect(store.get().progress['aesop--the-heron']).toMatchObject({
        blockIndex: 2,
        blockCount: 4,
      });
    });

    it('does not open a hidden story', async () => {
      const { store } = renderApp('/s/grimm--hidden-tale');
      await screen.findByRole('heading', { name: 'This story is hidden' });
      expect(store.get().openStoryId).toBeNull();
    });

    it('closes the story when it is finished', async () => {
      const { store } = renderApp('/s/aesop--the-heron');
      await screen.findByText('The Heron begins here.');
      act(() => io.show([3]));
      expect(store.get().openStoryId).toBeNull();
    });

    it('Close book clears it and goes to the shelf', async () => {
      const { store } = renderApp('/s/aesop--the-heron');
      await screen.findByText('The Heron begins here.');
      await userEvent.click(screen.getByRole('button', { name: 'Close book' }));
      expect(store.get().openStoryId).toBeNull();
      expect(await screen.findByRole('heading', { level: 1, name: 'Reading' })).toBeInTheDocument();
    });
  });
});
