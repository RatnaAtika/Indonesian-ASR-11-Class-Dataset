---
pretty_name: Indonesian ASR 11-Class Dataset
language:
- id
task_categories:
- automatic-speech-recognition
- audio-classification
size_categories:
- 100K<n<1M
license: other
private: true
---

# Indonesian ASR 11-Class Dataset

Private pre-publication Hugging Face staging repository for an Indonesian ASR corpus and its paper-supporting benchmark artifacts.

> **Current visibility:** private while the Data in Brief paper is being prepared/reviewed. Public release should happen only after consent, license, and paper-publication checks are complete.

## Dataset summary

- **Audio files:** 104,500 WAV files
- **Real/human recordings:** 104,368
- **Synthetic repair files:** 132
- **Sentence classes:** 11 Indonesian sentence categories
- **Public speaker labels:** `M1..M12`, `F1..F8`, plus synthetic labels `Ms*`/`Fs*`
- **Audio format:** 16 kHz, 16-bit, mono
- **Total duration:** about 134.18 hours
- **Splits:** speaker-disjoint train/dev/test, seed 42

The public metadata uses pseudonymous public labels only. Original respondent names and private crosswalks are not included in this repository.

## Category naming

All public Hugging Face category names are in English. See `docs/CATEGORY_NAMING.md` for the public English category list. The `category` column in `metadata/dataset_metadata_public.csv`, transcript filenames, and audio shard filenames use English names.

## Important transcript numbering note

Sentence IDs intentionally preserve the original collection numbering (`01`–`20`). Some category transcript lists skip one ID, for example `Clarification` skips `09`. These gaps are expected and come from curation/removal of duplicate or balancing sentences; they do **not** mean that the HF upload is incomplete. Do not renumber sentence IDs when using or citing the dataset.

For the full per-category inventory, read:

```text
docs/TRANSCRIPT_NUMBERING_NOTES.md
metadata/transcript_sentence_inventory_public.csv
```

For experiments, always use `metadata/dataset_metadata_public.csv` as the row-level source of truth.

## Repository structure

```text
data/
  audio_shards/by_category/*.tar                              # anonymized WAV tree packaged by sentence category
  audio_shards/audio_shards_manifest.csv                      # shard index
  transcripts/                                                # sentence transcripts by category
metadata/
  dataset_metadata_public.csv                                 # public metadata with anonymized labels
  speaker_labels/                                             # public label inventories/schema
splits/
  speaker_split_assignment_public.csv
  split_summary_public.json
paper/
  dataset_information/                                        # full-scope public dataset statistics
  dataset_information/figures_public/                         # regenerated public-label figures
docs/
  CITATION.md
  HF_DATASET_INFORMATION_FINAL_REPORT.md
  HF_DATASET_INFORMATION_SELECTION.md
```

## Dataset update notes

See `docs/DATASET_UPDATE_NOTES.md` for the 2026-06-18 transcript cleanup note. In short: transcript text files are clean public sentence lists; `metadata/dataset_metadata_public.csv` is the row-level source of truth. Audio shards and paths were not changed by the cleanup.

## Loading metadata

Use `metadata/dataset_metadata_public.csv`. Audio is stored as category-level tar shards under `data/audio_shards/by_category/`. Extract shards into your working directory to materialize paths such as `data/processed_balanced19_v7_natural_synth/Dataset_Balanced19/...`. Example:

```bash
mkdir -p extracted
tar -xf data/audio_shards/by_category/Declarative.tar -C extracted
```

Then join `extracted/` with the `audio_path` column. Important columns:

- `audio_path`: relative path after extracting the relevant tar shard to the repository root
- `split`: `train`, `dev`, or `test`
- `speaker_id`: public acoustic-source label (`M*`, `F*`, `Ms*`, `Fs*`)
- `speaker_type`: `human` or `synthetic`
- `speaker_gender`: public acoustic-source gender label
- `repair_target_speaker_id`: target human label for synthetic repair rows
- `voice_gender_matches_target`: whether synthetic voice gender matches repair target gender
- `transcript`: reference transcription

## Citation

Until the paper DOI is available, cite the dataset repository and the GitHub preparation commit. See `docs/CITATION.md` and [`CITATION.cff`](CITATION.cff).

## Caveats

- Two synthetic repair files are explicitly flagged with `voice_gender_matches_target=False`; review/regenerate them before final public release if strict gender-matched synthetic repair is required.
- `paper/dataset_information/` is generated from the full 104,500-file public metadata. Older paper-clean statistics are not used as full-scope statistics unless clearly labeled as a subset.
- License is intentionally marked `other` until the final public-release license is approved.
