# Training Summary per Paper Model (Paper Section 4.2)

## m08-hmm-gmm — HMM-GMM template classifier

- Checkpoint: `best.pkl` → best epoch 1
- Training epochs: 1
- Best train WER: 1.1687
- Test WER: 1.1687, CER: 0.8980
- Training meta:
  - Python: 3.10.18
  - Torch: 2.10.0+cu128
  - CUDA device: NVIDIA GeForce RTX 4060 Laptop GPU
  - Timestamp: 2026-05-28T18:52:49.094157
- Hyperparameters: `{"mode": "hmm_gmm", "max_train_samples": 200, "max_val_samples": 50, "hmm_states": 4, "hmm_mixtures": 2, "hmm_iters": 5, "cov_type": "diag", "dnn_hidden": 512, "dnn_layers": 4, "dnn_context": 5, "dnn_epochs": 3, "dnn_batch_size": 256, "dnn_lr": 0.001, "seed": 42}...`

## m09-dnn-hmm — DNN-HMM (hybrid)

_Status: MISSING_

## m10-gmm-hmm-dnn — GMM-HMM-DNN (3-stage)

_Status: MISSING_

## m11-vanilla-transformer — Vanilla Transformer (Vaswani 2017)

_Status: MISSING_

## m12-vit-modified-ID — ViT-modified-ID (Ratna 2026)

_Status: MISSING_

## m13-wav2letter — Wav2Letter CNN-CTC (Collobert 2016)

_Status: MISSING_

## m07-bilstm-ctc — Bi-LSTM CTC

_Status: MISSING_

## m06-conformer-ctc — Conformer-CTC (Gulati 2020)

_Status: MISSING_

## m02b-whisper-medium-ft — Whisper-medium FT (Radford 2022)

_Status: MISSING_
