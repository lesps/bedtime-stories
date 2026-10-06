import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router';
import { usePrefersReducedMotion } from '../app/theme';
import { useOnline } from '../app/useOnline';
import { FavoriteButton } from '../components/FavoriteButton';
import { CloseIcon, NoteIcon } from '../components/icons';
import { byReadingOrder } from '../domain/notebook';
import { resolveAnchor } from '../domain/annotations';
import { HighlightSheet } from '../notes/HighlightSheet';
import { HighlightToolbar } from '../notes/HighlightToolbar';
import type { Mark } from '../notes/MarkedText';
import { NotesPanel } from '../notes/NotesPanel';
import { readSelection, type SelectionInfo } from '../notes/selection';
import { DataError, loadStory } from '../data/client';
import { useIndex } from '../data/IndexProvider';
import type { Story } from '../data/types';
import { neighbors } from '../domain/navigation';
import { isVisible } from '../domain/visibility';
import { NotFoundPage } from '../pages/NotFoundPage';
import { FONT_SIZES } from '../storage/store';
import { useAppState, useSettings, useStore } from '../storage/StoreProvider';
import type { Highlight, HighlightColor } from '../storage/store';
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
  const { byId, stories, collectionsById, collectionLabel, tagsOf, tagDef } = useIndex();
  const settings = useSettings();
  const entry = byId.get(storyId);
  const visible = entry ? isVisible(entry, settings) : false;
  const [load, setLoad] = useState<Load>({ status: 'loading' });
  const [attempt, setAttempt] = useState(0);

  const store = useStore();
  const navigate = useNavigate();
  const [, setHeaderParams] = useSearchParams();
  useEffect(() => {
    if (entry && visible) store.openStory(entry.id);
  }, [store, entry, visible]);

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
  const versions = entry.workId
    ? stories.filter(
        (s) => s.workId === entry.workId && s.id !== entry.id && isVisible(s, settings),
      )
    : [];

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
              <button
                type="button"
                className="icon-btn"
                aria-label="Notes"
                onClick={() =>
                  setHeaderParams(
                    (p) => {
                      p.set('notes', '1');
                      return p;
                    },
                    { replace: true },
                  )
                }
              >
                <NoteIcon />
              </button>
              <FavoriteButton id={entry.id} title={entry.title} />
              <button
                type="button"
                className="icon-btn"
                aria-label="Close book"
                onClick={() => {
                  store.closeStory(entry.id);
                  navigate('/reading');
                }}
              >
                <CloseIcon />
              </button>
            </div>
          </div>
          <h1>{entry.title}</h1>
          <p className="muted byline">
            {collection?.contributor ?? collection?.author}
            {load.status === 'ready' && load.story.origin && <> · {load.story.origin}</>}
            {load.status === 'ready' && load.story.firstPublished && (
              <> · {load.story.firstPublished}</>
            )}
            {' · '}
            {entry.readingMinutes} min read
            {load.status === 'ready' && load.story.source && (
              <>
                {' · '}
                <a href={load.story.source} rel="noopener noreferrer" target="_blank">
                  Source
                </a>
              </>
            )}
          </p>
          <ul className="tag-chips" aria-label="Tags">
            {(['cultures', 'themes'] as const).flatMap((kind) =>
              tagsOf(entry.id)[kind].map((t) => (
                <li key={`${kind}-${t}`}>
                  <Link to={`/tags/${kind}/${t}`} className="tag-chip" data-kind={kind}>
                    {tagDef(kind, t)?.label ?? t}
                  </Link>
                </li>
              )),
            )}
          </ul>
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

        {load.status !== 'loading' && versions.length > 0 && (
          <nav className="versions" aria-label="Other versions">
            <h2>Other versions</h2>
            <ul>
              {versions.map((v) => (
                <li key={v.id}>
                  <Link to={`/s/${v.id}`}>{v.title}</Link>{' '}
                  <span className="muted">
                    {[
                      collectionLabel(v.collectionId),
                      collectionsById.get(v.collectionId)?.contributor,
                      `${v.readingMinutes} min`,
                    ]
                      .filter(Boolean)
                      .join(' · ')}
                  </span>
                </li>
              ))}
            </ul>
          </nav>
        )}
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
  // Opening a story always carries on from the saved place, unless it was finished (then: top).
  const [saved] = useState(() => {
    const p = store.get().progress[story.id];
    return p && !p.finished && p.blockIndex > 0 && p.blockIndex < story.blocks.length
      ? p.blockIndex
      : null;
  });
  const [root, setRoot] = useState<HTMLElement | null>(null);
  const finished = useRef(false);
  const [params, setParams] = useSearchParams();
  const notesOpen = params.get('notes') === '1';
  const { annotations, storyNotes } = useAppState();
  const highlights = useMemo(() => annotations[story.id] ?? [], [annotations, story.id]);
  const [selection, setSelection] = useState<SelectionInfo | null>(null);
  const [sheet, setSheet] = useState<{ id: string; focusNote: boolean } | null>(null);

  const onTopmost = useCallback(
    (i: number) => {
      if (finished.current || i === 0) return;
      store.setProgress(story.id, i, story.blocks.length);
    },
    [store, story.id, story.blocks.length],
  );
  const onFinal = useCallback(() => {
    finished.current = true;
    store.finishStory(story.id, story.blocks.length);
  }, [store, story.id, story.blocks.length]);

  useReadingTracker(root, story.blocks.length, onTopmost, onFinal);

  useEffect(() => {
    if (!root || saved == null) return;
    root.querySelector(`[data-block="${saved}"]`)?.scrollIntoView({ block: 'start' });
  }, [root, saved]);

  // Highlights are anchored to the displayed (typeset) text; re-anchor by quote if it moved.
  const { marksByBlock, placed, detached } = useMemo(() => {
    const marksByBlock = new Map<number, Mark[]>();
    const placed: Highlight[] = [];
    const detached: Highlight[] = [];
    for (const h of highlights) {
      const b = story.blocks[h.block];
      const at = b && b.type !== 'image' ? resolveAnchor(b.text, h) : null;
      if (!at) {
        detached.push(h);
        continue;
      }
      placed.push(h);
      const list = marksByBlock.get(h.block) ?? [];
      list.push({ id: h.id, ...at, color: h.color, hasNote: !!h.note });
      marksByBlock.set(h.block, list);
    }
    return { marksByBlock, placed: placed.sort(byReadingOrder), detached };
  }, [highlights, story.blocks]);

  useEffect(() => {
    if (!root) return;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const onChange = () => {
      clearTimeout(timer);
      timer = setTimeout(() => setSelection(readSelection(root)), 120);
    };
    document.addEventListener('selectionchange', onChange);
    return () => {
      clearTimeout(timer);
      document.removeEventListener('selectionchange', onChange);
    };
  }, [root]);

  const highlight = (color: HighlightColor, focusNote = false) => {
    if (!selection) return;
    const { block, start, end, quote } = selection;
    const id = store.addHighlight(story.id, { block, start, end, quote, color });
    window.getSelection()?.removeAllRanges();
    setSelection(null);
    if (focusNote) setSheet({ id, focusNote: true });
  };

  const closeNotes = () =>
    setParams(
      (p) => {
        p.delete('notes');
        return p;
      },
      { replace: true },
    );

  const jumpTo = (h: Highlight) => {
    closeNotes();
    root
      ?.querySelector(`[data-block="${h.block}"]`)
      ?.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'center' });
  };

  const open = sheet && highlights.find((h) => h.id === sheet.id);

  return (
    <>
      <div className="story-body" ref={setRoot}>
        {story.blocks.map((b, i) => (
          <BlockRenderer
            key={i}
            block={b}
            index={i}
            priority={i === 0}
            marks={marksByBlock.get(i)}
            onMark={(id) => setSheet({ id, focusNote: false })}
          />
        ))}
      </div>
      {selection && !sheet && (
        <HighlightToolbar
          selection={selection}
          onColor={(c) => highlight(c)}
          onNote={() => highlight('yellow', true)}
        />
      )}
      {open && (
        <HighlightSheet
          key={open.id}
          highlight={open}
          focusNote={sheet.focusNote}
          onColor={(color) => store.updateHighlight(story.id, open.id, { color })}
          onSaveNote={(note) => store.updateHighlight(story.id, open.id, { note })}
          onDelete={() => {
            store.removeHighlight(story.id, open.id);
            setSheet(null);
          }}
          onClose={() => setSheet(null)}
        />
      )}
      {notesOpen && (
        <NotesPanel
          storyNote={storyNotes[story.id]?.text ?? ''}
          highlights={placed}
          detached={detached}
          onSaveStoryNote={(text) => store.setStoryNote(story.id, text)}
          onJump={jumpTo}
          onClose={closeNotes}
        />
      )}
    </>
  );
}
