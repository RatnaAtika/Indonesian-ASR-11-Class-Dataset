"""Whisper-small FT entry point (PRIMARY)."""
import sys, subprocess
from pathlib import Path
HERE = Path(__file__).parent
TRAINING = HERE.parent
cmd = ["python3", str(TRAINING / "common/whisper_trainer.py"),
       "--model-id", "openai/whisper-small",
       "--run-dir", str(HERE / "runs/run_full"),
       "--epochs", "3", "--batch-size", "4", "--grad-accum", "4",
       "--lr", "1e-5"] + sys.argv[1:]
subprocess.run(cmd, check=False)
