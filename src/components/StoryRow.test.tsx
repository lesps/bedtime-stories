import { act, fireEvent, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { createStore } from '../storage/store';
import { renderApp } from '../test/renderApp';

const rowFor = (title: string) => screen.getByText(title).closest('li')!;
const content = (row: HTMLElement) => row.querySelector<HTMLElement>('.row-content')!;

function swipe(row: HTMLElement, dx: number, dy = 0, pointerType = 'touch') {
  const el = content(row);
  const at = (x: number, y: number) => ({ clientX: x, clientY: y, pointerId: 1, pointerType });
  fireEvent.pointerDown(el, { ...at(300, 100), button: 0 });
  fireEvent.pointerMove(el, at(300 + dx / 2, 100 + dy / 2));
  fireEvent.pointerMove(el, at(300 + dx, 100 + dy));
  fireEvent.pointerUp(el, at(300 + dx, 100 + dy));
}

describe('StoryRow swipe actions', () => {
  it('swiping left on a read story reveals "Mark unread", which clears it from history', async () => {
    const store = createStore(localStorage);
    store.markRead('aesop--the-heron');
    renderApp('/c/aesop', store);
    await screen.findByText('The Heron');
    const row = rowFor('The Heron');
    expect(row).toHaveTextContent('read');

    swipe(row, -120);
    expect(row).toHaveAttribute('data-open', 'true');
    await userEvent.click(within(row).getByRole('button', { name: 'Mark The Heron unread' }));

    expect(store.get().history).toEqual([]);
    expect(row).not.toHaveTextContent(/·\s*read/);
    expect(row).toHaveAttribute('data-open', 'false');
  });

  it('ignores mouse drags: with a mouse the action shows on hover instead', async () => {
    renderApp('/c/aesop');
    await screen.findByText('The Lion');
    const row = rowFor('The Lion');
    swipe(row, -120, 0, 'mouse');
    expect(row).toHaveAttribute('data-open', 'false');
  });

  it('offers "Mark read" on an unread story', async () => {
    const { store } = renderApp('/c/aesop');
    await screen.findByText('The Lion');
    const row = rowFor('The Lion');
    swipe(row, -120);
    await userEvent.click(within(row).getByRole('button', { name: 'Mark The Lion read' }));
    expect(store.get().history.map((h) => h.id)).toEqual(['aesop--the-lion']);
  });

  it('snaps back on a short swipe or a vertical scroll', async () => {
    renderApp('/c/aesop');
    await screen.findByText('The Lion');
    const row = rowFor('The Lion');
    swipe(row, -20);
    expect(row).toHaveAttribute('data-open', 'false');
    swipe(row, -60, 200);
    expect(row).toHaveAttribute('data-open', 'false');
  });

  it('does not open the story when the gesture was a swipe', async () => {
    renderApp('/c/aesop');
    await screen.findByText('The Lion');
    const row = rowFor('The Lion');
    swipe(row, -120);
    fireEvent.click(within(row).getByRole('link'));
    expect(screen.queryByRole('article')).not.toBeInTheDocument();
  });

  it('a tap on an open row closes it instead of navigating', async () => {
    renderApp('/c/aesop');
    await screen.findByText('The Lion');
    const row = rowFor('The Lion');
    swipe(row, -120);
    fireEvent.click(within(row).getByRole('link')); // the click that ends the swipe
    fireEvent.click(within(row).getByRole('link'));
    expect(row).toHaveAttribute('data-open', 'false');
    expect(screen.queryByRole('article')).not.toBeInTheDocument();
    fireEvent.click(within(row).getByRole('link'));
    expect(await screen.findByRole('article')).toBeInTheDocument();
  });

  it('closes other open rows when one opens', async () => {
    renderApp('/c/aesop');
    await screen.findByText('The Lion');
    swipe(rowFor('The Lion'), -120);
    swipe(rowFor('The Heron'), -120);
    expect(rowFor('The Lion')).toHaveAttribute('data-open', 'false');
    expect(rowFor('The Heron')).toHaveAttribute('data-open', 'true');
  });

  it('is reachable without swiping: focusing the action reveals it', async () => {
    renderApp('/c/aesop');
    await screen.findByText('The Lion');
    const row = rowFor('The Lion');
    const action = within(row).getByRole('button', { name: 'Mark The Lion read' });
    act(() => action.focus());
    expect(row).toHaveAttribute('data-open', 'true');
    act(() => action.blur());
    expect(row).toHaveAttribute('data-open', 'false');
  });
});
