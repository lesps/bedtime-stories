#!/usr/bin/env python3
"""Stories from the Qur'an in Marmaduke Pickthall's translation, The Meaning of the Glorious Koran
(1930), from Project Gutenberg's three-translation text.

    git clone --depth 1 https://github.com/GITenberg/Three-Translations-of-The-Koran--Al-Qur-an--side-by-side_16955.git src/Three-Translations-of-The-Koran--Al-Qur-an--side-by-side_16955
    python3 tools/extract_islamic.py src

The text gives each verse as "SSS.VVV" followed by three paragraphs, one per translator; the
"P:" paragraph is Pickthall's. A story's blocks are a note giving its reference, then one paragraph
per verse (a verse that ends mid-sentence runs on into the next), with a heading for each passage
when there is more than one. Pickthall's bracketed words are kept. FIXES restores three slips of
the digitization. Writes `pickthall-koran`, every story marked `livingTradition`; these stories never
carry pictures (the integrity test checks).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

PICKTHALL = {"id": "pickthall-koran", "title": "The Meaning of the Glorious Koran", "author": "The Qur'an",
             "contributor": "Translated by Marmaduke Pickthall", "firstPublished": 1930,
             "source": "https://www.gutenberg.org/ebooks/16955", "license": "Public domain in the USA",
             "language": "en", "originalLanguage": "ar"}
FILE = "Three-Translations-of-The-Koran--Al-Qur-an--side-by-side_16955/16955.txt"
LIVING = "Muslims"
INTRO = ("In the Qur'an, Allah speaks to the Prophet Muhammad, often as \"We\". The words in brackets "
         "are Pickthall's, to make the meaning clear.")

SURAHS = {11: "Hud", 18: "The Cave", 21: "The Prophets", 27: "The Ant", 37: "Those Who Set The Ranks"}

FIXES = {
    (18, 19): ("a day or some part of a day, (Others) said", "a day or some part of a day. (Others) said"),
    (11, 45): ("Thou are the Most Just", "Thou art the Most Just"),
    (37, 148): ("gave them comfort for a while", "gave them comfort for a while."),
}

# (title, workId, [(surah, first verse, last verse, note before this passage or None)])
STORIES = [
    ("The People of the Cave", "seven-sleepers", [(18, 9, 26, None)]),
    ("Solomon, the Ants and the Hoopoe", "islamic-sulayman", [(27, 15, 44, None)]),
    ("Noah and the Ship", "hebrew-noah", [(11, 25, 49, None)]),
    ("Jonah and the Fish", "hebrew-jonah",
     [(37, 139, 148, None),
      (21, 87, 88, "Dhu'n-Nun, \"the one of the fish\", is Jonah.")]),
]


def parse(text):
    verses = {}
    for m in re.finditer(r"^(\d{3})\.(\d{3})\n(.*?)(?=^\d{3}\.\d{3}\n|\Z)", text, re.S | re.M):
        p = re.search(r"^P: (.*?)(?=\n\s*\n|\Z)", m[3], re.S | re.M)
        if p:
            verses[(int(m[1]), int(m[2]))] = re.sub(r"\s+", " ", p[1]).strip()
    return verses


def verse(verses, s, v):
    text = verses[(s, v)]
    if (s, v) in FIXES:
        a, b = FIXES[(s, v)]
        assert a in text, (s, v)
        text = text.replace(a, b)
    return text


def blocks_of(verses, passages):
    refs = "; ".join(f"{SURAHS[s]} (Surah {s}), verses {a}–{b}" for s, a, b, _ in passages)
    blocks = [{"type": "note", "text": f"{refs}, in Marmaduke Pickthall's translation (1930). {INTRO}"}]
    for s, first, last, note in passages:
        if len(passages) > 1:
            blocks.append({"type": "heading", "text": f"{SURAHS[s]} (Surah {s})"})
        if note:
            blocks.append({"type": "note", "text": note})
        for v in range(first, last + 1):
            text = verse(verses, s, v)
            prev = blocks[-1]
            if prev["type"] == "p" and prev["text"][-1] not in ".?!":
                prev["text"] += " " + text  # the sentence runs on into this verse
            else:
                blocks.append({"type": "p", "text": text})
    return blocks


def main(src):
    verses = parse((Path(src) / FILE).read_text(encoding="ascii").replace("\r\n", "\n"))
    stories = []
    for i, (title, work_id, passages) in enumerate(STORIES, 1):
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "")).strip("-")
        stories.append(finish({"id": f"pickthall-koran--{slug}", "collectionId": PICKTHALL["id"], "order": i,
                               "title": title, "origin": None, "excluded": False, "flags": [], "moral": None,
                               "blocks": blocks_of(verses, passages), "workId": work_id,
                               "livingTradition": LIVING}))
    index = load_index()
    upsert_collection(index, PICKTHALL, stories)
    for st in stories:
        lv = st["readingLevel"]
        print(f"{st['id']:52} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
