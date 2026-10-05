/** Slider stops in minutes. Half the stories are ≤6 min, so the scale is dense at the short end. */
export const LENGTH_STOPS = [1, 2, 3, 5, 7, 10, 15, 20, 30, 45, 60] as const;

const FIRST = LENGTH_STOPS[0];
const LAST = LENGTH_STOPS[LENGTH_STOPS.length - 1]!;

/** Inclusive minutes range; `max: null` means no upper bound (the last stop reads "60+"). */
export type LengthRange = { min: number; max: number | null };

export const FULL_RANGE: LengthRange = { min: FIRST, max: null };

const upper = (r: LengthRange) => (r.max == null || r.max >= LAST ? null : r.max);

export function inRange(minutes: number, r: LengthRange): boolean {
  const max = upper(r);
  return minutes >= r.min && (max == null || minutes <= max);
}

export const isFullRange = (r: LengthRange) => r.min <= FIRST && upper(r) == null;

export const stopLabel = (m: number) => (m >= LAST ? `${LAST}+ min` : `${m} min`);

export function formatRange(r: LengthRange): string {
  const max = upper(r);
  if (isFullRange(r)) return 'Any length';
  if (max == null) return `${r.min} min or longer`;
  if (r.min <= FIRST) return `Up to ${max} min`;
  if (r.min === max) return `About ${max} min`;
  return `${r.min}–${max} min`;
}
