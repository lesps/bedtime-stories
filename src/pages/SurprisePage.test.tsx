import { fireEvent, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createStore } from '../storage/store';
import { renderApp } from '../test/renderApp';

beforeEach(() => {
  // Reduced motion → no shuffle animation, deterministic reveal.
  vi.stubGlobal('matchMedia', (q: string) => ({
    matches: q.includes('reduced-motion'),
    addEventListener() {},
    removeEventListener() {},
  }));
});

describe('SurprisePage', () => {
  it('defaults to Under 5 min and picks a visible matching story with an excerpt', async () => {
    const { store } = renderApp('/surprise');
    expect(await screen.findByRole('group', { name: 'Length' })).toHaveTextContent('Up to 5 min');
    await userEvent.click(screen.getByRole('button', { name: 'Pick a story' }));
    const card = await screen.findByRole('region', { name: 'Your story' });
    const id = store.get().recentPicks.at(-1)!;
    expect(['aesop--the-heron', 'aesop--the-fox-and-the-grapes', 'aesop--the-lion']).toContain(id);
    expect(card).toHaveTextContent(/begins here\. Middle part\./);
    expect(screen.getByRole('link', { name: 'Read it' })).toHaveAttribute('href', `/s/${id}`);
  });

  it('persists filter choices in settings', async () => {
    renderApp('/surprise');
    await userEvent.click(await screen.findByRole('button', { name: "Grimms' Fairy Tales" }));
    fireEvent.change(screen.getByRole('slider', { name: 'Longest' }), { target: { value: '10' } });
    fireEvent.change(screen.getByRole('slider', { name: 'Shortest' }), { target: { value: '6' } });
    await userEvent.click(screen.getByRole('checkbox', { name: 'Unread only' }));
    expect(createStore(localStorage).get().settings.picker).toEqual({
      collections: ['grimm'],
      minMinutes: 15,
      maxMinutes: null,
      unreadOnly: true,
      favoritesOnly: false,
    });
  });

  it('can pick only long stories', async () => {
    const { store } = renderApp('/surprise');
    fireEvent.change(await screen.findByRole('slider', { name: 'Longest' }), {
      target: { value: '10' },
    });
    fireEvent.change(screen.getByRole('slider', { name: 'Shortest' }), { target: { value: '6' } });
    await userEvent.click(screen.getByRole('button', { name: 'Pick a story' }));
    await screen.findByRole('region', { name: 'Your story' });
    expect(store.get().recentPicks.at(-1)).toBe('grimm--the-long-one');
  });

  it('explains when nothing matches', async () => {
    renderApp('/surprise');
    await userEvent.click(await screen.findByRole('checkbox', { name: 'Favorites only' }));
    await userEvent.click(screen.getByRole('button', { name: 'Pick a story' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('No stories match');
  });

  it('pick again avoids the previous pick', async () => {
    const { store } = renderApp('/surprise');
    await userEvent.click(await screen.findByRole('button', { name: 'Pick a story' }));
    await screen.findByRole('region', { name: 'Your story' });
    await userEvent.click(screen.getByRole('button', { name: 'Pick again' }));
    await userEvent.click(screen.getByRole('button', { name: 'Pick again' }));
    const picks = store.get().recentPicks;
    expect(new Set(picks).size).toBe(3);
  });

  it('shuffles briefly before revealing when motion is allowed', async () => {
    vi.stubGlobal('matchMedia', () => ({
      matches: false,
      addEventListener() {},
      removeEventListener() {},
    }));
    renderApp('/surprise');
    await userEvent.click(await screen.findByRole('button', { name: 'Pick a story' }));
    expect(screen.queryByRole('region', { name: 'Your story' })).not.toBeInTheDocument();
    expect(document.querySelector('.shuffling')).not.toBeNull();
    expect(
      await screen.findByRole('region', { name: 'Your story' }, { timeout: 2000 }),
    ).toBeInTheDocument();
  });
});
