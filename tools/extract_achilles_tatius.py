#!/usr/bin/env python3
"""Phoenician legend: how a shepherd's dog found the purple dye of Tyre, from Achilles Tatius's
Clitopho and Leucippe, Book II, in Rowland Smith's translation (Bohn's Classical Library, 1855).

    git clone --depth 1 https://github.com/GITenberg/The-Greek-Romances-of-Heliodorus-Longus-and-Achilles-Tatius-Ethiopics-Daphne-and-Chloe-Clitop__55406.git src/The-Greek-Romances-of-Heliodorus-Longus-and-Achilles-Tatius-Ethiopics-Daphne-and-Chloe-Clitop__55406
    python3 tools/extract_achilles_tatius.py src

The legend is a digression in the middle of one paragraph, from "The purple of the dress" to
"the treasure-house of dye."; a note says where it comes from. Footnote markers are dropped.
Writes `smith-achilles-tatius`.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

SMITH = {"id": "smith-achilles-tatius", "title": "Clitopho and Leucippe", "author": "Achilles Tatius",
         "contributor": "Translated by Rowland Smith", "firstPublished": 1855,
         "source": "https://www.gutenberg.org/ebooks/55406", "license": "Public domain in the USA",
         "language": "en", "originalLanguage": "el"}
FILE = "The-Greek-Romances-of-Heliodorus-Longus-and-Achilles-Tatius-Ethiopics-Daphne-and-Chloe-Clitop__55406/55406-0.txt"
NOTE = ("From the second book of Achilles Tatius's novel, written in Greek in the second century AD. "
        "Clitopho, who tells the story, is describing the purple of a wedding robe.")
FIRST, LAST = "The purple of the dress was of no ordinary dye", "he arrived at the treasure-house of dye."


def find(text, phrase, pos=0):
    """Finds a phrase whatever the line breaks inside it; returns (start, end)."""
    m = re.compile(r"\s+".join(map(re.escape, phrase.split()))).search(text, pos)
    if not m:
        raise SystemExit(f"not found: {phrase!r}")
    return m.span()


def main(src):
    text = (Path(src) / FILE).read_text(encoding="utf-8-sig")
    start = find(text, FIRST)[0]
    end = find(text, LAST, start)[1]
    para = re.sub(r"\[\d+\]", "", re.sub(r"\s+", " ", text[start:end])).strip()
    blocks = [{"type": "note", "text": NOTE}, {"type": "p", "text": para}]
    st = finish({"id": "smith-achilles-tatius--the-shepherds-dog-and-the-purple-dye", "collectionId": SMITH["id"],
                 "order": 1, "title": "The Shepherd's Dog and the Purple Dye", "origin": None, "excluded": False,
                 "flags": [], "moral": None, "blocks": blocks, "workId": "tyrian-purple-dog"})
    index = load_index()
    upsert_collection(index, SMITH, [st])
    lv = st["readingLevel"]
    print(f"{st['id']:62} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
