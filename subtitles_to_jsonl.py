"""Flatten OpenSubtitles per-film CSVs (hu/<year>/<imdb_id>/<file>.csv) into one JSONL.

Usage: python subtitles_to_jsonl.py <csv_root> <out.jsonl>
The CSVs are too large (~16GB) to version; keep them outside the repo.
"""
import csv
import json
import sys
from pathlib import Path

KEEP = ("doc_id", "year", "country", "original", "genre", "sentence_id", "text")


def main(root, out):
    with open(out, "w", encoding="utf-8") as fo:
        for path in sorted(Path(root).rglob("*.csv")):
            with open(path, newline="", encoding="utf-8") as fi:
                for row in csv.DictReader(fi):
                    fo.write(json.dumps({k: row[k] for k in KEEP}, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
