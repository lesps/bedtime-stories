#!/usr/bin/env python3
"""Russian tales: Ralston's Russian Fairy Tales (1873), Curtin's Myths and Folk-Tales of the
Russians (1890) and Magnus's translation of Afanasyev's Russian Folk-Tales (1915).

    git clone --depth 1 https://github.com/GITenberg/Russian-Fairy-Tales--A-Choice-Collection-of-Muscovite-Folk-lore_22373.git src/Russian-Fairy-Tales--A-Choice-Collection-of-Muscovite-Folk-lore_22373
    git clone --depth 1 https://github.com/GITenberg/Myths-and-Folk-tales-of-the-Russians-Western-Slavs-and-Magyars_50011.git src/Myths-and-Folk-tales-of-the-Russians-Western-Slavs-and-Magyars_50011
    git clone --depth 1 https://github.com/standardebooks/a-n-afanasyev_russian-folktales_leonard-a-magnus.git src/a-n-afanasyev_russian-folktales_leonard-a-magnus
    python3 tools/extract_russian.py src

Ralston embeds each tale (an <h4>) in his own commentary, so a tale runs from its heading to the
first paragraph of commentary (RALSTON_STORIES gives that paragraph's opening words). His bracketed
summary of the end of "Vasilissa the Fair" is kept. Curtin's tales are <h3>s; two share the title
"Koshchéi Without-Death", and the first (the one with the death hidden in an egg) is used. Its
first letter is a drop cap, set back into the word. Magnus is read from the Standard Ebooks
edition, one file per tale. Footnote markers, and Curtin's "Go to notes" links, are dropped. The
Firebird and Márya Moryévna are flagged `mature-themes`: in both the hero is cut to pieces before
being brought back to life. Writes `ralston-russian`, `curtin-russian` and `magnus-russian`.
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

COMMON = {"license": "Public domain in the USA", "language": "en", "originalLanguage": "ru"}
RALSTON = {**COMMON, "id": "ralston-russian", "title": "Russian Fairy Tales", "author": "Traditional (Russian)",
           "contributor": "Translated by W. R. S. Ralston", "firstPublished": 1873,
           "source": "https://www.gutenberg.org/ebooks/22373"}
CURTIN = {**COMMON, "id": "curtin-russian", "title": "Myths and Folk-Tales of the Russians",
          "author": "Traditional (Russian)", "contributor": "Translated by Jeremiah Curtin", "firstPublished": 1890,
          "source": "https://www.gutenberg.org/ebooks/50011"}
MAGNUS = {**COMMON, "id": "magnus-russian", "title": "Russian Folk-Tales", "author": "Aleksandr Afanasyev",
          "contributor": "Translated by Leonard A. Magnus", "firstPublished": 1915,
          "source": "https://standardebooks.org/ebooks/a-n-afanasyev/russian-folktales/leonard-a-magnus"}

# (<h4> text, title, workId, first words of the commentary that follows the tale)
RALSTON_STORIES = [
    ("Vasilissa the Fair.", "Vasilissa the Fair", "russian-vasilisa", "The puppet which plays"),
    ("Frost.", "Frost", "russian-morozko", "In a variant from the Kursk"),
]
# (<h3> text, which occurrence, title, workId)
CURTIN_STORIES = [
    ("IVAN TSAREVICH, THE FIRE-BIRD, AND THE GRAY WOLF.", 0, "Ivan Tsarevich, the Fire-Bird, and the Gray Wolf",
     "russian-firebird"),
    ("KOSHCHÉI WITHOUT-DEATH.", 0, "Koshchéi Without-Death", "russian-koshchei"),
]
# (Standard Ebooks file, title, workId)
MAGNUS_STORIES = [
    ("marya-moryevna", "Márya Moryévna", "russian-marya-morevna"),
    ("the-story-of-the-brave-and-doughty-knight-ilya-muromets-and-the-nightingale-robber",
     "Ilya Muromets and the Nightingale Robber", "russian-ilya-nightingale"),
]


# workIds of the tales flagged mature-themes (their retellings set `flags: none`)
MATURE = {"russian-firebird", "russian-marya-morevna"}


def text_of(el):
    return re.sub(r"\s+([,.;:!?’”])", r"\1", clean(el.get_text())).strip()


def story(col, order, title, work_id, blocks):
    st = {"id": f"{col['id']}--{slug(title)}", "collectionId": col["id"], "order": order,
          "title": title, "origin": None, "excluded": False,
          "flags": ["mature-themes"] if work_id in MATURE else [], "moral": None,
          "blocks": blocks, "workId": work_id}
    return finish(st)


def ralston(src):
    path = next((Path(src) / "Russian-Fairy-Tales--A-Choice-Collection-of-Muscovite-Folk-lore_22373").glob("*-h/*.htm"))
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for x in soup.select("span.pagenum, a.fnanchor"):
        x.decompose()
    out = []
    for order, (head_text, title, work_id, stop) in enumerate(RALSTON_STORIES, 1):
        head = next(h for h in soup.find_all("h4") if clean(h.get_text(" ")).startswith(head_text))
        blocks = []
        for el in head.find_all_next("p"):
            t = text_of(el)
            if t.startswith(stop):
                break
            if t:
                blocks.append({"type": "p", "text": t})
        out.append(story(RALSTON, order, title, work_id, blocks))
    return out


def curtin(src):
    path = next((Path(src) / "Myths-and-Folk-tales-of-the-Russians-Western-Slavs-and-Magyars_50011").glob("*-h/*.htm"))
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for x in soup.select("span.pagenum, a.fnanchor, div.footnote"):
        x.decompose()
    out = []
    for order, (head_text, nth, title, work_id) in enumerate(CURTIN_STORIES, 1):
        head = [h for h in soup.find_all("h3") if clean(h.get_text(" ")) == head_text][nth]
        blocks = []
        for el in head.find_all_next():
            if el.name in ("h2", "h3"):
                break
            if el.name == "p" and (t := text_of(el)) and t != "Go to notes":
                if not blocks:  # "IT happened" -> "It happened"
                    t = re.sub(r"^([A-Z])([A-Z]+)\b", lambda m: m.group(1) + m.group(2).lower(), t)
                blocks.append({"type": "p", "text": t})
        out.append(story(CURTIN, order, title, work_id, blocks))
    return out


def magnus(src):
    root = Path(src) / "a-n-afanasyev_russian-folktales_leonard-a-magnus" / "src" / "epub" / "text"
    out = []
    for order, (name, title, work_id) in enumerate(MAGNUS_STORIES, 1):
        soup = BeautifulSoup((root / f"{name}.xhtml").read_bytes(), "lxml")
        for x in soup.select('a[epub\\:type="noteref"], a[href*="endnotes"]'):
            x.decompose()
        blocks = [{"type": "p", "text": t} for p in soup.find("article").find_all("p") if (t := text_of(p))]
        out.append(story(MAGNUS, order, title, work_id, blocks))
    return out


def main(src):
    index = load_index()
    for col, stories in ((RALSTON, ralston(src)), (CURTIN, curtin(src)), (MAGNUS, magnus(src))):
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:58} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
