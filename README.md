# Indonesian ASR — 11-Class Dataset & 9-Model SOTA Benchmark

Reproducible research repository for an **Indonesian Automatic Speech Recognition (ASR)** study targeting a *Data in Brief* (Elsevier, ISSN 2352-3409) dataset publication. It contains the full training/testing/benchmark pipeline for **nine ASR systems** spanning three eras — classical HMM-GMM, neural-HMM hybrids, and modern from-scratch / pretrained neural models — evaluated under one **fair-comparison protocol** on a frozen Indonesian speech corpus.

> The heavy audio data, feature pickles, and model weights are intentionally **not** tracked in git (see `.gitignore`). This repo hosts the **code, configs, per-epoch logs, plots, and paper-grade reports** needed to reproduce and audit every result.

---

## 1. What's in this study

- **Corpus (v7)**: Indonesian read/template speech derived from 209 base sentences.
  - Splits (frozen): **train 71,792 / dev 15,376 / test 15,376** utterances.
  - Features: **80-bin log-mel**, 25 ms window / 10 ms hop, per-utterance CMVN.
  - Tokenizer: SentencePiece character model (`spm_v7_char`).
- **9 paper models** benchmarked head-to-head with **greedy decoding, no language model**, metrics via `jiwer` (WER/CER/MER/WIL/SER).

| Slot | Model | Family / era | Train budget |
|------|-------|--------------|:------------:|
| m08 | HMM-GMM | classical template classifier (1990s) | 30 EM iters |
| m09 | DNN-HMM | hybrid, CTC acoustic model (2010s) | 30 ep |
| m10 | GMM-HMM-DNN | 3-stage hybrid (2010s) | 30 EM + 30 ep |
| m11 | Vanilla Transformer | from-scratch enc-dec (Vaswani 2017) | 30 ep |
| **m12** | **ViT-modified-ID ★** | **novel architecture (this paper)** | 30 ep (+200 ep extended) |
| m07 | Bi-LSTM CTC | from-scratch RNN-CTC | 30 ep |
| m06 | Conformer-CTC | from-scratch conv+attn (Gulati 2020) | 30 ep |
| m13 | Wav2Letter | from-scratch CNN-CTC (Collobert 2016) | 30 ep |
| m02b | Whisper-medium FT | pretrained fine-tune (Radford 2022) | 5 ep |

★ = user's novel architecture (Ratna 2026, this paper's first public report).

---

## 2. Fair-comparison protocol (Approach C)

The core methodological decision is documented and defensible for reviewers:

> **Keunggulan model harus dapat diatribusikan ke arsitekturnya, bukan ke anggaran pelatihan yang tidak setara.** Yang diseragamkan adalah faktor **non-arsitektur**; anggaran pelatihan ditetapkan **per keluarga arsitektur** dengan justifikasi konvensional.

- **Seragam untuk semua model**: split data, fitur+CMVN, tokenizer, dekoding greedy tanpa LM, metrik, seed (42), dan **pemilihan checkpoint best-on-validation**.
- **Boleh berbeda (per keluarga, dijustifikasi)**: jumlah epoch & LR. Pretrained FT = 5 epoch (hindari catastrophic forgetting); from-scratch = 30 epoch; HMM = 30 EM iter.
- **Pagar anti-asimetri**: tidak ada model lemah diberi anggaran ekstra atau model kuat ditahan. m11 dan m12 memakai konfigurasi identik agar selisihnya murni arsitektur.

Rasional lengkap + prosa siap-tempel untuk §4.2 paper:
- `reports/hyperparameter_reference/FAIR_COMPARISON_PROTOCOL.md`
- `training_conventional/reports/fairness_protocol_C_FINAL.md`
- `training_conventional/reports/hyperparameter_fairness_decision.md`

---

## 3. Repository layout

```
Paper_Datatset_SOTA/
├── RUN_GUIDE.md                 # ★ MASTER guide: preflight, 9 paper commands, testing, aggregation
├── REPLAY_GUIDE.md              # re-plot to any journal style without retraining
├── training_conventional/       # m08–m14 (HMM family + from-scratch conventional)
│   ├── common/                  # shared trainers/testers (pkl_hmm_*, pkl_cnn_ctc_*, test_helper, utils)
│   ├── m08_hmm_gmm/ … m14_jasper_cnn/   # per-model train.py + test.py wrappers + runs/
│   └── reports/                 # fairness + pipeline audit reports
├── training/                    # m01–m07 + m02b (modern/pretrained); m06/m07 here
│   ├── common/                  # from_scratch_trainer, whisper_trainer, test_helper
│   └── m0X_*/                   # per-model wrappers + runs/
├── aggregate_paper_test_results.py   # 9 test JSONs → reports/paper_benchmark/{json,md,csv,tex}
├── aggregate_all_models.py           # full comparison table
├── replot_all.py / replot_compare.py # Data-in-Brief compliant figures
└── reports/                     # paper_benchmark/, hyperparameter_reference/, figures
```

Large excluded paths (regenerated locally): `Dataset_Ori/`, `Processed_Balanced19*/`, `*/data_pkl/`, `*/data_final/`, `*/checkpoints/`, `*.wav/.pt/.pth/.pkl/.safetensors`.

---

## 4. Reproduce (paper-grade)

Full, copy-paste commands live in **`RUN_GUIDE.md` → section "📖 PAPER-GRADE FAIR COMPARISON"** (P1–P9). Summary:

```bash
# 0. Environment + feature pickles (once)
source ~/miniconda3/etc/profile.d/conda.sh && conda activate torch-gpu
python3 training_conventional/common/spm_builder.py
python3 training_conventional/common/feature_builder.py

# 1. Train each of the 9 models (run in SEPARATE terminals, not in an agent)
python3 training_conventional/m08_hmm_gmm/train.py --hmm-iters 30 --hmm-states 5 --hmm-mixtures 3 --seed 42
python3 training_conventional/m09_dnn_hmm/train.py --dnn-epochs 30 --dnn-batch-size 12000 --dnn-lr 1e-3 --seed 42
# … P-3 … P-9 (see RUN_GUIDE.md)

# 2. Test each model → test_paper.json
python3 training_conventional/m08_hmm_gmm/test.py   # … all 9

# 3. Aggregate → paper Table 1 + figures
python3 aggregate_paper_test_results.py
python3 replot_all.py --style data_in_brief --pattern "run_paper_*" --formats pdf png
```

Each `runs/run_paper_*/` is a reproducibility bundle: `config.json`, `meta.json` (env snapshot), `history.json` (per-epoch WER/CER/loss/lr/gpu/throughput), `log.txt`, `predictions/`, `checkpoints/best*`.

---

## 5. Results status

- Benchmark single-source-of-truth: `reports/paper_benchmark/benchmark.json`.
- **Confirmed** (full test split): m08 HMM-GMM **WER 1.1687 / CER 0.8980** (closed-vocabulary baseline floor — see analysis below).
- **Confirmed (validation, best epoch)**: m07 Bi-LSTM **WER 0.0262 @ep19**, m06 Conformer **WER 0.0381 @ep16**.
- Remaining models: train + test pending; aggregator reports `n_paper_models_present/9` and gates on completeness.

Why HMM-GMM scores WER > 1 (and why that motivates the modern models) is analysed in `training_conventional/reports/m08_hmm_gmm_paper_analysis.md` (it is a low-capacity generative limitation, **not** a closed-vocabulary floor — test templates are 100% covered by train).

---

## 6. Pipeline integrity (audited)

The test→aggregate chain is audited end-to-end (`training_conventional/reports/pipeline_audit_test_aggregate.md`). Notable fixes:
- m10 artifact now stores DNN `model_state` (previously missing → random-init at test).
- m09/m10 artifacts use **best-on-validation** weights (from `best.pt`).
- `find_best_checkpoint` picks the best-WER epoch from `history.json` when only per-epoch checkpoints exist.
- The aggregator is authoritative for `family`/`model_id` labels (no drift into Table 1).

---

## 7. Notes & scope

- Run all training in dedicated terminals; large audio/processed trees must not be recursively scanned by agents (see `AGENTS.md`).
- This repository accompanies a dataset-focused manuscript; raw audio release, if any, follows a separate data-hosting route (e.g. Zenodo / HF Datasets), not git.
- License/authorship: research artifact (Ratna 2026). The ViT-modified-ID architecture is first reported in this work.
