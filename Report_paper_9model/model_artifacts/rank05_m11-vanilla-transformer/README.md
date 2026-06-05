# m11-vanilla-transformer artifact package

- Rank: 5
- Family: Vanilla Transformer (Vaswani 2017)
- WER/CER: 0.043931841040738266 / 0.0326697714313076
- Training time: 02:38:53 (2.648056 h)
- Full-test inference time: 00:21:33 (1293.28 s)
- Params/templates: 4212688 / n/a
- Training hardware: Training log records `Using device: cuda`; exact training OS/GPU model not recorded. Full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU.
- Source run: `/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA/training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328`
- Best artifact source: `/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA/training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328/checkpoints/best.pth`
- Best artifact exists locally: True

## Contents

- `metadata.json`: machine-readable evidence and checksums.
- `source_code/`: copied training/testing entry points and shared helper code needed to reproduce this model.
- `pseudocode.md`: algorithm-level pseudocode excerpt for this model.
- `architecture/`: text architecture summary and `model_summary.png` when available.
- `run_outputs/`: copied/hardlinked reports, logs, summaries, metrics, predictions, and model-summary images where available.
- `best_artifact/`: local hardlink/copy of the selected best testing model artifact.

Large binary weights are intentionally ignored by Git; keep this local package or upload it to Drive/Zenodo/OSF for submission reproducibility.
