#!/usr/bin/env python3
"""Welsh myths: Lady Charlotte Guest's Mabinogion (1849) and two Welsh tales from Jacobs (1892).

    git clone --depth 1 https://github.com/GITenberg/The-Mabinogion_5160.git src/The-Mabinogion_5160
    git clone --depth 1 https://github.com/GITenberg/Celtic-Fairy-Tales_7885.git src/Celtic-Fairy-Tales_7885
    python3 tools/extract_welsh.py src

In Guest's Mabinogion each tale is an <h2>; its paragraphs run to the next <h2>. The englyns and
Taliesin's songs (p.poetry, one <br> per line) become verse blocks. Guest's few footnotes become
note blocks after the paragraph that cites them, except the ones that only matter to scholars.
From Joseph Jacobs's Celtic Fairy Tales, which has no HTML edition here, the plain text gives
"The Shepherd of Myddvai" and "Beth Gellert": paragraphs are split on blank lines, indented
lines are verse. A few transcription errors in the Gutenberg texts are corrected (FIXES). Writes
`guest-mabinogion` and `jacobs-celtic`.
"""
import glob
import re
import sys
import warnings
from pathlib import Path

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
sys.path.insert(0, str(Path(__file__).parent))
from build_compendium import clean, slug  # noqa: E402
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

M = ["mature-themes"]
COMMON = {"license": "Public domain in the USA", "language": "en"}
GUEST = {**COMMON, "id": "guest-mabinogion", "title": "The Mabinogion",
         "author": "Traditional (medieval Welsh)", "contributor": "Translated by Lady Charlotte Guest",
         "firstPublished": 1849, "source": "https://www.gutenberg.org/ebooks/5160",
         "originalLanguage": "cy"}
JACOBS = {**COMMON, "id": "jacobs-celtic", "title": "Celtic Fairy Tales", "author": "Various (collected)",
          "contributor": "Edited by Joseph Jacobs", "firstPublished": 1892,
          "source": "https://www.gutenberg.org/ebooks/7885", "originalLanguage": "en"}

# (start of the <h2> text, story title, workId, flags)
GUEST_STORIES = [
    ("PWYLL PRINCE OF DYVED", "Pwyll Prince of Dyved", "welsh-pwyll", []),
    ("BRANWEN THE DAUGHTER OF LLYR", "Branwen the Daughter of Llyr", "welsh-branwen", M),
    ("MANAWYDDAN THE SON OF LLYR", "Manawyddan the Son of Llyr", "welsh-manawydan", []),
    ("MATH THE SON OF MATHONWY", "Math the Son of Mathonwy", "welsh-math", M),
    ("HERE IS THE STORY OF LLUDD AND LLEVELYS", "The Story of Lludd and Llevelys", "welsh-lludd-llefelys", []),
    ("TALIESIN", "Taliesin", "welsh-taliesin", []),
    ("KILHWCH AND OLWEN", "Kilhwch and Olwen", "welsh-culhwch-olwen", []),
]
# Guest's footnotes, by number: None drops one; a string replaces its wording.
FOOTNOTES = {
    1: None,  # a manuscript Guest could not get hold of
    2: "Annwvyn is the Otherworld; Guest's note calls it Hades.",
    5: None,  # wordplay that can't be translated
    6: None,  # "Taliesin" (the name already stands in the text)
    7: None,  # a scribe's slip of one name for another
}
JACOBS_STORIES = [
    ("THE SHEPHERD OF MYDDVAI", "The Shepherd of Myddvai", "welsh-myddfai", [],
     "From oral tradition, as given by W. Rees in The Physicians of Myddvai (1861). The physicians "
     "of Myddfai were real: a family of healers for some six hundred years, until the 1700s."),
    ("BETH GELLERT", "Beth Gellert", "welsh-gelert", M,
     "Jacobs retells W. R. Spencer's poem of 1800. No trace of the story at Beddgelert has been "
     "found before then; the tale of a faithful dog wrongly killed is far older, and came to Wales "
     "from India by way of the fable books of the Middle Ages."),
]
END_NOTES = {"welsh-taliesin": "Guest's translation stops here, before the songs of prophecy."}
GUEST_FIXES = {
    "White Mount an London": "White Mount in London",
    "they enamelled they, as them had done": "they enamelled them, as they had done",
    "what dust thou do here": "what dost thou do here",
    "on which the howl was placed": "on which the bowl was placed",
    "friendship mere pure": "friendship more pure",
    "take any price for at.": "take any price for it.",
    "Gronw rose up from the bill": "Gronw rose up from the hill",
    "as a fierce hull bitterly": "as a fierce bull bitterly",
}
BR = "\u2028"  # stands in for <br> until verse is split into lines
FIXES = {"Print Llewelyn": "Prince Llewelyn", "But one day here were going": "But one day they were going"}


def story(col, order, title, work_id, flags, blocks):
    return finish({"id": f"{col['id']}--{slug(title)}", "collectionId": col["id"], "order": order,
                   "title": title, "origin": None, "excluded": False, "flags": list(flags),
                   "moral": None, "blocks": blocks, "workId": work_id})


def text_of(el):
    return re.sub(r"\s+([,.;:!?’”])", r"\1", clean(el.get_text())).strip()


def fix(text):
    for bad, good in GUEST_FIXES.items():
        text = text.replace(bad, good)
    return text


def guest(src):
    soup = BeautifulSoup(open(glob.glob(f"{src}/The-Mabinogion_5160/*-h/*.htm")[0], "rb").read(), "lxml")
    for x in soup.select("span.pagenum"):
        x.decompose()
    notes = {}
    for a in soup.select("a.footnote"):
        n = int(a.get_text().strip("[]"))
        p = a.find_parent("p")
        a.decompose()
        notes[n] = text_of(p)
    for br in soup.find_all("br"):
        br.replace_with(BR)
    h2s = soup.find_all("h2")
    out = []
    for order, (start, title, work_id, flags) in enumerate(GUEST_STORIES, 1):
        head = next(h for h in h2s if " ".join(h.get_text(" ").split()).startswith(start))
        blocks = []
        for el in head.find_next_siblings():
            if el.name == "h2":
                break
            if el.name != "p":
                continue
            cites = [int(a.get_text().strip("[]")) for a in el.select("a.citation")]
            for a in el.select("a.citation"):
                a.decompose()
            if re.fullmatch(r"[*\s]*", el.get_text()):
                continue  # a row of asterisks
            if "poetry" in (el.get("class") or []):
                lines = [fix(clean(line)) for line in el.get_text().split(BR)]
                blocks.append({"type": "verse", "text": "\n".join(line for line in lines if line)})
            else:
                blocks.append({"type": "p", "text": fix(text_of(el).replace(BR, " "))})
            for n in cites:
                note = FOOTNOTES.get(n, notes[n])
                if note:
                    blocks.append({"type": "note", "text": note})
        if work_id in END_NOTES:
            blocks.append({"type": "note", "text": END_NOTES[work_id]})
        out.append(story(GUEST, order, title, work_id, flags, blocks))
    return out


def jacobs(src):
    text = open(f"{src}/Celtic-Fairy-Tales_7885/7885.txt", encoding="latin-1").read()
    for bad, good in FIXES.items():
        text = text.replace(bad, good)
    lines = text.splitlines()
    out = []
    for order, (head, title, work_id, flags, note) in enumerate(JACOBS_STORIES, 1):
        i = lines.index(head) + 1
        body = []
        while not re.fullmatch(r"[A-Z][A-Z' ]+", lines[i].strip() or "x"):
            body.append(lines[i])
            i += 1
        blocks = []
        for para in re.split(r"\n\s*\n", "\n".join(body)):
            rows = [r for r in para.split("\n") if r.strip()]
            if not rows:
                continue
            if all(r.startswith("  ") for r in rows):
                blocks.append({"type": "verse", "text": "\n".join(r.strip() for r in rows)})
            else:
                blocks.append({"type": "p", "text": clean(" ".join(r.strip() for r in rows))})
        blocks.append({"type": "note", "text": note})
        out.append(story(JACOBS, order, title, work_id, flags, blocks))
    return out


def main(src):
    index = load_index()
    for col, stories in ((GUEST, guest(src)), (JACOBS, jacobs(src))):
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:62} {st['wordCount']:5}w {st['readingMinutes']:3}m "
                  f"{lv['fkGrade']:5} {lv['band']:8} {st['flags']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
