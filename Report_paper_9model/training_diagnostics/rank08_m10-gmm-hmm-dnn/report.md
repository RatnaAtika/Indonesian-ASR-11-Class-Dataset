# Training Report — gmm_hmm_dnn

**Run dir**: training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736
**Generated**: 2026-05-31T21:17:05.069425

## Config
- Mode: gmm_hmm_dnn
- Train samples: 71792, Val samples: 15376
- HMM states: 5, mixtures: 3
- DNN: hidden=512, layers=4, ctx=±5, epochs=30

## Final
- WER: 0.9869
- CER: 0.9075
- MER: 0.9868
- WIL: 0.9989
- Train time: 06:29:10
- Eval time:  00:54:04
- Stage-1 templates: 209
- Stage-3 DNN params: 1,448,336
- Stage-1 WER: 1.0231
- Stage-3 WER: 0.9869
