# SCALING.md — Conventional Models Cloud Plan

> Primary scaling guide is `training/SCALING.md`. This file documents only the
> **delta** for the conventional models — what changes when you move m08–m14
> from the RTX 4060 Laptop to Colab / RunPod / Modal.

---

## Tier comparison (full v7 dataset: 71,792 train / 15,376 val / 15,376 test)

| Model | RTX 4060 Laptop | Colab Pro (T4) | Colab Pro+ (A100-40GB) | RunPod A100-80GB | RunPod H100 |
|-------|----------------:|----------------:|----------------------:|-----------------:|------------:|
| m08 HMM-GMM (CPU) | 30 min | 30 min (CPU) | 30 min (CPU) | 30 min | 30 min |
| m09 DNN-HMM | 1 h | 45 min | 15 min | 12 min | 8 min |
| m10 GMM-HMM-DNN | 2 h | 1.5 h | 30 min | 25 min | 18 min |
| m11 Vanilla Transformer | 14 h | 8 h | **2 h** | 1.5 h | 1 h |
| m12 ViT-modified-ID ★ | 14 h | 8 h | **2 h** | 1.5 h | 1 h |
| m13 Wav2Letter | 5 h | 3 h | 1 h | 50 min | 35 min |
| m14 Jasper-mini | 6 h | 4 h | 1.5 h | 1 h | 45 min |

**Total** for all 7 models: ~42 h on laptop, ~26 h on Colab Pro, **~8 h on Colab
Pro+ A100-40GB**, ~6 h on RunPod A100-80GB spot.

---

## Colab Pro+ recipe — full conventional pipeline

```python
# 1. Mount + clone
from google.colab import drive
drive.mount('/content/drive')
!git clone https://github.com/<you>/paper-dataset-asr.git
%cd paper-dataset-asr/training_conventional

# 2. Install
!pip install -q torch transformers accelerate jiwer soundfile sentencepiece \
    librosa hmmlearn matplotlib seaborn

# 3. Build features (one-time, ~10 min on Drive-mounted audio)
!python3 common/spm_builder.py
!python3 common/feature_builder.py \
    --audio-root /content/drive/MyDrive/paper-dataset-asr/Processed_Balanced19_v7_natural_synth/Dataset_Balanced19 \
    --splits-dir /content/paper-dataset-asr/training/data_final
```

Then any model trains the same way as on laptop, just point `--data-pkl-dir`
correctly. Disconnect-safe via `--save-strategy=epoch` (already default).

## RunPod recipe — overnight all-in-one

```bash
# Inside RunPod PyTorch 2.5 + CUDA 12.4 template
git clone <repo>
cd paper-dataset-asr/training_conventional
pip install hmmlearn jiwer sentencepiece librosa soundfile

rsync -avh /workspace/dataset/ ../Processed_Balanced19_v7_natural_synth/

# Sequential overnight (~6-8 h on A100-80GB):
python3 m08_hmm_gmm/train.py
python3 m09_dnn_hmm/train.py
python3 m10_gmm_hmm_dnn/train.py
python3 m13_wav2letter_cnn/train.py --epochs 50
python3 m14_jasper_cnn/train.py --epochs 40
python3 m11_vanilla_transformer/train.py --epochs 80
python3 m12_vit_modified/train.py --epochs 100

rsync -avh m??*/runs/* /workspace/results_conventional/
```

Cost: ~7 USD on RunPod A100-80GB spot.

---

## CPU-only HMM training notes

`hmmlearn` is single-threaded but releases the GIL during the EM E-step. To
parallelise across templates (209 of them), use `joblib.Parallel`:

```python
from joblib import Parallel, delayed

models = Parallel(n_jobs=-1)(
    delayed(train_one_hmm)(tmpl, template_to_X[tmpl]) for tmpl in templates
)
```

This drops m08 wall time from 30 min to ~5 min on a 16-core CPU. Not implemented
in the smoke version — easy enough to add when you actually run on a CPU box.

---

## DNN training optimisations (DNN-HMM and GMM-HMM-DNN)

The frame DNN currently uses a single batch loop over all training frames
(~14 M frames at full data, 80 dim each = ~5 GB RAM). For >12-h H100 / A100:
- Use `torch.utils.data.DataLoader` instead of in-memory batching
- Enable `pin_memory=True` and `num_workers=4`
- Precompute the ±5 stacked-context features to disk to avoid recomputing
  per epoch

These optimisations are not required for the laptop or Colab Pro+ run.

---

## Reproducibility

Same as `training/SCALING.md`:
```python
import torch, random, numpy as np
torch.manual_seed(42); np.random.seed(42); random.seed(42)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```
All trainers in `training_conventional/` already accept `--seed N`.

## Failure-mode playbook

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `hmmlearn` `Convergence warning: log-likelihood degrades` | Too many states for sample count | Lower `--hmm-states` or use `--hmm-mixtures 1` |
| HMM EM `LinAlgError: cov singular` | Too few unique frames per state | Switch to `--cov-type diag` (default already), reduce mixtures |
| DNN frame_acc stuck near 1/V | Linear-init labels are too noisy | Raise `--dnn-context`, use Stage-3 alignments from m10 instead |
| CNN val WER stuck at 1.0 | CTC needs more epochs | ≥30 epochs minimum, ideally 50 |
| Transformer val Acc plateaus | LR schedule | Try `--scheduler plateau` (already enabled in m12) |
| OOM on `--batch-size 16` for m14 | Jasper too deep for 8 GB | `--batch-size 4 --grad-accum 4` (TODO: add grad-accum to CTC trainer) |
