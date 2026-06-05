# Architecture summary — m06-conformer-ctc

- Family: Conformer-CTC (Gulati 2020)
- WER/CER: 0.011941638277990744 / 0.004322092427426721
- Parameter count: 11048219
- Template count: n/a
- Parameter note: Total Conformer-CTC model parameters.
- Decoding method: see test_paper.json
- Training hardware: Local Linux laptop, NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM

## Reproducibility pointers

- `../source_code/`: copied training/testing entry points and shared helper modules.
- `../pseudocode.md`: algorithm-level pseudocode for this model.
- `../metadata.json`: metrics, timing, parameter, hardware, checksum, and best-artifact provenance.
- `model_summary.png`: architecture diagram/torchinfo image when available from the run.
