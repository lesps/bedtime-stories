#!/usr/bin/env python3
"""Finnish and Estonian legends: R. Eivind's Finnish Legends for English Children (1893), a prose
Kalevala for children, and W. F. Kirby's prose Kalevipoeg in The Hero of Esthonia (1895).

    git clone --depth 1 https://github.com/GITenberg/Finnish-Legends-for-English-Children_24948.git src/Finnish-Legends-for-English-Children_24948
    git clone --depth 1 https://github.com/GITenberg/The-Hero-of-Esthonia-and-Other-Studies-in-the-Romantic-Literature-of-That-Country_19438.git src/The-Hero-of-Esthonia-and-Other-Studies-in-the-Romantic-Literature-of-That-Country_19438
    python3 tools/extract_finnic.py src

Eivind tells the Kalevala as an old man, Father Mikko, telling it to children by the fire. Each
chapter is an <h2>; the tale runs to a row of dots, after which the children talk and Mikko goes
on, so the extract stops at the first dots. Some stories here join two chapters, each under its
own heading. The pictures are only ornaments, and the footnotes glosses, so both are left out.
The first word of each chapter is printed in capitals beside a drop-cap picture; it is set in
ordinary case.

Kirby's Kalevipoeg is a canto-by-canto prose retelling of Kreutzwald's epic, with a few charms
kept as verse: each canto is an <h2> ("CANTO II") followed by an <h3> title. Stories that start in
the middle of things open with a bridging note (NOTES). Writes `eivind-finnish` and `kirby-esthonia`.
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

COMMON = {"license": "Public domain in the USA", "language": "en"}
EIVIND = {**COMMON, "id": "eivind-finnish", "title": "Finnish Legends for English Children",
          "author": "R. Eivind", "contributor": "Retold from the Kalevala", "firstPublished": 1893,
          "source": "https://www.gutenberg.org/ebooks/24948", "originalLanguage": "fi"}
KIRBY = {**COMMON, "id": "kirby-esthonia", "title": "The Hero of Esthonia",
         "author": "Friedrich Reinhold Kreutzwald", "contributor": "Translated by W. F. Kirby",
         "firstPublished": 1895, "source": "https://www.gutenberg.org/ebooks/19438", "originalLanguage": "et"}

# (story title, workId, flags, [chapter <h2> texts])
EIVIND_STORIES = [
    ("The World's Creation", "finnish-creation", [], ["THE WORLD'S CREATION AND THE BIRTH OF WAINAMOINEN"]),
    ("Wainamoinen and Youkahainen", "finnish-singing-contest", [], ["WAINAMOINEN AND YOUKAHAINEN"]),
    ("Ilmarinen Forges the Sampo", "finnish-sampo-forged", [], ["ILMARINEN FORGES THE SAMPO"]),
    ("Lemminkainen's Death and Restoration", "finnish-lemminkainen", ["mature-themes"],
     ["LEMMINKAINEN'S DEATH", "LEMMINKAINEN'S RESTORATION"]),
    ("The Birth of the Kantele", "finnish-kantele", [], ["WAINAMOINEN'S EXPEDITION AND THE BIRTH OF THE KANTELE (HARP)"]),
    ("The Capture of the Sampo", "finnish-sampo-stolen", [], ["THE CAPTURE OF THE SAMPO", "THE SAMPO IS LOST IN THE SEA"]),
    ("Louhi Steals the Sun and Moon", "finnish-sun-and-moon", [],
     ["LOUHI STEALS THE SUN, THE MOON, AND FIRE", "THE RESTORATION OF THE SUN AND MOON"]),
]
HEADINGS = {
    "LEMMINKAINEN'S DEATH": "Lemminkainen's death",
    "LEMMINKAINEN'S RESTORATION": "Lemminkainen's restoration",
    "THE CAPTURE OF THE SAMPO": "The capture of the Sampo",
    "THE SAMPO IS LOST IN THE SEA": "The Sampo is lost in the sea",
    "LOUHI STEALS THE SUN, THE MOON, AND FIRE": "Louhi steals the Sun, the Moon, and Fire",
    "THE RESTORATION OF THE SUN AND MOON": "The restoration of the Sun and Moon",
}
# (canto numeral, story title, workId, flags)
KIRBY_STORIES = [
    ("II", "The Death of Kalev", "estonian-linda", []),
    ("VIII", "The Contest and Parting of the Brothers", "estonian-kalevipoeg-king", []),
    ("XX", "Armageddon", "estonian-kalevipoeg-end", ["mature-themes"]),
]
# Bridging notes at the start of stories that begin in the middle of things, from the chapters before.
NOTES = {
    "Ilmarinen Forges the Sampo": "Lost far from home in the dark Northland, Wainamoinen was helped by "
    "Louhi, the old witch who rules it. She asked him to forge her the Sampo, a magic mill that grinds "
    "out flour, salt and money, and promised her daughter to whoever made it. Wainamoinen promised to "
    "send her the smith Ilmarinen instead. On his way home he wounded his knee with an axe, and an old "
    "man healed it.",
    "Lemminkainen's Death and Restoration": "Lemminkainen has asked Louhi, the old witch who rules the "
    "Northland, for one of her daughters. She told him to bring her the Hisi-reindeer, an enchanted deer "
    "made by the evil spirit Hisi. He chased it until his snow-shoes broke.",
    "The Birth of the Kantele": "Ilmarinen has come home from the Northland and told Wainamoinen how "
    "rich it has grown since Louhi got the Sampo.",
    "Louhi Steals the Sun and Moon": "After the Sampo was lost, Louhi tried twice to take her revenge on "
    "Kalevala: first she sent nine diseases, which Wainamoinen drove out, and then the great bear Otso, "
    "which he killed.",
    "The Contest and Parting of the Brothers": "Kalev, the old king, had decided that only one of his "
    "sons should be his heir. Now his three youngest sons set out to settle which of them it will be.",
    "Armageddon": "The son of Kalev, the Kalevide, is now king of Estonia. He has been feasting with his "
    "friends the Alevide and the Sulevide when news comes that the country has been invaded.",
}


def text_of(el):
    return re.sub(r"\s+([,.;:!?’”])", r"\1", clean(el.get_text())).strip()


def story(col, order, title, work_id, flags, blocks):
    st = {"id": f"{col['id']}--{slug(title)}", "collectionId": col["id"], "order": order,
          "title": title, "origin": None, "excluded": False, "flags": flags, "moral": None,
          "blocks": blocks, "workId": work_id}
    return finish(st)


def sentence_start(text):
    """'LONG, long ago' -> 'Long, long ago'; 'LEMMINKAINEN'S mother' -> 'Lemminkainen's mother'."""
    m = re.match(r"([A-Z][A-Z'’]+)\b", text)
    return text if not m or len(m.group(1)) < 2 else m.group(1).capitalize() + text[m.end():]


def eivind(src):
    path = next((Path(src) / "Finnish-Legends-for-English-Children_24948").glob("*-h/*.htm"))
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for x in soup.select("span.pagenum, a.fnanchor, div.footnote"):
        x.decompose()
    h2s = {clean(h.get_text(" ")): h for h in soup.find_all("h2")}
    out = []
    for order, (title, work_id, flags, chapters) in enumerate(EIVIND_STORIES, 1):
        blocks = [{"type": "note", "text": NOTES[title]}] if title in NOTES else []
        for chapter in chapters:
            if len(chapters) > 1:
                blocks.append({"type": "heading", "text": HEADINGS[chapter]})
            first = True
            for el in h2s[chapter].find_all_next():
                if el.name == "h2" or (el.name == "p" and "dots" in (el.get("class") or [])):
                    break
                if el.name == "p" and (t := text_of(el)):
                    blocks.append({"type": "p", "text": sentence_start(t) if first else t})
                    first = False
        out.append(story(EIVIND, order, title, work_id, flags, blocks))
    return out


def kirby(src):
    root = Path(src) / "The-Hero-of-Esthonia-and-Other-Studies-in-the-Romantic-Literature-of-That-Country_19438"
    path = next(root.glob("*-h/volume1.html"))
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for x in soup.select("span.pagenum, a.fnanchor"):
        x.decompose()
    out = []
    for order, (numeral, title, work_id, flags) in enumerate(KIRBY_STORIES, 1):
        canto = next(h for h in soup.find_all("h2") if clean(h.get_text(" ")) == f"CANTO {numeral}")
        blocks = [{"type": "note", "text": NOTES[title]}] if title in NOTES else []
        for el in canto.find_next("h3").find_all_next():
            if el.name in ("h2", "h4"):
                break
            if el.name == "div" and "stanza" in (el.get("class") or []):
                lines = [clean(x.get_text()) for x in el.find_all("span")]
                blocks.append({"type": "verse", "text": "\n".join(line for line in lines if line)})
            elif el.name == "p" and (t := text_of(el)):
                blocks.append({"type": "p", "text": t})
        out.append(story(KIRBY, order, title, work_id, flags, blocks))
    return out


def main(src):
    index = load_index()
    for col, stories in ((EIVIND, eivind(src)), (KIRBY, kirby(src))):
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:58} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
