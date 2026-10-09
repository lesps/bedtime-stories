import { Link, Navigate, useNavigate } from 'react-router';
import { useVisibleStories } from '../app/useVisibleStories';
import { StoryList } from '../components/StoryRow';
import { useIndex } from '../data/IndexProvider';
import type { IndexEntry } from '../data/types';
import { notebookMarkdown, notebookStories } from '../domain/notebook';
import { isInProgress, progressInfo } from '../domain/progress';
import { useAppState, useStore } from '../storage/StoreProvider';

export function ReadingPage() {
  const { openStoryId, progress, history, annotations, storyNotes } = useAppState();
  const { collectionLabel } = useIndex();
  const store = useStore();
  const navigate = useNavigate();
  const visible = useVisibleStories();
  const byId = new Map(visible.map((s) => [s.id, s]));

  if (openStoryId && byId.has(openStoryId)) {
    return <Navigate replace to={`/s/${openStoryId}`} />;
  }

  const inProgress = Object.entries(progress)
    .filter(([id, p]) => byId.has(id) && isInProgress(p))
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

  const notebook = notebookStories(visible, annotations, storyNotes);
  const exportNotes = () => {
    const md = notebookMarkdown(notebook, annotations, storyNotes, collectionLabel);
    const url = URL.createObjectURL(new Blob([md], { type: 'text/markdown' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = `storybook-notes-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };
  const startOver = (id: string) => {
    store.clearProgress(id);
    navigate(`/s/${id}`);
  };
  const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? '' : 's'}`;

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
          <div className="row">
            <Link to={`/s/${hero.entry.id}`} className="btn primary">
              Keep reading
            </Link>
            <StartOver title={hero.entry.title} onClick={() => startOver(hero.entry.id)} />
          </div>
        </section>
      )}

      {others.length > 0 && (
        <section aria-labelledby="also-h">
          <h2 id="also-h">Also in progress</h2>
          <ul className="story-list shelf-list" aria-label="Also in progress">
            {others.map(({ entry, info }) => (
              <li key={entry.id} className="story-row shelf-row">
                <Link to={`/s/${entry.id}`} className="story-link">
                  <span className="story-title">{entry.title}</span>
                  <span className="story-meta">
                    {collectionLabel(entry.collectionId)}
                    {info && <> · {Math.round(info.fraction * 100)}%</>}
                  </span>
                  {info && <Meter fraction={info.fraction} />}
                </Link>
                <StartOver title={entry.title} onClick={() => startOver(entry.id)} />
              </li>
            ))}
          </ul>
        </section>
      )}

      {notebook.length > 0 && (
        <section aria-labelledby="notebook-h">
          <div className="row section-head">
            <h2 id="notebook-h">Notebook</h2>
            <button type="button" className="btn ghost" onClick={exportNotes}>
              Export notes
            </button>
          </div>
          <ul className="story-list" aria-label="Notebook">
            {notebook.map(({ entry, highlights, notes }) => (
              <li key={entry.id} className="story-row">
                <Link to={`/s/${entry.id}?notes=1`} className="story-link">
                  <span className="story-title">{entry.title}</span>
                  <span className="story-meta">
                    {[highlights && plural(highlights, 'highlight'), notes && plural(notes, 'note')]
                      .filter(Boolean)
                      .join(' · ')}
                  </span>
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

function StartOver({ title, onClick }: { title: string; onClick: () => void }) {
  return (
    <button
      type="button"
      className="btn ghost"
      aria-label={`Start ${title} over`}
      onClick={onClick}
    >
      Start over
    </button>
  );
}
