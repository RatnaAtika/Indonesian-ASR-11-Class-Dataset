# Architecture summary — m08-hmm-gmm

- Family: HMM-GMM (classical)
- WER/CER: 0.9633216113236083 / 0.7204618840522383
- Parameter count: 511005
- Template count: 209
- Parameter note: Classical HMM-GMM numeric parameter count computed from the selected best.pkl template bank: 209 templates x (5 start probabilities + 25 transitions + 5x3x80 means + 5x3x80 diagonal covariances + 5x3 mixture weights) = 511,005. This is not a neural trainable-parameter count.
- Decoding method: see test_paper.json
- Training hardware: WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata

## Reproducibility pointers

- `../source_code/`: copied training/testing entry points and shared helper modules.
- `../pseudocode.md`: algorithm-level pseudocode for this model.
- `../metadata.json`: metrics, timing, parameter, hardware, checksum, and best-artifact provenance.
- `model_summary.png`: architecture diagram/torchinfo image when available from the run.
