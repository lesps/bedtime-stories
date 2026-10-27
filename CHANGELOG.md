# Changelog

All notable changes to this project are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning: [SemVer](https://semver.org/).

## [Unreleased]

### Added

- Mythology, part 8 (data only): the Irish shelf. From P. W. Joyce's _Old Celtic Romances_ (1879),
  a new `joyce-celtic-romances` collection: the Children of Lir, the Children of Turenn, the Voyage
  of Maildun, the Pursuit of Dermat and Grania, Oisin in Tirnanoge and the Sons of Usna (Turenn,
  Dermat and Grania and Usna are `mature-themes`). From James Stephens's _Irish Fairy Tales_
  (1920): Tuan mac Cairill and the Boyhood of Fionn (with the Salmon of Knowledge). From Eleanor
  Hull's _Cuchulain, the Hound of Ulster_ (1909): how Cuchulain got his name, and the Cattle Raid
  of Cooley in four chapters with bridging notes (`mature-themes`). William Carleton's "A Legend of
  Knockmany" from Yeats's _Fairy and Folk Tales of the Irish Peasantry_ (1888), labelled as a later
  folk legend. All eleven read at advanced level, so eighteen retellings make up the new _Irish
  Legends, Simply Told_ (grade 3.0–4.8): one for each original, plus seven with no public-domain
  text available here, retold without an original like Rübezahl: Lugh of all the skills (the four
  treasures, Nuada's silver hand, Lugh at the door of Tara, Balor), the Dagda's harp, Boann and
  the Boyne, Midir and Etain, the Voyage of Bran, Cuchulain and the beheading game, and Saint
  Brendan's voyage. New tool `extract_irish.py`.
- Mythology, part 7 (data only): the English and Anglo-Saxon shelf. From Bulfinch's _The Age of
  Chivalry_ (1858), a new `bulfinch-chivalry` collection: Brutus and the founding of Britain, and
  King Leir. Mabel Quiller-Couch's "How Corineus Fought the Chief of the Giants" from _Cornwall's
  Wonderland_ (1914; `mature-themes` for its bloody end). "The Story of Beowulf" from H. E.
  Marshall's _English Literature for Boys and Girls_ (1909; middle level, no retelling). Seven
  chapters of Howard Pyle's _The Merry Adventures of Robin Hood_ (1883): the outlaw and Little
  John, the golden arrow, Allan a Dale, Friar Tuck, Allan's wedding, King Richard and the Epilogue
  (`mature-themes`), with Pyle's songs as verse. Thorpe's Lay of Völund joins `thorpe-elder-edda`
  (`mature-themes`) as the source for Wayland. Claude's own translation of the Golden Legend's
  Saint George from the Latin joins `latin-sources`. Fourteen retellings in the new _English
  Legends, Simply Told_ (grade 2.8–5.4), including the Green Children of Woolpit, which, like
  Rübezahl, has no public-domain text available here and is retold without an original.
  `extract_bulfinch.py` reads the Age of Chivalry too and folds one-line footnote references into
  their note; new tool `extract_english.py`.
- Mythology, part 6 (data only): the German and Swiss shelf. James Baldwin's _The Story of
  Siegfried_ (1882): nine of its twenty Adventures (the forging of Balmung, Greyfell, the curse of
  Andvari's gold, Fafnir, Brunhild, the Nibelung hoard, the wooing of Brunhild for Gunther,
  Siegfried's death, and the hoard sunk in the Rhine with Baldwin's After Word), with note blocks
  bridging the chapters left out; the death is `mature-themes`. Robert Browning's "The Pied Piper
  of Hamelin" with Kate Greenaway's 1888 pictures (35 images). "The Story of William Tell" and
  "Arnold Winkelried" from Baldwin's _Fifty Famous Stories Retold_ (1896), with the Tell picture;
  both read at early/middle level and get no retelling. Claude's own verse translations, from the
  TextGrid texts in the German Poetry Corpus, of Brentano's Lore Lay ballad and Heine's "Lorelei"
  (labelled as a literary legend) and of Bürger's "The Wild Huntsman"; both are `mature-themes`.
  Thirteen retellings in the new _German Legends, Simply Told_ (grade 2.3–4.9), including the two
  ballads (retold because their originals are hidden by default) and Rübezahl, which has no
  public-domain text available here, so it is retold from the legend as Musäus told it and has
  no original (`adaptation: "retold"`, no `adaptedFrom`). Baldwin's Fafnir chapter and its
  retelling share `norse-sigurd-fafnir` with Lang's Sigurd. New culture `swiss` (16 in all). New
  tools `extract_baldwin.py` and `extract_browning.py`; `build_translations.py` gains
  `german-sources` and verse blocks; `build_simplified.py` gains `myths-german` and unsourced
  retellings (`basedOn` front matter).
- Mythology, part 5 (data only): the Norse shelf. Benjamin Thorpe's _Elder Edda_ (1866): the
  Völuspá, Odin's Rune-Song, and the lays of Hymir, Thrym, Alvis, Skirnir, Baldr's dreams and
  Fafnir. I. A. Blackwell's _Prose Edda_ (1847): fourteen stories from creation and Yggdrasil to
  Baldur's death and Ragnarok, with Idun and Skadi cut from one section (Skadi's story goes on in
  "Of Njord"). Lang's "The Story of Sigurd" from _The Red Fairy Book_ (1890). Claude's own
  translations from Snorri's Old Norse, where no free English version exists: Sif's golden hair
  and the dwarves' treasures, Thor and Hrungnir, and the passages about Freyja's necklace.
  Twenty-four retellings in the new _Norse Myths, Simply Told_ (grade 1.8–4.8), covering every
  Norse entry in the expansion plan; Odin's eye is part of the Yggdrasil story. Thorpe's poems
  read at middle level by the formula, but the verse is archaic, so six get their own retellings:
  the runes, Thrym and Alvis, plus Hymir's cauldron, Odin's ride to the dead seeress (Baldr's
  dreams) and the whole Völuspá, which tell more than the Prose Edda versions and so have their
  own `workId`s. Skirnir and Fafnir are linked to the Frey and Sigurd retellings with
  `alsoSimplifies`; the Frey retelling leaves out Skirnir's threats on purpose. Four originals are `mature-themes` (Skirnir's
  threats, Loki's punishment, the mead of poetry, and Sigurd's death in Lang); no retelling is.
  New culture `norse` (15 in all). New tool `extract_eddas.py`; `build_translations.py` gains
  `norse-sources`.
- Mythology, part 4b (data only): the three Greco-Roman myths with no public-domain English
  source, in Claude's own translations from the Greek and Latin texts of the Perseus Digital
  Library. _Myths from the Greek Writers_: Hephaestus and the golden throne (Pausanias 1.20.3;
  Iliad 18.394–407 and 1.571–600) and Sisyphus and Tantalus (Iliad 6, Apollodorus, Pausanias
  2.5.1, Pindar's first Olympian, Odyssey 11.582–600). _Myths from the Latin Writers_: Tages, the
  Etruscan child prophet ploughed up from a field (Cicero, _On Divination_ 2.50–51; Ovid,
  _Metamorphoses_ 15.547–559). Each passage is headed with its reference, and an end note names
  the editions. Three new retellings (grade 4.2–5.0). Tages reads at middle level but is two
  excerpts rather than a story, so it gets a retelling too. New culture `etruscan` (14 in all).
  New tool `build_translations.py`, source files in `tools/translations/`.
- Mythology, part 4 (data only): the rest of the Greco-Roman shelf. Hesiod's _Theogony_ and the
  Homeric Hymns to Demeter, Apollo, Hermes and Dionysus (Evelyn-White's 1914 translation);
  Church's _Stories from Virgil_ (1879), the whole _Aeneid_ in nine stories; three stories from
  Church's _Stories from Livy_ (1883) cut into four (Romulus, Numa, Lars Porsenna, the Gauls);
  Macaulay's "Horatius" (1842); and four Roman sections of Bulfinch (the Roman gods, Vertumnus
  and Pomona, Cupid and Psyche, the Sibyl). Twenty new retellings (grade 2.7–5.5): four in
  _Greek Myths, Simply Told_ (Zeus and the Titans, Apollo, Hermes, Dionysus) and sixteen in the
  new _Roman Myths, Simply Told_. The Hymn to Demeter links to the Persephone retelling and
  Macaulay's poem to the Horatius one. New culture `roman` (13 in all), set per story for
  Bulfinch's Roman sections. Ten originals are `mature-themes`, none of the retellings; Nisus and Euryalus already
  reads at middle level and keeps its original only. New tools `extract_hesiod.py`,
  `extract_church.py` and `extract_macaulay.py`.
- Mythology, part 3 (data only): heroes, Troy and the Odyssey. Kingsley's _The Heroes_ (1856):
  Perseus, The Argonauts, Theseus. Fifteen more Bulfinch sections: Perseus, the Sphinx,
  Bellerophon, Meleager, Atalanta, Hercules, Castor and Pollux, the Trojan War, the fall of Troy
  and five Odyssey sections. Twelve new simplified retellings (grade 2.7–5.0). Lang's _The
  Terrible Head_ now shares `greek-perseus` with the other Perseus versions. A retelling can
  stand in for several versions of one myth via `alsoSimplifies`; Kingsley's Theseus and
  Argonauts point to the existing Hawthorne-based retellings. New tool `extract_kingsley.py`;
  Bulfinch sections can now span several headings, and a footnote that ends on a poem no
  longer swallows the paragraphs after it.
- Mythology, part 2 (data only): 21 myths from Bulfinch's _The Age of Fable_ (1855): creation,
  Prometheus and Pandora, Phaeton, Midas, Arachne, Orpheus and others, with footnotes as `note`
  blocks. Twenty get simplified retellings in _Greek Myths, Simply Told_ (grade 2–4, 1–5 min);
  Arion already reads at middle level and keeps its original only. Six originals and four
  retellings are `mature-themes`; retellings can override their original's flags in front
  matter. New tool `extract_bulfinch.py`.
- Mythology, part 1 (data only): Hawthorne's _Tanglewood Tales_ (6 Greek myths) and _Greek
  Myths, Simply Told_, a simplified retelling of each for young readers (grade 2–3, 6–10 min
  against 40–73 min). Each pair shares a `workId`, so the reader links them under Other
  versions. New `Gods & heroes` theme. New data fields `readingLevel`, `simplifiedId` and
  `adaptedFrom`, not yet used by the app (see CLAUDE.md). New tools: `extract_hawthorne.py`,
  `build_simplified.py`, `readability.py`, `compendium_io.py`.

- Desktop layout: from 1024px the tab bar becomes a sidebar, pages widen with two-column story
  lists, three-column collection cards and side-by-side Settings cards; the highlight sheet is a
  centred dialog and the Notes panel docks on the right. Phones and tablets are unchanged.
- Mouse support for story rows: "Mark read/unread" appears on hover (mouse drags no longer swipe).
- Hover and pressed feedback on buttons, chips, cards and rows.
- Back and Forward return to where you were in a list instead of the top.
- Length slider and story count on collection and tag pages.

- Tab bar re-taps: tapping the current tab returns to its main screen, then scrolls to the top,
  then (Library) clears search and filters; in a story, tapping Reading closes the book. The
  current tab now follows the section you're in (collection and tag pages light up Library).
- Story rows show reading progress ("40% through") separately from the read mark.

- Highlights and notes: select text to highlight it (four colours) or add a note; tap a
  highlight to recolour, annotate or delete it; a Notes panel per story with a story note and a
  list of highlights; a Notebook on the Reading shelf with Markdown export. Clearing reading data
  keeps notes unless you ask otherwise.
- Reading tab in the middle of the tab bar: returns straight to the open story at its place, or
  shows a shelf of stories in progress (percent read, minutes left) and recently finished. The
  reader gains a Close book button.
- Fuller Surprise me: "Give me 3", culture and theme filters that include or exclude, presets
  (Quick & gentle, Something new, Old favorite), a recently-picked list, a card-flip reveal, and a
  note when fewer stories match than were asked for.
- Culture and theme tags for every story (12 cultures, 17 themes, including "Gentle & cosy" for
  bedtime), with "Browse by" in the library, tag pages, tag chips in the reader, and search by
  tag name. Generated by `tools/tag_stories.py`; an editorial first pass.
- Compendium patches 001–003, taking the library from 319 stories / 6 collections to 614 / 12:
  Andersen's _Little Mermaid_, _Thumbelina_ and _Ugly Duckling_ (Gutenberg #27200); 21 Beatrix
  Potter books with 536 illustrations; Margaret Hunt's complete _Household Tales_ (210); Ozaki's
  and Grace James's _Japanese Fairy Tales_; Busch's _Max and Maurice_.
- "Other versions" in the reader for tales that exist in more than one translation (`workId`).
- Potter stories show their own publication year and source link.
- Text-only option for the offline download, with sizes kept honest by the integrity test.
- Swipe a story row left to mark it unread (or read). The action is also reachable by keyboard
  and screen reader without swiping.

### Changed

- The text-only offline download is now advertised as about 9 MB (40 MB with illustrations), to
  match the larger compendium.
- Bulfinch footnotes inside a paragraph now follow it as `note` blocks instead of sitting
  mid-sentence in brackets, and cross-references to the book's appendix are dropped.

- Dialogs move focus inside, close on Escape from anywhere and hand focus back; the reading
  settings panel closes on Escape or a click outside.
- Illustrations are capped at 70% of the screen height.
- Recently picked shows story rows and leaves out the stories currently on screen.
- Settings says "Auto" follows your device, not your phone.

- The reader's toolbar (text settings, notes, favorite, close) stays reachable: it slides away
  while you read down and comes back on any scroll up.
- Collection and tag pages have a back link; collections with no visible stories are no longer
  listed (in the library or Surprise me), and counts say "1 story".
- Surprise me's "More filters" shows a chevron, so it reads as something to open.
- Stories open straight at the saved place instead of asking; Start over lives on the Reading
  shelf, per story. Finished stories start from the top.
- Finishing a story keeps its position as finished instead of deleting it, so read status and
  progress are independent: rereads resume and appear in Continue reading.
- Hidden swipe-action buttons no longer show a faint edge beside story rows.
- Collections that share a title are labelled with their translator's surname, e.g. "Japanese
  Fairy Tales (Ozaki)".
- Length filters are now a two-handled slider (1 min to 60+) in the library and Surprise me, so
  the picker can choose only medium or only long stories. Saved "under N min" choices carry
  over.
- Curly quotes and em dashes for sources that use ASCII punctuation, applied when data loads.
- Surprise me no longer offers another translation of a tale it picked recently.
- Offline caches hold up to 1000 stories and 1000 images (was 400 / 150).
- Image-size tool reads WebP as well as JPEG.

### Fixed

- Retellings of stories from an anthology credit the book and its editor instead of "Various's"
  (Lang's "Story of Sigurd").
- Escape didn't close the highlight sheet unless focus was inside it, so it could stay open behind
  the Notes panel.
- Keyboard focus rings on story rows were clipped.

- The reader's Aa settings panel ran off the left edge of phone screens.
- Layout shift on illustrated stories: images now reserve their space (dimensions generated by
  `npm run image-sizes`), the opening illustration loads eagerly, and prev/next waits for the
  story text. Lighthouse performance on Aesop fables went from an intermittent 78 to a steady 98.

### Changed

- `npm run perf` takes the median of three Lighthouse runs per page.

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
