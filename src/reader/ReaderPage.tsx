import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router';
import { usePrefersReducedMotion } from '../app/theme';
import { useOnline } from '../app/useOnline';
import { FavoriteButton } from '../components/FavoriteButton';
import { DataError, loadStory } from '../data/client';
import { useIndex } from '../data/IndexProvider';
import type { Story } from '../data/types';
import { neighbors } from '../domain/navigation';
import { isVisible } from '../domain/visibility';
import { NotFoundPage } from '../pages/NotFoundPage';
import { FONT_SIZES } from '../storage/store';
import { useSettings, useStore } from '../storage/StoreProvider';
import { BlockRenderer } from './BlockRenderer';
import { ProgressBar } from './ProgressBar';
import { ReaderControls } from './ReaderControls';
import { useReadingTracker } from './useReadingTracker';

export function ReaderRoute() {
  const { storyId = '' } = useParams();
  return <ReaderPage key={storyId} storyId={storyId} />;
}

type Load =
  { status: 'loading' } | { status: 'error'; error: unknown } | { status: 'ready'; story: Story };

function ReaderPage({ storyId }: { storyId: string }) {
  const { byId, stories, collectionsById } = useIndex();
  const settings = useSettings();
  const entry = byId.get(storyId);
  const visible = entry ? isVisible(entry, settings) : false;
  const [load, setLoad] = useState<Load>({ status: 'loading' });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (!entry || !visible) return;
    let live = true;
    loadStory(storyId).then(
      (story) => live && setLoad({ status: 'ready', story }),
      (error: unknown) => live && setLoad({ status: 'error', error }),
    );
    return () => {
      live = false;
    };
  }, [storyId, entry, visible, attempt]);

  if (!entry) return <NotFoundPage />;
  if (!visible)
    return (
      <div className="page">
        <h1 className="page-title">This story is hidden</h1>
        <p>It’s hidden by your content settings. A grown-up can change that in Settings.</p>
        <Link to="/">Back to the library</Link>
      </div>
    );

  const collection = collectionsById.get(entry.collectionId);
  const { prev, next } = neighbors(stories, storyId, settings);

  return (
    <>
      <ProgressBar />
      <article
        className="reader"
        style={
          {
            '--reader-size': `${FONT_SIZES[settings.fontSize]}px`,
            '--reader-leading': settings.lineHeight === 'relaxed' ? 1.9 : 1.6,
          } as React.CSSProperties
        }
      >
        <header className="story-header">
          <div className="story-header-top">
            <Link to={`/c/${entry.collectionId}`} className="muted crumb">
              {collection?.title}
            </Link>
            <div className="row">
              <ReaderControls />
              <FavoriteButton id={entry.id} title={entry.title} />
            </div>
          </div>
          <h1>{entry.title}</h1>
          <p className="muted byline">
            {collection?.contributor ?? collection?.author}
            {load.status === 'ready' && load.story.origin && <> · {load.story.origin}</>}
            {' · '}
            {entry.readingMinutes} min read
          </p>
        </header>

        {load.status === 'loading' && (
          <p className="status" role="status">
            Opening the book…
          </p>
        )}
        {load.status === 'error' && (
          <LoadError
            error={load.error}
            onRetry={() => (setLoad({ status: 'loading' }), setAttempt((a) => a + 1))}
          />
        )}
        {load.status === 'ready' && <StoryBody story={load.story} />}

        {load.status !== 'loading' && (
          <nav className="story-nav" aria-label="More stories">
            {prev ? (
              <Link to={`/s/${prev.id}`} rel="prev">
                <span className="muted">← Previous</span>
                <span>{prev.title}</span>
              </Link>
            ) : (
              <span />
            )}
            {next ? (
              <Link to={`/s/${next.id}`} rel="next" className="next">
                <span className="muted">Next →</span>
                <span>{next.title}</span>
              </Link>
            ) : (
              <span />
            )}
          </nav>
        )}
      </article>
    </>
  );
}

function LoadError({ error, onRetry }: { error: unknown; onRetry: () => void }) {
  const online = useOnline();
  const offline = !online || (error instanceof DataError && error.kind === 'network');
  return (
    <div className="status" role="alert">
      {offline ? (
        <>
          <p>
            <strong>This story isn’t saved for offline reading yet.</strong>
          </p>
          <p>
            Connect to the internet to open it. To read anywhere, use{' '}
            <Link to="/settings">Settings → Make all stories available offline</Link>.
          </p>
        </>
      ) : (
        <p>Something went wrong opening this story.</p>
      )}
      <button type="button" className="btn" onClick={onRetry}>
        Try again
      </button>
    </div>
  );
}

function StoryBody({ story }: { story: Story }) {
  const store = useStore();
  const reducedMotion = usePrefersReducedMotion();
  const [saved] = useState(() => store.get().progress[story.id]?.blockIndex ?? null);
  const [offer, setOffer] = useState(saved != null && saved > 0 && saved < story.blocks.length);
  const [root, setRoot] = useState<HTMLElement | null>(null);
  const finished = useRef(false);

  const onTopmost = useCallback(
    (i: number) => {
      if (finished.current || i === 0) return;
      store.setProgress(story.id, i);
      setOffer(false);
    },
    [store, story.id],
  );
  const onFinal = useCallback(() => {
    finished.current = true;
    store.clearProgress(story.id);
    store.markRead(story.id);
    setOffer(false);
  }, [store, story.id]);

  useReadingTracker(root, story.blocks.length, onTopmost, onFinal);

  const resume = () => {
    setOffer(false);
    root
      ?.querySelector(`[data-block="${saved}"]`)
      ?.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'start' });
  };

  return (
    <>
      {offer && (
        <div className="resume" role="region" aria-label="Resume">
          <button type="button" className="btn primary" onClick={resume}>
            Continue from where you left off
          </button>
          <button type="button" className="btn ghost" onClick={() => setOffer(false)}>
            Start over
          </button>
        </div>
      )}
      <div className="story-body" ref={setRoot}>
        {story.blocks.map((b, i) => (
          <BlockRenderer key={i} block={b} index={i} priority={i === 0} />
        ))}
      </div>
    </>
  );
}
