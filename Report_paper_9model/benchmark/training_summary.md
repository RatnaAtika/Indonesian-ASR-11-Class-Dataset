# Training Summary per Paper Model (Paper Section 4.2)

## m08-hmm-gmm — HMM-GMM (classical)

- Checkpoint: `best.pkl` → best epoch 1
- Training epochs: 1
- Best train WER: 1.0236
- Test WER: 0.9633, CER: 0.7205
- Training meta:
  - Python: 3.10.18
  - Torch: 2.10.0+cu128
  - CUDA device: NVIDIA GeForce RTX 4060 Laptop GPU
  - Timestamp: 2026-05-30T09:00:09.067776
- Hyperparameters: `{"mode": "hmm_gmm", "max_train_samples": 0, "max_val_samples": 0, "hmm_states": 5, "hmm_mixtures": 3, "hmm_iters": 30, "cov_type": "diag", "dnn_hidden": 512, "dnn_layers": 4, "dnn_context": 5, "dnn_epochs": 3, "dnn_batch_size": 256, "dnn_lr": 0.001, "seed": 42}...`

## m09-dnn-hmm — DNN-HMM (hybrid)

- Checkpoint: `best.pkl` → best epoch 12
- Training epochs: 30
- Best train WER: 0.9717
- Test WER: 0.9708, CER: 0.8437
- Training meta:
  - Python: 3.10.18
  - Torch: 2.10.0+cu128
  - CUDA device: NVIDIA GeForce RTX 4060 Laptop GPU
  - Timestamp: 2026-05-30T13:36:45.969267
- Hyperparameters: `{"mode": "dnn_hmm", "max_train_samples": 0, "max_val_samples": 0, "hmm_states": 5, "hmm_mixtures": 2, "hmm_iters": 10, "cov_type": "diag", "dnn_hidden": 512, "dnn_layers": 4, "dnn_context": 5, "dnn_epochs": 30, "dnn_batch_size": 12000, "dnn_lr": 0.001, "seed": 42}...`

## m10-gmm-hmm-dnn — GMM-HMM-DNN (3-stage)

- Checkpoint: `best.pkl` → best epoch 15
- Training epochs: 30
- Best train WER: 0.9783
- Test WER: 0.9703, CER: 0.8516
- Training meta:
  - Python: 3.10.18
  - Torch: 2.10.0+cu128
  - CUDA device: NVIDIA GeForce RTX 4060 Laptop GPU
  - Timestamp: 2026-05-31T07:17:45.519344
- Hyperparameters: `{"mode": "gmm_hmm_dnn", "max_train_samples": 0, "max_val_samples": 0, "hmm_states": 5, "hmm_mixtures": 3, "hmm_iters": 30, "cov_type": "diag", "dnn_hidden": 512, "dnn_layers": 4, "dnn_context": 5, "dnn_epochs": 30, "dnn_batch_size": 12000, "dnn_lr": 0.001, "seed": 42}...`

## m11-vanilla-transformer — Vanilla Transformer (Vaswani 2017)

- Checkpoint: `best.pth` → best epoch n/a
- Training epochs: 30
- Best train WER: n/a
- Test WER: 0.0439, CER: 0.0327
- Training meta:
  - Python: ?
  - Torch: ?
  - CUDA device: ?
  - Timestamp: ?
- Hyperparameters: `{"epochs": 30, "batch_size": 16, "lr": 0.0005}...`

## m12-vit-modified-ID — ViT-modified-ID (Ratna 2026)

- Checkpoint: `best.pth` → best epoch n/a
- Training epochs: 30
- Best train WER: n/a
- Test WER: 0.0178, CER: 0.0130
- Training meta:
  - Python: ?
  - Torch: ?
  - CUDA device: ?
  - Timestamp: ?
- Hyperparameters: `{"epochs": 30, "batch_size": 16, "lr": 0.0005}...`

## m13-wav2letter — Wav2Letter CNN-CTC (Collobert 2016)

- Checkpoint: `best.pt` → best epoch 27
- Training epochs: 30
- Best train WER: 0.0719
- Test WER: 0.0929, CER: 0.0520
- Training meta:
  - Python: 3.10.18
  - Torch: 2.10.0+cu128
  - CUDA device: NVIDIA GeForce RTX 4060 Laptop GPU
  - Timestamp: 2026-05-31T23:06:37.376699
- Hyperparameters: `{"arch": "wav2letter", "epochs": 30, "batch_size": 16, "lr": 0.0003, "warmup_pct": 0.1, "max_train_samples": 0, "max_val_samples": 0, "input_dim": 80, "dropout": 0.1, "seed": 42, "fp16": true, "grad_clip": 5.0}...`

## m07-bilstm-ctc — Bi-LSTM CTC

- Checkpoint: `best.pt` → best epoch 30
- Training epochs: 30
- Best train WER: 0.0241
- Test WER: 0.0401, CER: 0.0132
- Training meta:
  - Python: 3.10.16
  - Torch: 2.6.0+cu126
  - CUDA device: NVIDIA GeForce RTX 4060 Laptop GPU
  - Timestamp: 2026-06-02T13:38:16.774659
- Hyperparameters: `{"arch": "bilstm", "epochs": 30, "batch_size": 8, "grad_accum": 2, "lr": 0.0003, "max_train_samples": 0, "max_val_samples": 0, "n_mels": 80, "hidden_size": 512, "num_layers": 5, "dropout": 0.1, "seed": 42, "fp16": true}...`

## m06-conformer-ctc — Conformer-CTC (Gulati 2020)

- Checkpoint: `best.pt` → best epoch 29
- Training epochs: 30
- Best train WER: 0.0084
- Test WER: 0.0119, CER: 0.0043
- Training meta:
  - Python: 3.10.16
  - Torch: 2.6.0+cu126
  - CUDA device: NVIDIA GeForce RTX 4060 Laptop GPU
  - Timestamp: 2026-06-01T21:30:50.506925
- Hyperparameters: `{"arch": "conformer", "epochs": 30, "batch_size": 4, "grad_accum": 2, "lr": 0.0003, "max_train_samples": 0, "max_val_samples": 0, "n_mels": 80, "hidden_size": 256, "num_layers": 6, "dropout": 0.1, "seed": 42, "fp16": true}...`

## m02b-whisper-small-ft — Whisper-small FT (Radford 2022)

- Checkpoint: `best_model` → best epoch 5
- Training epochs: 5
- Best train WER: 0.0015
- Test WER: 0.0085, CER: 0.0019
- Training meta:
  - Python: 3.12.13
  - Torch: 2.11.0+cu128
  - CUDA device: NVIDIA A100-SXM4-40GB
  - Timestamp: 2026-06-04T00:51:15.338726
- Hyperparameters: `{"model_id": "openai/whisper-small", "epochs": 5, "batch_size": 8, "grad_accum": 4, "lr": 1e-05, "warmup_steps": 500, "max_train_samples": 0, "max_val_samples": 0, "language": "indonesian", "task": "transcribe", "gradient_checkpointing": true, "num_workers": 2, "fp16": true, "resume": null, "seed": ...`
