#!/usr/bin/env python3
"""Hesiod's Theogony and four Homeric Hymns, in Hugh G. Evelyn-White's translation (1914).

    git clone --depth 1 https://github.com/GITenberg/Hesiod-the-Homeric-Hymns-and-Homerica_348.git \\
        src/Hesiod-the-Homeric-Hymns-and-Homerica_348
    python3 tools/extract_hesiod.py src

Each poem is an <h2> ("IV. TO HERMES (582 lines)") followed by prose paragraphs, each opening
with its line numbers ("(ll. 1-29)"). The line numbers and footnote markers are dropped, and so
are the translator's endnotes; gaps in the Greek text ("((LACUNA))") are marked in plain words.
The Hymn to Apollo's two halves ("To Delian Apollo", "To Pythian Apollo") become heading blocks.
Writes the `hesiod-hymns` collection.
"""
import re
import sys
import warnings
from pathlib import Path

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
sys.path.insert(0, str(Path(__file__).parent))
from build_compendium import clean, slug  # noqa: E402
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

DIR = "Hesiod-the-Homeric-Hymns-and-Homerica_348"
COLLECTION = {
    "id": "hesiod-hymns",
    "title": "Hesiod and the Homeric Hymns",
    "author": "Hesiod and the Homeric poets",
    "contributor": "Translated by Hugh G. Evelyn-White",
    "firstPublished": 1914,
    "source": "https://www.gutenberg.org/ebooks/348",
    "license": "Public domain in the USA",
    "language": "en",
    "originalLanguage": "el",
}
M = ["mature-themes"]
POEMS = [  # (start of the <h2> text, title, workId, flags)
    ("THE THEOGONY", "The Theogony", "greek-theogony", M),
    ("II. TO DEMETER", "Hymn to Demeter", "greek-persephone", []),
    ("III. TO APOLLO", "Hymn to Apollo", "greek-apollo-delphi", []),
    ("IV. TO HERMES", "Hymn to Hermes", "greek-hermes-cattle", []),
    ("VII. TO DIONYSUS", "Hymn to Dionysus", "greek-dionysus-pirates", []),
]
LINES = re.compile(r"^\(ll?\.?\s*[\dA-Za-z,\s\-–]+\)\s*")
LACUNA = re.compile(r"\s*\.*\s*\(\(LACUNA\)\)\s*\.*\s*")
PART = re.compile(r"^TO (DELIAN|PYTHIAN) APOLLO\W*$")


def main(src):
    html = next((Path(src) / DIR).glob("*-h/*.htm"))
    soup = BeautifulSoup(html.read_bytes(), "lxml")
    for a in soup.select('a[href^="#linknote-"]'):
        a.decompose()
    found, cur = [], None
    for el in soup.body.find_all(["h2", "h3", "p"]):
        text = clean(el.get_text(" "))
        if el.name == "h2":
            poem = next((p for p in POEMS if text.startswith(p[0])), None)
            cur = {"poem": poem, "blocks": []} if poem else None
            if cur:
                found.append(cur)
        elif cur is None or not text:
            continue
        elif PART.match(text):
            cur["blocks"].append({"type": "heading", "text": f"To {PART.match(text)[1].title()} Apollo"})
        elif text == "((LACUNA))":
            cur["blocks"].append({"type": "note", "text": "Some lines of the poem are lost here."})
        elif el.name == "p":
            text = LACUNA.sub(" … [some lines are lost] … ", LINES.sub("", text))
            cur["blocks"].append({"type": "p", "text": re.sub(r"\s+([,.;:!?’”])", r"\1", text)})
    if len(found) != len(POEMS):
        raise SystemExit(f"found {len(found)} of {len(POEMS)} poems")
    stories = []
    for order, s in enumerate(found, 1):
        _, title, work_id, flags = s["poem"]
        stories.append(finish({
            "id": f"{COLLECTION['id']}--{slug(title)}",
            "collectionId": COLLECTION["id"],
            "order": order,
            "title": title,
            "origin": None,
            "excluded": False,
            "flags": list(flags),
            "moral": None,
            "blocks": s["blocks"],
            "workId": work_id,
        }))
    index = load_index()
    upsert_collection(index, COLLECTION, stories)
    save_index(index)
    for st in stories:
        print(f"{st['id']:32} {st['wordCount']:6}w {st['readingMinutes']:3}m {st['readingLevel']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
