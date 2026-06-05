# Training Summary per Paper Model (Paper Section 4.2)

## m08-hmm-gmm — HMM-GMM (classical)

- Checkpoint: `best.pkl` → best epoch 1
- Training epochs: 1
- Best train WER: 1.0236
- Test WER: 0.9633, CER: 0.7205
- Total training time: 03:17:11 (3.286 hours)
- Observed full-test evaluation wall time: 00:54:37 (3277.3 s)
- Parameter count: 511005 (Classical HMM-GMM numeric parameter count computed from the selected best.pkl template bank: 209 templates x (5 start probabilities + 25 transitions + 5x3x80 means + 5x3x80 diagonal covariances + 5x3 mixture weights) = 511,005. This is not a neural trainable-parameter count.)
- Training hardware provenance: WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata
- Best artifact: `training_conventional/m08_hmm_gmm/runs/run_paper_20260530/checkpoints/best.pkl`
- Evidence sources: training time `training_conventional/m08_hmm_gmm/runs/run_paper_20260530/report.md:16-17`, params `training_conventional/m08_hmm_gmm/runs/run_paper_20260530/checkpoints/best.pkl arrays; report.md:19 records 209 templates`
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
- Total training time: 03:12:11 (3.203 hours)
- Observed full-test evaluation wall time: 00:00:20 (19.8 s)
- Parameter count: 1448336 (DNN acoustic model parameters.)
- Training hardware provenance: WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata
- Best artifact: `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/checkpoints/best.pkl`
- Evidence sources: training time `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/report.md:16-17`, params `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/report.md:18`
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
- Total training time: 06:29:10 (6.486 hours)
- Observed full-test evaluation wall time: 00:00:19 (18.9 s)
- Parameter count: 1448336 (Stage-3 DNN parameters; Stage-1 trained 209 GMM-HMM templates.)
- Training hardware provenance: WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata
- Best artifact: `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/checkpoints/best.pkl`
- Evidence sources: training time `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/report.md:16-17`, params `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/report.md:18-19`
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
- Total training time: 02:38:53 (2.648 hours)
- Observed full-test evaluation wall time: 00:21:33 (1293.3 s)
- Parameter count: 4212688 (Total model parameters from torchinfo/log summary.)
- Training hardware provenance: Training log records `Using device: cuda`; exact training OS/GPU model not recorded. Full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU.
- Best artifact: `training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328/checkpoints/best.pth`
- Evidence sources: training time `training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328/Log_Run.txt:676`, params `training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328/Log_Run.txt:59`
- Training meta:
  - Python: ?
  - Torch: ?
  - CUDA device: ?
  - Timestamp: ?
- Hyperparameters: `{"epochs": 30, "batch_size": 16, "lr": 0.0005}...`

## m12-vit-modified-ID — ViT-modified-ID (proposed in this work)

- Checkpoint: `best.pth` → best epoch n/a
- Training epochs: 30
- Best train WER: n/a
- Test WER: 0.0178, CER: 0.0130
- Total training time: 03:44:58 (3.749 hours)
- Observed full-test evaluation wall time: 00:21:44 (1304.3 s)
- Parameter count: 4353248 (Total model parameters from torchinfo/log summary.)
- Training hardware provenance: Training log records `Using device: cuda`; exact training OS/GPU model not recorded. Full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU.
- Best artifact: `training_conventional/m12_vit_modified/runs/run_full_20260528_223323/checkpoints/best.pth`
- Evidence sources: training time `training_conventional/m12_vit_modified/runs/run_full_20260528_223323/Log_Run.txt:698`, params `training_conventional/m12_vit_modified/runs/run_full_20260528_223323/Log_Run.txt:58`
- Training meta:
  - Python: ?
  - Torch: ?
  - CUDA device: ?
  - Timestamp: ?
- Hyperparameters: `{"epochs": 30, "batch_size": 16, "lr": 0.0005}...`

## m13-wav2letter — Wav2Letter-style CNN-CTC (Collobert 2016)

- Checkpoint: `best.pt` → best epoch 27
- Training epochs: 30
- Best train WER: 0.0719
- Test WER: 0.0929, CER: 0.0520
- Total training time: 04:10:23 (4.173 hours)
- Observed full-test evaluation wall time: 00:00:23 (22.9 s)
- Parameter count: 24840900 (Total CNN-CTC model parameters.)
- Training hardware provenance: WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata
- Best artifact: `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/checkpoints/best.pt`
- Evidence sources: training time `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/report.md:17`, params `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/report.md:13`
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
- Total training time: 07:06:23 (7.106 hours)
- Observed full-test evaluation wall time: 00:01:10 (70.4 s)
- Parameter count: 32825659 (Total Bi-LSTM CTC model parameters.)
- Training hardware provenance: Local Linux laptop, NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM
- Best artifact: `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/checkpoints/best.pt`
- Evidence sources: training time `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/report.md:17`, params `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/report.md:14`
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
- Total training time: 06:31:49 (6.530 hours)
- Observed full-test evaluation wall time: 00:00:52 (52.5 s)
- Parameter count: 11048219 (Total Conformer-CTC model parameters.)
- Training hardware provenance: Local Linux laptop, NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM
- Best artifact: `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/checkpoints/best.pt`
- Evidence sources: training time `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/report.md:17`, params `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/report.md:14`
- Training meta:
  - Python: 3.10.16
  - Torch: 2.6.0+cu126
  - CUDA device: NVIDIA GeForce RTX 4060 Laptop GPU
  - Timestamp: 2026-06-01T21:30:50.506925
- Hyperparameters: `{"arch": "conformer", "epochs": 30, "batch_size": 4, "grad_accum": 2, "lr": 0.0003, "max_train_samples": 0, "max_val_samples": 0, "n_mels": 80, "hidden_size": 256, "num_layers": 6, "dropout": 0.1, "seed": 42, "fp16": true}...`

## m02b-whisper-small-ft — Whisper-small FT (Radford et al. 2023; arXiv 2022)

- Checkpoint: `best_model` → best epoch 5
- Training epochs: 5
- Best train WER: 0.0015
- Test WER: 0.0085, CER: 0.0019
- Total training time: 04:48:29 (4.808 hours)
- Observed full-test evaluation wall time: 01:12:43 (4363.1 s)
- Parameter count: 241734912 (Total fine-tuned Whisper-small model parameters from run report. The original Whisper paper lists small as approximately 244M parameters; this run reports the exact HF model count used here.)
- Training hardware provenance: Google Colab Linux, NVIDIA A100-SXM4-40GB GPU
- Best artifact: `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/best_model`
- Evidence sources: training time `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/report.md:24`, params `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/report.md:20`
- Training meta:
  - Python: 3.12.13
  - Torch: 2.11.0+cu128
  - CUDA device: NVIDIA A100-SXM4-40GB
  - Timestamp: 2026-06-04T00:51:15.338726
- Hyperparameters: `{"model_id": "openai/whisper-small", "epochs": 5, "batch_size": 8, "grad_accum": 4, "lr": 1e-05, "warmup_steps": 500, "max_train_samples": 0, "max_val_samples": 0, "language": "indonesian", "task": "transcribe", "gradient_checkpointing": true, "num_workers": 2, "fp16": true, "resume": null, "seed": ...`
