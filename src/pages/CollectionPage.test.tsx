import { screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { renderApp } from '../test/renderApp';

describe('CollectionPage', () => {
  it('lists visible stories in book order with minutes', async () => {
    renderApp('/c/aesop');
    const list = await screen.findByRole('list', { name: /Stories in/ });
    const rows = within(list).getAllByRole('listitem');
    expect(rows.map((r) => r.querySelector('.story-title')?.textContent)).toEqual([
      'The Fox and the Grapes',
      'The Heron',
      'The Lion',
    ]);
    expect(rows[0]).toHaveTextContent('2 min');
  });

  it('links back to the library', async () => {
    renderApp('/c/aesop');
    expect(await screen.findByRole('link', { name: '‹ Library' })).toHaveAttribute('href', '/');
  });

  it('shows not found for an unknown collection', async () => {
    renderApp('/c/nope');
    expect(await screen.findByRole('heading', { name: 'Not found' })).toBeInTheDocument();
  });
});
