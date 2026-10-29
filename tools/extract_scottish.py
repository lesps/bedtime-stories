#!/usr/bin/env python3
"""Scottish and Manx legends: Grierson's Scottish Fairy Book (1910) and Morrison's Manx Fairy Tales (1911).

    git clone --depth 1 https://github.com/GITenberg/The-Scottish-Fairy-Book_37532.git src/The-Scottish-Fairy-Book_37532
    git clone --depth 1 https://github.com/GITenberg/Manx-Fairy-Tales_51762.git src/Manx-Fairy-Tales_51762
    python3 tools/extract_scottish.py src

In Elizabeth W. Grierson's book each tale is an <h2>; its paragraphs and rhymes (div.stanza, one
span per line) run to the next <h2>. Morris Meredith Williams's pictures are left out: he died in
1973, so they are not public domain everywhere. In Sophia Morrison's book each tale is a div.tale with an <h2>
heading; rhymes are div.lgouter, one p.line per line. Writes `grierson-scottish` and
`morrison-manx`.
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

COMMON = {"license": "Public domain in the USA", "language": "en", "originalLanguage": "en"}
GRIERSON = {**COMMON, "id": "grierson-scottish", "title": "The Scottish Fairy Book",
            "author": "Elizabeth W. Grierson", "contributor": None,
            "firstPublished": 1910, "source": "https://www.gutenberg.org/ebooks/37532"}
MORRISON = {**COMMON, "id": "morrison-manx", "title": "Manx Fairy Tales", "author": "Sophia Morrison",
            "contributor": None, "firstPublished": 1911, "source": "https://www.gutenberg.org/ebooks/51762"}

# (<h2> text, story title, workId)
GRIERSON_STORIES = [
    ("THOMAS THE RHYMER", "Thomas the Rhymer", "scottish-thomas-rhymer"),
    ("THE SEAL CATCHER AND THE MERMAN", "The Seal Catcher and the Merman", "scottish-selkie"),
    ("ASSIPATTLE AND THE MESTER STOORWORM", "Assipattle and the Mester Stoorworm", "scottish-stoorworm"),
]
MORRISON_STORIES = [
    ("THE MAKING OF MANN", "The Making of Mann", "manx-making-of-mann"),
    ("THE COMING OF SAINT PATRICK", "The Coming of Saint Patrick", "manx-manannan-mist"),
]


def text_of(el):
    return re.sub(r"\s+([,.;:!?’”])", r"\1", clean(el.get_text())).strip()


def story(col, order, title, work_id, blocks):
    st = {"id": f"{col['id']}--{slug(title)}", "collectionId": col["id"], "order": order,
          "title": title, "origin": None, "excluded": False, "flags": [], "moral": None,
          "blocks": blocks, "workId": work_id}
    return finish(st)



def grierson(src):
    path = next((Path(src) / "The-Scottish-Fairy-Book_37532").glob("*-h/*.htm"))
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for x in soup.select("span.pagenum, a.fnanchor"):
        x.decompose()
    h2s = soup.find_all("h2")
    out = []
    for order, (head_text, title, work_id) in enumerate(GRIERSON_STORIES, 1):
        head = next(h for h in h2s if clean(h.get_text(" ")) == head_text)
        blocks = []
        for el in head.find_all_next():
            if el.name == "h2":
                break
            cls = el.get("class") or []
            if el.name == "p" and not el.find_parent("div", class_=["poem", "figcenter"]):
                t = text_of(el)
                if t:
                    blocks.append({"type": "p", "text": t})
            elif el.name == "div" and "stanza" in cls:
                lines = [clean(s.get_text()) for s in el.find_all("span")]
                blocks.append({"type": "verse", "text": "\n".join(line for line in lines if line)})
        out.append(story(GRIERSON, order, title, work_id, blocks))
    return out


def morrison(src):
    path = next((Path(src) / "Manx-Fairy-Tales_51762").glob("*-h/*.htm"))
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for x in soup.select("span.pagenum"):
        x.decompose()
    out = []
    for order, (head_text, title, work_id) in enumerate(MORRISON_STORIES, 1):
        head = next(h for h in soup.find_all("h2") if clean(h.get_text(" ")) == head_text)
        body = head.find_parent("div", class_="tale").find("div", class_="divBody")
        blocks = []
        for el in body.find_all(["p", "div"]):
            cls = el.get("class") or []
            if el.name == "div" and "lgouter" in cls:
                lines = [text_of(line) for line in el.find_all("p", class_="line")]
                blocks.append({"type": "verse", "text": "\n".join(line for line in lines if line)})
            elif el.name == "p" and "line" not in cls:
                t = text_of(el)
                if t:
                    blocks.append({"type": "p", "text": t})
        out.append(story(MORRISON, order, title, work_id, blocks))
    return out


def main(src):
    index = load_index()
    for col, stories in ((GRIERSON, grierson(src)), (MORRISON, morrison(src))):
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:62} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
