# Storybook — Spec

A reader for public-domain children's stories: browse collections, read in a calm typographic reader, bookmark favorites, resume where you left off, and let a random picker choose tonight's story.

The story data is already built and ships in `compendium/`. This spec covers the app only. Work is split into six self-contained sessions sized for Claude Code (Sonnet 4.6); each can run without reading the others.

## Decisions

**Static PWA, no backend.** Vite + React 18 + TypeScript (strict), React Router, Vitest + Testing Library for unit/component tests, Playwright for e2e, `vite-plugin-pwa` for offline. All state is per-device in `localStorage`. There is no account system and nothing to sync; that is a deliberate scope cut, not an oversight. If sync is ever wanted, the storage module (Session 4) is the only seam that changes.

**Data is static JSON served from `public/compendium/`.** The index (80 KB) loads at startup; story files (3.1 MB total) load on demand; images (8.8 MB, Aesop only) are runtime-cached, not precached.

**"Bookmarking" means two things:** a user-toggled _favorite_ per story, and an automatic _resume position_ per story. No arbitrary mid-text bookmarks in v1.

**Child-safety defaults are on.** Stories with `excluded: true` never appear anywhere unless a parent setting reveals them. Stories flagged `mature-themes` are hidden by default from the library _and_ the random picker, with a settings toggle to show them. The flags are an editorial first pass, not an exhaustive review.

**TDD throughout.** Each session writes or updates failing tests first. A session is not done if new behavior lacks coverage.

**Docs are deliverables.** Every session leaves `CLAUDE.md`, `README.md`, and `CHANGELOG.md` accurate to the code as it actually is.

## The compendium

```
compendium/
  index.json                      # collections + lightweight story index
  stories/<storyId>.json          # full story, one file each
  images/<collectionId>/<file>    # illustrations (Aesop / Milo Winter only)
tools/build_compendium.py         # regenerates compendium/ from Gutenberg sources
```

319 stories across six collections, about 399k words:

| collectionId     | Collection                                    | Stories | Median words | Notes                                                    |
| ---------------- | --------------------------------------------- | ------- | ------------ | -------------------------------------------------------- |
| `aesop`          | The Aesop for Children (Milo Winter, 1919)    | 147     | 161          | every fable has a `moral`; 111 illustrations             |
| `grimm`          | Grimms' Fairy Tales (tr. Taylor & Edwardes)   | 62      | 1,471        |                                                          |
| `andersen`       | Andersen's Fairy Tales                        | 18      | 1,913        | small selection; see Known gaps                          |
| `lang-blue`      | The Blue Fairy Book (ed. Andrew Lang, 1889)   | 37      | 3,351        | most stories carry an `origin` (e.g. "Charles Perrault") |
| `jacobs-english` | English Fairy Tales (ed. Joseph Jacobs, 1890) | 43      | 1,007        | dialect-heavy in places                                  |
| `kipling-justso` | Just So Stories (Kipling, 1902)               | 12      | 2,562        | each story ends with a verse                             |

### `index.json`

```ts
type Index = {
  schemaVersion: 1;
  collections: {
    id: string;
    title: string;
    author: string;
    contributor: string | null; // translator/editor/illustrator credit
    firstPublished: number | null;
    source: string; // gutenberg.org ebook URL
    license: 'Public domain in the USA';
    storyCount: number;
  }[];
  stories: {
    id: string; // "<collectionId>--<slug>", stable, URL-safe
    collectionId: string;
    order: number; // 1-based position in the source book
    title: string;
    wordCount: number;
    readingMinutes: number; // round(words / 180), min 1
    excluded: boolean;
    flags: ('mature-themes' | 'racial-slur')[];
    hasImages: boolean;
  }[];
};
```

### `stories/<id>.json`

Same fields as the index entry (minus `hasImages`), plus:

```ts
type Story = IndexEntry & {
  origin: string | null; // source attribution from the book's footnote, e.g. "Asbjornsen and Moe."
  moral: string | null; // Aesop only; also present as a "moral" block in reading order
  blocks: Block[];
};

type Block =
  | { type: 'p'; text: string }
  | { type: 'verse'; text: string } // preserve newlines and leading spaces
  | { type: 'moral'; text: string }
  | { type: 'heading'; text: string } // in-story chapter heads (e.g. Lilliput "Chapter I")
  | { type: 'note'; text: string } // editor's footnote; render as a small aside
  | { type: 'image'; src: string; alt: string }; // src relative to compendium/
```

Text is plain Unicode (curly quotes preserved); no inline markup.

### Licensing

All texts and the Milo Winter illustrations are public domain in the US. Project Gutenberg boilerplate has been stripped, so the Gutenberg trademark license doesn't attach. The app should not use "Project Gutenberg" as branding; a factual source link on the About page is fine. Non-US distribution: Kipling died 1936 and is public domain in life+70 jurisdictions; translator dates vary, so verify before shipping outside the US.

### Known gaps

The Andersen collection lacks _The Little Mermaid_, _The Ugly Duckling_, and _Thumbelina_. Gutenberg #27200 has them but its heading structure mixes stories and sub-chapters at the same level; adding it needs a custom parser pass. Beatrix Potter is also absent (one book per ebook). Both are good v2 data tasks.

---

## Session 1 — Scaffold and data layer

**Context.** New repo for "Storybook," a static React PWA for reading public-domain children's stories. A prebuilt dataset lives in `compendium/` at the repo root (schema in `SPEC.md` § "The compendium", which sits at the repo root). This session creates the project, wires the data, and proves the data is sound. No UI beyond a placeholder.

**Tasks.**

1. Scaffold Vite + React + TS (strict). Add Vitest, @testing-library/react, jsdom, Playwright, ESLint, Prettier. Scripts: `dev`, `build`, `preview`, `test`, `test:e2e`, `lint`, `typecheck`.
2. Move `compendium/` to `public/compendium/`. Keep `tools/build_compendium.py` at `tools/`.
3. `src/data/types.ts`: the `Index`, `IndexEntry`, `Story`, `Block` types. `src/data/schema.ts`: zod schemas mirroring them.
4. `src/data/client.ts`: `loadIndex()` (cached after first call) and `loadStory(id)` (memoized by id). Both validate with zod and throw a typed `DataError` on failure.
5. Tests first: (a) a data-integrity test that runs in Node over `public/compendium/` — every index entry validates, has a matching story file whose fields agree, every image `src` exists on disk, ids are unique, `storyCount` matches; (b) client tests with mocked `fetch` covering caching, memoization, and validation failure.
6. Write `CLAUDE.md` (stack, commands, directory map, data contract summary, testing conventions, "docs must match code" rule), `README.md`, `CHANGELOG.md` (Keep a Changelog format, `Unreleased` section).

**Done when.** All scripts run clean; integrity test passes over all 319 stories; docs describe what exists.

**Verify.**

```
npm run typecheck && npm run lint && npm test
npm run build
```

## Session 2 — Library and navigation

**Context.** Storybook is a Vite/React/TS PWA. `src/data/client.ts` exposes `loadIndex()` and `loadStory(id)`; types in `src/data/types.ts`. Each index entry has `collectionId`, `title`, `readingMinutes`, `excluded`, and `flags` (`"mature-themes"` hides a story by default). Read `CLAUDE.md` first. This session builds browsing.

**Tasks.**

1. Routes: `/` (library), `/c/:collectionId`, `/s/:storyId` (reader placeholder), `/settings`, `/about`.
2. `src/domain/visibility.ts`: pure `isVisible(entry, settings)` — `excluded` stories hidden unless `settings.showExcluded`; `mature-themes` hidden unless `settings.showMature`. Unit-test every combination first.
3. Settings context backed by a minimal `localStorage` wrapper (`showMature: false`, `showExcluded: false` defaults). Session 4 will generalize storage; keep this wrapper small and isolated.
4. Library page: collection cards (title, credit, visible-story count), a title search across all visible stories, and a length filter (Short ≤5 min, Medium 6–15, Long >15).
5. Collection page: stories in `order`, each row showing title and minutes.
6. About page: per-collection credits and source links from `index.json`.
7. Component tests for search, length filter, and that hidden stories never render.

**Done when.** A user can find any visible story in two taps or one search; hidden stories are unreachable from the UI; docs and changelog updated.

**Verify.**

```
npm run typecheck && npm run lint && npm test
```

## Session 3 — Reader

**Context.** Storybook is a Vite/React/TS PWA. Route `/s/:storyId` currently renders a placeholder. `loadStory(id)` returns a `Story` with `blocks` of type `p | verse | moral | heading | note | image` (image `src` is relative to `/compendium/`). Read `CLAUDE.md` first. This session builds the reading experience.

**Tasks.**

1. `BlockRenderer` with one component per block type. `verse` uses `white-space: pre-wrap` in a lighter italic; `moral` is a distinct card at the end of the fable; `note` is a small, muted aside; `image` is a `<figure>` with `loading="lazy"` and `alt`. Tests first for each type.
2. Story header: title, collection credit, `origin` if present, reading minutes.
3. Reader settings (persisted with the existing settings wrapper): font size (5 steps), theme (light / sepia / dark, default sepia), line height (normal / relaxed). Serif body type, max measure ~65ch, generous margins. Respect `prefers-reduced-motion` and `prefers-color-scheme` for the initial theme.
4. Footer navigation: previous/next story within the collection, skipping hidden stories.
5. Reading progress: a thin top progress bar based on scroll.
6. Accessibility: semantic `article`, heading order, focusable controls, 4.5:1 contrast in all themes. Add an axe check via `@axe-core/playwright` in an e2e test that opens one Aesop fable (has image + moral) and one Kipling story (has verse).

**Done when.** Every block type renders correctly; settings persist across reloads; axe reports no serious violations; docs updated.

**Verify.**

```
npm run typecheck && npm run lint && npm test
npm run build && npm run test:e2e
```

## Session 4 — Favorites, resume, history

**Context.** Storybook is a Vite/React/TS PWA with a library and reader. A small settings wrapper over `localStorage` exists. Read `CLAUDE.md` first. This session adds per-device persistence for user state and replaces the settings wrapper with one storage module.

**Tasks.**

1. `src/storage/store.ts`: one versioned `localStorage` key (`storybook:v1`) holding `{ settings, favorites: Record<id, savedAt>, progress: Record<id, { blockIndex, updatedAt }>, history: { id, readAt }[] }`. Includes a `migrate()` function (v1 is identity, but the seam and its test exist), tolerates corrupt JSON by resetting with a console warning, and ignores ids not in the current index. Tests first, including corrupt-data and unknown-id cases.
2. Migrate the existing settings onto the store without changing behavior; existing tests must still pass.
3. Favorites: heart toggle in the reader header and on story rows; `/favorites` page sorted by most recent.
4. Resume: track the topmost visible block with an `IntersectionObserver` (throttled writes); on reopening a story, offer "Continue from where you left off" rather than auto-jumping. Clear progress when the final block is reached.
5. History: record a story as read when its final block is seen; cap at 200 entries. Library gets a "Continue reading" row (in-progress stories, newest first).
6. Settings gets "Clear reading data" with a confirm step.

**Done when.** Favorites, resume, and history survive reload; corrupt storage cannot crash the app; docs and changelog updated.

**Verify.**

```
npm run typecheck && npm run lint && npm test
npm run test:e2e
```

## Session 5 — Random picker

**Context.** Storybook is a Vite/React/TS PWA. `src/storage/store.ts` holds settings, favorites, progress, and read history; `src/domain/visibility.ts` exports `isVisible(entry, settings)`. Index entries have `collectionId` and `readingMinutes`. Read `CLAUDE.md` first. This session builds "Surprise me."

**Tasks.**

1. `src/domain/picker.ts`: pure `pick(entries, opts, rng)` where `opts = { collections?: string[]; maxMinutes?: number; unreadOnly?: boolean; favoritesOnly?: boolean; recent: string[] }`. Always applies `isVisible`. Avoids the last 10 picks unless that empties the pool, then relaxes that rule only. Returns `null` with a reason (`"no-matches"`) when nothing qualifies. `rng` is injected (`() => number`); tests use a seeded PRNG (mulberry32). Tests first: filter combinations, repeat avoidance, relaxation, empty pool, and a distribution test that 10k picks over a small pool stay within tolerance of uniform.
2. `/surprise` page and a prominent library button. Filter chips for collection and length ("Under 5 min" defaults on — bedtime is the main use case), toggles for unread-only and favorites-only. Filter choices persist in settings.
3. The result shows as a card (title, collection, minutes, first ~25 words) with "Read it" and "Pick again." A brief shuffle animation, skipped under `prefers-reduced-motion`.
4. Recent picks stored in the store (cap 10).

**Done when.** Picker never returns a hidden story, honors every filter, explains empty results; docs and changelog updated.

**Verify.**

```
npm run typecheck && npm run lint && npm test
npm run test:e2e
```

## Session 6 — Offline, polish, release

**Context.** Storybook is a feature-complete Vite/React/TS app: library, reader, favorites/resume/history, random picker. Data lives in `public/compendium/` (index 80 KB, stories 3.1 MB, images 8.8 MB). Read `CLAUDE.md` first. This session makes it installable and offline-capable and closes gaps.

**Tasks.**

1. `vite-plugin-pwa`: manifest (name, icons, `display: standalone`, theme colors per reader theme). Precache the app shell and `index.json`; runtime-cache story JSON (stale-while-revalidate) and images (cache-first, capped). Add a "Make all stories available offline" button in settings that fetches every story file and reports progress.
2. Offline UX: banner when offline; stories not cached show a clear message instead of an error.
3. e2e: offline test (load, go offline, open a cached story), plus a full happy-path test: search → read → favorite → reload → resume → surprise.
4. Performance: Lighthouse CI or a scripted check; target ≥90 performance and accessibility on the library and an Aesop story.
5. Audit `CLAUDE.md`, `README.md`, `CHANGELOG.md` against the code; fix any drift and tag `0.1.0` in the changelog.

**Done when.** Installable PWA works offline for cached content; all test suites green; docs accurate.

**Verify.**

```
npm run typecheck && npm run lint && npm test
npm run build && npm run test:e2e
npx lighthouse http://localhost:4173 --only-categories=performance,accessibility --quiet
```

## Regenerating the compendium

`tools/build_compendium.py` needs Python 3 with `beautifulsoup4` and `lxml`. Clone the GITenberg mirrors into `src/` next to it, then run it; output lands in `out/compendium/`.

```
mkdir -p src && cd src
for r in The-Aesop-for-Children--13-With-pictures-by-Milo-Winter_19994 Grimms-Fairy-Tales_2591 \
  Andersen-s-Fairy-Tales_1597 The-Blue-Fairy-Book_503 English-Fairy-Tales_7439 Just-So-Stories_2781; do
  git clone --depth 1 https://github.com/GITenberg/$r.git; done
cd .. && python3 tools/build_compendium.py
```

Title overrides, content flags, and the mature-themes list are constants at the top of the script.
