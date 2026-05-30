"""GMM-HMM-DNN 3-stage hybrid entry point."""
import sys, subprocess
from pathlib import Path
HERE = Path(__file__).parent
TC = HERE.parent
cmd = ["python3", str(TC / "common/pkl_hmm_trainer.py"),
       "--mode", "gmm_hmm_dnn",
       "--run-dir", str(HERE / "runs/run_full"),
       "--hmm-states", "5", "--hmm-mixtures", "2",
       "--dnn-hidden", "512", "--dnn-layers", "4", "--dnn-context", "5",
       "--dnn-epochs", "5"] + sys.argv[1:]
subprocess.run(cmd, check=False)
