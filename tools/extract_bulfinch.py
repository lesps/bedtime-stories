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
from build_compendium import title_case  # noqa: E402
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
# (heading in the text, story title, workId, flags[, last heading]), in book order. With a last
# heading, the story runs through that section too, and the inner headings become heading blocks.
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
    # Heroes
    ("THE GRAEAE AND THE GORGONS", "Perseus", "greek-perseus", [], "THE WEDDING FEAST"),
    ("THE SPHINX", "The Sphinx", "greek-oedipus-sphinx", M),
    ("PEGASUS AND THE CHIMAERA", "Pegasus and the Chimaera", "greek-bellerophon", []),
    ("MELEAGER AND ATALANTA", "Meleager", "greek-meleager", M),
    ("ATALANTA", "Atalanta", "greek-atalanta", []),
    ("HERCULES", "Hercules", "greek-heracles-labours", M),  # madness, Nessus, death on the pyre
    ("CASTOR AND POLLUX", "Castor and Pollux", "greek-castor-pollux", []),
    # Troy and the Odyssey
    ("THE TROJAN WAR", "The Trojan War", "greek-trojan-war", M),
    ("THE FALL OF TROY", "The Fall of Troy", "greek-wooden-horse", M),
    ("RETURN OF ULYSSES", "The Return of Ulysses", "greek-odysseus-cyclops", []),
    ("THE LAESTRYGONIANS", "The Laestrygonians and Circe", "greek-odysseus-circe", []),
    ("SCYLLA AND CHARYBDIS", "Scylla and Charybdis", "greek-odysseus-sirens", []),
    ("THE PHAEACIANS", "The Phaeacians", "greek-odysseus-nausicaa", []),
    ("FATE OF THE SUITORS", "Fate of the Suitors", "greek-odysseus-homecoming", M),
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


def find(lines, heading):
    hits = [i for i, l in enumerate(lines) if l.strip() == heading]
    if len(hits) != 1:
        raise SystemExit(f"heading {heading!r} found {len(hits)} times")
    return hits[0]


def section(lines, heading, last=None):
    """Lines of one section; with `last`, through that later section, keeping inner headings."""
    i = find(lines, heading) + 1
    while i < len(lines) and (not lines[i].strip() or is_heading(lines[i])):
        i += 1
    stop = find(lines, last) if last else None
    body = []
    while i < len(lines):
        if is_heading(lines[i]):
            if stop is None or i > stop or lines[i].strip().startswith("CHAPTER"):
                break
            body.append("\x00" + lines[i].strip())
        else:
            body.append(lines[i])
        i += 1
    return body


def blocks_of(body):
    paras, cur = [], []
    for line in body + [""]:
        if line.startswith("\x00"):
            if cur:
                paras.append(cur)
                cur = []
            paras.append([line])
        elif line.strip():
            cur.append(line.rstrip())
        elif cur:
            paras.append(cur)
            cur = []
    blocks, in_note = [], False
    for p in paras:
        if p[0].startswith("\x00"):
            blocks.append({"type": "heading", "text": title_case(p[0][1:])})
            continue
        if all(l.startswith("  ") for l in p):
            indent = min(len(l) - len(l.lstrip()) for l in p)
            verse = "\n".join(l[indent:] for l in p)
            if in_note and verse.endswith("]"):  # a footnote can close on its quoted poem
                in_note, verse = False, verse[:-1]
            blocks.append({"type": "verse", "text": verse})
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
    for order, (heading, title, work_id, flags, *last) in enumerate(SECTIONS, 1):
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
            "blocks": blocks_of(section(lines, heading, *last)),
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
