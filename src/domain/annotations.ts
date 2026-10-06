export type Anchor = { start: number; end: number; quote: string };

/**
 * Where an anchor sits in `text` now. Offsets are trusted when they still spell the quote;
 * otherwise the quote is searched for (nearest occurrence to the old start). Null = detached.
 */
export function resolveAnchor(text: string, a: Anchor): { start: number; end: number } | null {
  if (text.slice(a.start, a.end) === a.quote) return { start: a.start, end: a.end };
  let best = -1;
  for (let i = text.indexOf(a.quote); i !== -1; i = text.indexOf(a.quote, i + 1)) {
    if (best === -1 || Math.abs(i - a.start) < Math.abs(best - a.start)) best = i;
  }
  return best === -1 ? null : { start: best, end: best + a.quote.length };
}

export type Segment = { text: string; id?: string };

/** Splits text into plain and marked runs. Overlaps: the mark that starts first wins. */
export function segments(
  text: string,
  marks: { id: string; start: number; end: number }[],
): Segment[] {
  const sorted = [...marks]
    .map((m) => ({ ...m, start: Math.max(0, m.start), end: Math.min(text.length, m.end) }))
    .filter((m) => m.end > m.start)
    .sort((a, b) => a.start - b.start);
  const out: Segment[] = [];
  let pos = 0;
  for (const m of sorted) {
    const start = Math.max(m.start, pos);
    if (start >= m.end) continue;
    if (start > pos) out.push({ text: text.slice(pos, start) });
    out.push({ text: text.slice(start, m.end), id: m.id });
    pos = m.end;
  }
  if (pos < text.length || out.length === 0) out.push({ text: text.slice(pos) });
  return out;
}
