import { useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router';
import { TagCards } from '../components/TagCards';
import { StoryList } from '../components/StoryRow';
import { SparkleIcon } from '../components/icons';
import { useIndex } from '../data/IndexProvider';
import { LengthSlider } from '../components/LengthSlider';
import { FULL_RANGE, inRange, isFullRange, type LengthRange } from '../domain/length';
import { matchesQuery } from '../domain/search';
import { useAppState } from '../storage/StoreProvider';
import { useVisibleStories } from '../app/useVisibleStories';

const BROWSE = [
  { id: 'collections', label: 'Collections' },
  { id: 'cultures', label: 'Cultures' },
  { id: 'themes', label: 'Themes' },
] as const;

export function LibraryPage() {
  const { collections, tagLabels } = useIndex();
  const [params, setParams] = useSearchParams();
  const by = BROWSE.find((b) => b.id === params.get('by'))?.id ?? 'collections';
  const visible = useVisibleStories();
  const { progress } = useAppState();
  const [query, setQuery] = useState('');
  const [length, setLength] = useState<LengthRange>(FULL_RANGE);

  const results = useMemo(
    () =>
      visible
        .filter((s) => matchesQuery(s, query, tagLabels(s.id)) && inRange(s.readingMinutes, length))
        .sort((a, b) => a.title.localeCompare(b.title)),
    [visible, query, length, tagLabels],
  );
  const inProgress = useMemo(
    () =>
      visible
        .filter((s) => s.id in progress)
        .sort((a, b) => progress[b.id]!.updatedAt - progress[a.id]!.updatedAt),
    [visible, progress],
  );
  const filtering = query.trim() !== '' || !isFullRange(length);

  return (
    <div className="page">
      <h1 className="page-title">Storybook</h1>

      <Link to="/surprise" className="surprise-cta">
        <SparkleIcon size={26} />
        <span>
          <strong>Surprise me</strong>
          <span className="sub">Pick tonight’s story</span>
        </span>
      </Link>

      {inProgress.length > 0 && !filtering && (
        <section aria-labelledby="continue-h">
          <h2 id="continue-h">Continue reading</h2>
          <StoryList entries={inProgress} showCollection label="Continue reading" />
        </section>
      )}

      <section aria-labelledby="find-h" className="finder">
        <h2 id="find-h">Find a story</h2>
        <input
          type="search"
          className="search"
          placeholder="Search titles, cultures, themes"
          aria-label="Search titles"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <LengthSlider value={length} onChange={setLength} />
      </section>

      {filtering ? (
        <section aria-label="Results">
          <p className="muted" role="status">
            {results.length} {results.length === 1 ? 'story' : 'stories'}
          </p>
          <StoryList entries={results} showCollection label="Results" />
        </section>
      ) : (
        <section aria-labelledby="browse-h">
          <h2 id="browse-h">Browse by</h2>
          <div className="chips" role="radiogroup" aria-label="Browse by">
            {BROWSE.map((b) => (
              <button
                key={b.id}
                type="button"
                role="radio"
                className="chip"
                aria-checked={by === b.id}
                onClick={() =>
                  setParams(b.id === 'collections' ? {} : { by: b.id }, { replace: true })
                }
              >
                {b.label}
              </button>
            ))}
          </div>
          {by === 'collections' ? (
            <ul className="collections">
              {collections.map((c) => {
                const count = visible.filter((s) => s.collectionId === c.id).length;
                return (
                  <li key={c.id}>
                    <Link to={`/c/${c.id}`} className="collection-card" data-collection={c.id}>
                      <span className="collection-title">{c.title}</span>
                      <span className="muted">{c.contributor ?? c.author}</span>
                      <span className="count">{count} stories</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          ) : (
            <TagCards kind={by} />
          )}
        </section>
      )}
      <p className="footer-links">
        <Link to="/about">About &amp; credits</Link>
      </p>
    </div>
  );
}
