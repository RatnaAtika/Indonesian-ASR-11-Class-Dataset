# Final 17-Architecture ASR Comparison (Indonesian Corpus v7)

**Source**: aggregated from `training/` + `training_conventional/` full runs.

> ⚠ **17 model(s) missing or incomplete**: m01-whisper-tiny, m02-whisper-small ★ (run dir exists but no metrics found), m03-w2v2-xlsr-300m, m04-cahya-w2v2-id, m05-mms-1b-adapter, m06-conformer-ctc, m07-bilstm-ctc, zs1-whisper-large-v3, zs2-whisper-medium, zs3-mms-1b-all, m08-hmm-gmm, m09-dnn-hmm, m10-gmm-hmm-dnn, m11-vanilla-transformer, m12-vit-modified-ID ★, m13-wav2letter, m14-jasper-mini

## Results table

| Slot | Family | Era | Params (M) | Notes | WER | CER | Train Acc | Val Acc | Run dir |
|------|--------|-----|-----------:|-------|----:|----:|----------:|--------:|---------|
| `m01-whisper-tiny` | Whisper | 2022 | 38 | FT | n/a | n/a | n/a | n/a | `MISSING` |
| `m02-whisper-small ★` | Whisper | 2022 | 244 | FT primary | n/a | n/a | n/a | n/a | `m02_whisper_small/runs/run_full_20260524` |
| `m03-w2v2-xlsr-300m` | wav2vec2 | 2021 | 315 | FT | n/a | n/a | n/a | n/a | `MISSING` |
| `m04-cahya-w2v2-id` | wav2vec2 | 2021 | 315 | FT (ID-pretrained) | n/a | n/a | n/a | n/a | `MISSING` |
| `m05-mms-1b-adapter` | MMS | 2023 | 965 | FT adapter (~3M trainable) | n/a | n/a | n/a | n/a | `MISSING` |
| `m06-conformer-ctc` | CNN-CTC | 2020 | 6.6 | from-scratch | n/a | n/a | n/a | n/a | `MISSING` |
| `m07-bilstm-ctc` | Bi-LSTM | 2014 | 6.6 | from-scratch | n/a | n/a | n/a | n/a | `MISSING` |
| `zs1-whisper-large-v3` | Whisper | 2023 | 1543 | zero-shot | n/a | n/a | n/a | n/a | `MISSING` |
| `zs2-whisper-medium` | Whisper | 2022 | 764 | zero-shot | n/a | n/a | n/a | n/a | `MISSING` |
| `zs3-mms-1b-all` | MMS | 2023 | 965 | zero-shot | n/a | n/a | n/a | n/a | `MISSING` |
| `m08-hmm-gmm` | HMM | 1990s | 0.01 | template classifier | n/a | n/a | n/a | n/a | `MISSING` |
| `m09-dnn-hmm` | Hybrid | 2010s | 3.7 | linear-init alignment | n/a | n/a | n/a | n/a | `MISSING` |
| `m10-gmm-hmm-dnn` | Hybrid | 2010s | 3.7 | 3-stage | n/a | n/a | n/a | n/a | `MISSING` |
| `m11-vanilla-transformer` | Transformer | 2017 | 3.5 | Vaswani 2017 ref | n/a | n/a | n/a | n/a | `MISSING` |
| `m12-vit-modified-ID ★` | Transformer-novel | 2026 | 3.5 | USER'S NOVEL ARCH (unpublished) | n/a | n/a | n/a | n/a | `MISSING` |
| `m13-wav2letter` | CNN-CTC | 2016 | 7.0 | from-scratch | n/a | n/a | n/a | n/a | `MISSING` |
| `m14-jasper-mini` | CNN-CTC | 2019 | 28.0 | from-scratch | n/a | n/a | n/a | n/a | `MISSING` |

## Plots
- `wer_bar_all17.png` — single bar chart of all 17 systems
- `wer_vs_params.png` — WER vs parameter count scatter
- `era_timeline.png` — WER by publication-era group
- `family_summary.png` — grouped bar by architectural family

## LaTeX
- `paper_table.tex` — paper Table 1, ready to `\input{}`

## Honest disclosure
1. **m12 ViT-modified-ID** is the user's own novel architecture (Ratna 2026)
   developed for Indonesian end-to-end limited-vocabulary ASR.
   **Not yet published** — this paper is its first public report.
2. **m08 (HMM-GMM)** is a closed-vocabulary template classifier
   (209 templates), not a free-form ASR system.
3. **m11 (Vanilla Transformer)** is the Vaswani 2017 reference baseline
   using the supervisor-validated root code, kept verbatim.
4. **132 synthetic Edge-TTS files (0.129%)** are present in the train
   set; only 2 (0.013%) in test. Disclosed at every level.
