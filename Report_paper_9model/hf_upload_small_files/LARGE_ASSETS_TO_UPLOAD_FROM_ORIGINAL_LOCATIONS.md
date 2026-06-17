# Large HF Assets — Upload From Original Locations

The small-files package copies only newly generated small public artifacts. The following large assets stay in their original folders and should be included during the actual Hugging Face upload.

## Final processed ASR dataset

- Local source: `Processed_Balanced19_v3/Dataset_Balanced19/`
- HF target: `data/processed_balanced19_v3/Dataset_Balanced19/`
- Approx. size: about 16 GB
- Action: Upload from original path during HF large-folder upload; do not move or modify source.

## Raw/original audio (optional, consent-gated)

- Local source: `Dataset_Ori/`
- HF target: `data/raw_original/`
- Approx. size: about 17 GB
- Action: Upload only if consent/license allows; keep original folder unchanged.

## Final 9-model best artifacts

- Local source: `Report_paper_9model/model_artifacts/rank*/best_artifact/`
- HF target: `models/final_9model_benchmark/rank*/best_artifact/`
- Approx. size: about 1.26 GB
- Action: Upload from original artifact package; do not commit large weights to GitHub.

## Full benchmark predictions CSV files

- Local source: `Final run directories test_results/predictions.csv`
- HF target: `models/final_9model_benchmark/rank*/run_outputs/predictions.csv`
- Approx. size: about 23.4 MB total
- Action: Upload from original final run directories; GitHub intentionally skipped these >1 MB files.

## Paper-clean legacy statistics subset (optional)

- Local source: `reports/dataset_statistics_v7_paper9/`
- HF target: `paper/dataset_information/paper_clean_subset_optional/`
- Approx. size: small/moderate
- Action: Upload only with clear label paper-clean/statistics subset; prefer regenerated full-scope package in this small-files folder.
