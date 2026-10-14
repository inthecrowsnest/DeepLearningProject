"""Convert every OpenSubtitles .xml file under a folder into a .csv.

Usage:
    python xml_to_csv.py <xml_root> <csv_folder>

if you have the entire zip file download then it can walk through ALL subfolders of <xml_root> (hu/<year>/<imdb_id>/<file>.xml),
converts each .xml to a .csv, and saves them all directly in <csv_folder>
(no subfolders): csv/<file>.csv. Already-converted files are skipped, so you
can stop and restart it safely.

Example:
    python xml_to_csv.py OpenSubtitles csv
"""
import csv
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

COLUMNS = ("doc_id", "year", "country", "original", "genre", "sentence_id", "text")

NO_SPACE_BEFORE = re.compile(r"\s+([.,!?;:%)\]}…»])")
NO_SPACE_AFTER = re.compile(r"([(\[{«„])\s+")


def detokenize(words):
    """'Szia , hogy vagy ?' -> 'Szia, hogy vagy?'"""
    text = " ".join(words)
    text = NO_SPACE_BEFORE.sub(r"\1", text)
    text = NO_SPACE_AFTER.sub(r"\1", text)
    return text.strip()


def meta_value(root, tag):
    el = root.find(f".//meta//{tag}")
    return el.text.strip() if el is not None and el.text else ""


def parse_xml(path, rel):
    """Return one row per subtitle sentence (<s> element)."""
    root = ET.parse(path).getroot()

    folder_year = path.parent.parent.name          # .../<year>/<imdb_id>/<file>.xml
    year = meta_value(root, "year") or (folder_year if folder_year.isdigit() else "")
    country = meta_value(root, "country")
    original = meta_value(root, "original")
    genre = meta_value(root, "genre")
    doc_id = rel.with_suffix("").as_posix()

    rows = []
    for s in root.iter("s"):
        words = [w.text for w in s.iter("w") if w.text]
        if words:                                   # tokenized XML (<w> tags)
            text = detokenize(words)
        else:                                       # raw XML (text directly in <s>)
            text = " ".join("".join(s.itertext()).split())
        if text:
            rows.append({
                "doc_id": doc_id, "year": year, "country": country,
                "original": original, "genre": genre,
                "sentence_id": s.get("id", ""), "text": text,
            })
    return rows


def main(xml_root, csv_root):
    xml_root, csv_root = Path(xml_root).resolve(), Path(csv_root).resolve()
    files = sorted(p for p in xml_root.rglob("*.xml") if csv_root not in p.parents)
    print(f"Found {len(files)} XML files")

    done = skipped = failed = 0
    for i, path in enumerate(files, 1):
        rel = path.relative_to(xml_root)
        out = csv_root / (path.stem + ".csv")       

        if out.exists():
            skipped += 1
        else:
            try:
                rows = parse_xml(path, rel)
            except ET.ParseError as e:
                failed += 1
                print(f"  ! could not parse {rel}: {e}", file=sys.stderr)
                continue

            out.parent.mkdir(parents=True, exist_ok=True)
            tmp = out.with_name(out.name + ".tmp")   # write to temp then rename,
            with open(tmp, "w", newline="", encoding="utf-8") as fo:  # so no half-written CSVs
                writer = csv.DictWriter(fo, fieldnames=COLUMNS)
                writer.writeheader()
                writer.writerows(rows)
            tmp.replace(out)
            done += 1

        if i % 1000 == 0 or i == len(files):
            print(f"  {i}/{len(files)}  converted={done} skipped={skipped} failed={failed}")

    print(f"Done: {done} converted, {skipped} already existed, {failed} failed -> {csv_root}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])