"""Builds compendium patch 002 (Beatrix Potter) from GITenberg clones in this directory."""
import json, re, shutil, sys, warnings
from pathlib import Path
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from PIL import Image

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
sys.path.insert(0, "..")
from build_compendium import slug

ROOT = Path(".")
OUT = Path("../patch-002/compendium")
COLL = "potter"
MAX_W, QUALITY = 800, 72

# (repo dir prefix, title, first published, gutenberg id, start-of-story prefix, mode)
# mode: html = text+images from HTML; text582/text572 = text from compilation, images anchored from HTML
BOOKS = [
    ("The-Tale-of-Peter-Rabbit_14838", "The Tale of Peter Rabbit", 1902, 14838, "Once upon a time there were four little Rabbits", "html"),
    ("The-Tale-of-Squirrel-Nutkin", "The Tale of Squirrel Nutkin", 1903, 14872, "This is a Tale about a tail", "html"),
    ("The-Tailor-of-Gloucester", "The Tailor of Gloucester", 1903, 14868, "In the time of swords", "html"),
    ("The-Tale-of-Benjamin-Bunny", "The Tale of Benjamin Bunny", 1904, 14407, "One morning a little rabbit sat on a bank", "html"),
    ("The-Tale-of-Two-Bad-Mice", "The Tale of Two Bad Mice", 1904, 45264, "ONCE upon a time there was a very beautiful doll", "text582"),
    ("The-Tale-of-Mrs.-Tiggy-Winkle_15137", "The Tale of Mrs. Tiggy-Winkle", 1905, 15137, "Once upon a time there was a little girl called Lucie", "html"),
    ("The-Tale-of-the-Pie-and-the-Patty-Pan", "The Tale of the Pie and the Patty-Pan", 1905, 15234, "Once upon a time there was a Pussy-cat called Ribby", "html"),
    ("The-Tale-of-Mr.-Jeremy-Fisher", "The Tale of Mr. Jeremy Fisher", 1906, 15077, "Once upon a time there was a frog", "html"),
    ("The-Story-of-a-Fierce-Bad-Rabbit", "The Story of a Fierce Bad Rabbit", 1906, 45265, "This is a fierce bad Rabbit", "text572"),
    ("The-Story-of-Miss-Moppet", "The Story of Miss Moppet", 1906, 14848, "This is a Pussy called Miss Moppet", "html"),
    ("The-Tale-of-Tom-Kitten", "The Tale of Tom Kitten", 1907, 14837, "Once upon a time there were three little kittens", "html"),
    ("The-Tale-of-Jemima-Puddle-Duck", "The Tale of Jemima Puddle-Duck", 1908, 14814, "What a funny sight it is", "html"),
    ("The-Tale-of-Samuel-Whiskers", "The Tale of Samuel Whiskers; or, The Roly-Poly Pudding", 1908, 15575, "Once upon a time there was an old cat", "html"),
    ("The-Tale-of-the-Flopsy-Bunnies", "The Tale of the Flopsy Bunnies", 1909, 14220, "It is said that the effect of eating too much lettuce", "html"),
    ("The-Tale-of-Ginger-and-Pickles", "The Tale of Ginger and Pickles", 1909, 14877, "Once upon a time there was a village shop", "html"),
    ("The-Tale-of-Mrs.-Tittlemouse", "The Tale of Mrs. Tittlemouse", 1910, 17089, "Once upon a time there was a wood-mouse", "html"),
    ("The-Tale-of-Timmy-Tiptoes", "The Tale of Timmy Tiptoes", 1911, 14797, "Once upon a time there was a little fat comfortable grey squirrel", "html"),
    ("The-Tale-of-Mr.-Tod", "The Tale of Mr. Tod", 1912, 19805, "I have made many books about well-behaved people", "html"),
    (None, "The Tale of Pigling Bland", 1913, 582, "ONCE upon a time there was an old pig called Aunt Pettitoes", "text582"),
    ("The-Tale-of-Johnny-Town-Mouse", "The Tale of Johnny Town-Mouse", 1918, 15284, "Johnny Town-mouse was born in a cupboard", "html"),
    ("Cecily-Parsley", "Cecily Parsley's Nursery Rhymes", 1922, 23350, "Cecily Parsley lived in a pen", "html"),
]

STOP_HEAD = re.compile(r"THE END|TALE OF|STORY OF|BY BEATRIX|LIST OF|^FINIS|^THE ORIGINAL", re.I)
STOP_P = re.compile(r"^(THE END\.?|\*+\s*END OF|End of (the )?Project Gutenberg)", re.I)

def norm(t):
    return re.sub(r"[^a-z]", "", t.lower())

def fix_dropcap(t):
    # "ONCE upon" / "IT belonged" -> "Once upon" / "It belonged" (OCR'd drop caps in the compilations)
    return re.sub(r"^([A-Z])([A-Z]+)\b(?=\s+[a-z])", lambda m: m.group(1) + m.group(2).lower(), t)

def para_text(el):
    """Lines split only at <br>; source-file soft wraps are collapsed."""
    for br in el.find_all("br"):
        br.replace_with("\x00")
    raw = el.get_text().replace("\xa0", " ")
    lines = [re.sub(r"\s+", " ", l).strip() for l in raw.split("\x00")]
    return [l for l in lines if l]

def is_verse(lines):
    # Printed-page line breaks in prose start mid-sentence; verse lines start with a capital or quote.
    return len(lines) > 1 and all(re.match(r"[A-Z\"'“‘(]", l) for l in lines[1:])

def html_blocks(html_path, start):
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "lxml")
    for x in soup.select("span.pagenum"):
        x.decompose()
    blocks, started = [], False
    for el in soup.body.find_all(["h1", "h2", "h3", "h4", "p", "img"]):
        if el.find_parent("pre"):
            continue
        if el.name == "img":
            if started:
                a = el.find_parent("a")
                src = a["href"] if a is not None and re.search(r"\.(jpe?g|png|gif)$", a.get("href", ""), re.I) else el["src"]
                blocks.append(dict(type="image", src=src, alt=(el.get("alt") or "").strip()))
            continue
        lines = para_text(el)
        if not lines:
            continue
        text = " ".join(lines)
        if not started:
            if norm(text).startswith(norm(start)[:30]):
                started = True
            else:
                continue
        if el.name != "p":
            if STOP_HEAD.search(text):
                break
            blocks.append(dict(type="heading", text=text))
            continue
        if STOP_P.search(text):
            break
        if is_verse(lines):
            blocks.append(dict(type="verse", text="\n".join(lines)))
        else:
            blocks.append(dict(type="p", text=re.sub(r"\s+([,.;:!?])", r"\1", text)))
    if not started:
        raise SystemExit(f"start not found in {html_path}")
    while blocks and blocks[-1]["type"] == "image" and False:
        blocks.pop()
    return html_path.parent, blocks

def compilation_paras(txt_path, start):
    raw = txt_path.read_text(encoding="utf-8", errors="replace").replace("\r", "")
    i = raw.find(start)
    if i < 0:
        raise SystemExit(f"start not found in {txt_path}")
    rest = raw[i:]
    m = re.search(r"\n\s*THE (TALE|STORY) OF\b|\n\s*THE ROLY|\n\*\*\* ?END|\nEnd of (the )?Project Gutenberg", rest)
    body = rest[: m.start()] if m else rest
    paras = []
    for chunk in re.split(r"\n\s*\n", body):
        t = re.sub(r"\s+", " ", chunk).strip()
        if t and not re.fullmatch(r"THE END\.?", t):
            paras.append(fix_dropcap(t))
    return paras

def anchored(paras, html_path):
    """Text from a compilation; images placed before the paragraph they precede in the HTML book."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "lxml")
    seq = [("img", el) if el.name == "img" else ("p", " ".join(para_text(el))) for el in soup.body.find_all(["p", "img"])]
    imgs = [el for k, el in seq if k == "img"]
    html_ps = [t for k, t in seq if k == "p" and t]
    out = [dict(type="p", text=p) for p in paras]
    if not html_ps:
        # picture-only HTML: one story image per page, pair in order (cover/frontis/title page excluded)
        story_imgs = [i for i in imgs if not re.search(r"cover|frontis|titlepage", i["src"])]
        if len(story_imgs) != len(paras):
            raise SystemExit(f"cannot pair {len(story_imgs)} images with {len(paras)} paragraphs")
        res = []
        for img, b in zip(story_imgs, out):
            res += [dict(type="image", src=img["src"], alt=(img.get("alt") or "").strip()), b]
        return html_path.parent, res
    pending, inserts, prev = [], {}, 0
    for k, v in seq:
        if k == "img":
            if not re.search(r"cover|frontis|titlepage", v["src"]):
                pending.append(dict(type="image", src=v["src"], alt=(v.get("alt") or "").strip()))
        elif v and pending:
            idx = next((j for j, p in enumerate(paras) if j >= prev and norm(p)[:40] == norm(v)[:40]), None)
            if idx is not None:
                # spread the run of images evenly over the paragraphs since the last anchor
                span = max(1, idx - prev + 1)
                for n, img in enumerate(pending):
                    slot = prev + (n * span) // len(pending) if len(pending) > 1 else idx
                    inserts.setdefault(min(slot, idx), []).append(img)
                pending, prev = [], idx + 1
    res = []
    for j, b in enumerate(out):
        res += inserts.get(j, []) + [b]
    return html_path.parent, res + pending

def save_image(src_dir, src, sid):
    p = (src_dir / src).resolve()
    name = f"{sid.split('--')[1]}-{Path(src).stem}.webp"
    dst = OUT / "images" / COLL / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(p)
    im = im.convert("RGBA") if im.mode in ("P", "LA", "RGBA") else im.convert("RGB")
    if im.mode == "RGBA":
        bg = Image.new("RGB", im.size, "white"); bg.paste(im, mask=im.split()[3]); im = bg
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    im.save(dst, "WEBP", quality=QUALITY, method=6)
    return f"images/{COLL}/{name}"

def main():
    if OUT.parent.exists():
        shutil.rmtree(OUT.parent)
    (OUT / "stories").mkdir(parents=True)
    t582 = next(ROOT.glob("A-Collection-of-Beatrix-Potter-Stories_582/582.txt"))
    t572 = next(ROOT.glob("The-Great-Big-Treasury-of-Beatrix-Potter_572/*.txt"))
    entries = []
    for order, (prefix, title, year, gid, start, mode) in enumerate(BOOKS, 1):
        sid = f"{COLL}--{slug(title.split(';')[0])}"
        html = next(ROOT.glob(f"{prefix}*/*-h/*.htm*")) if prefix else None
        if mode == "html":
            src_dir, blocks = html_blocks(html, start)
        else:
            paras = compilation_paras(t582 if mode == "text582" else t572, start)
            src_dir, blocks = anchored(paras, html) if html else (None, [dict(type="p", text=p) for p in paras])
        seen = set()
        final = []
        for b in blocks:
            if b["type"] == "image":
                if b["src"] in seen:
                    continue
                seen.add(b["src"])
                b["src"] = save_image(src_dir, b["src"], sid)
            final.append(b)
        words = len(" ".join(b.get("text", "") for b in final).split())
        story = dict(id=sid, collectionId=COLL, order=order, title=title, origin=None, excluded=False, flags=[],
                     wordCount=words, readingMinutes=max(1, round(words / 180)), moral=None,
                     firstPublished=year, source=f"https://www.gutenberg.org/ebooks/{gid}", blocks=final)
        (OUT / "stories" / f"{sid}.json").write_text(json.dumps(story, ensure_ascii=False, indent=1))
        entries.append({k: story[k] for k in ("id", "collectionId", "order", "title", "wordCount", "readingMinutes", "excluded", "flags")}
                       | {"hasImages": any(b["type"] == "image" for b in final)})
        print(f"{sid:55} {mode:8} words={words:5} imgs={sum(b['type']=='image' for b in final):3} blocks={len(final)}")
    coll = dict(id=COLL, title="The Tales of Beatrix Potter", author="Beatrix Potter", contributor="Illustrated by the author",
                firstPublished=1902, source="https://www.gutenberg.org/ebooks/search/?query=beatrix+potter",
                license="Public domain in the USA", storyCount=len(entries))
    Path(OUT.parent / "index.patch.json").write_text(json.dumps(dict(schemaVersion=1, addCollections=[coll], addStories=entries), ensure_ascii=False, indent=1))
    base = json.loads(Path("../patch/compendium/index.json").read_text())
    base["collections"].append(coll)
    base["stories"] += entries
    (OUT / "index.json").write_text(json.dumps(base, ensure_ascii=False, indent=1))
    print("total stories", len(base["stories"]))

if __name__ == "__main__":
    main()
