#!/usr/bin/env python3
"""James Baldwin's The Story of Siegfried (1882) and Fifty Famous Stories Retold (1896).

    git clone --depth 1 https://github.com/GITenberg/The-Story-of-Siegfried_6866.git src/The-Story-of-Siegfried_6866
    git clone --depth 1 https://github.com/GITenberg/Fifty-Famous-Stories-Retold_18442.git src/Fifty-Famous-Stories-Retold_18442
    python3 tools/extract_baldwin.py src

The Story of Siegfried is twenty "Adventures" under <h2>. Nine are taken: the forging of
Balmung, Greyfell, the curse of Andvari's gold, Fafnir, Brunhild, the Nibelung hoard, the
wooing of Brunhild for Gunther, Siegfried's death and the hoard sunk in the Rhine (with
Baldwin's After Word). The rest are Baldwin's digressions into other Norse myths and the
Burgundian court; where a chapter depends on them, a note block says what happened in between.
Endnote markers ("[EN#4]") are dropped and the endnotes left out. Writes `baldwin-siegfried`.

Fifty Famous Stories Retold prints each story under <h2>, with long words hyphenated into
syllables for young readers ("Swit-zer-land"); the hyphens are removed, except in the words in
KEEP_HYPHENS. Only the stories the expansion plan lists so far are taken, with their pictures.
Writes `baldwin-fifty-famous`.
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

M = ["mature-themes"]
COMMON = {"author": "James Baldwin", "license": "Public domain in the USA", "language": "en"}
SIEGFRIED = {
    **COMMON,
    "id": "baldwin-siegfried",
    "title": "The Story of Siegfried",
    "contributor": "Retold from the Nibelungenlied, the Völsunga saga and the Eddas",
    "firstPublished": 1882,
    "source": "https://www.gutenberg.org/ebooks/6866",
    "originalLanguage": "de",
}
FIFTY = {
    **COMMON,
    "id": "baldwin-fifty-famous",
    "title": "Fifty Famous Stories Retold",
    "contributor": None,
    "firstPublished": 1896,
    "source": "https://www.gutenberg.org/ebooks/18442",
    "originalLanguage": "en",
}

# (chapter number, title, workId, flags, note placed first or None)
ADVENTURES = [
    ("I", "Mimer, the Master", "german-siegfried-sword", [], None),
    ("II", "Greyfell", "german-siegfried-greyfell", [], None),
    ("III", "The Curse of Gold", "german-andvari-gold", [], None),
    ("IV", "Fafnir, the Dragon", "norse-sigurd-fafnir", [], None),
    ("VI", "Brunhild", "german-siegfried-brunhild", [], (
        "In the chapter before this one, Bragi's ship carries Siegfried north, past the kingdom "
        "of Aegir, the sea-king, to a strange and silent land.")),
    ("VII", "In Nibelungen Land", "german-nibelung-hoard", [], None),
    ("XIV", "How Gunther Outwitted Brunhild", "german-gunther-brunhild", [], (
        "In the chapters before this one, Siegfried goes home to Santen and then rides to Worms, "
        "in Burgundy, where King Gunther, his brothers Gernot and Giselher, their mother Ute and "
        "their sister Kriemhild make him welcome. He stays for a year, through the spring games "
        "and a war against the North-kings, until the midwinter feast.")),
    ("XIX", "How They Hunted in the Odenwald", "german-siegfried-death", M, (
        "In the chapters before this one, Gunther marries Brunhild, and Siegfried marries "
        "Kriemhild and takes her home to the Nibelungen Land. Later Gunther invites them to a "
        "feast at Worms. Brunhild, jealous of Kriemhild, learns that she was tricked, and Hagen "
        "persuades Gunther that Siegfried means to seize his kingdom. Pretending to want to "
        "guard Siegfried in battle, Hagen learns from Kriemhild that when Siegfried bathed in "
        "the dragon's blood a linden leaf fell between his shoulders, leaving one spot where he "
        "can be wounded; she sews a silk leaf on his coat to mark it. Hagen then has false "
        "heralds announce a war, and calls it off.")),
    ("XX", "How the Hoard Was Brought to Burgundy", "german-nibelung-rhine", [], None),
]
FIFTY_STORIES = [
    ("THE STORY OF WILLIAM TELL", "The Story of William Tell", "swiss-william-tell", []),
    ("ARNOLD WINKELRIED", "Arnold Winkelried", "swiss-winkelried", []),
]
KEEP_HYPHENS = {"to-day", "to-morrow", "to-night"}
ENDNOTE = re.compile(r"\s*\[EN#\d+\]\.?(\s*and\s*\[EN#\d+\])*")
PUNCT = re.compile(r"\s+([,.;:!?’”])")
MAX_W, QUALITY = 800, 72


def soup_of(path):
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for x in soup.select("span.pagenum"):
        x.decompose()
    return soup


def text_of(el):
    t = ENDNOTE.sub("", clean(el.get_text()))
    return PUNCT.sub(r"\1", t).strip()


def chapter_blocks(head):
    blocks = []
    for el in head.find_all_next():
        if el.name == "h2":
            break
        if el.name == "p" and el.find_parent("p") is None:
            t = text_of(el)
            if t and not t.startswith("End of The Story of Siegfried"):
                blocks.append({"type": "p", "text": t})
        elif el.name == "pre":
            lines = [l.strip() for l in el.get_text().strip("\n").splitlines()]
            blocks.append({"type": "verse", "text": "\n".join(l for l in lines if l)})
    return blocks


def story(col, order, title, work_id, flags, blocks):
    return finish({
        "id": f"{col['id']}--{slug(title)}",
        "collectionId": col["id"],
        "order": order,
        "title": title,
        "origin": None,
        "excluded": False,
        "flags": list(flags),
        "moral": None,
        "blocks": blocks,
        "workId": work_id,
    })


def siegfried(src):
    soup = soup_of(next((Path(src) / "The-Story-of-Siegfried_6866").glob("*-h/*.htm")))
    h2s = soup.find_all("h2")
    stories = []
    for order, (num, title, work_id, flags, note) in enumerate(ADVENTURES, 1):
        head = next(h for h in h2s if clean(h.get_text(" ")).startswith(f"Adventure {num}."))
        blocks = ([{"type": "note", "text": note}] if note else []) + chapter_blocks(head)
        if num == "XX":
            after = next(h for h in h2s if clean(h.get_text(" ")).startswith("The After Word"))
            blocks += [{"type": "heading", "text": "The After Word"}] + chapter_blocks(after)
        stories.append(story(SIEGFRIED, order, title, work_id, flags, blocks))
    return stories


def unhyphen(text):
    def fix(m):
        w = m.group(0)
        return w if w.lower() in KEEP_HYPHENS else w.replace("-", "")
    text = text.replace("´", "").replace("´", "")
    return re.sub(r"[A-Za-z]+(?:-[A-Za-z]+)+", fix, text)


def save_image(html_dir, src, sid):
    name = f"{sid.split('--')[1]}-{Path(src).stem}.webp"
    dst = ROOT / "images" / FIFTY["id"] / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(html_dir / src).convert("RGB")
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    im.save(dst, "WEBP", quality=QUALITY, method=6)
    return f"images/{FIFTY['id']}/{name}"


def fifty(src):
    path = next((Path(src) / "Fifty-Famous-Stories-Retold_18442").glob("*-h/*.htm"))
    soup = soup_of(path)
    h2s = soup.find_all("h2")
    stories = []
    for order, (heading, title, work_id, flags) in enumerate(FIFTY_STORIES, 1):
        head = next(h for h in h2s if clean(h.get_text(" ")).rstrip(".") == heading)
        sid = f"{FIFTY['id']}--{slug(title)}"
        blocks = []
        for el in head.find_all_next():
            if el.name == "h2":
                break
            if el.name == "p" and not el.find("img"):
                t = unhyphen(text_of(el))
                if t:
                    blocks.append({"type": "p", "text": t})
            elif el.name == "img":
                alt = clean(el.get("alt") or "").rstrip(".").title()
                blocks.append({"type": "image", "src": save_image(path.parent, el["src"], sid),
                               "alt": alt})
        stories.append(story(FIFTY, order, title, work_id, flags, blocks))
    return stories


def main(src):
    index = load_index()
    for col, stories in ((SIEGFRIED, siegfried(src)), (FIFTY, fifty(src))):
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:62} {st['wordCount']:5}w {st['readingMinutes']:3}m "
                  f"{lv['fkGrade']:5} {lv['band']:8} {st['flags']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
