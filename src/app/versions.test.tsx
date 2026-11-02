import { act, fireEvent, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { createStore } from '../storage/store';
import { renderApp } from '../test/renderApp';
import { versionsData } from '../test/versionsFixture';

const titles = (list: HTMLElement) =>
  within(list)
    .getAllByRole('listitem')
    .map((li) => li.querySelector('.story-title')?.textContent);

const render = (path: string, store = createStore(localStorage)) =>
  renderApp(path, store, {}, versionsData);

describe('one version of each myth in listings', () => {
  it('lists retellings in the library and leaves out books that are retold entirely', async () => {
    render('/');
    expect(
      await screen.findByRole('link', { name: /Irish Legends, Simply Told/ }),
    ).toHaveTextContent('4 stories');
    expect(screen.getByRole('link', { name: /Old Celtic Romances/ })).toHaveTextContent(/1 story$/);
    expect(screen.queryByRole('link', { name: /Hound of Ulster/ })).not.toBeInTheDocument();
  });

  it('lists the originals instead when Settings says so', async () => {
    const store = createStore(localStorage);
    render('/', store);
    await screen.findByRole('link', { name: /Irish Legends, Simply Told/ });
    act(() => store.updateSettings({ showOriginals: true }));
    expect(screen.getByRole('link', { name: /Old Celtic Romances/ })).toHaveTextContent(
      '2 stories',
    );
    expect(screen.getByRole('link', { name: /Hound of Ulster/ })).toHaveTextContent(/1 story$/);
    // Usna's original is hidden by the mature-themes setting, so its retelling stays.
    expect(screen.getByRole('link', { name: /Irish Legends, Simply Told/ })).toHaveTextContent(
      '2 stories',
    );
  });

  it('searches the listed version only', async () => {
    render('/');
    await userEvent.type(await screen.findByRole('searchbox'), 'children');
    expect(titles(screen.getByRole('list', { name: 'Results' }))).toEqual(['The Children of Lir']);
  });

  it('counts and lists one version per myth on culture cards and tag pages', async () => {
    const { unmount } = render('/?by=cultures');
    expect(await screen.findByRole('link', { name: /Irish/ })).toHaveTextContent('5 stories');
    unmount();
    render('/tags/cultures/irish');
    const list = await screen.findByRole('list', { name: 'Irish' });
    expect(titles(list)).toEqual([
      'Deirdre and the Sons of Usna',
      'Oisin in Tir na nOg',
      'The Children of Lir',
      'The Hound of Culann',
      'Tuan the Shape-Changer',
    ]);
  });

  it('shows a book’s retold originals in a section of their own', async () => {
    render('/c/joyce');
    expect(titles(await screen.findByRole('list', { name: /Stories in/ }))).toEqual([
      'Oisin in Tir na nOg',
    ]);
    const originals = screen.getByRole('list', { name: 'Original texts' });
    expect(titles(originals)).toEqual(['The Fate of the Children of Lir']);
    expect(screen.getByText(/listed in the library as their retellings/i)).toBeInTheDocument();
  });

  it('offers Surprise me only collections with listed stories', async () => {
    render('/surprise');
    const group = await screen.findByRole('group', { name: 'Collections' });
    expect(within(group).queryByRole('button', { name: /Hound of Ulster/ })).toBeNull();
    expect(within(group).getByRole('button', { name: /Irish Legends/ })).toBeInTheDocument();
  });

  it('has a Settings switch for listing originals', async () => {
    const { store } = render('/settings');
    const box = await screen.findByRole('checkbox', {
      name: 'List original texts instead of retellings',
    });
    expect(box).not.toBeChecked();
    fireEvent.click(box);
    expect(store.get().settings.showOriginals).toBe(true);
  });
});

describe('moving between an original and its retelling', () => {
  it('links a retelling to its original, and back', async () => {
    const { unmount } = render('/s/myths-irish--lir');
    const link = await screen.findByRole('link', { name: 'Read the original' });
    expect(link).toHaveAttribute('href', '/s/joyce--lir');
    unmount();
    render('/s/joyce--lir');
    expect(
      await screen.findByRole('link', { name: 'Read the retelling for young readers' }),
    ).toHaveAttribute('href', '/s/myths-irish--lir');
  });

  it('offers no link to an original that content settings hide, or that does not exist', async () => {
    const { unmount } = render('/s/myths-irish--usna');
    await screen.findByText(/begins here/);
    expect(screen.queryByRole('link', { name: 'Read the original' })).toBeNull();
    unmount();
    render('/s/myths-irish--tuan');
    await screen.findByText(/begins here/);
    expect(screen.queryByRole('link', { name: 'Read the original' })).toBeNull();
  });

  it('opens an original that listings leave out, with Next among the book’s originals', async () => {
    const { unmount } = render('/s/myths-irish--lir');
    const nav = await screen.findByRole('navigation', { name: 'More stories' });
    expect(within(nav).getByRole('link', { name: /Next/ })).toHaveTextContent(
      'Deirdre and the Sons of Usna',
    );
    unmount();
    render('/s/joyce--lir');
    expect(
      await screen.findByRole('heading', { level: 1, name: 'The Fate of the Children of Lir' }),
    ).toBeInTheDocument();
    // Usna's original is mature, so Lir is the only original of Joyce's to step through.
    const book = await screen.findByRole('navigation', { name: 'More stories' });
    expect(within(book).queryByRole('link')).toBeNull();
  });
});
