"""m08_hmm_gmm test entry point — paper model (mode=hmm_gmm)."""
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
        print(f"[m08_hmm_gmm-test] ERROR: no run found"); sys.exit(1)
cmd = ["python3", str(TC / "common/pkl_hmm_test.py"),
       "--mode", "hmm_gmm"] + extra
print(f"[m08_hmm_gmm-test] cmd: {' '.join(cmd)}")
subprocess.run(cmd, check=False)
