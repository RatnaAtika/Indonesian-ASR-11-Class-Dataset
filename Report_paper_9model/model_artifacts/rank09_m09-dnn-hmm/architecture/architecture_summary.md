# Architecture summary — m09-dnn-hmm

- Family: DNN-HMM (hybrid)
- WER/CER: 0.9708026517682126 / 0.8437097287945755
- Parameter count: 1448336
- Template count: n/a
- Parameter note: DNN acoustic model parameters.
- Decoding method: see test_paper.json
- Training hardware: WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata

## Reproducibility pointers

- `../source_code/`: copied training/testing entry points and shared helper modules.
- `../pseudocode.md`: algorithm-level pseudocode for this model.
- `../metadata.json`: metrics, timing, parameter, hardware, checksum, and best-artifact provenance.
- `model_summary.png`: architecture diagram/torchinfo image when available from the run.
