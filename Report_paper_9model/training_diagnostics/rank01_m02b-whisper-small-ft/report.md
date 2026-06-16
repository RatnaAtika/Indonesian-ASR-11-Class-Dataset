# Training Report — openai/whisper-small

**Run dir**: training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact
**Generated**: 2026-06-04T05:40:04.530740

## Config
- Model: openai/whisper-small
- Epochs: 5
- Batch size: 8 (grad accum 4)
- Learning rate: 1e-05
- Warmup steps: 500
- Train samples: 71792
- Val samples: 15376
- FP16: True
- DataLoader workers: 2
- Gradient checkpointing: True
- Seed: 42

## Model
- Total params: 241,734,912
- Trainable params: 241,734,912

## Final results
- Total training time: 04:48:29  (4 jam, 48 menit, 29 detik)
- Best WER: 0.0014584453561774
- Best CER: 0.0010674592595061152
- Best at epoch: 5

## Outputs
- History: `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/history.json`
- Log: `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/log.txt`
- Plots: `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/plots`
- Predictions: `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/predictions`
- Checkpoints: `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/checkpoints`
