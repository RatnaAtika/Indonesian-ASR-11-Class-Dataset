# Final Report — HF Dataset Information and Speaker-Label Corrections

Status: **completed and pushed**.

## 1. Critical scope issue resolved

Previous issue:

- `reports/dataset_statistics_v7_paper9/` was generated on the paper-clean subset: **102,544 files**.
- The Hugging Face upload target is the full dataset metadata: **104,500 files**.
- Therefore the old statistics package must not be presented as full-dataset statistics unless explicitly labeled as `paper-clean/statistics subset`.

Resolution:

- Generated a new public-safe, full-scope dataset information package from `metadata/dataset_metadata.csv`:

```text
Report_paper_9model/hf_dataset_information_public/
```

This package is the preferred source for HF `paper/dataset_information/` because it matches the full 104,500-file target and uses public labels only.

## 2. Corrected speaker-label policy

The speaker-label preparation now applies the corrected gender assignment requested by the project owner.

Human labels:

```text
Male:
M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, M12

Female:
F1, F2, F3, F4, F5, F6, F7, F8
```

Important correction:

- One respondent that was previously assigned `Female` in source metadata is corrected to **Male** in the public-label pipeline.
- The corrected respondent is assigned public label `M8`.
- This correction affects **5,225 metadata rows** in the full 104,500-file scope.
- The original-name detail is kept only in the private local crosswalk outside Git/HF.

## 3. Synthetic-data cross-check result

Synthetic labels are assigned using the **actual synthetic voice gender**, not only the repair-target gender:

- Male synthetic labels: `Ms1..Ms9`
- Female synthetic labels: `Fs1..Fs9`

Cross-check finding:

- Total synthetic files: **132**
- Synthetic male voice files: **73**
- Synthetic female voice files: **59**
- Voice-target gender mismatch files: **2**

The 2 mismatch files are synthetic female TTS voice rows that repair target speaker `M8`. They are not hidden; they are explicitly flagged in:

```text
Report_paper_9model/hf_anonymization/synthetic_repair_targets_public.csv
Report_paper_9model/hf_dataset_information_public/synthetic_repair_rows_public.csv
```

Relevant columns:

```text
repair_target_speaker_id
repair_target_speaker_gender
voice_gender_matches_target
```

## 4. Dataset information package generated for HF

Preferred full-scope public package:

```text
Report_paper_9model/hf_dataset_information_public/
```

Generated files:

```text
README.md
dataset_stats_public.json
word_frequency_public.csv
per_category_public.csv
per_split_public.csv
per_speaker_public.csv
synthetic_data_stats_public.json
synthetic_repair_rows_public.csv
audio_quality_sample_public.csv
figures_public/F1_files_per_speaker_split_public.pdf/png
figures_public/F3_speaker_total_duration_public.pdf/png
figures_public/F7_speaker_category_heatmap_public.pdf/png
```

Notes:

- `word_frequency_public.csv` is regenerated from the full 104,500-file metadata transcripts.
- `per_category_public.csv`, `per_split_public.csv`, and `per_speaker_public.csv` are full-scope public-label summaries.
- `audio_quality_sample_public.csv` is a public-safe anonymized version of the existing paper-clean audio-quality sample; it includes `source_scope=paper_clean_audio_quality_sample` so it is not confused with a full-scope audio-quality scan.
- Per-speaker figures F1/F3/F7 were regenerated with public labels.

## 5. Optimized upload decisions

Updated files documenting the selection:

```text
Report_paper_9model/HF_DATASET_INFORMATION_SELECTION.md
Report_paper_9model/hf_dataset_information_selection.csv
Report_paper_9model/hf_dataset_information_selection.json
Report_paper_9model/HUGGINGFACE_DATASET_UPLOAD_PLAN.md
```

Summary of decisions:

- Prefer `Report_paper_9model/hf_dataset_information_public/` for full-scope HF upload.
- Keep old `reports/dataset_statistics_v7_paper9/` only as optional `paper-clean/statistics subset`.
- Do not upload noisy detailed take-audit files with original paths/names.
- Do not upload private crosswalks.

## 6. Privacy and consistency verification

Checks passed:

- Public speaker-label verification OK.
- Full-scope dataset information generated from 104,500 rows.
- Public text/CSV/JSON files scanned for original respondent names: **0 leaks**.
- Private crosswalks remain outside the Git worktree in:

```text
C:\Users\wayandadang\AI\Dataset_ASR_PRIVATE_HF
```

- No staged files over 10 MB.
- Secret/token scan passed.
- `git diff --cached --check` passed.

## 7. Remaining HF-public caveat

The 2 synthetic voice/target gender mismatch rows should be reviewed before final public release. Options:

1. Keep them with explicit `voice_gender_matches_target=False` flags, or
2. Regenerate those 2 synthetic files using male TTS voice before final HF public release, then refresh the public information package.

Current preparation keeps them transparent and flagged.
