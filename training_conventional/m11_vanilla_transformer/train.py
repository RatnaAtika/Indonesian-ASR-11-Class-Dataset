"""Vanilla Transformer (Attention Is All You Need) wrapper.

Calls the project-root train_model_vanilla.py against our v7 .pkl features
and SPM. Default run_dir is timestamped (run_full_<YYYYMMDD>_<HHMMSS>) so
each run gets a fresh folder \u2014 hasil run sebelumnya TIDAK terhapus.

Wrapper merge logic: user-provided flags override wrapper defaults (no
duplicate args di cmd line).

Usage:
    # Default paper-grade
    python3 m11_vanilla_transformer/train.py

    # Override hyperparameters
    python3 m11_vanilla_transformer/train.py --epochs 50 --lr 3e-4
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
    """Pop --run-dir + collect user-provided flags as dict (for dedup)."""
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--run-dir", type=Path, default=None)
    known, remaining = p.parse_known_args(argv)
    return known.run_dir, remaining


def extract_user_flags(remaining):
    """Return set of flag names (e.g. '--epochs') user provided in remaining argv."""
    flags = set()
    for tok in remaining:
        if tok.startswith("--"):
            flags.add(tok.split("=")[0])  # handle --flag=value form too
    return flags


# Wrapper defaults (paper-grade). User flags override these.
DEFAULTS = [
    ("--epochs", "30"),                       # paper-grade fairness (was 80)
    ("--batch-size", "16"),
    ("--lr", "5e-4"),
    ("--d-model", "192"),
    ("--nhead", "4"),
    ("--num-layers", "6"),
    ("--ff", "256"),
    ("--dropout", "0.1"),
    ("--input-dim", "80"),
    ("--seed", "2026"),
]
DEFAULT_FLAGS_BOOL = ["--amp"]               # boolean flags (no value)


train_pkl = TC / "data_pkl" / "train.pkl"
val_pkl = TC / "data_pkl" / "valid.pkl"
spm_model = TC / "spm" / "spm_v7_char.model"

# Resolve run_dir
user_run_dir, extra = parse_extra(sys.argv[1:])
if user_run_dir:
    run_dir = unique_run_dir(user_run_dir)
else:
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = HERE / "runs" / f"run_full_{stamp}"
    run_dir = unique_run_dir(run_dir)
run_dir.mkdir(parents=True, exist_ok=True)
print(f"[m11-vanilla] resolved run_dir: {run_dir}")

ckpt_dir = run_dir / "checkpoints"
ckpt_dir.mkdir(exist_ok=True)
ckpt = ckpt_dir / "best.pth"

# Build cmd: dedup wrapper defaults vs user flags
user_flags = extract_user_flags(extra)
merged_defaults = []
for flag, value in DEFAULTS:
    if flag not in user_flags:
        merged_defaults += [flag, value]
for flag in DEFAULT_FLAGS_BOOL:
    if flag not in user_flags:
        merged_defaults.append(flag)

cmd = ([
    "python3", str(ASR_ROOT / "train_model_vanilla.py"),
    "--train-pkl", str(train_pkl),
    "--val-pkl", str(val_pkl),
    "--spm-model", str(spm_model),
    "--outdir", str(run_dir),
    "--checkpoint", str(ckpt),
] + merged_defaults + extra)

print(f"[m11-vanilla] cwd={ASR_ROOT}")
print(f"[m11-vanilla] cmd: {' '.join(cmd)}")
result = subprocess.run(cmd, cwd=str(ASR_ROOT), check=False)
sys.exit(result.returncode)
