"""Bi-LSTM CTC test entry point — m07 paper model."""
import sys, subprocess
from pathlib import Path
HERE = Path(__file__).parent
TRAINING = HERE.parent
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
        print(f"[m07-test] ERROR: no run found"); sys.exit(1)
cmd = ["python3", str(TRAINING / "common/from_scratch_test.py"),
       "--arch", "bilstm"] + extra_args
print(f"[m07-test] cmd: {' '.join(cmd)}")
subprocess.run(cmd, check=False)
