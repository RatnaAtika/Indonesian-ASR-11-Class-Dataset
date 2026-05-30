# README-RUN — Conventional Models Full-Run Commands

> All commands assume `source ~/miniconda3/etc/profile.d/conda.sh && conda activate torch-gpu` and `cd "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA"`.

> Convention: full runs go to `runs/run_full_<YYYYMMDD>/`. Smoke runs go to `runs/run_smoke_<YYYYMMDD>/`. Never overwrite previous runs.

---

## Step 0 — One-time data prep

```bash
# 0a. Build SPM (≈30 s; only needed once)
python3 training_conventional/common/spm_builder.py
# Output: training_conventional/spm/spm_v7_char.{model,vocab}

# 0b. Build full feature pickles (≈12-15 min on the Windows mount)
python3 training_conventional/common/feature_builder.py
# Output: training_conventional/data_pkl/{train,valid,test}.pkl + manifest.json
```

For smoke (already done) use `--max-train 2000 --max-val 500 --max-test 500`.

---

## m08 HMM-GMM template classifier (CPU only, ~30 min full)

```bash
python3 training_conventional/m08_hmm_gmm/train.py \
  --run-dir training_conventional/m08_hmm_gmm/runs/run_full_$(date +%Y%m%d) \
  --hmm-states 5 --hmm-mixtures 3 --hmm-iters 15
```
- 209 GMM-HMMs trained via Baum-Welch
- WER ≥ 0.5 expected (closed-vocab classifier on free-form ASR test)
- Pure CPU (no GPU usage)

## m09 DNN-HMM hybrid (~1 h full)

```bash
python3 training_conventional/m09_dnn_hmm/train.py \
  --run-dir training_conventional/m09_dnn_hmm/runs/run_full_$(date +%Y%m%d) \
  --dnn-hidden 512 --dnn-layers 4 --dnn-context 5 \
  --dnn-epochs 20 --dnn-batch-size 256 --dnn-lr 1e-3
```
- DNN: 4-layer 512-hidden, ±5 frame context (stacks 11 × 80-dim → 880-dim input)
- Linear-init frame labels via uniform partition; Viterbi-style decoding

## m10 GMM-HMM-DNN 3-stage (~2 h full)

```bash
python3 training_conventional/m10_gmm_hmm_dnn/train.py \
  --run-dir training_conventional/m10_gmm_hmm_dnn/runs/run_full_$(date +%Y%m%d) \
  --hmm-states 5 --hmm-mixtures 3 --hmm-iters 15 \
  --dnn-hidden 512 --dnn-layers 4 --dnn-context 5 --dnn-epochs 20
```
- Stage 1: GMM-HMM (m08 architecture)
- Stage 2: force-align (uniform partition for now)
- Stage 3: DNN classifier on alignments

## m11 Vanilla Transformer ★ (PRIMARY) (~14 h full on RTX 4060)

The supervisor-validated setup:
```bash
python3 training_conventional/m11_vanilla_transformer/train.py \
  --epochs 200 --batch-size 16 --lr 5e-4 \
  --d-model 192 --nhead 4 --num-layers 6 --ff 256 --dropout 0.1 \
  --input-dim 80 --amp --seed 2026
```
Test:
```bash
python3 training_conventional/m11_vanilla_transformer/test.py \
  --max-decode-len 64
```

## m12 ViT-modified-ID ★ (USER'S NOVEL ARCHITECTURE, unpublished) (~14 h full)

> This is the user's **own original architecture** — not yet published — designed
> specifically for **Indonesian end-to-end limited-vocabulary ASR**. The paper
> is its first public report. Hyperparameters below match the user's last
> validated stable run; do not modify without re-validating.

```bash
python3 training_conventional/m12_vit_modified/train.py \
  --epochs 200 --batch-size 16 --lr 5e-4 \
  --d-model 192 --nhead 4 --num-layers 2 --ff 256 --dropout 0.1 \
  --input-dim 80 --amp --specaug \
  --lambda-ctc 0.1 --scheduler plateau --seed 42
```
Test:
```bash
python3 training_conventional/m12_vit_modified/test.py \
  --max-decode-len 64
```

## m13 Wav2Letter CNN-CTC (~5 h full)

```bash
python3 training_conventional/m13_wav2letter_cnn/train.py \
  --run-dir training_conventional/m13_wav2letter_cnn/runs/run_full_$(date +%Y%m%d) \
  --epochs 50 --batch-size 16 --lr 3e-4
```
- 7 conv blocks + wide-context block + 2× 1×1 transitions
- ~7 M params, GLU/GELU activations
- CTC loss, greedy decode

## m14 Jasper-mini CNN-CTC (~6 h full)

```bash
python3 training_conventional/m14_jasper_cnn/train.py \
  --run-dir training_conventional/m14_jasper_cnn/runs/run_full_$(date +%Y%m%d) \
  --epochs 40 --batch-size 8 --lr 2e-4
```
- 5 Jasper blocks × 3 sub-blocks (residual + dense)
- ~28 M params, BatchNorm + dropout
- CTC loss, greedy decode

---

## Suggested order on a single RTX 4060 Laptop

| Day | Slot(s) | Approx wall time | Why this order |
|-----|---------|-----------------:|----------------|
| Day 1 (overnight) | m08 + m09 + m10 (all CPU + light GPU) | ~3-4 h sequential | Get classical baselines done first |
| Day 2 | m13 Wav2Letter | ~5 h | Single CNN model, low risk |
| Day 3 | m14 Jasper | ~6 h | Deeper CNN, more variance |
| Day 4-5 | m11 Vanilla Transformer | ~14 h | Long sequence training, primary CNN-baseline |
| Day 6-7 | m12 ViT-modified-ID ★ | ~14 h | **User's novel architecture, primary paper contribution** |
| Day 8 | rebuild comparison report | ~5 min | `python3 training_conventional/common/build_comparison.py` |

Total: ~7 nights / 65 wall hours on RTX 4060. With Colab Pro+ A100 (`SCALING.md`),
this collapses to ~12 hours.

---

## Re-plotting without retraining

```bash
python3 training_conventional/common/regen_plots.py \
  --run-dir training_conventional/m13_wav2letter_cnn/runs/run_full_20260601 \
  --dpi 200 --fontsize 12
```

## Resume from checkpoint

- HF Trainer doesn't apply (we don't use it here)
- `pkl_cnn_ctc_trainer.py` and `pkl_hmm_trainer.py` save full `epoch_NNN.pt` —
  load manually via `torch.load(...)` if needed for resume
- m11/m12 wrappers forward `--checkpoint <path>` to the root script's resume
  logic

## Monitoring

```bash
nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu --format=csv -l 5
tail -f training_conventional/m11_vanilla_transformer/runs/run_full_*/log.txt
```

## Common knobs

| Flag | Effect |
|------|--------|
| `--max-train-samples N` / `--max-val-samples N` | Subsample (smoke runs) |
| `--seed N` | Reproducibility (default 42 for HMM/CNN, 2026 for vanilla, 42 for ViT) |
| `--fp16` | AMP fp16 for CNN trainers (default on) |
| `--hmm-states N --hmm-mixtures K` | HMM topology |
| `--dnn-hidden H --dnn-layers L --dnn-context C` | DNN-HMM topology |
