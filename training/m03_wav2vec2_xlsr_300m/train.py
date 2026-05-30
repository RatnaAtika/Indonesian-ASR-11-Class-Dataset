"""wav2vec2-XLS-R-300M FT entry point."""
import sys, subprocess
from pathlib import Path
HERE = Path(__file__).parent
TRAINING = HERE.parent
cmd = ["python3", str(TRAINING / "common/wav2vec2_trainer.py"),
       "--model-id", "facebook/wav2vec2-xls-r-300m",
       "--run-dir", str(HERE / "runs/run_full"),
       "--epochs", "5", "--batch-size", "8", "--grad-accum", "2",
       "--lr", "1e-4"] + sys.argv[1:]
subprocess.run(cmd, check=False)
