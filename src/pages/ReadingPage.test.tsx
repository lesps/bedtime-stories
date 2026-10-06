import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createStore } from '../storage/store';
import { installFakeIO } from '../test/fakeIntersectionObserver';
import { renderApp } from '../test/renderApp';

beforeEach(() => {
  installFakeIO();
  Element.prototype.scrollIntoView = vi.fn();
});

describe('ReadingPage', () => {
  it('goes straight into the open story at its saved place', async () => {
    const store = createStore(localStorage);
    store.setProgress('grimm--rapunzel', 2, 4);
    store.openStory('grimm--rapunzel');
    renderApp('/reading', store);
    expect(await screen.findByText('Rapunzel begins here.')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 1, name: 'Rapunzel' })).toBeInTheDocument();
    expect(Element.prototype.scrollIntoView).toHaveBeenCalled();
  });

  it('shows the shelf when no story is open', async () => {
    let t = 0;
    const store = createStore(localStorage, () => ++t);
    store.finishStory('aesop--the-heron', 4);
    store.finishStory('grimm--the-long-one', 4);
    store.setProgress('grimm--the-long-one', 1, 4); // a reread in progress
    store.setProgress('grimm--rapunzel', 1, 4);
    store.setProgress('aesop--the-lion', 3, 4);
    renderApp('/reading', store);
    expect(await screen.findByRole('heading', { level: 1, name: 'Reading' })).toBeInTheDocument();

    const hero = screen.getByRole('region', { name: 'Pick up where you left off' });
    expect(hero).toHaveTextContent('The Lion');
    expect(hero).toHaveTextContent('75%');
    expect(within(hero).getByRole('link', { name: /Keep reading/ })).toHaveAttribute(
      'href',
      '/s/aesop--the-lion',
    );
    const others = screen.getByRole('list', { name: 'Also in progress' });
    expect(others).toHaveTextContent('Rapunzel');
    expect(others).toHaveTextContent('The Long One');
    expect(others).not.toHaveTextContent('The Heron');
    expect(others).toHaveTextContent('25%');
    expect(screen.getByRole('list', { name: 'Recently finished' })).toHaveTextContent('The Heron');
  });

  it('Start over on the shelf forgets the place and opens the story at the top', async () => {
    let t = 0;
    const store = createStore(localStorage, () => ++t);
    store.setProgress('grimm--rapunzel', 1, 4);
    store.setProgress('aesop--the-lion', 3, 4);
    renderApp('/reading', store);
    const hero = await screen.findByRole('region', { name: 'Pick up where you left off' });
    await userEvent.click(within(hero).getByRole('button', { name: 'Start The Lion over' }));
    expect(await screen.findByText('The Lion begins here.')).toBeInTheDocument();
    expect(store.get().progress['aesop--the-lion']).toBeUndefined();
    expect(Element.prototype.scrollIntoView).not.toHaveBeenCalled();
  });

  it('offers Start over on each other story in progress', async () => {
    let t = 0;
    const store = createStore(localStorage, () => ++t);
    store.setProgress('grimm--rapunzel', 1, 4);
    store.setProgress('aesop--the-lion', 3, 4);
    renderApp('/reading', store);
    const others = await screen.findByRole('list', { name: 'Also in progress' });
    await userEvent.click(within(others).getByRole('button', { name: 'Start Rapunzel over' }));
    expect(await screen.findByText('Rapunzel begins here.')).toBeInTheDocument();
    expect(store.get().progress['grimm--rapunzel']).toBeUndefined();
    expect(store.get().progress['aesop--the-lion']).toBeDefined();
  });

  it('shows the shelf when the open story is hidden by settings', async () => {
    const store = createStore(localStorage);
    store.openStory('aesop--dark-fable');
    renderApp('/reading', store);
    expect(await screen.findByRole('heading', { level: 1, name: 'Reading' })).toBeInTheDocument();
  });

  it('has an empty state', async () => {
    renderApp('/reading');
    expect(await screen.findByText(/Nothing on the go/)).toBeInTheDocument();
  });

  it('is the middle tab, and is current while reading the open story', async () => {
    const store = createStore(localStorage);
    store.openStory('aesop--the-heron');
    renderApp('/s/aesop--the-heron', store);
    await screen.findByText('The Heron begins here.');
    const tabs = within(screen.getByRole('navigation', { name: 'Main' })).getAllByRole('link');
    expect(tabs.map((a) => a.textContent)).toEqual([
      'Library',
      'Surprise',
      'Reading',
      'Favorites',
      'Settings',
    ]);
    expect(tabs[2]).toHaveAttribute('aria-current', 'page');
  });

  it('lists annotated stories in a Notebook, linking to their notes, and exports Markdown', async () => {
    const store = createStore(localStorage);
    store.addHighlight('aesop--the-heron', {
      block: 1,
      start: 0,
      end: 6,
      quote: 'Middle',
      color: 'yellow',
      note: 'Read slowly',
    });
    store.setStoryNote('grimm--rapunzel', 'Long but loved');
    renderApp('/reading', store);
    const book = await screen.findByRole('list', { name: 'Notebook' });
    const items = within(book).getAllByRole('link');
    expect(items.map((a) => a.getAttribute('href')).sort()).toEqual([
      '/s/aesop--the-heron?notes=1',
      '/s/grimm--rapunzel?notes=1',
    ]);
    expect(book).toHaveTextContent('1 highlight · 1 note');

    let blob: Blob | undefined;
    vi.stubGlobal('URL', {
      ...URL,
      createObjectURL: (b: Blob) => ((blob = b), 'blob:x'),
      revokeObjectURL() {},
    });
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
    await userEvent.click(screen.getByRole('button', { name: 'Export notes' }));
    expect(click).toHaveBeenCalled();
    const md = await blob!.text();
    expect(md).toContain('## The Heron');
    expect(md).toContain('> Middle');
    expect(md).toContain('Long but loved');
  });
});
