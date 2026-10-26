#!/usr/bin/env python3
"""Builds Claude's own translations of ancient sources from tools/translations/*.md.

Used where a myth has no public-domain English source to extract. Each Markdown file is one
story, named `<storyId>.md`; the collection is the id's prefix:

    ---
    title: Tages
    order: 1
    workId: etruscan-tages
    flags: optional comma list (default none)
    sources: the Latin of Cicero (ed. Müller, Teubner, 1915) and ...
    ---
    ## Cicero, On Divination 2.50–51      -> heading block naming the passage
    Note: context for the passage         -> note block
    > a line of verse                     -> verse block (every line of the paragraph starts
    > and the next line                      with "> "; line breaks are kept)
    Paragraphs of translation, separated by blank lines.

The story ends with a note naming the translator and the editions translated from. Run before
build_simplified.py, which links retellings to these stories:

    python3 tools/build_translations.py && python3 tools/build_simplified.py && python3 tools/tag_stories.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

SRC = Path(__file__).parent / "translations"
TRANSLATOR = "Claude (Anthropic), 2026"
COMMON = {
    "contributor": f"Translated by {TRANSLATOR}",
    "firstPublished": None,
    "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/translations",
    "license": "Public domain in the USA",
    "language": "en",
}
COLLECTIONS = {
    "greek-sources": {
        **COMMON,
        "id": "greek-sources",
        "title": "Myths from the Greek Writers",
        "author": "Homer, Pindar, Apollodorus and Pausanias",
        "originalLanguage": "el",
    },
    "latin-sources": {
        **COMMON,
        "id": "latin-sources",
        "title": "Myths from the Latin Writers",
        "author": "Cicero and Ovid",
        "originalLanguage": "la",
    },
    "norse-sources": {
        **COMMON,
        "id": "norse-sources",
        "title": "Myths from the Norse Writers",
        "author": "Snorri Sturluson and the Eddic poets",
        "originalLanguage": "is",
    },
    "german-sources": {
        **COMMON,
        "id": "german-sources",
        "title": "Legends from the German Poets",
        "author": "Clemens Brentano, Heinrich Heine and Gottfried August Bürger",
        "originalLanguage": "de",
    },
}


def parse(path):
    m = re.match(r"---\n(.*?)\n---\n(.*)", path.read_text(), re.S)
    if not m:
        raise SystemExit(f"{path.name}: missing front matter")
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines() if line.strip())
    blocks = []
    for para in re.split(r"\n\s*\n", m.group(2)):
        lines = [line.strip() for line in para.strip().splitlines()]
        if lines and all(line.startswith(">") for line in lines):
            blocks.append({"type": "verse", "text": "\n".join(line[1:].strip() for line in lines)})
            continue
        text = re.sub(r"\s*\n\s*", " ", para).strip()
        if not text:
            continue
        if text.startswith("## "):
            blocks.append({"type": "heading", "text": text[3:]})
        elif text.startswith("Note: "):
            blocks.append({"type": "note", "text": text[len("Note: "):]})
        else:
            blocks.append({"type": "p", "text": text})
    return meta, blocks


def main():
    index = load_index()
    by_collection = {cid: [] for cid in COLLECTIONS}
    for path in sorted(SRC.glob("*.md")):
        sid = path.stem
        cid = sid.split("--")[0]
        if cid not in COLLECTIONS:
            raise SystemExit(f"{path.name}: unknown collection {cid}")
        meta, blocks = parse(path)
        flags = [f.strip() for f in meta.get("flags", "").split(",") if f.strip() and f.strip() != "none"]
        blocks.append({"type": "note", "text": f"Translated by {TRANSLATOR}, from {meta['sources']}."})
        by_collection[cid].append(finish({
            "id": sid,
            "collectionId": cid,
            "order": int(meta["order"]),
            "title": meta["title"],
            "origin": None,
            "excluded": False,
            "flags": flags,
            "moral": None,
            "blocks": blocks,
            "workId": meta["workId"],
        }))
    for cid, stories in by_collection.items():
        if stories:
            upsert_collection(index, COLLECTIONS[cid], sorted(stories, key=lambda s: s["order"]))
    save_index(index)
    for stories in by_collection.values():
        for s in stories:
            print(f"{s['id']:52} {s['wordCount']:5} words {s['readingMinutes']:3} min  {s['readingLevel']}")


if __name__ == "__main__":
    main()
