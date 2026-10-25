#!/usr/bin/env python3
"""Myths from Bulfinch's The Age of Fable (1855), from the Gutenberg mirror (plain text).

    git clone --depth 1 https://github.com/GITenberg/Bulfinch-s-Mythology_4928.git src/Bulfinch-s-Mythology_4928
    python3 tools/extract_bulfinch.py src

Bulfinch groups several myths per chapter under all-caps headings. Each entry in SECTIONS names
the heading a story starts at; it runs to the next heading or chapter. Indented lines are verse
(Bulfinch quotes Milton, Byron and others). Only The Age of Fable is read, not the Age of
Chivalry or the Charlemagne legends that share the ebook. Writes the `bulfinch-fable` collection.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

COLLECTION = {
    "id": "bulfinch-fable",
    "title": "The Age of Fable",
    "author": "Thomas Bulfinch",
    "contributor": None,
    "firstPublished": 1855,
    "source": "https://www.gutenberg.org/ebooks/4928",
    "license": "Public domain in the USA",
    "language": "en",
    "originalLanguage": "en",
}

M = ["mature-themes"]
# (heading in the text, story title, workId, flags), in book order.
SECTIONS = [
    ("PROMETHEUS AND PANDORA", "Prometheus and Pandora", "greek-prometheus-pandora", []),
    ("APOLLO AND DAPHNE", "Apollo and Daphne", "greek-apollo-daphne", []),
    ("PYRAMUS AND THISBE", "Pyramus and Thisbe", "greek-pyramus-thisbe", M),
    ("AND THE RUSTICS", "Io", "greek-io", []),
    ("CALLISTO", "Callisto", "greek-callisto", []),
    ("DIANA AND ACTAEON", "Diana and Actaeon", "greek-actaeon", M),
    ("LATONA AND THE RUSTICS", "Latona and the Rustics", "greek-latona-frogs", []),
    ("PHAETON", "Phaeton", "greek-phaethon", []),
    ("MIDAS--BAUCIS AND PHILEMON", "Midas", "greek-midas", []),
    ("BAUCIS AND PHILEMON", "Baucis and Philemon", "greek-baucis-philemon", []),
    ("PYGMALION--DRYOPE-VENUS AND ADONIS--APOLLO AND HYACINTHUS", "Pygmalion", "greek-pygmalion", []),
    ("CEYX AND HALCYONE: OR, THE HALCYON BIRDS", "Ceyx and Halcyone", "greek-ceyx-alcyone", []),
    ("ECHO AND NARCISSUS", "Echo and Narcissus", "greek-echo-narcissus", []),
    ("CLYTIE", "Clytie", "greek-clytie", []),
    ("HERO AND LEANDER", "Hero and Leander", "greek-hero-leander", M),
    ("MINERVA", "Minerva and Arachne", "greek-arachne", M),  # Arachne hangs herself
    ("NIOBE", "Niobe", "greek-niobe", M),
    ("DAEDALUS", "Daedalus", "greek-daedalus", []),
    ("ORPHEUS AND EURYDICE", "Orpheus and Eurydice", "greek-orpheus", M),
    ("ARION", "Arion", "greek-arion", []),
    ("AURORA AND TITHONUS", "Aurora and Tithonus", "greek-tithonus", []),
]

HEADING = re.compile(r"^[A-Z][A-Z ,;:.'-]{3,}$")


def fable_lines(path):
    lines = path.read_text(encoding="utf-8", errors="replace").replace("\r", "").split("\n")
    start = next(i for i, l in enumerate(lines) if l.strip() == "CHAPTER I")
    # The Age of Chivalry restarts the numbering at CHAPTER I.
    end = next(i for i, l in enumerate(lines) if i > start and l.strip() == "CHAPTER I")
    return lines[start:end]


def is_heading(line):
    s = line.strip()
    return s.startswith("CHAPTER") or (line == s and bool(HEADING.match(s)))


def section(lines, heading):
    hits = [i for i, l in enumerate(lines) if l.strip() == heading]
    if len(hits) != 1:
        raise SystemExit(f"heading {heading!r} found {len(hits)} times")
    i = hits[0] + 1
    while i < len(lines) and (not lines[i].strip() or is_heading(lines[i])):
        i += 1
    body = []
    while i < len(lines) and not is_heading(lines[i]):
        body.append(lines[i])
        i += 1
    return body


def blocks_of(body):
    paras, cur = [], []
    for line in body + [""]:
        if line.strip():
            cur.append(line.rstrip())
        elif cur:
            paras.append(cur)
            cur = []
    blocks, in_note = [], False
    for p in paras:
        if all(l.startswith("  ") for l in p):
            indent = min(len(l) - len(l.lstrip()) for l in p)
            blocks.append({"type": "verse", "text": "\n".join(l[indent:] for l in p)})
            continue
        text = re.sub(r"\s+", " ", " ".join(l.strip() for l in p)).strip()
        # A footnote runs from "[Footnote:" to the paragraph ending in "]", sometimes several.
        if text.startswith("[Footnote"):
            in_note = True
            text = re.sub(r"^\[Footnote:?\s*", "Note: ", text)
        if in_note:
            if text.endswith("]"):
                in_note, text = False, text[:-1]
            blocks.append({"type": "note", "text": text})
        else:
            blocks.append({"type": "p", "text": text})
    return blocks


def main(src):
    lines = fable_lines(Path(src) / "Bulfinch-s-Mythology_4928" / "4928.txt")
    stories = []
    for order, (heading, title, work_id, flags) in enumerate(SECTIONS, 1):
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        story = {
            "id": f"{COLLECTION['id']}--{slug}",
            "collectionId": COLLECTION["id"],
            "order": order,
            "title": title,
            "origin": None,
            "excluded": False,
            "flags": list(flags),
            "moral": None,
            "blocks": blocks_of(section(lines, heading)),
            "workId": work_id,
        }
        stories.append(finish(story))
    index = load_index()
    upsert_collection(index, COLLECTION, stories)
    save_index(index)
    for st in stories:
        b = st["blocks"]
        print(f"{st['id']:42} {st['wordCount']:5}w {st['readingMinutes']:3}m "
              f"{st['readingLevel']['fkGrade']:5} {st['readingLevel']['band']:8} "
              f"verse={sum(x['type'] == 'verse' for x in b)}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
