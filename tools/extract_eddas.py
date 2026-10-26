#!/usr/bin/env python3
"""Norse myths from the two Eddas (Thorpe, 1866; Blackwell, 1847) and Lang's "Story of Sigurd" (1890).

    git clone --depth 1 https://github.com/GITenberg/The-Elder-Eddas-of-Saemund-Sigfusson--and-the-Younger-Eddas-of-Snorre-Sturleson_14726.git \\
        src/The-Elder-Eddas-of-Saemund-Sigfusson--and-the-Younger-Eddas-of-Snorre-Sturleson_14726
    git clone --depth 1 https://github.com/GITenberg/The-Red-Fairy-Book_540.git src/The-Red-Fairy-Book_540
    python3 tools/extract_eddas.py src

Gutenberg #14726 prints Benjamin Thorpe's Elder (Poetic) Edda, one <h2> per poem, and
I. A. Blackwell's Younger (Prose) Edda, one <h4> per section. A story is one poem, or a run of
Prose Edda sections (inner section titles become heading blocks), optionally cut at the paragraph
or sentence that starts with a given phrase. Stanza and paragraph numbers, page numbers and
footnote markers are dropped; the footnotes are left out. In Thorpe a speaker's name on its own
line ("Freyia.") is joined to the speech that follows it. From the Red Fairy Book only "The
Story of Sigurd" is taken (Lang's condensation of William Morris's Völsunga saga). Writes
`thorpe-elder-edda`, `blackwell-prose-edda` and `lang-red`.
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

EDDAS = "The-Elder-Eddas-of-Saemund-Sigfusson--and-the-Younger-Eddas-of-Snorre-Sturleson_14726"
RED = "The-Red-Fairy-Book_540"
M = ["mature-themes"]
COMMON = {"license": "Public domain in the USA", "language": "en"}
THORPE = {
    **COMMON,
    "id": "thorpe-elder-edda",
    "title": "The Elder Edda",
    "author": "Traditional (Old Norse poems)",
    "contributor": "Translated by Benjamin Thorpe",
    "firstPublished": 1866,
    "source": "https://www.gutenberg.org/ebooks/14726",
    "originalLanguage": "is",
}
BLACKWELL = {
    **COMMON,
    "id": "blackwell-prose-edda",
    "title": "The Prose Edda",
    "author": "Snorri Sturluson",
    "contributor": "Translated by I. A. Blackwell",
    "firstPublished": 1847,
    "source": "https://www.gutenberg.org/ebooks/14726",
    "originalLanguage": "is",
}
LANG_RED = {
    **COMMON,
    "id": "lang-red",
    "title": "The Red Fairy Book",
    "author": "Various",
    "contributor": "Edited by Andrew Lang",
    "firstPublished": 1890,
    "source": "https://www.gutenberg.org/ebooks/540",
    "originalLanguage": "en",
}
# (start of the <h2> text, title, workId, flags)
POEMS = [
    ("VÖLUSPÂ", "The Vala's Prophecy", "norse-ragnarok", []),
    ("ODIN'S RUNE-SONG", "Odin's Rune-Song", "norse-odin-runes", []),
    ("THE LAY OF HYMIR", "The Lay of Hymir", "norse-thor-fishing", []),
    ("THE LAY OF THRYM", "The Lay of Thrym", "norse-thor-thrym", []),
    ("THE LAY OF THE DWARF ALVIS", "The Lay of Alvis", "norse-alviss", []),
    ("THE JOURNEY OR LAY OF SKIRNIR", "The Journey of Skirnir", "norse-frey-gerd", M),
    ("THE LAY OF VEGTAM", "Baldr's Dreams", "norse-baldr", []),
    ("THE LAY OF FAFNIR", "The Lay of Fafnir", "norse-sigurd-fafnir", []),
]
# (first <h4>, last <h4> or None, title, workId, flags[, start phrase, stop phrase, [more <h4>s]])
# The extra sections are appended after the cut, with their titles as headings: Skadi's story goes
# on in "Of Njord", earlier in the book.
SECTIONS = [
    ("OF THE PRIMORDIAL STATE", "OF THE FORMATION OF THE FIRST MAN", "The Beginning of the World",
     "norse-creation", []),
    ("OF NIGHT AND DAY", "OF THE WOLVES", "Night and Day, Sun and Moon", "norse-sun-moon", []),
    ("OF THE WAY THAT LEADS TO HEAVEN", "OF THE VARIOUS CELESTIAL REGIONS", "The Ash Yggdrasil",
     "norse-yggdrasil", []),
    ("OF LOKI AND HIS PROGENY", "BINDING THE WOLF FENIR", "The Binding of the Wolf Fenrir",
     "norse-fenrir", []),
    ("OF FREY AND GERDA", None, "Frey and Gerda", "norse-frey-gerd", []),
    ("OF THE HORSE SLEIPNIR", None, "The Horse Sleipnir", "norse-asgard-wall", []),
    ("THOR'S ADVENTURES ON HIS JOURNEY", None, "Thor's Journey to the Land of the Giants",
     "norse-thor-utgard", []),
    ("HOW THOR WENT TO FISH", None, "How Thor Went Fishing for the Midgard Serpent",
     "norse-thor-fishing", []),
    ("THE DEATH OF BALDUR THE GOOD", "BALDUR IN THE ABODE", "The Death of Baldur", "norse-baldr", []),
    ("THE FLIGHT AND PUNISHMENT OF LOKI", None, "The Punishment of Loki", "norse-loki-bound", M),
    ("OF RAGNAROK", "THE RENOVATION OF THE UNIVERSE", "Ragnarok", "norse-ragnarok", []),
    ("IDUNA AND HER APPLES", None, "Iduna and Her Apples", "norse-idun", [],
     None, "When these tidings came to Thjassi's daughter"),
    ("IDUNA AND HER APPLES", None, "Skadi Chooses a Husband", "norse-skadi", [],
     "When these tidings came to Thjassi's daughter", None, ["OF NJORD"]),
    ("THE ORIGIN OF POETRY", "ODIN BEGUILES", "The Origin of Poetry", "norse-mead", M),
]
NUMBER = re.compile(r"^\d+\.\s*")
PUNCT = re.compile(r"\s+([,.;:!?’”])")


def soup_of(path):
    soup = BeautifulSoup(path.read_bytes(), "lxml")
    for x in soup.select("span.pagenum, div.pagenum"):
        x.decompose()
    for a in soup.find_all("a"):
        if re.fullmatch(r"\[\d+\]", a.get_text().strip()):
            a.decompose()
    return soup


def text_of(el):
    t = PUNCT.sub(r"\1", re.sub(r"\[\d+\]", "", clean(el.get_text()))).strip()
    return re.sub(r'^(["“‘\'])\s+', r"\1", t)


def paras_after(head, stop_tags):
    """Paragraphs (str) and quoted stanzas (("verse", str)) from `head` to the next heading."""
    out = []
    for el in head.find_all_next():
        if el.name in stop_tags:
            break
        if el.name == "p" and not el.find_parent("div", class_="stanza"):
            t = NUMBER.sub("", text_of(el))
            if t:
                out.append(t)
        elif el.name == "div" and "stanza" in (el.get("class") or []):
            lines = [clean(s.get_text()) for s in el.find_all("span", recursive=False)]
            out.append(("verse", "\n".join(l for l in lines if l)))
    return out


def blocks_of(paras):
    return [{"type": "verse", "text": t[1]} if isinstance(t, tuple) else {"type": "p", "text": t}
            for t in paras]


def poem_blocks(paras):
    """Join a speaker's name on its own line ("Freyia.") to the speech that follows."""
    blocks, speaker = [], None
    for t in paras:
        if isinstance(t, tuple):
            blocks.append({"type": "verse", "text": t[1]})
            continue
        if len(t) < 30 and t.endswith(".") and t[0].isupper() and " " not in t.strip(". ")[:20].strip():
            speaker = t.rstrip(". ")
            continue
        blocks.append({"type": "p", "text": f"{speaker}: {t}" if speaker else t})
        speaker = None
    return blocks


def cut(blocks, start, stop):
    """Keep the text from the phrase `start` on, and before the phrase `stop` (mid-paragraph ok)."""
    flat = []
    for b in blocks:
        t = b["text"]
        if start and start in t and b["type"] == "p":
            flat = [{"type": "p", "text": t[t.index(start):]}]
            continue
        if stop and stop in t and b["type"] == "p":
            head = t[: t.index(stop)].strip()
            if head:
                flat.append({"type": "p", "text": head})
            return flat
        flat.append(b)
    return flat


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


def main(src):
    soup = soup_of(next((Path(src) / EDDAS).glob("*-h/*.htm")))
    h2s = soup.find_all("h2")
    thorpe = []
    for order, (start, title, work_id, flags) in enumerate(POEMS, 1):
        head = next(h for h in h2s if clean(h.get_text(" ")).startswith(start))
        thorpe.append(story(THORPE, order, title, work_id, flags,
                            poem_blocks(paras_after(head, {"h2", "h3"}))))

    h4s = soup.find_all("h4")
    blackwell = []
    for order, (first, last, title, work_id, flags, *phrases) in enumerate(SECTIONS, 1):
        i = next(n for n, h in enumerate(h4s) if clean(h.get_text(" ")).startswith(first))
        j = next(n for n, h in enumerate(h4s) if clean(h.get_text(" ")).startswith(last)) if last else i
        blocks = []
        for h in h4s[i:j + 1]:
            if j > i:
                name = re.sub(r"\.,", ",", clean(h.get_text(" ")).rstrip("."))  # "Mimir's Well., and"
                blocks.append({"type": "heading", "text": title_case(name)})
            blocks += blocks_of(paras_after(h, {"h2", "h3", "h4"}))
        if phrases:
            blocks = cut(blocks, *phrases[:2])
        for extra in phrases[2] if len(phrases) > 2 else []:
            h = next(h for h in h4s if clean(h.get_text(" ")).startswith(extra))
            blocks.append({"type": "heading", "text": title_case(clean(h.get_text(" ")).rstrip("."))})
            blocks += blocks_of(paras_after(h, {"h2", "h3", "h4"}))
        blackwell.append(story(BLACKWELL, order, title, work_id, flags, blocks))

    red = soup_of(next((Path(src) / RED).glob("*-h/*.htm")))
    head = next(h for h in red.find_all("h2") if clean(h.get_text(" ")) == "THE STORY OF SIGURD")
    paras = [t for t in paras_after(head, {"h2"}) if not re.match(r"^\(\d+\)", str(t))]
    blocks = blocks_of(paras) + [{"type": "note", "text": (
        "Condensed by Andrew Lang from William Morris and Eiríkr Magnússon's translation of the "
        "Völsunga saga.")}]
    sigurd = story(LANG_RED, 1, "The Story of Sigurd", "norse-sigurd-fafnir", M, blocks)

    index = load_index()
    for col, stories in ((THORPE, thorpe), (BLACKWELL, blackwell), (LANG_RED, [sigurd])):
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:62} {st['wordCount']:5}w {st['readingMinutes']:3}m "
                  f"{lv['fkGrade']:5} {lv['band']:8} {st['flags']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
