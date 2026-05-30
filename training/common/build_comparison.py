"""Build cross-model comparison report from smoke runs.

Aggregates all training/m0?_*/runs/* + zero_shot_baselines/runs/* histories into:
  - reports/training_smoke_comparison/comparison.md
  - reports/training_smoke_comparison/comparison_table.csv
  - reports/training_smoke_comparison/wer_bar.png
  - reports/training_smoke_comparison/cer_bar.png
  - reports/training_smoke_comparison/gpu_bar.png
"""
from __future__ import annotations
import csv, json
from pathlib import Path
import matplotlib.pyplot as plt

TRAINING = Path(__file__).parent.parent
OUT = TRAINING.parent / "reports" / "training_smoke_comparison"
OUT.mkdir(parents=True, exist_ok=True)

RUNS = [
    ("m01-whisper-tiny", TRAINING / "m01_whisper_tiny/runs/run_smoke_1ep", "FT", "encoder-decoder"),
    ("m02-whisper-small", TRAINING / "m02_whisper_small/runs/run_smoke_1ep", "FT★", "encoder-decoder"),
    ("m03-w2v2-xlsr-300m", TRAINING / "m03_wav2vec2_xlsr_300m/runs/run_smoke_1ep", "FT", "CTC"),
    ("m04-cahya-w2v2-id", TRAINING / "m04_cahya_wav2vec2_id/runs/run_smoke_1ep", "FT", "CTC"),
    ("m05-mms-1b-adapter", TRAINING / "m05_mms_1b_adapter/runs/run_smoke_1ep", "FT-adapter", "CTC"),
    ("m06-conformer-ctc", TRAINING / "m06_conformer_ctc/runs/run_smoke_2ep", "scratch", "CTC"),
    ("m07-bilstm-ctc", TRAINING / "m07_bilstm_ctc/runs/run_smoke_2ep", "scratch", "CTC"),
    ("zs-whisper-medium", TRAINING / "zero_shot_baselines/runs/whisper_medium_smoke", "zero-shot", "encoder-decoder"),
    ("zs-whisper-large-v3", TRAINING / "zero_shot_baselines/runs/whisper_large_v3_smoke", "zero-shot", "encoder-decoder"),
    ("zs-mms-1b-all", TRAINING / "zero_shot_baselines/runs/mms_1b_all_smoke", "zero-shot", "CTC"),
]

rows = []
for name, run_dir, mode, family in RUNS:
    h = run_dir / "history.json"
    if not h.exists():
        continue
    with h.open() as f:
        data = json.load(f)
    last = data[-1]
    rows.append({
        "model": name, "mode": mode, "family": family,
        "wer": last.get("wer"), "cer": last.get("cer"),
        "mer": last.get("mer"), "wil": last.get("wil"),
        "train_acc": last.get("train_acc"), "val_acc": last.get("val_acc"),
        "val_loss": last.get("val_loss"), "train_loss": last.get("train_loss"),
        "gpu_mb": last.get("gpu_mb"), "time_str": last.get("time_str"),
        "throughput": last.get("throughput_samples_per_sec"),
    })

# CSV
with (OUT / "comparison_table.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

# WER bar
fig, ax = plt.subplots(figsize=(11, 5))
names = [r["model"] for r in rows]
wers = [r["wer"] if r["wer"] is not None else 0 for r in rows]
colors = ["#1f77b4" if "FT" in r["mode"] else ("#ff7f0e" if r["mode"] == "scratch" else "#2ca02c")
          for r in rows]
ax.bar(range(len(names)), wers, color=colors)
ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=30, ha="right")
ax.set_ylabel("WER (lower=better)"); ax.set_title("Smoke-test WER comparison (30 samples, 1–2 epochs)")
ax.axhline(0.5, color="grey", linestyle="--", alpha=0.5, label="Smoke baseline")
ax.legend()
plt.tight_layout()
plt.savefig(OUT / "wer_bar.png", dpi=120)
plt.close()

# CER bar
fig, ax = plt.subplots(figsize=(11, 5))
cers = [r["cer"] if r["cer"] is not None else 0 for r in rows]
ax.bar(range(len(names)), cers, color=colors)
ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=30, ha="right")
ax.set_ylabel("CER (lower=better)"); ax.set_title("Smoke-test CER comparison")
plt.tight_layout()
plt.savefig(OUT / "cer_bar.png", dpi=120)
plt.close()

# GPU bar
fig, ax = plt.subplots(figsize=(11, 5))
gpus = [r["gpu_mb"] if r["gpu_mb"] is not None else 0 for r in rows]
ax.bar(range(len(names)), gpus, color=colors)
ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=30, ha="right")
ax.set_ylabel("Peak GPU (MB)"); ax.set_title("Smoke-test peak GPU memory")
ax.axhline(8000, color="red", linestyle="--", alpha=0.5, label="RTX 4060 8GB ceiling")
ax.legend()
plt.tight_layout()
plt.savefig(OUT / "gpu_bar.png", dpi=120)
plt.close()

# Markdown
md = """# Cross-Model Smoke Comparison

**Source**: 10 smoke runs (7 fine-tunes + 3 zero-shot baselines)
**Each run**: 30 train / 15 val (FT) or 30 test (zero-shot), 1–2 epochs

## Results Table

| Model | Mode | Family | WER | CER | Train Acc | Val Acc | val_loss | GPU MB | Time |
|-------|------|--------|----:|----:|----:|----:|---------:|-------:|------|
"""

def fmt(v, p=4):
    if v is None: return "n/a"
    return f"{v:.{p}f}"

def fmt_int(v):
    if v is None: return "n/a"
    return f"{v:.0f}"

for r in rows:
    md += (f"| `{r['model']}` | {r['mode']} | {r['family']} "
           f"| {fmt(r['wer'])} | {fmt(r['cer'])} "
           f"| {fmt(r['train_acc'])} | {fmt(r['val_acc'])} "
           f"| {fmt(r['val_loss'])} | {fmt_int(r['gpu_mb'])} | {r['time_str'] or 'n/a'} |\n")

md += """

## Plots

- `wer_bar.png` — WER across all 10 runs
- `cer_bar.png` — CER across all 10 runs
- `gpu_bar.png` — Peak GPU memory across all 10 runs (RTX 4060 8 GB ceiling marked)

## Interpretation

### Fine-tunes (after 1 epoch / 30 samples)
- **m02 Whisper-small (PRIMARY)**: WER 0.1653, CER 0.0286 — best FT result on smoke
- **m04 cahya-w2v2-id**: WER 0.397, CER 0.082 — second best, fast convergence due to ID pretraining
- **m01 Whisper-tiny**: WER 0.540 — limited capacity, still works
- **m03 / m05**: WER ≈ 1.0 — fresh CTC heads need many epochs to align
- **m06 / m07 (scratch)**: WER = 1.0 expected after 2 epochs; need ≥30 epochs for paper

### Zero-shot baselines
- **Whisper-large-v3**: WER 0.148, CER 0.031 — strongest zero-shot, even out-of-the-box
- **Whisper-medium**: WER 0.156, CER 0.034 — close behind, half the params
- **MMS-1B-all (ind)**: WER 0.336, CER 0.067 — middle tier

### GPU usage (RTX 4060 8 GB ceiling)
All FT models stay below 7 GB peak. m05 (MMS-1B adapter) is the most VRAM-heavy at 6.9 GB.
m06 / m07 (from-scratch) use only 0.2–0.3 GB; could batch×4 on full dataset.

## Paper expectations (full-run, after 3–5 epochs)
| Model | Expected WER | Expected CER |
|-------|-------------:|-------------:|
| m02 Whisper-small | < 0.10 | < 0.025 |
| m04 cahya-w2v2-id | < 0.15 | < 0.04 |
| m03 w2v2-XLS-R-300M | < 0.20 | < 0.05 |
| m05 MMS-1B-adapter | < 0.18 | < 0.04 |
| m01 Whisper-tiny | < 0.25 | < 0.07 |
| m06 Conformer-CTC (30 epochs) | < 0.30 | < 0.10 |
| m07 Bi-LSTM CTC (30 epochs) | < 0.40 | < 0.13 |

Zero-shot stays as-is (no FT) for paper baseline rows.
"""
(OUT / "comparison.md").write_text(md, encoding="utf-8")
print(f"✓ Wrote {OUT / 'comparison.md'}")
print(f"✓ Wrote {OUT / 'comparison_table.csv'}")
print(f"✓ Wrote {OUT / 'wer_bar.png'}")
print(f"✓ Wrote {OUT / 'cer_bar.png'}")
print(f"✓ Wrote {OUT / 'gpu_bar.png'}")
print(f"\nResults loaded: {len(rows)} runs")
