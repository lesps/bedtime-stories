# Changelog

All notable changes to this project are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning: [SemVer](https://semver.org/).

## [Unreleased]

### Added

- Swipe a story row left to mark it unread (or read). The action is also reachable by keyboard
  and screen reader without swiping.

## [0.1.0] - 2026-10-05

### Added

- Project scaffold: Vite + React 18 + strict TypeScript, Vitest, Testing Library, Playwright, axe,
  ESLint, Prettier, Lighthouse script.
- Compendium of 319 stories in `public/compendium/`, zod-validated data client with caching, and a
  data-integrity test over every story and image.
- Library with collection cards, title search and length filter; collection pages; About page with
  credits and source links.
- Reader with per-block rendering (paragraph, verse, moral, heading, note, image), story header,
  previous/next within the collection, scroll progress bar, and reader settings (theme, 5 font
  sizes, line height).
- Themes: Auto (follows OS light/dark), light, sepia, dark — applied app-wide, no flash on load.
- Favorites, resume position with a "Continue from where you left off" prompt, read history
  (capped at 200), "Continue reading" row, and "Clear reading data" with confirmation.
- Single versioned `localStorage` store (`storybook:v1`) with migration seam, corrupt-data
  recovery and pruning of unknown story ids.
- Surprise me: filtered random picker (collections, length, unread, favorites) that avoids the
  last 10 picks, persisted filters, story excerpt, shuffle animation honouring reduced motion.
- Child-safety defaults: excluded and mature-themed stories hidden everywhere unless enabled.
- Installable PWA: manifest and icons, precached app shell and index, runtime-cached stories and
  illustrations, offline banner, clear message for stories not yet saved, and a "Make all stories
  available offline" download with progress.
- GitHub Pages deployment workflow gated on typecheck, lint, unit, e2e and Lighthouse (≥90).
