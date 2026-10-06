import { screen, within } from '@testing-library/react';
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
    store.setProgress('grimm--rapunzel', 1, 4);
    store.setProgress('aesop--the-lion', 3, 4);
    store.markRead('aesop--the-heron');
    renderApp('/reading', store);
    expect(await screen.findByRole('heading', { level: 1, name: 'Reading' })).toBeInTheDocument();

    const hero = screen.getByRole('region', { name: 'Pick up where you left off' });
    expect(hero).toHaveTextContent('The Lion');
    expect(hero).toHaveTextContent('75%');
    expect(within(hero).getByRole('link', { name: /Keep reading/ })).toHaveAttribute(
      'href',
      '/s/aesop--the-lion?resume=1',
    );
    const others = screen.getByRole('list', { name: 'Also in progress' });
    expect(others).toHaveTextContent('Rapunzel');
    expect(others).toHaveTextContent('25%');
    expect(screen.getByRole('list', { name: 'Recently finished' })).toHaveTextContent('The Heron');
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
});
