# Architecture summary — m11-vanilla-transformer

- Family: Vanilla Transformer (Vaswani 2017)
- WER/CER: 0.043931841040738266 / 0.0326697714313076
- Parameter count: 4212688
- Template count: n/a
- Parameter note: Total model parameters from torchinfo/log summary.
- Decoding method: see test_paper.json
- Training hardware: Training log records `Using device: cuda`; exact training OS/GPU model not recorded. Full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU.

## Reproducibility pointers

- `../source_code/`: copied training/testing entry points and shared helper modules.
- `../pseudocode.md`: algorithm-level pseudocode for this model.
- `../metadata.json`: metrics, timing, parameter, hardware, checksum, and best-artifact provenance.
- `model_summary.png`: architecture diagram/torchinfo image when available from the run.
