export type AutoHide = { visible: boolean; anchor: number };

const TOP = 64;
const THRESHOLD = 8;

/** Hide-on-scroll-down, show-on-scroll-up. `anchor` is the turning point of the current run. */
export function autoHide({ visible, anchor }: AutoHide, y: number): AutoHide {
  if (y <= TOP) return { visible: true, anchor: y };
  if (visible)
    return y - anchor > THRESHOLD
      ? { visible: false, anchor: y }
      : { visible, anchor: Math.min(anchor, y) };
  return anchor - y > THRESHOLD
    ? { visible: true, anchor: y }
    : { visible, anchor: Math.max(anchor, y) };
}
