import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { createStore } from '../storage/store';
import { renderApp } from '../test/renderApp';

describe('favorites', () => {
  it('toggles from a story row and lists most recent first', async () => {
    let t = 0;
    const store = createStore(localStorage, () => ++t);
    renderApp('/c/aesop', store);
    await userEvent.click(await screen.findByRole('button', { name: 'Favorite The Heron' }));
    await userEvent.click(screen.getByRole('button', { name: 'Favorite The Lion' }));
    expect(screen.getByRole('button', { name: 'Favorite The Lion' })).toHaveAttribute(
      'aria-pressed',
      'true',
    );

    await userEvent.click(screen.getByRole('link', { name: 'Favorites' }));
    const list = await screen.findByRole('list', { name: 'Favorites' });
    expect(
      within(list)
        .getAllByRole('listitem')
        .map((r) => r.querySelector('.story-title')?.textContent),
    ).toEqual(['The Lion', 'The Heron']);
  });

  it('shows an empty state', async () => {
    renderApp('/favorites');
    expect(await screen.findByText(/No favorites yet/)).toBeInTheDocument();
  });

  it('hides favorited stories that become hidden', async () => {
    const store = createStore(localStorage);
    store.updateSettings({ showMature: true });
    store.toggleFavorite('aesop--dark-fable');
    store.updateSettings({ showMature: false });
    renderApp('/favorites', store);
    expect(await screen.findByText(/No favorites yet/)).toBeInTheDocument();
  });
});
