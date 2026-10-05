import { Link } from 'react-router';
import type { IndexEntry } from '../data/types';
import { useIndex } from '../data/IndexProvider';
import { useAppState, useStore } from '../storage/StoreProvider';
import { FavoriteButton } from './FavoriteButton';
import { CheckIcon } from './icons';
import { useSwipeReveal } from './useSwipeReveal';

const ACTION_WIDTH = 112;

export function StoryRow({
  entry,
  showCollection,
}: {
  entry: IndexEntry;
  showCollection?: boolean;
}) {
  const { collectionLabel } = useIndex();
  const store = useStore();
  const read = useAppState().history.some((h) => h.id === entry.id);
  const { offset, open, dragging, setOpen, handlers } = useSwipeReveal(entry.id, ACTION_WIDTH);

  return (
    <li className="story-row" data-open={open} data-dragging={dragging}>
      <button
        type="button"
        className="row-action"
        style={{ width: ACTION_WIDTH }}
        aria-label={`Mark ${entry.title} ${read ? 'unread' : 'read'}`}
        onFocus={() => !open && setOpen(true)}
        onBlur={() => setOpen(false)}
        onClick={() => {
          if (read) store.markUnread(entry.id);
          else store.markRead(entry.id);
          setOpen(false);
        }}
      >
        {read ? 'Mark unread' : 'Mark read'}
      </button>
      <div
        className="row-content"
        style={{ transform: offset ? `translateX(${offset}px)` : undefined }}
        {...handlers}
      >
        <Link to={`/s/${entry.id}`} className="story-link" draggable={false}>
          <span className="story-title">{entry.title}</span>
          <span className="story-meta">
            {showCollection && <>{collectionLabel(entry.collectionId)} · </>}
            {entry.readingMinutes} min
            {read && (
              <span className="read-mark">
                {' · '}
                <CheckIcon /> read
              </span>
            )}
          </span>
        </Link>
        <FavoriteButton id={entry.id} title={entry.title} />
      </div>
    </li>
  );
}

export function StoryList({
  entries,
  showCollection,
  label,
}: {
  entries: IndexEntry[];
  showCollection?: boolean;
  label?: string;
}) {
  return (
    <ul className="story-list" aria-label={label}>
      {entries.map((e) => (
        <StoryRow key={e.id} entry={e} showCollection={showCollection} />
      ))}
    </ul>
  );
}
