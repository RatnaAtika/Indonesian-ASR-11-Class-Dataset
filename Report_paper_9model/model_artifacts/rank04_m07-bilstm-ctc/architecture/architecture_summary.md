# Architecture summary — m07-bilstm-ctc

- Family: Bi-LSTM CTC
- WER/CER: 0.04012184444231887 / 0.013216648861286718
- Parameter count: 32825659
- Template count: n/a
- Parameter note: Total Bi-LSTM CTC model parameters.
- Decoding method: see test_paper.json
- Training hardware: Local Linux laptop, NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM

## Reproducibility pointers

- `../source_code/`: copied training/testing entry points and shared helper modules.
- `../pseudocode.md`: algorithm-level pseudocode for this model.
- `../metadata.json`: metrics, timing, parameter, hardware, checksum, and best-artifact provenance.
- `model_summary.png`: architecture diagram/torchinfo image when available from the run.
