# Architecture summary — m13-wav2letter

- Family: Wav2Letter-style CNN-CTC (Collobert 2016)
- WER/CER: 0.09292935225495738 / 0.05196455821641889
- Parameter count: 24840900
- Template count: n/a
- Parameter note: Total CNN-CTC model parameters.
- Decoding method: see test_paper.json
- Training hardware: WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata

## Reproducibility pointers

- `../source_code/`: copied training/testing entry points and shared helper modules.
- `../pseudocode.md`: algorithm-level pseudocode for this model.
- `../metadata.json`: metrics, timing, parameter, hardware, checksum, and best-artifact provenance.
- `model_summary.png`: architecture diagram/torchinfo image when available from the run.
