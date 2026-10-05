import { beforeEach, describe, expect, it, vi } from 'vitest';
import {
  DEFAULT_STATE,
  HISTORY_CAP,
  RECENT_PICKS_CAP,
  STORAGE_KEY,
  createStore,
  migrate,
  type Store,
} from './store';

let store: Store;
let now = 1_000;
const clock = () => now;

beforeEach(() => {
  now = 1_000;
  store = createStore(localStorage, clock);
});

const persisted = () => JSON.parse(localStorage.getItem(STORAGE_KEY)!);

describe('store', () => {
  it('starts from defaults when empty', () => {
    expect(store.get()).toEqual(DEFAULT_STATE);
    expect(DEFAULT_STATE.settings).toMatchObject({
      showMature: false,
      showExcluded: false,
      theme: 'system',
    });
  });

  it('persists under one versioned key', () => {
    store.updateSettings({ showMature: true });
    expect(persisted()).toMatchObject({ version: 1, settings: { showMature: true } });
    expect(createStore(localStorage, clock).get().settings.showMature).toBe(true);
  });

  it('resets corrupt JSON with a warning', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    localStorage.setItem(STORAGE_KEY, '{not json');
    expect(createStore(localStorage, clock).get()).toEqual(DEFAULT_STATE);
    expect(warn).toHaveBeenCalled();
    warn.mockRestore();
  });

  it('resets structurally invalid data with a warning, keeping valid settings defaults', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ version: 1, favorites: 'nope', settings: 7 }),
    );
    const s = createStore(localStorage, clock).get();
    expect(s.favorites).toEqual({});
    expect(s.settings).toEqual(DEFAULT_STATE.settings);
    expect(warn).toHaveBeenCalled();
    warn.mockRestore();
  });

  it('fills settings added after the data was saved', () => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ version: 1, settings: { showMature: true } }),
    );
    const s = createStore(localStorage, clock).get();
    expect(s.settings.showMature).toBe(true);
    expect(s.settings.fontSize).toBe(DEFAULT_STATE.settings.fontSize);
  });

  it('survives a throwing storage backend', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    const broken = {
      getItem: () => {
        throw new Error('denied');
      },
      setItem: () => {
        throw new Error('quota');
      },
      removeItem: () => {},
    } as unknown as Storage;
    const s = createStore(broken, clock);
    s.toggleFavorite('a--x');
    expect(s.get().favorites['a--x']).toBe(1_000);
    warn.mockRestore();
  });

  it('prunes ids not in the current index', () => {
    store.toggleFavorite('a--keep');
    store.toggleFavorite('a--gone');
    store.setProgress('a--gone', 3);
    store.markRead('a--gone');
    store.recordPick('a--gone');
    store.prune(new Set(['a--keep']));
    const s = store.get();
    expect(Object.keys(s.favorites)).toEqual(['a--keep']);
    expect(s.progress).toEqual({});
    expect(s.history).toEqual([]);
    expect(s.recentPicks).toEqual([]);
    expect(persisted().favorites).toEqual({ 'a--keep': 1_000 });
  });

  it('toggles favorites with a timestamp', () => {
    store.toggleFavorite('a--x');
    expect(store.get().favorites).toEqual({ 'a--x': 1_000 });
    store.toggleFavorite('a--x');
    expect(store.get().favorites).toEqual({});
  });

  it('records progress and clears it', () => {
    store.setProgress('a--x', 4);
    expect(store.get().progress['a--x']).toEqual({ blockIndex: 4, updatedAt: 1_000 });
    store.clearProgress('a--x');
    expect(store.get().progress).toEqual({});
  });

  it('marks read, newest last, deduplicated, capped', () => {
    for (let i = 0; i < HISTORY_CAP + 5; i++) {
      now = i;
      store.markRead(`a--${i}`);
    }
    now = 9_999;
    store.markRead('a--10');
    const h = store.get().history;
    expect(h).toHaveLength(HISTORY_CAP);
    expect(h.at(-1)).toEqual({ id: 'a--10', readAt: 9_999 });
    expect(h.filter((e) => e.id === 'a--10')).toHaveLength(1);
    expect(h[0]?.id).not.toBe('a--0');
  });

  it('marks unread by removing from history only', () => {
    store.markRead('a--x');
    store.markRead('a--y');
    store.setProgress('a--x', 2);
    store.markUnread('a--x');
    expect(store.get().history.map((h) => h.id)).toEqual(['a--y']);
    expect(store.get().progress['a--x']?.blockIndex).toBe(2);
  });

  it('marking an unread story unread is a no-op', () => {
    const fn = vi.fn();
    store.subscribe(fn);
    store.markUnread('a--x');
    expect(fn).not.toHaveBeenCalled();
  });

  it('caps recent picks', () => {
    for (let i = 0; i < 15; i++) store.recordPick(`a--${i}`);
    expect(store.get().recentPicks).toHaveLength(RECENT_PICKS_CAP);
    expect(store.get().recentPicks.at(-1)).toBe('a--14');
  });

  it('clears reading data but keeps settings', () => {
    store.updateSettings({ theme: 'dark' });
    store.toggleFavorite('a--x');
    store.setProgress('a--x', 1);
    store.markRead('a--x');
    store.recordPick('a--x');
    store.clearReadingData();
    expect(store.get()).toEqual({
      ...DEFAULT_STATE,
      settings: { ...DEFAULT_STATE.settings, theme: 'dark' },
    });
  });

  it('notifies subscribers and returns a new snapshot only on change', () => {
    const fn = vi.fn();
    const unsub = store.subscribe(fn);
    const before = store.get();
    store.toggleFavorite('a--x');
    expect(fn).toHaveBeenCalledTimes(1);
    expect(store.get()).not.toBe(before);
    unsub();
    store.toggleFavorite('a--x');
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it('picks up changes made in another tab', () => {
    const other = createStore(localStorage, clock);
    store.toggleFavorite('a--x');
    window.dispatchEvent(new StorageEvent('storage', { key: STORAGE_KEY }));
    expect(other.get().favorites['a--x']).toBe(1_000);
  });
});

describe('migrate', () => {
  it('is identity for v1', () => {
    const v1 = { version: 1, settings: {}, favorites: {} };
    expect(migrate(v1)).toEqual(v1);
  });
  it('rejects unknown versions', () => {
    expect(() => migrate({ version: 99 })).toThrow();
    expect(() => migrate('x')).toThrow();
  });
});
