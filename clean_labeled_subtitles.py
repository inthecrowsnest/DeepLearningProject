"""Clean the output of label_subtitles.py: drop function words, proper names and
lemmatizer junk that happened to match a dictionary entry.

Usage: python clean_labeled_subtitles.py <in.csv> [out=labeled_subtitle_words.csv]
"""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent

# pronouns, numerals and interjections: not content words
FUNCTION = {"ő", "ó", "ez", "az", "én", "mi", "te", "ti", "ön", "két", "jé", "al", "ál"}
# proper names (people and places)
NAMES = {"müller", "tóth", "gyula", "ada", "semmelweis", "beethoven", "konrád", "léna",
         "moszkva", "visegrád", "frankfurt", "kazahsztán"}
# not real lemmas: inflected forms, English words, stray fragments
JUNK = {"várta", "sing", "os", "im", "ör", "basz", "bű", "eng", "alt"}


def main(src, out=HERE / "labeled_subtitle_words.csv"):
    df = pd.read_csv(src)
    drop = FUNCTION | NAMES | JUNK
    clean = df[~df["lemma"].isin(drop)]
    clean.to_csv(out, index=False, encoding="utf-8")
    print(f"{len(df)} -> {len(clean)} words (dropped {len(df) - len(clean)})")
    print(clean["label"].value_counts().to_string())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else HERE / "labeled_subtitle_words.csv")
