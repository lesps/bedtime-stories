import type { State } from '../storage/store';

type Progress = State['progress'][string];

/** How far through a story the reader is, or null if the block count wasn't recorded. */
export function progressInfo(p: Progress, readingMinutes: number) {
  if (!p.blockCount) return null;
  const fraction = Math.min(1, p.blockIndex / p.blockCount);
  return { fraction, minutesLeft: Math.max(1, Math.round(readingMinutes * (1 - fraction))) };
}
