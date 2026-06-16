# Training diagnostics package for final 9-model paper benchmark

Status: generated from the final run directories referenced by `Report_paper_9model/benchmark/benchmark.json`.

## Purpose

This folder collects paper-ready training plots, model-summary figures, run reports, logs, test summaries, and compact evaluation diagnostics for all nine final benchmark models. It is intended as the central source for training-result plots and appendix evidence used in the paper.

## Inclusion / skip policy

- Included: plots/figures (`.png`, `.pdf`), model summaries, `report.md`, `history.json`, `meta.json`, logs, `test_paper.json`, `test_summary.md`, and compact evaluation spreadsheets.
- Skipped: model/checkpoint artifacts, `best_model/`, per-epoch prediction JSON, full `predictions.csv`, full eval CSV >1 MB, and files over 10 MB.
- Rationale: GitHub stores paper evidence and plots; model weights and bulky prediction tables should go to Hugging Face/external artifact storage.

## Summary

- Included files: **120** / **4.3 MB**
- Skipped files: **182** / **1.3 GB**

| Model artifact folder | Included files | Plot/figure files | Report/data files | Size |
|---|---:|---:|---:|---:|
| `rank01_m02b-whisper-small-ft` | 14 | 7 | 7 | 409.8 KB |
| `rank02_m06-conformer-ctc` | 16 | 7 | 9 | 662.3 KB |
| `rank03_m12-vit-modified-ID` | 12 | 8 | 4 | 713.6 KB |
| `rank04_m07-bilstm-ctc` | 16 | 7 | 9 | 438.4 KB |
| `rank05_m11-vanilla-transformer` | 12 | 8 | 4 | 771.0 KB |
| `rank06_m13-wav2letter` | 14 | 7 | 7 | 575.0 KB |
| `rank07_m08-hmm-gmm` | 12 | 5 | 7 | 161.1 KB |
| `rank08_m10-gmm-hmm-dnn` | 12 | 5 | 7 | 341.5 KB |
| `rank09_m09-dnn-hmm` | 12 | 5 | 7 | 337.9 KB |

## Included files

### rank01_m02b-whisper-small-ft
- `Report_paper_9model/training_diagnostics/rank01_m02b-whisper-small-ft/config.json` — 586 B (source: `config.json`)
- `Report_paper_9model/training_diagnostics/rank01_m02b-whisper-small-ft/history.json` — 2.7 KB (source: `history.json`)
- `Report_paper_9model/training_diagnostics/rank01_m02b-whisper-small-ft/log.txt` — 6.8 KB (source: `log.txt`)
- `Report_paper_9model/training_diagnostics/rank01_m02b-whisper-small-ft/meta.json` — 2.4 KB (source: `meta.json`)
- `Report_paper_9model/training_diagnostics/rank01_m02b-whisper-small-ft/model_summary.pdf` — 21.6 KB (source: `model_summary.pdf`)
- `Report_paper_9model/training_diagnostics/rank01_m02b-whisper-small-ft/model_summary.png` — 117.2 KB (source: `model_summary.png`)
- `Report_paper_9model/training_diagnostics/rank01_m02b-whisper-small-ft/plots/accuracy.png` — 51.6 KB (source: `plots/accuracy.png`)
- `Report_paper_9model/training_diagnostics/rank01_m02b-whisper-small-ft/plots/gpu_mb.png` — 52.2 KB (source: `plots/gpu_mb.png`)
- `Report_paper_9model/training_diagnostics/rank01_m02b-whisper-small-ft/plots/loss.png` — 61.9 KB (source: `plots/loss.png`)
- `Report_paper_9model/training_diagnostics/rank01_m02b-whisper-small-ft/plots/lr.png` — 22.6 KB (source: `plots/lr.png`)
- `Report_paper_9model/training_diagnostics/rank01_m02b-whisper-small-ft/plots/wer_cer.png` — 58.1 KB (source: `plots/wer_cer.png`)
- `Report_paper_9model/training_diagnostics/rank01_m02b-whisper-small-ft/report.md` — 1.2 KB (source: `report.md`)
- `Report_paper_9model/training_diagnostics/rank01_m02b-whisper-small-ft/test_results/test_paper.json` — 8.1 KB (source: `test_results/test_paper.json`)
- `Report_paper_9model/training_diagnostics/rank01_m02b-whisper-small-ft/test_results/test_summary.md` — 2.8 KB (source: `test_results/test_summary.md`)

### rank02_m06-conformer-ctc
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/LINUX_SOURCE_MANIFEST.txt` — 472 B (source: `LINUX_SOURCE_MANIFEST.txt`)
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/config.json` — 516 B (source: `config.json`)
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/history.json` — 16.5 KB (source: `history.json`)
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/log.txt` — 39.2 KB (source: `log.txt`)
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/meta.json` — 2.3 KB (source: `meta.json`)
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/model_summary.pdf` — 22.2 KB (source: `model_summary.pdf`)
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/model_summary.png` — 297.7 KB (source: `model_summary.png`)
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/plots/accuracy.png` — 56.9 KB (source: `plots/accuracy.png`)
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/plots/gpu_mb.png` — 70.7 KB (source: `plots/gpu_mb.png`)
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/plots/loss.png` — 49.1 KB (source: `plots/loss.png`)
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/plots/lr.png` — 48.8 KB (source: `plots/lr.png`)
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/plots/wer_cer.png` — 48.5 KB (source: `plots/wer_cer.png`)
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/report.md` — 497 B (source: `report.md`)
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/test_results/test_paper.json` — 8.4 KB (source: `test_results/test_paper.json`)
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/test_results/test_summary.md` — 376 B (source: `test_results/test_summary.md`)
- `Report_paper_9model/training_diagnostics/rank02_m06-conformer-ctc/vocab.json` — 201 B (source: `vocab.json`)

### rank03_m12-vit-modified-ID
- `Report_paper_9model/training_diagnostics/rank03_m12-vit-modified-ID/Log_Run.txt` — 42.8 KB (source: `Log_Run.txt`)
- `Report_paper_9model/training_diagnostics/rank03_m12-vit-modified-ID/cer_vit.png` — 38.7 KB (source: `cer_vit.png`)
- `Report_paper_9model/training_diagnostics/rank03_m12-vit-modified-ID/char_accuracy_vit.png` — 33.2 KB (source: `char_accuracy_vit.png`)
- `Report_paper_9model/training_diagnostics/rank03_m12-vit-modified-ID/eval_greedy/results_vit.xlsx` — 338.0 KB (source: `eval_greedy/results_vit.xlsx`)
- `Report_paper_9model/training_diagnostics/rank03_m12-vit-modified-ID/eval_greedy/summary_vit.pdf` — 21.0 KB (source: `eval_greedy/summary_vit.pdf`)
- `Report_paper_9model/training_diagnostics/rank03_m12-vit-modified-ID/eval_greedy/summary_vit.png` — 32.1 KB (source: `eval_greedy/summary_vit.png`)
- `Report_paper_9model/training_diagnostics/rank03_m12-vit-modified-ID/model_summary_vit.pdf` — 22.0 KB (source: `model_summary_vit.pdf`)
- `Report_paper_9model/training_diagnostics/rank03_m12-vit-modified-ID/model_summary_vit.png` — 116.4 KB (source: `model_summary_vit.png`)
- `Report_paper_9model/training_diagnostics/rank03_m12-vit-modified-ID/test_results/test_paper.json` — 5.0 KB (source: `test_results/test_paper.json`)
- `Report_paper_9model/training_diagnostics/rank03_m12-vit-modified-ID/test_results/test_summary.md` — 2.8 KB (source: `test_results/test_summary.md`)
- `Report_paper_9model/training_diagnostics/rank03_m12-vit-modified-ID/training_val_accuracy_vit.png` — 32.5 KB (source: `training_val_accuracy_vit.png`)
- `Report_paper_9model/training_diagnostics/rank03_m12-vit-modified-ID/training_val_loss_vit.png` — 29.0 KB (source: `training_val_loss_vit.png`)

### rank04_m07-bilstm-ctc
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/LINUX_SOURCE_MANIFEST.txt` — 472 B (source: `LINUX_SOURCE_MANIFEST.txt`)
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/config.json` — 516 B (source: `config.json`)
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/history.json` — 16.5 KB (source: `history.json`)
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/log.txt` — 39.0 KB (source: `log.txt`)
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/meta.json` — 2.3 KB (source: `meta.json`)
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/model_summary.pdf` — 20.7 KB (source: `model_summary.pdf`)
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/model_summary.png` — 85.4 KB (source: `model_summary.png`)
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/plots/accuracy.png` — 48.0 KB (source: `plots/accuracy.png`)
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/plots/gpu_mb.png` — 74.0 KB (source: `plots/gpu_mb.png`)
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/plots/loss.png` — 44.1 KB (source: `plots/loss.png`)
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/plots/lr.png` — 48.4 KB (source: `plots/lr.png`)
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/plots/wer_cer.png` — 49.6 KB (source: `plots/wer_cer.png`)
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/report.md` — 492 B (source: `report.md`)
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/test_results/test_paper.json` — 8.4 KB (source: `test_results/test_paper.json`)
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/test_results/test_summary.md` — 373 B (source: `test_results/test_summary.md`)
- `Report_paper_9model/training_diagnostics/rank04_m07-bilstm-ctc/vocab.json` — 201 B (source: `vocab.json`)

### rank05_m11-vanilla-transformer
- `Report_paper_9model/training_diagnostics/rank05_m11-vanilla-transformer/Log_Run.txt` — 43.1 KB (source: `Log_Run.txt`)
- `Report_paper_9model/training_diagnostics/rank05_m11-vanilla-transformer/cer.png` — 42.1 KB (source: `cer.png`)
- `Report_paper_9model/training_diagnostics/rank05_m11-vanilla-transformer/char_accuracy.png` — 37.8 KB (source: `char_accuracy.png`)
- `Report_paper_9model/training_diagnostics/rank05_m11-vanilla-transformer/eval_greedy/results_vanilla.xlsx` — 351.2 KB (source: `eval_greedy/results_vanilla.xlsx`)
- `Report_paper_9model/training_diagnostics/rank05_m11-vanilla-transformer/eval_greedy/summary_vanilla.pdf` — 35.7 KB (source: `eval_greedy/summary_vanilla.pdf`)
- `Report_paper_9model/training_diagnostics/rank05_m11-vanilla-transformer/eval_greedy/summary_vanilla.png` — 41.4 KB (source: `eval_greedy/summary_vanilla.png`)
- `Report_paper_9model/training_diagnostics/rank05_m11-vanilla-transformer/model_summary.pdf` — 22.2 KB (source: `model_summary.pdf`)
- `Report_paper_9model/training_diagnostics/rank05_m11-vanilla-transformer/model_summary.png` — 124.5 KB (source: `model_summary.png`)
- `Report_paper_9model/training_diagnostics/rank05_m11-vanilla-transformer/test_results/test_paper.json` — 5.0 KB (source: `test_results/test_paper.json`)
- `Report_paper_9model/training_diagnostics/rank05_m11-vanilla-transformer/test_results/test_summary.md` — 2.8 KB (source: `test_results/test_summary.md`)
- `Report_paper_9model/training_diagnostics/rank05_m11-vanilla-transformer/training_val_accuracy.png` — 37.2 KB (source: `training_val_accuracy.png`)
- `Report_paper_9model/training_diagnostics/rank05_m11-vanilla-transformer/training_val_loss.png` — 27.8 KB (source: `training_val_loss.png`)

### rank06_m13-wav2letter
- `Report_paper_9model/training_diagnostics/rank06_m13-wav2letter/config.json` — 558 B (source: `config.json`)
- `Report_paper_9model/training_diagnostics/rank06_m13-wav2letter/history.json` — 16.6 KB (source: `history.json`)
- `Report_paper_9model/training_diagnostics/rank06_m13-wav2letter/log.txt` — 39.7 KB (source: `log.txt`)
- `Report_paper_9model/training_diagnostics/rank06_m13-wav2letter/meta.json` — 2.4 KB (source: `meta.json`)
- `Report_paper_9model/training_diagnostics/rank06_m13-wav2letter/model_summary.pdf` — 21.6 KB (source: `model_summary.pdf`)
- `Report_paper_9model/training_diagnostics/rank06_m13-wav2letter/model_summary.png` — 223.4 KB (source: `model_summary.png`)
- `Report_paper_9model/training_diagnostics/rank06_m13-wav2letter/plots/accuracy.png` — 50.6 KB (source: `plots/accuracy.png`)
- `Report_paper_9model/training_diagnostics/rank06_m13-wav2letter/plots/gpu_mb.png` — 65.9 KB (source: `plots/gpu_mb.png`)
- `Report_paper_9model/training_diagnostics/rank06_m13-wav2letter/plots/loss.png` — 45.4 KB (source: `plots/loss.png`)
- `Report_paper_9model/training_diagnostics/rank06_m13-wav2letter/plots/lr.png` — 47.5 KB (source: `plots/lr.png`)
- `Report_paper_9model/training_diagnostics/rank06_m13-wav2letter/plots/wer_cer.png` — 49.8 KB (source: `plots/wer_cer.png`)
- `Report_paper_9model/training_diagnostics/rank06_m13-wav2letter/report.md` — 481 B (source: `report.md`)
- `Report_paper_9model/training_diagnostics/rank06_m13-wav2letter/test_results/test_paper.json` — 8.2 KB (source: `test_results/test_paper.json`)
- `Report_paper_9model/training_diagnostics/rank06_m13-wav2letter/test_results/test_summary.md` — 2.8 KB (source: `test_results/test_summary.md`)

### rank07_m08-hmm-gmm
- `Report_paper_9model/training_diagnostics/rank07_m08-hmm-gmm/config.json` — 599 B (source: `config.json`)
- `Report_paper_9model/training_diagnostics/rank07_m08-hmm-gmm/history.json` — 528 B (source: `history.json`)
- `Report_paper_9model/training_diagnostics/rank07_m08-hmm-gmm/log.txt` — 1.5 KB (source: `log.txt`)
- `Report_paper_9model/training_diagnostics/rank07_m08-hmm-gmm/meta.json` — 2.4 KB (source: `meta.json`)
- `Report_paper_9model/training_diagnostics/rank07_m08-hmm-gmm/plots/accuracy.png` — 36.6 KB (source: `plots/accuracy.png`)
- `Report_paper_9model/training_diagnostics/rank07_m08-hmm-gmm/plots/gpu_mb.png` — 29.9 KB (source: `plots/gpu_mb.png`)
- `Report_paper_9model/training_diagnostics/rank07_m08-hmm-gmm/plots/loss.png` — 26.8 KB (source: `plots/loss.png`)
- `Report_paper_9model/training_diagnostics/rank07_m08-hmm-gmm/plots/lr.png` — 23.0 KB (source: `plots/lr.png`)
- `Report_paper_9model/training_diagnostics/rank07_m08-hmm-gmm/plots/wer_cer.png` — 28.5 KB (source: `plots/wer_cer.png`)
- `Report_paper_9model/training_diagnostics/rank07_m08-hmm-gmm/report.md` — 430 B (source: `report.md`)
- `Report_paper_9model/training_diagnostics/rank07_m08-hmm-gmm/test_results/test_paper.json` — 8.3 KB (source: `test_results/test_paper.json`)
- `Report_paper_9model/training_diagnostics/rank07_m08-hmm-gmm/test_results/test_summary.md` — 2.7 KB (source: `test_results/test_summary.md`)

### rank08_m10-gmm-hmm-dnn
- `Report_paper_9model/training_diagnostics/rank08_m10-gmm-hmm-dnn/config.json` — 617 B (source: `config.json`)
- `Report_paper_9model/training_diagnostics/rank08_m10-gmm-hmm-dnn/history.json` — 15.6 KB (source: `history.json`)
- `Report_paper_9model/training_diagnostics/rank08_m10-gmm-hmm-dnn/log.txt` — 33.1 KB (source: `log.txt`)
- `Report_paper_9model/training_diagnostics/rank08_m10-gmm-hmm-dnn/meta.json` — 2.5 KB (source: `meta.json`)
- `Report_paper_9model/training_diagnostics/rank08_m10-gmm-hmm-dnn/plots/accuracy.png` — 62.3 KB (source: `plots/accuracy.png`)
- `Report_paper_9model/training_diagnostics/rank08_m10-gmm-hmm-dnn/plots/gpu_mb.png` — 80.5 KB (source: `plots/gpu_mb.png`)
- `Report_paper_9model/training_diagnostics/rank08_m10-gmm-hmm-dnn/plots/loss.png` — 42.2 KB (source: `plots/loss.png`)
- `Report_paper_9model/training_diagnostics/rank08_m10-gmm-hmm-dnn/plots/lr.png` — 25.5 KB (source: `plots/lr.png`)
- `Report_paper_9model/training_diagnostics/rank08_m10-gmm-hmm-dnn/plots/wer_cer.png` — 68.5 KB (source: `plots/wer_cer.png`)
- `Report_paper_9model/training_diagnostics/rank08_m10-gmm-hmm-dnn/report.md` — 524 B (source: `report.md`)
- `Report_paper_9model/training_diagnostics/rank08_m10-gmm-hmm-dnn/test_results/test_paper.json` — 7.9 KB (source: `test_results/test_paper.json`)
- `Report_paper_9model/training_diagnostics/rank08_m10-gmm-hmm-dnn/test_results/test_summary.md` — 2.2 KB (source: `test_results/test_summary.md`)

### rank09_m09-dnn-hmm
- `Report_paper_9model/training_diagnostics/rank09_m09-dnn-hmm/config.json` — 609 B (source: `config.json`)
- `Report_paper_9model/training_diagnostics/rank09_m09-dnn-hmm/history.json` — 15.6 KB (source: `history.json`)
- `Report_paper_9model/training_diagnostics/rank09_m09-dnn-hmm/log.txt` — 33.7 KB (source: `log.txt`)
- `Report_paper_9model/training_diagnostics/rank09_m09-dnn-hmm/meta.json` — 2.5 KB (source: `meta.json`)
- `Report_paper_9model/training_diagnostics/rank09_m09-dnn-hmm/plots/accuracy.png` — 60.6 KB (source: `plots/accuracy.png`)
- `Report_paper_9model/training_diagnostics/rank09_m09-dnn-hmm/plots/gpu_mb.png` — 80.5 KB (source: `plots/gpu_mb.png`)
- `Report_paper_9model/training_diagnostics/rank09_m09-dnn-hmm/plots/loss.png` — 41.7 KB (source: `plots/loss.png`)
- `Report_paper_9model/training_diagnostics/rank09_m09-dnn-hmm/plots/lr.png` — 25.5 KB (source: `plots/lr.png`)
- `Report_paper_9model/training_diagnostics/rank09_m09-dnn-hmm/plots/wer_cer.png` — 66.8 KB (source: `plots/wer_cer.png`)
- `Report_paper_9model/training_diagnostics/rank09_m09-dnn-hmm/report.md` — 435 B (source: `report.md`)
- `Report_paper_9model/training_diagnostics/rank09_m09-dnn-hmm/test_results/test_paper.json` — 7.7 KB (source: `test_results/test_paper.json`)
- `Report_paper_9model/training_diagnostics/rank09_m09-dnn-hmm/test_results/test_summary.md` — 2.2 KB (source: `test_results/test_summary.md`)

## Skipped files

- `training_conventional/m08_hmm_gmm/runs/run_paper_20260530/checkpoints/best.pkl` — 9.8 MB — model_or_checkpoint_artifact
- `training_conventional/m08_hmm_gmm/runs/run_paper_20260530/predictions/epoch_001.json` — 1.0 KB — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m08_hmm_gmm/runs/run_paper_20260530/test_results/predictions.csv` — 3.1 MB — full_test_predictions_large_table_for_HuggingFace_or_external_artifact_storage
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/checkpoints/best.pkl` — 5.6 MB — model_or_checkpoint_artifact
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_001.json` — 603 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_002.json` — 631 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_003.json` — 668 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_004.json` — 671 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_005.json` — 696 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_006.json` — 681 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_007.json` — 702 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_008.json` — 670 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_009.json` — 715 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_010.json` — 704 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_011.json` — 665 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_012.json` — 670 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_013.json` — 657 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_014.json` — 684 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_015.json` — 663 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_016.json` — 685 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_017.json` — 672 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_018.json` — 657 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_019.json` — 672 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_020.json` — 667 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_021.json` — 658 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_022.json` — 645 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_023.json` — 657 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_024.json` — 643 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_025.json` — 641 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_026.json` — 664 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_027.json` — 652 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_028.json` — 673 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_029.json` — 650 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/predictions/epoch_030.json` — 646 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/test_results/predictions.csv` — 2.3 MB — full_test_predictions_large_table_for_HuggingFace_or_external_artifact_storage
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/checkpoints/best.pkl` — 5.6 MB — model_or_checkpoint_artifact
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_001.json` — 630 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_002.json` — 636 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_003.json` — 625 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_004.json` — 639 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_005.json` — 659 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_006.json` — 648 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_007.json` — 658 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_008.json` — 663 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_009.json` — 656 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_010.json` — 635 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_011.json` — 676 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_012.json` — 637 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_013.json` — 625 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_014.json` — 661 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_015.json` — 659 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_016.json` — 635 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_017.json` — 678 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_018.json` — 619 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_019.json` — 631 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_020.json` — 642 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_021.json` — 630 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_022.json` — 642 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_023.json` — 652 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_024.json` — 663 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_025.json` — 604 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_026.json` — 637 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_027.json` — 655 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_028.json` — 632 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_029.json` — 619 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/predictions/epoch_030.json` — 614 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/test_results/predictions.csv` — 2.3 MB — full_test_predictions_large_table_for_HuggingFace_or_external_artifact_storage
- `training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328/checkpoints/best.pth` — 28.1 MB — model_or_checkpoint_artifact
- `training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328/eval_greedy/results_vanilla.csv` — 2.9 MB — full_eval_result_csv_over_1MB_skipped_use_xlsx_or_external_storage
- `training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328/test_results/predictions.csv` — 2.1 MB — full_test_predictions_large_table_for_HuggingFace_or_external_artifact_storage
- `training_conventional/m12_vit_modified/runs/run_full_20260528_223323/checkpoints/best.pth` — 22.7 MB — model_or_checkpoint_artifact
- `training_conventional/m12_vit_modified/runs/run_full_20260528_223323/eval_greedy/results_vit.csv` — 2.9 MB — full_eval_result_csv_over_1MB_skipped_use_xlsx_or_external_storage
- `training_conventional/m12_vit_modified/runs/run_full_20260528_223323/test_results/predictions.csv` — 2.1 MB — full_test_predictions_large_table_for_HuggingFace_or_external_artifact_storage
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/checkpoints/best.pt` — 94.8 MB — model_or_checkpoint_artifact
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_001.json` — 934 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_002.json` — 858 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_003.json` — 868 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_004.json` — 860 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_005.json` — 890 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_006.json` — 877 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_007.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_008.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_009.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_010.json` — 877 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_011.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_012.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_013.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_014.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_015.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_016.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_017.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_018.json` — 870 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_019.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_020.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_021.json` — 871 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_022.json` — 870 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_023.json` — 876 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_024.json` — 870 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_025.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_026.json` — 870 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_027.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_028.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_029.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/predictions/epoch_030.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/test_results/predictions.csv` — 2.9 MB — full_test_predictions_large_table_for_HuggingFace_or_external_artifact_storage
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/checkpoints/best.pt` — 125.2 MB — model_or_checkpoint_artifact
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_001.json` — 755 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_002.json` — 841 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_003.json` — 877 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_004.json` — 864 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_005.json` — 868 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_006.json` — 868 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_007.json` — 872 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_008.json` — 875 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_009.json` — 867 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_010.json` — 868 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_011.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_012.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_013.json` — 867 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_014.json` — 863 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_015.json` — 862 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_016.json` — 867 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_017.json` — 867 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_018.json` — 870 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_019.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_020.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_021.json` — 866 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_022.json` — 866 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_023.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_024.json` — 864 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_025.json` — 867 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_026.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_027.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_028.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_029.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/predictions/epoch_030.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/test_results/predictions.csv` — 2.8 MB — full_test_predictions_large_table_for_HuggingFace_or_external_artifact_storage
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/checkpoints/best.pt` — 42.2 MB — model_or_checkpoint_artifact
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_001.json` — 835 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_002.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_003.json` — 863 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_004.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_005.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_006.json` — 866 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_007.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_008.json` — 867 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_009.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_010.json` — 866 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_011.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_012.json` — 864 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_013.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_014.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_015.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_016.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_017.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_018.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_019.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_020.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_021.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_022.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_023.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_024.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_025.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_026.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_027.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_028.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_029.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/predictions/epoch_030.json` — 865 B — per_epoch_prediction_json_not_training_plot_report
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/test_results/predictions.csv` — 2.8 MB — full_test_predictions_large_table_for_HuggingFace_or_external_artifact_storage
- `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/best_model/BEST_INFO.txt` — 259 B — model_or_checkpoint_artifact
- `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/best_model/config.json` — 1.3 KB — model_or_checkpoint_artifact
- `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/best_model/generation_config.json` — 4.5 KB — model_or_checkpoint_artifact
- `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/best_model/model.safetensors` — 922.2 MB — model_or_checkpoint_artifact
- `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/best_model/processor_config.json` — 409 B — model_or_checkpoint_artifact
- `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/best_model/tokenizer.json` — 3.7 MB — model_or_checkpoint_artifact
- `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/best_model/tokenizer_config.json` — 2.1 KB — model_or_checkpoint_artifact
- `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/predictions/epoch_001.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/predictions/epoch_002.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/predictions/epoch_003.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/predictions/epoch_004.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/predictions/epoch_005.json` — 869 B — per_epoch_prediction_json_not_training_plot_report
- `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/test_results/predictions.csv` — 2.9 MB — full_test_predictions_large_table_for_HuggingFace_or_external_artifact_storage

## Self-review / critique

- This package now covers the missing training plot folders such as `training/m07_bilstm_ctc/.../plots`.
- It intentionally avoids raw model/checkpoint files and bulky full prediction tables.
- The plots are copied from final run directories, not from old/non-final runs.
- For models m11/m12, the original scripts stored training plots at run root and evaluation summaries under `eval_greedy/`; both are included.
