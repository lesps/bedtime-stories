#!/usr/bin/env python3
"""Mesopotamian myths: Budge's The Babylonian Legends of the Creation (1921) and The Babylonian Story
of the Deluge and the Epic of Gilgamish (1920), Mackenzie's Myths of Babylonia and Assyria (1915)
and Jastrow's The Religion of Babylonia and Assyria (1898).

    git clone --depth 1 https://github.com/GITenberg/The-Babylonian-Legends-of-the-Creation_9914.git src/The-Babylonian-Legends-of-the-Creation_9914
    git clone --depth 1 https://github.com/GITenberg/The-Babylonian-Story-of-the-Deluge-as-Told-by-Assyrian-Tablets-from-Nineveh-The-Discovery-of-t__7096.git src/The-Babylonian-Story-of-the-Deluge-as-Told-by-Assyrian-Tablets-from-Nineveh-The-Discovery-of-t__7096
    git clone --depth 1 https://github.com/GITenberg/Myths-of-Babylonia-and-Assyria_16653.git src/Myths-of-Babylonia-and-Assyria_16653
    git clone --depth 1 https://github.com/GITenberg/The-Religion-of-Babylonia-and-Assyria_20758.git src/The-Religion-of-Babylonia-and-Assyria_20758
    python3 tools/extract_mesopotamian.py src

All four are read from the plain-text editions, a story being the passage from an opening phrase to
a closing phrase (both kept), split into paragraphs on blank lines. Illustration captions,
footnotes and footnote markers are dropped. Paragraphs of numbered lines (Budge's translated
passages) become verse without the numbers, and so do paragraphs of indented lines (a deeper indent
continues a line); a bracketed one-line paragraph in Budge's Deluge
("[The Building of the Ship.]") becomes a heading, or a note when it says lines are lost. Budge's
summary of the Gilgamish tablets is cut into six stories at tablet headings (Tablet XII, which is
too broken to follow, is left out); the sixth, Tablet XI, is his full translation of the Deluge
followed by his summary of the rest of that tablet. Where a writer stops the story to compare other myths, those paragraphs are
left out (SKIP), or only the narrative paragraphs are kept (KEEP, for Jastrow's Adapa, which is
mostly commentary around the translated lines). Writes `budge-babylonian-creation`,
`budge-gilgamish`, `mackenzie-babylonia` and `jastrow-babylonia`.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

COMMON = {"license": "Public domain in the USA", "language": "en", "contributor": None}
CREATION = {**COMMON, "id": "budge-babylonian-creation", "title": "The Babylonian Legends of the Creation",
            "author": "E. A. Wallis Budge", "firstPublished": 1921,
            "source": "https://www.gutenberg.org/ebooks/9914", "originalLanguage": "akk"}
GILGAMISH = {**COMMON, "id": "budge-gilgamish", "title": "The Babylonian Story of the Deluge and the Epic of Gilgamish",
             "author": "E. A. Wallis Budge", "firstPublished": 1920,
             "source": "https://www.gutenberg.org/ebooks/7096", "originalLanguage": "akk"}
MACKENZIE = {**COMMON, "id": "mackenzie-babylonia", "title": "Myths of Babylonia and Assyria",
             "author": "Donald A. Mackenzie", "firstPublished": 1915,
             "source": "https://www.gutenberg.org/ebooks/16653", "originalLanguage": "en"}
JASTROW = {**COMMON, "id": "jastrow-babylonia", "title": "The Religion of Babylonia and Assyria",
           "author": "Morris Jastrow", "firstPublished": 1898,
           "source": "https://www.gutenberg.org/ebooks/20758", "originalLanguage": "akk"}

CREATION_TXT = ("The-Babylonian-Legends-of-the-Creation_9914/9914-8.txt", "latin-1")
DELUGE_TXT = ("The-Babylonian-Story-of-the-Deluge-as-Told-by-Assyrian-Tablets-from-Nineveh-The-Discovery-of-t__7096"
              "/7096-8.txt", "latin-1")
MACKENZIE_TXT = ("Myths-of-Babylonia-and-Assyria_16653/16653-0.txt", "utf-8-sig")
JASTROW_TXT = ("The-Religion-of-Babylonia-and-Assyria_20758/20758-8.txt", "latin-1")

JASTROW_KEEP = (
    "The beginning of the story, as in the case", "The south wind blew", "Adapa's threat is carried out",
    "Even as he spoke", "Seven is to be interpreted", "\"Why has the south wind", "Anu, upon hearing the news",
    "... Two gods have disappeared", "\"Who are the two gods", "Tammuz and Gishzida will look",
    "Tammuz and Gishzida will know", "When thou comest before Anu", "Ea obeys the order", "Upon mounting to heaven",
    "Adapa replies:", "'Two gods have disappeared", "'Who are the two gods", "Tammuz and Gishzida looked",
    "'Come, Adapa, why hast", "Adapa answered Anu", "Tammuz and Gishzida thereupon intercede", "Anu is appeased",
    "Why did Ea permit", "The privilege accorded", "'Now what shall we grant", "Anu looked at him",
    "Adapa replies, unconscious", "'Ea, my lord, commanded", "Adapa returns to the earth",
)
CREATION_SKIP = ("The text of the Fifth Tablet, which", "At a later period, say about 500", "The accompanying illustration",
                 "The mutilated text of the Fifth Tablet", "Now among the texts which have been found")
DELUGE_CUT = ("The story of the Deluge as told by Uta-Napishtim to Gilgamish has already been given on pp. 31-40, "
              "and we therefore pass on to the remaining contents of this Tablet. ")

TABLET_XI_NOTE = ("Budge translates the Deluge story in full; the rest of the Eleventh Tablet is given in his "
                  "summary.")

# (collection, (file, encoding), title, workId, first words, last words, flags, keep, skip). A row
# with no title continues the story above it, after a note (given in the workId column).
STORIES = [
    (CREATION, CREATION_TXT, "The Seven Tablets of Creation", "babylonian-marduk-tiamat",
     "In the beginning nothing whatever existed except", "accepted the absolute supremacy of Marduk.",
     [], None, CREATION_SKIP),
    (GILGAMISH, DELUGE_TXT, "Gilgamish and Enkidu", "gilgamesh-1-enkidu",
     "The First Tablet.", "derived from a tablet at Philadelphia.", ["mature-themes"], None, ()),
    (GILGAMISH, DELUGE_TXT, "The Forest of Khumbaba", "gilgamesh-2-humbaba",
     "The Third Tablet.", "returned to Erech in triumph.", [], None, ()),
    (GILGAMISH, DELUGE_TXT, "Ishtar and the Bull of Heaven", "gilgamesh-3-bull",
     "The Sixth Tablet", "related it to Gilgamish.", ["mature-themes"], None, ()),
    (GILGAMISH, DELUGE_TXT, "The Death of Enkidu", "gilgamesh-4-enkidu-death",
     "The Seventh Tablet.", "like a lioness robbed of her whelps.", [], None, ()),
    (GILGAMISH, DELUGE_TXT, "The Journey to Uta-Napishtim", "gilgamesh-5-journey",
     "The Ninth Tablet.", "or escape from death.", [], None, ()),
    (GILGAMISH, DELUGE_TXT, "The Deluge and the Plant of Youth", "gilgamesh-6-flood-plant",
     "1. Gilgamish [10] said unto Uta-Napishtim", "made me to dwell at the mouth of the rivers.\"", [], None, ()),
    (GILGAMISH, DELUGE_TXT, None, TABLET_XI_NOTE,
     "The Eleventh Tablet.", "carried out during his absence.", [], None, ()),
    (MACKENZIE, MACKENZIE_TXT, "The Descent of Ishtar", "babylonian-descent-of-ishtar",
     "In one the goddess Ishtar visited Hades", "On a bier place him, and assemble the wake.", [], None, ()),
    (MACKENZIE, MACKENZIE_TXT, "Etana and the Eagle", "babylonian-etana",
     "In one fragmentary legend which was preserved", "and the Eagle's body is shattered.", [], None, ()),
    (JASTROW, JASTROW_TXT, "The Legend of Adapa", "babylonian-adapa",
     "The beginning of the story, as in the case of the Zu myth", "for the tablet here comes to an end.",
     [], JASTROW_KEEP, ()),
]


def find(text, phrase, pos=0):
    m = re.compile(r"\s+".join(map(re.escape, phrase.split()))).search(text, pos)
    if not m:
        raise SystemExit(f"not found: {phrase!r}")
    return m.span()


def passage(text, first, last):
    start = find(text, first)[0]
    return text[start:find(text, last, start)[1]]


def clean(t):
    t = re.sub(r"\s*\[(?:FN#)?\d+\]", "", t)  # footnote markers
    t = re.sub(r"_([^_]+)_", r"\1", t)  # italics
    return re.sub(r"\s+([,.;:!?])", r"\1", re.sub(r"\s+", " ", t)).strip()


def indented_verse(lines):
    """Indented lines; a deeper indent continues the line above."""
    indent = len(lines[0]) - len(lines[0].lstrip())
    verse = []
    for line in lines:
        if verse and len(line) - len(line.lstrip()) > indent:
            verse[-1] += " " + line.strip()
        else:
            verse.append(line.strip())
    return verse


def numbered_verse(lines):
    """Numbered lines without their numbers; an unnumbered line continues the line above unless it
    opens with a quotation mark (Budge prints some repeated lines unnumbered)."""
    verse = []
    for line in lines:
        if re.match(r"\s*\d+[O0-9]*\.\s", line):
            verse.append(re.sub(r"^\s*\d+[O0-9]*\.\s+", "", line))
        elif line.strip().startswith('"'):
            verse.append(line.strip())
        else:
            verse[-1] += " " + line.strip()
    return verse


def quotes_once(verse):
    """Budge opens every line of a speech with a quotation mark; keep only the speech's first."""
    out, inside = [], False
    for line in verse:
        if inside and line.startswith('"'):
            line = line[1:]
        inside ^= line.count('"') % 2 == 1
        out.append(line)
    return out


def blocks_of(raw, keep, skip):
    blocks = []
    for para in re.split(r"\n\s*\n", raw.replace("\r\n", "\n")):
        lines = [line for line in para.split("\n") if line.strip()]
        if not lines:
            continue
        first = lines[0].strip()
        if first.startswith(("[Illustration", "[Footnote")):
            continue
        text = clean(" ".join(lines))
        if keep is not None and not text.startswith(keep):
            continue
        if text.startswith(skip):
            continue
        if re.match(r"\d+\.\s", first):  # numbered lines of a translation
            verse = quotes_once([clean(v) for v in numbered_verse(lines)])
            blocks.append({"type": "verse", "text": "\n".join(verse)})
        elif re.fullmatch(r"\[[^\]]*\]", text):
            inner = text[1:-1].rstrip(".")
            blocks.append({"type": "note" if inner.startswith("Lines") else "heading", "text": inner})
        elif re.fullmatch(r"The \w+ Tablet\.?", text):
            blocks.append({"type": "heading", "text": text.rstrip(".")})
        elif all(line.startswith("  ") for line in lines) and len(lines) > 1 and keep is None:
            verse = quotes_once([clean(v) for v in indented_verse(lines)])
            blocks.append({"type": "verse", "text": "\n".join(verse)})
        elif text[0].islower() and blocks and blocks[-1]["type"] == "p" and blocks[-1]["text"][-1] not in '.!?:"':
            blocks[-1]["text"] += " " + text  # a sentence the e-text breaks with a blank line
        else:
            blocks.append({"type": "p", "text": text.replace(DELUGE_CUT.strip() + " ", "")})
    return blocks


def main(src):
    index = load_index()
    by_collection = {}
    for col, (file, enc), title, work_id, first, last, flags, keep, skip in STORIES:
        text = (Path(src) / file).read_bytes().decode(enc)
        blocks = blocks_of(passage(text, first, last), keep, skip)
        stories = by_collection.setdefault(col["id"], (col, []))[1]
        if title is None:
            prev = stories.pop()
            prev["blocks"] += [{"type": "note", "text": work_id}, *blocks]
            stories.append(finish(prev))
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        stories.append(finish({"id": f"{col['id']}--{slug}", "collectionId": col["id"], "order": len(stories) + 1,
                               "title": title, "origin": None, "excluded": False, "flags": flags, "moral": None,
                               "blocks": blocks, "workId": work_id}))
    for col, stories in by_collection.values():
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:62} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
