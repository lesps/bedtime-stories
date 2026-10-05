import { fireEvent, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createStore } from '../storage/store';
import { renderApp } from '../test/renderApp';

beforeEach(() => {
  // Reduced motion by default: no flip animation.
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
    expect(createStore(localStorage).get().settings.picker).toMatchObject({
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

  it('does not flip the card under reduced motion', async () => {
    renderApp('/surprise');
    await userEvent.click(await screen.findByRole('button', { name: 'Pick a story' }));
    expect(await screen.findByRole('region', { name: 'Your story' })).not.toHaveClass('flip');
  });

  it('flips in with motion allowed', async () => {
    vi.stubGlobal('matchMedia', () => ({
      matches: false,
      addEventListener() {},
      removeEventListener() {},
    }));
    renderApp('/surprise');
    await userEvent.click(await screen.findByRole('button', { name: 'Pick a story' }));
    expect(await screen.findByRole('region', { name: 'Your story' })).toHaveClass('flip');
  });

  it('applies a preset: Quick & gentle', async () => {
    const { store } = renderApp('/surprise');
    await userEvent.click(await screen.findByRole('button', { name: /Quick & gentle/ }));
    expect(screen.getByRole('group', { name: 'Length' })).toHaveTextContent('Up to 5 min');
    expect(store.get().settings.picker.themes).toEqual({ include: ['gentle'], exclude: [] });
    await userEvent.click(screen.getByRole('button', { name: 'Pick a story' }));
    await screen.findByRole('region', { name: 'Your story' });
    expect(store.get().recentPicks.at(-1)).toBe('aesop--the-heron');
  });

  it('offers three at once', async () => {
    const { store } = renderApp('/surprise');
    await userEvent.click(await screen.findByRole('radio', { name: 'Give me 3' }));
    fireEvent.change(screen.getByRole('slider', { name: 'Longest' }), { target: { value: '10' } });
    await userEvent.click(screen.getByRole('button', { name: 'Pick 3 stories' }));
    const cards = await screen.findAllByRole('region', { name: /Choice \d/ });
    expect(cards).toHaveLength(3);
    for (const c of cards)
      expect(within(c).getByRole('link', { name: /Read/ })).toBeInTheDocument();
    expect(store.get().recentPicks).toHaveLength(3);
    expect(store.get().settings.picker.count).toBe(3);
  });

  it('says so when fewer stories match than were asked for', async () => {
    renderApp('/surprise');
    await userEvent.click(await screen.findByRole('radio', { name: 'Give me 3' }));
    await userEvent.click(screen.getByText('More filters'));
    await userEvent.click(screen.getByRole('button', { name: /Gentle & cosy: any/ }));
    await userEvent.click(screen.getByRole('button', { name: 'Pick 3 stories' }));
    expect(await screen.findByRole('region', { name: 'Your story' })).toBeInTheDocument();
    expect(screen.getByText('Only 1 story matches these filters.')).toBeInTheDocument();
  });

  it('includes a culture on one tap and excludes a theme on two', async () => {
    const { store } = renderApp('/surprise');
    await userEvent.click(await screen.findByText('More filters'));
    fireEvent.change(screen.getByRole('slider', { name: 'Longest' }), { target: { value: '10' } });
    const royalty = screen.getByRole('button', { name: /Kings, queens & castles/ });
    await userEvent.click(royalty);
    expect(royalty).toHaveAccessibleName('Kings, queens & castles: included');
    await userEvent.click(royalty);
    expect(royalty).toHaveAccessibleName('Kings, queens & castles: excluded');
    for (let i = 0; i < 6; i++) {
      await userEvent.click(screen.getByRole('button', { name: /Pick (a story|again)/ }));
      await screen.findByRole('region', { name: 'Your story' });
    }
    expect(store.get().recentPicks.every((id) => id.startsWith('aesop'))).toBe(true);

    await userEvent.click(royalty);
    expect(royalty).toHaveAccessibleName('Kings, queens & castles: any');
    await userEvent.click(screen.getByRole('button', { name: /German/ }));
    expect(store.get().settings.picker.cultures).toEqual({ include: ['german'], exclude: [] });
  });

  it('lists recent picks with links, newest first', async () => {
    const store = createStore(localStorage);
    store.recordPick('aesop--the-lion');
    store.recordPick('aesop--the-heron');
    renderApp('/surprise', store);
    const recent = await screen.findByRole('list', { name: 'Recently picked' });
    expect(
      within(recent)
        .getAllByRole('link')
        .map((a) => a.textContent),
    ).toEqual(['The Heron', 'The Lion']);
  });

  it('resets filters to the defaults, keeping the count', async () => {
    const { store } = renderApp('/surprise');
    await userEvent.click(await screen.findByRole('radio', { name: 'Give me 3' }));
    await userEvent.click(screen.getByRole('button', { name: /Old favorite/ }));
    await userEvent.click(screen.getByText('More filters'));
    await userEvent.click(screen.getByRole('button', { name: 'Reset filters' }));
    expect(store.get().settings.picker).toMatchObject({
      favoritesOnly: false,
      maxMinutes: 5,
      count: 3,
    });
  });
});
