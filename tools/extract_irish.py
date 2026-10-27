#!/usr/bin/env python3
"""Irish myths: Joyce (1894 ed.), Stephens (1920), Hull (1909) and Carleton (in Yeats, 1888).

    git clone --depth 1 https://github.com/GITenberg/Old-Celtic-Romances_38041.git src/Old-Celtic-Romances_38041
    git clone --depth 1 https://github.com/GITenberg/Irish-Fairy-Tales_2892.git src/Irish-Fairy-Tales_2892
    git clone --depth 1 https://github.com/GITenberg/Cuchulain-the-Hound-of-Ulster_52963.git src/Cuchulain-the-Hound-of-Ulster_52963
    git clone --depth 1 https://github.com/GITenberg/Fairy-and-Folk-Tales-of-the-Irish-Peasantry_33887.git src/Fairy-and-Folk-Tales-of-the-Irish-Peasantry_33887
    python3 tools/extract_irish.py src

Each book prints a story under <h2>. In P. W. Joyce's Old Celtic Romances the chapters are
<h3> "CHAPTER I." with the chapter's title in the next centred paragraph, which becomes a heading
block; footnote markers ("[VII.]") are dropped. In James Stephens's Irish Fairy Tales the
chapters are numbered <h2>s and are run together without headings. In Eleanor Hull's
Cuchulain, the Hound of Ulster each chapter is an <h2>; a story made of several chapters gets
their titles as headings, and a note block where chapters are skipped; its poems (div.poetry,
one <p> per line) become verse blocks, one per stanza. From Yeats's Fairy and
Folk Tales of the Irish Peasantry only William Carleton's "A Legend of Knockmany" is taken.
Pictures and footnotes are left out. Writes `joyce-celtic-romances`, `stephens-irish-fairy-tales`,
`hull-cuchulain` and `yeats-irish-folk`.
"""
import glob
import re
import sys
import warnings
from pathlib import Path

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
sys.path.insert(0, str(Path(__file__).parent))
from build_compendium import clean, slug, title_case  # noqa: E402
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

M = ["mature-themes"]
COMMON = {"license": "Public domain in the USA", "language": "en", "originalLanguage": "ga"}
JOYCE = {**COMMON, "id": "joyce-celtic-romances", "title": "Old Celtic Romances",
         "author": "P. W. Joyce", "contributor": "Translated from the Gaelic", "firstPublished": 1879,
         "source": "https://www.gutenberg.org/ebooks/38041"}
STEPHENS = {**COMMON, "id": "stephens-irish-fairy-tales", "title": "Irish Fairy Tales",
            "author": "James Stephens", "contributor": None, "firstPublished": 1920,
            "source": "https://www.gutenberg.org/ebooks/2892"}
HULL = {**COMMON, "id": "hull-cuchulain", "title": "Cuchulain, the Hound of Ulster",
        "author": "Eleanor Hull", "contributor": None, "firstPublished": 1909,
        "source": "https://www.gutenberg.org/ebooks/52963"}
YEATS = {**COMMON, "id": "yeats-irish-folk", "title": "Fairy and Folk Tales of the Irish Peasantry",
         "author": "Various", "contributor": "Edited by W. B. Yeats", "firstPublished": 1888,
         "source": "https://www.gutenberg.org/ebooks/33887", "originalLanguage": "en"}

# (start of the <h2> text, story title, workId, flags)
JOYCE_STORIES = [
    ("THE FATE OF THE CHILDREN OF LIR", "The Fate of the Children of Lir", "irish-children-of-lir", []),
    ("THE FATE OF THE CHILDREN OF TURENN", "The Fate of the Children of Turenn", "irish-children-of-turenn", M),
    ("THE VOYAGE OF MAILDUN", "The Voyage of Maildun", "irish-maeldun", []),
    ("THE PURSUIT OF DERMAT AND GRANIA", "The Pursuit of Dermat and Grania", "irish-diarmuid-grainne", M),
    ("OISIN IN TIRNANOGE", "Oisin in Tirnanoge", "irish-oisin", []),
    ("THE FATE OF THE SONS OF USNA", "The Fate of the Sons of Usna", "irish-deirdre", M),
]
STEPHENS_STORIES = [
    ("THE STORY OF TUAN MAC CAIRILL", "The Story of Tuan mac Cairill", "irish-tuan", []),
    ("THE BOYHOOD OF FIONN", "The Boyhood of Fionn", "irish-fionn-boyhood", []),
]
# (title, workId, flags, [(chapter number, note before it or None)])
HULL_STORIES = [
    ("How Cuchulain Got His Name", "irish-cuchulain-name", [], [("IV", None)]),
    ("The Cattle Raid of Cooley", "irish-tain", M, [
        ("IX", None),
        ("XIV", "In the chapters between, Meave's great army marches into Ulster to seize the Brown Bull. "
                "The men of Ulster lie under an old curse of weakness, and only the boy Cuchulain, guarding "
                "the border alone, holds back the army, fighting one champion after another at the ford."),
        ("XV", None),
        ("XIX", "In the chapters between, Cuchulain lies wounded and the men of Ulster at last rise up "
                "from their weakness and gather for the great battle."),
    ]),
]
FNREF = re.compile(r"\[(?:[IVXLC]+\.|\d+)\]")


def soup_of(pattern):
    soup = BeautifulSoup(open(glob.glob(pattern)[0], "rb").read(), "lxml")
    for x in soup.select("a.fnanchor, span.pagenum, img, div.fig"):
        x.decompose()
    return soup


def para(el):
    t = FNREF.sub("", clean(el.get_text()))
    return re.sub(r"\s+([,.;:!?’”])", r"\1", t).strip()


def blocks_until(head, is_stop, chapter_heading=None):
    """Paragraphs and stanzas after `head` until an element for which is_stop() is true."""
    blocks = []
    for el in head.find_all_next():
        if el.name in ("h2", "h3") and is_stop(el):
            break
        cls = el.get("class") or []
        if el.name == "p" and not el.find_parent("div", class_=["poem", "poetry"]):
            if el.find("a", id=re.compile("^Footnote")):
                continue
            t = para(el)
            if not t:
                continue
            if "center" in cls and chapter_heading:
                blocks.append({"type": "heading", "text": title_case(t)})
            else:
                blocks.append({"type": "p", "text": t})
        elif el.name == "div" and "poetry" in cls:
            for stanza in el.find_all("div", class_="stanza") or [el]:
                lines = [l for l in (para(v) for v in stanza.find_all("p")) if l]
                if lines:
                    blocks.append({"type": "verse", "text": "\n".join(lines)})
        elif el.name == "div" and "stanza" in cls and not el.find_parent("div", class_="poetry"):
            lines = [clean(s.get_text()) for s in el.find_all("span", recursive=False)]
            lines = [l for l in lines if l]
            if "right" in cls and blocks and blocks[-1]["type"] == "verse":
                blocks[-1]["text"] += "\n— " + " ".join(lines).rstrip(".")
            elif lines:
                blocks.append({"type": "verse", "text": "\n".join(lines)})
    return blocks


def story(col, order, title, work_id, flags, blocks):
    return finish({"id": f"{col['id']}--{slug(title)}", "collectionId": col["id"], "order": order,
                   "title": title, "origin": None, "excluded": False, "flags": list(flags),
                   "moral": None, "blocks": blocks, "workId": work_id})


def h2_text(h):
    return clean(h.get_text(" "))


def joyce(src):
    soup = soup_of(f"{src}/Old-Celtic-Romances_38041/*-h/*.htm")
    h2s = soup.find_all("h2")
    out = []
    for order, (start, title, work_id, flags) in enumerate(JOYCE_STORIES, 1):
        head = next(h for h in h2s if h2_text(h).startswith(start))
        out.append(story(JOYCE, order, title, work_id, flags,
                         blocks_until(head, lambda el: el.name == "h2", chapter_heading=True)))
    return out


def stephens(src):
    soup = soup_of(f"{src}/Irish-Fairy-Tales_2892/*-h/*.htm")
    for x in soup.select("span.dropcap"):
        x.unwrap()
    h2s = soup.find_all("h2")
    out = []
    for order, (start, title, work_id, flags) in enumerate(STEPHENS_STORIES, 1):
        head = next(h for h in h2s if h2_text(h).startswith(start))
        stop = lambda el: el.name == "h2" and not h2_text(el).startswith("CHAPTER")  # noqa: E731
        out.append(story(STEPHENS, order, title, work_id, flags, blocks_until(head, stop)))
    return out


def hull(src):
    soup = soup_of(f"{src}/Cuchulain-the-Hound-of-Ulster_52963/*-h/*.htm")
    h2s = soup.find_all("h2")
    out = []
    for order, (title, work_id, flags, chapters) in enumerate(HULL_STORIES, 1):
        blocks = []
        for num, note in chapters:
            head = next(h for h in h2s if re.match(rf"CHAPTER {num} ", h2_text(h)))
            if note:
                blocks.append({"type": "note", "text": note})
            if len(chapters) > 1:
                blocks.append({"type": "heading", "text": h2_text(head).split(" ", 2)[2]})
            blocks += blocks_until(head, lambda el: el.name == "h2")
        out.append(story(HULL, order, title, work_id, flags, blocks))
    return out


def yeats(src):
    soup = soup_of(f"{src}/Fairy-and-Folk-Tales-of-the-Irish-Peasantry_33887/*-h/*.htm")
    head = next(h for h in soup.find_all("h2") if h2_text(h) == "A LEGEND OF KNOCKMANY.")
    blocks = [b for b in blocks_until(head, lambda el: el.name == "h2")]
    blocks.append({"type": "note", "text": "By William Carleton (1794–1869). The Giant's Causeway "
                   "stories are a later folk legend about Fionn, not part of the old Fenian tales."})
    return [story(YEATS, 1, "A Legend of Knockmany", "irish-fionn-causeway", [], blocks)]


def main(src):
    index = load_index()
    for col, stories in ((JOYCE, joyce(src)), (STEPHENS, stephens(src)), (HULL, hull(src)),
                         (YEATS, yeats(src))):
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:62} {st['wordCount']:5}w {st['readingMinutes']:3}m "
                  f"{lv['fkGrade']:5} {lv['band']:8} {st['flags']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
