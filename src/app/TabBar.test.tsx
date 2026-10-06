import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createStore } from '../storage/store';
import { installFakeIO } from '../test/fakeIntersectionObserver';
import { renderApp } from '../test/renderApp';

const tab = (name: string) =>
  within(screen.getByRole('navigation', { name: 'Main' })).getByRole('link', { name });

const setScrollY = (y: number) =>
  Object.defineProperty(window, 'scrollY', { value: y, configurable: true, writable: true });

beforeEach(() => {
  installFakeIO();
  Element.prototype.scrollIntoView = vi.fn();
  window.scrollTo = vi.fn() as typeof window.scrollTo;
  setScrollY(0);
});

describe('tab bar', () => {
  it.each([
    ['/c/aesop', 'Library'],
    ['/tags/themes/animals', 'Library'],
    ['/s/aesop--the-heron', 'Reading'],
    ['/about', 'Settings'],
    ['/surprise', 'Surprise'],
  ])('marks the section of %s (%s) as current', async (path, name) => {
    renderApp(path);
    await screen.findByRole('navigation', { name: 'Main' });
    await vi.waitFor(() => expect(tab(name)).toHaveAttribute('aria-current', 'page'));
    for (const other of ['Library', 'Surprise', 'Reading', 'Favorites', 'Settings'].filter(
      (n) => n !== name,
    )) {
      expect(tab(other)).not.toHaveAttribute('aria-current');
    }
  });

  it('tapping Reading while reading closes the book and shows the shelf', async () => {
    const store = createStore(localStorage);
    renderApp('/s/aesop--the-heron', store);
    await screen.findByText('The Heron begins here.');
    expect(store.get().openStoryId).toBe('aesop--the-heron');
    await userEvent.click(tab('Reading'));
    expect(await screen.findByRole('heading', { level: 1, name: 'Reading' })).toBeInTheDocument();
    expect(store.get().openStoryId).toBeNull();
  });

  it('tapping Library from inside a collection goes back to the library', async () => {
    renderApp('/c/aesop');
    await screen.findByRole('heading', { level: 1, name: 'The Aesop for Children' });
    await userEvent.click(tab('Library'));
    expect(await screen.findByRole('heading', { name: 'Browse by' })).toBeInTheDocument();
  });

  it('tapping Library on the library scrolls to the top first, then resets search and filters', async () => {
    renderApp('/?by=themes');
    const search = await screen.findByRole('searchbox');
    await userEvent.type(search, 'heron');
    setScrollY(500);
    await userEvent.click(tab('Library'));
    expect(window.scrollTo).toHaveBeenCalledWith(expect.objectContaining({ top: 0 }));
    expect(screen.getByRole('searchbox')).toHaveValue('heron');

    setScrollY(0);
    await userEvent.click(tab('Library'));
    expect(await screen.findByRole('searchbox')).toHaveValue('');
    expect(screen.getByRole('radio', { name: 'Collections' })).toHaveAttribute(
      'aria-checked',
      'true',
    );
  });

  it('tapping a different tab just goes there', async () => {
    renderApp('/');
    await screen.findByRole('heading', { name: 'Browse by' });
    await userEvent.click(tab('Surprise'));
    expect(
      await screen.findByRole('heading', { level: 1, name: 'Surprise me' }),
    ).toBeInTheDocument();
  });
});
