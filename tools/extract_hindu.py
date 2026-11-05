#!/usr/bin/env python3
"""Hindu stories, part 1: myths of Vishnu, Shiva and the Ganga from Kisari Mohan Ganguli's
Mahabharata (1883–96), Manmatha Nath Dutt's Vishnu Purana (1896, after H. H. Wilson) and Dutt's
Ramayana (1891).

    git clone --depth 1 https://github.com/GITenberg/The-Mahabharata-of-Krishna-Dwaipayana-Vyasa-Volume-1Books-1-2-and-3_15474.git src/The-Mahabharata-of-Krishna-Dwaipayana-Vyasa-Volume-1Books-1-2-and-3_15474
    git clone --depth 1 https://github.com/GITenberg/A-Prose-English-Translation-of-Vishnupuranam-Based-on-Professor-H-H-Wilsons-translation_66208.git src/A-Prose-English-Translation-of-Vishnupuranam-Based-on-Professor-H-H-Wilsons-translation_66208
    git clone --depth 1 https://github.com/GITenberg/The-Ramayana-Volume-One-Balakandam-and-Ayodhyakandam_57265.git src/The-Ramayana-Volume-One-Balakandam-and-Ayodhyakandam_57265
    python3 tools/extract_hindu.py src

A story is one or more runs of text, each from a phrase to a phrase (both kept), split into
paragraphs on blank lines; a note can come before each run. Section headings, the Mahabharata's
"So ends the … section" lines and "(… continued)" lines, footnote markers and the Ramayana's
footnotes are dropped. Writes `ganguli-mahabharata`, `dutt-vishnu-purana` and `dutt-ramayana`,
every story marked `livingTradition`.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

COMMON = {"license": "Public domain in the USA", "language": "en", "originalLanguage": "sa"}
GANGULI = {**COMMON, "id": "ganguli-mahabharata", "title": "The Mahabharata of Krishna-Dwaipayana Vyasa",
           "author": "The Mahabharata", "contributor": "Translated by Kisari Mohan Ganguli", "firstPublished": 1883,
           "source": "https://www.gutenberg.org/ebooks/15474"}
VISHNU = {**COMMON, "id": "dutt-vishnu-purana", "title": "A Prose English Translation of Vishnupuranam",
          "author": "The Vishnu Purana", "contributor": "Translated by Manmatha Nath Dutt, after H. H. Wilson",
          "firstPublished": 1896, "source": "https://www.gutenberg.org/ebooks/66208"}
RAMAYANA = {**COMMON, "id": "dutt-ramayana", "title": "The Ramayana", "author": "Valmiki",
            "contributor": "Translated by Manmatha Nath Dutt", "firstPublished": 1891,
            "source": "https://www.gutenberg.org/ebooks/57265"}
FILES = {
    "ganguli-mahabharata": "The-Mahabharata-of-Krishna-Dwaipayana-Vyasa-Volume-1Books-1-2-and-3_15474/15474-0.txt",
    "dutt-vishnu-purana": "A-Prose-English-Translation-of-Vishnupuranam-Based-on-Professor-H-H-Wilsons-translation_66208/66208-0.txt",
    "dutt-ramayana": "The-Ramayana-Volume-One-Balakandam-and-Ayodhyakandam_57265/57265-0.txt",
}
LIVING = "Hindus"

MARKANDEYA = "Markandeya, a sage who has lived through many ages, tells this story to the Pandava prince Yudhishthira."
PARASARA = "The sage Parasara tells this story to his pupil Maitreya."

# (collection, title, workId, flags, [(first words, last words, note before the run or None)])
STORIES = [
    (GANGULI, "The Lotus from Vishnu's Navel", "hindu-lotus", [],
     [("When the world became one broad expanse of water", "with his keenedged discus!’”", MARKANDEYA)]),
    (GANGULI, "Manu and the Fish", "hindu-matsya", ["mature-themes"],  # "reeled about like a drunken harlot"
     [("there was a powerful and great Rishi of the name of Manu", "goeth to heaven.”", MARKANDEYA)]),
    (GANGULI, "The Churning of the Ocean", "hindu-churning", [],
     [("There is a mountain named Meru, of blazing appearance", "(during solar and lunar eclipses).",
       "The bard Sauti tells this story to the sage Saunaka.")]),
    (RAMAYANA, "The Dwarf's Three Steps", "hindu-vamana", [],
     [("Here, O mighty-armed Rāma, Vishnu of mighty asceticism", "and made them subject to his control.",
       "The sage Vishvamitra tells the young princes Rama and Lakshmana about the hermitage they have "
       "come to.")]),
    (VISHNU, "The Legend of Prahlada", "hindu-prahlada", ["mature-themes"],
     [("Parāçara said:—Maitreya, hear the interesting story", "constantly listens to his history.", PARASARA)]),
    (VISHNU, "Dhruva, the Pole Star", "hindu-dhruva", [],
     [("Parāçara said:—I mentioned unto you that the Menu Swāyambhava", "possessed of every blessing\".",
       PARASARA)]),
    (RAMAYANA, "The Descent of the Ganga", "hindu-ganga", [],
     [("When Sagara had bowed unto the influence of Time", "his life and fame increase.’",
       "The sage Vishvamitra tells this story to Rama. The sixty thousand sons of King Sagara had been burned "
       "to ashes by the sage Kapila, and only the waters of the Ganga, which then flowed in heaven, could "
       "bring their souls to rest.")]),
    (GANGULI, "Markandeya and the Child on the Banyan Tree", "hindu-markandeya", [],
     [("And then when the universe become one dead expanse of water", "spoke unto me these words.”",
       "Markandeya tells the Pandava prince Yudhishthira what he saw at the end of an age, when the whole "
       "world had been destroyed."),
      ("‘Markandeya continued, ‘Having said so unto me", "at the end of the Yuga!",
       "The child tells Markandeya that he is Narayana, who makes and unmakes all things, and who sleeps in "
       "the form of a child until Brahma wakes to create the world again.")]),
]


def find(text, phrase, pos=0):
    m = re.compile(r"\s+".join(map(re.escape, phrase.split()))).search(text, pos)
    if not m:
        raise SystemExit(f"not found: {phrase!r}")
    return m.span()


def paragraphs(raw):
    out = []
    for para in re.split(r"\n\s*\n", raw):
        t = re.sub(r"\s+", " ", para).strip()
        if (not t or re.match(r"SECTION [IVXLC]+\.?$", t) or t.startswith("So ends the")
                or re.fullmatch(r"\(.*continued\)", t) or re.match(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]", t)):
            continue
        t = re.sub(r"\[\d+\]|[⁰¹²³⁴⁵⁶⁷⁸⁹]+", "", t)
        out.append(re.sub(r"\s+([,.;:!?])", r"\1", t))
    return out


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "")).strip("-")


def main(src):
    texts = {cid: (Path(src) / f).read_text(encoding="utf-8-sig") for cid, f in FILES.items()}
    by_collection = {}
    for col, title, work_id, flags, runs in STORIES:
        text, blocks = texts[col["id"]], []
        for first, last, note in runs:
            start = find(text, first)[0]
            if note:
                blocks.append({"type": "note", "text": note})
            blocks += [{"type": "p", "text": p} for p in paragraphs(text[start:find(text, last, start)[1]])]
        stories = by_collection.setdefault(col["id"], (col, []))[1]
        stories.append(finish({"id": f"{col['id']}--{slug(title)}", "collectionId": col["id"],
                               "order": len(stories) + 1, "title": title, "origin": None, "excluded": False,
                               "flags": flags, "moral": None, "blocks": blocks, "workId": work_id,
                               "livingTradition": LIVING}))
    index = load_index()
    for col, stories in by_collection.values():
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:58} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
