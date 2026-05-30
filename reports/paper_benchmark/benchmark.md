# Paper Benchmark Report — 9-Model Comparison on Indonesian v7 Test Set

**Generated**: 2026-05-28T22:27:39.404426
**Target journal**: Data in Brief (Elsevier, ISSN 2352-3409)
**Scope**: Paper Section 5 (Results) + Table 1 + Appendix B
**Test set**: 15,376 utterances (full v7 test split)

## Status

- Paper models present: **1 / 9**
- Secondary models present: 0 / 6
- ⚠ **Missing paper models**: m09-dnn-hmm, m10-gmm-hmm-dnn, m11-vanilla-transformer, m12-vit-modified-ID, m13-wav2letter, m07-bilstm-ctc, m06-conformer-ctc, m02b-whisper-medium-ft

## Best Paper Model

- **m08-hmm-gmm** — HMM-GMM template classifier
  - WER: **1.1687**
  - CER: **0.8980**
  - User novel architecture: no

## Paper Table 1 — 9-Model Comparison (greedy decoding, no LM, full test set)

| Rank | Slot | Family | Params (M) | WER | CER | MER | WIL | SER | Wall (s) | GPU MB | Best train epoch | Status |
|-----:|------|--------|-----------:|----:|----:|----:|----:|----:|---------:|-------:|-----------------:|--------|
| 1 | `m08-hmm-gmm` | HMM-GMM template classifier | n/a | 1.1687 | 0.8980 | 0.9272 | 0.9932 | 0.9400 | 0.5 | 0 | 1 | OK |
| - | `m09-dnn-hmm` | DNN-HMM (hybrid) | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | MISSING |
| - | `m10-gmm-hmm-dnn` | GMM-HMM-DNN (3-stage) | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | MISSING |
| - | `m11-vanilla-transformer` | Vanilla Transformer (Vaswani 2017) | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | MISSING |
| - | `m12-vit-modified-ID ☆` | ViT-modified-ID (Ratna 2026) | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | MISSING |
| - | `m13-wav2letter` | Wav2Letter CNN-CTC (Collobert 2016) | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | MISSING |
| - | `m07-bilstm-ctc` | Bi-LSTM CTC | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | MISSING |
| - | `m06-conformer-ctc` | Conformer-CTC (Gulati 2020) | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | MISSING |
| - | `m02b-whisper-medium-ft` | Whisper-medium FT (Radford 2022) | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | MISSING |

☆ = User's novel architecture (Ratna 2026, this paper's first public report)

## Per-Model Hyperparameter Summary

| Model | Epochs trained | Best train epoch | Best train WER | Test WER | Test CER |
|-------|---------------:|-----------------:|--------------:|---------:|---------:|
| `m08-hmm-gmm` | 1 | 1 | 1.1687 | 1.1687 | 0.8980 |
| `m09-dnn-hmm` | n/a | n/a | n/a | n/a | n/a |
| `m10-gmm-hmm-dnn` | n/a | n/a | n/a | n/a | n/a |
| `m11-vanilla-transformer` | n/a | n/a | n/a | n/a | n/a |
| `m12-vit-modified-ID` | n/a | n/a | n/a | n/a | n/a |
| `m13-wav2letter` | n/a | n/a | n/a | n/a | n/a |
| `m07-bilstm-ctc` | n/a | n/a | n/a | n/a | n/a |
| `m06-conformer-ctc` | n/a | n/a | n/a | n/a | n/a |
| `m02b-whisper-medium-ft` | n/a | n/a | n/a | n/a | n/a |

## How AI Agent Should Read This

1. `benchmark.json` adalah single source of truth.
2. Untuk paper Section 5 (Results), gunakan `paper_models_ranked_by_wer` dan `best_paper_model`.
3. Untuk paper Table 1, gunakan field `paper_models[*].metrics` + `paper_models[*].family`.
4. Untuk paper Appendix A (sample predictions), gunakan `paper_models[*].sample_predictions`.
5. Untuk paper Section 4.2 (Experimental Setup), gunakan `paper_models[*].config` + `paper_models[*].training_meta`.
6. Setiap model punya `predictions_csv` path untuk full predictions.
7. Status `MISSING` artinya model belum di-test. Re-run testing per RUN_GUIDE.md PAPER-GRADE section.

## Files

- `benchmark.json` — master file (all data + metadata)
- `benchmark.md` — this file (human-readable)
- `benchmark_table.csv` — paper Table 1 raw data
- `paper_table.tex` — LaTeX `\input{}` ready
- `sample_predictions.md` — per-model 10 samples for Appendix
- `training_summary.md` — hyperparameters + env per-model