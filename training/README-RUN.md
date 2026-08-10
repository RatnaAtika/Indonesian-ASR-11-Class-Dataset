# README-RUN — Full Training Commands

> All commands assume `source ~/miniconda3/etc/profile.d/conda.sh && conda activate torch-gpu` and `cd /mnt/c/Users/ratnaatika/AI/Dataset\ ASR/Paper_Datatset_SOTA/training`.

> Convention: every full run goes to `runs/run_full_<YYYYMMDD>` so smoke and full runs are never overwritten.

---

## RTX 4060 Laptop 8 GB — recommended on-laptop runs

> For models that need >7 GB at full batch (m02, m05), do **not** run them in parallel.
> All commands are designed to use ≤6.5 GB peak so you can keep the GUI responsive.

### m01 Whisper-tiny FT (5 epochs, full data)
```bash
python3 m01_whisper_tiny/train.py \
  --run-dir m01_whisper_tiny/runs/run_full_$(date +%Y%m%d) \
  --epochs 5 --batch-size 16 --grad-accum 1 --lr 5e-6 --warmup-steps 500
```
Estimated: ~3 h on full 71,792 train samples.

### m02 Whisper-small FT — ★ PRIMARY (3 epochs, full data)
```bash
python3 m02_whisper_small/train.py \
  --run-dir m02_whisper_small/runs/run_full_$(date +%Y%m%d) \
  --epochs 3 --batch-size 4 --grad-accum 4 --lr 1e-5 --warmup-steps 500
```
Estimated: ~12–14 h on full data, peak ~6.2 GB. Best target: **WER < 0.10, CER < 0.025**.

### m03 wav2vec2-XLS-R-300M FT (5 epochs)
```bash
python3 m03_wav2vec2_xlsr_300m/train.py \
  --run-dir m03_wav2vec2_xlsr_300m/runs/run_full_$(date +%Y%m%d) \
  --epochs 5 --batch-size 8 --grad-accum 2 --lr 1e-4 --warmup-steps 1000
```
Estimated: ~10–12 h. Builds CTC head from scratch; expect WER >0.5 in epoch 1, decreasing rapidly.

### m04 cahya/wav2vec2-large-xlsr-indonesian FT (5 epochs)
```bash
python3 m04_cahya_wav2vec2_id/train.py \
  --run-dir m04_cahya_wav2vec2_id/runs/run_full_$(date +%Y%m%d) \
  --epochs 5 --batch-size 8 --grad-accum 2 --lr 5e-5 --warmup-steps 500
```
Estimated: ~10 h. Pretrained on Indonesian → fast convergence, smoke epoch already at WER 0.40.

### m05 MMS-1B adapter FT (5 epochs, adapter-only)
```bash
python3 m05_mms_1b_adapter/train.py \
  --run-dir m05_mms_1b_adapter/runs/run_full_$(date +%Y%m%d) \
  --epochs 5 --batch-size 4 --grad-accum 4 --lr 1e-3 --warmup-steps 500
```
Estimated: ~14 h. Only ~3 M trainable adapter params; base 1 B params frozen.

### m06 Conformer-CTC small (30 epochs, from scratch)
```bash
python3 m06_conformer_ctc/train.py \
  --run-dir m06_conformer_ctc/runs/run_full_$(date +%Y%m%d) \
  --epochs 30 --batch-size 32 --hidden-size 256 --num-layers 6 --lr 3e-4
```
Estimated: ~6–8 h. From-scratch baseline — needs many epochs.

### m07 Bi-LSTM CTC (30 epochs, from scratch — DeepSpeech-2 style)
```bash
python3 m07_bilstm_ctc/train.py \
  --run-dir m07_bilstm_ctc/runs/run_full_$(date +%Y%m%d) \
  --epochs 30 --batch-size 32 --hidden-size 512 --num-layers 5 --lr 3e-4
```
Estimated: ~5 h.

---

## Zero-shot baselines (test set only, ~16 min total for all three)

```bash
python3 zero_shot_baselines/run_inference.py \
  --model-id openai/whisper-large-v3 \
  --run-dir zero_shot_baselines/runs/whisper_large_v3_full_$(date +%Y%m%d) \
  --max-samples 0   # 0 = all 15,376 test samples

python3 zero_shot_baselines/run_inference.py \
  --model-id openai/whisper-medium \
  --run-dir zero_shot_baselines/runs/whisper_medium_full_$(date +%Y%m%d) \
  --max-samples 0

python3 zero_shot_baselines/run_inference.py \
  --model-id facebook/mms-1b-all --target-lang ind \
  --run-dir zero_shot_baselines/runs/mms_1b_all_full_$(date +%Y%m%d) \
  --max-samples 0
```

---

## Suggested execution order on a single RTX 4060 Laptop

1. **m07 Bi-LSTM CTC** (≤5 h, ≤300 MB) — overnight, lowest VRAM, classic baseline
2. **m06 Conformer-CTC** (≤8 h) — next overnight
3. **m04 cahya-w2v2-id** (≤10 h) — best ID-pretrained baseline
4. **m01 Whisper-tiny** (≤3 h) — quick win
5. **Zero-shot all three** (≤30 min, run together)
6. **m03 w2v2-XLS-R-300M** (≤12 h)
7. **m05 MMS-1B-adapter** (≤14 h, run weekend)
8. **m02 Whisper-small ★** (≤14 h, primary — run on stable power, ideally Colab Pro+)

Total laptop wall time: ~75 h sequential. With Colab Pro+ A100 (see SCALING.md), this drops to ~16 h.

---

## Re-plotting without retraining

```bash
python3 common/regen_plots.py --run-dir m02_whisper_small/runs/run_full_20260601 \
  --dpi 200 --fontsize 12
```
Outputs `plots/{wer_cer,loss,gpu_mb,lr}.png` to the same run folder.

## Resume from checkpoint
HF Trainer auto-resumes if you re-run with the same `--run-dir`. PyTorch from-scratch
runs save to `checkpoints/epoch_NNN.pt` and can be loaded manually.

## Monitoring while running
```bash
# In another terminal
nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu --format=csv -l 5
tail -f training/m02_whisper_small/runs/run_full_*/log.txt
```

## Common knobs

| Flag | Effect |
|------|--------|
| `--max-train-samples N` | Subsample for fast iteration (smoke runs) |
| `--max-val-samples N` | Subsample val set |
| `--gradient-checkpointing` | Trade speed for VRAM (Whisper trainer; ~30 % slower, ~30 % less VRAM) |
| `--fp16` | On by default. Disable for debugging numerical issues |
| `--seed N` | Reproducibility (default 42) |

## When you change `data_final/*.tsv`
Re-run all smoke tests first to confirm the splits are consistent:
```bash
for f in m01 m02 m03 m04 m05 m06 m07; do
  python3 ${f}_*/train.py --epochs 1 --max-train-samples 30 --max-val-samples 15 \
    --run-dir ${f}_*/runs/run_smoke_$(date +%H%M)
done
```
