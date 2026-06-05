# Architecture summary — m10-gmm-hmm-dnn

- Family: GMM-HMM-DNN (3-stage)
- WER/CER: 0.9703327925057448 / 0.8515677534730824
- Parameter count: 1448336
- Template count: 209
- Parameter note: Stage-3 DNN parameters; Stage-1 trained 209 GMM-HMM templates.
- Decoding method: see test_paper.json
- Training hardware: WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata

## Reproducibility pointers

- `../source_code/`: copied training/testing entry points and shared helper modules.
- `../pseudocode.md`: algorithm-level pseudocode for this model.
- `../metadata.json`: metrics, timing, parameter, hardware, checksum, and best-artifact provenance.
- `model_summary.png`: architecture diagram/torchinfo image when available from the run.
