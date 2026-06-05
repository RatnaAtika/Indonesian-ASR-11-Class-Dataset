# Architecture summary — m02b-whisper-small-ft

- Family: Whisper-small FT (Radford et al. 2023; arXiv 2022)
- WER/CER: 0.008523540683204734 / 0.0018570295438410948
- Parameter count: 241734912
- Template count: n/a
- Parameter note: Total fine-tuned Whisper-small model parameters from run report. The original Whisper paper lists small as approximately 244M parameters; this run reports the exact HF model count used here.
- Decoding method: see test_paper.json
- Training hardware: Google Colab Linux, NVIDIA A100-SXM4-40GB GPU

## Reproducibility pointers

- `../source_code/`: copied training/testing entry points and shared helper modules.
- `../pseudocode.md`: algorithm-level pseudocode for this model.
- `../metadata.json`: metrics, timing, parameter, hardware, checksum, and best-artifact provenance.
- `model_summary.png`: architecture diagram/torchinfo image when available from the run.
