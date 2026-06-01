"""Whisper-MEDIUM fine-tune entry point — Option B (large-GPU, secondary model).

Pretrained Whisper-medium (764M params) fine-tuned on Indonesian v7 for 5 epochs
(pretrained-FT convention; longer FT causes catastrophic forgetting).
Needs ~>12GB GPU: OOMs on an 8GB RTX 4060 Laptop even at batch 2 + grad-ckpt
(verified). Use a larger GPU (A100/3090/4090) or Colab Pro+. For the 8GB-friendly
paper run use Option A: m02b_whisper_small_ft/.

Every run creates a NEW timestamped folder under runs/ (old runs are preserved).
Pass --run-dir to override, or --resume to continue an existing run.

Usage (large GPU):
    python3 training/m02b_whisper_medium_ft/train.py \
      --epochs 5 --batch-size 2 --grad-accum 16 --lr 1e-5 \
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
       "--model-id", "openai/whisper-medium"]
if inject_run_dir:
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    cmd += ["--run-dir", str(HERE / "runs" / f"run_paper_{stamp}")]
cmd += argv

print(f"[m02b-whisper-medium] cmd: {' '.join(cmd)}")
subprocess.run(cmd, check=False)
