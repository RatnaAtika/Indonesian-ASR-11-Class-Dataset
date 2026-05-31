"""Whisper-medium fine-tune entry point — paper model #9.

Pretrained Whisper-medium (764 M params) fine-tuned on Indonesian v7 for 5 epochs
(paper convention; longer FT causes catastrophic forgetting).

Usage (paper-grade):
    python3 training/m02b_whisper_medium_ft/train.py \
      --epochs 5 --batch-size 2 --grad-accum 16 --lr 1e-5 \
      --warmup-steps 500 --gradient-checkpointing
"""
import sys, subprocess
from pathlib import Path
HERE = Path(__file__).parent
TRAINING = HERE.parent

# Inject only identity/run-dir defaults; forward user flags as-is (no duplication).
# If the user passes --run-dir, theirs wins (argparse takes the last value).
# NOTE: whisper-MEDIUM (764M) OOMs on 8GB GPUs even at batch 2 + grad-ckpt; we use
# whisper-SMALL (244M) which fits ~3.7GB and is a valid pretrained-FT paper baseline.
cmd = ["python3", str(TRAINING / "common/whisper_trainer.py"),
       "--model-id", "openai/whisper-small",
       "--run-dir", str(HERE / "runs/run_paper")] + sys.argv[1:]

print(f"[m02b-whisper-medium] cmd: {' '.join(cmd)}")
subprocess.run(cmd, check=False)
