#!/usr/bin/env python3
"""English legends: Pyle's Robin Hood (1883), Marshall's Beowulf (1909), Quiller-Couch's Corineus (1914).

    git clone --depth 1 https://github.com/GITenberg/The-Merry-Adventures-of-Robin-Hood_10148.git src/The-Merry-Adventures-of-Robin-Hood_10148
    git clone --depth 1 https://github.com/GITenberg/English-Literature-for-Boys-and-Girls_5725.git src/English-Literature-for-Boys-and-Girls_5725
    git clone --depth 1 https://github.com/GITenberg/Cornwall-s-Wonderland_26755.git src/Cornwall-s-Wonderland_26755
    python3 tools/extract_english.py src

The Merry Adventures of Robin Hood is one chapter per <h2>. Seven are taken: how Robin became an
outlaw (and met Little John), the shooting match, Allan a Dale, the Curtal Friar, Allan's
wedding, King Richard in Sherwood and the Epilogue (Robin's death; `mature-themes` for the battle
and the bleeding). Pyle's songs, printed in tables, become verse blocks; footnotes, footnote
markers and pictures are left out. Writes `pyle-robin-hood`.

From H. E. Marshall's English Literature for Boys and Girls only chapter XI, "The Story of
Beowulf", is taken (plain text; the reading list at its end is dropped). Writes
`marshall-english-literature`. From Mabel Quiller-Couch's Cornwall's Wonderland only "How
Corineus Fought the Chief of the Giants" (plain text). Writes `quiller-couch-cornwall`.
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
PYLE = {
    **COMMON,
    "id": "pyle-robin-hood",
    "title": "The Merry Adventures of Robin Hood",
    "author": "Howard Pyle",
    "contributor": None,
    "firstPublished": 1883,
    "source": "https://www.gutenberg.org/ebooks/10148",
}
MARSHALL = {
    **COMMON,
    "id": "marshall-english-literature",
    "title": "English Literature for Boys and Girls",
    "author": "H. E. Marshall",
    "contributor": None,
    "firstPublished": 1909,
    "source": "https://www.gutenberg.org/ebooks/5725",
}
QUILLER_COUCH = {
    **COMMON,
    "id": "quiller-couch-cornwall",
    "title": "Cornwall's Wonderland",
    "author": "Mabel Quiller-Couch",
    "contributor": None,
    "firstPublished": 1914,
    "source": "https://www.gutenberg.org/ebooks/26755",
}
# (chapter heading, story title, workId, flags)
PYLE_CHAPTERS = [
    ("How Robin Hood Came to Be an Outlaw", "How Robin Hood Came to Be an Outlaw", "english-robin-outlaw", []),
    ("The Shooting Match at Nottingham Town", "The Shooting Match at Nottingham Town", "english-robin-shooting-match", []),
    ("Robin Hood and Allan a Dale", "Robin Hood and Allan a Dale", "english-robin-allan-a-dale", []),
    ("Robin Hood Seeks the Curtal Friar", "Robin Hood Seeks the Curtal Friar", "english-robin-friar-tuck", []),
    ("Robin Hood Compasses a Marriage", "Robin Hood Compasses a Marriage", "english-robin-wedding", []),
    ("King Richard Comes to Sherwood Forest", "King Richard Comes to Sherwood Forest", "english-robin-king-richard", []),
    ("Epilogue", "Epilogue: The Death of Robin Hood", "english-robin-death", ["mature-themes"]),
]
PUNCT = re.compile(r"\s+([,.;:!?’”])")


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


def pyle(src):
    path = next((Path(src) / "The-Merry-Adventures-of-Robin-Hood_10148").glob("*-h/*.htm"))
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for x in soup.select("sup, small, img"):
        x.decompose()
    for t in soup.find_all("table"):
        if t.find("a", attrs={"name": re.compile(r"^note")}):
            t.decompose()  # footnotes
    h2s = soup.find_all("h2")
    stories = []
    for order, (heading, title, work_id, flags) in enumerate(PYLE_CHAPTERS, 1):
        head = next(h for h in h2s if clean(h.get_text(" ")) == heading)
        blocks = []
        for el in head.find_all_next():
            if el.name == "h2":
                break
            if el.name == "p" and not el.find_parent("table"):
                t = PUNCT.sub(r"\1", clean(el.get_text())).strip()
                if t:
                    blocks.append({"type": "p", "text": t})
            elif el.name == "table":
                blocks += song_blocks(el.get_text())
            elif el.name == "center" and not el.find(["table", "img"]) and el.get_text(strip=True):
                lines = [clean(x) for x in el.get_text("\n").split("\n") if x.strip()]
                blocks.append({"type": "verse", "text": "\n".join(lines)})  # the Kirklees epitaph
        stories.append(story(PYLE, order, title, work_id, flags, blocks))
    return stories


def song_blocks(raw):
    """A song printed in a table: one verse block per stanza. Pyle's HTML sets some quote marks and
    closing punctuation on lines of their own; they are joined to the line they belong to."""
    out, lines = [], []
    pending = ""
    for line in raw.replace("\t", "    ").split("\n") + [""]:
        t = line.strip()
        if re.fullmatch(r"[\"']+", t):          # an opening quote alone on its line
            pending += t
            continue
        if lines and re.fullmatch(r"[.,;:!?]*[\"']*[.,;:!?]*", t) and t:  # closing punctuation alone
            lines[-1] += t
            continue
        if not t:
            if lines:
                out.append({"type": "verse", "text": "\n".join(lines)})
                lines = []
            continue
        lines.append(pending + t)
        pending = ""
    return out


def text_section(path, start, stop):
    """Paragraphs between the line `start` and the line starting with `stop` (plain-text ebook)."""
    lines = path.read_text(encoding="latin-1").replace("\r", "").split("\n")
    i = max(n for n, l in enumerate(lines) if l.strip() == start) + 1
    paras, cur = [], []
    for line in lines[i:]:
        if line.strip().startswith(stop):
            break
        if line.strip():
            cur.append(line.strip())
        elif cur:
            paras.append(" ".join(cur))
            cur = []
    if cur:
        paras.append(" ".join(cur))
    return [{"type": "p", "text": re.sub(r"\s+", " ", p)} for p in paras]


def main(src):
    beowulf = story(MARSHALL, 1, "The Story of Beowulf", "english-beowulf", [], text_section(
        Path(src) / "English-Literature-for-Boys-and-Girls_5725" / "5725-8.txt",
        "Chapter XI THE STORY OF BEOWULF", "BOOKS TO READ"))
    corineus = story(QUILLER_COUCH, 1, "How Corineus Fought the Chief of the Giants", "english-gogmagog",
                     ["mature-themes"],  # the giant dashed on the rocks, the sea dyed with blood
                     text_section(Path(src) / "Cornwall-s-Wonderland_26755" / "26755.txt",
                                  "HOW CORINEUS FOUGHT THE CHIEF OF THE GIANTS",
                                  "THE GIANT OF ST. MICHAEL'S MOUNT"))
    index = load_index()
    for col, stories in ((PYLE, pyle(src)), (MARSHALL, [beowulf]), (QUILLER_COUCH, [corineus])):
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:62} {st['wordCount']:5}w {st['readingMinutes']:3}m "
                  f"{lv['fkGrade']:5} {lv['band']:8} {st['flags']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
