Plan:
Count: 2,127 words in four classes: German 795, native 498, Turkic 427, Slavic 355. Turkic comes from CLDF (Róna-Tas and Berta, with the link), and the rest from Wiktionary through kaikki (with the link and download date). Mention that build_table.py makes the table.
Five rows: df.sample(5) from labeled_words.csv, ideally one per class.
Split: 70/15/15 by word, stratified by class, so about 1,489 / 319 / 319. Print all three sizes. Say plainly that we split on word type, so no test word appears in training.
Honest look:
The classes are uneven: German is more than twice the size of Slavic.
Only 498 native words are confirmed.
We removed 40 disputed words.
Some German words are international words like detonáció.
Related words, like a root and its compound, could end up on both sides of the split.

## Loanword project setup

- Python 3.9+ (on Windows use `python` instead of `python3`).
- `pip install -r requirements.txt`, then `python -c "import huspacy; huspacy.download()"`.
- `hungarian.jsonl` (560 MB) and the OpenSubtitles data are not in the repo. `build_table.py` needs the former; to train you only need `labeled_words.csv`.
- Scripts find their files relative to their own folder, so they can be run from anywhere.
