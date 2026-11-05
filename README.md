# Milestone 1 Readme 

**Team Winners:** Joy, Radiah, Ellie. Deep Learning

Given a single Hungarian word (its lemma), predict which language it came from: **native** (inherited Uralic), **German**, **Slavic** or **Turkic**.
Words come from Hungarian film subtitles (OpenSubtitles); labels come from etymology databases (Wiktionary via kaikki.org, and CLDF).

## Milestone 1 hand-in

| What | File |
|---|---|
| **Notebook (runs top to bottom)** | [`m1_updated_model.ipynb`](m1_updated_model.ipynb) |
| Data the notebook uses | `tokens_dataset_updated.csv` (in this repo) |
| Preprocessing that produced that data | `preprocessing_updated.py` |
| Report | the PDF handed in separately |

The notebook contains one baseline and one simple model, both scored on the same test folds. It actually has three baselines (majority class, frequency only, character n-gram logistic regression) and one main model (a character-level bidirectional GRU). Everything is evaluated with 5-fold stratified cross-validation, and the primary metric is macro-F1.

## How to run the notebook

You don't need to download or preprocess anything: the data file is in the repo.

### Option A: Google Colab (easiest)
1. Open `m1_updated_model.ipynb` on GitHub and click **Open in Colab**. You can also open https://colab.research.google.com and use File → Open notebook → GitHub with `inthecrowsnest/DeepLearningProject`.
2. Click **Runtime → Run all**.

The first code cell clones this repo, so the data file is found automatically. A CPU runtime is enough; the whole notebook runs in a few minutes.

### Option B: locally
```bash
git clone https://github.com/inthecrowsnest/DeepLearningProject.git
cd DeepLearningProject
pip install -r requirements.txt jupyter
jupyter notebook m1_updated_model.ipynb      # then Kernel → Restart & Run All
```

### Requirements
- Python 3.9 or newer
- `requirements.txt`: pandas, scikit-learn, torch, matplotlib (needed for the notebook), and huspacy (only needed for preprocessing)
- No GPU needed

## What the notebook does

1. **Loads** `tokens_dataset_updated.csv` and keeps only the four classes.
2. **Cleans** the data with hand-picked rules that remove pronouns, interjections, proper names and lemmatiser junk.
3. **Splits** with 5-fold cross-validation **by word**, stratified by class, seed 0. Inside each training fold, 15% of words are held out as validation for early stopping. No test word ever appears in training.
4. **Baselines**:
   - majority class (0 parameters)
   - frequency only: logistic regression on the log subtitle count (5 parameters)
   - character 2–4-gram TF-IDF + logistic regression
5. **Main model**: a character-level bidirectional GRU. It has an embedding of size 16, a BiGRU with 32 units per direction and dropout 0.3, then a linear layer to 4 classes, for 10,436 parameters in total. It uses class-weighted cross-entropy, Adam (learning rate 3e-3, weight decay 1e-4), batch size 32, and early stopping on validation macro-F1 with patience 15.
6. **Sanity check**: with dropout off, the GRU memorises 20 words (5 per class) to near-zero loss.
7. **Outputs**: a results table (mean ± std over 5 folds), the GRU training curve (fold 0), and confusion matrices for the n-gram model and the GRU.

### Results (mean ± std over 5 folds)

| Model | Accuracy | Macro-F1 |
|---|---|---|
| Majority baseline | 0.383 ± 0.000 | 0.138 ± 0.000 |
| Frequency only | 0.435 ± 0.033 | 0.332 ± 0.038 |
| Char n-gram LR | 0.637 ± 0.041 | 0.609 ± 0.041 |
| Char-GRU | 0.607 ± 0.013 | 0.576 ± 0.006 |

The GRU does not beat the character n-gram baseline; the gap is within the fold-to-fold variation. The report explains why.

## Data and preprocessing (optional: only to rebuild the data)

```bash
python preprocessing_updated.py   # the first run installs the HuSpaCy model and stops: run it again
```
- **Text:** Hungarian OpenSubtitles from OPUS (v2024, raw XML). The script downloads `hu.zip` (~5 GB, ignored by git) and reads sentences straight from the zip, in a shuffled file order (seed 42), without unzipping.
- **Pipeline:**
  - tokenise and lemmatise with HuSpaCy `hu_core_news_lg`
  - drop stop words, punctuation and non-alphabetic tokens, and lowercase everything
  - look each lemma up in `labeled_words.csv`, keeping only the four classes
  - keep each lemma once, with its subtitle `count`
  - stop at 1,000 labeled words
- **Output:** `tokens_dataset_updated.csv`, with columns `token, lemma, label, text, count`.
- `huspacy.download()` fails on recent pip, because the model's wheel filename has no version in it, so the script installs the model itself.

**Labels:** `build_table.py` builds `words.csv` / `labeled_words.csv` from the Hungarian Wiktionary dump at [kaikki.org](https://kaikki.org/dictionary/Hungarian/). That dump is `hungarian.jsonl`, 560 MB, and not in the repo. Turkic labels come from CLDF (Róna-Tas & Berta, 2011; `cldf_turkic.csv`). There are 2,075 words in the four classes. Ottoman Turkish words and 40 disputed words are excluded.

## Repository layout

| File | Purpose |
|---|---|
| `m1_updated_model.ipynb` | **Milestone 1 notebook**: cleaning, split, baselines, GRU, results |
| `preprocessing_updated.py` | subtitles → labeled words with counts |
| `tokens_dataset_updated.csv` | the data the notebook uses |
| `build_table.py` | builds the label table from Wiktionary + CLDF |
| `labeled_words.csv`, `words.csv` | label tables (one row per word) |
| `cldf_turkic.csv`, `source_counts.csv` | Turkic loanwords from CLDF; counts of Wiktionary source languages |
| `xml_to_csv.py`, `label_subtitles.py`, `clean_labeled_subtitles.py`, `subtitles_to_jsonl.py`, `labeled_subtitle_words.csv` | earlier version of the pipeline, kept for reference |
