#!/usr/bin/env python3
"""West Slavic and Serbian legends: Libussa and the founding of Prague from Count Lützow's The Story
of Prague (1902), and three Prince Marko pieces from Petrovitch's Hero Tales and Legends of the
Serbians (1914).

    git clone --depth 1 https://github.com/GITenberg/The-Story-of-Prague_46533.git src/The-Story-of-Prague_46533
    git clone --depth 1 https://github.com/GITenberg/Hero-Tales-and-Legends-of-the-Serbians_38571.git src/Hero-Tales-and-Legends-of-the-Serbians_38571
    python3 tools/extract_slavic.py src

Lützow's legend is the opening of his first chapter, from "The earliest tales" to the end of his
quotation from Cosmas ("the mistress of all Bohemia"); the two sentences tying Premysl's line to the
reigning Habsburg are cut. Petrovitch's Marko chapter is a run of <h3> sections: a ballad starts at
an all-capitals heading and its mixed-case subsections follow (kept as headings). "Prince Marko and
Sharatz" is his section on the horse, without its paragraph on how many ballads there are.
Petrovitch's colour plates (William Sewell and Gilbert James, whose dates aren't known) are left
out. Footnote markers and page numbers are dropped. Writes `lutzow-prague` and
`petrovitch-serbian`.
"""
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent))
from build_compendium import clean, slug  # noqa: E402
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

LUTZOW = {"id": "lutzow-prague", "title": "The Story of Prague", "author": "Count Lützow",
          "contributor": None, "firstPublished": 1902,
          "source": "https://www.gutenberg.org/ebooks/46533", "license": "Public domain in the USA",
          "language": "en", "originalLanguage": "en"}
PETROVITCH = {"id": "petrovitch-serbian", "title": "Hero Tales and Legends of the Serbians",
              "author": "Woislav M. Petrovitch", "contributor": None, "firstPublished": 1914,
              "source": "https://www.gutenberg.org/ebooks/38571", "license": "Public domain in the USA",
              "language": "en", "originalLanguage": "sr"}

LUTZOW_CUT = (" Premysl became the founder of a line that ruled in Bohemia up to 1306; and the present King"
              " of Bohemia, Francis Joseph, is his successor in the female line.")
# (first <h3>, title, workId, opening words of paragraphs to leave out)
MARKO = [
    ("The Horse Sharatz", "Prince Marko and Sharatz", "serbian-marko-sharatz", ("There are in existence",)),
    ("PRINCE MARKO TELLS WHOSE THE EMPIRE SHALL BE", "Prince Marko Tells Whose the Empire Shall Be",
     "serbian-marko-empire", ()),
    ("PRINCE MARKO AND THE VEELA", "Prince Marko and the Veela", "serbian-marko-veela", ()),
]


def text_of(el):
    return re.sub(r"\s+([,.;:!?’”])", r"\1", clean(el.get_text())).strip()


def story(col, order, title, work_id, blocks):
    return finish({"id": f"{col['id']}--{slug(title)}", "collectionId": col["id"], "order": order,
                   "title": title, "origin": None, "excluded": False, "flags": [], "moral": None,
                   "blocks": blocks, "workId": work_id})


def soup_of(path):
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for x in soup.select("span.pagenum, a.noteref, div.footnotes, div.figure"):
        x.decompose()
    return soup


def lutzow(src):
    soup = soup_of(next((Path(src) / "The-Story-of-Prague_46533").glob("*-h/*.htm")))
    first = next(p for p in soup.find_all("p") if text_of(p).startswith("THE earliest tales"))
    blocks = []
    for p in [first, *first.find_next_siblings("p")]:
        t = re.sub(r"\[\d+\]", "", text_of(p)).replace(LUTZOW_CUT, "")
        if not blocks:  # drop cap: "THE earliest" -> "The earliest"
            t = "The" + t[3:]
        blocks.append({"type": "p", "text": t})
        if t.endswith("mistress of all Bohemia.’"):
            break
    else:
        raise SystemExit("Lützow: end of the Libussa passage not found")
    return [story(LUTZOW, 1, "Libussa and the Founding of Prague", "czech-libuse", blocks)]


def petrovitch(src):
    soup = soup_of(Path(src) / "Hero-Tales-and-Legends-of-the-Serbians_38571" / "38571-h" / "38571-h.htm")
    heads = soup.find_all("h3")
    out = []
    for order, (head_text, title, work_id, skip) in enumerate(MARKO, 1):
        i = next(i for i, h in enumerate(heads) if text_of(h) == head_text)
        blocks = []
        for j, h in enumerate(heads[i:], i):
            name = text_of(h)
            if j > i and (name.isupper() or head_text == "The Horse Sharatz"):
                break
            if j > i:
                blocks.append({"type": "heading", "text": name})
            body = h.find_parent("div", class_="divHead").find_next_sibling("div", class_="divBody")
            for p in body.find_all("p", recursive=False):
                t = text_of(p)
                if t and not t.startswith(skip or ("\0",)):
                    blocks.append({"type": "p", "text": t})
        out.append(story(PETROVITCH, order, title, work_id, blocks))
    return out


def main(src):
    index = load_index()
    for col, stories in ((LUTZOW, lutzow(src)), (PETROVITCH, petrovitch(src))):
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:58} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
