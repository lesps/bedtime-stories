import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router';
import { usePrefersReducedMotion } from '../app/theme';
import { useVisibleStories } from '../app/useVisibleStories';
import { LengthSlider } from '../components/LengthSlider';
import { StoryList } from '../components/StoryRow';
import { TagFilterChips } from '../components/TagFilterChips';
import { loadStory } from '../data/client';
import { useIndex } from '../data/IndexProvider';
import type { IndexEntry } from '../data/types';
import { excerpt } from '../domain/excerpt';
import { pickMany, type PickManyResult } from '../domain/picker';
import { PRESETS, applyPreset } from '../domain/presets';
import { DEFAULT_STATE, type PickerSettings } from '../storage/store';
import { useAppState, useStore } from '../storage/StoreProvider';

export function SurprisePage() {
  const { stories, collections, collectionLabel, tags, tagsOf } = useIndex();
  const store = useStore();
  const state = useAppState();
  const { picker, showMature, showExcluded } = state.settings;
  const reducedMotion = usePrefersReducedMotion();
  const visible = useVisibleStories();
  const [result, setResult] = useState<PickManyResult | null>(null);
  const [round, setRound] = useState(0);

  const setPicker = (patch: Partial<PickerSettings>) =>
    store.updateSettings({ picker: { ...picker, ...patch } });

  const ctx = useMemo(
    () => ({
      visibility: { showMature, showExcluded },
      readIds: new Set(state.history.map((h) => h.id)),
      favoriteIds: new Set(Object.keys(state.favorites)),
      tagsOf,
    }),
    [showMature, showExcluded, state.history, state.favorites, tagsOf],
  );

  const doPick = () => {
    const r = pickMany(
      stories,
      {
        collections: picker.collections,
        minMinutes: picker.minMinutes,
        maxMinutes: picker.maxMinutes ?? undefined,
        unreadOnly: picker.unreadOnly,
        favoritesOnly: picker.favoritesOnly,
        cultures: picker.cultures,
        themes: picker.themes,
        recent: store.get().recentPicks,
      },
      picker.count,
      Math.random,
      ctx,
    );
    for (const s of r.stories) store.recordPick(s.id);
    setResult(r);
    setRound((n) => n + 1);
  };

  const toggleCollection = (id: string) => {
    const set = new Set(picker.collections);
    if (set.has(id)) set.delete(id);
    else set.add(id);
    setPicker({ collections: [...set] });
  };

  const presetCtx = {
    readIds: ctx.readIds,
    tagsOf,
    cultures: tags.cultures.map((c) => c.id),
  };
  const activeFilters =
    picker.collections.length +
    picker.cultures.include.length +
    picker.cultures.exclude.length +
    picker.themes.include.length +
    picker.themes.exclude.length +
    Number(picker.unreadOnly) +
    Number(picker.favoritesOnly);

  const onScreen = new Set(result?.stories.map((s) => s.id));
  const recent = [...state.recentPicks]
    .reverse()
    .filter((id) => !onScreen.has(id))
    .map((id) => visible.find((s) => s.id === id))
    .filter((s): s is IndexEntry => !!s);

  const flip = !reducedMotion;
  const label = picker.count === 3 ? 'Pick 3 stories' : 'Pick a story';

  return (
    <div className="page">
      <h1 className="page-title">Surprise me</h1>

      <div className="presets" role="group" aria-label="Presets">
        {PRESETS.map((p) => (
          <button
            key={p.id}
            type="button"
            className="preset"
            onClick={() => store.updateSettings({ picker: applyPreset(p.id, picker, presetCtx) })}
          >
            <strong>{p.label}</strong>
            <span>{p.hint}</span>
          </button>
        ))}
      </div>

      <LengthSlider
        value={{ min: picker.minMinutes, max: picker.maxMinutes }}
        onChange={(r) => setPicker({ minMinutes: r.min, maxMinutes: r.max })}
      />

      <details className="more-filters">
        <summary>
          More filters
          {activeFilters > 0 && <span className="badge">{activeFilters} on</span>}
        </summary>
        <h2 className="filter-h">Collections</h2>
        <div className="chips" role="group" aria-label="Collections">
          <button
            type="button"
            className="chip"
            aria-pressed={picker.collections.length === 0}
            onClick={() => setPicker({ collections: [] })}
          >
            All collections
          </button>
          {collections
            .filter(
              (c) =>
                picker.collections.includes(c.id) || visible.some((s) => s.collectionId === c.id),
            )
            .map((c) => (
              <button
                key={c.id}
                type="button"
                className="chip"
                aria-pressed={picker.collections.includes(c.id)}
                onClick={() => toggleCollection(c.id)}
              >
                {collectionLabel(c.id)}
              </button>
            ))}
        </div>
        <h2 className="filter-h">Cultures</h2>
        <p className="muted hint">Tap once to include, twice to leave out.</p>
        <TagFilterChips
          label="Cultures"
          defs={tags.cultures}
          value={picker.cultures}
          onChange={(cultures) => setPicker({ cultures })}
        />
        <h2 className="filter-h">Themes</h2>
        <TagFilterChips
          label="Themes"
          defs={tags.themes}
          value={picker.themes}
          onChange={(themes) => setPicker({ themes })}
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
        <button
          type="button"
          className="btn ghost"
          onClick={() =>
            store.updateSettings({
              picker: { ...DEFAULT_STATE.settings.picker, count: picker.count },
            })
          }
        >
          Reset filters
        </button>
      </details>

      <div className="chips" role="radiogroup" aria-label="How many">
        {([1, 3] as const).map((n) => (
          <button
            key={n}
            type="button"
            role="radio"
            className="chip"
            aria-checked={picker.count === n}
            onClick={() => setPicker({ count: n })}
          >
            {n === 1 ? 'Just one' : 'Give me 3'}
          </button>
        ))}
      </div>

      {!result?.stories.length && (
        <button type="button" className="btn primary big" onClick={doPick}>
          {label}
        </button>
      )}

      <div aria-live="polite">
        {result && 'reason' in result && (
          <div className="pick-card" role="alert">
            <p>
              <strong>No stories match these choices.</strong>
            </p>
            <p className="muted">
              Try a wider length, fewer culture or theme filters, or turning off “Unread only” /
              “Favorites only”.
            </p>
          </div>
        )}
        {result && result.stories.length > 0 && (
          <>
            {result.stories.length < picker.count && (
              <p className="muted">
                Only {result.stories.length}{' '}
                {result.stories.length === 1 ? 'story matches' : 'stories match'} these filters.
              </p>
            )}
            <div className={result.stories.length > 1 ? 'pick-grid' : undefined}>
              {result.stories.map((s, i) => (
                <PickCard
                  key={`${round}-${s.id}`}
                  entry={s}
                  name={result.stories.length > 1 ? `Choice ${i + 1}` : 'Your story'}
                  collectionTitle={collectionLabel(s.collectionId)}
                  flip={flip}
                  delay={i * 120}
                />
              ))}
            </div>
            <div className="row pick-actions">
              <button type="button" className="btn" onClick={doPick}>
                Pick again
              </button>
            </div>
          </>
        )}
      </div>

      {recent.length > 0 && (
        <section aria-labelledby="recent-h" className="recent">
          <h2 id="recent-h">Recently picked</h2>
          <StoryList entries={recent} showCollection label="Recently picked" />
        </section>
      )}
    </div>
  );
}

function PickCard({
  entry,
  name,
  collectionTitle,
  flip,
  delay,
}: {
  entry: IndexEntry;
  name: string;
  collectionTitle: string;
  flip: boolean;
  delay: number;
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
    <section
      className={`pick-card${flip ? ' flip' : ''}`}
      style={flip ? { animationDelay: `${delay}ms` } : undefined}
      aria-label={name}
    >
      <h2 className="pick-title">{entry.title}</h2>
      <p className="muted">
        {collectionTitle} · {entry.readingMinutes} min
      </p>
      {text && <p className="excerpt">{text}</p>}
      <Link to={`/s/${entry.id}`} className="btn primary">
        Read it
      </Link>
    </section>
  );
}
