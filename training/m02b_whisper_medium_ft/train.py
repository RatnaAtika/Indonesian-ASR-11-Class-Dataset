"""Whisper-MEDIUM fine-tune entry point — Option B (large-GPU, secondary model).

Pretrained Whisper-medium (764M params) fine-tuned on Indonesian v7 for 5 epochs
(pretrained-FT convention; longer FT causes catastrophic forgetting).
Needs ~>12GB GPU: OOMs on an 8GB RTX 4060 Laptop even at batch 2 + grad-ckpt
(verified). Use a larger GPU (A100/3090/4090) or Colab Pro+. Results saved here
under runs/. For the 8GB-friendly paper run use Option A: m02b_whisper_small_ft/.

Usage (large GPU):
    python3 training/m02b_whisper_medium_ft/train.py \
      --epochs 5 --batch-size 2 --grad-accum 16 --lr 1e-5 \
      --warmup-steps 500 --gradient-checkpointing --seed 42
"""
import sys, subprocess
from pathlib import Path
HERE = Path(__file__).parent
TRAINING = HERE.parent

cmd = ["python3", str(TRAINING / "common/whisper_trainer.py"),
       "--model-id", "openai/whisper-medium",
       "--run-dir", str(HERE / "runs/run_paper")] + sys.argv[1:]

print(f"[m02b-whisper-medium] cmd: {' '.join(cmd)}")
subprocess.run(cmd, check=False)
