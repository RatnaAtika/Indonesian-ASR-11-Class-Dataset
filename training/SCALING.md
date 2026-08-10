# SCALING.md — Cloud Scaling Plan

When laptop wall-time becomes a bottleneck (especially for m02 Whisper-small ★, m03,
m05), move to managed GPU. The trainers were designed to scale **without code changes**
— only batch size and epoch count differ.

---

## Tier comparison (full dataset: 71,792 train / 15,376 val / 15,376 test)

| Tier | GPU | VRAM | Cost/h (USD) | Speed vs RTX 4060 | m02 full ETA |
|------|-----|------|--------------|-------------------|--------------|
| Local | RTX 4060 Laptop | 8 GB | 0.00 | 1.0× | ~14 h |
| Colab Free | T4 | 16 GB | 0.00 | ~1.3× | ~10 h (12-h limit) |
| **Colab Pro** | T4 / V100 | 16 GB | ~10/mo | 1.3–2.5× | ~6–8 h |
| **Colab Pro+** | A100-40GB | 40 GB | ~50/mo | 6–10× | **~2 h** |
| RunPod A100 | A100-80GB | 80 GB | 1.10/h spot | 8–12× | ~1.5 h |
| RunPod H100 | H100-80GB | 80 GB | 2.50/h spot | 14–18× | ~1 h |
| Modal A10G | A10G | 24 GB | 1.10/h | 3–4× | ~4 h |

> ETAs above are for the primary m02 Whisper-small (244 M params, 3 epochs full data).

---

## Colab Pro+ recipe (recommended for paper)

### One-shot setup notebook (`colab_setup.ipynb`)
```python
# 1. Mount + clone
from google.colab import drive
drive.mount('/content/drive')
!git clone https://github.com/<you>/paper-dataset-asr.git
%cd paper-dataset-asr/training

# 2. Pip install
!pip install -q transformers==4.46.0 datasets accelerate jiwer soundfile torchaudio==2.5

# 3. Copy data_final + Dataset_Balanced19 from Drive
!ls /content/drive/MyDrive/paper-dataset-asr/Processed_Balanced19_v7_natural_synth
# Update --data-root and --data-final accordingly when running below
```

### m02 full run on Colab Pro+ A100-40GB
```python
!python3 m02_whisper_small/train.py \
  --run-dir m02_whisper_small/runs/run_full_colab_$(date +%Y%m%d) \
  --epochs 3 --batch-size 16 --grad-accum 1 --lr 1e-5 --warmup-steps 500 \
  --data-root /content/drive/MyDrive/paper-dataset-asr/Processed_Balanced19_v7_natural_synth/Dataset_Balanced19 \
  --data-final /content/paper-dataset-asr/training/data_final
```
A100-40GB lets us crank batch_size=16 (vs 4 on laptop) → 4× fewer optimizer steps
→ ~2 h end-to-end. **Save to Drive every epoch** so disconnects don't lose progress.

### Disconnect-safe pattern
- HF Trainer auto-resumes from latest checkpoint if `--run-dir` is unchanged.
- Use `nohup ... &` if SSH-attached; for Colab use `--save-strategy=epoch` (already default).

---

## RunPod recipe (best speed/$ for marathon runs)

```bash
# On RunPod template "PyTorch 2.5 + CUDA 12.4"
git clone <repo>
cd paper-dataset-asr/training
pip install transformers==4.46.0 datasets jiwer soundfile torchaudio==2.5

# Pull data from object store / persistent volume
rsync -avh /workspace/dataset/ ../Processed_Balanced19_v7_natural_synth/

# Run all 7 FT models in sequence (overnight, ~10 h total on A100-80GB)
for slot in m01 m02 m03 m04 m05; do
  python3 ${slot}_*/train.py \
    --run-dir ${slot}_*/runs/run_full_runpod_$(date +%Y%m%d) \
    --epochs 5 --batch-size 32 --grad-accum 1
done

# m06 + m07 from scratch (GPU is over-provisioned but throughput is best)
python3 m06_conformer_ctc/train.py --run-dir m06_conformer_ctc/runs/run_full_runpod \
  --epochs 30 --batch-size 64 --hidden-size 256 --num-layers 6 --lr 5e-4
python3 m07_bilstm_ctc/train.py --run-dir m07_bilstm_ctc/runs/run_full_runpod \
  --epochs 30 --batch-size 64 --hidden-size 512 --num-layers 5 --lr 5e-4

# Sync results back
rsync -avh m0?_*/runs/run_full_runpod_* /workspace/results/
```

Estimated: **~10 h total wall-time on a single A100-80GB** for all 7 FT models +
3 zero-shot baselines. Cost: ~11 USD spot.

---

## Multi-GPU (DistributedDataParallel)

The HF Trainer-based scripts (m01–m05) accept `accelerate launch` for multi-GPU:

```bash
accelerate config  # one-time
accelerate launch m02_whisper_small/train.py \
  --run-dir m02_whisper_small/runs/run_full_4gpu \
  --epochs 3 --batch-size 8   # per-GPU; effective 8×4=32
```

The from-scratch trainers (m06/m07) currently use single-GPU. To scale, wrap the
model with `torch.nn.parallel.DistributedDataParallel` in `from_scratch_trainer.py`
(see `accelerate.Accelerator()` example). Plan ~1 day of work; not blocking for paper.

---

## Cost ceiling for paper completion

Strict-budget plan (paper-only, no fluff):
| Resource | Hours | Cost |
|----------|-------|------|
| Colab Pro (1 month) | unlimited | $10 |
| Colab Pro+ (1 month) | unlimited | $50 |
| **OR** RunPod A100-80GB spot | 12 h | ~$13 |
| **OR** RunPod H100-80GB spot | 8 h | ~$20 |

**Recommended for paper:** RunPod A100-80GB spot → run all 10 architectures in one
overnight session (~12 h, ~$13). Sync results to local box, do post-analysis offline.

---

## Reproducibility checklist (always set before cloud runs)

```python
import torch, random, numpy as np
torch.manual_seed(42); np.random.seed(42); random.seed(42)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```
The trainers already accept `--seed 42` (default). Save `pip freeze` output to the run
folder for citation:
```bash
pip freeze > $RUN_DIR/pip_freeze.txt
nvidia-smi > $RUN_DIR/nvidia_smi.txt
```

---

## Storage notes

- `Dataset_Balanced19/` is ~14 GB raw WAV. On Colab, store in Drive (read-only) and
  pre-cache features on first epoch. On RunPod, use `--save-strategy=epoch` and a
  persistent volume.
- Each `runs/<run_full>/` is ~1–4 GB (checkpoints) — clean old checkpoints with
  `--save-total-limit=2` (already default).

---

## Failure-mode playbook

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `datasets.map()` hangs forever | WSL2 /mnt/c arrow cache | Already fixed: trainers use custom torch Dataset (no map()) |
| `CUDA out of memory` mid-epoch | Long audio in batch | Lower `--batch-size`, raise `--grad-accum`, enable `--gradient-checkpointing` |
| `RuntimeError: backward graph` | gradient_checkpointing + autocast | Disable `--gradient-checkpointing` on HF Trainer (known issue) |
| Loss diverges to NaN (m05 MMS) | LR too high for adapter | Drop `--lr 1e-3` → `5e-4`, raise `--warmup-steps` 1000 |
| WER stuck at 1.0 (m03/m06/m07) | CTC needs more epochs | Run ≥10 epochs; smoke test is just pipeline validation |
| Whisper outputs English | Language tag dropped | Already enforced via `--language indonesian --task transcribe` |
