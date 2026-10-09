import { act, fireEvent, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { createStore } from '../storage/store';
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

  it('leaves out collections with no visible stories, and counts in the singular', async () => {
    const store = createStore(localStorage);
    renderApp('/', store);
    await screen.findByRole('link', { name: /The Aesop for Children/ });
    expect(screen.queryByRole('link', { name: /Max and Maurice/ })).not.toBeInTheDocument();
    act(() => store.updateSettings({ showExcluded: true }));
    expect(await screen.findByRole('link', { name: /Max and Maurice/ })).toHaveTextContent(
      /1 story$/,
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
    // Medium: 7–15 min (stop indices 4..6)
    fireEvent.change(await screen.findByRole('slider', { name: 'Shortest' }), {
      target: { value: '4' },
    });
    fireEvent.change(screen.getByRole('slider', { name: 'Longest' }), { target: { value: '6' } });
    expect(
      within(screen.getByRole('list', { name: 'Results' })).getAllByRole('listitem'),
    ).toHaveLength(2);
    expect(screen.getByText('Rapunzel')).toBeInTheDocument();
    expect(screen.getByText('Rapunzel (Hunt)')).toBeInTheDocument();
    // Long: 15 min and up
    fireEvent.change(screen.getByRole('slider', { name: 'Longest' }), { target: { value: '10' } });
    fireEvent.change(screen.getByRole('slider', { name: 'Shortest' }), { target: { value: '6' } });
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
    expect(screen.getByText('0 stories')).toBeInTheDocument();
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

  it('leaves finished stories out of Continue reading, and shows read and progress separately', async () => {
    const { store } = renderApp('/c/aesop');
    await screen.findByText('The Heron');
    act(() => {
      store.finishStory('aesop--the-heron', 4);
      store.markRead('aesop--the-lion');
      store.setProgress('aesop--the-lion', 2, 4); // rereading
    });
    const heron = screen.getByText('The Heron').closest('li')!;
    const lion = screen.getByText('The Lion').closest('li')!;
    expect(heron).toHaveTextContent(/·\s*read/);
    expect(heron).not.toHaveTextContent('% through');
    expect(lion).toHaveTextContent(/read/);
    expect(lion).toHaveTextContent('50% through');
  });

  it('browses by culture, with visible-story counts, into a tag page', async () => {
    renderApp('/');
    await userEvent.click(await screen.findByRole('radio', { name: 'Cultures' }));
    // grimm--rapunzel, grimm--the-long-one, hunt--rapunzel; hidden and mature ones don't count
    const german = screen.getByRole('link', { name: /German/ });
    expect(german).toHaveTextContent('3 stories');
    expect(screen.getByRole('link', { name: /Ancient Greek/ })).toHaveTextContent('3 stories');
    await userEvent.click(german);
    expect(await screen.findByRole('heading', { level: 1, name: 'German' })).toBeInTheDocument();
    expect(screen.getByText('The Long One')).toBeInTheDocument();
    expect(screen.queryByText('Hidden Tale')).not.toBeInTheDocument();
  });

  it('browses by theme', async () => {
    renderApp('/');
    await userEvent.click(await screen.findByRole('radio', { name: 'Themes' }));
    expect(screen.getByRole('link', { name: /Fables with a moral/ })).toHaveTextContent(
      '3 stories',
    );
    expect(screen.queryByRole('link', { name: /The Aesop for Children/ })).not.toBeInTheDocument();
  });

  it('finds stories by tag name in search', async () => {
    renderApp('/');
    await userEvent.type(await screen.findByRole('searchbox'), 'german long');
    const results = screen.getByRole('list', { name: 'Results' });
    expect(within(results).getAllByRole('listitem')).toHaveLength(1);
    expect(results).toHaveTextContent('The Long One');
  });
});
