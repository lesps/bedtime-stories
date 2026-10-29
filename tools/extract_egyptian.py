#!/usr/bin/env python3
"""Egyptian myths: Budge's Legends of the Gods (1912) and The Book of the Dead, Spence's Myths and
Legends of Ancient Egypt (1915), Petrie's Egyptian Tales (1895) and Herodotus on the phoenix
(Macaulay's translation, 1890).

    git clone --depth 1 https://github.com/GITenberg/Legends-of-the-Gods-The-Egyptian-Texts-edited-with-Translations_9411.git src/Legends-of-the-Gods-The-Egyptian-Texts-edited-with-Translations_9411
    git clone --depth 1 https://github.com/GITenberg/The-Book-of-the-Dead_7145.git src/The-Book-of-the-Dead_7145
    git clone --depth 1 https://github.com/GITenberg/Myths-and-Legends-of-Ancient-Egypt_43662.git src/Myths-and-Legends-of-Ancient-Egypt_43662
    git clone --depth 1 https://github.com/GITenberg/Egyptian-Tales-Translated-from-the-Papyri--13-First-series-IVth-to-XIIth-dynasty_7386.git src/Egyptian-Tales-Translated-from-the-Papyri--13-First-series-IVth-to-XIIth-dynasty_7386
    git clone --depth 1 https://github.com/GITenberg/The-History-of-Herodotus---Volume-1_2707.git src/The-History-of-Herodotus---Volume-1_2707
    python3 tools/extract_egyptian.py src

All five are read from the plain-text editions. Each story is a passage running from an opening
phrase to a closing phrase (both kept); paragraphs are split on blank lines, footnotes
("[FN#..." paragraphs) and footnote markers are dropped, and so are the stela's line numbers that
Budge leaves inside the Metternich text. The two Metternich passages (Isis's narrative and the
stinging of Horus) make one story, joined by a note where the stela breaks off for other spells.
Budge prints Plutarch in Samuel Squire's translation
(1744), so those two stories open with a note saying so. Petrie's pictures (Tristram Ellis) are
left out. Writes `budge-legends`, `budge-book-of-the-dead`, `spence-egypt`, `petrie-egyptian`
and `macaulay-herodotus`.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

COMMON = {"license": "Public domain in the USA", "language": "en"}
BUDGE = {**COMMON, "id": "budge-legends", "title": "Legends of the Gods", "author": "E. A. Wallis Budge",
         "contributor": None, "firstPublished": 1912, "source": "https://www.gutenberg.org/ebooks/9411",
         "originalLanguage": "egy"}
DEAD = {**COMMON, "id": "budge-book-of-the-dead", "title": "The Book of the Dead", "author": "E. A. Wallis Budge",
        "contributor": None, "firstPublished": None, "source": "https://www.gutenberg.org/ebooks/7145",
        "originalLanguage": "egy"}
SPENCE = {**COMMON, "id": "spence-egypt", "title": "Myths and Legends of Ancient Egypt", "author": "Lewis Spence",
          "contributor": None, "firstPublished": 1915, "source": "https://www.gutenberg.org/ebooks/43662",
          "originalLanguage": "en"}
PETRIE = {**COMMON, "id": "petrie-egyptian", "title": "Egyptian Tales, First Series",
          "author": "W. M. Flinders Petrie", "contributor": None, "firstPublished": 1895,
          "source": "https://www.gutenberg.org/ebooks/7386", "originalLanguage": "egy"}
HERODOTUS = {**COMMON, "id": "macaulay-herodotus", "title": "The History of Herodotus", "author": "Herodotus",
             "contributor": "Translated by G. C. Macaulay", "firstPublished": 1890,
             "source": "https://www.gutenberg.org/ebooks/2707", "originalLanguage": "el"}

SQUIRE = ("Plutarch's account, in Samuel Squire's translation (1744), as Budge reprints it. Plutarch calls "
          "the gods by Greek names: Rhea is Nut, Kronos is Geb, Helios is Ra, Hermes is Thoth, Selene is the "
          "Moon, and Typhon is Set.")
SQUIRE_OSIRIS = "Plutarch's account, in Samuel Squire's translation (1744), as Budge reprints it. Typhon is Set."

METTERNICH_BRIDGE = ("Here the stela breaks off for other spells, and then goes on with Isis's own story of "
                     "how Horus was stung in the marshes.")

# (collection, file, encoding, title, workId, first words, last words, flags, opening note, headings).
# A row with no title continues the story above it, after a note (given in the workId column).
STORIES = [
    (BUDGE, "Legends-of-the-Gods-The-Egyptian-Texts-edited-with-Translations_9411/9411-8.txt", "latin-1",
     "The Creation", "egyptian-creation", "[These are] the words which the god Neb-er-tcher spake",
     "multitudinous offspring in this earth.\"", ["mature-themes"], None, ()),
    (BUDGE, "Legends-of-the-Gods-The-Egyptian-Texts-edited-with-Translations_9411/9411-8.txt", "latin-1",
     "The Destruction of Mankind", "egyptian-destruction-of-mankind", "[Here is the story of Ra,]",
     "father carrying a son upon his head.", ["mature-themes"], None, ()),
    (BUDGE, "Legends-of-the-Gods-The-Egyptian-Texts-edited-with-Translations_9411/9411-8.txt", "latin-1",
     "The Legend of Ra and Isis", "egyptian-ra-isis-name", "The Chapter of the divine (or, mighty) god",
     "an image of Isis and an image of Horus.", [], None, ()),
    (BUDGE, "Legends-of-the-Gods-The-Egyptian-Texts-edited-with-Translations_9411/9411-8.txt", "latin-1",
     "Isis and Horus in the Marshes", "egyptian-isis-horus-marshes", "I am Isis, [and] I have come forth",
     "everyone who is stricken shall be in good case likewise.", [], None, ()),
    (BUDGE, "Legends-of-the-Gods-The-Egyptian-Texts-edited-with-Translations_9411/9411-8.txt", "latin-1",
     None, METTERNICH_BRIDGE, "\"I am Isis, who conceived a child",
     "I have made haste . . . . . .\"", [], None, ()),
    (BUDGE, "Legends-of-the-Gods-The-Egyptian-Texts-edited-with-Translations_9411/9411-8.txt", "latin-1",
     "The Five Added Days", "egyptian-five-days", "The goddess Rhea,[FN#293] they say",
     "and the Greeks Apollo.", ["mature-themes"], SQUIRE, ()),
    (BUDGE, "Legends-of-the-Gods-The-Egyptian-Texts-edited-with-Translations_9411/9411-8.txt", "latin-1",
     "The History of Isis and Osiris", "egyptian-osiris", "XIII.  Osiris having become king of Egypt",
     "and was lame in his lower limbs.", ["mature-themes"], SQUIRE_OSIRIS, ()),
    (DEAD, "The-Book-of-the-Dead_7145/7145-8.txt", "latin-1",
     "The Weighing of the Heart", "egyptian-weighing-heart", "In great papyri of the Book of the Dead",
     "passed into the Kingdom of Osiris.", [], None, ()),
    (SPENCE, "Myths-and-Legends-of-Ancient-Egypt_43662/43662-0.txt", "utf-8-sig",
     "The Journey of the Sun through the Night", "egyptian-ra-night-journey", "We find other descriptions of the Duat",
     "a similar journey is outlined in it.", [], None, ()),
    (SPENCE, "Myths-and-Legends-of-Ancient-Egypt_43662/43662-0.txt", "utf-8-sig",
     "Khnemu and the Source of the Nile", "egyptian-khnum", "At the city of Elephantine or Abu",
     "unto the god Khnemu, the god of the Nile.", [], None, ("The Legend of the Nile's Source",)),
    (PETRIE, "Egyptian-Tales-Translated-from-the-Papyri--13-First-series-IVth-to-XIIth-dynasty_7386/7386.txt",
     "latin-1", "The Shipwrecked Sailor", "egyptian-shipwrecked-sailor", "The wise servant said",
     "and behold I have become such.\"", [], None, ("THE FAREWELL",)),
    (HERODOTUS, "The-History-of-Herodotus---Volume-1_2707/2707.txt", "latin-1",
     "The Phoenix", "egyptian-phoenix", "73. There is also another sacred bird",
     "Thus they say that this bird does.", [], None, ()),
]


def find(text, phrase, pos=0):
    """Finds a phrase whatever the line breaks inside it; returns (start, end)."""
    m = re.compile(r"\s+".join(map(re.escape, phrase.split()))).search(text, pos)
    if not m:
        raise SystemExit(f"not found: {phrase!r}")
    return m.span()


def passage(text, first, last):
    start = find(text, first)[0]
    return text[start:find(text, last, start)[1]]


def paragraphs(raw, headings):
    blocks = []
    for para in re.split(r"\n\s*\n", raw.replace("\r\n", "\n")):
        t = re.sub(r"\s+", " ", re.sub(r"(?<=\w)-[ \t]*\n\s*(?=\w)", "-", para)).strip()
        t = re.sub(r"_([^_]+)_", r"\1", t)  # Spence's italics
        if not t or t.startswith("[FN#"):
            continue
        t = re.sub(r"\s*\[FN#\d+\]", "", t)
        t = re.sub(r"\s*\[\d+\]", "", t)
        t = re.sub(r"(?<=[a-z,;]) \d{1,3} (?=[a-z])", " ", t)  # stela line numbers in Budge
        t = re.sub(r"^\d+\. ", "", t)  # Herodotus's section number
        t = re.sub(r"^[XVI]+\. +", "", t)  # Plutarch's section numbers
        if t in headings:
            blocks.append({"type": "heading", "text": t.title() if t.isupper() else t})
        else:
            blocks.append({"type": "p", "text": t})
    return blocks


def main(src):
    index = load_index()
    by_collection = {}
    for col, file, enc, title, work_id, first, last, flags, note, headings in STORIES:
        text = (Path(src) / file).read_bytes().decode(enc)
        blocks = paragraphs(passage(text, first, last), headings)
        if note:
            blocks.insert(0, {"type": "note", "text": note})
        stories = by_collection.setdefault(col["id"], (col, []))[1]
        if title is None:  # a continuation: append to the previous story and recount it
            prev = stories.pop()
            prev["blocks"] += [{"type": "note", "text": work_id}, *blocks]
            stories.append(finish({k: v for k, v in prev.items() if k not in ("wordCount", "readingMinutes",
                                                                              "readingLevel", "hasImages")}))
            continue
        stories.append(finish({"id": f"{col['id']}--{re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')}",
                               "collectionId": col["id"], "order": len(stories) + 1, "title": title,
                               "origin": None, "excluded": False, "flags": flags, "moral": None,
                               "blocks": blocks, "workId": work_id}))
    for col, stories in by_collection.values():
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:62} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
