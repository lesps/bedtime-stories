# Storybook

A calm, offline-capable reader for 908 public-domain children's stories in 49 collections — Aesop
(with Milo Winter's illustrations), Grimm (Taylor's selection and Hunt's complete translation),
Andersen, Beatrix Potter's 21 illustrated tales, Lang's Blue Fairy Book, Jacobs' English Fairy
Tales, Kipling's Just So Stories, two collections of Japanese fairy tales (Ozaki; James with Warwick
Goble's plates), Busch's Max and Maurice, and a growing world-mythology shelf. Greek and Roman:
Hesiod and the Homeric Hymns (Evelyn-White's translation), Hawthorne's Tanglewood Tales,
Kingsley's The Heroes, 40 sections of Bulfinch's The Age of Fable, Church's Stories from Virgil and
Stories from Livy, and Macaulay's "Horatius". Norse: Thorpe's Elder Edda, Blackwell's Prose Edda
and Lang's "Story of Sigurd". German and Swiss: Baldwin's The Story of Siegfried, Browning's "The
Pied Piper of Hamelin" with Kate Greenaway's pictures, and William Tell and Arnold Winkelried from
Baldwin's Fifty Famous Stories Retold. English: Brutus and King Leir from Bulfinch's The Age of
Chivalry, Corineus and the giant from Quiller-Couch's Cornwall's Wonderland, Beowulf from
Marshall's English Literature for Boys and Girls, seven chapters of Pyle's The Merry Adventures of
Robin Hood, and Thorpe's Lay of Völund (Wayland). Irish: six romances from Joyce's Old Celtic
Romances (Lir, Turenn, Maildun, Dermat and Grania, Oisin, the Sons of Usna), Tuan mac Cairill and
the boyhood of Fionn from Stephens's Irish Fairy Tales, two chapters of Hull's Cuchulain, the Hound
of Ulster, and Carleton's "A Legend of Knockmany". Welsh: seven tales from Lady Charlotte Guest's
Mabinogion (the Four Branches, Lludd and Llefelys, Taliesin, Culhwch and Olwen), and the Shepherd
of Myddvai and Beth Gellert from Jacobs's Celtic Fairy Tales. Scottish and Manx: Thomas the Rhymer,
the Seal Catcher and Assipattle from Grierson's The Scottish Fairy Book, and the making of Mann and
Manannan's mist from Morrison's Manx Fairy Tales. Where no free English version exists, Claude's
own translations from Homer, Pindar, Apollodorus, Pausanias, Cicero, Ovid, Snorri, the Golden
Legend's Saint George, and the Lorelei and Wild Huntsman ballads of Brentano, Heine and Bürger.
Simplified retellings for young readers in Greek, Roman, Norse, German, English, Irish, Welsh and
Scottish, Manx and Breton collections "Simply Told".

**Live:** https://lesps.github.io/bedtime-stories/

- Browse by collection, culture (Japanese, Norwegian, French…) or theme (animals, tricksters,
  gentle & cosy…); search titles and tags; filter by length with a two-handled slider (in the
  library and on every collection and tag page).
- Serif reader with light / sepia / dark themes (Auto follows your phone), 5 text sizes, relaxed
  spacing, scroll progress, previous/next. Its toolbar slides away as you read and comes back
  when you scroll up.
- Highlight passages in four colours, add notes to a passage or a whole story, and export your
  notebook as Markdown.
- A **Reading** tab that takes you straight back into the story you have open, or shows your
  shelf of stories in progress (with percent read) and recently finished ones. Stories always
  open where you left off (Start over on the shelf begins again); finished ones start from the
  top, and rereads keep their own place.
- Tabs behave like a phone app's: tap the current tab to go back to its main screen, scroll to
  the top, or (in a story) close the book.
- Favorites, reading positions and read history — stored only on your device.
  Swipe a story left to mark it unread (or read).
- **Surprise me**: one story or "Give me 3", filtered by length range, collection, culture and
  theme (include or leave out — "no monsters tonight"), unread or favorites, with one-tap presets
  (Quick & gentle, Something new, Old favorite). Avoids your last 10 picks and other translations
  of them.
- Works on phones, tablets and desktops: a bottom tab bar on small screens, a sidebar with wider,
  multi-column pages on desktop; keyboard-friendly dialogs (Escape closes), hover actions with a
  mouse, and Back returns to where you were in a list.
- Installable PWA that works offline; one tap in Settings saves every story (~40 MB with
  illustrations, ~9 MB text only).
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

The simplified retellings (the seven "Simply Told" collections, `myths-*`) were written by Claude
(Anthropic) from public-domain originals; their editable source is `tools/simplified/*.md`, rebuilt
into story JSON by `tools/build_simplified.py`. Each one links to its original, except the few
legends with no public-domain text available, whose end note says what they were retold from.
Likewise, the Greek, Latin, Norse and German "sources" collections are Claude's translations of
old passages, edited in `tools/translations/*.md` and built by `tools/build_translations.py`.
