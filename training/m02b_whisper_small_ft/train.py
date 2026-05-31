"""Whisper-SMALL fine-tune entry point — Option A (paper model #9, 8GB-friendly).

Pretrained Whisper-small (244M params) fine-tuned on Indonesian v7 for 5 epochs
(pretrained-FT convention; longer FT causes catastrophic forgetting).
Fits ~3.7GB GPU, runs on an RTX 4060 Laptop 8GB. Results saved here under runs/.

Usage (paper-grade):
    python3 training/m02b_whisper_small_ft/train.py \
      --epochs 5 --batch-size 8 --grad-accum 4 --lr 1e-5 \
      --warmup-steps 500 --gradient-checkpointing --seed 42
"""
import sys, subprocess
from pathlib import Path
HERE = Path(__file__).parent
TRAINING = HERE.parent

cmd = ["python3", str(TRAINING / "common/whisper_trainer.py"),
       "--model-id", "openai/whisper-small",
       "--run-dir", str(HERE / "runs/run_paper")] + sys.argv[1:]

print(f"[m02b-whisper-small] cmd: {' '.join(cmd)}")
subprocess.run(cmd, check=False)
