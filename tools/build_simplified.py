#!/usr/bin/env python3
"""Builds the simplified-retelling collections from tools/simplified/*.md.

Each Markdown file is one story, named `<storyId>.md`, with a small front matter:

    ---
    title: Theseus and the Minotaur
    adaptedFrom: hawthorne-tanglewood--the-minotaur
    order: 1
    namesNote: optional sentence about names that differ in the original
    flags: optional; "none" or a comma list, when the retelling leaves out what flagged the original
    alsoSimplifies: optional comma list of other versions of the same myth this retelling stands in for
    ---
    Paragraphs, separated by blank lines.

A legend with no public-domain text to work from (marked ‡ in the expansion plan) has no
original: its front matter gives `basedOn` (what it was retold from) and `workId` instead of
`adaptedFrom`, and its end note says that no source text was used.

The story inherits `workId` from its original, gets `adaptation`, `adaptedBy`, `adaptedFrom`
and `readingLevel`, and ends with a note naming the original. The original gets
`simplifiedId` pointing back, and so does every story in `alsoSimplifies` (which must share the
workId, or have none yet, in which case it is given this one). Edit the .md files, never the generated JSON, then run:

    python3 tools/build_simplified.py && python3 tools/tag_stories.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compendium_io import finish, load_index, load_story, save_index, sync_entry, upsert_collection  # noqa: E402

SRC = Path(__file__).parent / "simplified"
ADAPTED_BY = "Claude (Anthropic), 2026"

COLLECTIONS = {
    "myths-greek": {
        "id": "myths-greek",
        "title": "Greek Myths, Simply Told",
        "author": "Traditional (ancient Greek)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-roman": {
        "id": "myths-roman",
        "title": "Roman Myths, Simply Told",
        "author": "Traditional (ancient Roman)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-norse": {
        "id": "myths-norse",
        "title": "Norse Myths, Simply Told",
        "author": "Traditional (Old Norse)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-english": {
        "id": "myths-english",
        "title": "English Legends, Simply Told",
        "author": "Traditional (English)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-german": {
        "id": "myths-german",
        "title": "German Legends, Simply Told",
        "author": "Traditional (German)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-irish": {
        "id": "myths-irish",
        "title": "Irish Legends, Simply Told",
        "author": "Traditional (Irish)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-welsh": {
        "id": "myths-welsh",
        "title": "Welsh Legends, Simply Told",
        "author": "Traditional (Welsh)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-celtic": {
        "id": "myths-celtic",
        "title": "Scottish, Manx and Breton Legends, Simply Told",
        "author": "Traditional (Scottish, Manx and Breton)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
}


def parse(path):
    raw = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    if not m:
        raise SystemExit(f"{path.name}: missing front matter")
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines() if line.strip())
    paras = [re.sub(r"\s*\n\s*", " ", p).strip() for p in re.split(r"\n\s*\n", m.group(2))]
    return meta, [p for p in paras if p]


def flags_of(meta, orig):
    if "flags" not in meta:
        return orig["flags"]
    value = meta["flags"].strip()
    return [] if value == "none" else [f.strip() for f in value.split(",")]


def unsourced(sid, cid, meta, paras):
    """A retelling with no public-domain original to link to (‡ in the expansion plan)."""
    note = (f"Retold by {ADAPTED_BY}, from {meta['basedOn']}. No public-domain text of this "
            "legend could be used, so there is no original to compare it with.")
    return {
        "id": sid,
        "collectionId": cid,
        "order": int(meta["order"]),
        "title": meta["title"],
        "origin": None,
        "excluded": False,
        "flags": flags_of(meta, {"flags": []}),
        "moral": None,
        "blocks": [{"type": "p", "text": p} for p in paras] + [{"type": "note", "text": note}],
        "workId": meta["workId"],
        "adaptation": "retold",
        "adaptedBy": ADAPTED_BY,
    }


def main():
    index = load_index()
    by_collection = {cid: [] for cid in COLLECTIONS}
    originals, work_ids = {}, {}
    for path in sorted(SRC.glob("*.md")):
        sid = path.stem
        cid = sid.split("--")[0]
        if cid not in COLLECTIONS:
            raise SystemExit(f"{path.name}: unknown collection {cid}")
        meta, paras = parse(path)
        if "adaptedFrom" not in meta:
            by_collection[cid].append(finish(unsourced(sid, cid, meta, paras)))
            continue
        orig = load_story(meta["adaptedFrom"])
        coll = next(c for c in index["collections"] if c["id"] == orig["collectionId"])
        credit = f"{coll['author']}'s “{orig['title']}” in {coll['title']}"
        if (coll.get("contributor") or "").startswith("Translated by "):
            # The collection title names the poets; credit the translator instead.
            translator = coll["contributor"].removeprefix("Translated by ")
            credit = f"“{orig['title']}” in {coll['title']}, translated by {translator}"
        elif coll["author"].startswith("Various"):
            # An anthology ("Various", "Various (collected)"): name the book and its editor.
            credit = f"“{orig['title']}” in {coll['title']}"
            if (coll.get("contributor") or "").startswith("Edited by "):
                credit += ", edited by " + coll["contributor"].removeprefix("Edited by ")
        if coll.get("firstPublished"):
            credit += f" ({coll['firstPublished']})"
        note = f"A simplified retelling of {credit}. The original is listed under Other versions."
        if meta.get("namesNote"):
            note += " " + meta["namesNote"]
        story = {
            "id": sid,
            "collectionId": cid,
            "order": int(meta["order"]),
            "title": meta["title"],
            "origin": None,
            "excluded": orig["excluded"],
            "flags": flags_of(meta, orig),
            "moral": None,
            "blocks": [{"type": "p", "text": p} for p in paras] + [{"type": "note", "text": note}],
            "workId": orig["workId"],
            "adaptation": "simplified",
            "adaptedBy": ADAPTED_BY,
            "adaptedFrom": orig["id"],
        }
        if "source" in orig:
            story["source"] = orig["source"]
        by_collection[cid].append(finish(story))
        originals[orig["id"]] = sid
        for other in filter(None, (x.strip() for x in meta.get("alsoSimplifies", "").split(","))):
            originals[other] = sid
            work_ids[other] = orig["workId"]
    for cid, stories in by_collection.items():
        if stories:
            upsert_collection(index, COLLECTIONS[cid], sorted(stories, key=lambda s: s["order"]))
    for oid, sid in originals.items():
        orig = load_story(oid)
        if oid in work_ids:
            if orig.get("workId", work_ids[oid]) != work_ids[oid]:
                raise SystemExit(f"{oid}: workId {orig['workId']} differs from {work_ids[oid]}")
            orig["workId"] = work_ids[oid]
        orig["simplifiedId"] = sid
        sync_entry(index, orig)
    save_index(index)
    for stories in by_collection.values():
        for s in stories:
            print(f"{s['id']:55} {s['wordCount']:5} words {s['readingMinutes']:3} min  {s['readingLevel']}")


if __name__ == "__main__":
    main()
