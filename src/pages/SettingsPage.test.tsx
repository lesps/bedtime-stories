import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { createStore } from '../storage/store';
import { renderApp } from '../test/renderApp';

describe('SettingsPage', () => {
  it('toggles content visibility settings', async () => {
    const { store } = renderApp('/settings');
    await userEvent.click(await screen.findByRole('checkbox', { name: /mature themes/ }));
    await userEvent.click(screen.getByRole('checkbox', { name: /excluded/ }));
    expect(store.get().settings).toMatchObject({ showMature: true, showExcluded: true });
  });

  it('clears reading data only after confirming', async () => {
    const store = createStore(localStorage);
    store.toggleFavorite('aesop--the-heron');
    store.setProgress('aesop--the-lion', 2);
    store.markRead('aesop--the-lion');
    store.updateSettings({ theme: 'light' });
    renderApp('/settings', store);

    await userEvent.click(await screen.findByRole('button', { name: 'Clear reading data' }));
    await userEvent.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(store.get().favorites).toHaveProperty('aesop--the-heron');

    await userEvent.click(screen.getByRole('button', { name: 'Clear reading data' }));
    await userEvent.click(screen.getByRole('button', { name: 'Yes, clear' }));
    expect(store.get()).toMatchObject({ favorites: {}, progress: {}, history: [] });
    expect(store.get().settings.theme).toBe('light');
    expect(screen.getByRole('status')).toHaveTextContent('Reading data cleared.');
  });
});
