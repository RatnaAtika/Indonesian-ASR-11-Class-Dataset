"""Standalone plot regeneration script.

Use to update plots from history.json without retraining (e.g., to change
font size, figure size, dpi for paper formatting).

Usage:
    python3 common/regen_plots.py --run-dir <path/to/run> [--fontsize 12 --dpi 200]
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

# Ensure parent in path
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.utils import regenerate_plots


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--fontsize", type=int, default=11)
    p.add_argument("--figsize", nargs=2, type=int, default=[8, 5])
    p.add_argument("--dpi", type=int, default=150)
    p.add_argument("--title-suffix", default="")
    args = p.parse_args()
    
    history = args.run_dir / "history.json"
    if not history.exists():
        print(f"ERROR: history.json not found in {args.run_dir}", file=sys.stderr)
        return 1
    
    style = {"fontsize": args.fontsize, "figsize": tuple(args.figsize), "dpi": args.dpi}
    paths = regenerate_plots(history, args.run_dir / "plots", args.title_suffix, style)
    print("Regenerated plots:")
    for k, p in paths.items():
        print(f"  {k}: {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
