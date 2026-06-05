# Paper Benchmark Report — 9-Model Comparison on Indonesian v7 Test Set

**Generated**: 2026-06-05T08:10:36.527899
**Target journal**: Data in Brief (Elsevier, ISSN 2352-3409)
**Scope**: Paper Section 5 (Results) + Table 1 + Appendix B
**Test set**: 15,376 utterances (full v7 test split)

## Status

- Paper models present: **9 / 9**
- Secondary models present: 0 / 7

## Best Paper Model

- **m02b-whisper-small-ft** — Whisper-small FT (Radford et al. 2023; arXiv 2022)
  - WER: **0.0085**
  - CER: **0.0019**
  - User novel architecture: no

## Paper Table 1 — 9-Model Comparison (greedy decoding, no LM, full test set)

| Rank | Slot | Family | WER | CER | MER | WIL | SER | Train time | Test wall | Params (M) | Train hardware | Best epoch | Status |
|-----:|------|--------|----:|----:|----:|----:|----:|----------:|----------:|-----------:|----------------|----------:|--------|
| 1 | `m02b-whisper-small-ft` | Whisper-small FT (Radford et al. 2023; arXiv 2022) | 0.0085 | 0.0019 | 0.0085 | 0.0130 | 0.0390 | 04:48:29 | 4363.1 s | 241.735 | Google Colab Linux, NVIDIA A100-SXM4-40GB GPU | 5 | OK |
| 2 | `m06-conformer-ctc` | Conformer-CTC (Gulati 2020) | 0.0119 | 0.0043 | 0.0119 | 0.0205 | 0.0598 | 06:31:49 | 52.5 s | 11.048 | Local Linux laptop, NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM | 29 | OK |
| 3 | `m12-vit-modified-ID ☆` | ViT-modified-ID (proposed in this work) | 0.0178 | 0.0130 | 0.0177 | 0.0315 | 0.0184 | 03:44:58 | 1304.3 s | 4.353 | Training log records `Using device: cuda`; exact training OS/GPU model not recorded. Full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU. | n/a | OK |
| 4 | `m07-bilstm-ctc` | Bi-LSTM CTC | 0.0401 | 0.0132 | 0.0400 | 0.0721 | 0.1516 | 07:06:23 | 70.4 s | 32.826 | Local Linux laptop, NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM | 30 | OK |
| 5 | `m11-vanilla-transformer` | Vanilla Transformer (Vaswani 2017) | 0.0439 | 0.0327 | 0.0438 | 0.0774 | 0.0454 | 02:38:53 | 1293.3 s | 4.213 | Training log records `Using device: cuda`; exact training OS/GPU model not recorded. Full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU. | n/a | OK |
| 6 | `m13-wav2letter` | Wav2Letter-style CNN-CTC (Collobert 2016) | 0.0929 | 0.0520 | 0.0920 | 0.1524 | 0.2822 | 04:10:23 | 22.9 s | 24.841 | WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata | 27 | OK |
| 7 | `m08-hmm-gmm` | HMM-GMM (classical) | 0.9633 | 0.7205 | 0.8789 | 0.9822 | 0.9192 | 03:17:11 | 3277.3 s | 0.511 | WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata | 1 | OK |
| 8 | `m10-gmm-hmm-dnn` | GMM-HMM-DNN (3-stage) | 0.9703 | 0.8516 | 0.9690 | 0.9965 | 1.0000 | 06:29:10 | 18.9 s | 1.448 | WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata | 15 | OK |
| 9 | `m09-dnn-hmm` | DNN-HMM (hybrid) | 0.9708 | 0.8437 | 0.9693 | 0.9967 | 1.0000 | 03:12:11 | 19.8 s | 1.448 | WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata | 12 | OK |

☆ = User's proposed/novel architecture in this work (no external citation claimed).

## Per-Model Hyperparameter Summary

| Model | Epochs trained | Best train epoch | Best train WER | Test WER | Test CER |
|-------|---------------:|-----------------:|--------------:|---------:|---------:|
| `m08-hmm-gmm` | 1 | 1 | 1.0236 | 0.9633 | 0.7205 |
| `m09-dnn-hmm` | 30 | 12 | 0.9717 | 0.9708 | 0.8437 |
| `m10-gmm-hmm-dnn` | 30 | 15 | 0.9783 | 0.9703 | 0.8516 |
| `m11-vanilla-transformer` | 30 | n/a | n/a | 0.0439 | 0.0327 |
| `m12-vit-modified-ID` | 30 | n/a | n/a | 0.0178 | 0.0130 |
| `m13-wav2letter` | 30 | 27 | 0.0719 | 0.0929 | 0.0520 |
| `m07-bilstm-ctc` | 30 | 30 | 0.0241 | 0.0401 | 0.0132 |
| `m06-conformer-ctc` | 30 | 29 | 0.0084 | 0.0119 | 0.0043 |
| `m02b-whisper-small-ft` | 5 | 5 | 0.0015 | 0.0085 | 0.0019 |

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