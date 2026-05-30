# Cross-Model Smoke Comparison

**Source**: 10 smoke runs (7 fine-tunes + 3 zero-shot baselines)
**Each run**: 30 train / 15 val (FT) or 30 test (zero-shot), 1–2 epochs

## Results Table

| Model | Mode | Family | WER | CER | MER | WIL | val_loss | GPU MB | Time |
|-------|------|--------|----:|----:|----:|----:|---------:|-------:|------|
| `m01-whisper-tiny` | FT | encoder-decoder | 0.5404 | 0.1248 | 0.5058 | 0.7345 | 2.4082 | 1093 | 00:00:07 |
| `m02-whisper-small` | FT★ | encoder-decoder | 0.1653 | 0.0286 | 0.1626 | 0.2872 | 2.0426 | 5812 | 00:00:10 |
| `m03-w2v2-xlsr-300m` | FT | CTC | 1.0000 | 0.9834 | 1.0000 | 1.0000 | 8.5305 | 5640 | 00:00:06 |
| `m04-cahya-w2v2-id` | FT | CTC | 0.3967 | 0.0820 | 0.3529 | 0.5259 | 0.3809 | 5436 | 00:00:04 |
| `m05-mms-1b-adapter` | FT-adapter | CTC | 1.0248 | 1.8647 | 1.0000 | 1.0000 | 8.6890 | 6859 | 00:00:10 |
| `m06-conformer-ctc` | scratch | CTC | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 2.9233 | 348 | 00:00:03 |
| `m07-bilstm-ctc` | scratch | CTC | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 4.9673 | 240 | 00:00:01 |
| `zs-whisper-medium` | zero-shot | encoder-decoder | 0.1557 | 0.0345 | 0.1557 | 0.2843 | n/a | 1618 | 00:00:16 |
| `zs-whisper-large-v3` | zero-shot | encoder-decoder | 0.1475 | 0.0307 | 0.1475 | 0.2703 | n/a | 3202 | 00:00:25 |
| `zs-mms-1b-all` | zero-shot | CTC | 0.3361 | 0.0668 | 0.3333 | 0.5482 | n/a | 3900 | 00:00:03 |


## Plots

- `wer_bar.png` — WER across all 10 runs
- `cer_bar.png` — CER across all 10 runs
- `gpu_bar.png` — Peak GPU memory across all 10 runs (RTX 4060 8 GB ceiling marked)

## Interpretation

### Fine-tunes (after 1 epoch / 30 samples)
- **m02 Whisper-small (PRIMARY)**: WER 0.1653, CER 0.0286 — best FT result on smoke
- **m04 cahya-w2v2-id**: WER 0.397, CER 0.082 — second best, fast convergence due to ID pretraining
- **m01 Whisper-tiny**: WER 0.540 — limited capacity, still works
- **m03 / m05**: WER ≈ 1.0 — fresh CTC heads need many epochs to align
- **m06 / m07 (scratch)**: WER = 1.0 expected after 2 epochs; need ≥30 epochs for paper

### Zero-shot baselines
- **Whisper-large-v3**: WER 0.148, CER 0.031 — strongest zero-shot, even out-of-the-box
- **Whisper-medium**: WER 0.156, CER 0.034 — close behind, half the params
- **MMS-1B-all (ind)**: WER 0.336, CER 0.067 — middle tier

### GPU usage (RTX 4060 8 GB ceiling)
All FT models stay below 7 GB peak. m05 (MMS-1B adapter) is the most VRAM-heavy at 6.9 GB.
m06 / m07 (from-scratch) use only 0.2–0.3 GB; could batch×4 on full dataset.

## Paper expectations (full-run, after 3–5 epochs)
| Model | Expected WER | Expected CER |
|-------|-------------:|-------------:|
| m02 Whisper-small | < 0.10 | < 0.025 |
| m04 cahya-w2v2-id | < 0.15 | < 0.04 |
| m03 w2v2-XLS-R-300M | < 0.20 | < 0.05 |
| m05 MMS-1B-adapter | < 0.18 | < 0.04 |
| m01 Whisper-tiny | < 0.25 | < 0.07 |
| m06 Conformer-CTC (30 epochs) | < 0.30 | < 0.10 |
| m07 Bi-LSTM CTC (30 epochs) | < 0.40 | < 0.13 |

Zero-shot stays as-is (no FT) for paper baseline rows.
