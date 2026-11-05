# -*- coding: utf-8 -*-
"""data_processing_m1 — streams Hungarian OpenSubtitles straight from hu.zip,
tokenizes + lemmatizes with HuSpaCy, labels via labeled_words.csv (four classes), and stops once
TARGET labeled rows are collected.

Run locally from the project folder:   python data_processing_m1.py
"""

# ── 1: install HuSpaCy model (skip if already installed) ──
import importlib.util, subprocess, sys, urllib.request, zipfile, re, os

if importlib.util.find_spec("hu_core_news_lg") is None:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "spacy", "huspacy"], check=True)
    url = "https://huggingface.co/huspacy/hu_core_news_lg/resolve/main/hu_core_news_lg-any-py3-none-any.whl"
    tmp = "/tmp/hu_core_news_lg.whl"
    urllib.request.urlretrieve(url, tmp)
    with zipfile.ZipFile(tmp) as z:
        meta = next(n for n in z.namelist() if n.endswith(".dist-info/METADATA"))
        version = re.search(r"^Version: (.+)$", z.read(meta).decode(), re.M).group(1).strip()
    fixed = f"/tmp/hu_core_news_lg-{version}-py3-none-any.whl"
    os.rename(tmp, fixed)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", fixed], check=True)
    print("Model installed — run the script again to continue.")
    sys.exit(0)
else:
    print("hu_core_news_lg already installed.")

# ── 2: download the subtitle corpus (once, ~5 GB, stays zipped) ──
ZIP_PATH = "hu.zip"  # saved next to this script
ZIP_URL = "https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2024/raw/hu.zip"

def _progress(blocks, block_size, total):
    done = blocks * block_size
    if total > 0 and blocks % 2000 == 0:
        print(f"\r  downloading hu.zip: {done / total:5.1%} of {total / 1e9:.1f} GB", end="", flush=True)

if not os.path.exists(ZIP_PATH):
    urllib.request.urlretrieve(ZIP_URL, ZIP_PATH + ".part", _progress)
    os.rename(ZIP_PATH + ".part", ZIP_PATH)
    print()
print(f"{ZIP_PATH}: {os.path.getsize(ZIP_PATH) / 1e9:.1f} GB")

# ── 3: settings + label lookup ──
import gzip, random
import xml.etree.ElementTree as ET
import pandas as pd
import spacy

from collections import Counter

TARGET = 1000            # stop after this many labeled rows
UNIQUE_LEMMAS = True     # True = each lemma appears once; False = keep repeats
LABELS_CSV = "labeled_words.csv"   # has the 40 disputed words marked
CLASSES = {"inherited", "german", "slavic", "turkic"}   # the four project classes
OUT_CSV = "tokens_dataset_updated.csv"

labels = pd.read_csv(LABELS_CSV)
print(LABELS_CSV, "columns:", list(labels.columns))
# Column names in labeled_words.csv:
LEMMA_COL, LABEL_COL = "lemma", "label"
labels = labels[labels[LABEL_COL].isin(CLASSES)].copy()   # drop disputed, ottoman, other_*
labels[LEMMA_COL] = labels[LEMMA_COL].astype(str).str.lower().str.strip()
label_lookup = dict(zip(labels[LEMMA_COL], labels[LABEL_COL]))
print(len(label_lookup), "labeled lemmas available")

# ── 4: stream sentences directly out of the zip (replaces xml_to_csv.py) ──
def iter_sentences(zip_path, shuffle=True, seed=42):
    """Yield subtitle sentences one at a time without unzipping anything."""
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if n.endswith((".xml", ".xml.gz"))]
        if shuffle:  # zip is ordered by year; shuffle for a varied sample
            random.Random(seed).shuffle(names)
        for name in names:
            with z.open(name) as f:
                if name.endswith(".gz"):
                    f = gzip.open(f)
                try:
                    for _, elem in ET.iterparse(f, events=("end",)):
                        if elem.tag == "s":
                            text = " ".join("".join(elem.itertext()).split())
                            if text:
                                yield text
                            elem.clear()
                except ET.ParseError:
                    continue

# ── 5: tokenize, lemmatize, label — stop at TARGET ──
nlp = spacy.load("hu_core_news_lg", disable=["ner", "parser"])

rows, seen, n_sent = [], set(), 0
counts = Counter()       # how often each lemma appears in the sentences read
for doc in nlp.pipe(iter_sentences(ZIP_PATH), batch_size=256):
    n_sent += 1
    for t in doc:
        if t.is_stop or t.is_punct or t.is_space or not t.is_alpha:
            continue
        lemma = t.lemma_.lower()
        counts[lemma] += 1
        if UNIQUE_LEMMAS and lemma in seen:
            continue
        label = label_lookup.get(lemma)
        if label is None:
            continue
        seen.add(lemma)
        rows.append({"token": t.text.lower(), "lemma": lemma, "label": label, "text": doc.text})
        if len(rows) % 100 == 0:
            print(f"{len(rows)} labeled rows ({n_sent} sentences read)")
    if len(rows) >= TARGET:
        break

tokens_df = pd.DataFrame(rows[:TARGET])
tokens_df["count"] = tokens_df["lemma"].map(counts)   # subtitle frequency, for the frequency baseline
tokens_df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
print(f"Saved {len(tokens_df)} rows → {OUT_CSV} after {n_sent} sentences")
print(tokens_df["label"].value_counts().to_string())
print(tokens_df.head())