# Training Report — openai/whisper-tiny

**Run dir**: m01_whisper_tiny/runs/run_smoke_1ep
**Generated**: 2026-05-24T11:13:05.710424

## Config
- Model: openai/whisper-tiny
- Epochs: 1
- Batch size: 4 (grad accum 1)
- Learning rate: 1e-05
- Warmup steps: 5
- Train samples: 50
- Val samples: 20
- FP16: True
- Gradient checkpointing: False
- Seed: 42

## Model
- Total params: 37,760,640
- Trainable params: 37,184,640

## Final results
- Total training time: 00:00:13
- Best WER: 0.5403726708074534
- Best CER: 0.12479338842975207
- Best at epoch: 1

## Outputs
- History: `m01_whisper_tiny/runs/run_smoke_1ep/history.json`
- Log: `m01_whisper_tiny/runs/run_smoke_1ep/log.txt`
- Plots: `m01_whisper_tiny/runs/run_smoke_1ep/plots`
- Predictions: `m01_whisper_tiny/runs/run_smoke_1ep/predictions`
- Checkpoints: `m01_whisper_tiny/runs/run_smoke_1ep/checkpoints`
