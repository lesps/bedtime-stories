import type { Block } from '../data/types';

export function excerpt(blocks: Block[], words = 25): string {
  const all = blocks
    .flatMap((b) => (b.type === 'p' || b.type === 'verse' ? b.text.split(/\s+/) : []))
    .filter(Boolean);
  return all.length > words ? `${all.slice(0, words).join(' ')}…` : all.join(' ');
}
