# m13-wav2letter artifact package

- Rank: 6
- Family: Wav2Letter-style CNN-CTC (Collobert 2016)
- WER/CER: 0.09292935225495738 / 0.05196455821641889
- Training time: 04:10:23 (4.173056 h)
- Full-test inference time: 00:00:23 (22.87 s)
- Params/templates: 24840900 / n/a
- Training hardware: WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata
- Source run: `/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA/training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637`
- Best artifact source: `/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA/training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/checkpoints/best.pt`
- Best artifact exists locally: True

## Contents

- `metadata.json`: machine-readable evidence and checksums.
- `source_code/`: copied training/testing entry points and shared helper code needed to reproduce this model.
- `pseudocode.md`: algorithm-level pseudocode excerpt for this model.
- `architecture/`: text architecture summary and `model_summary.png` when available.
- `run_outputs/`: copied/hardlinked reports, logs, summaries, metrics, predictions, and model-summary images where available.
- `best_artifact/`: local hardlink/copy of the selected best testing model artifact.

Large binary weights are intentionally ignored by Git; keep this local package or upload it to Drive/Zenodo/OSF for submission reproducibility.
