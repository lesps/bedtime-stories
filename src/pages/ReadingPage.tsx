import { Link, Navigate } from 'react-router';
import { useVisibleStories } from '../app/useVisibleStories';
import { StoryList } from '../components/StoryRow';
import { useIndex } from '../data/IndexProvider';
import type { IndexEntry } from '../data/types';
import { progressInfo } from '../domain/progress';
import { useAppState } from '../storage/StoreProvider';

export function ReadingPage() {
  const { openStoryId, progress, history } = useAppState();
  const { collectionLabel } = useIndex();
  const visible = useVisibleStories();
  const byId = new Map(visible.map((s) => [s.id, s]));

  if (openStoryId && byId.has(openStoryId)) {
    return <Navigate replace to={`/s/${openStoryId}?resume=1`} />;
  }

  const inProgress = Object.entries(progress)
    .filter(([id]) => byId.has(id))
    .sort(([, a], [, b]) => b.updatedAt - a.updatedAt)
    .map(([id, p]) => ({
      entry: byId.get(id)!,
      info: progressInfo(p, byId.get(id)!.readingMinutes),
    }));
  const [hero, ...others] = inProgress;
  const finished = [...history]
    .reverse()
    .map((h) => byId.get(h.id))
    .filter((s): s is IndexEntry => !!s)
    .slice(0, 5);

  return (
    <div className="page">
      <h1 className="page-title">Reading</h1>

      {!hero && (
        <p className="muted">
          Nothing on the go. Open a story from the <Link to="/">library</Link> or let{' '}
          <Link to="/surprise">Surprise me</Link> choose one, and it will wait for you here.
        </p>
      )}

      {hero && (
        <section className="shelf-hero" aria-label="Pick up where you left off">
          <p className="muted eyebrow">Pick up where you left off</p>
          <h2 className="pick-title">{hero.entry.title}</h2>
          <p className="muted">
            {collectionLabel(hero.entry.collectionId)}
            {hero.info && (
              <>
                {' '}
                · {Math.round(hero.info.fraction * 100)}% · about {hero.info.minutesLeft} min left
              </>
            )}
          </p>
          {hero.info && <Meter fraction={hero.info.fraction} />}
          <Link to={`/s/${hero.entry.id}?resume=1`} className="btn primary">
            Keep reading
          </Link>
        </section>
      )}

      {others.length > 0 && (
        <section aria-labelledby="also-h">
          <h2 id="also-h">Also in progress</h2>
          <ul className="story-list shelf-list" aria-label="Also in progress">
            {others.map(({ entry, info }) => (
              <li key={entry.id} className="story-row">
                <Link to={`/s/${entry.id}?resume=1`} className="story-link">
                  <span className="story-title">{entry.title}</span>
                  <span className="story-meta">
                    {collectionLabel(entry.collectionId)}
                    {info && <> · {Math.round(info.fraction * 100)}%</>}
                  </span>
                  {info && <Meter fraction={info.fraction} />}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      {finished.length > 0 && (
        <section aria-labelledby="finished-h">
          <h2 id="finished-h">Recently finished</h2>
          <StoryList entries={finished} showCollection label="Recently finished" />
        </section>
      )}
    </div>
  );
}

function Meter({ fraction }: { fraction: number }) {
  return (
    <span className="meter" aria-hidden="true">
      <span style={{ width: `${Math.round(fraction * 100)}%` }} />
    </span>
  );
}
