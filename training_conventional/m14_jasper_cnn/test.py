"""Jasper-mini test entry point — m14 (secondary, not paper-9 but ready)."""
import sys, subprocess
from pathlib import Path
HERE = Path(__file__).parent
TC = HERE.parent
extra = sys.argv[1:]
if "--run-dir" not in extra:
    runs = HERE / "runs"
    cands = sorted([d for d in runs.glob("run_paper_*") if d.is_dir()],
                   key=lambda d: d.stat().st_mtime, reverse=True)
    if not cands:
        cands = sorted([d for d in runs.glob("run_full_*") if d.is_dir()],
                       key=lambda d: d.stat().st_mtime, reverse=True)
    if cands:
        extra = ["--run-dir", str(cands[0])] + extra
    else:
        print(f"[m14-test] ERROR: no run"); sys.exit(1)
cmd = ["python3", str(TC / "common/pkl_cnn_ctc_test.py"),
       "--arch", "jasper"] + extra
print(f"[m14-test] cmd: {' '.join(cmd)}")
subprocess.run(cmd, check=False)
