"""Shared helpers for adding collections to public/compendium. Run tools from the repo root.

Story files and index.json are written the way the original build wrote them
(indent=1, UTF-8, no trailing newline). `upsert_collection` replaces a collection and its
stories in place, so every extractor can be rerun safely.
"""
import json
from pathlib import Path

from readability import level

ROOT = Path("public/compendium")
ENTRY_KEYS = ("id", "collectionId", "order", "title", "wordCount", "readingMinutes", "excluded", "flags")
# Optional fields carried into index entries when a story has them (see CLAUDE.md, data contract).
OPTIONAL_ENTRY_KEYS = ("workId", "readingLevel", "simplifiedId", "adaptedFrom")


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1)


def load_index():
    return json.loads((ROOT / "index.json").read_text())


def save_index(index):
    (ROOT / "index.json").write_text(dump(index))


def load_story(sid):
    return json.loads((ROOT / "stories" / f"{sid}.json").read_text())


def save_story(story):
    (ROOT / "stories" / f"{story['id']}.json").write_text(dump(story))


def word_count(blocks):
    return len(" ".join(b["text"] for b in blocks if "text" in b).split())


def finish(story):
    """Fill the derived fields (wordCount, readingMinutes, readingLevel) from the blocks."""
    words = word_count(story["blocks"])
    story["wordCount"] = words
    story["readingMinutes"] = max(1, round(words / 180))
    story["readingLevel"] = level(story["blocks"])
    return story


def entry_of(story):
    e = {k: story[k] for k in ENTRY_KEYS}
    e["hasImages"] = any(b["type"] == "image" for b in story["blocks"])
    for k in OPTIONAL_ENTRY_KEYS:
        if k in story:
            e[k] = story[k]
    return e


def upsert_collection(index, collection, stories):
    """Replace `collection` and its stories in the index (append if new) and write story files."""
    cid = collection["id"]
    collection = {**collection, "storyCount": len(stories)}
    ids = [i for i, c in enumerate(index["collections"]) if c["id"] == cid]
    if ids:
        index["collections"][ids[0]] = collection
    else:
        index["collections"].append(collection)
    old = [s for s in index["stories"] if s["collectionId"] == cid]
    for s in old:
        p = ROOT / "stories" / f"{s['id']}.json"
        if p.exists():
            p.unlink()
    first = next((i for i, s in enumerate(index["stories"]) if s["collectionId"] == cid), None)
    index["stories"] = [s for s in index["stories"] if s["collectionId"] != cid]
    entries = []
    for st in stories:
        save_story(st)
        entries.append(entry_of(st))
    pos = len(index["stories"]) if first is None else first
    index["stories"][pos:pos] = entries
    return index


def sync_entry(index, story):
    """Rewrite one story file and its index entry after a field change."""
    save_story(story)
    for i, e in enumerate(index["stories"]):
        if e["id"] == story["id"]:
            index["stories"][i] = entry_of(story)
            return
    raise KeyError(story["id"])
