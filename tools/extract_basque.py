#!/usr/bin/env python3
"""Basque legend: the Tartaro, the one-eyed giant, from Wentworth Webster's Basque Legends (1877).

    git clone --depth 1 https://github.com/GITenberg/Basque-LegendsWith-an-Essay-on-the-Basque-Language_34902.git src/Basque-LegendsWith-an-Essay-on-the-Basque-Language_34902
    python3 tools/extract_basque.py src

The story is Webster's "M. d'Abbadie's Version", from "In my infancy" to the end of the next
paragraph on other versions ("dashed to pieces and drowned"). Webster's sentence introducing the
narrator becomes a note. Writes `webster-basque`.
"""
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent))
from build_compendium import clean  # noqa: E402
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

WEBSTER = {"id": "webster-basque", "title": "Basque Legends", "author": "Wentworth Webster",
           "contributor": None, "firstPublished": 1877, "source": "https://www.gutenberg.org/ebooks/34902",
           "license": "Public domain in the USA", "language": "en", "originalLanguage": "eu"}
NOTE = ("Webster gives this version as the Abbé Heguiagaray, parish priest of Esquiule in La Soule, "
        "heard it from his mother, and as Antoine d'Abbadie passed it on to the Société des Sciences et "
        "des Arts de Bayonne.")


def text_of(el):
    return re.sub(r"\s+([,.;:!?’”])", r"\1", clean(el.get_text())).strip()


def main(src):
    path = Path(src) / "Basque-LegendsWith-an-Essay-on-the-Basque-Language_34902" / "34902-h" / "34902-h.htm"
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for x in soup.select("span.pagenum, a.noteref, a.fnanchor"):
        x.decompose()
    first = next(p for p in soup.find_all("p") if text_of(p).startswith("In my infancy"))
    blocks = [{"type": "note", "text": NOTE}]
    for p in [first, *first.find_next_siblings("p")]:
        t = re.sub(r"\s*\[\d+\]", "", text_of(p))
        blocks.append({"type": "p", "text": t})
        if t.endswith("dashed to pieces and drowned."):
            break
    else:
        raise SystemExit("Webster: end of the Tartaro tale not found")
    st = finish({"id": "webster-basque--the-tartaro", "collectionId": WEBSTER["id"], "order": 1,
                 "title": "The Tartaro", "origin": None, "excluded": False, "flags": [], "moral": None,
                 "blocks": blocks, "workId": "basque-tartaro"})
    index = load_index()
    upsert_collection(index, WEBSTER, [st])
    lv = st["readingLevel"]
    print(f"{st['id']:40} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
