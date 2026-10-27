#!/usr/bin/env python3
"""Arthurian legends: Mrs. Lang's tales in The Book of Romance (1902) and Merlin's first prophecy
from Geoffrey of Monmouth's British History (Thompson's translation, revised by Giles, 1848).

    git clone --depth 1 https://github.com/GITenberg/The-Book-of-Romance_26646.git src/The-Book-of-Romance_26646
    git clone --depth 1 https://github.com/GITenberg/Old-English-Chronicles_37848.git src/Old-English-Chronicles_37848
    python3 tools/extract_arthurian.py src

The Book of Romance, edited by Andrew Lang, is Leonora Blanche Lang's retelling of Malory (her
husband's preface: "All the romances are written by Mrs. Lang"). Each tale is an <h2>; its
paragraphs and H. J. Ford's pictures run to the next <h2>. The Grail quest's numbered sections
(an <h3> numeral, then an <h3> title) become heading blocks, in sentence case (GRAIL_HEADINGS). Captions are all capitals in the
book, so CAPTIONS gives them in sentence case; a plate printed inside the Grail quest that belongs
to a later tale is left out (SKIP_IMAGES).

Geoffrey's story is Book VI, chapters 17-19, and the start of Book VII, chapter 3, cut after the
prophecy of the boar of Cornwall. Writes `lang-romance` and `geoffrey-british-history`.
"""
import re
import sys
import warnings
from pathlib import Path

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from PIL import Image

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
sys.path.insert(0, str(Path(__file__).parent))
from build_compendium import clean, slug  # noqa: E402
from compendium_io import ROOT, finish, load_index, save_index, upsert_collection  # noqa: E402

COMMON = {"license": "Public domain in the USA", "language": "en"}
LANG = {**COMMON, "id": "lang-romance", "title": "The Book of Romance", "author": "Leonora Blanche Lang",
        "contributor": "Edited by Andrew Lang, illustrated by H. J. Ford", "firstPublished": 1902,
        "source": "https://www.gutenberg.org/ebooks/26646", "originalLanguage": "en"}
GEOFFREY = {**COMMON, "id": "geoffrey-british-history", "title": "The British History",
            "author": "Geoffrey of Monmouth", "contributor": "Translated by Aaron Thompson, revised by J. A. Giles",
            "firstPublished": 1848, "source": "https://www.gutenberg.org/ebooks/37848", "originalLanguage": "la"}

# (<h2> text, story title, workId, flags)
LANG_STORIES = [
    ("THE DRAWING OF THE SWORD", "The Drawing of the Sword", "arthurian-sword-in-stone", []),
    ("THE SWORD EXCALIBUR", "The Sword Excalibur", "arthurian-excalibur", []),
    ("HOW THE ROUND TABLE BEGAN", "How the Round Table Began", "arthurian-round-table", []),
    ("WHAT BEAUMAINS ASKED OF THE KING", "What Beaumains Asked of the King", "arthurian-gareth", []),
    ("THE QUEST OF THE HOLY GRAAL", "The Quest of the Holy Graal", "arthurian-grail", ["mature-themes"]),
    ("THE END OF IT ALL", "The End of It All", "arthurian-passing", ["mature-themes"]),
]
CAPTIONS = {
    "image_022": "How Arthur drew the sword",
    "image_032": "Arthur meets the Lady of the Lake and gets the sword Excalibur",
    "image_054": "“Faugh, sir! You smell of the kitchen.” Gareth and Linet",
    "image_066": "Linet and the Black Knight",
    "image_074": "The Lady of Lyonesse sees Sir Gareth",
    "image_092": "Sir Galahad opens the tomb",
    "image_097": "Lancelot at the chapel",
    "image_102": "Sir Percivale slays the serpent",
    "image_110": "How Sir Bors was saved from killing his brother",
    "image_190": "The last battle: Sir Mordred",
    "image_194": "Excalibur returns to the mere",
}
GRAIL_HEADINGS = [
    "How the King went on pilgrimage, and his squire was slain in a dream",
    "The coming of the Holy Graal",
    "The adventure of Sir Galahad",
    "How Sir Lancelot saw a vision, and repented of his sins",
    "The adventure of Sir Percivale",
    "An adventure of Sir Lancelot",
    "An adventure of Sir Gawaine",
    "The adventure of Sir Bors",
    "Adventure of Sir Galahad",
    "Sir Lancelot meets Sir Galahad, and they part for ever",
    "How Sir Galahad found the Graal and died of that finding",
]
SKIP_IMAGES = {"images/image_118.jpg"}  # "Lancelot and the Dwarf" faces a page of the Grail quest
MAX_W, QUALITY = 800, 72


def text_of(el):
    return re.sub(r"\s+([,.;:!?’”])", r"\1", clean(el.get_text())).strip()


def story(col, order, title, work_id, flags, blocks):
    st = {"id": f"{col['id']}--{slug(title)}", "collectionId": col["id"], "order": order,
          "title": title, "origin": None, "excluded": False, "flags": flags, "moral": None,
          "blocks": blocks, "workId": work_id}
    return finish(st)


def save_image(html_dir, src):
    name = f"lang-romance-{Path(src).stem}.webp"
    dst = ROOT / "images" / LANG["id"] / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(html_dir / src).convert("RGB")
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    im.save(dst, "WEBP", quality=QUALITY, method=6)
    return f"images/{LANG['id']}/{name}"


def lang(src):
    path = next((Path(src) / "The-Book-of-Romance_26646").glob("*-h/*.htm"))
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for x in soup.select("span.pagenum, a.fnanchor, div.footnote"):
        x.decompose()
    h2s = soup.find_all("h2")
    out = []
    for order, (head_text, title, work_id, flags) in enumerate(LANG_STORIES, 1):
        head = next(h for h in h2s if clean(h.get_text(" ")).rstrip(".") == head_text)
        blocks, numeral, headings = [], None, iter(GRAIL_HEADINGS)
        for el in head.find_all_next():
            if el.name == "h2":
                break
            if el.name == "h3":
                t = clean(el.get_text(" "))
                if re.fullmatch(r"[IVX]+", t):
                    numeral = t
                else:
                    sub = next(headings)
                    assert sub.lower() == t.lower(), (sub, t)
                    blocks.append({"type": "heading", "text": f"{numeral}. {sub}"})
            elif el.name == "p" and not el.find_parent("div", class_=["figcenter", "poem"]):
                t = text_of(el)
                if t:
                    blocks.append({"type": "p", "text": t})
            elif el.name == "img" and el["src"] not in SKIP_IMAGES:
                alt = CAPTIONS[Path(el["src"]).stem]
                blocks.append({"type": "image", "src": save_image(path.parent, el["src"]), "alt": alt})
        out.append(story(LANG, order, title, work_id, flags, blocks))
    return out


def geoffrey(src):
    path = next((Path(src) / "Old-English-Chronicles_37848").glob("*-h/*.htm"))
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for x in soup.select("span.pagenum, a.fnanchor"):
        x.decompose()
    start = soup.find("h2", string=re.compile("BRITISH HISTORY"))
    book6 = next(h for h in start.find_all_next("h3") if clean(h.get_text()) == "BOOK VI.")
    book7 = next(h for h in book6.find_all_next("h3") if clean(h.get_text()) == "BOOK VII.")

    def chapter(book, numeral):
        return next(h for h in book.find_all_next("h3") if clean(h.get_text(" ")).startswith(f"Chap. {numeral}."))

    blocks = [{"type": "note", "text": "Vortigern has made himself king of Britain by treachery, and the "
               "Saxons he invited over to fight for him have turned against him and seized much of the land."}]
    for numeral in ("XVII", "XVIII", "XIX"):
        h = chapter(book6, numeral)
        for el in h.find_next_siblings():
            if el.name in ("h3", "h2") or "footnotes" in (el.get("class") or []):
                break
            if el.name == "p" and (t := text_of(el)):
                blocks.append({"type": "p", "text": t})
    h = chapter(book7, "III")
    for el in h.find_next_siblings():
        if el.name == "p" and (t := text_of(el)):
            cut = t.find("Six of his posterity")
            blocks.append({"type": "p", "text": t[:cut].strip() if cut > 0 else t})
            if cut > 0:
                break
    blocks.append({"type": "note", "text": "Merlin's prophecy runs on for many pages of riddles about the "
                   "kings to come. It is cut here, after the boar of Cornwall, whom readers have always "
                   "taken to be King Arthur."})
    return [story(GEOFFREY, 1, "Merlin and Vortigern's Tower", "arthurian-merlin-vortigern",
                  ["mature-themes"], blocks)]


def main(src):
    index = load_index()
    for col, stories in ((LANG, lang(src)), (GEOFFREY, geoffrey(src))):
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:58} {st['wordCount']:5}w {st['readingMinutes']:3}m "
                  f"{lv['fkGrade']:5} {lv['band']:8} images={sum(b['type'] == 'image' for b in st['blocks'])}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
