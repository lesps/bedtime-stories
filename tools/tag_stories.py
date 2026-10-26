#!/usr/bin/env python3
"""Generates public/compendium/tags.json: culture and theme tags for every story.

Cultures come from the collection, refined by each story's `origin` (Lang's Blue Fairy Book mixes
French, Norwegian, German, Arabian Nights and other sources) or set per story in STORY_CULTURE. Themes come from vocabulary scoring
over the full text and title, collection rules, and the OVERRIDES table below, which records
hand-review decisions. Like the content flags, this is an editorial first pass.

Run from the repo root: python3 tools/tag_stories.py
"""
import json
import re
from pathlib import Path

ROOT = Path("public/compendium")

CULTURES = [
    ("greek", "Ancient Greek"),
    ("roman", "Ancient Roman"),
    ("etruscan", "Etruscan"),
    ("norse", "Old Norse"),
    ("german", "German"),
    ("swiss", "Swiss"),
    ("danish", "Danish"),
    ("french", "French"),
    ("norwegian", "Norwegian"),
    ("english", "English"),
    ("scottish", "Scottish"),
    ("irish", "Irish"),
    ("arabian", "Arabian Nights"),
    ("turkish", "Turkish"),
    ("estonian", "Estonian"),
    ("japanese", "Japanese"),
]

THEMES = [
    ("animals", "Animals"),
    ("fables", "Fables with a moral"),
    ("tricksters", "Tricksters & clever escapes"),
    ("kindness", "Kindness rewarded"),
    ("greed-pride", "Greed & pride punished"),
    ("royalty", "Kings, queens & castles"),
    ("magic", "Magic & enchantment"),
    ("monsters", "Giants, witches & monsters"),
    ("family", "Brothers, sisters & family"),
    ("how-things-began", "How things came to be"),
    ("fools", "Fools & silly folk"),
    ("quests", "Journeys & quests"),
    ("wishes", "Wishes & bargains"),
    ("underdogs", "Youngest & underdogs"),
    ("legends", "Faith & legends"),
    ("ghosts", "Ghosts & spirits"),
    ("gentle", "Gentle & cosy"),
    ("gods-heroes", "Gods & heroes"),
]

COLLECTION_CULTURE = {
    "aesop": "greek",
    "grimm": "german",
    "grimm-hunt": "german",
    "busch-max-maurice": "german",
    "andersen": "danish",
    "andersen-27200": "danish",
    "jacobs-english": "english",
    "potter": "english",
    "kipling-justso": "english",
    "japan-ozaki": "japanese",
    "japan-james": "japanese",
    "hawthorne-tanglewood": "greek",
    "myths-greek": "greek",
    "bulfinch-fable": "greek",
    "kingsley-heroes": "greek",
    "hesiod-hymns": "greek",
    "church-virgil": "roman",
    "church-livy": "roman",
    "macaulay-lays": "roman",
    "myths-roman": "roman",
    "greek-sources": "greek",
    "latin-sources": "roman",
    "thorpe-elder-edda": "norse",
    "blackwell-prose-edda": "norse",
    "lang-red": "norse",
    "norse-sources": "norse",
    "myths-norse": "norse",
    "baldwin-siegfried": "german",
    "browning-pied-piper": "german",
    "german-sources": "german",
    "myths-german": "german",
    "baldwin-fifty-famous": "english",
}

# Stories whose culture differs from their collection's: Bulfinch's Roman sections, and the
# Etruscan Tages, known only from Roman writers.
STORY_CULTURE = {
    "latin-sources--tages": "etruscan",
    "myths-roman--tages-the-child-from-the-furrow": "etruscan",
    "bulfinch-fable--the-roman-gods": "roman",
    "bulfinch-fable--vertumnus-and-pomona": "roman",
    "bulfinch-fable--cupid-and-psyche": "roman",
    "bulfinch-fable--the-sibyl": "roman",
    "baldwin-fifty-famous--the-story-of-william-tell": "swiss",
    "baldwin-fifty-famous--arnold-winkelried": "swiss",
}

# Myth collections: every story gets the gods-heroes theme.
MYTH_COLLECTIONS = {
    "hawthorne-tanglewood",
    "kingsley-heroes",
    "bulfinch-fable",
    "myths-greek",
    "hesiod-hymns",
    "church-virgil",
    "church-livy",
    "macaulay-lays",
    "myths-roman",
    "greek-sources",
    "latin-sources",
    "thorpe-elder-edda",
    "blackwell-prose-edda",
    "lang-red",
    "norse-sources",
    "myths-norse",
    "baldwin-siegfried",
}

ORIGIN_CULTURE = [
    (r"perrault|aulnoy|villeneuve|beaumont|cabinet des fees", "french"),
    (r"asbjornsen", "norwegian"),
    (r"grimm", "german"),
    (r"arabian nights", "arabian"),
    (r"scotland", "scottish"),
    (r"asie mineure", "turkish"),
    (r"swift", "irish"),
    (r"chapbook", "english"),
]

# Blue Fairy Book tales whose `origin` is empty, attributed from the tales themselves.
LANG_NO_ORIGIN = {
    "lang-blue--little-red-riding-hood": "french",  # Perrault
    "lang-blue--the-sleeping-beauty-in-the-wood": "french",  # Perrault
    "lang-blue--the-brave-little-tailor": "german",  # Grimm KHM 20
    "lang-blue--the-history-of-whittington": "english",
    "lang-blue--the-terrible-head": "greek",  # Perseus
    "lang-blue--the-water-lily-the-gold-spinners": "estonian",  # Kreutzwald
}

W = r"\b(?:{})\b"
VOCAB = {
    "animals": W.format(
        "fox|foxes|wolf|wolves|bear|bears|cat|cats|kitten|dog|dogs|mouse|mice|bird|birds|rabbit|"
        "rabbits|hare|frog|frogs|lion|lions|goose|geese|duck|ducks|horse|horses|donkey|ass|pig|pigs|"
        "sheep|lamb|goat|goats|crow|raven|eagle|monkey|elephant|kangaroo|whale|tortoise|badger|"
        "squirrel|owl|sparrow|crab|snake|serpent|ant|ants|bee|bees|cock|hen|crane|stag|deer|mole|"
        "rat|rats|toad|jackal|ox|oxen|cow|calf|bull|fish|beaver|weasel|hedgehog|camel|ape|"
        "badger|ermine|tit|lark|dove|pigeon|swan|stork|heron|nightingale|mice|puppy|hound|"
        "tanuki|badgers|crane|carp|jellyfish|turtle|pheasant|spider|grasshopper|beetle|fly|"
        "cockerel|chicken|chickens|kid|bat|leopard|zebra|giraffe|rhinoceros|armadillo|butterfly"
    ),
    "tricksters": W.format(
        "trick|tricks|tricked|cunning|clever|cleverly|outwit|outwitted|sly|slyly|cheat|cheated|"
        "deceive|deceived|fooled|wily|crafty|artful|ruse|shrewd"
    ),
    "kindness": W.format(
        "kind|kindly|kindness|pity|pitied|compassion|grateful|gratitude|reward|rewarded|"
        "good-hearted|gentle|generous|charity|helped"
    ),
    "greed-pride": W.format(
        "greedy|greed|vain|vanity|proud|pride|envy|envious|boast|boasted|boasting|covet|"
        "coveted|avarice|miser|miserly|haughty|arrogant|selfish"
    ),
    "royalty": W.format("king|kings|queen|queens|prince|princes|princess|princesses|palace|throne|castle|court"),
    "magic": W.format(
        "magic|magical|enchant|enchanted|enchantment|enchanter|spell|spells|fairy|fairies|wand|"
        "transformed|bewitched|charm|charmed|sorcery|sorcerer|talisman|ring|invisible"
    ),
    "monsters": W.format(
        "giant|giants|ogre|ogres|ogress|troll|trolls|dragon|dragons|witch|witches|devil|devils|"
        "monster|monsters|demon|demons|oni|goblin|goblins|sorceress|wizard|man-eater|"
        "cannibal|beast|hag"
    ),
    "family": W.format(
        "brother|brothers|sister|sisters|stepmother|step-mother|stepdaughter|stepsister|"
        "stepsisters|twins|siblings|grandmother|grandfather|mother|father"
    ),
    "fools": W.format(
        "fool|fools|foolish|silly|sillies|simpleton|stupid|numskull|noodle|blockhead|dunce|idiot|"
        "dummling|nonsense|absurd|witless|clever elsie"
    ),
    "quests": W.format(
        "journey|journeyed|travel|travelled|traveled|wandered|wandering|seek|sought|quest|"
        "fortune|far away|set out|set off|world"
    ),
    "wishes": W.format(
        "wish|wishes|wished|bargain|bargained|promise|promised|pact|agreement|granted"
    ),
    "underdogs": W.format(
        "youngest|dummling|simpleton|third son|poor lad|cinder|cinders|despised|scorned|ragged"
    ),
    "legends": W.format(
        "god|angel|angels|saint|heaven|heavenly|virgin|christ|jesus|church|apostle|apostles|"
        "paradise|prayed|prayer|prayers|holy|our lady|st\\. peter|saint peter|the lord|buddha|"
        "kwannon|temple|priest|priests|shrine|karma|gods|goddess"
    ),
    "ghosts": W.format(
        "ghost|ghosts|phantom|phantoms|haunted|haunts|apparition|spectre|specter|wraith|"
        "spirit|goblin|demon|shroud"
    ),
}
SCARY = W.format(
    "kill|killed|killing|murder|murdered|blood|bloody|dead|death|died|devour|devoured|eat him|"
    "ate him|cut off|chopped|burned|burnt|hanged|wicked|witch|giant|ogre|devil|troll|dragon|"
    "beheaded|poison|poisoned|slay|slew|slain|corpse|grave"
)

# Per-1000-word density needed to count a theme (title hits count separately).
THRESHOLD = {
    "animals": 12,
    "tricksters": 1.2,
    "kindness": 2.2,
    "greed-pride": 1.6,
    "royalty": 9,
    "magic": 3.0,
    "monsters": 2.5,
    "family": 9,
    "fools": 1.6,
    "quests": 3.2,
    "wishes": 3.5,
    "underdogs": 0.9,
    "legends": 4,
    "ghosts": 1.5,
}

# Hand-review decisions: story id -> {"add": [...], "remove": [...]}.
OVERRIDES: dict[str, dict[str, list[str]]] = {
    # Persephone is carried off and the world starves: not "gentle", whatever the word counts say.
    "hawthorne-tanglewood--the-pomegranate-seeds": {"remove": ["gentle"]},
    "myths-greek--persephone-and-the-pomegranate-seeds": {"remove": ["gentle"]},
    # A death at the heart of the story is not "gentle", even when few violent words appear.
    "myths-greek--phaethon-and-the-sun-chariot": {"remove": ["gentle"]},
    "myths-greek--daedalus-and-icarus": {"remove": ["gentle"]},
    "bulfinch-fable--io": {"remove": ["gentle"]},
    "myths-greek--oedipus-and-the-sphinx": {"remove": ["gentle"]},  # a riddle with deadly stakes
    # Greek gods (part 4): creation myths, and corrections to the word counts.
    "hesiod-hymns--the-theogony": {"add": ["how-things-began", "monsters"]},
    "myths-greek--zeus-and-the-titans": {"add": ["how-things-began", "monsters"], "remove": ["gentle"]},
    "myths-greek--apollo-is-born": {"add": ["how-things-began"]},
    "hesiod-hymns--hymn-to-dionysus": {"add": ["magic", "animals"], "remove": ["quests"]},
    "myths-greek--dionysus-and-the-pirates": {"add": ["magic", "animals"], "remove": ["fools"]},
    # Roman (part 4).
    "bulfinch-fable--the-roman-gods": {"add": ["how-things-began"], "remove": ["ghosts"]},
    "myths-roman--janus-and-the-gods-of-rome": {"add": ["how-things-began"], "remove": ["kindness"]},
    "bulfinch-fable--cupid-and-psyche": {"add": ["magic"]},
    "myths-roman--cupid-and-psyche": {"add": ["magic"], "remove": ["monsters"]},
    "macaulay-lays--horatius": {"remove": ["greed-pride"]},
    "myths-roman--romulus-and-remus": {"add": ["animals", "how-things-began"]},
    "myths-roman--aeneas-and-turnus": {"remove": ["wishes"]},
    # Claude's translations (part 4): Sisyphus is the craftiest of men; Tages begins Etruscan
    # divination, and Cicero's scoffing ("foolish") is not a fools tale.
    "greek-sources--sisyphus-and-tantalus": {"add": ["tricksters"]},
    "myths-greek--sisyphus-and-tantalus": {"add": ["tricksters"]},
    "latin-sources--tages": {"add": ["how-things-began"], "remove": ["tricksters", "fools"]},
    "myths-roman--tages-the-child-from-the-furrow": {"add": ["how-things-began"]},
    # Norse (part 5): creation myths, tricksters, and corrections to the word counts.
    "blackwell-prose-edda--the-beginning-of-the-world": {"add": ["how-things-began"], "remove": ["quests"]},
    "myths-norse--the-beginning-of-the-world": {"add": ["how-things-began"], "remove": ["quests"]},
    "blackwell-prose-edda--the-ash-yggdrasil": {"add": ["how-things-began"]},
    "myths-norse--yggdrasil-and-odin-s-eye": {"add": ["how-things-began"], "remove": ["quests"]},
    "blackwell-prose-edda--night-and-day-sun-and-moon": {"add": ["how-things-began"]},
    "myths-norse--the-sun-and-moon-chased-by-wolves": {"add": ["how-things-began"], "remove": ["quests"]},
    "myths-norse--the-giant-who-built-the-wall": {"add": ["tricksters"], "remove": ["quests"]},
    "blackwell-prose-edda--the-horse-sleipnir": {"add": ["tricksters"], "remove": ["kindness", "wishes"]},
    "norse-sources--sif-s-golden-hair": {"add": ["tricksters", "magic"]},
    "myths-norse--sif-s-golden-hair": {"add": ["tricksters"], "remove": ["gentle"]},
    "thorpe-elder-edda--the-lay-of-alvis": {"add": ["tricksters"], "remove": ["quests"]},
    "myths-norse--thor-and-the-clever-dwarf": {"remove": ["quests", "wishes"]},
    "myths-norse--skadi-chooses-a-husband": {"remove": ["fools"]},
    "blackwell-prose-edda--frey-and-gerda": {"remove": ["wishes"]},
    "myths-norse--the-death-of-baldur": {"remove": ["wishes"]},
    "blackwell-prose-edda--how-thor-went-fishing-for-the-midgard-serpent": {"remove": ["how-things-began"]},
    "blackwell-prose-edda--the-punishment-of-loki": {"add": ["tricksters"]},
    "thorpe-elder-edda--the-vala-s-prophecy": {"add": ["how-things-began"], "remove": ["ghosts"]},
    "myths-norse--what-the-wise-woman-saw": {"add": ["how-things-began"], "remove": ["quests"]},
    # German shelf: the Siegfried retellings are hero legends; Baldwin's chapters get gods-heroes
    # from MYTH_COLLECTIONS.
    "myths-german--siegfried-forges-a-sword": {"add": ["gods-heroes"]},
    "myths-german--siegfried-and-the-horse-greyfell": {"add": ["gods-heroes"]},
    "myths-german--the-curse-of-the-dwarf-s-gold": {"add": ["gods-heroes"]},
    "myths-german--siegfried-and-the-dragon-fafnir": {"add": ["gods-heroes"]},
    "myths-german--siegfried-wakes-brunhild": {"add": ["gods-heroes"]},
    "myths-german--siegfried-and-the-nibelung-treasure": {"add": ["gods-heroes"]},
    "myths-german--the-death-of-siegfried": {"add": ["gods-heroes"]},
    "myths-german--siegfried-helps-king-gunther": {"add": ["gods-heroes"], "remove": ["gentle"]},
    "myths-german--the-treasure-in-the-rhine": {"add": ["gods-heroes", "greed-pride"]},
    "baldwin-siegfried--how-gunther-outwitted-brunhild": {"remove": ["how-things-began"]},
    "baldwin-siegfried--how-they-hunted-in-the-odenwald": {"remove": ["how-things-began"]},
    "baldwin-siegfried--how-the-hoard-was-brought-to-burgundy": {"add": ["greed-pride"], "remove": ["how-things-began"]},
    "german-sources--the-wild-huntsman": {"add": ["ghosts", "greed-pride"], "remove": ["fools"]},
    "myths-german--the-wild-huntsman": {"add": ["ghosts", "greed-pride"], "remove": ["gentle", "quests"]},
    "myths-german--rubezahl-spirit-of-the-mountains": {"remove": ["monsters", "quests"]},
    "browning-pied-piper--the-pied-piper-of-hamelin": {"add": ["magic", "greed-pride"]},
    "myths-german--the-pied-piper-of-hamelin": {"add": ["magic", "greed-pride"], "remove": ["gentle"]},
    "baldwin-fifty-famous--the-story-of-william-tell": {"add": ["underdogs"]},
    "baldwin-fifty-famous--arnold-winkelried": {"add": ["underdogs"], "remove": ["gentle", "greed-pride"]},
    # Battles and monsters are not "gentle", whatever the word counts say.
    "myths-roman--king-evander-and-the-shield-of-aeneas": {"add": ["monsters"], "remove": ["gentle"]},
    "myths-roman--horatius-at-the-bridge": {"remove": ["gentle"]},
    "myths-roman--the-geese-that-saved-rome": {"remove": ["gentle"]},
    "aesop--the-lion-the-bear-and-the-fox": {
        "remove": [
            "ghosts"
        ]
    },
    "grimm--cat-and-mouse-in-partnership": {
        "remove": [
            "legends"
        ]
    },
    "grimm--doctor-knowall": {
        "remove": [
            "legends"
        ]
    },
    "grimm--iron-hans": {
        "remove": [
            "gentle"
        ]
    },
    "grimm-hunt--cat-and-mouse-in-partnership": {
        "remove": [
            "legends"
        ]
    },
    "grimm-hunt--doctor-knowall": {
        "remove": [
            "legends"
        ]
    },
    "grimm-hunt--iron-john": {
        "remove": [
            "gentle"
        ]
    },
    "grimm-hunt--knoist-and-his-three-sons": {
        "remove": [
            "legends"
        ]
    },
    "grimm-hunt--one-eye-two-eyes-and-three-eyes": {
        "remove": [
            "gentle"
        ]
    },
    "grimm-hunt--the-ditmarsch-tale-of-wonders": {
        "remove": [
            "legends"
        ]
    },
    "grimm-hunt--the-fox-and-the-geese": {
        "remove": [
            "legends"
        ]
    },
    "grimm-hunt--the-iron-stove": {
        "remove": [
            "gentle"
        ]
    },
    "grimm-hunt--the-ungrateful-son": {
        "remove": [
            "gentle"
        ]
    },
    "grimm-hunt--wise-folks": {
        "remove": [
            "legends"
        ]
    },
    "japan-james--the-peony-lantern": {
        "add": [
            "ghosts"
        ]
    },
    "lang-blue--east-of-the-sun-and-west-of-the-moon": {
        "remove": [
            "gentle"
        ]
    },
    "lang-blue--rumpelstiltzkin": {
        "remove": [
            "ghosts"
        ]
    }
}


def words(text):
    return len(text.split())


def culture_of(story):
    if story["id"] in STORY_CULTURE:
        return STORY_CULTURE[story["id"]]
    if story["collectionId"] == "lang-blue":
        if story["id"] in LANG_NO_ORIGIN:
            return LANG_NO_ORIGIN[story["id"]]
        origin = (story.get("origin") or "").lower()
        for pattern, culture in ORIGIN_CULTURE:
            if re.search(pattern, origin):
                return culture
        raise SystemExit(f"No culture for {story['id']} (origin {story.get('origin')!r})")
    return COLLECTION_CULTURE[story["collectionId"]]


def themes_of(story):
    text = " ".join(b.get("text", "") for b in story["blocks"]).lower()
    title = story["title"].lower()
    n = max(words(text), 1)
    scores = {}
    found = set()
    for theme, pattern in VOCAB.items():
        density = len(re.findall(pattern, text)) * 1000 / n
        scores[theme] = density / THRESHOLD[theme]
        if density >= THRESHOLD[theme] or re.search(pattern, title):
            found.add(theme)
    col = story["collectionId"]
    if col == "aesop":
        found.add("fables")
    if col == "kipling-justso" or re.match(r"(how|why) ", title):
        found.add("how-things-began")
    if col == "potter":
        found.add("animals")
    if col in MYTH_COLLECTIONS:
        found.add("gods-heroes")
    scary = len(re.findall(SCARY, text)) * 1000 / n
    if scary < 1.0 and "mature-themes" not in story["flags"] and not {"monsters", "ghosts"} & found:
        found.add("gentle")
    o = OVERRIDES.get(story["id"], {})
    found |= set(o.get("add", []))
    found -= set(o.get("remove", []))
    if not found:  # every story gets at least one theme: its strongest signal
        found.add(max(scores, key=scores.get))
    order = [t for t, _ in THEMES]
    return sorted(found, key=order.index)


def main():
    index = json.loads((ROOT / "index.json").read_text())
    stories = {}
    for entry in index["stories"]:
        story = json.loads((ROOT / "stories" / f"{entry['id']}.json").read_text())
        stories[entry["id"]] = {"cultures": [culture_of(story)], "themes": themes_of(story)}
    out = {
        "schemaVersion": 1,
        "cultures": [{"id": i, "label": l} for i, l in CULTURES],
        "themes": [{"id": i, "label": l} for i, l in THEMES],
        "stories": stories,
    }
    # One story per line keeps diffs reviewable without the bulk of full indentation.
    lines = [
        "{",
        '"schemaVersion": 1,',
        f'"cultures": {json.dumps(out["cultures"], ensure_ascii=False)},',
        f'"themes": {json.dumps(out["themes"], ensure_ascii=False)},',
        '"stories": {',
        ",\n".join(f"{json.dumps(k)}: {json.dumps(v)}" for k, v in stories.items()),
        "}",
        "}",
    ]
    (ROOT / "tags.json").write_text("\n".join(lines) + "\n")
    print(f"tagged {len(stories)} stories")


if __name__ == "__main__":
    main()
