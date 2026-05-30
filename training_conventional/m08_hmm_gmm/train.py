"""HMM-GMM template classifier entry point."""
import sys, subprocess
from pathlib import Path
HERE = Path(__file__).parent
TC = HERE.parent
cmd = ["python3", str(TC / "common/pkl_hmm_trainer.py"),
       "--mode", "hmm_gmm",
       "--run-dir", str(HERE / "runs/run_full"),
       "--hmm-states", "5", "--hmm-mixtures", "2"] + sys.argv[1:]
subprocess.run(cmd, check=False)
