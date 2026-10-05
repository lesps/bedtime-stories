import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { useStore } from '../storage/StoreProvider';
import { loadIndex } from './client';
import type { Collection, Index, IndexEntry } from './types';

type IndexValue = Index & {
  byId: Map<string, IndexEntry>;
  collectionsById: Map<string, Collection>;
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
    loadIndex().then(
      (index) => {
        if (!live) return;
        const byId = new Map(index.stories.map((s) => [s.id, s]));
        store.prune(new Set(byId.keys()));
        setState({
          status: 'ready',
          value: {
            ...index,
            byId,
            collectionsById: new Map(index.collections.map((c) => [c.id, c])),
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
