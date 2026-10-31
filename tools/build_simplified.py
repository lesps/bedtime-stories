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
`adaptedFrom`, and its end note says there is no original in the app to compare it with.

The story inherits `workId` from its original, gets `adaptation`, `adaptedBy`, `adaptedFrom`
and `readingLevel`, and ends with a note naming the original (and, if the original is hidden by default, the setting
that shows it). The original gets
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
# Settings labels (src/pages/SettingsPage.tsx) for the flags that hide a story by default.
# Retellings inherit `excluded`, so only a flag the retelling drops can hide its original.
SETTING_FOR_FLAG = {"mature-themes": "Show stories with mature themes"}

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
    "myths-arthurian": {
        "id": "myths-arthurian",
        "title": "Arthurian Legends, Simply Told",
        "author": "Traditional (Arthurian)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-finnic": {
        "id": "myths-finnic",
        "title": "Finnish, Estonian and Sámi Legends, Simply Told",
        "author": "Traditional (Finnish, Estonian and Sámi)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-baltic": {
        "id": "myths-baltic",
        "title": "Lithuanian and Latvian Legends, Simply Told",
        "author": "Traditional (Lithuanian and Latvian)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-west-slavic": {
        "id": "myths-west-slavic",
        "title": "Polish and Czech Legends, Simply Told",
        "author": "Traditional (Polish and Czech)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-balkan": {
        "id": "myths-balkan",
        "title": "Serbian, Romanian and Albanian Legends, Simply Told",
        "author": "Traditional (Serbian, Romanian and Albanian)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-hungarian": {
        "id": "myths-hungarian",
        "title": "Hungarian Legends, Simply Told",
        "author": "Traditional (Hungarian)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-caucasus": {
        "id": "myths-caucasus",
        "title": "Legends of the Caucasus, Simply Told",
        "author": "Traditional (Circassian and Georgian)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-basque": {
        "id": "myths-basque",
        "title": "Basque Legends, Simply Told",
        "author": "Traditional (Basque)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-egyptian": {
        "id": "myths-egyptian",
        "title": "Egyptian Myths, Simply Told",
        "author": "Traditional (Egyptian)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-hittite-canaanite": {
        "id": "myths-hittite-canaanite",
        "title": "Hittite and Canaanite Myths, Simply Told",
        "author": "Traditional (Hittite, Hurrian and Canaanite)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-mesopotamian": {
        "id": "myths-mesopotamian",
        "title": "Mesopotamian Myths, Simply Told",
        "author": "Traditional (Mesopotamian)",
        "contributor": "Simplified retellings by Claude (Anthropic), 2026",
        "firstPublished": None,
        "source": "https://github.com/lesps/bedtime-stories/tree/main/tools/simplified",
        "license": "Public domain in the USA",
        "language": "en",
        "originalLanguage": "en",
    },
    "myths-russian": {
        "id": "myths-russian",
        "title": "Russian Tales and Legends, Simply Told",
        "author": "Traditional (Russian)",
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
    note = (f"Retold by {ADAPTED_BY}, from {meta['basedOn']}. There is no public-domain text "
            "of this legend in the app to compare it with.")
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
        flags = flags_of(meta, orig)
        # Other versions lists only visible stories: name the setting that shows a hidden original.
        hidden_by = [label for flag, label in SETTING_FOR_FLAG.items()
                     if flag in orig["flags"] and flag not in flags]
        if hidden_by:
            note = (f"A simplified retelling of {credit}. The original is listed under Other versions "
                    "only when " + " and ".join(f"“{label}” is on" for label in hidden_by)
                    + " in Settings.")
        else:
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
            "flags": flags,
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
