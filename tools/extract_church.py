#!/usr/bin/env python3
"""Alfred J. Church's Stories from Virgil (1879) and Stories from Livy (1883), from their mirrors.

    git clone --depth 1 https://github.com/GITenberg/Stories-from-Virgil_40622.git src/Stories-from-Virgil_40622
    git clone --depth 1 https://github.com/GITenberg/Stories-from-Livy_24030.git src/Stories-from-Livy_24030
    python3 tools/extract_church.py src

Both books are chapters under <h2> ("CHAPTER VII. ~~ THE STORY OF CORIOLANUS."). A story here
is one chapter, a run of chapters (each chapter's title becomes a heading block), or part of a
chapter cut at the paragraph that starts with a given phrase. Text only: page numbers, the
Pinelli and Flaxman plates and the publishers' lists are left out. Writes the `church-virgil`
and `church-livy` collections. Every chapter of Stories from Virgil is taken; from Livy, only
the stories the expansion plan lists.
"""
import re
import sys
import warnings
from pathlib import Path

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
sys.path.insert(0, str(Path(__file__).parent))
from build_compendium import clean, slug, title_case  # noqa: E402
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

M = ["mature-themes"]
COMMON = {"author": "Alfred J. Church", "license": "Public domain in the USA", "language": "en"}
BOOKS = [
    {
        "dir": "Stories-from-Virgil_40622",
        "collection": {
            **COMMON,
            "id": "church-virgil",
            "title": "Stories from Virgil",
            "contributor": "Retold from Virgil's Aeneid",
            "firstPublished": 1879,
            "source": "https://www.gutenberg.org/ebooks/40622",
            "originalLanguage": "la",
        },
        # (first chapter, last chapter, title, workId, flags[, start phrase, stop phrase])
        "stories": [
            ("I", "III", "The Fall of Troy", "roman-aeneas-troy", M),
            ("IV", "VI", "The Wanderings of Aeneas", "roman-aeneas-wanderings", []),
            ("VII", "IX", "Dido, Queen of Carthage", "roman-dido", M),
            ("X", "XII", "The Funeral Games", "roman-aeneas-games", []),
            ("XIII", "XIV", "The Sibyl and the Dwellings of the Dead", "roman-aeneas-underworld", M),
            ("XV", "XVII", "Aeneas Comes to Latium", "roman-aeneas-latium", []),
            ("XVIII", "XIX", "King Evander and the Arms of Aeneas", "roman-evander", []),
            ("XX", "XX", "Nisus and Euryalus", "roman-nisus-euryalus", M),
            ("XXI", "XXVI", "The War in Latium", "roman-aeneas-war", M),
        ],
    },
    {
        "dir": "Stories-from-Livy_24030",
        "collection": {
            **COMMON,
            "id": "church-livy",
            "title": "Stories from Livy",
            "contributor": "Retold from Livy's History of Rome",
            "firstPublished": 1883,
            "source": "https://www.gutenberg.org/ebooks/24030",
            "originalLanguage": "la",
        },
        "stories": [
            ("I", "I", "The Story of Romulus", "roman-romulus-remus", M, None, "And now it was needful"),
            ("I", "I", "The Story of Numa", "roman-numa-egeria", [], "And now it was needful", None),
            ("VI", "VI", "The Story of Lars Porsenna", "roman-horatius", []),
            ("XIII", "XIV", "Rome and the Gauls", "roman-gauls-capitol", M),
        ],
    },
]
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV",
         "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI"]
CHAPTER = re.compile(r"^CHAPTER ([IVXL]+)\.\s*(?:~~)?\s*(.*?)\.?$")


def chapters(path):
    """{numeral: (title, [paragraph, ...])} up to "THE END."."""
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for x in soup.select("span.pagenum, div.fig, div.figcenter, img"):
        x.decompose()
    out, cur = {}, None
    for el in soup.body.find_all(["h2", "p"]):
        text = clean(el.get_text(" "))
        if text == "THE END.":
            break
        m = CHAPTER.match(text) if el.name == "h2" else None
        if m:
            cur = out.setdefault(m[1], (m[2], []))[1]
        elif el.name == "p" and cur is not None and text:
            cur.append(re.sub(r"\s+([,.;:!?’”])", r"\1", text))
    return out


def story_blocks(chaps, first, last, start=None, stop=None):
    nums = ROMAN[ROMAN.index(first):ROMAN.index(last) + 1]
    # A run of chapters gets their titles as headings, unless it is one story "(continued)".
    titles = [chaps[n][0] for n in nums]
    headed = len({t.replace(" (continued)", "") for t in titles}) > 1
    blocks = []
    for n in nums:
        title, paras = chaps[n]
        if headed:
            blocks.append({"type": "heading", "text": "—".join(map(title_case, title.split("—")))})
        blocks += [{"type": "p", "text": p} for p in paras]
    if start:
        blocks = blocks[next(i for i, b in enumerate(blocks) if b["text"].startswith(start)):]
    if stop:
        blocks = blocks[:next(i for i, b in enumerate(blocks) if b["text"].startswith(stop))]
    return blocks


def main(src):
    index = load_index()
    for book in BOOKS:
        col = book["collection"]
        chaps = chapters(next((Path(src) / book["dir"]).glob("*-h/*.htm")))
        stories = []
        for order, (first, last, title, work_id, flags, *cut) in enumerate(book["stories"], 1):
            stories.append(finish({
                "id": f"{col['id']}--{slug(title)}",
                "collectionId": col["id"],
                "order": order,
                "title": title,
                "origin": None,
                "excluded": False,
                "flags": list(flags),
                "moral": None,
                "blocks": story_blocks(chaps, first, last, *cut),
                "workId": work_id,
            }))
        upsert_collection(index, col, stories)
        for st in stories:
            heads = [b["text"] for b in st["blocks"] if b["type"] == "heading"]
            print(f"{st['id']:52} {st['wordCount']:6}w {st['readingMinutes']:3}m "
                  f"{st['readingLevel']['fkGrade']:5} {st['readingLevel']['band']:8} {heads}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
