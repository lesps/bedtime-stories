import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { renderApp } from '../test/renderApp';

describe('LibraryPage', () => {
  it('shows collection cards with visible-story counts', async () => {
    renderApp('/');
    const aesop = await screen.findByRole('link', { name: /The Aesop for Children/ });
    expect(aesop).toHaveTextContent('3 stories'); // mature one hidden
    expect(screen.getByRole('link', { name: /Grimms' Fairy Tales/ })).toHaveTextContent(
      '2 stories',
    );
  });

  it('searches titles across all visible stories', async () => {
    renderApp('/');
    await userEvent.type(await screen.findByRole('searchbox', { name: 'Search titles' }), 'the');
    const results = screen.getByRole('list', { name: 'Results' });
    const titles = within(results)
      .getAllByRole('link')
      .map((a) => a.querySelector('.story-title')?.textContent);
    expect(titles).toEqual(['The Fox and the Grapes', 'The Heron', 'The Lion', 'The Long One']);
  });

  it('filters by length', async () => {
    renderApp('/');
    await userEvent.click(await screen.findByRole('button', { name: /Medium/ }));
    expect(
      within(screen.getByRole('list', { name: 'Results' })).getAllByRole('listitem'),
    ).toHaveLength(1);
    expect(screen.getByText('Rapunzel')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /Long/ }));
    expect(screen.getByText('The Long One')).toBeInTheDocument();
    expect(screen.queryByText('Rapunzel')).not.toBeInTheDocument();
  });

  it('never renders hidden stories, even when searched for', async () => {
    renderApp('/');
    const box = await screen.findByRole('searchbox');
    await userEvent.type(box, 'dark');
    expect(screen.queryByText('A Dark Fable')).not.toBeInTheDocument();
    await userEvent.clear(box);
    await userEvent.type(box, 'hidden');
    expect(screen.queryByText('Hidden Tale')).not.toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveTextContent('0 stories');
  });

  it('reveals mature stories when the setting is on', async () => {
    const { store } = renderApp('/');
    store.updateSettings({ showMature: true });
    await userEvent.type(await screen.findByRole('searchbox'), 'dark');
    expect(screen.getByText('A Dark Fable')).toBeInTheDocument();
  });

  it('shows in-progress stories under Continue reading, newest first', async () => {
    const { store } = renderApp('/');
    await screen.findByRole('searchbox');
    store.setProgress('grimm--rapunzel', 2);
    await new Promise((r) => setTimeout(r, 2));
    store.setProgress('aesop--the-heron', 1);
    const list = await screen.findByRole('list', { name: 'Continue reading' });
    const titles = within(list)
      .getAllByRole('link')
      .map((a) => a.querySelector('.story-title')?.textContent);
    expect(titles).toEqual(['The Heron', 'Rapunzel']);
  });
});
