# Quick Reference — Hyperparameter Tables (Paper-Friendly)

> **Single-glance** version. For full per-model breakdown + recipes + commands,
> see `HYPERPARAMETER_REFERENCE.md` in this folder.

## Table 1 — Hyperparameter Concept per Family

| Family | Flag yang menambah training | Flag yang ubah model size |
|--------|------------------------------|----------------------------|
| **Whisper / wav2vec2 / MMS** (m01–m05) | `--epochs N` | `--batch-size`, `--lr`, `--gradient-checkpointing` |
| **Conformer / Bi-LSTM / CNN** (m06, m07, m13, m14) | `--epochs N` | `--hidden-size`, `--num-layers`, `--dropout` |
| **Vanilla TF + ViT-modified-ID** (m11, m12) | `--epochs N` | `--d-model`, `--num-layers`, `--ff`, `--nhead` |
| **m08 HMM-GMM** | `--hmm-iters N` ⭐ | `--hmm-states`, `--hmm-mixtures`, `--cov-type` |
| **m09 DNN-HMM** | `--dnn-epochs N` | `--dnn-hidden`, `--dnn-layers`, `--dnn-context` |
| **m10 GMM-HMM-DNN** | `--hmm-iters` + `--dnn-epochs` | semua flag HMM + DNN |

## Table 2 — Tiga Recipe Tuning

| Recipe | Tujuan | Trade-off |
|--------|--------|-----------|
| **A: Lebih akurat** | Akurasi paper-grade (full data + epoch besar + model besar) | Lebih lambat, RAM/VRAM lebih |
| **B: Lebih cepat** | Smoke / debug (200 sample / 1 ep) | WER tinggi, tapi pipeline OK |
| **C: VRAM-constrained** | RTX 4060 8 GB (`--batch-size 2 --grad-accum 8 --gradient-checkpointing`) | ~30% lebih lambat |

> Setiap recipe sudah ada copy-paste-ready command di `RUN_GUIDE.md` untuk semua 14 model.
