import { act, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createStore } from '../storage/store';
import { installFakeIO } from '../test/fakeIntersectionObserver';
import { renderApp } from '../test/renderApp';

beforeEach(() => {
  installFakeIO();
  Element.prototype.scrollIntoView = vi.fn();
});

/** Selects `text` inside the block with the given index, optionally extending into another block. */
function select(block: number, text: string, toBlock?: { block: number; text: string }) {
  const node = (i: number) => document.querySelector(`[data-block="${i}"]`)!;
  const textNode = (el: Element) => {
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    return w.nextNode() as Text;
  };
  const a = textNode(node(block));
  const range = document.createRange();
  const start = a.data.indexOf(text);
  range.setStart(a, start);
  if (toBlock) {
    const b = textNode(node(toBlock.block));
    range.setEnd(b, b.data.indexOf(toBlock.text) + toBlock.text.length);
  } else {
    range.setEnd(a, start + text.length);
  }
  const sel = window.getSelection()!;
  sel.removeAllRanges();
  sel.addRange(range);
  act(() => void document.dispatchEvent(new Event('selectionchange')));
}

async function openHeron(store = createStore(localStorage)) {
  const r = renderApp('/s/aesop--the-heron', store);
  await screen.findByText('The Heron begins here.');
  return r;
}

describe('highlights and notes', () => {
  it('highlights a selection in one colour tap', async () => {
    const { store } = await openHeron();
    select(1, 'Middle');
    const bar = await screen.findByRole('toolbar', { name: 'Highlight' });
    await userEvent.click(within(bar).getByRole('button', { name: 'Highlight yellow' }));
    expect(store.get().annotations['aesop--the-heron']).toMatchObject([
      { block: 1, start: 0, end: 6, quote: 'Middle', color: 'yellow' },
    ]);
    const mark = screen.getByRole('button', { name: /Highlight: Middle/ });
    expect(mark).toHaveAttribute('data-color', 'yellow');
    expect(screen.queryByRole('toolbar', { name: 'Highlight' })).not.toBeInTheDocument();
  });

  it('clamps a selection that crosses paragraphs to the first paragraph', async () => {
    const { store } = await openHeron();
    select(1, 'part', { block: 2, text: 'More' });
    await userEvent.click(await screen.findByRole('button', { name: 'Highlight blue' }));
    expect(store.get().annotations['aesop--the-heron']).toMatchObject([
      { block: 1, quote: 'part.', color: 'blue' },
    ]);
  });

  it('adds a note to a new highlight', async () => {
    const { store } = await openHeron();
    select(2, 'More middle');
    await userEvent.click(await screen.findByRole('button', { name: 'Add note' }));
    const sheet = screen.getByRole('dialog', { name: /Highlight/ });
    await userEvent.type(within(sheet).getByRole('textbox', { name: 'Note' }), 'Ada asked why');
    await userEvent.click(within(sheet).getByRole('button', { name: 'Done' }));
    expect(store.get().annotations['aesop--the-heron']?.[0]).toMatchObject({
      quote: 'More middle',
      note: 'Ada asked why',
    });
    expect(
      screen.getByRole('button', { name: /Highlight: More middle.*has a note/ }),
    ).toBeInTheDocument();
  });

  it('opens an existing highlight to recolour or delete it', async () => {
    const store = createStore(localStorage);
    store.addHighlight('aesop--the-heron', {
      block: 1,
      start: 0,
      end: 6,
      quote: 'Middle',
      color: 'yellow',
    });
    await openHeron(store);
    await userEvent.click(screen.getByRole('button', { name: /Highlight: Middle/ }));
    const sheet = screen.getByRole('dialog', { name: /Highlight/ });
    await userEvent.click(within(sheet).getByRole('radio', { name: 'Green' }));
    expect(store.get().annotations['aesop--the-heron']?.[0]?.color).toBe('green');
    await userEvent.click(within(sheet).getByRole('button', { name: 'Delete highlight' }));
    expect(store.get().annotations).toEqual({});
    expect(screen.queryByRole('button', { name: /Highlight: Middle/ })).not.toBeInTheDocument();
  });

  it('moves focus into the highlight sheet, closes it on Escape and returns focus', async () => {
    const store = createStore(localStorage);
    store.addHighlight('aesop--the-heron', {
      block: 1,
      start: 0,
      end: 6,
      quote: 'Middle',
      color: 'yellow',
    });
    await openHeron(store);
    const mark = screen.getByRole('button', { name: /Highlight: Middle/ });
    await userEvent.click(mark);
    const sheet = screen.getByRole('dialog', { name: /Highlight/ });
    expect(sheet).toContainElement(document.activeElement as HTMLElement);
    await userEvent.keyboard('{Escape}');
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(mark).toHaveFocus();
  });

  it('closes the Notes panel on Escape from anywhere', async () => {
    await openHeron();
    const button = screen.getByRole('button', { name: 'Notes' });
    await userEvent.click(button);
    expect(screen.getByRole('dialog', { name: 'Notes' })).toContainElement(
      document.activeElement as HTMLElement,
    );
    act(() => (document.activeElement as HTMLElement).blur());
    await userEvent.keyboard('{Escape}');
    expect(screen.queryByRole('dialog', { name: 'Notes' })).not.toBeInTheDocument();
  });

  it('keeps a story note and lists highlights in the Notes panel, jumping to one', async () => {
    const store = createStore(localStorage);
    store.addHighlight('aesop--the-heron', {
      block: 2,
      start: 0,
      end: 4,
      quote: 'More',
      color: 'pink',
      note: 'Read slowly',
    });
    await openHeron(store);
    await userEvent.click(screen.getByRole('button', { name: 'Notes' }));
    const panel = screen.getByRole('dialog', { name: 'Notes' });
    const story = within(panel).getByRole('textbox', { name: 'Note on this story' });
    await userEvent.type(story, 'Both kids loved it');
    await userEvent.tab();
    expect(store.get().storyNotes['aesop--the-heron']?.text).toBe('Both kids loved it');

    const item = within(panel).getByRole('button', { name: /More/ });
    expect(item).toHaveTextContent('Read slowly');
    await userEvent.click(item);
    expect(Element.prototype.scrollIntoView).toHaveBeenCalled();
    expect(screen.queryByRole('dialog', { name: 'Notes' })).not.toBeInTheDocument();
  });

  it('sets aside highlights whose text can no longer be found', async () => {
    const store = createStore(localStorage);
    store.addHighlight('aesop--the-heron', {
      block: 1,
      start: 0,
      end: 9,
      quote: 'Vanished!',
      color: 'yellow',
    });
    renderApp('/s/aesop--the-heron?notes=1', store);
    const panel = await screen.findByRole('dialog', { name: 'Notes' });
    expect(within(panel).getByText(/Couldn’t find these in the text/)).toBeInTheDocument();
    expect(panel).toHaveTextContent('Vanished!');
  });
});
