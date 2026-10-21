# Story text review

A review of all 614 stories for consistency and completeness (October 2026). Corrections live in
`tools/fix_text.py`, which re-applies them after any regeneration; `src/data/integrity.test.ts`
("story text") fails if the fixed kinds of problem come back. The last section is a brief for an
assistant with web access: what could not be settled without the printed sources.

## How it was checked

Every story was scanned for: Project Gutenberg leftovers, encoding damage (mojibake, HTML entities),
markup, footnote markers, empty or junk blocks, story endings without closing punctuation, paragraphs
that look like another story's title (merged stories), word counts and reading times against the
text, title casing, duplicate titles and paragraphs, line-wrap hyphenation, missing spaces around
punctuation, and paired quotation marks traced through each story as the app displays it. Rare words
were spell-checked against a dictionary and the corpus' own vocabulary to surface OCR typos. Every
hit was then read in context.

Clean on: encoding, markup, Gutenberg boilerplate, word counts, endings (no truncated stories found),
spacing, images (all present).

## Fixed

| Kind                                 | Stories | Examples                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------ | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Merged stories                       | 1       | Hunt's _The Three Sluggards_ contained a second tale, "151\* The Twelve Idle Servants" (KHM 151a). Split into its own story, `grimm-hunt--the-twelve-idle-servants` (615 stories now).                                                                                                                                                                                                                                                                                                                                                                            |
| Footnotes printed as story text      | 9       | Andersen's _Shoes of Fortune_ (9 notes), _Dream of Little Tuk_ (6), _The Shadow_, _The Elderbush_, _The Swineherd_; Ozaki's _Urashima Taro_ and _Tongue-Cut Sparrow_; Taylor's _Golden Goose_ ("[\*] Simpleton" was the last "verse" of the story). Now note blocks; the `*`, `[*]`, `[1]` markers are gone.                                                                                                                                                                                                                                                      |
| Junk at the end of a story           | 2       | _The Golden Key_ ended with a separator line and "Children's Legends" (the next section's title); Ozaki's _Stones of Five Colors_ ended with "THE END."                                                                                                                                                                                                                                                                                                                                                                                                           |
| Section headings as plain paragraphs | 6       | _The Snow Queen_ ("SECOND STORY. …"), _The Shoes of Fortune_ ("II. …"), _Chanticleer and Partlet_, both _Wedding of Mrs. Fox_, Hunt's _The Elves_. Now headings; the two missing first-section headings were added.                                                                                                                                                                                                                                                                                                                                               |
| Quotation marks                      | 25      | Missing closing quotes (Hunt's _Mother Holle_, _Death's Messengers_, _The Riddle_, _The Two Kings' Children_, _Faithful John_, _Hans Married_), missing opening quotes (_Johnny-Cake_, _Ginger and Pickles_, _Pigling Bland_), stray quotes (_Mrs. Tiggy-winkle_, _The Fox and the Geese_), a space inside a quote (Aesop's _Travelers and the Purse_), a backwards curly quote (Lang's _Cinderella_), and speech-within-speech printed with double quotes (Hunt's _Doctor Knowall_, _Iron John_, _The Goose-Girl at the Well_, _The Bittern and the Hoopoe_, …). |
| Typos                                | 14      | daugher, strategem, swimmming, neverthless, burries, princes's, willt, scolar, hunstman, "breen clover", "himfor", "nor hear anything", "red stockings on' and", "thy heldest" (the drummer's other verses say "thou heldest").                                                                                                                                                                                                                                                                                                                                   |
| Line-wrap hyphenation                | 9       | "Rose- red", "goose- girl", "Cock-a- doodle-doo", "High-and- Mighty" (all Hunt).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Drop-cap capitals                    | 31      | "THERE was once…", "THE Camel's hump…", "I AM the Most Wise Baviaan…" (Hunt, Kipling, Lang, Potter) → ordinary capitalisation.                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Dash rendering (app)                 | 33      | Hunt writes a dash as `---`; the typesetter turned it into "—-". It now renders any run of hyphens as one em dash.                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Titles                               | 9       | Hunt titles brought in line with the rest: "Odds and Ends", "Brides on Their Trial", "The Devil with the Three Golden Hairs", "Little Snow-White", "One-Eye, Two-Eyes, and Three-Eyes", …                                                                                                                                                                                                                                                                                                                                                                         |
| Source notes                         | 7       | Lang's origins regained their accents: Asbjørnsen and Moe, Cabinet des Fées, Fortunée, La Belle et la Bête.                                                                                                                                                                                                                                                                                                                                                                                                                                                       |

Word counts and reading times were recomputed. Stories that gained a block (_The Snow Queen_,
_The Shoes of Fortune_, _The Swineherd_) shift later block positions by one, so a saved place or a
highlight in them may land one paragraph off; highlights re-anchor by their quoted text.

## Checked and left as they are

- Archaic verb forms (leavest, darest, saidst), dialect (cauld, catcht, gooden, "hur" in the Welsh
  giant's speech, "a dry cappy"), Kipling's invented words (thinked, so'd, xactly), names and
  Japanese words. They are correct as printed.
- Repeated paragraphs are refrains (the Fisherman's rhyme, the Frog Prince's song, the Looking-glass).
- Potter's rhymes open every line with a quotation mark (_Pigling Bland_); that is her convention.
- Verses inside speech in Hunt (_One-Eye…_, _Ferdinand the Faithful_, _The Robber Bridegroom_) keep
  the source's quote marks.
- Aesop's three duplicated titles are different fables; eleven fables have two morals in the book.
- Capitals that are meant: "BE BOLD, BE BOLD…" (_Mr. Fox_), "NO MORE TWIST" (_Tailor of
  Gloucester_), Johnny-Cake's shout.
- Hunt's _Little Red-Cap_ keeps its "\* \* \*" break before the second wolf episode.

## Brief for an assistant with web access

> You are helping verify the text of a children's story-reading app. Its stories come from Project
> Gutenberg editions (listed below). An automated and manual review fixed what it could from the
> data alone; the items below need the original editions. For each item, look at the Gutenberg
> HTML or text of the named ebook and report back, per item: the story, what the source says
> (quote it exactly), and a correction in the form _story id — current text → corrected text_, or
> "matches source, no change". Do not change anything that is not listed; old spellings and dialect
> are intentional.
>
> Sources: Andersen's Fairy Tales — gutenberg.org/ebooks/1597 · The Blue Fairy Book (Lang) —
> /ebooks/503 · Household Tales (Grimm, tr. Margaret Hunt) — /ebooks/5314 · Grimms' Fairy Tales
> (tr. Taylor & Edwardes) — /ebooks/2591 · The Tale of Pigling Bland — /ebooks/582 · The Tale of
> Ginger and Pickles — /ebooks/14877 · The Tale of Mrs. Tiggy-Winkle — /ebooks/15137.
>
> 1. **Added headings (Andersen, #1597).** _The Snow Queen_ (`andersen--the-snow-queen`) now opens
>    with the heading "First Story. Which Treats of a Mirror and of the Splinters", and _The Shoes
>    of Fortune_ (`andersen--the-shoes-of-fortune`) with "I. A Beginning". Both were missing from
>    the extracted text and were added from memory. Confirm the exact wording.
> 2. **Prince Ahmed (Lang, #503).** `lang-blue--the-story-of-prince-ahmed-and-the-fairy-paribanou`
>    has a lone section marker "II" (before "When Prince Ahmed came pretty nigh to these rocks…")
>    and no "I". Does the book mark a part I, and where? Or should the "II" go?
> 3. **Missing source notes (Lang, #503).** Most Blue Fairy Book tales carry a source footnote
>    (e.g. "Charles Perrault.", "Grimm."). These six have none in the data: Little Red Riding Hood,
>    The Brave Little Tailor, The History of Whittington, The Sleeping Beauty in the Wood, The
>    Terrible Head, The Water-Lily; or, The Gold-Spinners. Give each one's footnote text if the book
>    has one.
> 4. **Lost footnotes (Hunt, #5314).** Two asterisks pointed at footnotes whose text is missing and
>    were removed: _The Grave-Mound_ ("lend me four measures\* of corn") and _The Raven_ ("cried
>    aloud in their delight.\* Then he alighted"). Give the footnote text if the edition has one.
> 5. **The Twelve Idle Servants (Hunt, #5314).** Split out of _The Three Sluggards_, where it
>    appeared as "151\* The Twelve Idle Servants". Confirm it is a separate tale in the edition, its
>    German title (entered as "Die zwölf faulen Knechte"), and whether the eighth, ninth and tenth
>    servants each have their own paragraph (the data runs them into the seventh's).
> 6. **Quote fixes made without the source.** Confirm these match the printed text:
>    - _Pigling Bland_ (#582): the paragraph beginning "Alexander, you are not attending. Here are
>      two licences…" was given an opening quotation mark (the narrator's speech, "said I impressively",
>      continues from the paragraph before).
>    - _Ginger and Pickles_ (#14877): the poster text now opens with a quote: …re-open the
>      shop—"Henny's Opening Sale! Grand co-operative Jumble! … Come buy, come try, come buy!"
>    - _Mrs. Tiggy-Winkle_ (#15137): a stray opening quote was removed from "Then Mrs. Tiggy-winkle
>      made tea…".
>    - Hunt (#5314): in _The Goose-Girl at the Well_, the Queen's account quotes the King and her
>      daughters; those inner quotes are now single, and a closing quote was added in "We all begged
>      and prayed for her," said the Queen, "but…".
> 7. **Completeness spot-check.** No truncated stories were found, but this was judged from the
>    text alone. Check the story counts against the books (Aesop for Children #19994: 147; Grimm
>    #2591: 62; Andersen #1597: 18; Blue Fairy Book #503: 37; English Fairy Tales #7439: 43; Just So
>    Stories #2781: 12; Household Tales #5314: 200 tales + 10 children's legends, plus the split-out
>    151a; Ozaki #4018: 22; James #35853: 38), and compare the final sentence of the five longest
>    stories with the source: The Shoes of Fortune, The Snow Queen, The Story of Prince Ahmed and
>    the Fairy Paribanou, The Little Mermaid, and Hunt's The Two Brothers.
