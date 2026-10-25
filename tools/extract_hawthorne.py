#!/usr/bin/env python3
"""Hawthorne's Greek myth books for children, from their Gutenberg mirrors.

    git clone --depth 1 https://github.com/GITenberg/Tanglewood-Tales_976.git src/Tanglewood-Tales_976
    python3 tools/extract_hawthorne.py src

Each story is an <h2> section. The introductory frame story ("The Wayside") is left out;
Hawthorne's six myths stand on their own. Writes the `hawthorne-tanglewood` collection.
"""
import re
import sys
from pathlib import Path

import warnings

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

sys.path.insert(0, str(Path(__file__).parent))
from build_compendium import clean, slug, title_case  # noqa: E402
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

BOOKS = [
    {
        "dir": "Tanglewood-Tales_976",
        "collection": {
            "id": "hawthorne-tanglewood",
            "title": "Tanglewood Tales",
            "author": "Nathaniel Hawthorne",
            "contributor": None,
            "firstPublished": 1853,
            "source": "https://www.gutenberg.org/ebooks/976",
            "license": "Public domain in the USA",
            "language": "en",
            "originalLanguage": "en",
        },
        "skip": {"TANGLEWOOD TALES", "BY NATHANIEL HAWTHORNE", "CONTENTS", "THE WAYSIDE. INTRODUCTORY."},
        "workIds": {
            "the-minotaur": "greek-theseus",
            "the-pygmies": "greek-heracles-antaeus",
            "the-dragon-s-teeth": "greek-cadmus",
            "circe-s-palace": "greek-odysseus-circe",
            "the-pomegranate-seeds": "greek-persephone",
            "the-golden-fleece": "greek-jason",
        },
    },
]


def stories_of(html, skip):
    soup = BeautifulSoup(html.read_text(encoding="utf-8", errors="replace"), "lxml")
    for x in soup.select("span.pagenum, pre"):
        x.decompose()
    out, cur = [], None
    for el in soup.body.find_all(["h1", "h2", "p"]):
        text = clean(el.get_text(" "))
        if not text:
            continue
        if el.name in ("h1", "h2"):
            cur = None
            if text.upper() in skip:
                continue
            cur = {"title": title_case(text), "blocks": []}
            out.append(cur)
        elif cur is not None:
            text = re.sub(r"\s+([,.;:!?’”])", r"\1", text)
            cur["blocks"].append({"type": "p", "text": text})
    return out


def main(src):
    index = load_index()
    for book in BOOKS:
        coll = book["collection"]
        html = next((Path(src) / book["dir"]).glob("*-h/*.htm"))
        stories = []
        for i, s in enumerate(stories_of(html, book["skip"]), 1):
            key = slug(s["title"])
            sid = f"{coll['id']}--{key}"
            story = {
                "id": sid,
                "collectionId": coll["id"],
                "order": i,
                "title": s["title"],
                "origin": None,
                "excluded": False,
                "flags": [],
                "moral": None,
                "blocks": s["blocks"],
                "workId": book["workIds"][key],
            }
            stories.append(finish(story))
        upsert_collection(index, coll, stories)
        for st in stories:
            print(f"{st['id']:55} {st['wordCount']:6} words {st['readingMinutes']:3} min  {st['readingLevel']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
