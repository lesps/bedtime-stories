import json, re, sys
from pathlib import Path
from bs4 import BeautifulSoup
sys.path.insert(0, ".")
from build_compendium import clean, slug

SRC = next(Path("src").glob("Fairy-Tales-of-Hans*/27200-h/27200-h.htm"))
TARGETS = {"THE LITTLE MERMAID": "The Little Mermaid",
           "LITTLE TINY OR THUMBELINA": "Little Tiny; or, Thumbelina",
           "THE UGLY DUCKLING": "The Ugly Duckling"}
MATURE = {"andersen-27200--the-little-mermaid"}

soup = BeautifulSoup(SRC.read_text(encoding="utf-8", errors="replace"), "lxml")
for sp in soup.select("span.pagenum"):
    sp.decompose()
stories, cur = [], None
for el in soup.body.find_all(["h2", "h3", "p", "pre", "img"]):
    if el.name in ("h2", "h3"):
        t = el.get_text(" ", strip=True).upper()
        cur = None
        if t in TARGETS:
            cur = dict(title=TARGETS[t], blocks=[]); stories.append(cur)
        continue
    if cur is None or (el.name == "p" and el.find_parent("pre")):
        continue
    if el.name == "img":
        raise SystemExit("unexpected image")
    if el.name == "pre":
        txt = "\n".join(l.rstrip() for l in el.get_text().replace("\r", "").split("\n")).strip("\n")
        if txt.strip(): cur["blocks"].append(dict(type="verse", text=txt))
    else:
        txt = re.sub(r"\s+([,.;:!?’”])", r"\1", clean(el.get_text(" ")))
        if txt: cur["blocks"].append(dict(type="p", text=txt))

out = Path("patch/compendium/stories"); out.mkdir(parents=True, exist_ok=True)
entries = []
for i, s in enumerate(stories, 1):
    sid = f"andersen-27200--{slug(s['title'])}"
    words = len(" ".join(b["text"] for b in s["blocks"]).split())
    st = dict(id=sid, collectionId="andersen-27200", order=i, title=s["title"], origin=None,
              excluded=False, flags=["mature-themes"] if sid in MATURE else [],
              wordCount=words, readingMinutes=max(1, round(words / 180)), moral=None, blocks=s["blocks"])
    (out / f"{sid}.json").write_text(json.dumps(st, ensure_ascii=False, indent=1))
    entries.append({k: st[k] for k in ("id","collectionId","order","title","wordCount","readingMinutes","excluded","flags")} | {"hasImages": False})
coll = dict(id="andersen-27200", title="Fairy Tales of Hans Christian Andersen", author="Hans Christian Andersen",
            contributor=None, firstPublished=None, source="https://www.gutenberg.org/ebooks/27200",
            license="Public domain in the USA", storyCount=len(entries))
Path("patch/index.patch.json").write_text(json.dumps(dict(schemaVersion=1, addCollections=[coll], addStories=entries), ensure_ascii=False, indent=1))
idx = json.load(open("out/compendium/index.json"))
idx["collections"].insert(3, coll)
pos = max(i for i, s in enumerate(idx["stories"]) if s["collectionId"] == "andersen") + 1
idx["stories"][pos:pos] = entries
Path("patch/compendium/index.json").write_text(json.dumps(idx, ensure_ascii=False, indent=1))
for e in entries: print(e["id"], e["wordCount"], len(json.load(open(out/f"{e['id']}.json"))["blocks"]), e["flags"])
print("total stories", len(idx["stories"]))
