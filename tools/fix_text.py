"""Editorial text corrections, applied to public/compendium after the extract/build scripts.

Every fix here was checked by reading the story; see docs/text-review.md for the review and what
still needs checking against the printed sources. The script is idempotent: a fix that has already
been applied is skipped, and one whose text can no longer be found fails loudly.

Run from the repo root:  python3 tools/fix_text.py && python3 tools/tag_stories.py
"""
import json
import re
from pathlib import Path

ROOT = Path("public/compendium")
STORIES = ROOT / "stories"

# (story id, old, new) — exact substrings, each expected exactly once in the story.
REPLACE = [
    # Quotation marks: missing closes, stray marks, and quotes inside speech printed as doubles.
    ("aesop--the-travelers-and-the-purse", 'angrily. " I found', 'angrily. "I found'),
    ("grimm-hunt--doctor-knowall", 'the words, "I am Doctor Knowall," and', "the words, 'I am Doctor Knowall,' and"),
    ("grimm-hunt--faithful-john", 'will be saved. "But what avails', 'will be saved." "But what avails'),
    ("grimm-hunt--hans-in-luck", 'click your tongue and call out, "Jup! Jup!"', "click your tongue and call out, 'Jup! Jup!'\""),
    ("grimm-hunt--hans-married", 'they said, "Klink," and', "they said, 'Klink,' and"),
    ("grimm-hunt--hans-married", "and broke in two.", 'and broke in two."'),
    ("grimm-hunt--iron-john",
     'crying, "Here comes our hobblety jig back again!" They asked, too, "Under what hedge hast thou '
     'been lying sleeping all the time?" He, however, said, "I did the best of all, and it would have '
     'gone badly without me." And then',
     "crying, 'Here comes our hobblety jig back again!' They asked, too, 'Under what hedge hast thou "
     "been lying sleeping all the time?' He, however, said, 'I did the best of all, and it would have "
     "gone badly without me.' And then"),
    ("grimm-hunt--the-devil-s-sooty-brother",
     'you must say, "From hell," and when you are asked who you are, you are to say, "The Devil\'s '
     'sooty brother, and my King as well." The soldier',
     "you must say, 'From hell,' and when you are asked who you are, you are to say, 'The Devil's "
     "sooty brother, and my King as well.'\" The soldier"),
    ("grimm-hunt--the-goose-girl-at-the-well", "We all begged and prayed for her, said the Queen, \"but",
     'We all begged and prayed for her," said the Queen, "but'),
    ("grimm-hunt--the-goose-girl-at-the-well", "neither seen nor hear anything", "neither seen nor heard anything"),
    ("grimm-hunt--the-three-little-men-in-the-wood", 'asked,"My child', 'asked, "My child'),
    ("grimm-hunt--mother-holle", "on the earth. I am Mother Holle.", 'on the earth. I am Mother Holle."'),
    ("grimm-hunt--the-two-kings-children", "into a fish-pond and myself into a fish.",
     'into a fish-pond and myself into a fish."'),
    ("grimm-hunt--death-s-messengers", "already dead? The man could make no answer",
     'already dead?" The man could make no answer'),
    ("grimm-hunt--the-riddle", "then it will be your wedding-mantle.", 'then it will be your wedding-mantle."'),
    ("grimm-hunt--the-fox-and-the-geese", 'still praying without stopping."', "still praying without stopping."),
    ("grimm-hunt--the-bittern-and-the-hoopoe", 'He called, "Come, cows, come," but', "He called, 'Come, cows, come,' but"),
    ("grimm-hunt--the-bittern-and-the-hoopoe", '"Up, up, up," screamed he', "'Up, up, up,' screamed he"),
    ("grimm-hunt--the-bittern-and-the-hoopoe", 'cries, "Come, cows, come," and the hoopoe, "Up, up, up."',
     "cries, 'Come, cows, come,' and the hoopoe, 'Up, up, up.'\""),
    ("grimm-hunt--the-robber-bridegroom", "'Does my bridegroom live in this house? She",
     "'Does my bridegroom live in this house?' She"),
    ("japan-ozaki--the-story-of-urashima-taro-the-fisher-lad", 'no "sake" in my boat', "no 'sake' in my boat"),
    ("lang-blue--cinderella-or-the-little-glass-slipper", "I wish I could—“;", "I wish I could—”;"),
    ("jacobs-english--johnny-cake", "screamed out: I'VE OUTRUN", "screamed out: “I'VE OUTRUN"),
    ("potter--the-tale-of-mrs-tiggy-winkle", '"Then Mrs. Tiggy-winkle made tea', "Then Mrs. Tiggy-winkle made tea"),
    ("potter--the-tale-of-ginger-and-pickles", "re-open the shop—Henny's Opening Sale!",
     're-open the shop—"Henny\'s Opening Sale!'),
    ("potter--the-tale-of-pigling-bland", "Alexander, you are not attending. Here are two licences",
     '"Alexander, you are not attending. Here are two licences'),
    # Typos (OCR or source), each with an unambiguous correction.
    ("grimm-hunt--the-wedding-of-mrs-fox", "red stockings on' and", "red stockings on, and"),
    ("grimm-hunt--king-thrushbeard", "his daugher did", "his daughter did"),
    ("grimm-hunt--cinderella", "used a strategem", "used a stratagem"),
    ("grimm-hunt--the-frog-king-or-iron-henry", "came swimmming up", "came swimming up"),
    ("grimm-hunt--the-lazy-spinner", "Neverthless after", "Nevertheless after"),
    ("grimm-hunt--the-master-thief", "as a dog burries things", "as a dog buries things"),
    ("grimm-hunt--the-six-servants", "into the princes's arms", "into the princess's arms"),
    ("grimm-hunt--the-old-woman-in-the-wood", "thou willt find", "thou wilt find"),
    ("grimm-hunt--the-drummer", "Hast thou forgotten thy heldest me dear?", "Hast thou forgotten thou heldest me dear?"),
    ("grimm-hunt--the-four-skilful-brothers", "more than breen clover", "more than green clover"),
    ("grimm-hunt--the-spirit-in-the-bottle", "the scolar was about", "the scholar was about"),
    ("grimm-hunt--the-two-brothers", '"Dear hunstman,', '"Dear huntsman,'),
    ("grimm-hunt--old-hildebrand", "ask himfor the", "ask him for the"),
    ("kipling-justso--the-elephants-child", "I Keep six honest", "I keep six honest"),
    # Line-break hyphenation left in the Hunt text ("Rose- red").
    ("grimm-hunt--domestic-servants", "From-thy-work- do-not-budge", "From-thy-work-do-not-budge"),
    ("grimm-hunt--the-story-of-schlauraffen-land", "Cock-a- doodle-doo", "Cock-a-doodle-doo"),
    ("grimm-hunt--snow-white-and-rose-red", "than Rose- red.", "than Rose-red."),
    ("grimm-hunt--the-glass-coffin", "the self- same day", "the self-same day"),
    ("grimm-hunt--the-griffin", "the wood- house", "the wood-house"),
    ("grimm-hunt--the-bittern-and-the-hoopoe", "too high- spirited", "too high-spirited"),
    ("grimm-hunt--the-goose-girl-at-the-well", "to the goose- girl", "to the goose-girl"),
    ("grimm-hunt--the-nix-of-the-mill-pond", "over the mill- dam", "over the mill-dam"),
    ("grimm-hunt--fair-katrinelje-and-pif-paf-poltrie", "High-and- Mighty", "High-and-Mighty"),
    # Footnote markers whose note text was lost in the source.
    ("grimm-hunt--the-grave-mound", "four measures* of corn", "four measures of corn"),
    ("grimm-hunt--the-raven", "in their delight.* Then", "in their delight. Then"),
]

# Section headings stored as plain paragraphs -> heading blocks (story id, paragraph text, heading).
HEADINGS = [
    ("andersen--the-snow-queen", "SECOND STORY. A Little Boy and a Little Girl", "Second Story. A Little Boy and a Little Girl"),
    ("andersen--the-snow-queen", "THIRD STORY. Of the Flower-Garden At the Old Woman's Who Understood Witchcraft",
     "Third Story. Of the Flower-Garden at the Old Woman’s Who Understood Witchcraft"),
    ("andersen--the-snow-queen", "FOURTH STORY. The Prince and Princess", "Fourth Story. The Prince and Princess"),
    ("andersen--the-snow-queen", "FIFTH STORY. The Little Robber Maiden", "Fifth Story. The Little Robber Maiden"),
    ("andersen--the-snow-queen", "SIXTH STORY. The Lapland Woman and the Finland Woman",
     "Sixth Story. The Lapland Woman and the Finland Woman"),
    ("andersen--the-snow-queen", "SEVENTH STORY. What Took Place in the Palace of the Snow Queen, and what Happened Afterward.",
     "Seventh Story. What Took Place in the Palace of the Snow Queen, and What Happened Afterward"),
    ("andersen--the-shoes-of-fortune", "II. What Happened to the Councillor", "II. What Happened to the Councillor"),
    ("andersen--the-shoes-of-fortune", "III. The Watchman's Adventure", "III. The Watchman’s Adventure"),
    ("andersen--the-shoes-of-fortune",
     "IV. A Moment of Head Importance—An Evening's “Dramatic Readings”—A Most Strange Journey",
     "IV. A Moment of Head Importance—An Evening’s “Dramatic Readings”—A Most Strange Journey"),
    ("andersen--the-shoes-of-fortune", "V. Metamorphosis of the Copying-Clerk", "V. Metamorphosis of the Copying-Clerk"),
    ("andersen--the-shoes-of-fortune", "VI. The Best That the Galoshes Gave", "VI. The Best That the Galoshes Gave"),
    ("grimm--the-adventures-of-chanticleer-and-partlet", "1. HOW THEY WENT TO THE MOUNTAINS TO EAT NUTS",
     "1. How They Went to the Mountains to Eat Nuts"),
    ("grimm--the-adventures-of-chanticleer-and-partlet", "2. HOW CHANTICLEER AND PARTLET WENT TO VISIT MR KORBES",
     "2. How Chanticleer and Partlet Went to Visit Mr Korbes"),
    ("grimm--the-adventures-of-chanticleer-and-partlet",
     "3. HOW PARTLET DIED AND WAS BURIED, AND HOW CHANTICLEER DIED OF GRIEF",
     "3. How Partlet Died and Was Buried, and How Chanticleer Died of Grief"),
    ("grimm--the-wedding-of-mrs-fox", "FIRST STORY", "First Story"),
    ("grimm--the-wedding-of-mrs-fox", "SECOND STORY", "Second Story"),
    ("grimm-hunt--the-wedding-of-mrs-fox", "FIRST STORY", "First Story"),
    ("grimm-hunt--the-wedding-of-mrs-fox", "SECOND STORY", "Second Story"),
    ("grimm-hunt--the-elves", "FIRST STORY", "First Story"),
    ("grimm-hunt--the-elves", "SECOND STORY", "Second Story"),
    ("grimm-hunt--the-elves", "THIRD STORY", "Third Story"),
]

# The first section of these stories had no heading at all; it goes before block 0.
# Wording as in the Gutenberg editions (Andersen #1597); listed for checking in docs/text-review.md.
LEADING_HEADINGS = {
    "andersen--the-snow-queen": "First Story. Which Treats of a Mirror and of the Splinters",
    "andersen--the-shoes-of-fortune": "I. A Beginning",
}

# Trailing junk: a separator line and the next section's title, and an end mark.
DROP_TRAILING = {
    "grimm-hunt--the-golden-key": [
        "----------------------------------------------------------- -----------------------------------------------------------",
        "Children's Legends",
    ],
    "japan-ozaki--the-stones-of-five-colors-and-the-empress-jokwa": ["THE END."],
}

# Translator's footnotes printed as body text -> note blocks; their markers come out of the text.
FOOTNOTE_STORIES = {
    "andersen--the-dream-of-little-tuk", "andersen--the-elderbush", "andersen--the-shadow",
    "andersen--the-shoes-of-fortune", "japan-ozaki--the-story-of-urashima-taro-the-fisher-lad",
    "japan-ozaki--the-tongue-cut-sparrow",
}
FOOTNOTE_BLOCK = re.compile(r"^\s*(?:\[\*\]|\[\d\]|\*)\s*")
FOOTNOTE_MARK = re.compile(r"\s?\[\*\]|\[\d\]|(?<=[\w.,!?”’])\*(?=\s|$)")

TITLES = {
    "grimm-hunt--the-devil-with-the-three-golden-hairs": "The Devil with the Three Golden Hairs",
    "grimm-hunt--fundevogel-bird-foundling": "Fundevogel (Bird-Foundling)",
    "grimm-hunt--little-snow-white": "Little Snow-White",
    "grimm-hunt--stories-about-snakes": "Stories About Snakes",
    "grimm-hunt--one-eye-two-eyes-and-three-eyes": "One-Eye, Two-Eyes, and Three-Eyes",
    "grimm-hunt--brides-on-their-trial": "Brides on Their Trial",
    "grimm-hunt--odds-and-ends": "Odds and Ends",
    "grimm-hunt--the-sparrow-and-his-four-children": "The Sparrow and His Four Children",
    "grimm-hunt--the-spindle-the-shuttle-and-the-needle": "The Spindle, the Shuttle, and the Needle",
}

# Lang's source notes lost their accents in the ASCII edition.
ORIGINS = {
    "Asbjornsen and Moe.": "Asbjørnsen and Moe.",
    "Cabinet des Fees.": "Cabinet des Fées.",
    "Fortunee. Par Madame la Comtesse d’Aulnoy.": "Fortunée. Par Madame la Comtesse d’Aulnoy.",
    "La Belle et la Bete. Par Madame de Villeneuve.": "La Belle et la Bête. Par Madame de Villeneuve.",
}

# Opening words set in capitals by the printed books' drop caps ("THERE was once", "I AM the").
# Only when the next word has lower case, so shouted lines ("BE BOLD, BE BOLD") are left alone.
DROP_CAP = re.compile(r"^(\s*[“‘\"']?)(I )?([A-Z])([A-Z]+)(?=[\s,’']+[A-Za-z’']*[a-z])")

# Speech quoted inside speech but printed with double quotes: (story id, from, to) spans whose
# double quotes become single.
NESTED = [
    ("grimm-hunt--the-goose-girl-at-the-well", 'Then the King spoke, "My daughters', 'repaid thee with salt."'),
]


def load(sid):
    return json.loads((STORIES / f"{sid}.json").read_text())


def save(story):
    (STORIES / f"{story['id']}.json").write_text(json.dumps(story, ensure_ascii=False, indent=1))


def texts(story):
    return [b for b in story["blocks"] if "text" in b]


def replace(story, old, new):
    applied = any(new in b["text"] for b in texts(story))
    hits = [b for b in texts(story) if old in b["text"]]
    if not hits or (old in new and applied):
        if applied:
            return False
        raise SystemExit(f"{story['id']}: text not found: {old!r}")
    if len(hits) > 1 or hits[0]["text"].count(old) > 1:
        raise SystemExit(f"{story['id']}: ambiguous: {old!r}")
    hits[0]["text"] = hits[0]["text"].replace(old, new)
    return True


def footnotes(story):
    changed = False
    for b in story["blocks"]:
        if b["type"] in ("p", "verse") and FOOTNOTE_BLOCK.match(b["text"]):
            text = " ".join(line.strip() for line in b["text"].split("\n") if line.strip())
            b.clear()
            b.update(type="note", text=FOOTNOTE_BLOCK.sub("", text))
            changed = True
        elif "text" in b and FOOTNOTE_MARK.search(b["text"]) and b["type"] != "note":
            b["text"] = FOOTNOTE_MARK.sub("", b["text"])
            changed = True
    return changed


def drop_caps(story):
    changed = False
    for b in story["blocks"]:
        if b["type"] not in ("p", "verse"):
            continue
        t = DROP_CAP.sub(lambda m: f"{m[1]}I {(m[3] + m[4]).lower()}" if m[2] else f"{m[1]}{m[3]}{m[4].lower()}",
                         b["text"])
        if t != b["text"]:
            b["text"], changed = t, True
    return changed


def split_twelve_idle_servants(index, stories):
    """Hunt's 151* 'The Twelve Idle Servants' was merged into 151 'The Three Sluggards'."""
    sid = "grimm-hunt--the-three-sluggards"
    new_id = "grimm-hunt--the-twelve-idle-servants"
    if new_id in stories:
        return set()
    s = stories[sid]
    at = next(i for i, b in enumerate(s["blocks"]) if b.get("text") == "151* The Twelve Idle Servants")
    rest = s["blocks"][at + 1:]
    s["blocks"] = s["blocks"][:at]
    order = s["order"] + 1
    touched = {sid, new_id}
    for e in index["stories"]:
        if e["collectionId"] == "grimm-hunt" and e["order"] >= order:
            e["order"] += 1
            stories[e["id"]]["order"] = e["order"]
            touched.add(e["id"])
    stories[new_id] = dict(s, id=new_id, order=order, title="The Twelve Idle Servants",
                           workId="grimm-khm-151a", originalTitle="Die zwölf faulen Knechte", blocks=rest)
    pos = next(i for i, e in enumerate(index["stories"]) if e["id"] == sid)
    index["stories"].insert(pos + 1, dict(index["stories"][pos], id=new_id, order=order,
                                          title="The Twelve Idle Servants", workId="grimm-khm-151a"))
    for c in index["collections"]:
        if c["id"] == "grimm-hunt":
            c["storyCount"] += 1
    return touched


def main():
    # Everything is applied in memory and only written once every fix has been found.
    index = json.loads((ROOT / "index.json").read_text())
    stories = {e["id"]: load(e["id"]) for e in index["stories"]}
    touched = split_twelve_idle_servants(index, stories)

    for sid, old, new in REPLACE:
        if replace(stories[sid], old, new):
            touched.add(sid)
    for sid, start, end in NESTED:
        for b in texts(stories[sid]):
            i = b["text"].find(start)
            j = b["text"].find(end, i)
            if i >= 0 and j > i:
                j += len(end)
                b["text"] = b["text"][:i] + b["text"][i:j].replace('"', "'") + b["text"][j:]
                touched.add(sid)
                break
        else:
            if not any(start.replace('"', "'") in b["text"] for b in texts(stories[sid])):
                raise SystemExit(f"{sid}: nested span not found: {start!r}")
    for sid, para, heading in HEADINGS:
        b = next((b for b in stories[sid]["blocks"] if b.get("text") in (para, heading)), None)
        if b is None:
            raise SystemExit(f"{sid}: heading paragraph not found: {para!r}")
        if b["type"] != "heading" or b["text"] != heading:
            b.update(type="heading", text=heading)
            touched.add(sid)
    for sid, heading in LEADING_HEADINGS.items():
        blocks = stories[sid]["blocks"]
        if not (blocks[0]["type"] == "heading" and blocks[0]["text"] == heading):
            blocks.insert(0, dict(type="heading", text=heading))
            touched.add(sid)
    for sid, junk in DROP_TRAILING.items():
        blocks = stories[sid]["blocks"]
        while blocks and blocks[-1].get("text") in junk:
            blocks.pop()
            touched.add(sid)
    for sid in FOOTNOTE_STORIES:
        if footnotes(stories[sid]):
            touched.add(sid)
    # One-offs: a footnote inside a verse block, and one stored as verse at the end of the story.
    sw = stories["andersen--the-swineherd"]["blocks"]
    i = next(i for i, b in enumerate(sw) if "Alles ist weg" in b.get("text", ""))
    if "\n\n" in sw[i]["text"]:
        verse, note = sw[i]["text"].split("\n\n", 1)
        sw[i]["text"] = verse.replace("weg!”*", "weg!”")
        sw.insert(i + 1, dict(type="note", text=" ".join(l.strip() for l in note.lstrip(" *").split("\n"))))
        touched.add("andersen--the-swineherd")
    gg = stories["grimm--the-golden-goose"]
    if gg["blocks"][-1]["type"] == "verse" and "[*] Simpleton" in gg["blocks"][-1]["text"]:
        gg["blocks"][-1] = dict(type="note", text="Dummling: Simpleton.")
        gg["blocks"][0]["text"] = gg["blocks"][0]["text"].replace("Dummling,[*]", "Dummling,")
        touched.add("grimm--the-golden-goose")
    for sid, s in stories.items():
        if drop_caps(s):
            touched.add(sid)
        if s.get("origin") in ORIGINS:
            s["origin"] = ORIGINS[s["origin"]]
            touched.add(sid)
        if sid in TITLES and s["title"] != TITLES[sid]:
            s["title"] = TITLES[sid]
            touched.add(sid)

    for e in index["stories"]:
        s = stories[e["id"]]
        words = len(" ".join(b.get("text", "") for b in s["blocks"]).split())
        s["wordCount"], s["readingMinutes"] = words, max(1, round(words / 180))
        if e["id"] in touched:
            save(s)
        e.update(title=s["title"], wordCount=s["wordCount"], readingMinutes=s["readingMinutes"])
    (ROOT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1))
    print(f"{len(touched)} stories corrected")


if __name__ == "__main__":
    main()
