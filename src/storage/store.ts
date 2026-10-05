import { z } from 'zod';

export const STORAGE_KEY = 'storybook:v1';
export const HISTORY_CAP = 200;
export const RECENT_PICKS_CAP = 10;

export const THEMES = ['system', 'light', 'sepia', 'dark'] as const;
export const FONT_SIZES = [15, 17, 19, 22, 25] as const;

const settingsSchema = z.object({
  showMature: z.boolean().catch(false),
  showExcluded: z.boolean().catch(false),
  theme: z.enum(THEMES).catch('system'),
  fontSize: z
    .number()
    .int()
    .min(0)
    .max(FONT_SIZES.length - 1)
    .catch(2),
  lineHeight: z.enum(['normal', 'relaxed']).catch('normal'),
  picker: z
    .object({
      collections: z.array(z.string()).catch([]),
      minMinutes: z.number().positive().catch(1),
      /** null = no upper bound */
      maxMinutes: z.number().positive().nullable().catch(5),
      unreadOnly: z.boolean().catch(false),
      favoritesOnly: z.boolean().catch(false),
    })
    .catch({
      collections: [],
      minMinutes: 1,
      maxMinutes: 5,
      unreadOnly: false,
      favoritesOnly: false,
    }),
});

const progressSchema = z.object({
  blockIndex: z.number().int().nonnegative(),
  updatedAt: z.number(),
});

const stateSchema = z.object({
  version: z.literal(1),
  settings: z.unknown().transform((v) => settingsSchema.parse(typeof v === 'object' && v ? v : {})),
  favorites: z.record(z.number()).catch({}),
  progress: z.record(progressSchema).catch({}),
  history: z.array(z.object({ id: z.string(), readAt: z.number() })).catch([]),
  recentPicks: z.array(z.string()).catch([]),
});

export type Settings = z.infer<typeof settingsSchema>;
export type State = z.infer<typeof stateSchema>;
export type Theme = Settings['theme'];

export const DEFAULT_STATE: State = stateSchema.parse({ version: 1, settings: {} });

/** Upgrades older persisted shapes to the current version. v1 is the first, so identity. */
export function migrate(raw: unknown): unknown {
  if (typeof raw !== 'object' || raw === null) throw new Error('Stored state is not an object');
  const version = (raw as { version?: unknown }).version;
  if (version === 1) return raw;
  throw new Error(`Unknown stored state version ${String(version)}`);
}

function parse(json: string | null): State {
  if (json == null) return DEFAULT_STATE;
  try {
    const raw = migrate(JSON.parse(json));
    // Each field falls back to its default independently, so one bad field doesn't wipe the rest.
    const state = stateSchema.parse(raw);
    const rawRec = raw as Record<string, unknown>;
    const repaired = (['favorites', 'progress', 'history', 'recentPicks'] as const).some(
      (k) => k in rawRec && JSON.stringify(rawRec[k]) !== JSON.stringify(state[k]),
    );
    if (repaired) console.warn('[storybook] Some stored data was invalid and has been reset.');
    return state;
  } catch (e) {
    console.warn('[storybook] Stored data was unreadable and has been reset.', e);
    return DEFAULT_STATE;
  }
}

export type Store = ReturnType<typeof createStore>;

export function createStore(storage: Storage, now: () => number = Date.now) {
  const read = () => {
    try {
      return parse(storage.getItem(STORAGE_KEY));
    } catch (e) {
      console.warn('[storybook] Storage unavailable; using defaults.', e);
      return DEFAULT_STATE;
    }
  };
  let state = read();
  const listeners = new Set<() => void>();
  const emit = () => listeners.forEach((l) => l());

  const set = (next: State) => {
    state = next;
    try {
      storage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      console.warn('[storybook] Could not save to storage.', e);
    }
    emit();
  };

  if (typeof window !== 'undefined') {
    window.addEventListener('storage', (e) => {
      if (e.key !== STORAGE_KEY && e.key !== null) return;
      state = read();
      emit();
    });
  }

  const omit = <T>(rec: Record<string, T>, id: string) => {
    const { [id]: _, ...rest } = rec;
    void _;
    return rest;
  };

  return {
    get: () => state,
    subscribe(fn: () => void) {
      listeners.add(fn);
      return () => void listeners.delete(fn);
    },
    updateSettings(patch: Partial<Settings>) {
      set({ ...state, settings: { ...state.settings, ...patch } });
    },
    toggleFavorite(id: string) {
      const favorites =
        id in state.favorites ? omit(state.favorites, id) : { ...state.favorites, [id]: now() };
      set({ ...state, favorites });
    },
    setProgress(id: string, blockIndex: number) {
      if (state.progress[id]?.blockIndex === blockIndex) return;
      set({ ...state, progress: { ...state.progress, [id]: { blockIndex, updatedAt: now() } } });
    },
    clearProgress(id: string) {
      if (!(id in state.progress)) return;
      set({ ...state, progress: omit(state.progress, id) });
    },
    markRead(id: string) {
      const history = [...state.history.filter((h) => h.id !== id), { id, readAt: now() }];
      set({ ...state, history: history.slice(-HISTORY_CAP) });
    },
    markUnread(id: string) {
      if (!state.history.some((h) => h.id === id)) return;
      set({ ...state, history: state.history.filter((h) => h.id !== id) });
    },
    recordPick(id: string) {
      const recentPicks = [...state.recentPicks.filter((p) => p !== id), id];
      set({ ...state, recentPicks: recentPicks.slice(-RECENT_PICKS_CAP) });
    },
    clearReadingData() {
      set({ ...DEFAULT_STATE, settings: state.settings });
    },
    /** Drops user data for stories that no longer exist in the index. */
    prune(known: ReadonlySet<string>) {
      const keep = (id: string) => known.has(id);
      const filterRec = <T>(rec: Record<string, T>) =>
        Object.fromEntries(Object.entries(rec).filter(([id]) => keep(id)));
      const next: State = {
        ...state,
        favorites: filterRec(state.favorites),
        progress: filterRec(state.progress),
        history: state.history.filter((h) => keep(h.id)),
        recentPicks: state.recentPicks.filter(keep),
      };
      if (JSON.stringify(next) !== JSON.stringify(state)) set(next);
    },
  };
}
