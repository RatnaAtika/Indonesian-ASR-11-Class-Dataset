# Run outputs uploaded to GitHub (safe subset)

This manifest documents the GitHub-safe subset of `run_outputs/` for all 9 paper model artifacts.

## Policy

- Include: run output files with size <= 1,000,000 bytes.
- Exclude: model/checkpoint files (`.pt`, `.pth`, `.pkl`, `.safetensors`, `.bin`, `.ckpt`, `.h5`, `.keras`).
- Exclude: files > 1 MB. These are intentionally skipped for GitHub and should be uploaded separately to Hugging Face/model artifact storage when needed.

## Summary

- Included files: **61** / **1.5 MB**
- Skipped files: **9** / **23.4 MB**

## Included files by model

### rank01_m02b-whisper-small-ft
- `Report_paper_9model/model_artifacts/rank01_m02b-whisper-small-ft/run_outputs/best_model_BEST_INFO.txt` — 259 B
- `Report_paper_9model/model_artifacts/rank01_m02b-whisper-small-ft/run_outputs/history.json` — 2.7 KB
- `Report_paper_9model/model_artifacts/rank01_m02b-whisper-small-ft/run_outputs/meta.json` — 2.4 KB
- `Report_paper_9model/model_artifacts/rank01_m02b-whisper-small-ft/run_outputs/model_summary.pdf` — 21.6 KB
- `Report_paper_9model/model_artifacts/rank01_m02b-whisper-small-ft/run_outputs/model_summary.png` — 117.2 KB
- `Report_paper_9model/model_artifacts/rank01_m02b-whisper-small-ft/run_outputs/report.md` — 1.2 KB
- `Report_paper_9model/model_artifacts/rank01_m02b-whisper-small-ft/run_outputs/test_paper.json` — 8.1 KB
- `Report_paper_9model/model_artifacts/rank01_m02b-whisper-small-ft/run_outputs/test_summary.md` — 2.8 KB
- `Report_paper_9model/model_artifacts/rank01_m02b-whisper-small-ft/run_outputs/training_log.txt` — 6.8 KB

### rank02_m06-conformer-ctc
- `Report_paper_9model/model_artifacts/rank02_m06-conformer-ctc/run_outputs/history.json` — 16.5 KB
- `Report_paper_9model/model_artifacts/rank02_m06-conformer-ctc/run_outputs/meta.json` — 2.3 KB
- `Report_paper_9model/model_artifacts/rank02_m06-conformer-ctc/run_outputs/model_summary.pdf` — 22.2 KB
- `Report_paper_9model/model_artifacts/rank02_m06-conformer-ctc/run_outputs/model_summary.png` — 297.7 KB
- `Report_paper_9model/model_artifacts/rank02_m06-conformer-ctc/run_outputs/report.md` — 497 B
- `Report_paper_9model/model_artifacts/rank02_m06-conformer-ctc/run_outputs/test_paper.json` — 8.4 KB
- `Report_paper_9model/model_artifacts/rank02_m06-conformer-ctc/run_outputs/test_summary.md` — 376 B
- `Report_paper_9model/model_artifacts/rank02_m06-conformer-ctc/run_outputs/training_log.txt` — 39.2 KB

### rank03_m12-vit-modified-ID
- `Report_paper_9model/model_artifacts/rank03_m12-vit-modified-ID/run_outputs/model_summary.pdf` — 22.0 KB
- `Report_paper_9model/model_artifacts/rank03_m12-vit-modified-ID/run_outputs/model_summary.png` — 116.4 KB
- `Report_paper_9model/model_artifacts/rank03_m12-vit-modified-ID/run_outputs/test_paper.json` — 5.0 KB
- `Report_paper_9model/model_artifacts/rank03_m12-vit-modified-ID/run_outputs/test_summary.md` — 2.8 KB
- `Report_paper_9model/model_artifacts/rank03_m12-vit-modified-ID/run_outputs/training_log.txt` — 42.8 KB

### rank04_m07-bilstm-ctc
- `Report_paper_9model/model_artifacts/rank04_m07-bilstm-ctc/run_outputs/history.json` — 16.5 KB
- `Report_paper_9model/model_artifacts/rank04_m07-bilstm-ctc/run_outputs/meta.json` — 2.3 KB
- `Report_paper_9model/model_artifacts/rank04_m07-bilstm-ctc/run_outputs/model_summary.pdf` — 20.7 KB
- `Report_paper_9model/model_artifacts/rank04_m07-bilstm-ctc/run_outputs/model_summary.png` — 85.4 KB
- `Report_paper_9model/model_artifacts/rank04_m07-bilstm-ctc/run_outputs/report.md` — 492 B
- `Report_paper_9model/model_artifacts/rank04_m07-bilstm-ctc/run_outputs/test_paper.json` — 8.4 KB
- `Report_paper_9model/model_artifacts/rank04_m07-bilstm-ctc/run_outputs/test_summary.md` — 373 B
- `Report_paper_9model/model_artifacts/rank04_m07-bilstm-ctc/run_outputs/training_log.txt` — 39.0 KB

### rank05_m11-vanilla-transformer
- `Report_paper_9model/model_artifacts/rank05_m11-vanilla-transformer/run_outputs/model_summary.pdf` — 22.2 KB
- `Report_paper_9model/model_artifacts/rank05_m11-vanilla-transformer/run_outputs/model_summary.png` — 124.5 KB
- `Report_paper_9model/model_artifacts/rank05_m11-vanilla-transformer/run_outputs/test_paper.json` — 5.0 KB
- `Report_paper_9model/model_artifacts/rank05_m11-vanilla-transformer/run_outputs/test_summary.md` — 2.8 KB
- `Report_paper_9model/model_artifacts/rank05_m11-vanilla-transformer/run_outputs/training_log.txt` — 43.1 KB

### rank06_m13-wav2letter
- `Report_paper_9model/model_artifacts/rank06_m13-wav2letter/run_outputs/history.json` — 16.6 KB
- `Report_paper_9model/model_artifacts/rank06_m13-wav2letter/run_outputs/meta.json` — 2.4 KB
- `Report_paper_9model/model_artifacts/rank06_m13-wav2letter/run_outputs/model_summary.pdf` — 21.6 KB
- `Report_paper_9model/model_artifacts/rank06_m13-wav2letter/run_outputs/model_summary.png` — 223.4 KB
- `Report_paper_9model/model_artifacts/rank06_m13-wav2letter/run_outputs/report.md` — 481 B
- `Report_paper_9model/model_artifacts/rank06_m13-wav2letter/run_outputs/test_paper.json` — 8.2 KB
- `Report_paper_9model/model_artifacts/rank06_m13-wav2letter/run_outputs/test_summary.md` — 2.8 KB
- `Report_paper_9model/model_artifacts/rank06_m13-wav2letter/run_outputs/training_log.txt` — 39.7 KB

### rank07_m08-hmm-gmm
- `Report_paper_9model/model_artifacts/rank07_m08-hmm-gmm/run_outputs/history.json` — 528 B
- `Report_paper_9model/model_artifacts/rank07_m08-hmm-gmm/run_outputs/meta.json` — 2.4 KB
- `Report_paper_9model/model_artifacts/rank07_m08-hmm-gmm/run_outputs/report.md` — 430 B
- `Report_paper_9model/model_artifacts/rank07_m08-hmm-gmm/run_outputs/test_paper.json` — 8.3 KB
- `Report_paper_9model/model_artifacts/rank07_m08-hmm-gmm/run_outputs/test_summary.md` — 2.7 KB
- `Report_paper_9model/model_artifacts/rank07_m08-hmm-gmm/run_outputs/training_log.txt` — 1.5 KB

### rank08_m10-gmm-hmm-dnn
- `Report_paper_9model/model_artifacts/rank08_m10-gmm-hmm-dnn/run_outputs/history.json` — 15.6 KB
- `Report_paper_9model/model_artifacts/rank08_m10-gmm-hmm-dnn/run_outputs/meta.json` — 2.5 KB
- `Report_paper_9model/model_artifacts/rank08_m10-gmm-hmm-dnn/run_outputs/report.md` — 524 B
- `Report_paper_9model/model_artifacts/rank08_m10-gmm-hmm-dnn/run_outputs/test_paper.json` — 7.9 KB
- `Report_paper_9model/model_artifacts/rank08_m10-gmm-hmm-dnn/run_outputs/test_summary.md` — 2.2 KB
- `Report_paper_9model/model_artifacts/rank08_m10-gmm-hmm-dnn/run_outputs/training_log.txt` — 33.1 KB

### rank09_m09-dnn-hmm
- `Report_paper_9model/model_artifacts/rank09_m09-dnn-hmm/run_outputs/history.json` — 15.6 KB
- `Report_paper_9model/model_artifacts/rank09_m09-dnn-hmm/run_outputs/meta.json` — 2.5 KB
- `Report_paper_9model/model_artifacts/rank09_m09-dnn-hmm/run_outputs/report.md` — 435 B
- `Report_paper_9model/model_artifacts/rank09_m09-dnn-hmm/run_outputs/test_paper.json` — 7.7 KB
- `Report_paper_9model/model_artifacts/rank09_m09-dnn-hmm/run_outputs/test_summary.md` — 2.2 KB
- `Report_paper_9model/model_artifacts/rank09_m09-dnn-hmm/run_outputs/training_log.txt` — 33.7 KB

## Skipped files

- `Report_paper_9model/model_artifacts/rank01_m02b-whisper-small-ft/run_outputs/predictions.csv` — 2.9 MB — skipped_over_1MB_github_limit_policy
- `Report_paper_9model/model_artifacts/rank02_m06-conformer-ctc/run_outputs/predictions.csv` — 2.8 MB — skipped_over_1MB_github_limit_policy
- `Report_paper_9model/model_artifacts/rank03_m12-vit-modified-ID/run_outputs/predictions.csv` — 2.1 MB — skipped_over_1MB_github_limit_policy
- `Report_paper_9model/model_artifacts/rank04_m07-bilstm-ctc/run_outputs/predictions.csv` — 2.8 MB — skipped_over_1MB_github_limit_policy
- `Report_paper_9model/model_artifacts/rank05_m11-vanilla-transformer/run_outputs/predictions.csv` — 2.1 MB — skipped_over_1MB_github_limit_policy
- `Report_paper_9model/model_artifacts/rank06_m13-wav2letter/run_outputs/predictions.csv` — 2.9 MB — skipped_over_1MB_github_limit_policy
- `Report_paper_9model/model_artifacts/rank07_m08-hmm-gmm/run_outputs/predictions.csv` — 3.1 MB — skipped_over_1MB_github_limit_policy
- `Report_paper_9model/model_artifacts/rank08_m10-gmm-hmm-dnn/run_outputs/predictions.csv` — 2.3 MB — skipped_over_1MB_github_limit_policy
- `Report_paper_9model/model_artifacts/rank09_m09-dnn-hmm/run_outputs/predictions.csv` — 2.3 MB — skipped_over_1MB_github_limit_policy
