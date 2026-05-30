"""Wav2Letter CNN-CTC entry point."""
import sys, subprocess
from pathlib import Path
HERE = Path(__file__).parent
TC = HERE.parent
cmd = ["python3", str(TC / "common/pkl_cnn_ctc_trainer.py"),
       "--arch", "wav2letter",
       "--run-dir", str(HERE / "runs/run_full"),
       "--epochs", "30", "--batch-size", "16", "--lr", "3e-4"] + sys.argv[1:]
subprocess.run(cmd, check=False)
