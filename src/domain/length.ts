export type Length = 'short' | 'medium' | 'long';

export const LENGTHS: { id: Length; label: string }[] = [
  { id: 'short', label: 'Short (≤5 min)' },
  { id: 'medium', label: 'Medium (6–15)' },
  { id: 'long', label: 'Long (>15)' },
];

export function lengthOf(minutes: number): Length {
  if (minutes <= 5) return 'short';
  if (minutes <= 15) return 'medium';
  return 'long';
}
