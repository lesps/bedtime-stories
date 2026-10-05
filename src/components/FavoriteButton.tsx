import { useAppState, useStore } from '../storage/StoreProvider';
import { HeartIcon } from './icons';

export function FavoriteButton({ id, title }: { id: string; title: string }) {
  const store = useStore();
  const on = id in useAppState().favorites;
  return (
    <button
      type="button"
      className="icon-btn fav"
      aria-pressed={on}
      aria-label={`Favorite ${title}`}
      onClick={() => store.toggleFavorite(id)}
    >
      <HeartIcon filled={on} />
    </button>
  );
}
