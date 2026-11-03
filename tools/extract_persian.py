#!/usr/bin/env python3
"""Persian stories: nine from Helen Zimmern's The Epic of Kings (1882), her prose retelling of
Ferdowsi's Shahnameh, and Yima's enlarging of the earth from the Avesta, in James Darmesteter's
translation (1880) as Epiphanius Wilson prints it in Sacred Books of the East (1900).

    git clone --depth 1 --filter=blob:none --no-checkout https://github.com/TheMITTech/classics.git src/classics
    git -C src/classics checkout HEAD -- Ferdowsi
    git clone --depth 1 https://github.com/GITenberg/Sacred-Books-of-the-East_12894.git src/Sacred-Books-of-the-East_12894
    python3 tools/extract_persian.py src

Zimmern's text is the Internet Classics Archive's plain-text copy, split into its eighteen
sections on the rules between them. That copy has lost most blank lines between paragraphs, so a
paragraph is taken to end where a line stops short of the 75-column wrap after closing
punctuation (the next word would have fitted), and Rustem's song is set out again as verse. A story is one or more runs of paragraphs, each
from a paragraph starting with given words to one ending with given words; a note can come before
each run. FIXES restores the copy's few slips. Writes `zimmern-kings` and `darmesteter-avesta`
(the Yima story marked `livingTradition`).
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

COMMON = {"license": "Public domain in the USA", "language": "en"}
ZIMMERN = {**COMMON, "id": "zimmern-kings", "title": "The Epic of Kings: Stories Retold from Firdusi",
           "author": "Helen Zimmern", "contributor": None, "firstPublished": 1882,
           "source": "http://classics.mit.edu/Ferdowsi/kings.html", "originalLanguage": "fa"}
AVESTA = {**COMMON, "id": "darmesteter-avesta", "title": "The Zend-Avesta", "author": "The Avesta",
          "contributor": "Translated by James Darmesteter", "firstPublished": 1880,
          "source": "https://www.gutenberg.org/ebooks/12894", "originalLanguage": "ae"}
ZIMMERN_TXT = "classics/Ferdowsi/kings.mb.txt"
AVESTA_TXT = "Sacred-Books-of-the-East_12894/12894-8.txt"

FIXES = [
    ("and P the sword slept", "and the sword slept"),
    ("Queen of Iran. for since", "Queen of Iran. For since"),
    ("and-bade Rustem", "and bade Rustem"),
    ("deliver the Shah? When he had thus spoken", "deliver the Shah?\" When he had thus spoken"),
    ("may the tree of gladness sprout again for Iran!", "may the tree of gladness sprout again for Iran!\""),
    ("that glisten with gold in the sunlight?", "that glisten with gold in the sunlight?\""),
    ("save thy life? \"", "save thy life?\""),
    ("how do these things regard thee? \"", "how do these things regard thee?\""),
    ("art thou the master of Rakush?' \"", "art thou the master of Rakush?'\""),
    ("in his narrow prison.\"'", "in his narrow prison.'\""),
]
# Paragraphs that the wrap rule splits in the middle of a speech: (start of the second half).
JOIN = ["Prepare food for them, therefore", "To thee I owe all that I am"]
# Rustem's song, whose lines the archive's copy runs together: a line starts at each capital,
# except at the names inside a line.
SONG = ('"Rustem is the scourge', '"There the sword of Rustem', '"Cups of wine and wreaths')
SONG_NAMES = ("Rustem", "Deevs")

# (title, workId, flags, [(section, first words, last words, note before the run or None)])
STORIES = [
    ("The First Shahs", "persian-first-shahs", [],
     [("THE SHAHS OF OLD", "Kaiumers first sat upon the throne", "and Ahriman had power over the land.", None)]),
    ("Zohak the Serpent King", "persian-zohak", ["mature-themes"],
     [("THE SHAHS OF OLD", "Now there dwelt in the deserts of Arabia", "his heart was filled with anguish.",
       "Jemshid has grown proud and named himself God, and God has turned away from him.")]),
    ("Kawah the Blacksmith", "persian-kawah", ["mature-themes"],
     [("THE SHAHS OF OLD", "In this year Zohak caused his army", "and Feridoun reigned in his stead.",
       "Zohak, the Serpent King, has ruled Iran for a thousand years, and every day two men are killed to "
       "feed the serpents on his shoulders. His wise men have foretold that Feridoun, of the family of "
       "Jemshid, will overthrow him, and Feridoun's mother has hidden the boy away.")]),
    ("Zal and the Simurgh", "persian-zal", [],
     [("ZAL", "Seistan, which is to the south of Iran", "and that Zal was a hero among men.", None)]),
    ("Rustem and Rakush", "persian-rakush", [],
     [("RUSTEM", "Now ere the son of Zal was born", "because a hero was arisen in Iran.", None),
      ("RUSTEM", "Then he called before him his son", "they made them ready to stand against Afrasiyab.",
       "Years of war follow. When Afrasiyab of Turan invades Iran once more, the people turn to Zal, "
       "who is now old, and he calls on his son.")]),
    ("The Seven Labours of Rustem", "persian-seven-labours", [],
     [("THE MARCH INTO MAZINDERAN", "When Zal heard this message", "Kai Kaous bade them desist from further bloodshed.",
       "Kai Kaous, the Shah, has marched into Mazinderan, the land of the Deevs, though Zal warned him "
       "not to. The White Deev has struck him and his army blind and holds them captive, and Kai Kaous "
       "has sent to Zal for help.")]),
    ("Rustem and Sohrab", "persian-sohrab", ["mature-themes"],
     [("RUSTEM AND SOHRAB", "Give ear unto the combat of Sohrab", "went forth after Sohrab her son.", None)]),
    ("Saiawush and the Fire", "persian-saiawush", ["mature-themes"],
     [("SAIAWUSH", "On a certain day it came about that Tus", "the Shah was glad again in her sight.", None)]),
    ("Byzun and Manijeh", "persian-byzun", [],
     [("BYZUN AND MANIJEH", "Peace reigned again within the borders", "Thus endeth the history of Byzun and Manijeh.",
       None)]),
]

YIMA_NOTE = ("From the second chapter of the Vendidad, a book of the Avesta, in James Darmesteter's "
             "translation (1880). Epiphanius Wilson's Sacred Books of the East (1900) ends it here; the "
             "chapter goes on to tell how Yima built a shelter against a terrible winter. Yima is the king "
             "the Shahnameh calls Jemshid.")


def zimmern_sections(text):
    text = html.unescape(re.sub(r"<[^>]+>", "", text[text.index("THE SHAHS OF OLD"):]))
    sections = {}
    for part in re.split(r"\n-{20,}\n", text):
        head, _, body = part.strip("\n").partition("\n")
        lines = [line.rstrip() for line in body.split("\n")]
        paras, cur = [], []
        for i, line in enumerate(lines):
            if not line.strip():
                if cur:
                    paras.append(cur)
                    cur = []
                continue
            cur.append(line.strip())
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if nxt and len(line) + 1 + len(nxt.split(" ")[0]) <= 74 and re.search(r"[.?!\"'\-:)]$", line):
                paras.append(cur)
                cur = []
        if cur:
            paras.append(cur)
        out = []
        for p in paras:
            t = " ".join(p)
            for a, b in FIXES:
                t = t.replace(a, b)
            t = re.sub(r"-$", ":", t)  # "he said-" before a speech
            t = re.sub(r"(\w)- \"", r'\1: "', t)
            if out and any(t.startswith(j) for j in JOIN):
                out[-1] += " " + t
            else:
                out.append(t)
        sections[head.strip()] = out
    return sections


def block(text):
    if not text.startswith(SONG):
        return {"type": "p", "text": text}
    words, lines = text.split(" "), []
    for i, w in enumerate(words):
        if i and w[0].isupper() and not w.startswith(SONG_NAMES):
            lines.append([])
        lines[-1:] = [(lines[-1] if lines else []) + [w]]
    return {"type": "verse", "text": "\n".join(" ".join(line) for line in lines)}


def run(paras, first, last):
    start = next(i for i, p in enumerate(paras) if p.startswith(first))
    end = next(i for i in range(start, len(paras)) if paras[i].endswith(last))
    return paras[start:end + 1]


def yima_blocks(text):
    start = text.index("Zarathustra asked Ahura Mazda:--")
    end = text.index("as many as he wished.\"", start) + len("as many as he wished.\"")
    blocks = [{"type": "note", "text": YIMA_NOTE}]
    for para in re.split(r"\n\s*\n", text[start:end]):
        blocks.append({"type": "p", "text": re.sub(r"\s+", " ", para).strip()})
    return blocks


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "")).strip("-")


def main(src):
    sections = zimmern_sections((Path(src) / ZIMMERN_TXT).read_text(encoding="latin-1"))
    kings = []
    for i, (title, work_id, flags, runs) in enumerate(STORIES, 1):
        blocks = []
        for section, first, last, note in runs:
            if note:
                blocks.append({"type": "note", "text": note})
            blocks += [block(p) for p in run(sections[section], first, last)]
        kings.append(finish({"id": f"zimmern-kings--{slug(title)}", "collectionId": ZIMMERN["id"], "order": i,
                             "title": title, "origin": None, "excluded": False, "flags": flags, "moral": None,
                             "blocks": blocks, "workId": work_id}))
    avesta_text = (Path(src) / AVESTA_TXT).read_text(encoding="latin-1")
    yima = [finish({"id": "darmesteter-avesta--yima-the-good-shepherd", "collectionId": AVESTA["id"], "order": 1,
                    "title": "Yima, the Good Shepherd", "origin": None, "excluded": False, "flags": [],
                    "moral": None, "blocks": yima_blocks(avesta_text), "workId": "persian-yima",
                    "livingTradition": "Zoroastrians"})]
    index = load_index()
    for col, stories in ((ZIMMERN, kings), (AVESTA, yima)):
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:52} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
