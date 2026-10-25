#!/usr/bin/env python3
"""Charles Kingsley's The Heroes, or Greek Fairy Tales for My Children (1856), from its mirror.

    git clone --depth 1 https://github.com/GITenberg/The-Heroes--or-Greek-Fairy-Tales-for-My-Children_677.git \\
        src/The-Heroes--or-Greek-Fairy-Tales-for-My-Children_677
    python3 tools/extract_kingsley.py src

Three stories, each an <h2> ("STORY I.—PERSEUS") with its parts as <h3>, which become heading
blocks. Footnote markers are dropped; the footnotes themselves (end of book) are left out.
Text only: the edition's eight plates are not taken. Writes the `kingsley-heroes` collection.
"""
import re
import sys
import warnings
from pathlib import Path

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
sys.path.insert(0, str(Path(__file__).parent))
from build_compendium import clean, slug, title_case  # noqa: E402
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

DIR = "The-Heroes--or-Greek-Fairy-Tales-for-My-Children_677"
COLLECTION = {
    "id": "kingsley-heroes",
    "title": "The Heroes, or Greek Fairy Tales for My Children",
    "author": "Charles Kingsley",
    "contributor": None,
    "firstPublished": 1856,
    "source": "https://www.gutenberg.org/ebooks/677",
    "license": "Public domain in the USA",
    "language": "en",
    "originalLanguage": "en",
}
STORIES = {  # h2 text after "STORY N.—" -> (title, workId)
    "PERSEUS": ("Perseus", "greek-perseus"),
    "THE ARGONAUTS": ("The Argonauts", "greek-jason"),
    "THESEUS": ("Theseus", "greek-theseus"),
}


def main(src):
    html = next((Path(src) / DIR).glob("*-h/*.htm"))
    soup = BeautifulSoup(html.read_text(encoding="utf-8", errors="replace"), "lxml")
    for x in soup.select("span.pagenum, a.citation"):
        x.decompose()
    found, cur = [], None
    for el in soup.body.find_all(["h2", "h3", "p"]):
        for br in el.find_all("br"):
            br.replace_with(": ")
        text = clean(el.get_text(" "))
        if not text:
            continue
        if el.name == "h2":
            key = re.sub(r"^STORY [IVX]+\.\s*[—-]+\s*", "", text)
            cur = {"key": key, "blocks": []} if key in STORIES else None
            if cur:
                found.append(cur)
        elif cur is None:
            continue
        elif el.name == "h3":
            part, _, name = text.partition(": ")
            part = re.sub(r"^PART\s+([IVX]+)$", r"Part \1", part)
            cur["blocks"].append({"type": "heading", "text": f"{part}: {title_case(name)}"})
        else:
            cur["blocks"].append({"type": "p", "text": re.sub(r"\s+([,.;:!?’”])", r"\1", text)})
    stories = []
    for order, s in enumerate(found, 1):
        title, work_id = STORIES[s["key"]]
        stories.append(finish({
            "id": f"{COLLECTION['id']}--{slug(title)}",
            "collectionId": COLLECTION["id"],
            "order": order,
            "title": title,
            "origin": None,
            "excluded": False,
            "flags": [],
            "moral": None,
            "blocks": s["blocks"],
            "workId": work_id,
        }))
    index = load_index()
    upsert_collection(index, COLLECTION, stories)
    save_index(index)
    for st in stories:
        heads = [b["text"] for b in st["blocks"] if b["type"] == "heading"]
        print(f"{st['id']:32} {st['wordCount']:6}w {st['readingMinutes']:3}m {st['readingLevel']}  parts={len(heads)}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
