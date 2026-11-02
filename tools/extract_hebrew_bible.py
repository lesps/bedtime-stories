#!/usr/bin/env python3
"""Stories from the Hebrew Bible, in the Jewish Publication Society's translation, The Holy
Scriptures According to the Masoretic Text (1917).

    git clone --depth 1 --filter=blob:none --no-checkout https://github.com/scrollmapper/bible_databases.git src/bible_databases
    git -C src/bible_databases checkout HEAD -- formats/txt/JPS.txt
    python3 tools/extract_hebrew_bible.py src

The text file has one verse per line ("[1:3] And ..."), under "### Book" headings. Each story is
one or more verse ranges; a story's blocks are a note giving its reference, then one paragraph per
verse (the numbers dropped; a verse that ends mid-sentence runs on into the next), with a
heading at each new chapter. Where a story skips verses, a note
says what is left out. This digitization writes the divine names reverently as HaShem, G-d and
L-rd; they are restored to the 1917 printing's "the LORD", "God" and "Lord" (FIXES corrects the
digitization's few typos in these passages). Writes `jps-1917`, with every story marked
`livingTradition`.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

JPS = {"id": "jps-1917", "title": "The Holy Scriptures According to the Masoretic Text",
       "author": "The Hebrew Bible", "contributor": "Translated by the Jewish Publication Society",
       "firstPublished": 1917, "source": "https://github.com/scrollmapper/bible_databases/tree/master/sources/en/JPS",
       "license": "Public domain in the USA", "language": "en", "originalLanguage": "he"}
FILE = "bible_databases/formats/txt/JPS.txt"
LIVING = "Jews and Christians"

FIXES = {
    "And be said: 'Jacob.'": "And he said: 'Jacob.'",  # Genesis 32:28
    "the land of Caanan": "the land of Canaan",  # Genesis 42:5
    "the third day. 'This do": "the third day: 'This do",  # Genesis 42:18
    "then will ye bring down my gray hairs with sorrow to the grave.\n":
        "then will ye bring down my gray hairs with sorrow to the grave.'\n",  # Genesis 42:38
    "say: The lord hath not appeared": "say: The LORD hath not appeared",  # Exodus 4:1
    "from serving us?\n": "from serving us?'\n",  # Exodus 14:5
    "'Oh, HaShem, I pray Thee": "'Oh, Lord, I pray Thee",  # Judges 13:8, Adonai
    "wherewith no work, hath been done": "wherewith no work hath been done",  # Judges 16:11
    "to go,but could not": "to go, but could not",  # 1 Samuel 17:39
    "`The one saith": "'The one saith",  # 1 Kings 3:23
    "parted them both assunder": "parted them both asunder",  # 2 Kings 2:11
}

# (title, workId, [(book, first "c:v", last "c:v", note before this range or None)], flags)
STORIES = [
    ("The Creation", "hebrew-creation", [("Genesis", "1:1", "2:3", None)], []),
    ("The Garden of Eden", "hebrew-eden", [("Genesis", "2:4", "3:24", None)], []),
    ("Cain and Abel", "hebrew-cain-abel", [("Genesis", "4:1", "4:16", None)], ["mature-themes"]),
    ("Noah and the Flood", "hebrew-noah", [("Genesis", "6:5", "9:17", None)], []),
    ("The Tower of Babel", "hebrew-babel", [("Genesis", "11:1", "11:9", None)], []),
    ("Jacob's Ladder", "hebrew-jacob-ladder", [("Genesis", "28:10", "28:22", None)], []),
    ("Jacob Wrestles with the Angel", "hebrew-jacob-wrestles",
     [("Genesis", "32:23", "32:33", "Jacob is on his way home to meet his brother Esau, after twenty years away.")], []),
    ("Joseph and His Coat", "hebrew-joseph-1", [("Genesis", "37:1", "37:36", None)], []),
    ("Joseph in Egypt", "hebrew-joseph-2", [("Genesis", "39:1", "41:57", None)], ["mature-themes"]),
    ("Joseph and His Brothers", "hebrew-joseph-3", [("Genesis", "42:1", "45:28", None)], []),
    ("The Baby in the Bulrushes", "hebrew-moses-baby", [("Exodus", "1:8", "2:10", None)], []),
    ("The Burning Bush", "hebrew-burning-bush", [("Exodus", "3:1", "4:17", None)], []),
    ("The Ten Plagues", "hebrew-plagues",
     [("Exodus", "7:8", "11:10", None),
      ("Exodus", "12:29", "12:36", "Chapter 12 begins with the laws of the Passover, left out here.")], []),
    ("Crossing the Red Sea", "hebrew-red-sea", [("Exodus", "14:5", "14:31", None)], []),
    ("Samson", "hebrew-samson", [("Judges", "13:1", "16:31", None)], ["mature-themes"]),
    ("David and Goliath", "hebrew-david-goliath", [("I Samuel", "17:1", "17:51", None)], []),
    ("The Wisdom of Solomon", "hebrew-solomon", [("I Kings", "3:5", "3:28", None)], ["mature-themes"]),
    ("Elijah and the Chariot of Fire", "hebrew-elijah", [("II Kings", "2:1", "2:15", None)], []),
    ("Jonah", "hebrew-jonah", [("Jonah", "1:1", "4:11", None)], []),
    ("Daniel in the Lions' Den", "hebrew-daniel", [("Daniel", "6:2", "6:29", None)], []),
]

BOOK_NAMES = {"I Samuel": "1 Samuel", "I Kings": "1 Kings", "II Kings": "2 Kings"}


def parse(text):
    books, book = {}, None
    for line in text.splitlines():
        if line.startswith("### "):
            book = books.setdefault(line[4:].strip(), [])
        elif m := re.match(r"\[(\d+):(\d+)\] (.*)", line):
            book.append((int(m[1]), int(m[2]), m[3].strip()))
    return books


def restore(verse):
    """The 1917 printing's divine names, in place of this digitization's reverent forms."""
    verse += "\n"  # so a fix can match the end of a verse
    for a, b in FIXES.items():
        verse = verse.replace(a, b)
    verse = re.sub(r"\bO HaShem\b", "O LORD", verse.rstrip("\n"))
    verse = re.sub(r"\b([Tt])he HaShem\b", r"\1he LORD", verse)
    verse = re.sub(r"\bHaShem\b", "the LORD", verse)
    verse = re.sub(r"(^|[.!?:]\s+|['\"(]\s*)the LORD", lambda m: m[1] + "The LORD", verse)
    return verse.replace("G-d", "God").replace("L-rd", "Lord")


def at(ref):
    c, v = ref.split(":")
    return int(c), int(v)


def reference(book, first, last):
    name = BOOK_NAMES.get(book, book)
    (c1, v1), (c2, v2) = at(first), at(last)
    return f"{name} {c1}:{v1}–{v2}" if c1 == c2 else f"{name} {c1}:{v1}–{c2}:{v2}"


def blocks_of(books, ranges):
    refs = "; ".join(reference(b, f, la) for b, f, la, _ in ranges)
    blocks = [{"type": "note", "text": f"{refs}, in the Jewish Publication Society's translation (1917)."}]
    multi = len({c for b, f, la, _ in ranges for c in range(at(f)[0], at(la)[0] + 1)}) > 1
    for book, first, last, note in ranges:
        if note:
            blocks.append({"type": "note", "text": note})
        chapter = None
        for c, v, text in books[book]:
            if not at(first) <= (c, v) <= at(last):
                continue
            if multi and c != chapter:
                blocks.append({"type": "heading", "text": f"{BOOK_NAMES.get(book, book)} {c}"})
            text = restore(text)
            prev = blocks[-1]
            if prev["type"] == "p" and c == chapter and prev["text"].rstrip("-")[-1] not in ".?!'\"":
                prev["text"] += " " + text  # the sentence runs on into this verse
            else:
                blocks.append({"type": "p", "text": text})
            chapter = c
    return blocks


def main(src):
    books = parse((Path(src) / FILE).read_text(encoding="utf-8"))
    stories = []
    for i, (title, work_id, ranges, flags) in enumerate(STORIES, 1):
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "")).strip("-")
        stories.append(finish({"id": f"jps-1917--{slug}", "collectionId": JPS["id"], "order": i, "title": title,
                               "origin": None, "excluded": False, "flags": flags, "moral": None,
                               "blocks": blocks_of(books, ranges), "workId": work_id,
                               "livingTradition": LIVING}))
    index = load_index()
    upsert_collection(index, JPS, stories)
    for st in stories:
        lv = st["readingLevel"]
        print(f"{st['id']:52} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
