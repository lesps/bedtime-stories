#!/usr/bin/env python3
"""Christian stories: three Gospel passages in the American Standard Version (1901), and the Seven
Sleepers of Ephesus from Jacobus de Voragine's Golden Legend, as Sabine Baring-Gould translates it
in Curious Myths of the Middle Ages (1866).

    git clone --depth 1 --filter=blob:none --no-checkout https://github.com/scrollmapper/bible_databases.git src/bible_databases
    git -C src/bible_databases checkout HEAD -- formats/txt/ASV.txt
    git clone --depth 1 https://github.com/GITenberg/Curious-Myths-of-the-Middle-Ages_36127.git src/Curious-Myths-of-the-Middle-Ages_36127
    python3 tools/extract_christian.py src

The Gospel passages are built as in extract_hebrew_bible.py: a note giving the reference, then one
paragraph per verse, with a heading for each passage when a story has more than one. The Seven
Sleepers is the Golden Legend passage Baring-Gould quotes, without his opening quotation marks or
footnote marker. Writes `asv-1901` (every story marked `livingTradition`) and `baring-gould-myths`.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402
from extract_hebrew_bible import at, parse  # noqa: E402

ASV = {"id": "asv-1901", "title": "The Holy Bible, American Standard Version", "author": "The New Testament",
       "contributor": "Translated by the American Revision Committee", "firstPublished": 1901,
       "source": "https://github.com/scrollmapper/bible_databases/tree/master/sources/en/ASV",
       "license": "Public domain in the USA", "language": "en", "originalLanguage": "el"}
ASV_FILE = "bible_databases/formats/txt/ASV.txt"
LIVING = "Christians"

BARING_GOULD = {"id": "baring-gould-myths", "title": "Curious Myths of the Middle Ages",
                "author": "Sabine Baring-Gould", "contributor": None, "firstPublished": 1866,
                "source": "https://www.gutenberg.org/ebooks/36127", "license": "Public domain in the USA",
                "language": "en", "originalLanguage": "la"}
BARING_GOULD_FILE = "Curious-Myths-of-the-Middle-Ages_36127/36127-0.txt"

# (title, workId, [(book, first "c:v", last "c:v", note before this passage or None)], flags)
GOSPELS = [
    ("The Nativity", "christian-nativity",
     [("Luke", "2:1", "2:20", None), ("Matthew", "2:1", "2:12", None)], []),
    ("The Good Samaritan", "christian-good-samaritan", [("Luke", "10:25", "10:37", None)], []),
    ("The Prodigal Son", "christian-prodigal-son",
     [("Luke", "15:11", "15:32", "Jesus tells this story after the Pharisees and scribes grumble that he "
       "welcomes sinners and eats with them.")],
     ["mature-themes"]),  # the elder son says his brother spent the money "with harlots"
]


def reference(book, first, last):
    (c1, v1), (c2, v2) = at(first), at(last)
    return f"{book} {c1}:{v1}–{v2}" if c1 == c2 else f"{book} {c1}:{v1}–{c2}:{v2}"


def gospel_blocks(books, passages):
    refs = "; ".join(reference(b, f, la) for b, f, la, _ in passages)
    blocks = [{"type": "note", "text": f"{refs}, in the American Standard Version (1901)."}]
    for book, first, last, note in passages:
        if len(passages) > 1:
            blocks.append({"type": "heading", "text": f"{book} {at(first)[0]}"})
        if note:
            blocks.append({"type": "note", "text": note})
        for c, v, text in books[book]:
            if not at(first) <= (c, v) <= at(last):
                continue
            prev = blocks[-1]
            if prev["type"] == "p" and prev["text"][-1] not in ".?!":
                prev["text"] += " " + text  # the sentence runs on into this verse
            else:
                blocks.append({"type": "p", "text": text})
    return blocks


def find(text, phrase, pos=0):
    m = re.compile(r"\s+".join(map(re.escape, phrase.split()))).search(text, pos)
    if not m:
        raise SystemExit(f"not found: {phrase!r}")
    return m.span()


def sleepers_blocks(text):
    start = find(text, "The seven sleepers were natives of Ephesus")[0]
    end = find(text, "till God should raise them again.\"", start)[1]
    blocks = [{"type": "note", "text": "Jacobus de Voragine's telling in The Golden Legend (about 1260). "
                                       "Baring-Gould leaves out a few passages, marked with dots."}]
    for para in re.split(r"\n\s*\n", text[start:end]):
        t = re.sub(r"\s+", " ", para).strip()
        t = re.sub(r'^"|"$', "", re.sub(r"\[\d+\]", "", t))
        blocks.append({"type": "p", "text": t})
    return blocks


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "")).strip("-")


def main(src):
    books = parse((Path(src) / ASV_FILE).read_text(encoding="utf-8"))
    gospels = [finish({"id": f"asv-1901--{slug(title)}", "collectionId": ASV["id"], "order": i, "title": title,
                       "origin": None, "excluded": False, "flags": flags, "moral": None,
                       "blocks": gospel_blocks(books, passages), "workId": work_id, "livingTradition": LIVING})
               for i, (title, work_id, passages, flags) in enumerate(GOSPELS, 1)]
    text = (Path(src) / BARING_GOULD_FILE).read_text(encoding="utf-8-sig")
    sleepers = [finish({"id": "baring-gould-myths--the-seven-sleepers-of-ephesus", "collectionId": BARING_GOULD["id"],
                        "order": 1, "title": "The Seven Sleepers of Ephesus", "origin": None, "excluded": False,
                        "flags": [], "moral": None, "blocks": sleepers_blocks(text), "workId": "seven-sleepers"})]
    index = load_index()
    for col, stories in ((ASV, gospels), (BARING_GOULD, sleepers)):
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:52} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
