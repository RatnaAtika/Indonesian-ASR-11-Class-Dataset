"""cahya/wav2vec2-large-xlsr-indonesian FT entry point."""
import sys, subprocess
from pathlib import Path
HERE = Path(__file__).parent
TRAINING = HERE.parent
cmd = ["python3", str(TRAINING / "common/wav2vec2_trainer.py"),
       "--model-id", "cahya/wav2vec2-large-xlsr-indonesian",
       "--run-dir", str(HERE / "runs/run_full"),
       "--epochs", "5", "--batch-size", "8", "--grad-accum", "2",
       "--lr", "5e-5"] + sys.argv[1:]
subprocess.run(cmd, check=False)
