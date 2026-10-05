import json, re, shutil, unicodedata
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

SRC = Path("src")
OUT = Path("out/compendium")

SOURCES = [
    dict(id="aesop", dir="The-Aesop-for-Children--13-With-pictures-by-Milo-Winter_19994", gid=19994,
         title="The Aesop for Children", author="Aesop", contributor="Illustrated by Milo Winter", year=1919,
         skip={"MILO WINTER", "A LIST OF THE FABLES", "THE ÆSOP FOR CHILDREN"}),
    dict(id="grimm", dir="Grimms-Fairy-Tales_2591", gid=2591,
         title="Grimms' Fairy Tales", author="Jacob and Wilhelm Grimm",
         contributor="Translated by Edgar Taylor and Marian Edwardes", year=1823,
         skip={"BY THE BROTHERS GRIMM"}),
    dict(id="andersen", dir="Andersen-s-Fairy-Tales_1597", gid=1597,
         title="Andersen's Fairy Tales", author="Hans Christian Andersen", contributor=None, year=None,
         skip={"BY HANS CHRISTIAN ANDERSEN"}),
    dict(id="lang-blue", dir="The-Blue-Fairy-Book_503", gid=503,
         title="The Blue Fairy Book", author="Various", contributor="Edited by Andrew Lang", year=1889,
         skip={"BY VARIOUS", "EDITED BY ANDREW LANG"}),
    dict(id="jacobs-english", dir="English-Fairy-Tales_7439", gid=7439,
         title="English Fairy Tales", author="Various (collected)", contributor="Edited by Joseph Jacobs", year=1890,
         skip={"BY ANONYMOUS", "HOW TO GET INTO THIS BOOK.", "PREFACE", "NOTES AND REFERENCES"}),
    dict(id="kipling-justso", dir="Just-So-Stories_2781", gid=2781,
         title="Just So Stories", author="Rudyard Kipling", contributor=None, year=1902,
         skip={"BY RUDYARD KIPLING"}),
]

SMALL = {"a", "an", "and", "the", "of", "in", "on", "to", "with", "at", "by", "for", "or"}

TITLE_OVERRIDES = {
    "grimm--little-red-cap-little-red-riding-hood": "Little Red-Cap (Little Red Riding Hood)",
    "lang-blue--the-water-lily-the-gold-spinners": "The Water-Lily; or, The Gold-Spinners",
    "lang-blue--the-master-cat-or-puss-in-boots": "The Master Cat; or, Puss in Boots",
    "lang-blue--cinderella-or-the-little-glass-slipper": "Cinderella; or, The Little Glass Slipper",
}

# Editorial judgment, not exhaustive. "excluded" = hidden by default; "mature" = parental filter.
FLAGS = {
    "kipling-justso--how-the-leopard-got-his-spots": {"excluded": True, "flags": ["racial-slur"]},
}
MATURE = {
    "grimm--the-juniper-tree", "grimm--the-robber-bridegroom", "andersen--the-red-shoes",
    "andersen--the-little-match-girl", "andersen--the-story-of-a-mother", "lang-blue--blue-beard",
    "jacobs-english--mr-fox", "jacobs-english--the-rose-tree", "jacobs-english--binnorie",
    "jacobs-english--the-golden-arm", "andersen--the-shadow",
}

def title_case(s):
    s = re.sub(r"\s+", " ", s).strip().rstrip(".")
    words = s.lower().split(" ")
    out = []
    for i, w in enumerate(words):
        if i and w in SMALL:
            out.append(w)
        else:
            out.append("-".join(p[:1].upper() + p[1:] for p in w.split("-")))
    return " ".join(out).replace("’S", "’s").replace("'S", "'s")

def slug(s):
    s = unicodedata.normalize("NFKD", s).replace("Æ", "AE").replace("æ", "ae")
    s = s.encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def clean(t):
    t = t.replace("\r", "").replace("\xa0", " ")
    return re.sub(r"[ \t]+", " ", re.sub(r"\s*\n\s*", " ", t)).strip()

def strip_noise(soup):
    for sp in soup.select("span.pagenum, a.pginternal, div.mynote"):
        sp.decompose()

def parse(src):
    html_path = next((SRC / src["dir"]).glob("*-h/*.htm"))
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "lxml")
    strip_noise(soup)
    # cut Gutenberg license footer
    stories, cur = [], None
    for el in soup.body.find_all(["h2", "p", "pre", "img"]):
        if el.name == "h2":
            raw = el.get_text(" ", strip=True)
            if raw.upper() in src["skip"]:
                cur = None
                continue
            if re.fullmatch(r"CHAPTER [IVXLC]+\.?", raw.upper()) and stories:
                cur = stories[-1]
                cur["blocks"].append(dict(type="heading", text="Chapter " + raw.split()[1].rstrip(".")))
                continue
            cur = dict(title=title_case(raw), blocks=[])
            stories.append(cur)
            continue
        if cur is None:
            continue
        txt_all = el.get_text(" ", strip=True)
        if "Project Gutenberg" in txt_all or "END OF THE PROJECT" in txt_all.upper():
            cur = None
            continue
        if el.name == "img":
            parent_a = el.find_parent("a")
            full = parent_a["href"] if parent_a and parent_a.get("href", "").startswith("images/") else el["src"]
            cur["blocks"].append(dict(type="image", src=full, alt=el.get("alt", "")))
        elif el.name == "pre":
            lines = [l.rstrip() for l in el.get_text().replace("\r", "").split("\n")]
            text = "\n".join(lines).strip("\n")
            if text.strip():
                cur["blocks"].append(dict(type="verse", text=text))
        elif el.name == "p":
            if "toc" in (el.get("class") or []) or el.find_parent("pre"):
                continue
            text = clean(el.get_text(" "))
            text = re.sub(r"\s+([,.;:!?’”])", r"\1", text)
            if not text:
                continue
            if src["id"] == "aesop" and "center" in (el.get("class") or []) and el.find("i"):
                cur["blocks"].append(dict(type="moral", text=text))
            else:
                cur["blocks"].append(dict(type="p", text=text))
    return html_path.parent, [s for s in stories if any(b["type"] != "image" for b in s["blocks"])]

FN = re.compile(r"\s?\((\d)\)")

def footnotes(blocks):
    """Trailing '(1) Source.' -> origin; mid-story '(n) note' -> note block. Inline markers removed."""
    origin = None
    if blocks and blocks[-1].get("type") == "p" and re.match(r"\(\d\) ", blocks[-1]["text"]):
        origin = blocks.pop()["text"][4:].strip()
    out = []
    for b in blocks:
        if b.get("type") == "p" and re.match(r"\(\d\) ", b["text"]):
            out.append(dict(type="note", text=b["text"][4:].strip()))
            continue
        if "text" in b:
            b["text"] = FN.sub("", b["text"])
        out.append(b)
    return origin, out

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "stories").mkdir(parents=True)
    collections, index = [], []
    for src in SOURCES:
        html_dir, stories = parse(src)
        ids_seen = set()
        for i, s in enumerate(stories):
            sid = f"{src['id']}--{slug(s['title'])}"
            while sid in ids_seen:
                sid += "-2"
            ids_seen.add(sid)
            title = TITLE_OVERRIDES.get(sid, s["title"])
            origin, s["blocks"] = footnotes(s["blocks"])
            for b in s["blocks"]:
                if b["type"] == "image":
                    dst = OUT / "images" / src["id"] / Path(b["src"]).name
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(html_dir / b["src"], dst)
                    b["src"] = f"images/{src['id']}/{dst.name}"
            text = " ".join(b.get("text", "") for b in s["blocks"])
            words = len(text.split())
            moral = next((b["text"] for b in s["blocks"] if b["type"] == "moral"), None)
            fl = FLAGS.get(sid, {})
            flags = fl.get("flags", []) + (["mature-themes"] if sid in MATURE else [])
            story = dict(id=sid, collectionId=src["id"], order=i + 1, title=title, origin=origin,
                         excluded=fl.get("excluded", False), flags=flags,
                         wordCount=words, readingMinutes=max(1, round(words / 180)),
                         moral=moral, blocks=s["blocks"])
            (OUT / "stories" / f"{sid}.json").write_text(json.dumps(story, ensure_ascii=False, indent=1))
            index.append({k: story[k] for k in ("id", "collectionId", "order", "title", "wordCount", "readingMinutes", "excluded", "flags")}
                         | {"hasImages": any(b["type"] == "image" for b in s["blocks"])})
        collections.append(dict(id=src["id"], title=src["title"], author=src["author"],
                                contributor=src["contributor"], firstPublished=src["year"],
                                source=f"https://www.gutenberg.org/ebooks/{src['gid']}",
                                license="Public domain in the USA", storyCount=len(stories)))
    (OUT / "index.json").write_text(json.dumps(dict(schemaVersion=1, collections=collections, stories=index),
                                               ensure_ascii=False, indent=1))
    for c in collections:
        print(c["id"], c["storyCount"])
    print("total", len(index))

if __name__ == "__main__":
    main()
