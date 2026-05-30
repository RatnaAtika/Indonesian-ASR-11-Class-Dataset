"""Whisper-tiny FT entry point."""
import sys, subprocess
from pathlib import Path
HERE = Path(__file__).parent
TRAINING = HERE.parent
cmd = ["python3", str(TRAINING / "common/whisper_trainer.py"),
       "--model-id", "openai/whisper-tiny",
       "--run-dir", str(HERE / "runs/run_full"),
       "--epochs", "5", "--batch-size", "8", "--grad-accum", "2",
       "--lr", "5e-6"] + sys.argv[1:]
subprocess.run(cmd, check=False)
