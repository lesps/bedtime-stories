import { useState } from 'react';
import type { IndexEntry } from '../data/types';
import { FULL_RANGE, inRange, isFullRange, type LengthRange } from '../domain/length';
import { LengthSlider } from './LengthSlider';
import { StoryList } from './StoryRow';

const stories = (n: number) => (n === 1 ? 'story' : 'stories');

/** A story list with its own length slider and a count ("2 of 3 stories" while filtering). */
export function LengthFilteredList({
  entries,
  label,
  showCollection,
}: {
  entries: IndexEntry[];
  label: string;
  showCollection?: boolean;
}) {
  const [length, setLength] = useState<LengthRange>(FULL_RANGE);
  const shown = entries.filter((s) => inRange(s.readingMinutes, length));
  const total = entries.length;
  return (
    <>
      <LengthSlider value={length} onChange={setLength} />
      <p className="muted list-count">
        {isFullRange(length)
          ? `${total} ${stories(total)}`
          : `${shown.length} of ${total} ${stories(total)}`}
      </p>
      {shown.length === 0 && total > 0 && <p className="muted">No stories of that length here.</p>}
      <StoryList entries={shown} showCollection={showCollection} label={label} />
    </>
  );
}
