# Cross-check report: `model_artifacts` vs `training_diagnostics`

Status: **passed after one corrective alignment**.

## Scope

This cross-check verifies that the training diagnostics package is consistent with the final model report package in:

- `Report_paper_9model/model_artifacts/`
- `Report_paper_9model/training_diagnostics/`
- `Report_paper_9model/benchmark/benchmark.json`

The goal is to ensure that training plots/reports copied into `training_diagnostics/` come from the same final runs used by the 9-model benchmark and model-artifact package.

## Remote state checked

- Local `HEAD`: `3e82720` before corrective alignment.
- `origin/main`: `3e82720` before corrective alignment.
- Remote HEAD was reachable and matched local before this check.

## Mapping checks

Verified 9/9 model IDs are consistent across:

1. `benchmark/benchmark.json` `paper_models[*]`
2. `model_artifacts/artifact_index.json`
3. each `model_artifacts/rank*/metadata.json`
4. `training_diagnostics/training_diagnostics_manifest.json`

| Artifact folder | Model ID | Final run source |
|---|---|---|
| `rank01_m02b-whisper-small-ft` | `m02b-whisper-small-ft` | `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact` |
| `rank02_m06-conformer-ctc` | `m06-conformer-ctc` | `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux` |
| `rank03_m12-vit-modified-ID` | `m12-vit-modified-ID` | `training_conventional/m12_vit_modified/runs/run_full_20260528_223323` |
| `rank04_m07-bilstm-ctc` | `m07-bilstm-ctc` | `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux` |
| `rank05_m11-vanilla-transformer` | `m11-vanilla-transformer` | `training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328` |
| `rank06_m13-wav2letter` | `m13-wav2letter` | `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637` |
| `rank07_m08-hmm-gmm` | `m08-hmm-gmm` | `training_conventional/m08_hmm_gmm/runs/run_paper_20260530` |
| `rank08_m10-gmm-hmm-dnn` | `m10-gmm-hmm-dnn` | `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736` |
| `rank09_m09-dnn-hmm` | `m09-dnn-hmm` | `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634` |

Note: m02b uses a logical path under `training/...` that resolves through a symlink to `Colab_ASR_A100_Training/results/...`. This is the same physical final run; the logical path is the one used by `benchmark.json` and metadata.

## Corrective alignment performed

Initial byte-level comparison found 6 non-material mismatches between overlapping `model_artifacts/*/run_outputs` files and `training_diagnostics/*` files:

- `rank07_m08-hmm-gmm/history.json`
- `rank07_m08-hmm-gmm/meta.json`
- `rank08_m10-gmm-hmm-dnn/history.json`
- `rank08_m10-gmm-hmm-dnn/meta.json`
- `rank09_m09-dnn-hmm/history.json`
- `rank09_m09-dnn-hmm/meta.json`

Cause: newline/EOF normalization differences introduced during packaging; content was semantically the same but byte sizes differed by one byte in each file.

Action: replaced the 6 `training_diagnostics` copies with the exact corresponding `model_artifacts/run_outputs` bytes and regenerated:

- `training_diagnostics_manifest.json`
- `training_diagnostics_files.csv`

After alignment:

- Exact byte matches between overlapping `model_artifacts/run_outputs` and `training_diagnostics`: **60**
- Expected skips, mostly full `predictions.csv`: **10**
- Remaining mismatches: **0**
- Warnings: **0**

## Plot/report coverage checks

Verified required diagnostic plots or equivalent training/eval plots for 9/9 models.

Examples:

- m07 BiLSTM-CTC includes final-run plots from `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/plots/`.
- m06, m07, m08, m09, m10, m13, and m02b include `plots/loss.png` and `plots/wer_cer.png`.
- m11 includes `training_val_loss.png`, `cer.png`, and `eval_greedy/summary_vanilla.png`.
- m12 includes `training_val_loss_vit.png`, `cer_vit.png`, and `eval_greedy/summary_vit.png`.

## Safety checks

Verified:

- Included diagnostics: **120 files / 4.3 MB**
- Skipped artifacts: **182 files / 1.3 GB**
- Skipped full `test_results/predictions.csv`: **9/9**
- No checkpoint/model file included (`.pt`, `.pth`, `.pkl`, `.safetensors`, `.bin`, `.ckpt`, `.h5`, `.keras`).
- No actual `checkpoints/` or `best_model/` path included in `training_diagnostics/`.
- No included file > 10 MB.
- No hardlink sharing between source training run files and package files.

## Verification commands passed

```bash
python3 tools_verify_training_diagnostics_package.py
python3 tools_verify_report_model_artifacts.py
python3 tools_verify_report_readability.py
```

## Conclusion

The `Report_paper_9model/training_diagnostics/` package is now consistent with the final 9-model benchmark and `model_artifacts` package. The only issue found was byte-level newline drift in 6 small JSON metadata/history files, and it has been corrected. The diagnostic plots and reports are sourced from the same final run directories used by the paper benchmark.
