"""ViT-modified-ID test entry point — m12 paper model (USER NOVEL).

1. Run root test_model_vit.py to produce predictions CSV
2. Read CSV, compute aggregated WER/CER/MER/WIL/SER
3. Save machine-readable test_paper.json untuk AI agent

Usage:
    python3 training_conventional/m12_vit_modified/test.py
    python3 training_conventional/m12_vit_modified/test.py \\
      --run-dir training_conventional/m12_vit_modified/runs/run_paper_20260601
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
    cands = sorted([d for d in slot_runs.glob("run_paper_*") if d.is_dir()],
                   key=lambda d: d.stat().st_mtime, reverse=True)
    if not cands:
        cands = sorted([d for d in slot_runs.glob("run_full_*") if d.is_dir()],
                       key=lambda d: d.stat().st_mtime, reverse=True)
    return cands[0] if cands else None


args, extra = parse_args()
if args.run_dir is None:
    args.run_dir = auto_pick_run(HERE / "runs")
    if args.run_dir is None:
        print(f"[m12-test] ERROR: no run found"); sys.exit(1)
print(f"[m12-test] run_dir: {args.run_dir}")

# Find best checkpoint (root script writes best.pth not best.pt)
ckpt_info = find_best_checkpoint(args.run_dir)
if not ckpt_info.get("path"):
    best_pth = args.run_dir / "checkpoints" / "best.pth"
    if best_pth.exists():
        ckpt_info = {"path": str(best_pth), "filename": "best.pth",
                     "format": "pth", "best_wer": None, "best_epoch": None}
    else:
        print(f"[m12-test] ERROR: no checkpoint")
        sys.exit(1)
print(f"[m12-test] checkpoint: {ckpt_info['filename']}")

test_pkl = TC / "data_pkl" / "test.pkl"
spm_model = TC / "spm" / "spm_v7_char.model"
eval_dir = args.run_dir / "eval_greedy"
eval_dir.mkdir(parents=True, exist_ok=True)

cmd = ["python3", str(ASR_ROOT / "test_model_vit.py"),
       "--test-pkl", str(test_pkl),
       "--spm-model", str(spm_model),
       "--checkpoint", ckpt_info["path"],
       "--max-decode-len", str(args.max_decode_len),
       "--outdir", str(eval_dir)] + extra
print(f"[m12-test] cmd: {' '.join(cmd)}")
t0 = time.perf_counter()
result = subprocess.run(cmd, cwd=str(ASR_ROOT), check=False)
wall_time = time.perf_counter() - t0

if result.returncode != 0:
    print(f"[m12-test] WARN: root script exit code {result.returncode}")

csv_candidates = list(eval_dir.glob("results_*.csv"))
if not csv_candidates:
    print(f"[m12-test] ERROR: no results_*.csv in {eval_dir}")
    sys.exit(1)
csv_path = csv_candidates[0]

predictions = []
preds_list, labels_list = [], []
with csv_path.open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        pred = row.get("hyp") or row.get("pred") or row.get("prediction") or ""
        label = row.get("ref") or row.get("label") or row.get("target") or row.get("gt") or ""
        audio = row.get("fname") or row.get("filename") or row.get("audio_path") or row.get("audio") or ""
        preds_list.append(pred); labels_list.append(label)
        predictions.append({
            "idx": i, "audio": audio, "pred": pred, "label": label,
            "per_sample_wer": float(row.get("wer", per_sample_wer(pred, label))),
            "per_sample_cer": float(row.get("cer", per_sample_cer(pred, label))),
        })

metrics = compute_test_metrics(preds_list, labels_list)
print(f"[m12-test] WER: {metrics['wer']:.4f}, CER: {metrics['cer']:.4f}")

out_dir = args.run_dir / "test_results"
json_path = write_test_results(
    out_dir=out_dir,
    model_id="m12-vit-modified-ID",
    family="ViT-modified-ID (Ratna 2026, unpublished)",
    is_paper_model=True,
    is_user_novel=True,           # ★ USER NOVEL
    run_dir=args.run_dir,
    checkpoint_info=ckpt_info,
    test_set_info={"split": "test", "n_samples": len(preds_list),
                   "audio_root": "data_pkl", "feature_format": "pkl_logmel80"},
    metrics=metrics,
    decoding_info={"method": "greedy_ar_with_ctc_aux", "beam_size": 1, "lm": None,
                   "max_decode_len": args.max_decode_len},
    wall_time_sec=wall_time,
    n_samples=len(preds_list),
    peak_gpu_mb=0.0,
    predictions=predictions,
    extra={"root_eval_csv": str(csv_path), "root_eval_dir": str(eval_dir)},
)
print(f"[m12-test] \u2713 {json_path}")
sys.exit(0)
