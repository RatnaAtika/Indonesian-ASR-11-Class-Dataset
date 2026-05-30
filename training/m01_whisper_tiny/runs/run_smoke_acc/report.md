# Training Report — openai/whisper-tiny

**Run dir**: training/m01_whisper_tiny/runs/run_smoke_acc
**Generated**: 2026-05-24T14:50:12.508136

## Config
- Model: openai/whisper-tiny
- Epochs: 1
- Batch size: 4 (grad accum 1)
- Learning rate: 1e-05
- Warmup steps: 5
- Train samples: 30
- Val samples: 15
- FP16: True
- Gradient checkpointing: False
- Seed: 42

## Model
- Total params: 37,760,640
- Trainable params: 37,184,640

## Final results
- Total training time: 00:00:12
- Best WER: 0.5289256198347108
- Best CER: 0.1222466960352423
- Best at epoch: 1

## Outputs
- History: `training/m01_whisper_tiny/runs/run_smoke_acc/history.json`
- Log: `training/m01_whisper_tiny/runs/run_smoke_acc/log.txt`
- Plots: `training/m01_whisper_tiny/runs/run_smoke_acc/plots`
- Predictions: `training/m01_whisper_tiny/runs/run_smoke_acc/predictions`
- Checkpoints: `training/m01_whisper_tiny/runs/run_smoke_acc/checkpoints`
