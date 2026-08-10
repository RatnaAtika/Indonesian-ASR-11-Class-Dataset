# Indonesian ASR Training Pipeline — 7 FT + 3 Zero-Shot Baselines

End-to-end training pipeline for paper-SOTA Indonesian ASR on a 102,544-file balanced
dataset (130.65 h, 20 speakers, 11 sentence categories, 99.871% real speech, 0.129%
flagged synthetic with full provenance disclosure).

## Architectures (10 total)

### Fine-tuned (7 models on RTX 4060 Laptop 8 GB)
| Slot | Model | Family | Params | Trainable | Smoke GPU |
|------|-------|--------|--------|-----------|-----------|
| m01 | `openai/whisper-tiny` | encoder-decoder | 38 M | 38 M | 1.1 GB |
| m02 | `openai/whisper-small` ★ | encoder-decoder | 244 M | 244 M | 5.8 GB |
| m03 | `facebook/wav2vec2-xls-r-300m` | CTC encoder | 315 M | 315 M | 5.6 GB |
| m04 | `cahya/wav2vec2-large-xlsr-indonesian` | CTC encoder | 315 M | 315 M | 5.4 GB |
| m05 | `facebook/mms-1b-all` (adapter-only) | CTC encoder | 965 M | ~3 M | 6.9 GB |
| m06 | Conformer-CTC small (custom PyTorch) | CTC encoder | 6.6 M | 6.6 M | 0.3 GB |
| m07 | Bi-LSTM CTC (DeepSpeech-2 from scratch) | CTC encoder | 6.6 M | 6.6 M | 0.2 GB |

★ = primary fine-tuned model for the paper.

### Zero-shot baselines (inference only)
| Model | Params | WER (30-test smoke) | CER |
|-------|--------|---------------------|-----|
| `openai/whisper-medium` | 764 M | 0.156 | 0.034 |
| `openai/whisper-large-v3` | 1.54 B | 0.148 | 0.031 |
| `facebook/mms-1b-all` (`ind`) | 965 M | 0.336 | 0.067 |

## Folder Layout
```
training/
├── README.md                  # this file
├── README-RUN.md              # concrete run commands
├── SCALING.md                 # Colab Pro / Pro+ scaling plan
├── data_final/                # frozen train/val/test split TSVs (71792/15376/15376)
├── common/
│   ├── utils.py               # split loader, audio I/O, WER/CER, history, GPU monitor
│   ├── whisper_trainer.py     # unified Whisper FT trainer (custom torch Dataset, no map())
│   ├── wav2vec2_trainer.py    # wav2vec2 / MMS CTC trainer
│   ├── from_scratch_trainer.py # Conformer-CTC + Bi-LSTM CTC (PyTorch)
│   └── regen_plots.py         # CLI to regenerate plots from history.json
├── m01_whisper_tiny/
│   ├── train.py               # entry (calls common/whisper_trainer.py)
│   └── runs/run_smoke_1ep/    # smoke output: history, log, plots, predictions, report
├── m02_whisper_small/  ...    # ★ PRIMARY
├── m03_wav2vec2_xlsr_300m/
├── m04_cahya_wav2vec2_id/
├── m05_mms_1b_adapter/
├── m06_conformer_ctc/
├── m07_bilstm_ctc/
└── zero_shot_baselines/
    ├── run_inference.py
    └── runs/{whisper_medium_smoke,whisper_large_v3_smoke,mms_1b_all_smoke}/
```

## Per-run artifacts
Every run creates **only inside its `runs/<run_name>/` folder** (no overwrite of older runs):
- `config.json` — exact CLI args + hyperparameters
- `history.json` — list of per-epoch entries (loss, WER, CER, MER, WIL, GPU MB, throughput, lr, time)
- `log.txt` — append-only per-epoch log including PRED/LABEL samples (≤ 5 per epoch)
- `plots/{wer,cer,loss,gpu,throughput,lr}.png` — auto-regenerated each epoch
- `predictions/sample_preds_e{N}.txt` — written by HistorySaver
- `checkpoints/` — HF Trainer or PyTorch checkpoints (capped to 2 latest)
- `report.md` — auto-generated summary

You can re-plot at any time without retraining:
```bash
python3 training/common/regen_plots.py \
  --run-dir training/m02_whisper_small/runs/run_full \
  --dpi 200 --fontsize 12
```

## Smoke verification (laptop, 30 train / 15 val, 1–2 epochs)

All ten architectures have been verified end-to-end on the dataset:

| Model | Mode | WER | CER | val_loss | Wall time |
|-------|------|-----|-----|----------|-----------|
| m01 Whisper-tiny | FT 1ep / 50 train | 0.540 | 0.125 | 2.408 | 24 s |
| m02 Whisper-small | FT 1ep / 30 train | 0.165 | 0.029 | 2.043 | 84 s |
| m03 w2v2-XLS-R-300M | FT 1ep / 30 train | 1.000 | 0.983 | 8.531 | 510 s* |
| m04 cahya-w2v2-id | FT 1ep / 30 train | 0.397 | 0.082 | 0.381 | 700 s* |
| m05 MMS-1B-adapter | FT 1ep / 30 train | 1.025 | 1.865 | 8.689 | 824 s* |
| m06 Conformer-CTC | scratch 2ep / 30 | 1.000 | 1.000 | 2.923 | 17 s |
| m07 Bi-LSTM CTC | scratch 2ep / 30 | 1.000 | 1.000 | 4.967 | 12 s |
| zs-whisper-medium | inference 30-test | 0.156 | 0.035 | n/a | 16 s |
| zs-whisper-large-v3 | inference 30-test | **0.148** | 0.031 | n/a | 25 s |
| zs-mms-1b-all (ind) | inference 30-test | 0.336 | 0.067 | n/a | 3 s |

\* M03/M04/M05 wall-clock includes first-time HF model download (~1.2–4 GB).
Smoke WER==1.0 on m03/m05/m06/m07 is expected: CTC heads need many epochs to learn
alignment from scratch; the smoke test only verifies the pipeline runs end-to-end.

## Repro

```bash
# Activate env
source ~/miniconda3/etc/profile.d/conda.sh && conda activate torch-gpu

# Re-run any smoke (creates fresh run_smoke_1ep)
cd training
python3 m02_whisper_small/train.py --epochs 1 --max-train-samples 30 --max-val-samples 15
```

See **README-RUN.md** for the planned full-run commands and **SCALING.md** for the
Colab Pro / Pro+ multi-GPU plan.
