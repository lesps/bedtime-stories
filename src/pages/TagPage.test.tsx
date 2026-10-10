import { fireEvent, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { renderApp } from '../test/renderApp';

describe('TagPage', () => {
  it('lists visible stories with the tag, alphabetically, with their collection', async () => {
    renderApp('/tags/themes/royalty');
    expect(
      await screen.findByRole('heading', { level: 1, name: 'Kings, queens & castles' }),
    ).toBeInTheDocument();
    const list = screen.getByRole('list', { name: 'Kings, queens & castles' });
    expect(
      within(list)
        .getAllByRole('listitem')
        .map((li) => li.querySelector('.story-title')?.textContent),
    ).toEqual(['Rapunzel', 'Rapunzel (Hunt)', 'The Long One']);
    expect(list).toHaveTextContent("Grimms' Fairy Tales");
  });

  it('filters by length', async () => {
    renderApp('/tags/themes/royalty');
    const list = await screen.findByRole('list', { name: 'Kings, queens & castles' });
    // 15 min and up (stop index 6)
    fireEvent.change(screen.getByRole('slider', { name: 'Shortest' }), { target: { value: '6' } });
    expect(within(list).getAllByRole('listitem')).toHaveLength(1);
    expect(list).toHaveTextContent('The Long One');
    expect(screen.getByText('1 of 3 stories')).toBeInTheDocument();
  });

  it('links back to the library, browsing that kind of tag', async () => {
    renderApp('/tags/themes/royalty');
    expect(await screen.findByRole('link', { name: '‹ Themes' })).toHaveAttribute(
      'href',
      '/?by=themes',
    );
  });

  it('says the kind of tag it is', async () => {
    renderApp('/tags/cultures/greek');
    expect(await screen.findByText(/Culture/)).toBeInTheDocument();
  });

  it('shows not found for an unknown tag or kind', async () => {
    renderApp('/tags/themes/nope');
    expect(await screen.findByRole('heading', { name: 'Not found' })).toBeInTheDocument();
  });
});
