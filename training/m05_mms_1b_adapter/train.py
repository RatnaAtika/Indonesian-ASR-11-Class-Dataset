"""MMS-1B-all adapter FT entry point."""
import sys, subprocess
from pathlib import Path
HERE = Path(__file__).parent
TRAINING = HERE.parent
cmd = ["python3", str(TRAINING / "common/wav2vec2_trainer.py"),
       "--model-id", "facebook/mms-1b-all",
       "--target-lang", "ind", "--adapter-only",
       "--run-dir", str(HERE / "runs/run_full"),
       "--epochs", "5", "--batch-size", "4", "--grad-accum", "4",
       "--lr", "1e-3"] + sys.argv[1:]
subprocess.run(cmd, check=False)
