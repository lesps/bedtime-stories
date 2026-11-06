#!/usr/bin/env python3
"""Hindu stories: myths of Vishnu, Shiva, the Ganga, Ganesha, Krishna and Hanuman, and episodes of
the Mahabharata, from Kisari Mohan Ganguli's Mahabharata (1883–96), Manmatha Nath Dutt's Vishnu
Purana (1896, after H. H. Wilson) and Dutt's Ramayana (1891–94), and Krishna's childhood from Baba
Premanand Bharati's Sree Krishna, the Lord of Love (1904). (The rest of the Ramayana serial is
Romesh C. Dutt's verse, in `extract_ramayana_verse.py`.)

    git clone --depth 1 https://github.com/GITenberg/The-Mahabharata-of-Krishna-Dwaipayana-Vyasa-Volume-1Books-1-2-and-3_15474.git src/The-Mahabharata-of-Krishna-Dwaipayana-Vyasa-Volume-1Books-1-2-and-3_15474
    git clone --depth 1 https://github.com/GITenberg/A-Prose-English-Translation-of-Vishnupuranam-Based-on-Professor-H-H-Wilsons-translation_66208.git src/A-Prose-English-Translation-of-Vishnupuranam-Based-on-Professor-H-H-Wilsons-translation_66208
    git clone --depth 1 https://github.com/GITenberg/The-Ramayana-Volume-One-Balakandam-and-Ayodhyakandam_57265.git src/The-Ramayana-Volume-One-Balakandam-and-Ayodhyakandam_57265
    git clone --depth 1 https://github.com/GITenberg/The-Ramayana-Volume-Two_57826.git src/The-Ramayana-Volume-Two_57826
    git clone --depth 1 https://github.com/GITenberg/The-Ramayana-Volume-3-Yuddhakandam_60188.git src/The-Ramayana-Volume-3-Yuddhakandam_60188
    git clone --depth 1 https://github.com/GITenberg/The-Ramayana-Volume-4-Uttara-Kanda_62496.git src/The-Ramayana-Volume-4-Uttara-Kanda_62496
    git clone --depth 1 https://github.com/GITenberg/Sree-Krishna-the-Lord-of-Love_67019.git src/Sree-Krishna-the-Lord-of-Love_67019
    python3 tools/extract_hindu.py src

A story is one or more runs of text, each from a phrase to a phrase (both kept) in one of the
books, split into paragraphs on blank lines; a note can come before each run. Section headings,
the Mahabharata's "So ends the … section" lines and "(… continued)" lines, footnote markers and
the Ramayana's footnotes and italic marks are dropped. A Ramayana story from a later volume carries that volume as
its own `source` and `firstPublished`. Writes `ganguli-mahabharata`, `dutt-vishnu-purana`,
`dutt-ramayana` and `bharati-krishna`, every story marked `livingTradition`.
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
BHARATI = {**COMMON, "id": "bharati-krishna", "title": "Sree Krishna, the Lord of Love",
           "author": "Baba Premanand Bharati", "contributor": None, "firstPublished": 1904,
           "source": "https://www.gutenberg.org/ebooks/67019"}
# Books by key; a run names its book when it isn't the collection's own (the key is the collection id).
FILES = {
    "ganguli-mahabharata": "The-Mahabharata-of-Krishna-Dwaipayana-Vyasa-Volume-1Books-1-2-and-3_15474/15474-0.txt",
    "dutt-vishnu-purana": "A-Prose-English-Translation-of-Vishnupuranam-Based-on-Professor-H-H-Wilsons-translation_66208/66208-0.txt",
    "dutt-ramayana": "The-Ramayana-Volume-One-Balakandam-and-Ayodhyakandam_57265/57265-0.txt",
    "ramayana-2": "The-Ramayana-Volume-Two_57826/57826-0.txt",
    "ramayana-3": "The-Ramayana-Volume-3-Yuddhakandam_60188/60188-0.txt",
    "ramayana-4": "The-Ramayana-Volume-4-Uttara-Kanda_62496/62496-0.txt",
    "bharati-krishna": "Sree-Krishna-the-Lord-of-Love_67019/67019-0.txt",
}
# The book a story comes from, where it isn't its collection's first volume: (source, firstPublished).
VOLUMES = {"ramayana-3": ("https://www.gutenberg.org/ebooks/60188", 1893),
           "ramayana-4": ("https://www.gutenberg.org/ebooks/62496", 1894)}
LIVING = "Hindus"
# Slips in the digitized texts, put right wherever they turn up (each must be used).
FIXES = [
    ("Sribatsa an his breast", "Sribatsa on his breast"), ("withold thy four-armed", "withhold thy four-armed"),
    ("who was formerly the destroyer, Considering", "who was formerly the destroyer. Considering"),
    ("stricken with grief and keeping", "stricken with grief and weeping"), ("Hearing those wards", "Hearing those words"),
    ("the most subtiles of atoms", "the most subtile of atoms"), ("vomitted", "vomited"),
    ("the rainy reason", "the rainy season"), ("they will like the offenders", "they will kill the offenders"),
    ("autumnal dowers", "autumnal flowers"), ("Govaradhana", "Govardhana"), ("Parsara said", "Parāçara said"),
    ("subsistance", "subsistence"),
    ("At the every day", "At the very day"), ("obstructing all execrations", "obstructing all excretions"),
    ("everything before him. in wrath", "everything before him, in wrath"), ("boon, O lard,", "boon, O lord,"),
    ("touched my hand lo His", "touched my hand to His"), ("pots and chums", "pots and churns"),
    ("walking: away", "walking away"), ("came on earth. He would", "came on earth, He would"),
    ("And. O Bharata", "And, O Bharata"), ("addressed by the swan. Damayanti", "addressed by the swan, Damayanti"),
    ("the swans in burning me", "the swans is burning me"), ("Mahavat", "Maghavat"), ("slaver of Vala", "slayer of Vala"),
    ("stood revealed to his shadow", "stood revealed by his shadow"), ("blessed legions", "blessed regions"),
    ("set out tor that", "set out for that"), ("harsh syllabus", "harsh syllables"),
    ("Salyavana’s", "Satyavan’s"), ("given away but one;", "given away but once;"),
    ("a longer way of.", "a longer way off."), ("said into me", "said unto me"),
    ("lather and grand-father", "father and grand-father"),
    ("hundrerds", "hundreds"), ("covetuousness", "covetousness"), ("Laskhmana", "Lakshmana"),
    ("(Formerly) is Mandara", "(Formerly) in Mandara"),
]

MARKANDEYA = "Markandeya, a sage who has lived through many ages, tells this story to the Pandava prince Yudhishthira."
PARASARA = "The sage Parasara tells this story to his pupil Maitreya."
DRONA = ("Drona, a great master of arms, teaches the young princes of the Kuru royal family: the five Pandava "
         "brothers, Yudhishthira, Bhima, Arjuna and the twins Nakula and Sahadeva, and their cousins, the hundred "
         "sons of Dhritarashtra, led by Duryodhana. The bard Vaisampayana tells this story to King Janamejaya.")
KANSA = ("Kansa, the cruel king of Mathura, has been warned that the eighth child of his cousin Devaki will "
         "destroy him. He keeps Devaki and her husband Vasudeva prisoner, and has killed each of their "
         "children as soon as it was born, all but the seventh, who was carried away before birth to be "
         "born to Vasudeva's other wife, Rohini. Now the gods have prayed to Vishnu, and he is to be born as "
         "Devaki's eighth child.")

# (collection, title, workId, flags, [(first words, last words, note before the run or None[, book])])
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
    (GANGULI, "Ganesha Writes Down the Mahabharata", "hindu-ganesha-scribe", [],
     [("The son of Satyavati having, by penance and meditation", "other verses in great abundance.",
       "The bard Sauti tells the sage Saunaka how the Mahabharata was first written down. Vyasa, the son "
       "of Satyavati, is the poet who made it.")]),
    (VISHNU, "The Birth of Krishna", "hindu-krishna-birth", ["mature-themes"],  # Kansa kills Devaki's babies
     [("Parāçara said;—Being thus eulogised by the celestials", "the sight of the king of the Bhojas.",
       KANSA + " " + PARASARA)]),
    (BHARATI, "Krishna the Butter Thief", "hindu-krishna-butter", [],
     [("And Nanda prepared a great feast for the naming of Him", "know Him as her Lord?",
       "Baby Krishna has been carried in secret to the village of the cowherd Nanda, whose wife Yasoda "
       "brings him up as her own son. His brother Balarama, Devaki's seventh child, is there too."),
      ("And naughty Thou wert and full of mischief", "as they crashed down beside him.", None)]),
    (VISHNU, "Krishna and the Serpent Kaliya", "hindu-kaliya", [],
     [("Parāçara said:—Once on a time Krishna went to Vrindavana", "Krishna came back to Vraja.",
       "Krishna is growing up among the cowherds of Vraja with his brother Balarama (Rama). "
       + PARASARA)]),
    (VISHNU, "Krishna Lifts the Mountain", "hindu-govardhan", [],
     [("At this season, when the heavens were clear", "to its original site.",
       "The rainy season is over, and it is autumn in Vraja. Sakra is another name for Indra, the king of "
       "the gods, who sends the rain. " + PARASARA),
      ("Parāçara said:—After the inhabitants of Gokula had been saved", "deluged the earth with their milk.",
       None)]),
    (RAMAYANA, "Hanuman and the Sun", "hindu-hanuman-sun", [],
     [("Hanumān’s father Keshari reigned", "were all moved with pity.",
       "After the great war, the sage Agastya tells Rama about the wonderful thing his friend Hanuman, the "
       "monkey hero, did when he was a baby. Marut is the Wind, Hanuman's father, and Rahu is the demon who "
       "swallows the sun and moon at an eclipse.", "ramayana-4"),
      ("From this circumstance, thy name hath been known", "Thy death shall take place according to thy will.’",
       "The end of the story is told in an earlier book of the Ramayana, the Kishkindha Kanda (Dutt's "
       "second volume, 1891). Before Hanuman leaps across the ocean to find Sita, the old bear Jambavan "
       "reminds him of it:", "ramayana-2")]),
    (RAMAYANA, "The Ramayana, Part 4: The Bridge to Lanka", "hindu-ramayana-4", [],
     [("Then on the shore of the sea, Rāghava, spreading", "honored by the Brahmanas, Rāma.",
       "Hanuman has come back with news of Sita, and Rama (Raghava) has marched south with King Sugriva and "
       "his army of monkeys to the shore of the sea. Ravana's good brother Vibhishana (Bibhishana) begged "
       "Ravana to give Sita back, and when Ravana drove him away, he came over to Rama's side. Now the army "
       "must find a way across the sea to Lanka. Lakshmana is Rama's brother; Varuna is the lord of the "
       "waters, and Makaras are sea monsters.", "ramayana-3")]),
    (GANGULI, "Arjuna Sees Only the Bird", "hindu-arjuna-bird", [],
     [("And Drona, beholding his pupil’s devotion to arms", "an archer equal to thee in this world.’", DRONA),
      ("O bull among men, one day Drona desirous of testing", "brought it down to the ground.", None)]),
    (GANGULI, "Ekalavya, the Archer Who Taught Himself", "hindu-ekalavya", ["mature-themes"],  # cuts off his thumb
     [("Amongst those that came there, O monarch, was a prince named Ekalavya", "the fever (of jealousy) having left him.",
       DRONA + " Drona has promised his favourite pupil, Arjuna, that no archer in the world will ever equal "
       "him.")]),
    (GANGULI, "Nala and Damayanti", "hindu-nala", ["mature-themes"],  # "poison, or fire, or water or the rope"
     [("There was a king named Nala, the son of Virasena", "the king ruled the earth abounding in wealth.’”",
       "The sage Vrihadaswa tells this story to the Pandava prince Yudhishthira, who has lost his kingdom in a "
       "game of dice and is living in exile in the forest. It is the first part of the long story of Nala and "
       "Damayanti.")]),
    (GANGULI, "Bhima Meets Hanuman", "hindu-bhima-hanuman", [],
     [("Then the Pandava winded with all his might his loud-blowing shell", "lieth even in that direction.”",
       "During their exile, the five Pandava brothers have come to the mountain Gandhamadana in the "
       "Himalayas. The wind has blown a wonderful golden lotus to their queen, Draupadi, and she has asked "
       "Bhima (Bhimasena), the strongest of the brothers, to bring her more. Bhima, like Hanuman, is a son of "
       "the Wind god. He has forced his way up the mountain, scattering the wild beasts before him."),
      ("Thus addressed, the powerful Bhimasena of mighty arms", "Verily, Time is irresistible’", None),
      ("Bhimasena said, ‘Without beholding thy former shape", "hath established his fame among men.",
       "Bhima asks Hanuman about the four ages of the world, and Hanuman tells him at length how goodness "
       "grows less in each age. Then Bhima asks once more."),
      ("Then contracting that huge body of his", "Hanuman vanished at that spot.”", None)]),
    (GANGULI, "Savitri and Satyavan", "hindu-savitri", [],
     [("On one occasion, O Bharata, when that king, the lord of the Madras", "preparations for his daughter’s wedding!’”",
       "The sage Markandeya tells this story to the Pandava prince Yudhishthira. Aswapati, king of the Madras, "
       "had no children until the goddess Savitri granted him a daughter, whom he named after her. When she "
       "grew up and no one asked to marry her, her father told her to go out and choose a husband for herself."),
      ("At length, O king, after a long time had passed away", "hastily proceeded towards the hermitage.’”",
       "Savitri marries Satyavan and goes to live with him and his blind parents in the forest. She puts "
       "aside her jewels, dresses like a hermit and serves them all lovingly, but she never forgets Narada's "
       "words."),
      ("And it so happened, O king, that there came to that hermitage", "as also the race of her husband.",
       "Meanwhile Satyavan's father has found that he can see again. Late at night Savitri and Satyavan reach "
       "the hermitage, and Savitri tells the hermits all that happened and the five boons she won from Yama.")]),
    (GANGULI, "Yudhishthira and the Yaksha", "hindu-yaksha", [],
     [("Then king Yudhishthira addressed Nakula saying", "and was struck with wonder.”",
       "Near the end of the twelfth year of their exile, the five Pandava brothers have chased a deer that ran off "
       "with a Brahmana's fire-sticks, and lost it. Tired and thirsty, they sit down under a tree. Arjuna is "
       "also called Vijaya, Vibhatsu and Dhananjaya, and Bhima is Vrikodara. Vaisampayana tells this story to "
       "King Janamejaya."),
      ("Yudhishthira saw his brothers, each possessed of the glory", "gave back that Brahmana his firesticks.",
       None)]),
]


def find(text, phrase, pos=0):
    m = re.compile(r"\s+".join(map(re.escape, phrase.split()))).search(text, pos)
    if not m:
        raise SystemExit(f"not found: {phrase!r}")
    return m.span()


USED = set()


def paragraphs(raw):
    out = []
    for para in re.split(r"\n\s*\n", raw):
        t = re.sub(r"\s+", " ", para).strip()
        if (not t or re.match(r"SECTION [IVXLC]+\.?$", t) or t.startswith("So ends the")
                or re.fullmatch(r"\(.*continued\)", t) or re.match(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]", t)):
            continue
        t = re.sub(r"\[\d+\]|[⁰¹²³⁴⁵⁶⁷⁸⁹]+", "", t)
        t = re.sub(r"_([^_]+)_", r"\1", t)  # the Ramayana's italics
        for a, b in FIXES:
            if a in t:
                t = t.replace(a, b)
                USED.add(a)
        out.append(re.sub(r"\s+([,.;:!?])", r"\1", t))
    return out


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "")).strip("-")


def main(src):
    texts = {key: (Path(src) / f).read_text(encoding="utf-8-sig") for key, f in FILES.items()}
    by_collection = {}
    for col, title, work_id, flags, runs in STORIES:
        blocks, books = [], []
        for first, last, note, *book in runs:
            books.append(book[0] if book else col["id"])
            text = texts[books[-1]]
            start = find(text, first)[0]
            if note:
                blocks.append({"type": "note", "text": note})
            blocks += [{"type": "p", "text": p} for p in paragraphs(text[start:find(text, last, start)[1]])]
        stories = by_collection.setdefault(col["id"], (col, []))[1]
        story = {"id": f"{col['id']}--{slug(title)}", "collectionId": col["id"], "order": len(stories) + 1,
                 "title": title, "origin": None, "excluded": False, "flags": flags, "moral": None,
                 "blocks": blocks, "workId": work_id, "livingTradition": LIVING}
        if books[0] in VOLUMES:
            story["source"], story["firstPublished"] = VOLUMES[books[0]]
        stories.append(finish(story))
    unused = [a for a, _ in FIXES if a not in USED]
    if unused:
        raise SystemExit(f"fixes not used: {unused}")
    index = load_index()
    for col, stories in by_collection.values():
        upsert_collection(index, col, stories)
        for st in stories:
            lv = st["readingLevel"]
            print(f"{st['id']:58} {st['wordCount']:5}w {st['readingMinutes']:3}m {lv['fkGrade']:5} {lv['band']}")
    save_index(index)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "src")
