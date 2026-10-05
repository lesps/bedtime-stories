"""Compendium patch 003: existing public-domain English translations of German and Japanese tales."""
import json, math, re, shutil, sys, warnings
from collections import Counter
from pathlib import Path
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from PIL import Image

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
sys.path.insert(0, "..")
from build_compendium import slug, title_case

BASE = Path("../patch-002/compendium")      # cumulative compendium after patches 001+002
PREV = Path("../out/compendium")            # original build (story files for the first 319)
OUT = Path("../patch-003/compendium")
MAX_W, QUALITY = 800, 72

# ---------- helpers ----------
def blocks_from_html(path, start_pred, stop_pred, story_level, skip_titles=()):
    """Split an HTML book into stories at `story_level` headings; returns [(title, blocks, src_dir)]."""
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "lxml")
    for x in soup.select("span.pagenum, p.caption"):
        x.decompose()
    stories, cur, started = [], None, False
    for el in soup.body.find_all(["h1", "h2", "h3", "h4", "p", "img", "div"]):
        if el.name == "div" and "poem" not in (el.get("class") or []):
            continue
        if el.find_parent("pre") or (el.name == "p" and el.find_parent("div", class_="poem")):
            continue
        if el.name == "img":
            if cur is not None:
                cur[1].append(dict(type="image", src=el["src"], alt=(el.get("alt") or "").strip()))
            continue
        for br in el.find_all("br"):
            br.replace_with("\x00")
        lines = [re.sub(r"\s+", " ", l).strip() for l in el.get_text().replace("\xa0", " ").split("\x00")]
        lines = [l for l in lines if l]
        if not lines:
            continue
        text = " ".join(lines)
        if el.name.startswith("h"):
            if stop_pred(text):
                break
            if el.name == story_level:
                if not started and not start_pred(text):
                    continue
                started = True
                if text.upper().rstrip(".") in skip_titles:
                    cur = None
                    continue
                cur = (text, [])
                stories.append(cur)
            elif cur is not None:
                cur[1].append(dict(type="heading", text=title_case(text)))
            continue
        if cur is None:
            continue
        if el.name == "div" or len(lines) > 1:
            cur[1].append(dict(type="verse", text="\n".join(lines)))
        else:
            cur[1].append(dict(type="p", text=re.sub(r"\s+([,.;:!?’”])", r"\1", text)))
    return [(t, b, path.parent) for t, b in stories if any(x["type"] != "image" for x in b)]

def save_image(src_dir, src, coll, sid):
    p = (src_dir / src).resolve()
    name = f"{sid.split('--')[1]}-{Path(src).stem}.webp"
    dst = OUT / "images" / coll / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(p)
    if im.mode in ("P", "LA", "RGBA"):
        im = im.convert("RGBA"); bg = Image.new("RGB", im.size, "white"); bg.paste(im, mask=im.split()[3]); im = bg
    else:
        im = im.convert("RGB")
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    im.save(dst, "WEBP", quality=QUALITY, method=6)
    return f"images/{coll}/{name}"

def words_of(blocks):
    return len(" ".join(b.get("text", "") for b in blocks).split())

SLURS = re.compile(r"\b(nigger|negro|darkie|darky|squaw|redskin|hottentot|chinaman)s?\b", re.I)
JEW = re.compile(r"\bjews?\b", re.I)

# ---------- Hunt (Grimm, complete) ----------
def hunt():
    raw = Path("hunt.txt").read_text()
    body_start = raw.index("\n1 The Frog-King, or Iron Henry\n")
    end = raw.index("*** END OF THE PROJECT GUTENBERG")
    contents = raw[:body_start]
    # German titles from the contents (entries may wrap onto an indented line)
    german = {}
    for m in re.finditer(r"^\s*((?:Legend )?\d+) (.+?)\((.+?)\)\s*$", re.sub(r"\n {4,}", " ", contents), re.M):
        german[m.group(1)] = re.sub(r"\s+", " ", m.group(3)).strip()
    body = raw[body_start:end]
    parts = re.split(r"\n *((?:Legend )?\d+) ([^\n]+)\n", "\n" + body)
    out = []
    for i in range(1, len(parts), 3):
        num, title, text = parts[i], parts[i + 1].strip(), parts[i + 2]
        paras = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
        blocks = []
        for p in paras:
            if not p:
                continue
            # verse: original lines short and indented
            blocks.append(dict(type="p", text=p))
        # restore verse where the source indents lines
        blocks = verse_fix(text, blocks)
        legend = num.startswith("Legend")
        n = int(num.split()[-1])
        out.append(dict(num=num, n=n, legend=legend, title=title, german=german.get(num), blocks=blocks,
                         workId=(f"grimm-kl-{n:02d}" if legend else f"grimm-khm-{n:03d}")))
    return out

def verse_fix(text, blocks):
    out = []
    for chunk in re.split(r"\n\s*\n", text):
        lines = [l for l in chunk.split("\n") if l.strip()]
        if not lines:
            continue
        if len(lines) > 1 and all(l.startswith((" ", "\t")) for l in lines):
            out.append(dict(type="verse", text="\n".join(l.strip() for l in lines)))
        else:
            out.append(dict(type="p", text=re.sub(r"\s+", " ", chunk).strip()))
    return out

# ---------- similarity linking ----------
def tokens(blocks, n=400):
    w = re.findall(r"[a-z]+", " ".join(b.get("text", "") for b in blocks).lower())
    return Counter(w[:n])

def link(candidates, targets, threshold):
    """candidates: [(id, blocks)]; targets: [(workId, blocks)] -> {id: (workId, score)}"""
    docs = [tokens(b) for _, b in targets]
    df = Counter(t for d in docs for t in d)
    N = len(docs)
    idf = {t: math.log(N / df[t]) for t in df}
    def vec(c):
        v = {t: c[t] * idf.get(t, math.log(N)) for t in c}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1
        return {t: x / norm for t, x in v.items()}
    tv = [vec(d) for d in docs]
    res = {}
    for cid, b in candidates:
        cv = vec(tokens(b))
        scores = [sum(cv.get(t, 0) * x for t, x in v.items()) for v in tv]
        best = max(range(N), key=scores.__getitem__)
        if scores[best] >= threshold:
            res[cid] = (targets[best][0], round(scores[best], 3))
    return res

# ---------- Japanese work ids (manual, both books) ----------
JA_WORK = {
    "urashima": ["the-story-of-urashima-taro-the-fisher-lad", "urashima"],
    "momotaro": ["momotaro-or-the-story-of-the-son-of-a-peach", "momotaro"],
    "tongue-cut-sparrow": ["the-tongue-cut-sparrow"],
    "matsuyama-mirror": ["the-mirror-of-matsuyama", "the-matsuyama-mirror"],
    "jellyfish-and-monkey": ["the-jelly-fish-and-the-monkey", "the-jelly-fish-takes-a-journey"],
    "hanasaka-jiji": ["the-story-of-the-old-man-who-made-withered-trees-to-flower", "hana-saka-jiji"],
    "bamboo-cutter": ["the-bamboo-cutter-and-the-moon-child", "the-moon-maiden"],
    "happy-hunter": ["the-happy-hunter-and-the-skillful-fisher", "the-sea-king-and-the-magic-jewels"],
}

MATURE = {
    # Hunt
    "grimm-hunt--the-juniper-tree", "grimm-hunt--the-robber-bridegroom", "grimm-hunt--fitcher-s-bird",
    "grimm-hunt--the-girl-without-hands", "grimm-hunt--the-wilful-child",
    "grimm-hunt--the-three-army-surgeons", "grimm-hunt--the-singing-bone", "grimm-hunt--the-death-of-the-little-hen",
    "grimm-hunt--godfather-death", "grimm-hunt--the-godfather", "grimm-hunt--mrs-trudy", "grimm-hunt--frau-trude",
    "grimm-hunt--the-three-snake-leaves", "grimm-hunt--the-poor-boy-in-the-grave", "grimm-hunt--the-shroud",
    "grimm-hunt--the-bright-sun-brings-it-to-light", "grimm-hunt--the-grave-mound",
    # Grace James
    "japan-james--the-peony-lantern", "japan-james--the-bell-of-dojoji", "japan-james--karma",
    "japan-james--the-sad-story-of-the-yaoyas-daughter", "japan-james--tamamo-the-fox-maiden",
    "japan-james--the-land-of-yomi", "japan-james--the-nurse",
    # Ozaki
    "japan-ozaki--the-goblin-of-adachigahara",
    # Busch
    "busch-max-maurice--max-and-maurice",
}
EXCLUDE_TERMS = {"grimm-hunt--the-jew-among-thorns": "antisemitic-caricature",
                 "grimm-hunt--the-good-bargain": "antisemitic-caricature"}
# reviewed by hand: "Redskin" is the fox's name here; the Jewish character in KHM 115 is the murder victim
SLUR_FALSE_POSITIVE = {"grimm-hunt--the-wishing-table-the-gold-ass-and-the-cudgel-in-the-sack"}
JEW_REVIEWED_OK = {"grimm-hunt--the-bright-sun-brings-it-to-light"}

def main():
    if OUT.parent.exists():
        shutil.rmtree(OUT.parent)
    (OUT / "stories").mkdir(parents=True)
    index = json.loads((BASE / "index.json").read_text())
    new_colls, new_stories = [], []

    def emit(coll, order, title, blocks, src_dir=None, **extra):
        sid = f"{coll}--{slug(title)}"
        for b in blocks:
            if b["type"] == "image":
                b["src"] = save_image(src_dir, b["src"], coll, sid)
        w = words_of(blocks)
        text = " ".join(b.get("text", "") for b in blocks)
        flags = []
        if sid in MATURE:
            flags.append("mature-themes")
        if SLURS.search(text) and sid not in SLUR_FALSE_POSITIVE:
            flags.append("racial-slur")
        if sid in EXCLUDE_TERMS:
            flags.append(EXCLUDE_TERMS[sid])
        elif JEW.search(text) and sid not in JEW_REVIEWED_OK:
            flags.append("antisemitic-caricature-review")
        excluded = sid in EXCLUDE_TERMS or "racial-slur" in flags
        st = dict(id=sid, collectionId=coll, order=order, title=title, origin=None, excluded=excluded,
                  flags=flags, wordCount=w, readingMinutes=max(1, round(w / 180)), moral=None)
        st.update({k: v for k, v in extra.items() if v is not None})
        st["blocks"] = blocks
        (OUT / "stories" / f"{sid}.json").write_text(json.dumps(st, ensure_ascii=False, indent=1))
        entry = {k: st[k] for k in ("id", "collectionId", "order", "title", "wordCount", "readingMinutes", "excluded", "flags")}
        if "workId" in st:
            entry["workId"] = st["workId"]
        entry["hasImages"] = any(b["type"] == "image" for b in blocks)
        new_stories.append(entry)
        return sid

    # Hunt
    h = hunt()
    for i, t in enumerate(h, 1):
        title = t["title"].replace("Frog-King", "Frog-King")
        emit("grimm-hunt", i, title, t["blocks"], workId=t["workId"], originalTitle=t["german"])
    new_colls.append(dict(id="grimm-hunt", title="Household Tales", author="Jacob and Wilhelm Grimm",
                          contributor="Translated by Margaret Hunt", firstPublished=1884, language="en",
                          originalLanguage="de", source="https://www.gutenberg.org/ebooks/5314",
                          license="Public domain in the USA", storyCount=len(h)))

    # Ozaki
    oz = blocks_from_html(next(Path(".").glob("Japanese-Fairy-Tales_4018/*-h/*.htm")),
                          lambda t: "BAG OF RICE" in t.upper(), lambda t: False, "h3")
    for i, (t, b, d) in enumerate(oz, 1):
        title = title_case(re.sub(r"\.?\s+(A STORY OF OLD JAPAN|AN OLD CHINESE STORY)\.?$", "", t, flags=re.I))
        title = title.replace("Shinansha", "Shinansha")
        emit("japan-ozaki", i, title, b, d)
    new_colls.append(dict(id="japan-ozaki", title="Japanese Fairy Tales", author="Traditional",
                          contributor="Compiled and translated by Yei Theodora Ozaki", firstPublished=1903,
                          language="en", originalLanguage="ja", source="https://www.gutenberg.org/ebooks/4018",
                          license="Public domain in the USA", storyCount=len(oz)))

    # Grace James
    gj = blocks_from_html(next(Path(".").glob("Japanese-Fairy-Tales_35853/*-h/*.htm")),
                          lambda t: t.upper().startswith("I GREEN WILLOW"), lambda t: t.lower().startswith("transcriber"), "h2")
    for i, (t, b, d) in enumerate(gj, 1):
        title = title_case(re.sub(r"^[IVXL]+\s+", "", t)).replace("Dōjōji", "Dōjōji")
        emit("japan-james", i, title, b, d)
    new_colls.append(dict(id="japan-james", title="Japanese Fairy Tales", author="Traditional",
                          contributor="Retold by Grace James, illustrated by Warwick Goble", firstPublished=1910,
                          language="en", originalLanguage="ja", source="https://www.gutenberg.org/ebooks/35853",
                          license="Public domain in the USA", storyCount=len(gj)))

    # Max and Maurice: one story, tricks as headings
    mm = blocks_from_html(next(Path(".").glob("Max-and-Maurice*/*-h/*.htm")),
                          lambda t: t.upper().startswith("TRICK FIRST"), lambda t: "NONSENSE BOOKS" in t.upper(), "__none__")
    soup_blocks = []
    path = next(Path(".").glob("Max-and-Maurice*/*-h/*.htm"))
    # treat every h2 from TRICK FIRST to CONCLUSION as an in-story heading
    for t, b, d in blocks_from_html(path, lambda t: t.upper().startswith("TRICK FIRST"), lambda t: "NONSENSE BOOKS" in t.upper(), "h2"):
        soup_blocks.append(dict(type="heading", text=title_case(t)))
        soup_blocks += b
    emit("busch-max-maurice", 1, "Max and Maurice", soup_blocks, path.parent)
    new_colls.append(dict(id="busch-max-maurice", title="Max and Maurice: A Juvenile History in Seven Tricks",
                          author="Wilhelm Busch", contributor="Translated by Charles T. Brooks", firstPublished=1871,
                          language="en", originalLanguage="de", source="https://www.gutenberg.org/ebooks/28847",
                          license="Public domain in the USA", storyCount=1))

    # ---- workId linking for existing collections ----
    ids_by_coll = lambda c: [s for s in new_stories if s["collectionId"] == c]
    hunt_targets = [(s["workId"], json.loads((OUT / "stories" / f"{s['id']}.json").read_text())["blocks"]) for s in ids_by_coll("grimm-hunt")]
    def load_prev(sid):
        for base in (PREV, Path("../patch/compendium"), BASE):
            p = base / "stories" / f"{sid}.json"
            if p.exists():
                return json.loads(p.read_text())
    updated = {}
    cands = [(s["id"], load_prev(s["id"])["blocks"]) for s in index["stories"] if s["collectionId"] in ("grimm", "lang-blue", "jacobs-english")]
    links = link(cands, hunt_targets, 0.35)
    # Taylor titles that diverge too far from Hunt for the similarity pass (checked by hand)
    MANUAL = {"grimm--the-travelling-musicians": "grimm-khm-027", "grimm--briar-rose": "grimm-khm-050",
              "grimm--the-adventures-of-chanticleer-and-partlet": "grimm-khm-010", "grimm--tom-thumb": "grimm-khm-037",
              "grimm--the-miser-in-the-bush": "grimm-khm-110", "grimm--the-four-clever-brothers": "grimm-khm-129",
              "grimm--lily-and-the-lion": "grimm-khm-088"}
    for k, v in MANUAL.items():
        links[k] = (v, None)
    for sid, (wid, score) in links.items():
        st = load_prev(sid); st["workId"] = wid; updated[sid] = (st, score)
    # Japanese: manual
    slug_to_work = {sl: w for w, sls in JA_WORK.items() for sl in sls}
    for s in new_stories:
        if s["collectionId"] in ("japan-ozaki", "japan-james"):
            wid = slug_to_work.get(s["id"].split("--")[1])
            if wid:
                s["workId"] = f"ja-{wid}"
                p = OUT / "stories" / f"{s['id']}.json"
                st = json.loads(p.read_text()); st["workId"] = s["workId"]; p.write_text(json.dumps(st, ensure_ascii=False, indent=1))

    for sid, (st, _) in updated.items():
        (OUT / "stories" / f"{sid}.json").write_text(json.dumps(st, ensure_ascii=False, indent=1))
    for s in index["stories"]:
        if s["id"] in updated:
            s["workId"] = updated[s["id"]][0]["workId"]

    # language on every collection
    for c in index["collections"]:
        c.setdefault("language", "en")
        c.setdefault("originalLanguage", {"grimm": "de", "andersen": "da", "andersen-27200": "da"}.get(c["id"], "en"))
    index["collections"] += new_colls
    index["stories"] += new_stories
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1))
    Path(OUT.parent / "index.patch.json").write_text(json.dumps(dict(
        schemaVersion=1, addCollections=new_colls, addStories=new_stories,
        updateStories={sid: {"workId": st["workId"]} for sid, (st, _) in updated.items()},
        updateCollections={c["id"]: {"language": c["language"], "originalLanguage": c["originalLanguage"]} for c in index["collections"] if c not in new_colls},
    ), ensure_ascii=False, indent=1))
    Path("links.json").write_text(json.dumps({k: v for k, v in sorted(links.items())}, indent=1))
    for c in new_colls:
        print(c["id"], c["storyCount"])
    print("linked existing:", len(updated), "| total stories", len(index["stories"]))

if __name__ == "__main__":
    main()
