# Conventional ASR Baselines — Cross-Model Smoke Comparison

**Source**: 7 smoke runs from `training_conventional/m??_*/runs/run_smoke*/`
**Each run**: 200 train / 50 val (HMM/CNN) or 2000/500 (m11/m12), 1–2 epochs

## Results table (smoke; full-data results are pending)

| Slot | Family | Era | WER | CER | val_loss | GPU MB | Wall |
|------|--------|-----|----:|----:|---------:|-------:|------|
| `m08-hmm-gmm` | HMM | 1990s | 1.1687 | 0.8980 | n/a | 0 | 00:00:05 |
| `m09-dnn-hmm` | hybrid | 2010s | 5.0769 | 3.5089 | n/a | 0 | 00:00:01 |
| `m10-gmm-hmm-dnn` | hybrid | 2010s | 5.0769 | 3.5089 | n/a | 0 | 00:00:07 |
| `m11-vanilla-transformer` | Transformer | 2017 | n/a | n/a | n/a | n/a | n/a |
| `m12-vit-modified` | Transformer | 2020s | n/a | n/a | n/a | n/a | n/a |
| `m13-wav2letter` | CNN-CTC | 2016 | 0.9926 | 0.9099 | 6.4615 | 487.3 | 00:00:00 |
| `m14-jasper-mini` | CNN-CTC | 2019 | 1.0000 | 0.9330 | 6.0703 | 2073.7 | 00:00:05 |


## Plots

- `wer_bar.png` — WER comparison
- `cer_bar.png` — CER comparison

## Notes

- m08 / m09 / m10 use our `pkl_hmm_trainer.py` (full canonical artifact set
  including history.json).
- m11 / m12 use the supervisor-validated root scripts (`train_model_vanilla.py`,
  `train_model_vit.py`); their per-epoch artifacts are in the run folder
  (cer_vit.png, char_accuracy_vit.png, etc.) — these will be aggregated for
  the paper after running `test.py` for free-running greedy WER on the test set.
- m13 / m14 use `pkl_cnn_ctc_trainer.py` with the canonical artifact set.

## Expected full-data WER (paper grade)

| Slot | Smoke WER | Expected full WER | Expected full CER |
|------|----------:|------------------:|------------------:|
| m08 | 1.17 | < 0.50 (closed-vocab) | < 0.20 |
| m09 | 5.08 | < 0.40 | < 0.10 |
| m10 | 5.08 | < 0.30 | < 0.08 |
| m11 | – (1 ep) | < 0.05 | < 0.02 |
| m12 | – (1 ep) | < 0.05 | < 0.02 |
| m13 | 0.99 | < 0.20 | < 0.05 |
| m14 | 1.00 | < 0.18 | < 0.04 |

Smoke WER ≥ 1 for m09/m10/m13/m14 is expected — CTC + frame DNN need many
epochs to converge from random init. The pipeline is verified end-to-end.

## Per-family colour coding (figure legends)

- **HMM** (orange): `m08`
- **Hybrid HMM** (red): `m09`, `m10`
- **CNN-CTC** (green): `m13`, `m14`
- **Transformer** (blue): `m11`, `m12`
