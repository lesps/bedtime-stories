#!/usr/bin/env python3
"""Buddhist stories: seven Jātaka tales from the Cambridge translation edited by E. B. Cowell
(1895–97), the four omens, the Great Renunciation and the enlightenment under the Bo-tree from the
Nidānakathā in T. W. Rhys Davids's Buddhist Birth Stories (1880), and Kisā Gotamī and the mustard
seed from Paul Carus's The Gospel of Buddha (1894).

    git clone --depth 1 --filter=blob:none --no-checkout https://github.com/jonnyg23/mahabrain.git src/mahabrain
    git -C src/mahabrain checkout HEAD -- sacred_obsidian_vault/bud/j1 sacred_obsidian_vault/bud/j2 sacred_obsidian_vault/bud/j3
    git clone --depth 1 https://github.com/GITenberg/Buddhist-birth-stories-or-Jataka-tales-Volume-1_51880.git src/Buddhist-birth-stories-or-Jataka-tales-Volume-1_51880
    git clone --depth 1 https://github.com/GITenberg/The-Gospel-of-Buddha-Compiled-from-Ancient-Records_35895.git src/The-Gospel-of-Buddha-Compiled-from-Ancient-Records_35895
    python3 tools/extract_buddhist.py src

The Jātaka text is the sacred-texts.com edition (one HTML page per tale), as mirrored in that
repository. A Jātaka has three parts: the story in the present (why the Buddha told it), the story
of the past, and the identification ("I myself was the hare"). A story here is the story of the
past and the identification, each a run of paragraphs from one containing given words to one
containing others (the first and last cut at those words), after a note that gives the occasion
in a sentence. A paragraph with line breaks is a stanza (a verse block); bracketed numbers are the
Pali edition's pages. Rhys Davids's and Carus's texts are cut the same way from the Gutenberg
plain text, Rhys Davids's verse numbers and Carus's verse numbers left out. FIXES puts right the
digitizations' slips in the passages used (each must be used). Writes `cowell-jataka`,
`rhys-davids-birth-stories` and `carus-gospel-of-buddha`, every story marked `livingTradition`.
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

LICENSE = {"license": "Public domain in the USA", "language": "en", "originalLanguage": "pi"}
COWELL = {"id": "cowell-jataka", "title": "The Jātaka, or Stories of the Buddha's Former Births",
          "author": "The Jātaka", "contributor": "Translated by various hands, edited by E. B. Cowell",
          "firstPublished": 1895, "source": "https://sacred-texts.com/bud/j1/index.htm", **LICENSE}
RHYS_DAVIDS = {"id": "rhys-davids-birth-stories", "title": "Buddhist Birth Stories", "author": "The Nidānakathā",
               "contributor": "Translated by T. W. Rhys Davids", "firstPublished": 1880,
               "source": "https://www.gutenberg.org/ebooks/51880", **LICENSE}
CARUS = {"id": "carus-gospel-of-buddha", "title": "The Gospel of Buddha", "author": "Paul Carus", "contributor": None,
         "firstPublished": 1894, "source": "https://www.gutenberg.org/ebooks/35895", **LICENSE}
JATAKA = "mahabrain/sacred_obsidian_vault/bud/{}.md"
RHYS_DAVIDS_FILE = "Buddhist-birth-stories-or-Jataka-tales-Volume-1_51880/51880-0.txt"
CARUS_FILE = "The-Gospel-of-Buddha-Compiled-from-Ancient-Records_35895/35895-0.txt"
LIVING = "Buddhists"

# The Cowell volumes: (translator, source, firstPublished).
VOLUMES = {
    "j1": ("Robert Chalmers", "https://sacred-texts.com/bud/j1/index.htm", 1895),
    "j2": ("W. H. D. Rouse", "https://sacred-texts.com/bud/j2/index.htm", 1895),
    "j3": ("H. T. Francis and R. A. Neil", "https://sacred-texts.com/bud/j3/index.htm", 1897),
}
BODHISATTA = "In the Jātaka, the stories of the Buddha's earlier lives, the Bodhisatta is the Buddha-to-be."

# (title, workId, file, number, Pali name, occasion, (story start, end), (identification start, end), flags)
JATAKAS = [
    ("The Banyan Deer", "jataka-012", "j1/j1015", 12, "Nigrodhamiga",
     "The Buddha told this story about a young nun whom his cousin and rival Devadatta had wrongly turned "
     "out of the order, and her son, Prince Kassapa, whom the Buddha saved.",
     ("Once on a time, when Brahmadatta", "according to his deserts."),
     ("He then shewed the connexion", "King Banyan Deer.\""), []),
    ("The Quails and the Net", "jataka-033", "j1/j1036", 33, "Sammodamāna",
     "The Buddha told this story to his own kinsmen, to stop a quarrel among them.",
     ("Once upon a time when Brahmadatta", "his wife's face was wreathed with smiles."),
     ("\"Thus, sire,\" said the Master", "the wise and good quail.\""), []),
    ("The Monkey and the Crocodile", "jataka-208", "j2/j2061", 208, "Suṃsumāra",
     "The Buddha told this story when he heard that his cousin Devadatta had tried to kill him. Ciñcā was "
     "a woman who told lies about the Buddha.",
     ("Once upon a time, while Brahmadatta", "to the place where he lived."),
     ("When the Master had ended this discourse", "I was the Monkey.\""), []),
    ("The Tortoise Who Talked Too Much", "jataka-215", "j2/j2068", 215, "Kacchapa",
     "The Buddha told this story about Kokālika, a monk who was ruined by his own tongue. The two famous "
     "Elders are the Buddha's chief disciples, Sāriputta and Moggallāna, and Ānanda was his cousin and "
     "attendant.",
     ("Once on a time Brahmadatta", "became a man of few words."),
     ("This discourse ended", "his wise adviser.\""), []),
    ("The Hare in the Moon", "jataka-316", "j3/j3017", 316, "Sasa",
     "The Buddha told this story to thank a landowner who had fed him and five hundred monks for a week. "
     "Sakka is the king of the gods. Ānanda was the Buddha's cousin and attendant, and Moggallāna and "
     "Sāriputta his chief disciples.",
     ("Once upon a time when Brahmadatta", "fare according to their deeds."),
     ("The Master, when he had ended his lesson", "I myself was the wise hare.\""), []),
    ("The Hare Who Thought the World Was Ending", "jataka-322", "j3/j3023", 322, "Daddabha",
     "The Buddha told this story when his monks asked whether there was any good in the painful penances "
     "that other holy men put themselves through.",
     ("Once upon a time when Brahmadatta", "inspired by Perfect Wisdom."),
     ("The Master, having ended his lesson", "I myself was the lion.\""), []),
    ("The Monkey King's Bridge", "jataka-407", "j3/j3108", 407, "Mahākapi",
     "The Buddha told this story when his monks were praising the good he did for his relatives. Ānanda "
     "was the Buddha's cousin and attendant.",
     ("Once upon a time when Brahmadatta", "became destined for heaven."),
     ("After the lesson, the Master", "the monkey-king myself.\""), []),
]

# (title, workId, (start, end), note)
NIDANAKATHA = [
    ("The Four Omens and the Great Renunciation", "buddha-renunciation",
     ("Now one day the future Buddha, wanting to go", "reverently, and departed."),
     "From the Nidānakathā, the life of the Buddha that opens the Pāli commentary on the Jātaka. The "
     "Bodisat, the Buddha-to-be, is Prince Siddhattha, the son of King Suddhodana of the Sakyas; his wife "
     "is called “the mother of Rāhula”, after their son."),
    ("The Victory under the Bo-tree", "buddha-enlightenment",
     ("And the Great Being’s six years’ penance became noised abroad", "reached at last!"),
     "From the Nidānakathā, the life of the Buddha that opens the Pāli commentary on the Jātaka. Prince "
     "Siddhattha, the Bodisat or Great Being, has left home, and for six years has fasted and punished his "
     "body, hoping to find wisdom that way, until he fell down in a faint. Māra is the Tempter, the lord "
     "of desire and death."),
]

CARUS_STORY = ("The Mustard Seed", "kisa-gotami", ("There was a rich man who found his gold", "and be blessed.\""),
               "Chapter 84 of The Gospel of Buddha, which Carus put together from the translations of the "
               "Buddhist scriptures in his day. Kisā Gotamī's story comes from the old Pāli commentaries; "
               "Sakyamuni is the Buddha.")

FIXES = [
    # The Banyan Deer
    ("the sheen of his horns was as of, silver", "the sheen of his horns was as of silver"),
    ("with his head on the block, Cried the cook", "with his head on the block. Cried the cook"),
    ("How comes it that you are lying here?\n", "How comes it that you are lying here?\"\n"),
    ("what will the rest of four-footed creatures do?\".", "what will the rest of four-footed creatures do?\""),
    # The Monkey and the Crocodile
    ("live on had fruits", "live on bad fruits"),
    ("give it her to eat\"\n", "give it her to eat.\"\n"),
    ("all knocked to pieces'\"", "all knocked to pieces!\""),
    # The Tortoise
    ("keep his month shut", "keep his mouth shut"),
    ("what made this creature fall?'", "what made this creature fall?\""),
    # The Hare in the Moon
    ("to the wise bare", "to the wise hare"),
    ("it fails to beat even", "it fails to heat even"),
    ("he thy virtue known throughout a whole won", "be thy virtue known throughout a whole æon"),
    ("First Path:—\" At that time", "First Path:—\"At that time"),
    # The Hare Who Thought the World Was Ending
    ("methought, \"If this earth should break up, where shall I go?\"",
     "methought, 'If this earth should break up, where shall I go?'"),
    ("must have fallen on a palm leaf and made a \"thud,\" and", "must have fallen on a palm leaf and made a 'thud,' and"),
    # The Monkey King's Bridge
    ("\"Who will know?\"The foresters, sire.\"", "\"Who will know?\" \"The foresters, sire.\""),
    ("saying, \"We will shoot those vagrant monkeys:\" what", "saying, 'We will shoot those vagrant monkeys:' what"),
]


def clean(text):
    t = html.unescape(re.sub(r"<[^>]+>", "", text))
    t = re.sub(r"\[\d+\]\s*", "", t.replace("[paragraph continues]", ""))
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r" ([.,;:])", r"\1", t)  # a footnote marker's space left before punctuation


def jataka_paragraphs(path):
    """(kind, text) for each paragraph of a sacred-texts.com Jātaka page, a stanza's lines joined by newlines."""
    s = path.read_text(encoding="utf-8").split('<h3 align="CENTER">Footnotes</h3>')[0]
    s = re.sub(r'<a href="#fn_\d+">.*?</a>', "", s)  # footnote markers
    s = re.sub(r'<a name="page_\d+">.*?</a>', "\x01", s)  # page breaks
    out, page_break = [], False
    for chunk in re.split(r"<(?:/?p|/?div|hr)\b[^>]*>", s):
        page_break |= "\x01" in chunk
        lines = [x for x in (clean(line) for line in re.split(r"<br\s*/?>", chunk.replace("\x01", ""))) if x]
        if not lines:
            continue
        if len(lines) > 1:
            out.append(("verse", "\n".join(lines)))
        elif out and out[-1][0] == "p" and ("[paragraph continues]" in chunk
                                             or page_break and re.search(r"[a-zā-ž,]$", out[-1][1])):
            out[-1] = ("p", out[-1][1] + " " + lines[0])  # a paragraph running on over a page break
        else:
            out.append(("p", lines[0]))
        page_break = False
    return out


def text_paragraphs(text):
    """(kind, text) for each paragraph of a Gutenberg plain text: indented paragraphs are verse."""
    out = []
    for para in re.split(r"\n\s*\n", text):
        lines = [x.rstrip() for x in para.split("\n") if x.strip()]
        if not lines:
            continue
        if all(x.startswith("   ") for x in lines):
            lines = [re.sub(r"\[\d+\]", "", re.sub(r"^\d+\.\s+", "", x.strip())) for x in lines]
            out.append(("verse", "\n".join(lines)))
        else:
            t = " ".join(re.sub(r"\s{3,}\d+$", "", x).strip() for x in lines)  # Carus's verse numbers
            t = re.sub(r"\[\d+\]", "", t).replace("_", "")
            out.append(("p", re.sub(r"\s+", " ", t)))
    return out


def run(paras, start, end):
    """Paragraphs from the one containing `start` to the one containing `end`, cut at those words."""
    first = next((i for i, (_, t) in enumerate(paras) if start in t), None)
    if first is None:
        raise SystemExit(f"not found: {start!r}")
    last = next((i for i in range(first, len(paras)) if end in paras[i][1]), None)
    if last is None:
        raise SystemExit(f"not found after {start!r}: {end!r}")
    out = [list(p) for p in paras[first:last + 1]]
    out[-1][1] = out[-1][1][:out[-1][1].index(end) + len(end)]
    out[0][1] = out[0][1][out[0][1].index(start):]
    return [{"type": "verse" if k == "verse" else "p", "text": t} for k, t in out]


def fix(blocks, used):
    text = "\x00".join(b["text"] + "\n" for b in blocks)
    for a, b in FIXES:
        if a in text:
            text, used = text.replace(a, b), used | {a}
    for blk, t in zip(blocks, text.split("\x00")):
        blk["text"] = t[:-1]
    return blocks, used


def story(collection, order, title, work_id, blocks, **extra):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "").replace("’", "")).strip("-")
    return finish({"id": f"{collection['id']}--{slug}", "collectionId": collection["id"], "order": order,
                   "title": title, "origin": None, "excluded": False, "flags": extra.pop("flags", []),
                   "moral": None, "blocks": blocks, "workId": work_id, "livingTradition": LIVING, **extra})


def main(src):
    src, used = Path(src), set()
    jatakas = []
    for order, (title, work_id, page, number, pali, occasion, past, ident, flags) in enumerate(JATAKAS, 1):
        translator, source, year = VOLUMES[page.split("/")[0]]
        paras = jataka_paragraphs(src / JATAKA.format(page))
        blocks, used = fix(run(paras, *past) + run(paras, *ident), used)
        note = (f"The {pali} Jātaka (No. {number}), translated by {translator}. {occasion} {BODHISATTA}")
        jatakas.append(story(COWELL, order, title, work_id, [{"type": "note", "text": note}] + blocks,
                             flags=flags, source=source, firstPublished=year))
    paras = text_paragraphs((src / RHYS_DAVIDS_FILE).read_text(encoding="utf-8-sig"))
    nidana = []
    for order, (title, work_id, cut, note) in enumerate(NIDANAKATHA, 1):
        blocks, used = fix(run(paras, *cut), used)
        nidana.append(story(RHYS_DAVIDS, order, title, work_id, [{"type": "note", "text": note}] + blocks))
    title, work_id, cut, note = CARUS_STORY
    blocks, used = fix(run(text_paragraphs((src / CARUS_FILE).read_text(encoding="utf-8-sig")), *cut), used)
    carus = [story(CARUS, 1, title, work_id, [{"type": "note", "text": note}] + blocks)]
    unused = [a for a, _ in FIXES if a not in used]
    if unused:
        raise SystemExit(f"unused FIXES: {unused}")
    index = load_index()
    for col, stories in ((COWELL, jatakas), (RHYS_DAVIDS, nidana), (CARUS, carus)):
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:62} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
