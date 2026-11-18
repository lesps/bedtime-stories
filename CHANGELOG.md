# Changelog

All notable changes to this project are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning: [SemVer](https://semver.org/).

## [Unreleased]

### Changed

- A collection's `originalLanguage` may now be a three-letter ISO 639-2/3 code where the language
  has no two-letter one (`egy`, Ancient Egyptian); the schema accepted only two letters.

- The Scottish Fairy Book stories no longer carry Morris Meredith Williams's five pictures: he died
  in 1973, so they aren't public domain everywhere, and the mythology shelves only use sources
  that are.

- `build_simplified.py` reads quoted front-matter values: Prettier quotes a value with ": " in it,
  such as a retelling title with a colon, and the quotes ended up in the title.

- The offline download is now advertised as about 12 MB of text (47 MB with illustrations), up
  from 9 and 40, to keep up with the mythology shelves.

- The end note of a retelling with no original now says "There is no public-domain text of this
  legend in the app to compare it with", instead of saying no text could be used: some of these
  legends have public-domain versions that this project couldn't reach.

### Fixed

- Dutt's Ramayana kept the digitization's italic underscores ("_Yugas_") in Vamana's three steps;
  `extract_hindu.py` now drops them.
- CI runs on `ubuntu-24.04` instead of `ubuntu-latest`: GitHub moved `ubuntu-latest` to Ubuntu 26.04,
  where the project's Playwright (1.56) can't install Chromium, so every run (and the deploy) failed.

- A retelling's end note said its original was "listed under Other versions" even when the
  original is hidden by default. For retellings of `mature-themes` originals, the note now
  says the original appears there only when "Show stories with mature themes" is on; the integrity
  test checks every retelling's note.

### Added

- Mythology, part 29: Tamil myths, a new `myths-tamil` collection and `tamil` culture, both retold
  by Claude with no public-domain text to work from (‡). Murugan and the fruit of wisdom, the
  Palani temple legend, shares a `workId` with Ganesha and Kartikeya's race, so each lists the
  other under Other versions; it is marked as sacred to Hindus. Kannagi and the anklet, from Ilango
  Adigal's Silappatikaram, is `mature-themes` (Kovalan's execution and the burning of Madurai).
- Mythology, part 28: Hindu myths, third part. The Ramayana in six parts: the bow and the exile,
  Sita stolen, Hanuman finding Sita, the bridge to Lanka, the battle and Rama's homecoming. Parts
  1–3, 5 and 6 are Romesh C. Dutt's verse condensation (1899, new collection `rc-dutt-ramayana`,
  `tools/extract_ramayana_verse.py`), from sacred-texts.com's edition with its slips corrected; part
  4 is Manmatha Nath Dutt's prose (Yuddha Kanda XXI–XXII, 1893), as Romesh Dutt leaves the bridge out.
  Parts 1, 2, 5 and 6 are `mature-themes` (Kaikeyi's and Bharat's threats to die, Surpa-nakha maimed,
  the battlefield, Sita asking for her pyre). From Ganguli's Mahabharata: Arjuna sees only the bird,
  Ekalavya (`mature-themes`: he cuts off his thumb), Nala and Damayanti up to their wedding
  (`mature-themes`: she names ways she would kill herself), Bhima meets Hanuman, Savitri and
  Satyavan, and Yudhishthira and the yaksha. `myths-hindu` retells all twelve; all are marked as
  sacred to Hindus.
- Mythology, part 27: Hindu myths, second part. From Ganguli's Mahabharata: Ganesha writes down the
  Mahabharata at Vyasa's dictation. From Dutt's Vishnu Purana: the birth of Krishna
  (`mature-themes`: Kansa kills Devaki's babies), Krishna and the serpent Kaliya, and Krishna lifting
  Mount Govardhana. From Dutt's Ramayana: Hanuman leaping for the sun, from the Uttara Kanda (1894)
  with its ending from the Kishkindha Kanda (1891), since Dutt's Uttara Kanda leaves out the boons.
  From Baba Premanand Bharati's Sree Krishna, the Lord of Love (1904, `bharati-krishna`): Krishna the
  butter thief, with the universe in his mouth and the uprooted trees. `myths-hindu` retells all
  six, and adds three with no original in the app (‡): how Ganesha got his elephant head and his
  race around the world with Kartikeya (Shiva Purana), and Durga and the buffalo demon (Devi
  Mahatmya). All are marked as sacred to Hindus. A Ramayana story from a later volume carries that
  volume's `source` and `firstPublished`, and a retelling's end note now credits the original's
  own year where it has one.
- Mythology, part 26: Hindu myths, first part. From Kisari Mohan Ganguli's Mahabharata (1883–96,
  `ganguli-mahabharata`): the lotus from Vishnu's navel, Manu and the fish, the churning of the
  ocean (with Shiva swallowing the poison) and Markandeya's vision of the child on the banyan tree.
  From Manmatha Nath Dutt's Vishnu Purana (1896, after H. H. Wilson; `dutt-vishnu-purana`): Prahlada
  and Dhruva the Pole Star. From Dutt's Ramayana (1891, `dutt-ramayana`): Vamana's three steps and the
  descent of the Ganga. All are marked as sacred to Hindus; Manu and the fish (a simile about a
  "drunken harlot") and Prahlada are `mature-themes`. New "Hindu Myths, Simply Told" (`myths-hindu`)
  retells all eight. New culture `hindu` ("Hindu"); `tools/extract_hindu.py`.
- Mythology, part 25: Armenian myths. "Armenian Myths, Simply Told" (`myths-armenian`): Hayk the
  archer and Ara the Beautiful from Movses Khorenatsi's History of the Armenians, Vahagn the
  dragon-slayer (with Claude's own translation of the song of his birth, and the Straw Thief's
  Way), and David of Sassoun from the folk epic. All four are retold with no original in the app:
  Ananikian's Armenian Mythology isn't reachable, and the reachable English versions (Boettiger's
  Armenian Legends and Festivals, F. B. Collins's David of Sassun) are by translators whose dates
  are unknown. Retelling files can now hold verse: a paragraph whose lines all start with `> `.
  New culture `armenian` ("Armenian").
- Mythology, part 24: Persian myths. Nine stories from Helen Zimmern's The Epic of Kings (1882,
  `zimmern-kings`), her prose Shahnameh: the first kings (Hushang's fire, Jamshid's golden age and
  pride), Zahhak the Serpent King, Kaveh the blacksmith, Zal and the Simurgh, Rostam and Rakhsh,
  the seven labours of Rostam, Rostam and Sohrab, Siyavash and the fire, and Bijan and Manizheh;
  Zahhak, Kaveh, Sohrab and Siyavash are `mature-themes`. Yima the good shepherd from the Avesta,
  in James Darmesteter's translation (1880, `darmesteter-avesta`), marked as sacred to
  Zoroastrians. New "Persian Myths, Simply Told" (`myths-persian`): retellings of all ten, with
  the modern spellings (Rostam, Zahhak, Siyavash), and the Zoroastrian creation retold from the
  Bundahishn with no original in the app. A retelling with no original may now set
  `livingTradition` in its front matter. New culture `persian` ("Persian");
  `tools/extract_persian.py`.
- Mythology, part 23: stories from the Qur'an. The People of the Cave (Surah 18), Solomon, the
  ants and the hoopoe (Surah 27), Noah (Surah 11) and Jonah (Surahs 37 and 21), in Marmaduke
  Pickthall's translation (1930, `pickthall-koran`), marked as sacred to Muslims. The Cave shares
  the Seven Sleepers' `workId`, and Noah and Jonah share the Hebrew Bible's, so each lists the
  other under Other versions. New "Stories from the Qur'an, Simply Told" (`quran-stories`):
  retellings of all four, using the Arabic names (Nuh, Sulayman, Yunus). New culture `islamic`
  ("Islamic"); `tools/extract_islamic.py`. A new integrity test fails if a story sacred to Muslims
  ever carries a picture.
- Mythology, part 22: Christian stories. The Nativity (Luke 2:1–20 and Matthew 2:1–12), the Good
  Samaritan and the Prodigal Son in the American Standard Version (1901, `asv-1901`), marked as
  sacred to Christians today; the Prodigal Son is `mature-themes` (the elder son's "with harlots"),
  as the Hebrew Bible's harlots were. The Seven Sleepers of Ephesus from Jacobus de Voragine's
  Golden Legend, in Baring-Gould's translation in Curious Myths of the Middle Ages (1866,
  `baring-gould-myths`), with `workId` `seven-sleepers` for the Qur'an's Sleepers of the Cave to
  share. New "Christian Stories, Simply Told" (`christian-stories`): all four retold, the Prodigal
  Son `flags: none`. New culture `christian` ("Christian"); `tools/extract_christian.py`.
- Mythology, part 21: Jewish legend. Abraham smashing his father's idols, from Ginzberg's The
  Legends of the Jews, volume 1 (Szold's translation, 1909, `ginzberg-legends`); King Solomon, the
  demon king Ashmodai and the stone-cutting worm Shamir, from Friedlander's Jewish Fairy Stories
  (1917, `friedlander-jewish`); and Honi's hundred-year sleep and the Golem of Prague ("The Rabbi's
  Bogey-Man"), from Landa's Jewish Fairy Tales and Legends (1919, `landa-jewish`). Beatrice
  Hirschfeld's pictures for Friedlander are left out (her dates are unknown). New "Jewish Legends,
  Simply Told" (`jewish-legends`): retellings of Abraham, Solomon and the Golem, and Honi the
  Circle-Maker drawing his circle for rain, retold from the Talmud (Ta'anit 23a) with no original
  in the app. Honi's sleep reads at `middle` and has no retelling. New culture `jewish`
  ("Jewish"); `tools/extract_jewish.py`.
- Mythology, part 20: stories from the Hebrew Bible. Twenty passages in the Jewish Publication
  Society's translation (1917, `jps-1917`), from the creation to Daniel in the lions' den, with
  Joseph in three parts. Cain and Abel, Joseph in Egypt (Potiphar's wife), Samson and the judgment
  of Solomon (the two mothers are called harlots) are `mature-themes`. New "Stories from the Hebrew
  Bible, Simply Told" (`hebrew-bible`): eighteen retellings that stay close to the text, the
  mature ones `flags: none`. Cain and Abel and Jacob wrestling the angel read at `middle` and have
  no retelling. New culture `hebrew` ("Hebrew Bible"); `tools/extract_hebrew_bible.py`.
- Stories sacred in a living tradition say so in one line under the byline ("This story is sacred
  to Jews and Christians today."), from a new optional `livingTradition` field on story files that
  retellings inherit.

- The library lists one version of each retold myth: the simplified retelling, with a "Read the
  original" link in the reader (and "Read the retelling for young readers" in the original). Search,
  Cultures/Themes counts, tag pages, collection pages, previous/next and Surprise me follow suit;
  favorites, Continue reading and the Reading shelf don't. A new Settings switch, "List original
  texts instead of retellings", flips it. Books whose every story is retold drop out of the
  library (77 collections → 35 by default); their pages list the originals under "Original texts".
  `simplifiedId` and `adaptedFrom` are now part of the index schema, and the integrity test checks
  that they link both ways within one `workId`.

- Mythology, part 19 (data only): Hittite, Hurrian and Canaanite myths. One original, the Tyrian
  legend of the shepherd's dog that found the purple dye, from Achilles Tatius's _Clitopho and
  Leucippe_ in Rowland Smith's translation (1855, `smith-achilles-tatius`, advanced). New
  `myths-hittite-canaanite` collection, "Hittite and Canaanite Myths, Simply Told": a retelling of
  the purple dye and four ‡ retellings (no public-domain translation exists: these texts were
  first translated in the 1930s) of Telipinu, the god who went away; the Storm God and the dragon
  Illuyanka; Ullikummi, the stone giant; and Baal and Yam. New cultures `hittite` ("Hittite and
  Hurrian") and `canaanite`; `tools/extract_achilles_tatius.py`.

- Mythology, part 18 (data only): Mesopotamian myths. Ten originals in four new collections: the
  Seven Tablets of Creation from Budge's _The Babylonian Legends of the Creation_ (1921,
  `budge-babylonian-creation`); the Epic of Gilgamesh in six stories from Budge's _The Babylonian
  Story of the Deluge and the Epic of Gilgamish_ (1920, `budge-gilgamish`) — Gilgamish and Enkidu
  and Ishtar and the Bull of Heaven are `mature-themes`, Tablet XII is left out, and the sixth joins
  Budge's full translation of the Deluge to his summary of the rest of Tablet XI; the Descent of
  Ishtar and Etana from Mackenzie's _Myths of Babylonia and Assyria_ (1915, `mackenzie-babylonia`);
  and Adapa from Jastrow's _The Religion of Babylonia and Assyria_ (1898, `jastrow-babylonia`,
  narrative paragraphs only). Eight are `advanced`; Tablet XI and Adapa are `middle` but retold
  anyway (see CLAUDE.md). New `myths-mesopotamian` collection, "Mesopotamian Myths, Simply Told":
  ten retellings (the two `mature-themes` Gilgamesh parts retold `flags: none`) and three ‡ retellings
  with no public-domain source in reach: Inanna and the gifts of wisdom (the _me_), Lugalbanda and
  the Anzu bird, and the gods making people from clay in Atrahasis. New culture `mesopotamian`;
  `tools/extract_mesopotamian.py`.

- Mythology, part 17 (data only): Egyptian myths. Eleven originals in five new collections, all
  advanced: from Budge's _Legends of the Gods_ (1912, `budge-legends`) the creation (`mature-themes`),
  the destruction of mankind (`mature-themes`), Ra and Isis, Isis and Horus in the marshes (the
  Metternich Stela's two narrative passages, joined by a note), and Plutarch's five added days and story of Isis
  and Osiris in Samuel Squire's translation (1744) as Budge reprints it (both `mature-themes`); the
  weighing of the heart from Budge's _The Book of the Dead_ (`budge-book-of-the-dead`); the sun's
  night journey and Khnemu and the Nile from Lewis Spence's _Myths and Legends of Ancient Egypt_
  (1915, `spence-egypt`); Petrie's "The Shipwrecked Sailor" (1895, `petrie-egyptian`); and
  Herodotus on the phoenix in Macaulay's translation (1890, `macaulay-herodotus`). Eleven
  retellings in _Egyptian Myths, Simply Told_. The Contendings of Horus and Set (the lettuce and the
  stone boats) has no translation before 1931, so Horus and Set's battles come from Plutarch.
  New culture `egyptian` (34 in all). Over 1,000 stories.
- Mythology, part 16 (data only): Hungarian, Caucasus and Basque legends. Originals: Claude's
  verse translation of János Arany's legend of the wondrous stag, the sixth canto of _Buda halála_
  (1864), in a new _Legends from the Hungarian Poets_ (`hungarian-sources`; no public-domain
  English version of Hunor and Magor, and the Latin chronicles couldn't be reached), and the
  Tartaro, the one-eyed giant, from Wentworth Webster's _Basque Legends_ (1877, `webster-basque`).
  Retold in three new Simply Told collections: Hunor and Magor (the poem is middle-band but long
  and in verse, so it gets a prose retelling) and the Tartaro, plus, with no original in the app
  and flagged for review, Emese's dream and the turul bird, Sosruko the child of the stone
  (in place of the planned fire-theft story, which isn't well enough attested to retell without a
  source; Dumézil's French Nart legends, the planned source, aren't public domain everywhere),
  Amirani the chained giant, Martin Txiki and the Basajauns, and Mari of Anboto. New cultures
  `hungarian`, `circassian`, `georgian` and `basque` (33 in all).
- Mythology, part 15 (data only): West Slavic and Balkan legends. Originals, in two new
  collections: Libussa and the founding of Prague, the opening of Count Lützow's _The Story of
  Prague_ (1902, `lutzow-prague`; his chronicle quotations stand in for a translation of Cosmas,
  whose Latin text couldn't be reached), and three Prince Marko pieces from Petrovitch's _Hero
  Tales and Legends of the Serbians_ (1914, `petrovitch-serbian`): his horse Sharatz, "Prince Marko
  Tells Whose the Empire Shall Be" and "Prince Marko and the Veela", without the colour plates,
  whose illustrators' dates aren't known. All four are advanced, so all are retold, in two new
  Simply Told collections, `myths-west-slavic` (Polish and Czech) and `myths-balkan` (Serbian,
  Romanian and Albanian). Retold with no original in the app, and flagged for review: Lech, Czech
  and Rus, the Wawel dragon, Master Manole and the monastery of Argeș (`mature-themes`: his wife is
  walled up alive), and how Mujo got his strength from the mountain fairies. New cultures `polish`,
  `czech`, `serbian`, `romanian` and `albanian` (29 in all).
- Mythology, part 14 (data only): the Russian shelf. The plan named Ransome's _Old Peter's Russian
  Tales_, but Ransome died in 1967 and isn't public domain everywhere, so the tales come from
  three older translations, each a new collection: Vasilissa the Fair and Frost from Ralston's
  _Russian Fairy Tales_ (1873, `ralston-russian`), the Firebird and the Grey Wolf
  (`mature-themes`) and Koshchei the Deathless from Curtin's _Myths and Folk-Tales of the
  Russians_ (1890, `curtin-russian`), and Márya Moryévna (`mature-themes`) and Ilya Muromets and
  the Nightingale Robber from Magnus's translation of Afanasyev, _Russian Folk-Tales_ (1915,
  `magnus-russian`). The four that are advanced or over 20 minutes are retold in the new _Russian
  Tales and Legends, Simply Told_ (`myths-russian`), which also has three legends with no
  public-domain text that could be reached, retold and flagged for review: Dobrynya and the
  dragon, Sadko (following Hapgood's 1902 outline of the bylina) and the Snow Maiden. Perun and
  Veles is left out (the myth is a modern scholars' reconstruction, not a story anyone told), and
  so is the Little Humpbacked Horse (Yershov's poem, with no reachable public-domain
  translation). New culture `russian` (24 in all).
- Mythology, part 13 (data only): Sámi, Lithuanian and Latvian, all retold without an original in
  the app. The plan was to translate public-domain originals (Donner's _Lappalaisia lauluja_,
  1876; Basanavičius's tales, 1904; Rėza's dainos, 1825; Barons's _Latvju dainas_), but none of
  them can be reached from here. So, written from the attested versions and flagged for review:
  the Son of the Sun and the giant's daughter (added to `myths-finnic`, now _Finnish, Estonian and
  Sámi Legends, Simply Told_), and, in the new _Lithuanian and Latvian Legends, Simply Told_
  (`myths-baltic`), Eglė the Queen of Serpents, Jūratė and Kastytis (labelled a writers' legend),
  the Sun, the Moon and the Morning Star (Lithuanian and Latvian versions), and Perkūnas and the
  devil. New cultures `sami` and `lithuanian` (23 in all).
- Mythology, part 12 (data only): the Finnish and Estonian shelf. From R. Eivind's _Finnish
  Legends for English Children_ (1893), a prose Kalevala for children, a new `eivind-finnish`
  collection: the world made from the duck's eggs, the singing contest, the forging of the Sampo,
  Lemminkainen's death and his mother's rake (`mature-themes`), the first kantele, the capture of
  the Sampo and the stolen sun and moon, with bridging notes where a story starts mid-saga and the
  storyteller's frame left out. From W. F. Kirby's prose Kalevipoeg in _The Hero of Esthonia_
  (1895), `kirby-esthonia`: the death of Kalev (Linda builds Tallinn's hill and weeps Lake
  Ülemiste), the brothers' stone-throwing contest, and the hero's end at the brook and his watch
  at the gates of the underworld (`mature-themes`). All ten read at advanced level, so the new
  _Finnish and Estonian Legends, Simply Told_ has a retelling of each (grade 4.2–5.9), using modern
  spellings. New culture `finnish` (21 in all). New tool `extract_finnic.py`.
- Mythology, part 11 (data only): the Arthurian shelf. Pyle's Arthur books, Weston's _Gawain_
  and Lanier's _Boy's King Arthur_ are past the end of the Gutenberg mirrors this project can
  reach, so the tales come from _The Book of Romance_ (1902), edited by Andrew Lang and written by
  Mrs. Lang from Malory, in a new `lang-romance` collection with eleven of H. J. Ford's pictures:
  the drawing of the sword, Excalibur, how the Round Table began, Beaumains (Gareth), the Quest of
  the Holy Graal and the end of Arthur (the last two `mature-themes`). Merlin and the dragons
  under Vortigern's tower comes from Geoffrey of Monmouth's _British History_ in Thompson's
  translation as revised by Giles (1848), cut after the prophecy of the boar of Cornwall
  (`mature-themes`), in `geoffrey-british-history`. All seven read at advanced level, so the new
  _Arthurian Legends, Simply Told_ has a retelling of each (grade 3.2–4.9), plus Gawain and the
  Green Knight, retold from the poem without an original in the app. New culture `arthurian` (20
  in all). New tool `extract_arthurian.py`.
- Mythology, part 10 (data only): the Scottish, Manx and Breton shelf. From Elizabeth W.
  Grierson's _The Scottish Fairy Book_ (1910), a new `grierson-scottish` collection: Thomas the
  Rhymer, the Seal Catcher and the Merman, and Assipattle and the Mester Stoorworm. From Sophia Morrison's _Manx Fairy Tales_ (1911),
  `morrison-manx`: "The Making of Mann" and "The Coming of Saint Patrick" (Manannan's mist and the
  three-legged men). All five read at advanced level and get retellings in the new _Scottish, Manx
  and Breton Legends, Simply Told_ (grade 3.8–6.3), plus two retold without an original: the
  Cailleach, queen of winter, and the drowned Breton city of Ys. New cultures `manx` and `breton`
  (19 in all). New tool `extract_scottish.py`.
- Mythology, part 9 (data only): the Welsh shelf. From Lady Charlotte Guest's _Mabinogion_ (1849), a
  new `guest-mabinogion` collection: the Four Branches (Pwyll, Branwen, Manawyddan and Math;
  Branwen and Math are `mature-themes`), Lludd and Llevelys, Taliesin and Kilhwch and Olwen, with
  the englyns and Taliesin's songs as verse and a few transcription errors corrected. From Joseph
  Jacobs's _Celtic Fairy Tales_ (1892), `jacobs-celtic`: "The Shepherd of Myddvai" and "Beth
  Gellert" (`mature-themes`; its end note says the legend is no older than about 1800 at
  Beddgelert). All nine get retellings in the new _Welsh Legends, Simply Told_ (grade 3.3–5.4),
  plus the drowned land of Cantre'r Gwaelod, retold without an original. New culture `welsh` (17
  in all). New tool `extract_welsh.py`; retellings from Jacobs credit the book and its editor.
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
