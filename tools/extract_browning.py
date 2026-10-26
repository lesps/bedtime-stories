#!/usr/bin/env python3
"""Robert Browning's "The Pied Piper of Hamelin" (1842), with Kate Greenaway's pictures (1888).

    git clone --depth 1 https://github.com/GITenberg/The-Pied-Piper-of-Hamelin_18343.git src/The-Pied-Piper-of-Hamelin_18343
    python3 tools/extract_browning.py src

Gutenberg #18343 lays the poem out like the picture book: the fifteen numbered sections, with
Greenaway's illustrations between them and, in places, between single lines printed as
captions. Each run of lines between two pictures becomes one verse block (the section numbers
are dropped), and each picture an image block, saved as WebP. The frontispiece opens the story;
the title pages, audio links and colophon are left out. Writes `browning-pied-piper`.
"""
import sys
import warnings
from pathlib import Path

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from PIL import Image

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
sys.path.insert(0, str(Path(__file__).parent))
from build_compendium import clean  # noqa: E402
from compendium_io import ROOT, finish, load_index, save_index, upsert_collection  # noqa: E402

DIR = "The-Pied-Piper-of-Hamelin_18343"
COLLECTION = {
    "id": "browning-pied-piper",
    "title": "The Pied Piper of Hamelin",
    "author": "Robert Browning",
    "contributor": "Illustrated by Kate Greenaway",
    "firstPublished": 1888,
    "source": "https://www.gutenberg.org/ebooks/18343",
    "license": "Public domain in the USA",
    "language": "en",
    "originalLanguage": "en",
}
SID = f"{COLLECTION['id']}--the-pied-piper-of-hamelin"
FRONTISPIECE = "images/img02.jpg"
MAX_W, QUALITY = 800, 72


def save_image(html_dir, src):
    name = f"pied-piper-{Path(src).stem}.webp"
    dst = ROOT / "images" / COLLECTION["id"] / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(html_dir / src).convert("RGB")
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    im.save(dst, "WEBP", quality=QUALITY, method=6)
    return f"images/{COLLECTION['id']}/{name}"


def main(src):
    path = next((Path(src) / DIR).glob("*-h/*.htm"))
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for x in soup.select("span.pagenum, p.soundbyte"):
        x.decompose()
    start = soup.find("a", attrs={"name": "THE_PIED_PIPER_OF_HAMELIN"}).parent
    blocks = [{"type": "image", "src": save_image(path.parent, FRONTISPIECE), "alt": ""}]
    lines = []

    def flush():
        if lines:
            blocks.append({"type": "verse", "text": "\n".join(lines)})
            lines.clear()

    for el in start.find_all_next():
        cls = el.get("class") or []
        if el.name == "p" and "center" in cls:
            text = clean(el.get_text(" "))
            if text.startswith("First published"):
                break
            lines.append(text)
        elif el.name == "div" and "stanza" in cls:
            lines.extend(clean(s.get_text()) for s in el.find_all("span", recursive=False))
        elif el.name == "h3":
            flush()
        elif el.name == "img":
            flush()
            full = el.parent.get("href") if el.parent.name == "a" else el["src"]
            blocks.append({"type": "image", "src": save_image(path.parent, full), "alt": ""})
    flush()
    story = finish({
        "id": SID,
        "collectionId": COLLECTION["id"],
        "order": 1,
        "title": "The Pied Piper of Hamelin",
        "origin": None,
        "excluded": False,
        "flags": [],
        "moral": None,
        "blocks": blocks,
        "workId": "german-pied-piper",
    })
    index = load_index()
    upsert_collection(index, COLLECTION, [story])
    save_index(index)
    lv = story["readingLevel"]
    print(f"{SID} {story['wordCount']}w {story['readingMinutes']}m {lv} "
          f"images={sum(b['type'] == 'image' for b in blocks)} verse={sum(b['type'] == 'verse' for b in blocks)}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
