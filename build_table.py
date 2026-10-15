"""
Step 1 of the loanword project: build one word-level table from kaikki.

Download the Hungarian JSONL from https://kaikki.org/dictionary/Hungarian/
(the "all entries" JSONL link) and put it next to this script as hungarian.jsonl.

Run:  python build_table.py
Outputs:
  words.csv          one row per word: lemma, label, source_code, template, n_sources
  source_counts.csv  how many words came from each source language code
                     (check this to fix the class mapping below)
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

# Resolve files relative to this script, so it works from any working directory.
HERE = Path(__file__).resolve().parent
INPUT = HERE / "hungarian.jsonl"

if not INPUT.exists():
    sys.exit(
        f"{INPUT} not found. It is 560 MB and not in the repo; download it from "
        "https://kaikki.org/dictionary/Hungarian/ and place it next to this script.\n"
        "If you only want to train, you don't need it: use labeled_words.csv."
    )

BORROW = {"bor", "bor+", "lbor", "slbor", "obor", "ubor"}
INHERIT = {"inh", "inh+"}

# Mapping from Wiktionary language codes to classes (checked against source_counts.csv).
# Anything not listed becomes "other_borrowed" or "other_inherited" and is left out of the
# main experiment. Note: "ohu" (Old Hungarian) is NOT treated as native, because many words
# "inherited from Old Hungarian" are older Turkic loans (gyöngy, dió, sarló, olló).
CLASS_MAP = {
    # Turkic, old (West Old Turkic / Oghur / Volga Bulgar / Chuvash)
    "otk": "turkic", "trk-pro": "turkic", "trk": "turkic", "trk-ogr": "turkic",
    "cv": "turkic", "cv-old": "turkic", "xbo-vol": "turkic",
    # Ottoman Turkish, newer (Luca's comparison class)
    "ota": "ottoman", "tr": "ottoman",
    # Slavic
    "sla": "slavic", "sla-pro": "slavic", "zls": "slavic", "zlw": "slavic",
    "zle": "slavic", "orv": "slavic", "cu": "slavic", "sk": "slavic",
    "cs": "slavic", "cs,sk": "slavic", "sh": "slavic", "sr": "slavic",
    "hr": "slavic", "sl": "slavic", "ru": "slavic", "uk": "slavic",
    "pl": "slavic", "bg": "slavic",
    # German
    "de": "german", "de-AT": "german", "de-AT-vie": "german", "gmh": "german",
    "goh": "german", "bar": "german", "nds": "german", "gem-pro": "german",
    # Inherited (Uralic / Finno-Ugric / Ugric)
    "urj-pro": "inherited", "fiu-pro": "inherited", "urj-ugr-pro": "inherited",
    "ugr-pro": "inherited",
}


def first_source(templates):
    """Return (kind, source_code, template_name, number_of_sources) or None."""
    found = []
    for t in templates or []:
        name = t.get("name")
        args = t.get("args", {})
        if args.get("1") != "hu":
            continue
        if name in BORROW:
            found.append(("borrowed", args.get("2", ""), name))
        elif name in INHERIT:
            found.append(("inherited", args.get("2", ""), name))
    if not found:
        return None
    kind, code, name = found[0]  # first template = immediate source
    return kind, code, name, len({c for _, c, _ in found})


rows = {}
code_counts = Counter()

with open(INPUT, encoding="utf-8") as f:
    for line in f:
        entry = json.loads(line)
        word = entry.get("word", "").strip().lower()
        if not word or " " in word or word in rows:
            continue  # skip multiword entries and duplicate POS entries
        src = first_source(entry.get("etymology_templates"))
        if src is None:
            continue
        kind, code, tname, n = src
        code_counts[(kind, code)] += 1
        label = CLASS_MAP.get(code, "other_" + kind)
        rows[word] = {"lemma": word, "label": label, "source_code": code,
                      "template": tname, "n_sources": n, "dataset": "wiktionary"}

# Merge in the scholarly Turkic list from CLDF (Rona-Tas and Berta 2011).
# If a word is in both, the CLDF label wins because it is the expert source.
added = overridden = 0
try:
    with open(HERE / "cldf_turkic.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            word = r["lemma"]
            if word in rows:
                if rows[word]["label"] != "turkic":
                    # The two sources disagree. Often it is a homograph (kés "knife" vs
                    # kés "be late"), sometimes a real scholarly dispute (szó, szép).
                    # Keep it out of training and testing.
                    overridden += 1
                    rows[word].update(label="disputed", dataset="both")
                else:
                    rows[word].update(dataset="both")
            else:
                rows[word] = {"lemma": word, "label": "turkic", "source_code": "wot",
                              "template": "cldf", "n_sources": 1, "dataset": "cldf"}
                added += 1
    print(f"CLDF: added {added} new Turkic words, marked {overridden} words as disputed")
except FileNotFoundError:
    print("cldf_turkic.csv not found, skipping the CLDF merge")

with open(HERE / "words.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["lemma", "label", "source_code", "template", "n_sources", "dataset"])
    w.writeheader()
    w.writerows(rows.values())

with open(HERE / "source_counts.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["kind", "source_code", "count"])
    for (kind, code), n in code_counts.most_common():
        w.writerow([kind, code, n])

print("Words kept:", len(rows))
for label, n in Counter(r["label"] for r in rows.values()).most_common():
    print(f"  {label:20s} {n}")
