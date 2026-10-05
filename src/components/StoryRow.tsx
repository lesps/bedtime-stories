import { Link } from 'react-router';
import type { IndexEntry } from '../data/types';
import { useIndex } from '../data/IndexProvider';
import { useAppState } from '../storage/StoreProvider';
import { FavoriteButton } from './FavoriteButton';
import { CheckIcon } from './icons';

export function StoryRow({
  entry,
  showCollection,
}: {
  entry: IndexEntry;
  showCollection?: boolean;
}) {
  const { collectionsById } = useIndex();
  const read = useAppState().history.some((h) => h.id === entry.id);
  return (
    <li className="story-row">
      <Link to={`/s/${entry.id}`} className="story-link">
        <span className="story-title">{entry.title}</span>
        <span className="story-meta">
          {showCollection && <>{collectionsById.get(entry.collectionId)?.title} · </>}
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
