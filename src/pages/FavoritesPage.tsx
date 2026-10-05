import { Link } from 'react-router';
import { StoryList } from '../components/StoryRow';
import { useAppState } from '../storage/StoreProvider';
import { useVisibleStories } from '../app/useVisibleStories';

export function FavoritesPage() {
  const { favorites } = useAppState();
  const list = useVisibleStories()
    .filter((s) => s.id in favorites)
    .sort((a, b) => favorites[b.id]! - favorites[a.id]!);
  return (
    <div className="page">
      <h1 className="page-title">Favorites</h1>
      {list.length === 0 ? (
        <p className="muted">
          No favorites yet. Tap the heart on any story to keep it here.{' '}
          <Link to="/">Browse the library</Link>
        </p>
      ) : (
        <StoryList entries={list} showCollection label="Favorites" />
      )}
    </div>
  );
}
