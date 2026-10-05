import { useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router';
import { LengthSlider } from '../components/LengthSlider';
import { usePrefersReducedMotion } from '../app/theme';
import { loadStory } from '../data/client';
import { useIndex } from '../data/IndexProvider';
import type { IndexEntry } from '../data/types';
import { excerpt } from '../domain/excerpt';
import { pick, type PickResult } from '../domain/picker';
import { useAppState, useStore } from '../storage/StoreProvider';
import { useVisibleStories } from '../app/useVisibleStories';

const SHUFFLE_MS = 700;

export function SurprisePage() {
  const { stories, collections, collectionsById } = useIndex();
  const store = useStore();
  const state = useAppState();
  const { picker, showMature, showExcluded } = state.settings;
  const reducedMotion = usePrefersReducedMotion();
  const [result, setResult] = useState<PickResult | null>(null);
  const [shuffling, setShuffling] = useState<string | null>(null);
  const visible = useVisibleStories();
  const timers = useRef<number[]>([]);

  useEffect(() => () => timers.current.forEach((t) => window.clearTimeout(t)), []);

  const setPicker = (patch: Partial<typeof picker>) =>
    store.updateSettings({ picker: { ...picker, ...patch } });

  const ctx = useMemo(
    () => ({
      visibility: { showMature, showExcluded },
      readIds: new Set(state.history.map((h) => h.id)),
      favoriteIds: new Set(Object.keys(state.favorites)),
    }),
    [showMature, showExcluded, state.history, state.favorites],
  );

  const doPick = () => {
    const r = pick(
      stories,
      {
        collections: picker.collections,
        minMinutes: picker.minMinutes,
        maxMinutes: picker.maxMinutes ?? undefined,
        unreadOnly: picker.unreadOnly,
        favoritesOnly: picker.favoritesOnly,
        recent: store.get().recentPicks,
      },
      Math.random,
      ctx,
    );
    if (r.story) store.recordPick(r.story.id);
    if (reducedMotion || !r.story) {
      setResult(r);
      return;
    }
    // Brief shuffle through visible titles before revealing the pick.
    const titles = visible.map((s) => s.title);
    setResult(null);
    setShuffling(r.story.title);
    const iv = window.setInterval(
      () => setShuffling(titles[Math.floor(Math.random() * titles.length)]!),
      70,
    );
    const to = window.setTimeout(() => {
      window.clearInterval(iv);
      setShuffling(null);
      setResult(r);
    }, SHUFFLE_MS);
    timers.current.push(iv, to);
  };

  const toggleCollection = (id: string) => {
    const set = new Set(picker.collections);
    if (set.has(id)) set.delete(id);
    else set.add(id);
    setPicker({ collections: [...set] });
  };

  return (
    <div className="page">
      <h1 className="page-title">Surprise me</h1>

      <div className="chips" role="group" aria-label="Collections">
        <button
          type="button"
          className="chip"
          aria-pressed={picker.collections.length === 0}
          onClick={() => setPicker({ collections: [] })}
        >
          All collections
        </button>
        {collections.map((c) => (
          <button
            key={c.id}
            type="button"
            className="chip"
            aria-pressed={picker.collections.includes(c.id)}
            onClick={() => toggleCollection(c.id)}
          >
            {c.title}
          </button>
        ))}
      </div>

      <LengthSlider
        value={{ min: picker.minMinutes, max: picker.maxMinutes }}
        onChange={(r) => setPicker({ minMinutes: r.min, maxMinutes: r.max })}
      />

      <div className="toggles">
        <label className="toggle">
          <input
            type="checkbox"
            checked={picker.unreadOnly}
            onChange={(e) => setPicker({ unreadOnly: e.target.checked })}
          />
          Unread only
        </label>
        <label className="toggle">
          <input
            type="checkbox"
            checked={picker.favoritesOnly}
            onChange={(e) => setPicker({ favoritesOnly: e.target.checked })}
          />
          Favorites only
        </label>
      </div>

      {!result && !shuffling && (
        <button type="button" className="btn primary big" onClick={doPick}>
          Pick a story
        </button>
      )}

      <div aria-live="polite">
        {shuffling && (
          <div className="pick-card shuffling" aria-hidden="true">
            <p className="pick-title">{shuffling}</p>
          </div>
        )}
        {result?.story === null && (
          <div className="pick-card" role="alert">
            <p>
              <strong>No stories match these choices.</strong>
            </p>
            <p className="muted">
              Try a longer length, more collections, or turning off “Unread only” / “Favorites
              only”.
            </p>
          </div>
        )}
        {result?.story && (
          <PickCard
            key={result.story.id}
            entry={result.story}
            collectionTitle={collectionsById.get(result.story.collectionId)?.title ?? ''}
            onAgain={doPick}
          />
        )}
      </div>
    </div>
  );
}

function PickCard({
  entry,
  collectionTitle,
  onAgain,
}: {
  entry: IndexEntry;
  collectionTitle: string;
  onAgain: () => void;
}) {
  const [text, setText] = useState<string | null>(null);
  useEffect(() => {
    let live = true;
    loadStory(entry.id).then(
      (s) => live && setText(excerpt(s.blocks)),
      () => live && setText(''),
    );
    return () => {
      live = false;
    };
  }, [entry.id]);
  return (
    <section className="pick-card" aria-label="Your story">
      <h2 className="pick-title">{entry.title}</h2>
      <p className="muted">
        {collectionTitle} · {entry.readingMinutes} min
      </p>
      {text && <p className="excerpt">{text}</p>}
      <div className="row">
        <Link to={`/s/${entry.id}`} className="btn primary">
          Read it
        </Link>
        <button type="button" className="btn" onClick={onAgain}>
          Pick again
        </button>
      </div>
    </section>
  );
}
