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
