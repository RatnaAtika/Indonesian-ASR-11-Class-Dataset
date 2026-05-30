"""ViT-modified-ID \u2605 \u2014 User's own original architecture (Ratna 2026, unpublished).

Wrapper that calls the project-root train_model_vit.py against our v7 .pkl
features. Default run_dir timestamped, user flags override wrapper defaults
(no duplicate args).

PAPER-GRADE: epoch=30, num-layers=6 (matches m11). Untuk extended training
reproduction (200 epoch / 2-layer), pass `--epochs 200 --num-layers 2`.

Usage:
    # Default paper-grade
    python3 m12_vit_modified/train.py

    # Override
    python3 m12_vit_modified/train.py --epochs 200 --num-layers 2
"""
import sys, subprocess, argparse, datetime
from pathlib import Path

HERE = Path(__file__).parent
PROJECT_ROOT = HERE.parent.parent
ASR_ROOT = PROJECT_ROOT.parent
TC = HERE.parent

sys.path.insert(0, str(TC))
from common.utils import unique_run_dir


def parse_extra(argv):
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--run-dir", type=Path, default=None)
    known, remaining = p.parse_known_args(argv)
    return known.run_dir, remaining


def extract_user_flags(remaining):
    flags = set()
    for tok in remaining:
        if tok.startswith("--"):
            flags.add(tok.split("=")[0])
    return flags


DEFAULTS = [
    ("--epochs", "30"),                    # paper-grade (was 200)
    ("--batch-size", "16"),
    ("--lr", "5e-4"),
    ("--d-model", "192"),
    ("--nhead", "4"),
    ("--num-layers", "6"),                  # matches m11 (was 2)
    ("--ff", "256"),
    ("--dropout", "0.1"),
    ("--input-dim", "80"),
    ("--lambda-ctc", "0.1"),
    ("--scheduler", "plateau"),
    ("--seed", "42"),
]
DEFAULT_FLAGS_BOOL = ["--amp", "--specaug"]


train_pkl = TC / "data_pkl" / "train.pkl"
val_pkl = TC / "data_pkl" / "valid.pkl"
spm_model = TC / "spm" / "spm_v7_char.model"

user_run_dir, extra = parse_extra(sys.argv[1:])
if user_run_dir:
    run_dir = unique_run_dir(user_run_dir)
else:
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = HERE / "runs" / f"run_full_{stamp}"
    run_dir = unique_run_dir(run_dir)
run_dir.mkdir(parents=True, exist_ok=True)
print(f"[m12-vit-modified-ID] resolved run_dir: {run_dir}")

ckpt_dir = run_dir / "checkpoints"; ckpt_dir.mkdir(exist_ok=True)
ckpt = ckpt_dir / "best.pth"

user_flags = extract_user_flags(extra)
merged_defaults = []
for flag, value in DEFAULTS:
    if flag not in user_flags:
        merged_defaults += [flag, value]
for flag in DEFAULT_FLAGS_BOOL:
    if flag not in user_flags:
        merged_defaults.append(flag)

cmd = ([
    "python3", str(ASR_ROOT / "train_model_vit.py"),
    "--train-pkl", str(train_pkl),
    "--val-pkl", str(val_pkl),
    "--spm-model", str(spm_model),
    "--outdir", str(run_dir),
    "--checkpoint", str(ckpt),
] + merged_defaults + extra)

print(f"[m12-vit] cmd: {' '.join(cmd)}")
result = subprocess.run(cmd, cwd=str(ASR_ROOT), check=False)
sys.exit(result.returncode)
