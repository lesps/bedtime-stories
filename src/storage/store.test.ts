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

  it('defaults the picker to stories up to 5 minutes, one at a time, no tag filters', () => {
    expect(DEFAULT_STATE.settings.picker).toMatchObject({
      minMinutes: 1,
      maxMinutes: 5,
      count: 1,
      cultures: { include: [], exclude: [] },
      themes: { include: [], exclude: [] },
    });
  });

  it('repairs a malformed tag filter without losing the rest of the picker', () => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        version: 1,
        settings: { picker: { maxMinutes: 20, themes: 'nope', count: 7 } },
      }),
    );
    expect(createStore(localStorage, clock).get().settings.picker).toMatchObject({
      maxMinutes: 20,
      themes: { include: [], exclude: [] },
      count: 1,
    });
  });

  it('keeps an older saved maxMinutes and adds the new minimum', () => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ version: 1, settings: { picker: { collections: [], maxMinutes: 20 } } }),
    );
    expect(createStore(localStorage, clock).get().settings.picker).toMatchObject({
      minMinutes: 1,
      maxMinutes: 20,
    });
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

  it('tracks the open story: opening replaces it, closing only clears the matching one', () => {
    expect(store.get().openStoryId).toBeNull();
    store.openStory('a--x');
    store.openStory('a--y');
    expect(store.get().openStoryId).toBe('a--y');
    store.closeStory('a--x');
    expect(store.get().openStoryId).toBe('a--y');
    store.closeStory('a--y');
    expect(store.get().openStoryId).toBeNull();
  });

  it('prunes an unknown open story and clears it with reading data', () => {
    store.openStory('a--gone');
    store.prune(new Set(['a--keep']));
    expect(store.get().openStoryId).toBeNull();
    store.openStory('a--keep');
    store.clearReadingData();
    expect(store.get().openStoryId).toBeNull();
  });

  it('remembers how many blocks a story has alongside its progress', () => {
    store.setProgress('a--x', 3, 12);
    expect(store.get().progress['a--x']).toEqual({
      blockIndex: 3,
      blockCount: 12,
      updatedAt: 1_000,
    });
    store.setProgress('a--y', 2);
    expect(store.get().progress['a--y']).toEqual({ blockIndex: 2, updatedAt: 1_000 });
  });

  describe('highlights and notes', () => {
    const hl = { block: 2, start: 5, end: 16, quote: 'upon a time', color: 'yellow' as const };

    it('adds a highlight and returns its id', () => {
      const id = store.addHighlight('a--x', hl);
      expect(store.get().annotations['a--x']).toEqual([
        { id, ...hl, createdAt: 1_000, updatedAt: 1_000 },
      ]);
    });

    it('updates colour and note, and an empty note removes the note', () => {
      const id = store.addHighlight('a--x', hl);
      now = 2_000;
      store.updateHighlight('a--x', id, { color: 'blue', note: 'Ada laughed here' });
      expect(store.get().annotations['a--x']?.[0]).toMatchObject({
        color: 'blue',
        note: 'Ada laughed here',
        updatedAt: 2_000,
      });
      store.updateHighlight('a--x', id, { note: '   ' });
      expect(store.get().annotations['a--x']?.[0]).not.toHaveProperty('note');
    });

    it('removes a highlight, and the story entry when it was the last one', () => {
      const id = store.addHighlight('a--x', hl);
      store.removeHighlight('a--x', id);
      expect(store.get().annotations).toEqual({});
    });

    it('keeps a story note, and an empty one deletes it', () => {
      store.setStoryNote('a--x', 'Favourite of both kids');
      expect(store.get().storyNotes['a--x']).toEqual({
        text: 'Favourite of both kids',
        updatedAt: 1_000,
      });
      store.setStoryNote('a--x', '');
      expect(store.get().storyNotes).toEqual({});
    });

    it('keeps notes when reading data is cleared, unless asked to include them', () => {
      store.addHighlight('a--x', hl);
      store.setStoryNote('a--x', 'note');
      store.clearReadingData();
      expect(Object.keys(store.get().annotations)).toEqual(['a--x']);
      expect(Object.keys(store.get().storyNotes)).toEqual(['a--x']);
      store.clearReadingData({ includeNotes: true });
      expect(store.get().annotations).toEqual({});
      expect(store.get().storyNotes).toEqual({});
    });

    it('prunes notes for stories no longer in the index', () => {
      store.addHighlight('a--gone', hl);
      store.setStoryNote('a--gone', 'x');
      store.prune(new Set(['a--keep']));
      expect(store.get().annotations).toEqual({});
      expect(store.get().storyNotes).toEqual({});
    });

    it('drops malformed highlights without losing good ones', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          version: 1,
          annotations: {
            'a--x': [
              { id: 'h1', ...hl, createdAt: 1, updatedAt: 1 },
              { id: 'h2', block: 'nope' },
            ],
          },
        }),
      );
      expect(createStore(localStorage, clock).get().annotations['a--x']).toHaveLength(1);
      warn.mockRestore();
    });
  });

  describe('finishing vs read', () => {
    it('finishing marks read, closes the book and keeps progress as finished', () => {
      store.openStory('a--x');
      store.setProgress('a--x', 3, 10);
      store.finishStory('a--x', 10);
      expect(store.get().history.map((h) => h.id)).toEqual(['a--x']);
      expect(store.get().openStoryId).toBeNull();
      expect(store.get().progress['a--x']).toMatchObject({
        blockIndex: 9,
        blockCount: 10,
        finished: true,
      });
    });

    it('rereading overwrites the finished marker but keeps the story read', () => {
      store.finishStory('a--x', 10);
      store.setProgress('a--x', 2, 10);
      expect(store.get().progress['a--x']).not.toHaveProperty('finished');
      expect(store.get().history.map((h) => h.id)).toEqual(['a--x']);
    });

    it('marking unread leaves the reading position alone', () => {
      store.setProgress('a--x', 4, 10);
      store.markRead('a--x');
      store.markUnread('a--x');
      expect(store.get().progress['a--x']?.blockIndex).toBe(4);
    });
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
