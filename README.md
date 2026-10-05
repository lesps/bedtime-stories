# Storybook

A calm, offline-capable reader for 319 public-domain children's stories — Aesop (with Milo Winter's
illustrations), Grimm, Andersen, Lang's Blue Fairy Book, Jacobs' English Fairy Tales and Kipling's
Just So Stories.

**Live:** https://lesps.github.io/bedtime-stories/

- Browse collections, search titles, filter by length.
- Serif reader with light / sepia / dark themes (Auto follows your phone), 5 text sizes, relaxed
  spacing, scroll progress, previous/next.
- Favorites, "continue from where you left off", read history — stored only on your device.
  Swipe a story left to mark it unread (or read).
- **Surprise me**: random pick filtered by collection, length (Under 5 min by default), unread or
  favorites, avoiding the last 10 picks.
- Installable PWA that works offline; one tap in Settings saves every story (~12 MB).
- Child-safe defaults: stories flagged for mature themes or offensive language are hidden until a
  grown-up turns them on in Settings.

## Install on a phone

Open the live URL, then **Share → Add to Home Screen** (iOS Safari) or **⋮ → Install app**
(Android Chrome). Stories you open are kept for offline use; use **Settings → Make all stories
available offline** to save the lot.

## Development

Requires Node 22.

```sh
npm ci
npm run dev            # http://localhost:5173/bedtime-stories/
npm test               # unit + component + data integrity
npm run build && npm run test:e2e && npm run perf
```

See `CLAUDE.md` for architecture, commands and conventions, and `SPEC.md` for the original spec
and data schema.

## Deployment

`.github/workflows/deploy.yml` runs typecheck, lint, unit, e2e and Lighthouse on every push and PR,
and deploys `dist/` to GitHub Pages on pushes to `main`. One-time setup: **Settings → Pages →
Build and deployment → Source: GitHub Actions**.

## Data and licensing

Texts and illustrations are public domain in the USA. Project Gutenberg boilerplate has been
stripped; sources are linked on the About page. Check translator dates before distributing outside
the US. To regenerate the data, see "Regenerating the compendium" in `SPEC.md`.
