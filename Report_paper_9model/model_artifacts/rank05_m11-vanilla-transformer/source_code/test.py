"""Vanilla Transformer test entry point — m11 paper model.

1. Run root test_model_vanilla.py to produce predictions CSV
2. Read CSV, compute aggregated WER/CER/MER/WIL/SER
3. Save machine-readable test_paper.json untuk AI agent

Usage:
    # Default: pakai run_dir terbaru run_paper_*
    python3 training_conventional/m11_vanilla_transformer/test.py

    # Override:
    python3 training_conventional/m11_vanilla_transformer/test.py \\
      --run-dir training_conventional/m11_vanilla_transformer/runs/run_paper_20260601
"""
import sys, subprocess, argparse, csv, time
from pathlib import Path

HERE = Path(__file__).parent
PROJECT_ROOT = HERE.parent.parent
ASR_ROOT = PROJECT_ROOT.parent
TC = HERE.parent

sys.path.insert(0, str(TC))
from common.test_helper import (
    compute_test_metrics, per_sample_wer, per_sample_cer,
    find_best_checkpoint, write_test_results,
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--run-dir", type=Path, default=None)
    p.add_argument("--max-decode-len", type=int, default=64)
    return p.parse_known_args()


def auto_pick_run(slot_runs: Path) -> Path:
    """Pilih run_paper_* terbaru, fallback ke run_full_*."""
    cands = sorted([d for d in slot_runs.glob("run_paper_*") if d.is_dir()],
                   key=lambda d: d.stat().st_mtime, reverse=True)
    if not cands:
        cands = sorted([d for d in slot_runs.glob("run_full_*") if d.is_dir()],
                       key=lambda d: d.stat().st_mtime, reverse=True)
    return cands[0] if cands else None


# 1. Resolve run_dir
args, extra = parse_args()
if args.run_dir is None:
    args.run_dir = auto_pick_run(HERE / "runs")
    if args.run_dir is None:
        print(f"[m11-test] ERROR: no run found in {HERE / 'runs'}")
        sys.exit(1)
print(f"[m11-test] run_dir: {args.run_dir}")

# 2. Find best checkpoint
ckpt_info = find_best_checkpoint(args.run_dir)
if not ckpt_info.get("path"):
    # Root script writes 'best.pth' (not best.pt) — check that
    best_pth = args.run_dir / "checkpoints" / "best.pth"
    if best_pth.exists():
        ckpt_info = {"path": str(best_pth), "filename": "best.pth",
                     "format": "pth", "best_wer": None, "best_epoch": None}
    else:
        print(f"[m11-test] ERROR: no checkpoint in {args.run_dir}/checkpoints/")
        sys.exit(1)
print(f"[m11-test] checkpoint: {ckpt_info['filename']}")

# 3. Run root test script
test_pkl = TC / "data_pkl" / "test.pkl"
spm_model = TC / "spm" / "spm_v7_char.model"
eval_dir = args.run_dir / "eval_greedy"
eval_dir.mkdir(parents=True, exist_ok=True)

cmd = ["python3", str(ASR_ROOT / "test_model_vanilla.py"),
       "--test-pkl", str(test_pkl),
       "--spm-model", str(spm_model),
       "--checkpoint", ckpt_info["path"],
       "--max-decode-len", str(args.max_decode_len),
       "--outdir", str(eval_dir)] + extra
print(f"[m11-test] cmd: {' '.join(cmd)}")
t0 = time.perf_counter()
result = subprocess.run(cmd, cwd=str(ASR_ROOT), check=False)
wall_time = time.perf_counter() - t0

if result.returncode != 0:
    print(f"[m11-test] WARN: root script exit code {result.returncode}")

# 4. Read predictions CSV produced by root script
csv_candidates = list(eval_dir.glob("results_*.csv"))
if not csv_candidates:
    print(f"[m11-test] ERROR: no results_*.csv in {eval_dir}")
    sys.exit(1)
csv_path = csv_candidates[0]
print(f"[m11-test] reading predictions from {csv_path}")

predictions = []
preds_list, labels_list = [], []
with csv_path.open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        # Root script CSV format: idx, fname, hyp, ref, cer, wer (or similar)
        # Auto-detect the columns
        pred = row.get("hyp") or row.get("pred") or row.get("prediction") or ""
        label = row.get("ref") or row.get("label") or row.get("target") or row.get("gt") or ""
        audio = row.get("fname") or row.get("filename") or row.get("audio_path") or row.get("audio") or ""
        preds_list.append(pred)
        labels_list.append(label)
        predictions.append({
            "idx": i, "audio": audio, "pred": pred, "label": label,
            "per_sample_wer": float(row.get("wer", per_sample_wer(pred, label))),
            "per_sample_cer": float(row.get("cer", per_sample_cer(pred, label))),
        })

# 5. Compute aggregated metrics
metrics = compute_test_metrics(preds_list, labels_list)
print(f"[m11-test] WER: {metrics['wer']:.4f}, CER: {metrics['cer']:.4f}")

# 6. Write our JSON
out_dir = args.run_dir / "test_results"
json_path = write_test_results(
    out_dir=out_dir,
    model_id="m11-vanilla-transformer",
    family="Vanilla Transformer (Vaswani 2017)",
    is_paper_model=True, is_user_novel=False,
    run_dir=args.run_dir,
    checkpoint_info=ckpt_info,
    test_set_info={"split": "test", "n_samples": len(preds_list),
                   "audio_root": "data_pkl", "feature_format": "pkl_logmel80"},
    metrics=metrics,
    decoding_info={"method": "greedy_ar", "beam_size": 1, "lm": None,
                   "max_decode_len": args.max_decode_len},
    wall_time_sec=wall_time,
    n_samples=len(preds_list),
    peak_gpu_mb=0.0,
    predictions=predictions,
    extra={"root_eval_csv": str(csv_path),
           "root_eval_dir": str(eval_dir)},
)
print(f"[m11-test] \u2713 {json_path}")
sys.exit(0)
