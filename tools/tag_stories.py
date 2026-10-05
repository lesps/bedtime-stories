#!/usr/bin/env python3
"""Generates public/compendium/tags.json: culture and theme tags for every story.

Cultures come from the collection, refined by each story's `origin` (Lang's Blue Fairy Book mixes
French, Norwegian, German, Arabian Nights and other sources). Themes come from vocabulary scoring
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
    ("german", "German"),
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
