# Architecture summary — m12-vit-modified-ID

- Family: ViT-modified-ID (proposed in this work)
- WER/CER: 0.01776655336206327 / 0.013009616165317267
- Parameter count: 4353248
- Template count: n/a
- Parameter note: Total model parameters from torchinfo/log summary.
- Decoding method: see test_paper.json
- Training hardware: Training log records `Using device: cuda`; exact training OS/GPU model not recorded. Full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU.

## Reproducibility pointers

- `../source_code/`: copied training/testing entry points and shared helper modules.
- `../pseudocode.md`: algorithm-level pseudocode for this model.
- `../metadata.json`: metrics, timing, parameter, hardware, checksum, and best-artifact provenance.
- `model_summary.png`: architecture diagram/torchinfo image when available from the run.
