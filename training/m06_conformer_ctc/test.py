"""Conformer-CTC test entry point — m06 paper model.

Auto-detect best.pt dari run_dir terbaru, jalankan greedy CTC decode
pada test split, save JSON ke <run_dir>/test_results/.

Usage:
    # Default: pakai run_dir terbaru run_paper_*
    python3 training/m06_conformer_ctc/test.py
    
    # Override run_dir:
    python3 training/m06_conformer_ctc/test.py \
      --run-dir training/m06_conformer_ctc/runs/run_paper_20260601
"""
import sys, subprocess
from pathlib import Path

HERE = Path(__file__).parent
TRAINING = HERE.parent

# Auto-pick latest run_paper_* if no --run-dir given
extra_args = sys.argv[1:]
if "--run-dir" not in extra_args:
    runs_dir = HERE / "runs"
    candidates = sorted([d for d in runs_dir.glob("run_paper_*") if d.is_dir()],
                        key=lambda d: d.stat().st_mtime, reverse=True)
    if not candidates:
        candidates = sorted([d for d in runs_dir.glob("run_full_*") if d.is_dir()],
                            key=lambda d: d.stat().st_mtime, reverse=True)
    if candidates:
        extra_args = ["--run-dir", str(candidates[0])] + extra_args
    else:
        print(f"[m06-test] ERROR: no run_paper_* / run_full_* found in {runs_dir}")
        sys.exit(1)

cmd = ["python3", str(TRAINING / "common/from_scratch_test.py"),
       "--arch", "conformer"] + extra_args
print(f"[m06-test] cmd: {' '.join(cmd)}")
subprocess.run(cmd, check=False)
