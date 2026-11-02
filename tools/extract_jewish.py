#!/usr/bin/env python3
"""Jewish legends: Abraham and the idols from Ginzberg's The Legends of the Jews, volume 1 (Henrietta
Szold's translation, 1909); King Solomon and the worm Shamir from Gerald Friedlander's Jewish Fairy
Stories (1917); and Honi's long sleep and the Golem of Prague from Gertrude Landa's Jewish Fairy Tales and
Legends (1919).

    git clone --depth 1 https://github.com/GITenberg/The-Legends-of-the-Jews-Volume-1_1493.git src/The-Legends-of-the-Jews-Volume-1_1493
    git clone --depth 1 https://github.com/GITenberg/Jewish-fairy-stories_72880.git src/Jewish-fairy-stories_72880
    git clone --depth 1 https://github.com/GITenberg/Jewish-Fairy-Tales-and-Legends_26711.git src/Jewish-Fairy-Tales-and-Legends_26711
    python3 tools/extract_jewish.py src

Each story is the passage from an opening phrase to a closing phrase (both kept), split into
paragraphs on blank lines. Illustration captions and footnote markers are dropped, and so is
Friedlander's closing reference line, which becomes the opening note instead. The books' pictures
(Beatrice Hirschfeld's for Friedlander, uncredited in Landa) are left out. Writes
`ginzberg-legends`, `friedlander-jewish` and `landa-jewish`.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

COMMON = {"license": "Public domain in the USA", "language": "en"}
GINZBERG = {**COMMON, "id": "ginzberg-legends", "title": "The Legends of the Jews, Volume 1",
            "author": "Louis Ginzberg", "contributor": "Translated by Henrietta Szold", "firstPublished": 1909,
            "source": "https://www.gutenberg.org/ebooks/1493", "originalLanguage": "de"}
FRIEDLANDER = {**COMMON, "id": "friedlander-jewish", "title": "Jewish Fairy Stories", "author": "Gerald Friedlander",
               "contributor": None, "firstPublished": 1917,
               "source": "https://www.gutenberg.org/ebooks/72880", "originalLanguage": "he"}
LANDA = {**COMMON, "id": "landa-jewish", "title": "Jewish Fairy Tales and Legends", "author": "Gertrude Landa",
         "contributor": None, "firstPublished": 1919,
         "source": "https://www.gutenberg.org/ebooks/26711", "originalLanguage": "en"}

GINZBERG_TXT = ("The-Legends-of-the-Jews-Volume-1_1493/1493.txt", "latin-1")
FRIEDLANDER_TXT = ("Jewish-fairy-stories_72880/72880-0.txt", "utf-8-sig")
LANDA_TXT = ("Jewish-Fairy-Tales-and-Legends_26711/26711.txt", "latin-1")

# (collection, (file, encoding), title, workId, first words, last words, opening note)
STORIES = [
    (GINZBERG, GINZBERG_TXT, "Abraham and the Idols", "jewish-abraham-idols",
     "But Terah could not be convinced", "broke it therewith, and ran away.",
     "Terah, Abraham's father, made idols and worshipped them."),
    (FRIEDLANDER, FRIEDLANDER_TXT, "King Solomon and the Worm", "jewish-solomon-shamir",
     "King Solomon, the wisest of men, resolved", "no one knows where it is to be found.",
     "From the Babylonian Talmud, tractate Gittin 68a–b, retold by Friedlander."),
    (LANDA, LANDA_TXT, "The Sleep of One Hundred Years", "jewish-honi-sleep",
     "It was at the time of the destruction of the First Temple", "not in this world will he awaken.",
     "Rabbi Onias is Honi, the sage of the Talmud also remembered as Honi the Circle-Maker. In the "
     "Talmud he sleeps for seventy years."),
    (LANDA, LANDA_TXT, "The Rabbi's Bogey-Man", "jewish-golem",
     "Rabbi Lion, of the ancient city of Prague", "the story was told of the rabbi's bogey-man.",
     "Landa's telling of the Golem of Prague. Rabbi Lion is Rabbi Judah Loew, who lived in Prague "
     "in the 1500s."),
]


def find(text, phrase, pos=0):
    """Finds a phrase whatever the line breaks inside it; returns (start, end)."""
    m = re.compile(r"\s+".join(map(re.escape, phrase.split()))).search(text, pos)
    if not m:
        raise SystemExit(f"not found: {phrase!r}")
    return m.span()


def blocks_of(raw):
    blocks = []
    for para in re.split(r"\n\s*\n", raw.replace("\r\n", "\n")):
        t = re.sub(r"\s+", " ", para).strip()
        if not t or t.startswith("[Illustration"):
            continue
        t = re.sub(r"\[\d+\]", "", t)
        blocks.append({"type": "p", "text": re.sub(r"\s+([,.;:!?])", r"\1", t)})
    return blocks


def main(src):
    index = load_index()
    by_collection = {}
    for col, (file, enc), title, work_id, first, last, note in STORIES:
        text = (Path(src) / file).read_bytes().decode(enc)
        start = find(text, first)[0]
        blocks = blocks_of(text[start:find(text, last, start)[1]])
        if note:
            blocks.insert(0, {"type": "note", "text": note})
        stories = by_collection.setdefault(col["id"], (col, []))[1]
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "")).strip("-")
        stories.append(finish({"id": f"{col['id']}--{slug}", "collectionId": col["id"], "order": len(stories) + 1,
                               "title": title, "origin": None, "excluded": False, "flags": [], "moral": None,
                               "blocks": blocks, "workId": work_id}))
    for col, stories in by_collection.values():
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:58} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
