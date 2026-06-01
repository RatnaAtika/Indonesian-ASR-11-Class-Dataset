"""Whisper-SMALL fine-tune entry point — Option A (paper model #9, 8GB-friendly).

Pretrained Whisper-small (244M params) fine-tuned on Indonesian v7 for 5 epochs
(pretrained-FT convention; longer FT causes catastrophic forgetting).
Fits ~3.7GB GPU, runs on an RTX 4060 Laptop 8GB.

Every run creates a NEW timestamped folder under runs/ (old runs are preserved).
Pass --run-dir to override, or --resume to continue an existing run.

Usage (paper-grade):
    python3 training/m02b_whisper_small_ft/train.py \
      --epochs 5 --batch-size 8 --grad-accum 4 --lr 1e-5 \
      --warmup-steps 500 --gradient-checkpointing --seed 42
"""
import sys, subprocess, datetime
from pathlib import Path
HERE = Path(__file__).parent
TRAINING = HERE.parent

# New timestamped run-dir per invocation unless the user supplies --run-dir/--resume.
argv = sys.argv[1:]
inject_run_dir = ("--run-dir" not in argv and "--resume" not in argv)
cmd = ["python3", str(TRAINING / "common/whisper_trainer.py"),
       "--model-id", "openai/whisper-small"]
if inject_run_dir:
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    cmd += ["--run-dir", str(HERE / "runs" / f"run_paper_{stamp}")]
cmd += argv

print(f"[m02b-whisper-small] cmd: {' '.join(cmd)}")
subprocess.run(cmd, check=False)
