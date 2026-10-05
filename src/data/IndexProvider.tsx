import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { useStore } from '../storage/StoreProvider';
import { collectionLabels } from '../domain/collectionLabel';
import { loadIndex, loadTags } from './client';
import type { Collection, Index, IndexEntry, StoryTags, TagDef, TagKind, Tags } from './types';

const NO_TAGS: StoryTags = { cultures: [], themes: [] };

type IndexValue = Index & {
  byId: Map<string, IndexEntry>;
  collectionsById: Map<string, Collection>;
  tags: Tags;
  /** Collection title, with the credited surname added where two collections share a title. */
  collectionLabel: (collectionId: string) => string;
  tagsOf: (storyId: string) => StoryTags;
  tagDef: (kind: TagKind, id: string) => TagDef | undefined;
  /** Every tag label on a story, for search. */
  tagLabels: (storyId: string) => string[];
};

const IndexContext = createContext<IndexValue | null>(null);

export function IndexProvider({ children }: { children: ReactNode }) {
  const store = useStore();
  const [state, setState] = useState<
    | { status: 'loading' }
    | { status: 'error'; error: unknown }
    | { status: 'ready'; value: IndexValue }
  >({ status: 'loading' });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let live = true;
    Promise.all([loadIndex(), loadTags()]).then(
      ([index, tags]) => {
        if (!live) return;
        const byId = new Map(index.stories.map((s) => [s.id, s]));
        store.prune(new Set(byId.keys()));
        const defs = {
          cultures: new Map(tags.cultures.map((t) => [t.id, t])),
          themes: new Map(tags.themes.map((t) => [t.id, t])),
        };
        const tagsOf = (id: string) => tags.stories[id] ?? NO_TAGS;
        const labels = collectionLabels(index.collections);
        setState({
          status: 'ready',
          value: {
            ...index,
            byId,
            collectionsById: new Map(index.collections.map((c) => [c.id, c])),
            tags,
            collectionLabel: (id) => labels.get(id) ?? id,
            tagsOf,
            tagDef: (kind, id) => defs[kind].get(id),
            tagLabels: (id) => {
              const t = tagsOf(id);
              return [
                ...t.cultures.map((c) => defs.cultures.get(c)?.label ?? c),
                ...t.themes.map((c) => defs.themes.get(c)?.label ?? c),
              ];
            },
          },
        });
      },
      (error: unknown) => live && setState({ status: 'error', error }),
    );
    return () => {
      live = false;
    };
  }, [store, attempt]);

  if (state.status === 'loading')
    return (
      <p className="status" role="status">
        Loading stories…
      </p>
    );
  if (state.status === 'error')
    return (
      <div className="status" role="alert">
        <p>Couldn’t load the story library. Check your connection and try again.</p>
        <button
          type="button"
          className="btn"
          onClick={() => {
            setState({ status: 'loading' });
            setAttempt((a) => a + 1);
          }}
        >
          Try again
        </button>
      </div>
    );
  return <IndexContext.Provider value={state.value}>{children}</IndexContext.Provider>;
}

export function useIndex(): IndexValue {
  const v = useContext(IndexContext);
  if (!v) throw new Error('useIndex must be used inside <IndexProvider>');
  return v;
}
