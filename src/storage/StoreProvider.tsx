import { createContext, useContext, useState, useSyncExternalStore, type ReactNode } from 'react';
import { createStore, type State, type Store } from './store';

const StoreContext = createContext<Store | null>(null);

export function StoreProvider({ store, children }: { store?: Store; children: ReactNode }) {
  const [value] = useState(() => store ?? createStore(localStorage));
  return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}

export function useStore(): Store {
  const store = useContext(StoreContext);
  if (!store) throw new Error('useStore must be used inside <StoreProvider>');
  return store;
}

export function useAppState(): State {
  const store = useStore();
  return useSyncExternalStore(store.subscribe, store.get);
}

export const useSettings = () => useAppState().settings;
