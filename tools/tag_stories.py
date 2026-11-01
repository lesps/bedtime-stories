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
    ("welsh", "Welsh"),
    ("manx", "Manx"),
    ("breton", "Breton"),
    ("arthurian", "Arthurian"),
    ("arabian", "Arabian Nights"),
    ("turkish", "Turkish"),
    ("finnish", "Finnish"),
    ("estonian", "Estonian"),
    ("sami", "Sámi"),
    ("lithuanian", "Lithuanian"),
    ("russian", "Russian"),
    ("polish", "Polish"),
    ("czech", "Czech"),
    ("serbian", "Serbian"),
    ("romanian", "Romanian"),
    ("albanian", "Albanian"),
    ("hungarian", "Hungarian"),
    ("circassian", "Circassian"),
    ("georgian", "Georgian"),
    ("basque", "Basque"),
    ("egyptian", "Ancient Egyptian"),
    ("mesopotamian", "Mesopotamian"),
    ("hittite", "Hittite and Hurrian"),
    ("canaanite", "Canaanite"),
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
    "bulfinch-chivalry": "english",
    "pyle-robin-hood": "english",
    "marshall-english-literature": "english",
    "quiller-couch-cornwall": "english",
    "myths-english": "english",
    "joyce-celtic-romances": "irish",
    "stephens-irish-fairy-tales": "irish",
    "hull-cuchulain": "irish",
    "yeats-irish-folk": "irish",
    "myths-irish": "irish",
    "guest-mabinogion": "welsh",
    "jacobs-celtic": "welsh",
    "myths-welsh": "welsh",
    "grierson-scottish": "scottish",
    "morrison-manx": "manx",
    "myths-celtic": "scottish",
    # Only the Arthurian tales are taken from Lang's Book of Romance and Geoffrey so far.
    "lang-romance": "arthurian",
    "geoffrey-british-history": "arthurian",
    "myths-arthurian": "arthurian",
    "eivind-finnish": "finnish",
    "kirby-esthonia": "estonian",
    "myths-finnic": "finnish",
    "myths-baltic": "lithuanian",
    "ralston-russian": "russian",
    "curtin-russian": "russian",
    "magnus-russian": "russian",
    "myths-russian": "russian",
    "lutzow-prague": "czech",
    "petrovitch-serbian": "serbian",
    "myths-west-slavic": "polish",
    "myths-balkan": "serbian",
    "hungarian-sources": "hungarian",
    "myths-hungarian": "hungarian",
    "myths-caucasus": "circassian",
    "webster-basque": "basque",
    "myths-basque": "basque",
    "budge-legends": "egyptian",
    "budge-book-of-the-dead": "egyptian",
    "spence-egypt": "egyptian",
    "petrie-egyptian": "egyptian",
    "macaulay-herodotus": "egyptian",
    "myths-egyptian": "egyptian",
    "budge-babylonian-creation": "mesopotamian",
    "budge-gilgamish": "mesopotamian",
    "mackenzie-babylonia": "mesopotamian",
    "jastrow-babylonia": "mesopotamian",
    "myths-mesopotamian": "mesopotamian",
    "myths-hittite-canaanite": "hittite",
    "smith-achilles-tatius": "canaanite",
}

# Stories whose culture differs from their collection's: Bulfinch's Roman sections, the
# Etruscan Tages, known only from Roman writers, the Manx and Breton retellings in `myths-celtic`,
# the Estonian and Sámi ones in `myths-finnic`, the Czech one in `myths-west-slavic`, and the
# Romanian and Albanian ones in `myths-balkan`, and the Georgian one in `myths-caucasus`.
STORY_CULTURE = {
    "myths-hittite-canaanite--baal-and-the-sea": "canaanite",
    "myths-hittite-canaanite--the-dog-who-found-the-purple-dye": "canaanite",
    "latin-sources--tages": "etruscan",
    "myths-roman--tages-the-child-from-the-furrow": "etruscan",
    "bulfinch-fable--the-roman-gods": "roman",
    "bulfinch-fable--vertumnus-and-pomona": "roman",
    "bulfinch-fable--cupid-and-psyche": "roman",
    "bulfinch-fable--the-sibyl": "roman",
    "baldwin-fifty-famous--the-story-of-william-tell": "swiss",
    "baldwin-fifty-famous--arnold-winkelried": "swiss",
    "latin-sources--saint-george-and-the-dragon": "english",
    "thorpe-elder-edda--the-lay-of-volund": "norse",
    "myths-celtic--the-making-of-mann": "manx",
    "myths-celtic--saint-patrick-and-manannans-mist": "manx",
    "myths-celtic--the-drowned-city-of-ys": "breton",
    "myths-finnic--linda-and-the-hill-of-tallinn": "estonian",
    "myths-west-slavic--libuse-and-the-founding-of-prague": "czech",
    "myths-balkan--master-manole": "romanian",
    "myths-balkan--mujo-and-the-mountain-fairies": "albanian",
    "myths-caucasus--amirani": "georgian",
    "myths-finnic--how-kalevipoeg-became-king": "estonian",
    "myths-finnic--kalevipoeg-at-the-gates": "estonian",
    "myths-finnic--the-son-of-the-sun": "sami",
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
    "bulfinch-chivalry",
    "pyle-robin-hood",
    "marshall-english-literature",
    "quiller-couch-cornwall",
    "joyce-celtic-romances",
    "stephens-irish-fairy-tales",
    "hull-cuchulain",
    "myths-irish",
    "guest-mabinogion",
    "myths-welsh",
    "lang-romance",
    "geoffrey-british-history",
    "myths-arthurian",
    "eivind-finnish",
    "kirby-esthonia",
    "myths-finnic",
    "myths-baltic",
    "lutzow-prague",
    "petrovitch-serbian",
    "myths-west-slavic",
    "myths-balkan",
    "hungarian-sources",
    "myths-hungarian",
    "myths-caucasus",
    "webster-basque",
    "myths-basque",
    "budge-legends",
    "budge-book-of-the-dead",
    "spence-egypt",
    "myths-egyptian",
    "budge-babylonian-creation",
    "budge-gilgamish",
    "mackenzie-babylonia",
    "jastrow-babylonia",
    "myths-mesopotamian",
    "myths-hittite-canaanite",
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
    "myths-greek--odysseus-comes-home": {"add": ["royalty"]},  # king and queen of Ithaca; sits at the threshold
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
    # English shelf. Retellings of hero legends get gods-heroes by hand (the originals' collections
    # are in MYTH_COLLECTIONS); the Green Children are not a hero legend.
    "myths-english--brutus-comes-to-albion": {"add": ["gods-heroes", "how-things-began"]},
    "bulfinch-chivalry--brutus-and-the-founding-of-britain": {"add": ["how-things-began"]},
    "myths-english--corineus-and-the-giant-gogmagog": {"add": ["gods-heroes", "how-things-began"]},
    "myths-english--king-leir-and-his-three-daughters": {"add": ["gods-heroes"], "remove": ["quests"]},
    "bulfinch-chivalry--king-leir-and-his-daughters": {"remove": ["quests"]},
    "thorpe-elder-edda--the-lay-of-volund": {"add": ["magic", "greed-pride"]},
    "myths-english--wayland-the-smith": {"add": ["gods-heroes", "magic", "greed-pride"], "remove": ["gentle"]},
    "myths-english--the-green-children-of-woolpit": {"add": ["magic", "family"], "remove": ["animals"]},
    "pyle-robin-hood--how-robin-hood-came-to-be-an-outlaw": {"add": ["underdogs"], "remove": ["how-things-began"]},
    "myths-english--how-robin-hood-became-an-outlaw": {"add": ["gods-heroes", "underdogs"], "remove": ["how-things-began"]},
    "pyle-robin-hood--the-shooting-match-at-nottingham-town": {"add": ["tricksters"]},
    "myths-english--robin-hood-and-the-golden-arrow": {"add": ["gods-heroes", "tricksters"]},
    "pyle-robin-hood--robin-hood-and-allan-a-dale": {"add": ["kindness"]},
    "myths-english--robin-hood-and-allan-a-dale": {"add": ["gods-heroes"], "remove": ["legends"]},
    "pyle-robin-hood--robin-hood-seeks-the-curtal-friar": {"add": ["tricksters"], "remove": ["gentle"]},
    "myths-english--robin-hood-and-friar-tuck": {"add": ["gods-heroes"], "remove": ["gentle"]},
    "pyle-robin-hood--robin-hood-compasses-a-marriage": {"add": ["kindness", "tricksters"], "remove": ["legends"]},
    "myths-english--robin-hood-and-the-wedding": {"add": ["gods-heroes", "kindness", "tricksters"], "remove": ["legends"]},
    "pyle-robin-hood--king-richard-comes-to-sherwood-forest": {"add": ["tricksters"]},
    "myths-english--robin-hood-and-king-richard": {"add": ["gods-heroes", "tricksters"]},
    "pyle-robin-hood--epilogue-the-death-of-robin-hood": {"add": ["kindness"], "remove": ["quests"]},
    "myths-english--the-last-arrow-of-robin-hood": {"add": ["gods-heroes", "kindness"]},
    "myths-english--saint-george-and-the-dragon": {"add": ["gods-heroes"]},
    # Irish shelf. Carleton's Fin McCool is a folk tale, so its collection is not in
    # MYTH_COLLECTIONS, but he is still the hero Fionn; Saint Brendan is a saint's legend.
    "joyce-celtic-romances--the-fate-of-the-children-of-lir": {"add": ["family"]},
    "myths-irish--the-children-of-lir": {"add": ["family"], "remove": ["royalty"]},
    "joyce-celtic-romances--the-fate-of-the-children-of-turenn": {"add": ["magic"]},
    "myths-irish--the-sons-of-turenn": {"add": ["quests"]},
    "joyce-celtic-romances--the-voyage-of-maildun": {"add": ["quests", "magic", "monsters"]},
    "myths-irish--the-voyage-of-maildun": {"add": ["quests", "magic"], "remove": ["family"]},
    "joyce-celtic-romances--the-pursuit-of-dermat-and-grania": {"add": ["magic", "monsters"]},
    "joyce-celtic-romances--oisin-in-tirnanoge": {"add": ["magic"], "remove": ["kindness"]},
    "myths-irish--oisin-in-the-land-of-youth": {"add": ["magic", "quests"]},
    "joyce-celtic-romances--the-fate-of-the-sons-of-usna": {"add": ["royalty"]},
    "myths-irish--deirdre": {"remove": ["kindness"]},
    "stephens-irish-fairy-tales--the-story-of-tuan-mac-cairill": {"add": ["magic", "animals", "how-things-began"]},
    "myths-irish--tuan-the-oldest-man-in-ireland": {"add": ["magic", "animals", "how-things-began", "legends"]},
    "stephens-irish-fairy-tales--the-boyhood-of-fionn": {"add": ["magic", "quests", "monsters"]},
    "myths-irish--fionn-and-the-salmon-of-knowledge": {"add": ["magic", "monsters"]},
    "hull-cuchulain--how-cuchulain-got-his-name": {"add": ["animals"], "remove": ["royalty"]},
    "myths-irish--how-cuchulain-got-his-name": {"remove": ["royalty", "quests"]},
    "hull-cuchulain--the-cattle-raid-of-cooley": {"add": ["animals", "greed-pride"]},
    "yeats-irish-folk--a-legend-of-knockmany": {"add": ["tricksters", "gods-heroes"]},
    "myths-irish--fin-mccool-and-the-giant": {"add": ["tricksters"], "remove": ["kindness"]},
    "myths-irish--lugh-of-all-the-skills": {"add": ["magic"], "remove": ["gentle"]},
    "myths-irish--boann-and-the-river-boyne": {"add": ["how-things-began"], "remove": ["gentle"]},
    "myths-irish--the-voyage-of-bran": {"add": ["quests", "magic"]},
    "myths-irish--cuchulain-and-the-beheading-game": {"add": ["wishes"]},
    "myths-irish--saint-brendans-voyage": {"add": ["quests", "animals"], "remove": ["gods-heroes"]},
    # Welsh shelf. Jacobs's two tales are folk legends, so `jacobs-celtic` is not in
    # MYTH_COLLECTIONS, and their retellings drop gods-heroes, as does the drowned land.
    "guest-mabinogion--pwyll-prince-of-dyved": {"add": ["magic", "tricksters"]},
    "myths-welsh--pwyll-and-rhiannon": {"add": ["royalty", "magic", "tricksters"]},
    "guest-mabinogion--branwen-the-daughter-of-llyr": {"add": ["royalty", "magic", "family"]},
    "myths-welsh--branwen-and-bran-the-blessed": {"add": ["royalty", "magic", "family"]},
    "guest-mabinogion--manawyddan-the-son-of-llyr": {"add": ["magic", "tricksters"], "remove": ["legends"]},
    "myths-welsh--manawydan-and-the-enchanted-land": {"add": ["tricksters", "animals"]},
    "guest-mabinogion--math-the-son-of-mathonwy": {"add": ["animals", "how-things-began"], "remove": ["quests"]},
    "myths-welsh--lleu-and-the-woman-made-of-flowers": {"add": ["animals", "tricksters", "how-things-began"]},
    "guest-mabinogion--the-story-of-lludd-and-llevelys": {"add": ["magic"]},
    "myths-welsh--lludd-and-llefelys": {"add": ["magic"], "remove": ["ghosts"]},
    "guest-mabinogion--taliesin": {"add": ["magic", "animals", "tricksters"]},
    "myths-welsh--the-birth-of-taliesin": {"add": ["animals", "tricksters"]},
    "guest-mabinogion--kilhwch-and-olwen": {"add": ["monsters", "magic", "animals"]},
    "myths-welsh--culhwch-and-olwen": {"add": ["quests", "animals"]},
    "jacobs-celtic--the-shepherd-of-myddvai": {"add": ["magic", "wishes"]},
    "myths-welsh--the-lady-of-the-lake": {"add": ["magic", "wishes"], "remove": ["gods-heroes"]},
    "jacobs-celtic--beth-gellert": {"add": ["legends"], "remove": ["greed-pride"]},
    "myths-welsh--gelert-the-faithful-hound": {"add": ["legends"], "remove": ["magic", "gods-heroes"]},
    "myths-welsh--the-drowned-land": {"add": ["legends", "how-things-began"], "remove": ["gentle", "gods-heroes"]},
    # Scottish, Manx and Breton shelf. Grierson's and Morrison's books are fairy books, so neither
    # they nor `myths-celtic` are in MYTH_COLLECTIONS; the Cailleach, Assipattle, Finn and
    # Manannan get gods-heroes by hand.
    "grierson-scottish--thomas-the-rhymer": {"add": ["magic", "legends"]},
    "myths-celtic--thomas-the-rhymer": {"add": ["magic", "legends"]},
    "grierson-scottish--the-seal-catcher-and-the-merman": {"add": ["animals", "kindness", "wishes"]},
    "myths-celtic--the-seal-catcher-and-the-merman": {"add": ["animals", "kindness", "wishes"], "remove": ["gentle"]},
    "grierson-scottish--assipattle-and-the-mester-stoorworm": {"add": ["gods-heroes", "underdogs", "monsters", "tricksters", "how-things-began"]},
    "myths-celtic--assipattle-and-the-stoorworm": {"add": ["gods-heroes", "underdogs", "monsters", "tricksters", "how-things-began"]},
    "morrison-manx--the-making-of-mann": {"add": ["gods-heroes", "monsters", "how-things-began"], "remove": ["tricksters"]},
    "myths-celtic--the-making-of-mann": {"add": ["gods-heroes", "monsters", "how-things-began"], "remove": ["tricksters"]},
    "morrison-manx--the-coming-of-saint-patrick": {"add": ["gods-heroes", "magic", "legends"]},
    "myths-celtic--saint-patrick-and-manannans-mist": {"add": ["gods-heroes", "magic", "legends"]},
    "myths-celtic--the-cailleach-queen-of-winter": {"add": ["gods-heroes", "magic", "how-things-began"], "remove": ["royalty"]},
    "myths-celtic--the-drowned-city-of-ys": {"add": ["legends", "royalty", "greed-pride"], "remove": ["gentle"]},
    # Arthurian shelf.
    "lang-romance--the-drawing-of-the-sword": {"add": ["royalty", "magic", "underdogs"]},
    "myths-arthurian--the-sword-in-the-stone": {"add": ["magic", "underdogs"], "remove": ["legends"]},
    "lang-romance--the-sword-excalibur": {"add": ["magic", "wishes"]},
    "myths-arthurian--excalibur-and-the-lady-of-the-lake": {"add": ["magic", "royalty"]},
    "myths-arthurian--the-round-table": {"add": ["how-things-began"]},
    "lang-romance--what-beaumains-asked-of-the-king": {"add": ["underdogs", "quests"]},
    "myths-arthurian--gareth-the-kitchen-knight": {"add": ["underdogs", "quests"]},
    "lang-romance--the-quest-of-the-holy-graal": {"add": ["magic"]},
    "myths-arthurian--galahad-and-the-holy-grail": {"add": ["magic"], "remove": ["underdogs"]},
    "lang-romance--the-end-of-it-all": {"add": ["magic"]},
    "myths-arthurian--the-passing-of-arthur": {"add": ["magic"], "remove": ["tricksters"]},
    "geoffrey-british-history--merlin-and-vortigern-s-tower": {"add": ["magic"], "remove": ["ghosts"]},
    "myths-arthurian--merlin-and-the-two-dragons": {"add": ["magic"], "remove": ["family"]},
    "myths-arthurian--gawain-and-the-green-knight": {"add": ["magic", "monsters"], "remove": ["legends"]},
    # Finnish and Estonian shelf.
    "eivind-finnish--the-world-s-creation": {"add": ["how-things-began"], "remove": ["quests"]},
    "myths-finnic--how-the-world-was-made": {"remove": ["quests"]},
    "eivind-finnish--wainamoinen-and-youkahainen": {"remove": ["gentle"]},
    "myths-finnic--the-singing-contest": {"remove": ["gentle", "family", "quests"]},
    "eivind-finnish--ilmarinen-forges-the-sampo": {"add": ["tricksters"]},
    "myths-finnic--the-forging-of-the-sampo": {"add": ["tricksters", "wishes"]},
    "eivind-finnish--lemminkainen-s-death-and-restoration": {"add": ["family", "quests"]},
    "myths-finnic--lemminkainen-and-his-mother": {"remove": ["legends"]},
    "eivind-finnish--the-birth-of-the-kantele": {"add": ["animals", "how-things-began"]},
    "myths-finnic--the-first-kantele": {"add": ["animals", "how-things-began"], "remove": ["gentle"]},
    "eivind-finnish--the-capture-of-the-sampo": {"add": ["quests", "monsters"]},
    "myths-finnic--the-capture-of-the-sampo": {"add": ["quests"], "remove": ["legends"]},
    "eivind-finnish--louhi-steals-the-sun-and-moon": {"add": ["tricksters"]},
    "myths-finnic--the-stolen-sun-and-moon": {"add": ["tricksters", "quests"], "remove": ["legends"]},
    "kirby-esthonia--the-death-of-kalev": {"add": ["family", "how-things-began"], "remove": ["quests", "underdogs"]},
    "myths-finnic--linda-and-the-hill-of-tallinn": {"add": ["family", "how-things-began"], "remove": ["quests", "underdogs"]},
    "kirby-esthonia--the-contest-and-parting-of-the-brothers": {"add": ["royalty", "how-things-began"], "remove": ["quests"]},
    "myths-finnic--how-kalevipoeg-became-king": {"remove": ["legends", "quests"]},
    "kirby-esthonia--armageddon": {"add": ["magic", "monsters"]},
    # Sámi and Baltic retellings (no originals in the app). Eglė is a folk tale, not a myth.
    "myths-finnic--the-son-of-the-sun": {"add": ["magic", "quests", "how-things-began"]},
    "myths-baltic--egle-queen-of-serpents": {"add": ["magic", "family", "animals", "how-things-began"], "remove": ["underdogs", "gods-heroes"]},
    "myths-baltic--jurate-and-kastytis": {"add": ["magic", "how-things-began"], "remove": ["gentle"]},
    "myths-baltic--the-sun-and-the-moon": {"add": ["how-things-began", "family"], "remove": ["quests"]},
    "myths-baltic--perkunas-and-the-devil": {"add": ["how-things-began", "tricksters"]},
    # Russian tales and their retellings
    "ralston-russian--vasilissa-the-fair": {"add": ["magic", "monsters", "underdogs"]},
    "ralston-russian--frost": {"add": ["kindness", "magic", "greed-pride"], "remove": ["fools"]},
    "curtin-russian--ivan-tsarevich-the-fire-bird-and-the-gray-wolf": {"add": ["magic", "quests", "royalty", "underdogs", "family"]},
    "curtin-russian--koshchei-without-death": {"add": ["magic", "monsters", "quests", "royalty", "animals"], "remove": ["family", "legends"]},
    "magnus-russian--marya-moryevna": {"add": ["magic", "monsters", "family", "animals", "royalty"]},
    "magnus-russian--ilya-muromets-and-the-nightingale-robber": {"add": ["gods-heroes", "monsters"], "remove": ["animals", "family"]},
    "myths-russian--the-firebird-and-the-grey-wolf": {"add": ["magic", "royalty", "underdogs", "family"]},
    "myths-russian--koshchei-the-deathless": {"add": ["magic", "monsters", "royalty"], "remove": ["fools"]},
    "myths-russian--marya-morevna": {"add": ["magic", "monsters", "family", "royalty"]},
    "myths-russian--ilya-muromets-and-the-nightingale-robber": {"add": ["gods-heroes", "monsters", "legends"], "remove": ["animals", "gentle"]},
    "myths-russian--dobrynya-and-the-dragon": {"add": ["gods-heroes", "quests", "royalty"]},
    "myths-russian--sadko": {"add": ["gods-heroes", "magic", "wishes", "quests"]},
    "myths-russian--the-snow-maiden": {"add": ["magic", "family"], "remove": ["tricksters", "kindness"]},
    # West Slavic and Balkan legends
    "lutzow-prague--libussa-and-the-founding-of-prague": {"add": ["how-things-began", "royalty"]},
    "myths-west-slavic--libuse-and-the-founding-of-prague": {"add": ["how-things-began", "royalty", "gentle"], "remove": ["quests"]},
    "myths-west-slavic--lech-czech-and-rus": {"add": ["how-things-began", "family"]},
    "myths-west-slavic--the-wawel-dragon": {"add": ["tricksters", "underdogs"], "remove": ["kindness"]},
    "petrovitch-serbian--prince-marko-and-sharatz": {"add": ["magic"]},
    "petrovitch-serbian--prince-marko-tells-whose-the-empire-shall-be": {"add": ["family"]},
    "petrovitch-serbian--prince-marko-and-the-veela": {"add": ["magic"], "remove": ["gentle"]},
    "myths-balkan--master-manole": {"add": ["how-things-began"], "remove": ["gods-heroes"]},
    # Hungarian, Caucasus and Basque legends
    "hungarian-sources--the-wondrous-stag": {"add": ["quests", "family", "how-things-began"]},
    "myths-hungarian--hunor-and-magor": {"add": ["how-things-began"]},
    "myths-hungarian--emese-and-the-turul": {"add": ["how-things-began", "magic"]},
    "myths-caucasus--sosruko-the-child-of-the-stone": {"add": ["magic"]},
    "myths-basque--martin-txiki-and-the-basajauns": {"add": ["how-things-began", "underdogs"]},
    "myths-basque--mari-of-anboto": {"add": ["magic", "ghosts", "kindness"], "remove": ["gentle"]},
    # Egyptian myths
    "budge-legends--the-creation": {"add": ["how-things-began", "magic"]},
    "myths-egyptian--khepera-rises-from-the-waters": {"add": ["how-things-began", "magic", "family"], "remove": ["kindness"]},
    "budge-legends--the-destruction-of-mankind": {"add": ["how-things-began", "royalty", "monsters"]},
    "myths-egyptian--sekhmet-and-the-red-beer": {"add": ["how-things-began", "royalty", "monsters", "tricksters"]},
    "budge-legends--the-legend-of-ra-and-isis": {"add": ["magic", "tricksters", "royalty", "animals"]},
    "myths-egyptian--isis-and-the-secret-name-of-ra": {"add": ["royalty"]},
    "budge-legends--isis-and-horus-in-the-marshes": {"add": ["animals", "kindness", "greed-pride", "magic"]},
    "myths-egyptian--isis-and-the-seven-scorpions": {"add": ["animals", "kindness", "greed-pride"]},
    "budge-legends--the-five-added-days": {"add": ["how-things-began", "tricksters", "family"], "remove": ["quests"]},
    "myths-egyptian--thoth-and-the-five-extra-days": {"add": ["how-things-began", "tricksters", "family"], "remove": ["quests"]},
    "budge-legends--the-history-of-isis-and-osiris": {"add": ["royalty", "family", "magic", "quests"]},
    "myths-egyptian--osiris-and-the-wonderful-chest": {"add": ["family", "magic"], "remove": ["gentle"]},
    "budge-book-of-the-dead--the-weighing-of-the-heart": {"add": ["ghosts", "monsters"]},
    "myths-egyptian--the-weighing-of-the-heart": {"add": ["ghosts"], "remove": ["tricksters"]},
    "spence-egypt--the-journey-of-the-sun-through-the-night": {"add": ["monsters", "magic"]},
    "myths-egyptian--the-sun-boat-and-the-serpent-apep": {"add": ["monsters", "magic"], "remove": ["animals"]},
    "spence-egypt--khnemu-and-the-source-of-the-nile": {"add": ["how-things-began", "magic"]},
    "myths-egyptian--khnum-and-the-river-nile": {"add": ["how-things-began", "magic"]},
    "petrie-egyptian--the-shipwrecked-sailor": {"add": ["animals", "magic", "quests", "kindness"]},
    "myths-egyptian--the-shipwrecked-sailor": {"add": ["animals", "magic", "quests", "kindness"]},
    "macaulay-herodotus--the-phoenix": {"add": ["magic"]},
    "myths-egyptian--the-phoenix": {"add": ["animals", "magic"], "remove": ["quests"]},
    # Mesopotamian myths
    "budge-babylonian-creation--the-seven-tablets-of-creation": {"add": ["how-things-began", "magic"]},
    "myths-mesopotamian--marduk-and-tiamat": {"add": ["how-things-began"], "remove": ["tricksters"]},
    "myths-mesopotamian--how-people-were-made-from-clay": {"add": ["magic"], "remove": ["tricksters", "ghosts"]},
    "jastrow-babylonia--the-legend-of-adapa": {"add": ["tricksters", "magic"]},
    "myths-mesopotamian--adapa-and-the-south-wind": {"add": ["magic"]},
    "mackenzie-babylonia--etana-and-the-eagle": {"add": ["quests", "magic"], "remove": ["gentle"]},
    "myths-mesopotamian--etana-and-the-eagle": {"add": ["quests", "magic"], "remove": ["gentle"]},
    "myths-mesopotamian--inanna-and-the-gifts-of-wisdom": {"add": ["magic", "how-things-began", "tricksters"]},
    "mackenzie-babylonia--the-descent-of-ishtar": {"add": ["ghosts", "quests", "magic"]},
    "myths-mesopotamian--ishtar-goes-down-to-the-land-of-the-dead": {"add": ["ghosts", "quests", "greed-pride"]},
    "myths-mesopotamian--lugalbanda-and-the-anzu-bird": {"add": ["quests", "kindness", "wishes", "magic"]},
    "budge-gilgamish--gilgamish-and-enkidu": {"add": ["royalty", "animals"]},
    "myths-mesopotamian--gilgamesh-and-enkidu": {"add": ["royalty", "animals"], "remove": ["gentle"]},
    "budge-gilgamish--the-forest-of-khumbaba": {"add": ["monsters", "quests", "ghosts"], "remove": ["gentle"]},
    "myths-mesopotamian--gilgamesh-and-the-cedar-forest": {"add": ["monsters", "ghosts"]},
    "budge-gilgamish--ishtar-and-the-bull-of-heaven": {"add": ["monsters", "greed-pride"]},
    "myths-mesopotamian--gilgamesh-and-the-bull-of-heaven": {"add": ["monsters", "greed-pride"]},
    "budge-gilgamish--the-death-of-enkidu": {"remove": ["kindness"]},
    "myths-mesopotamian--gilgamesh-loses-his-friend": {"remove": ["animals", "kindness"]},
    "budge-gilgamish--the-journey-to-uta-napishtim": {"add": ["monsters"], "remove": ["underdogs"]},
    "myths-mesopotamian--gilgamesh-goes-to-the-end-of-the-world": {"add": ["monsters"], "remove": ["underdogs"]},
    "budge-gilgamish--the-deluge-and-the-plant-of-youth": {"add": ["quests", "animals", "magic"]},
    "myths-mesopotamian--the-great-flood-and-the-plant-of-youth": {"add": ["quests", "animals", "magic"]},
    # Hittite, Hurrian and Canaanite myths
    "myths-hittite-canaanite--telipinu-the-god-who-went-away": {"add": ["quests", "magic"]},
    "myths-hittite-canaanite--the-storm-god-and-the-dragon-illuyanka": {"add": ["tricksters"]},
    "myths-hittite-canaanite--ullikummi-the-stone-giant": {"add": ["magic", "royalty"]},
    "myths-hittite-canaanite--baal-and-the-sea": {"add": ["magic"], "remove": ["animals", "tricksters", "gentle"]},
    "smith-achilles-tatius--the-shepherds-dog-and-the-purple-dye": {"add": ["how-things-began"], "remove": ["kindness"]},
    "myths-hittite-canaanite--the-dog-who-found-the-purple-dye": {"add": ["how-things-began"], "remove": ["gods-heroes"]},
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
