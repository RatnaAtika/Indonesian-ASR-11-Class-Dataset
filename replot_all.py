"""Re-plot all 14 ASR model runs with a chosen journal style — single CLI.

Walks `training/m??_*/runs/run_*` and `training_conventional/m??_*/runs/run_*`,
auto-discovers history.json files, and produces journal-ready plots for each.

Usage:
    # Re-plot all smoke runs in IEEE style, output PNG + PDF
    python3 replot_all.py --style ieee --formats png pdf

    # Only full runs
    python3 replot_all.py --style ieee --pattern "run_full*" \\
        --out-root reports/paper_figures_ieee

    # Re-plot one specific model
    python3 replot_all.py --style acm --slot m02_whisper_small

    # All five journal styles in one go (one folder per style)
    for s in ieee acm springer elsevier thesis; do
      python3 replot_all.py --style $s --out-root reports/paper_figures_$s
    done

Outputs go to:
  - default: <run_dir>/plots_<style>/
  - or: <out_root>/<slot>/<run_name>/<style>/
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
from typing import List, Tuple

THIS = Path(__file__).parent
sys.path.insert(0, str(THIS / "training"))
sys.path.insert(0, str(THIS / "training_conventional"))

from common.journal_plotting import replot_run, STYLES


# Discovery roots
DISCOVERY_ROOTS = [
    (THIS / "training",              "modern"),
    (THIS / "training_conventional", "conventional"),
]


def discover_runs(pattern: str = "run_*", slot_filter: str = None) -> List[Tuple[str, Path, str]]:
    """Walk both training trees, find runs matching pattern.
    
    Returns list of (slot_name, run_path, kind) tuples.
    Kind ∈ {modern, conventional}.
    """
    found = []
    for root, kind in DISCOVERY_ROOTS:
        if not root.exists():
            continue
        for slot_dir in sorted(root.iterdir()):
            if not slot_dir.is_dir():
                continue
            slot_name = slot_dir.name
            if slot_filter and slot_filter not in slot_name:
                continue
            runs_dir = slot_dir / "runs"
            if not runs_dir.exists():
                continue
            for run in sorted(runs_dir.glob(pattern)):
                if not run.is_dir():
                    continue
                if not (run / "history.json").exists():
                    continue
                found.append((slot_name, run, kind))
    return found


def parse_args():
    p = argparse.ArgumentParser(description="Re-plot all ASR runs in a journal style")
    p.add_argument("--style", default="plain", choices=list(STYLES.keys()),
                   help="Journal style preset")
    p.add_argument("--formats", nargs="+", default=["png", "pdf"],
                   choices=["png", "pdf", "svg", "eps"])
    p.add_argument("--pattern", default="run_*",
                   help="Glob pattern for run dirs (default: run_*; use 'run_full*' for full only)")
    p.add_argument("--slot", default=None,
                   help="Filter by slot name substring (e.g. 'm02', 'whisper', 'hmm')")
    p.add_argument("--out-root", type=Path, default=None,
                   help="Aggregate output root (default: per-run dir <run>/plots_<style>)")
    p.add_argument("--no-combined", action="store_true")
    p.add_argument("--list-only", action="store_true",
                   help="Just list discovered runs, no plotting")
    return p.parse_args()


def main():
    args = parse_args()
    runs = discover_runs(args.pattern, args.slot)
    print(f"[replot-all] discovered {len(runs)} runs:")
    for slot, run, kind in runs:
        print(f"  [{kind}] {slot}/{run.name}")
    if args.list_only or not runs:
        return 0
    
    print(f"\n[replot-all] style={args.style}, formats={args.formats}")
    if args.out_root:
        print(f"[replot-all] aggregate out_root={args.out_root}")
    print()
    
    t0 = time.perf_counter()
    succeeded, failed = 0, []
    for slot, run, kind in runs:
        if args.out_root:
            out_dir = args.out_root / slot / run.name
        else:
            out_dir = run / f"plots_{args.style}"
        try:
            saved = replot_run(
                run_dir=run, style=args.style, formats=args.formats,
                out_dir=out_dir, include_combined=not args.no_combined,
            )
            n_files = sum(len(v) for v in saved.values())
            print(f"  ✓ {slot}/{run.name}: {len(saved)} plots, {n_files} files → {out_dir}")
            succeeded += 1
        except Exception as e:
            print(f"  ✗ {slot}/{run.name}: {e}")
            failed.append((slot, run, str(e)))
    
    elapsed = time.perf_counter() - t0
    print(f"\n[replot-all] done in {elapsed:.1f}s — {succeeded}/{len(runs)} succeeded")
    if failed:
        print(f"[replot-all] {len(failed)} failed:")
        for slot, run, err in failed:
            print(f"  - {slot}/{run.name}: {err}")
    
    # Write top-level manifest
    if args.out_root:
        args.out_root.mkdir(parents=True, exist_ok=True)
        manifest = {
            "style": args.style,
            "formats": list(args.formats),
            "n_runs": len(runs),
            "n_succeeded": succeeded,
            "n_failed": len(failed),
            "runs": [{"slot": s, "run": str(r), "kind": k} for s, r, k in runs],
        }
        (args.out_root / "_replot_manifest.json").write_text(
            json.dumps(manifest, indent=2, default=str), encoding="utf-8")
        print(f"[replot-all] manifest: {args.out_root / '_replot_manifest.json'}")
    
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
