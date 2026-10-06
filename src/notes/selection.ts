export type SelectionInfo = {
  block: number;
  start: number;
  end: number;
  quote: string;
  rect: DOMRect | null;
};

const blockOf = (n: Node) =>
  (n.nodeType === Node.ELEMENT_NODE ? (n as Element) : n.parentElement)?.closest('[data-block]');

/** Characters of `block`'s text before (container, offset). Works across nested <mark>s. */
function offsetIn(block: Element, container: Node, offset: number) {
  const r = document.createRange();
  r.selectNodeContents(block);
  r.setEnd(container, offset);
  return r.toString().length;
}

/**
 * The current selection as a highlightable span of one text block inside `root`. A selection
 * running into later blocks is clamped to the block it starts in; surrounding spaces are trimmed.
 */
export function readSelection(root: HTMLElement): SelectionInfo | null {
  const sel = window.getSelection();
  if (!sel || sel.isCollapsed || sel.rangeCount === 0) return null;
  const range = sel.getRangeAt(0);
  const block = blockOf(range.startContainer);
  if (!block || !root.contains(block) || block.tagName === 'FIGURE') return null;
  const text = block.textContent ?? '';
  let start = offsetIn(block, range.startContainer, range.startOffset);
  let end = block.contains(range.endContainer)
    ? offsetIn(block, range.endContainer, range.endOffset)
    : text.length;
  while (start < end && /\s/.test(text[start]!)) start++;
  while (end > start && /\s/.test(text[end - 1]!)) end--;
  if (end <= start) return null;
  const rect =
    typeof range.getBoundingClientRect === 'function' ? range.getBoundingClientRect() : null;
  return {
    block: Number(block.getAttribute('data-block')),
    start,
    end,
    quote: text.slice(start, end),
    rect,
  };
}
