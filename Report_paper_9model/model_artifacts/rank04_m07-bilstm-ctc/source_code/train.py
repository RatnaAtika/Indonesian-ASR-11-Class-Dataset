"""Bi-LSTM CTC (DeepSpeech-2 from-scratch) entry point."""
import sys, subprocess
from pathlib import Path
HERE = Path(__file__).parent
TRAINING = HERE.parent
cmd = ["python3", str(TRAINING / "common/from_scratch_trainer.py"),
       "--arch", "bilstm",
       "--run-dir", str(HERE / "runs/run_full"),
       "--epochs", "30", "--batch-size", "16", "--lr", "3e-4",
       "--hidden-size", "512", "--num-layers", "5"] + sys.argv[1:]
subprocess.run(cmd, check=False)
