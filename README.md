# Storybook

A calm, offline-capable reader for 614 public-domain children's stories in 12 collections — Aesop
(with Milo Winter's illustrations), Grimm (Taylor's selection and Hunt's complete translation),
Andersen, Beatrix Potter's 21 illustrated tales, Lang's Blue Fairy Book, Jacobs' English Fairy
Tales, Kipling's Just So Stories, two collections of Japanese fairy tales (Ozaki; James with Warwick
Goble's plates) and Busch's Max and Maurice.

**Live:** https://lesps.github.io/bedtime-stories/

- Browse by collection, culture (Japanese, Norwegian, French…) or theme (animals, tricksters,
  gentle & cosy…); search titles and tags; filter by length with a two-handled slider.
- Serif reader with light / sepia / dark themes (Auto follows your phone), 5 text sizes, relaxed
  spacing, scroll progress, previous/next.
- Favorites, "continue from where you left off", read history — stored only on your device.
  Swipe a story left to mark it unread (or read).
- **Surprise me**: one story or "Give me 3", filtered by length range, collection, culture and
  theme (include or leave out — "no monsters tonight"), unread or favorites, with one-tap presets
  (Quick & gentle, Something new, Old favorite). Avoids your last 10 picks and other translations
  of them.
- Installable PWA that works offline; one tap in Settings saves every story (~36 MB with
  illustrations, ~5 MB text only).
- Tales told in more than one translation link to each other ("Other versions").
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
stripped; sources are linked on the About page (and per book for Potter). Frederick Warne holds
trademarks on Peter Rabbit and other Potter characters, so don't use them in the app's name, icon
or marketing. Check translator dates before distributing outside
the US. To regenerate the data, see "Regenerating the compendium" in `SPEC.md`.
