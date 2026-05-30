# Training Report — openai/whisper-small

**Run dir**: m02_whisper_small/runs/run_smoke_1ep
**Generated**: 2026-05-24T11:22:58.691979

## Config
- Model: openai/whisper-small
- Epochs: 1
- Batch size: 2 (grad accum 2)
- Learning rate: 1e-05
- Warmup steps: 5
- Train samples: 30
- Val samples: 15
- FP16: True
- Gradient checkpointing: False
- Seed: 42

## Model
- Total params: 241,734,912
- Trainable params: 240,582,912

## Final results
- Total training time: 00:01:07
- Best WER: 0.1652892561983471
- Best CER: 0.028634361233480177
- Best at epoch: 1

## Outputs
- History: `m02_whisper_small/runs/run_smoke_1ep/history.json`
- Log: `m02_whisper_small/runs/run_smoke_1ep/log.txt`
- Plots: `m02_whisper_small/runs/run_smoke_1ep/plots`
- Predictions: `m02_whisper_small/runs/run_smoke_1ep/predictions`
- Checkpoints: `m02_whisper_small/runs/run_smoke_1ep/checkpoints`
