"""Reading-level scoring for compendium stories. Standard library only.

`level(blocks)` returns {"fkGrade", "avgSentenceWords", "band"} for a story's text blocks.
Flesch-Kincaid grade uses a vowel-group syllable heuristic (within about half a grade of
dictionary-based counts on prose like this). Bands:

  early     fkGrade <= 3.5 and avgSentenceWords <= 14    read-aloud for ages ~4-7
  middle    fkGrade <= 6.5 and avgSentenceWords <= 20    ages ~7-10
  advanced  anything harder

`needs_simplifying(level, minutes)` is the rule for adding a simplified version: band is
"advanced", or the story runs longer than 20 minutes (a bedtime-length ceiling).
"""
import re

TEXT_TYPES = {"p", "verse", "moral"}
_WORD = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)*")
_SENT_END = re.compile(r"[.!?]+[\"'’”)]*(?:\s|$)")


def syllables(word):
    w = word.lower().replace("’", "'")
    w = re.sub(r"'s$|'d$|'ll$", "", w)
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|[^laeiouy]ed|[^laeiouy]e)$", lambda m: m.group(0)[0], w)
    w = re.sub(r"^y", "", w)
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if re.search(r"[^aeiouy]le$", word.lower()):
        n += 1
    return max(1, n)


def level(blocks):
    text = " ".join(b["text"] for b in blocks if b["type"] in TEXT_TYPES)
    words = _WORD.findall(text)
    if not words:
        return {"fkGrade": 0.0, "avgSentenceWords": 0.0, "band": "early"}
    sentences = max(1, len(_SENT_END.findall(text)))
    wps = len(words) / sentences
    spw = sum(syllables(w) for w in words) / len(words)
    fk = round(0.39 * wps + 11.8 * spw - 15.59, 1)
    wps = round(wps, 1)
    if fk <= 3.5 and wps <= 14:
        band = "early"
    elif fk <= 6.5 and wps <= 20:
        band = "middle"
    else:
        band = "advanced"
    return {"fkGrade": fk, "avgSentenceWords": wps, "band": band}


def needs_simplifying(lvl, minutes):
    return lvl["band"] == "advanced" or minutes > 20
