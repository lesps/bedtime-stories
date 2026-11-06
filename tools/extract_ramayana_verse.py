#!/usr/bin/env python3
"""The Ramayana in five parts from Romesh C. Dutt's verse condensation (1899), for the Hindu
shelf's six-part Ramayana (part 4, the bridge, is Manmatha Nath Dutt's prose, in
`extract_hindu.py`).

    git clone --depth 1 --filter=blob:none --no-checkout https://github.com/jonnyg23/mahabrain.git src/mahabrain
    git -C src/mahabrain checkout HEAD -- sacred_obsidian_vault/hin/dutt
    python3 tools/extract_ramayana_verse.py src

The text is the sacred-texts.com edition (one HTML page per book), as mirrored in that
repository. Each canto has a numeral and a title; each couplet is a paragraph. A story is one or
more runs of cantos from one book, each run a note (or None) and the first and last canto
numerals, optionally cut to the couplets from one containing given words to one containing
others; a canto title becomes a heading and each couplet a verse block. FIXES puts right the
digitization's slips in the cantos used (each must be used); a single hyphen after punctuation
is the digitization's dash, and Dutt's capitals for the gods' names are printed as ordinary
names. Writes `rc-dutt-ramayana`, every story marked `livingTradition`.
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compendium_io import finish, load_index, save_index, upsert_collection  # noqa: E402

COLLECTION = {"id": "rc-dutt-ramayana", "title": "The Ramayana, Condensed into English Verse", "author": "Valmiki",
              "contributor": "Translated by Romesh C. Dutt", "firstPublished": 1899,
              "source": "https://sacred-texts.com/hin/dutt/index.htm", "license": "Public domain in the USA",
              "language": "en", "originalLanguage": "sa"}
BOOKS = "mahabrain/sacred_obsidian_vault/hin/dutt/rama{:02}.md"
LIVING = "Hindus"

FIXES = [
    # Book I
    ("spake his memage", "spake his message"), ("to the risha famed", "to the rishi famed"),
    ("strung the bow Of RUDRA", "strung the bow of RUDRA"), ("adorn our palace balls", "adorn our palace halls"),
    # Book II
    ("Carne the old", "Came the old"), ("woke-within", "woke within"), ("thy king a obedience", "thy king's obedience"),
    ("his tom and tortured", "his torn and tortured"), ("Rath my unknown", "Hath my unknown"),
    ("ever-lovinging", "ever-loving"), ("you Will serve", "you will serve"), ('uttered Rama," what', 'uttered Rama, "what'),
    # Book III
    ("Dearest song they disinherit", "Dearest sons they disinherit"), ("roval father willetb", "royal father willeth"),
    ("what Sita, said", "what Sita said"), ("Lakshman,shall", "Lakshman shall"), ("thyloving", "thy loving"),
    ("this then they sacred", "this then thy sacred"), ("whenwith", "when with"), ("tempered wen", "tempered well"),
    ("Seekand", "Seek and"), ("Part we then from loving kinsmen", '"Part we then from loving kinsmen'),
    # Book IV
    ("Till. once more", "Till once more"),
    # Book VI
    ("SURPA-YARUA", "SURPA-NAKHA"), ("forlove makes bold afemale, thus didshe", "for love makes bold a female, thus did she"),
    ("Surpa -nakha", "Surpa-nakha"), ("Ruddy in thy youthful beauty", '"Ruddy in thy youthful beauty'),
    ("Are these mocking accents", '"Are these mocking accents'), ('ample-hearted love! "', 'ample-hearted love!"'),
    ("Maricha, wore", "Maricha wore"), ("thou caust capture", "thou canst capture"), ("my in-most", "my inmost"),
    ("Markest thou my Rama's danger", '"Markest thou my Rama\'s danger'), ("trembled' neath", "trembled 'neath"),
    ("his red eve's", "his red eye's"), ("sylvan russet drew", "sylvan russet dress"), ("dwclls", "dwells"),
    ("Royal balls and", "Royal halls and"), ("Vassus", "Vasus"), ("Beast's of prey", "Beasts of prey"),
    ("Wheref ore", "Wherefore"), ("upon my Sita, wait", "upon my Sita wait"), ("Ragu's son", "Raghu's son"),
    ("smiling vale'.", "smiling vale,"), ("consort say'", "consort say,"), ("Rania's", "Rama's"),
    # Book VII
    ("Banished from, Kishkindha's", "Banished from Kishkindha's"), ("stoutly stand.!", "stoutly stand!"),
    ("the hand lie offered", "the hand he offered"), ("we will f ace", "we will face"),
    ("thy brotherfall", "thy brother fall"), ("Jambaman", "Jambavan"),
    # Book VIII
    ("bush and trep.", "bush and tree,"), ("Kanka was like", "Lanka was like"), ("depicted with it sigh", "depicted with a sigh"),
    ("Stem destroyer", "Stern destroyer"), ("Sagriva's", "Sugriva's"), ("Hantiman", "Hanuman"), ("soft eve", "soft eye"),
    ("veng-eful", "vengeful"), ("mountains . slaying", "mountains, slaying"), ("Sita, held", "Sita held"),
    ("Till he, wins", "Till he wins"), ("her loving row", "her loving vow"), ("llanuman, iny friend", "Hanuman, my friend"),
    ("shrouded then her light", "shrouded when her light"), ("methink the gracious", "methinks the gracious"),
    # Book X
    ("Once, more healed", "Once more healed"), ("Mightiest be of all", "Mightiest he of all"),
    ("and massive rock.", "and massive rock,"), ("Raksha's towering held", "Raksha's towering head"),
    ("Kunibha-karna", "Kumbha-karna"), ("Suguriva", "Sugriva"), ("Kumbha-kama", "Kumbha-karna"),
    ("ears awail", "ears assail"), ("royal best was heard", "royal hest was heard"), ("Mahaparshwa. slumbered", "Mahaparshwa slumbered"),
    ("wingéd courses flew", "wingéd coursers flew"), ("gallant charges slew", "gallant chargers slew"),
    ("Dashina from", "Dashing from"), ("Laksliman", "Lakshman"), ("Welcome, Lakshman! thee", '"Welcome, Lakshman! thee'),
    ("trite is love", "true is love"), ("Where is be who", "Where is he who"), ("thus unconscious he,", "thus unconscious lie,"),
    ("terror havan sought", "terror Ravan sought"), ("lain the lifeless", "laid the lifeless"), ("to facein", "to face in"),
    ("due abititions", "due ablutions"),
    # Book XI
    ("saintly Sita, spake", "saintly Sita spake"), ("with vour mighty", "with your mighty"), ("Risked your fife", "Risked your life"),
    ("FuneraI", "Funeral"), ("betraved", "betrayed"), ('" I am true', '"I am true'), ("Pare is she", "Pure is she"),
    ("Never from the time I saw her", '"Never from the time I saw her'), ("Bibhisban", "Bibhishan"),
    ("faitbful", "faithful"), ("pearls in eaves", "pearls in caves"), ("Sita, lived", "Sita lived"),
    ("in her might '", "in her might,"), ("a happy, night", "a happy night"), ("gentle Sita,!", "gentle Sita!"),
    ("ourpriests", "our priests"), ("Ayodhya'a", "Ayodhya's"), ("did, Ayodhya's", "did Ayodhya's"),
    ("Gautama. and", "Gautama and"), ("verged in holy", "versed in holy"), ("fraurant", "fragrant"),
    ("consecrated kine", "consecrated king"), ("soft and smiling vale,", "soft and smiling vale."),
]
LOWER = {"and", "of", "the", "by", "in", "on", "to", "a", "an", "at", "for", "with", "from"}

# (title, workId, flags, [(book, note or None, first canto, last canto[, (first words, last words)])])
STORIES = [
    ("The Ramayana, Part 1: The Bow and the Exile", "hindu-ramayana-1",
     ["mature-themes"],  # Kaikeyi threatens to die, Bharat vows to die on the pyre
     [(1, "King Dasa-ratha of Ayodhya has four sons, and Rama, the eldest, is the hero of this story. The sage "
          "Viswa-mitra has brought Rama and his brother Lakshman to the city of Mithila, whose king, Janak, has "
          "promised his daughter Sita to the man who can bend the great bow of the god Rudra (Shiva). A rishi is "
          "a holy sage, and Rakshas are demons.", "II", "II"),
      (2, "Rama marries Sita. Years later old King Dasa-ratha decides to crown Rama as his heir. But Queen "
          "Kaikeyi, the youngest of his three queens and the mother of his son Bharat, is persuaded by her maid "
          "that Rama's crowning will ruin her and her son, and she remembers two boons that the king once "
          "promised her.", "V", "V"),
      (2, "All night the king begs Kaikeyi to change her mind, but she will not.", "VII", "VII"),
      (3, None, "I", "II"),
      (4, "Rama, Sita and Lakshman go away into the forest, and the old king dies of grief. Bharat, who was far "
          "away, comes home, refuses the throne, and follows Rama into the forest to beg him to come back and "
          "be king.", "V", "V")]),
    ("The Ramayana, Part 2: Sita Is Stolen", "hindu-ramayana-2",
     ["mature-themes"],  # Surpa-nakha maimed; Ravan's lust
     [(6, "For thirteen years Rama, Sita and Lakshman have lived in the forest. Now they have made their home at "
          "Panchavati, by the river Godavari, in a land where the Rakshas roam. The ten-headed Ravan, king of "
          "the Rakshas, rules the island of Lanka in the far south.", "I", "VII")]),
    ("The Ramayana, Part 3: Hanuman Finds Sita", "hindu-ramayana-3", [],
     [(7, "Rama and Lakshman have searched everywhere for Sita, and the dying vulture Jatayu has told them that "
          "Ravan carried her away to the south. Vanars are the monkey people.", "I", "I"),
      (7, "Rama keeps his promise: Bali is slain, and Sugriva becomes king of the Vanars in Kishkindha. When the "
          "rains are over, Sugriva sends out armies to search for Sita in every direction. To his bravest chiefs, "
          "Hanuman among them, he gives the south.", "VI", "VI", ("Next to Nila", "ocean wave!\"")),
      (8, "Far in the south the searchers learn that Sita is held in Lanka, an island across the sea. Hanuman, the "
          "son of the Wind, leaps across the sea and searches the city of Lanka.", "I", "IV")]),
    ("The Ramayana, Part 5: The Battle", "hindu-ramayana-5",
     ["mature-themes"],  # the battlefield
     [(10, "Rama's army of Vanars has crossed the sea to Lanka on the bridge it built, and the battle has begun. "
           "Lakshman has been struck down once already and healed. Kumbha-karna, Ravan's giant brother, sleeps "
           "for months at a time.", "IV", "IV"),
      (10, "Ravan's son Indrajit, a great magician, fights three battles, and at last Lakshman slays him. Ravan "
           "mourns his son.", "VIII", "XII")]),
    ("The Ramayana, Part 6: Rama Comes Home", "hindu-ramayana-6",
     ["mature-themes"],  # Sita asks for her funeral pyre
     [(11, "Ravan is dead, and his good brother Bibhishan is king of Lanka. Sita is brought to Rama before all "
           "the army. The fourteen years of Rama's exile are nearly over.", "I", "V",
       (None, "soft and smiling vale."))]),
]


def titlecase(s):
    words = [w.capitalize() for w in s.lower().split()]
    words = [w if i == 0 or w.lower() not in LOWER else w.lower() for i, w in enumerate(words)]
    return re.sub(r"'S\b", "'s", " ".join(words))


def fix(text, used):
    for a, b in FIXES:
        if a in text:
            text = text.replace(a, b)
            used.add(a)
    text = re.sub(r"(?<=[,;:.!?])-(?=[\w\"' ])", "--", text)  # the digitization's dash
    return re.sub(r"\b[A-Z][A-Z]+(?:-[A-Z]+)?\b(?:'S)?", lambda m: m.group(0).title().replace("'S", "'s")
                  if m.group(0) not in ("I",) else m.group(0), text)


def cantos(src, book, used):
    raw = (Path(src) / BOOKS.format(book)).read_text(encoding="utf-8")
    raw = raw[raw.find("<h1"):]
    parts = re.split(r'<h2 align="CENTER">([IVXL]+)\.?</h2>\s*<h2 align="CENTER">(.*?)</h2>', raw, flags=re.S)
    out = {}
    for i in range(1, len(parts), 3):
        body = parts[i + 2].split("<hr>")[0]
        couplets = []
        for para in re.findall(r"<p>(.*?)</p>", body, flags=re.S):
            lines = [html.unescape(re.sub(r"<[^>]+>", "", line)).strip() for line in para.split("<br>")]
            lines = [re.sub(r"\s+", " ", line) for line in lines if line]
            if lines:
                couplets.append(fix("\n".join(lines), used))
        title = fix(html.unescape(parts[i + 1]).strip(), used)
        out[parts[i]] = (titlecase(title), couplets)
    return out


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "")).strip("-")


def main(src):
    used, books, stories = set(), {}, []
    for title, work_id, flags, runs in STORIES:
        blocks = []
        for book, note, first, last, *cut in runs:
            numbered = books.setdefault(book, cantos(src, book, used))
            keys = list(numbered)
            if note:
                blocks.append({"type": "note", "text": note})
            run = []
            for key in keys[keys.index(first):keys.index(last) + 1]:
                heading, couplets = numbered[key]
                run.append({"type": "heading", "text": heading})
                run += [{"type": "verse", "text": c} for c in couplets]
            if cut:
                start, end = cut[0]
                i = next(i for i, b in enumerate(run) if start and start in b["text"]) if start else 1
                j = next(j for j, b in enumerate(run) if end and end in b["text"]) if end else len(run) - 1
                run = run[:1] + run[i:j + 1]
            blocks += run
        stories.append(finish({"id": f"{COLLECTION['id']}--{slug(title)}", "collectionId": COLLECTION["id"],
                               "order": len(stories) + 1, "title": title, "origin": None, "excluded": False,
                               "flags": flags, "moral": None, "blocks": blocks, "workId": work_id,
                               "livingTradition": LIVING}))
    unused = [a for a, _ in FIXES if a not in used]
    if unused:
        raise SystemExit(f"fixes not used: {unused}")
    index = load_index()
    upsert_collection(index, COLLECTION, stories)
    for st in stories:
        lv = st["readingLevel"]
        print(f"{st['id']:62} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
