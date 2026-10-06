import { z } from 'zod';

export const STORAGE_KEY = 'storybook:v1';
export const HISTORY_CAP = 200;
export const RECENT_PICKS_CAP = 10;

export const THEMES = ['system', 'light', 'sepia', 'dark'] as const;
export const FONT_SIZES = [15, 17, 19, 22, 25] as const;

const tagFilter = z
  .object({ include: z.array(z.string()).catch([]), exclude: z.array(z.string()).catch([]) })
  .catch({ include: [], exclude: [] });

const DEFAULT_PICKER = {
  collections: [],
  minMinutes: 1,
  maxMinutes: 5,
  unreadOnly: false,
  favoritesOnly: false,
  cultures: { include: [], exclude: [] },
  themes: { include: [], exclude: [] },
  count: 1 as const,
};

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
      cultures: tagFilter,
      themes: tagFilter,
      /** How many stories to offer at once. */
      count: z.union([z.literal(1), z.literal(3)]).catch(1),
    })
    .catch(() => DEFAULT_PICKER),
});

const progressSchema = z.object({
  blockIndex: z.number().int().nonnegative(),
  /** Total blocks in the story, so progress can be shown as a fraction. */
  blockCount: z.number().int().positive().optional(),
  updatedAt: z.number(),
});

export const HIGHLIGHT_COLORS = ['yellow', 'green', 'blue', 'pink'] as const;

const highlightSchema = z.object({
  id: z.string().min(1),
  block: z.number().int().nonnegative(),
  start: z.number().int().nonnegative(),
  end: z.number().int().positive(),
  /** The highlighted text, used to re-anchor if a story's wording ever changes. */
  quote: z.string().min(1),
  color: z.enum(HIGHLIGHT_COLORS).catch('yellow'),
  note: z.string().optional(),
  createdAt: z.number(),
  updatedAt: z.number(),
});

/** Keeps the valid items of an array and drops the rest. */
const validItems = <S extends z.ZodTypeAny>(schema: S) =>
  z.array(z.unknown()).transform((xs): z.output<S>[] =>
    xs.flatMap((x) => {
      const r = schema.safeParse(x);
      return r.success ? [r.data as z.output<S>] : [];
    }),
  );

const stateSchema = z.object({
  version: z.literal(1),
  settings: z.unknown().transform((v) => settingsSchema.parse(typeof v === 'object' && v ? v : {})),
  favorites: z.record(z.number()).catch({}),
  progress: z.record(progressSchema).catch({}),
  history: z.array(z.object({ id: z.string(), readAt: z.number() })).catch([]),
  recentPicks: z.array(z.string()).catch([]),
  /** The story the Reading tab returns to; cleared when finished or closed. */
  openStoryId: z.string().nullable().catch(null),
  /** Highlights (optionally with a passage note) per story. */
  annotations: z.record(validItems(highlightSchema)).catch({}),
  /** One free-form note per story. */
  storyNotes: z.record(z.object({ text: z.string(), updatedAt: z.number() })).catch({}),
});

export type Settings = z.infer<typeof settingsSchema>;
export type PickerSettings = Settings['picker'];
export type State = z.infer<typeof stateSchema>;
export type Theme = Settings['theme'];
export type Highlight = z.infer<typeof highlightSchema>;
export type HighlightColor = (typeof HIGHLIGHT_COLORS)[number];

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
    const repaired = (
      ['favorites', 'progress', 'history', 'recentPicks', 'annotations'] as const
    ).some((k) => k in rawRec && JSON.stringify(rawRec[k]) !== JSON.stringify(state[k]));
    if (repaired) console.warn('[storybook] Some stored data was invalid and has been reset.');
    return state;
  } catch (e) {
    console.warn('[storybook] Stored data was unreadable and has been reset.', e);
    return DEFAULT_STATE;
  }
}

const newId = () =>
  typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;

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
    setProgress(id: string, blockIndex: number, blockCount?: number) {
      const prev = state.progress[id];
      if (prev?.blockIndex === blockIndex && prev.blockCount === blockCount) return;
      const entry = { blockIndex, ...(blockCount ? { blockCount } : {}), updatedAt: now() };
      set({ ...state, progress: { ...state.progress, [id]: entry } });
    },
    openStory(id: string) {
      if (state.openStoryId === id) return;
      set({ ...state, openStoryId: id });
    },
    closeStory(id: string) {
      if (state.openStoryId !== id) return;
      set({ ...state, openStoryId: null });
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
    /** Clears favorites, progress and history; highlights and notes only if asked. */
    clearReadingData({ includeNotes = false }: { includeNotes?: boolean } = {}) {
      set({
        ...DEFAULT_STATE,
        settings: state.settings,
        ...(includeNotes ? {} : { annotations: state.annotations, storyNotes: state.storyNotes }),
      });
    },
    addHighlight(
      storyId: string,
      h: Pick<Highlight, 'block' | 'start' | 'end' | 'quote' | 'color'> & { note?: string },
    ): string {
      const id = newId();
      const t = now();
      const list = [
        ...(state.annotations[storyId] ?? []),
        { id, ...h, createdAt: t, updatedAt: t },
      ];
      set({ ...state, annotations: { ...state.annotations, [storyId]: list } });
      return id;
    },
    updateHighlight(storyId: string, id: string, patch: { color?: HighlightColor; note?: string }) {
      const list = (state.annotations[storyId] ?? []).map((h) => {
        if (h.id !== id) return h;
        const next: Highlight = { ...h, ...patch, updatedAt: now() };
        if (patch.note !== undefined && !patch.note.trim()) delete next.note;
        return next;
      });
      set({ ...state, annotations: { ...state.annotations, [storyId]: list } });
    },
    removeHighlight(storyId: string, id: string) {
      const list = (state.annotations[storyId] ?? []).filter((h) => h.id !== id);
      const annotations = list.length
        ? { ...state.annotations, [storyId]: list }
        : omit(state.annotations, storyId);
      set({ ...state, annotations });
    },
    setStoryNote(storyId: string, text: string) {
      const storyNotes = text.trim()
        ? { ...state.storyNotes, [storyId]: { text, updatedAt: now() } }
        : omit(state.storyNotes, storyId);
      set({ ...state, storyNotes });
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
        openStoryId: state.openStoryId && keep(state.openStoryId) ? state.openStoryId : null,
        annotations: filterRec(state.annotations),
        storyNotes: filterRec(state.storyNotes),
      };
      if (JSON.stringify(next) !== JSON.stringify(state)) set(next);
    },
  };
}
