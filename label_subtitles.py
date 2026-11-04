"""Lemmatize subtitle CSVs with HuSpaCy and label the lemmas from labeled_words.csv.

Usage: python label_subtitles.py <csv_root> [n_files=500] [out=labeled_subtitle_words.csv]
Takes the first n_files CSVs (sorted) under csv_root, keeps only words whose lemma is in
labeled_words.csv with one of the four classes (no NaN, disputed or other_* labels), and writes one row per distinct lemma with its count.
"""
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
LABELS = HERE / "labeled_words.csv"
CLASSES = {"german", "inherited", "turkic", "slavic"}  # the four project classes


def main(root, n_files=500, out=HERE / "labeled_subtitle_words.csv"):
    root = Path(root)
    if not root.is_dir():
        sys.exit(f"{root} is not a folder")
    files = sorted(root.rglob("*.csv"))[:n_files]
    if not files:
        sys.exit(f"no .csv files under {root}")

    try:
        import spacy
        nlp = spacy.load("hu_core_news_lg", disable=["ner", "parser"])
    except (ImportError, OSError):
        sys.exit("HuSpaCy model missing: pip install -r requirements.txt, then "
                 "python -c 'import huspacy; huspacy.download()'")

    labels = pd.read_csv(LABELS)
    labels = labels[labels["label"].isin(CLASSES)].drop_duplicates("lemma").set_index("lemma")["label"]
    counts = Counter()
    for i, path in enumerate(files, 1):
        texts = pd.read_csv(path, usecols=["text"], dtype=str)["text"].dropna()
        for doc in nlp.pipe(texts, batch_size=200):
            counts.update(t.lemma_.lower() for t in doc
                          if t.is_alpha and not t.is_stop)
        if i % 50 == 0:
            print(f"{i}/{len(files)} files", flush=True)

    df = pd.DataFrame(counts.items(), columns=["lemma", "count"])
    df["label"] = df["lemma"].map(labels)
    labeled = df.dropna(subset=["label"]).sort_values("count", ascending=False)
    labeled.to_csv(out, index=False, encoding="utf-8")
    print(f"{len(files)} files, {len(df)} distinct lemmas, {len(labeled)} labeled")
    print(labeled["label"].value_counts().to_string())


if __name__ == "__main__":
    a = sys.argv
    main(a[1], int(a[2]) if len(a) > 2 else 500, a[3] if len(a) > 3 else HERE / "labeled_subtitle_words.csv")
