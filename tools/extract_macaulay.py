#!/usr/bin/env python3
""""Horatius", from Thomas Babington Macaulay's Lays of Ancient Rome (1842), from its mirror.

    git clone --depth 1 https://github.com/GITenberg/Lays-of-Ancient-Rome_847.git src/Lays-of-Ancient-Rome_847
    python3 tools/extract_macaulay.py src

The poem is one <pre> after Macaulay's prose introduction (not taken). Each numbered stanza
becomes a verse block, without its numeral. The transcription's "Closium" in the first line is
corrected to "Clusium", as the poem spells it everywhere else. Writes the `macaulay-lays`
collection.
"""
import re
import sys
import warnings
from pathlib import Path

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
sys.path.insert(0, str(Path(__file__).parent))
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

DIR = "Lays-of-Ancient-Rome_847"
COLLECTION = {
    "id": "macaulay-lays",
    "title": "Lays of Ancient Rome",
    "author": "Thomas Babington Macaulay",
    "contributor": None,
    "firstPublished": 1842,
    "source": "https://www.gutenberg.org/ebooks/847",
    "license": "Public domain in the USA",
    "language": "en",
    "originalLanguage": "en",
}
NUMERAL = re.compile(r"^\s*[IVXL]+\s*$")


def main(src):
    soup = BeautifulSoup(next((Path(src) / DIR).glob("*-h/*.htm")).read_bytes(), "lxml")
    pre = next(p for p in soup.find_all("pre") if "A Lay Made About" in p.get_text())
    text = pre.get_text().replace("Porsena of Closium", "Porsena of Clusium")
    stanzas, cur = [], None
    for line in text.split("\n"):
        if NUMERAL.match(line):
            cur = []
            stanzas.append(cur)
        elif cur is not None and line.strip():
            cur.append(line.rstrip())
    blocks = []
    for st in stanzas:
        indent = min(len(l) - len(l.lstrip()) for l in st)
        blocks.append({"type": "verse", "text": "\n".join(l[indent:] for l in st)})
    story = finish({
        "id": "macaulay-lays--horatius",
        "collectionId": COLLECTION["id"],
        "order": 1,
        "title": "Horatius",
        "origin": None,
        "excluded": False,
        "flags": [],
        "moral": None,
        "blocks": blocks,
        "workId": "roman-horatius",
    })
    index = load_index()
    upsert_collection(index, COLLECTION, [story])
    save_index(index)
    print(f"{story['id']} {len(blocks)} stanzas {story['wordCount']}w "
          f"{story['readingMinutes']}m {story['readingLevel']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
