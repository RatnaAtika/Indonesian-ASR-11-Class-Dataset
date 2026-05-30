"""Journal-style replot library — re-plot any saved history.json without retraining.

Use after training to produce paper-ready figures matching specific journal
formatting requirements (IEEE, ACM, Springer, Elsevier, thesis, plain).

Each plotting function reads ONLY history.json (and optionally meta.json).
No model checkpoints or training data are required.

Style presets define:
  - figsize (tuned for column width per journal)
  - font family + size
  - line styles (dashed for B&W print)
  - tick / spine / grid policy
  - default DPI

Usage (CLI):
    python3 -m common.journal_plotting --run-dir <run_dir> --style ieee \\
        --formats png pdf svg --out-dir <run_dir>/plots_ieee

Usage (Python API):
    from common.journal_plotting import replot_run, STYLES
    replot_run(run_dir="m02_whisper_small/runs/run_full_20260601",
               style="ieee", formats=["png", "pdf"])
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams


# ============================================================
# Journal style presets
# ============================================================
# Width references (rough):
#   IEEE 1-col = 3.487 in, 2-col = 7.16 in
#   ACM 1-col = 3.33 in,  2-col = 7.0 in
#   Springer LNCS = 4.6 in
#   Elsevier 1-col = 3.5 in, 2-col = 7.5 in
STYLES: Dict[str, Dict] = {
    "ieee": {
        "name": "IEEE (1-col, sans-serif, BW-friendly)",
        "rc": {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "xtick.labelsize": 7, "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "lines.linewidth": 1.2,
            "axes.linewidth": 0.7,
            "grid.linewidth": 0.4,
            "axes.grid": True, "grid.alpha": 0.35,
            "axes.spines.top": False, "axes.spines.right": False,
            "savefig.dpi": 600, "figure.dpi": 100,
        },
        "figsize": (3.487, 2.6),
        "figsize_double": (7.16, 3.0),
        "linestyles": ["-", "--", "-.", ":"],
        "colors": ["#000000", "#444444", "#888888", "#bbbbbb"],
    },
    "acm": {
        "name": "ACM (1-col, serif, color-friendly)",
        "rc": {
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8, "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "lines.linewidth": 1.4,
            "axes.linewidth": 0.8,
            "grid.linewidth": 0.45,
            "axes.grid": True, "grid.alpha": 0.3,
            "axes.spines.top": False, "axes.spines.right": False,
            "savefig.dpi": 600, "figure.dpi": 100,
        },
        "figsize": (3.33, 2.5),
        "figsize_double": (7.0, 3.2),
        "linestyles": ["-", "--", "-.", ":"],
        "colors": ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00"],
    },
    "springer": {
        "name": "Springer LNCS (single-col, serif)",
        "rc": {
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "CMU Serif", "Times"],
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8, "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "lines.linewidth": 1.3,
            "axes.linewidth": 0.7,
            "axes.grid": True, "grid.alpha": 0.3,
            "savefig.dpi": 600, "figure.dpi": 100,
        },
        "figsize": (4.6, 3.0),
        "figsize_double": (4.6, 3.0),
        "linestyles": ["-", "--", "-.", ":"],
        "colors": ["#0072B2", "#D55E00", "#009E73", "#CC79A7"],
    },
    "elsevier": {
        "name": "Elsevier (1-col, sans-serif, color OK)",
        "rc": {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8, "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "lines.linewidth": 1.4,
            "axes.linewidth": 0.8,
            "axes.grid": True, "grid.alpha": 0.3,
            "axes.spines.top": False, "axes.spines.right": False,
            "savefig.dpi": 600, "figure.dpi": 100,
        },
        "figsize": (3.5, 2.7),
        "figsize_double": (7.5, 3.3),
        "linestyles": ["-", "--", "-.", ":"],
        "colors": ["#005A9C", "#E65100", "#2E7D32", "#6A1B9A"],
    },
    "thesis": {
        "name": "Thesis / dissertation (full-page)",
        "rc": {
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "CMU Serif"],
            "font.size": 11,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "xtick.labelsize": 10, "ytick.labelsize": 10,
            "legend.fontsize": 10,
            "lines.linewidth": 1.6,
            "axes.linewidth": 0.9,
            "axes.grid": True, "grid.alpha": 0.3,
            "savefig.dpi": 300, "figure.dpi": 100,
        },
        "figsize": (6.5, 4.0),
        "figsize_double": (13.0, 4.0),
        "linestyles": ["-", "--", "-.", ":"],
        "colors": ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"],
    },
    "plain": {
        "name": "Plain default (matplotlib defaults)",
        "rc": {
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 9, "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "lines.linewidth": 1.5,
            "axes.grid": True, "grid.alpha": 0.3,
            "savefig.dpi": 300, "figure.dpi": 100,
        },
        "figsize": (8.0, 5.0),
        "figsize_double": (12.0, 5.0),
        "linestyles": ["-", "--", "-.", ":"],
        "colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
    },
    "data_in_brief": {
        "name": "Data in Brief / Elsevier (DiB compliant: PDF vector, viridis, 600 DPI, line+marker)",
        "rc": {
            # DiB body uses Times-like serif for prose; figures can be sans-serif as long as readable.
            # We choose serif to match Elsevier final-typeset look.
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman", "Times", "CMU Serif"],
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8, "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "lines.linewidth": 1.4,
            "lines.markersize": 4,
            "axes.linewidth": 0.8,
            "grid.linewidth": 0.4,
            "axes.grid": True, "grid.alpha": 0.3,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "savefig.dpi": 600,                  # DiB raster halftone min 300 dpi; we go 600 for safety
            "figure.dpi": 100,
            "savefig.transparent": False,
            "savefig.facecolor": "white",
            # Embed PDF fonts inside file (Elsevier requires)
            "pdf.fonttype": 42,                  # TrueType (rather than Type-3 — type-3 is rejected by Elsevier)
            "ps.fonttype": 42,
            "text.usetex": False,
        },
        "figsize": (3.54, 2.6),                  # DiB single-col = 90 mm = 3.54 in
        "figsize_double": (7.48, 3.0),           # DiB double-col / full page = 190 mm = 7.48 in
        # Line patterns sufficient on their own (BW-print friendly), color is a bonus.
        "linestyles": ["-", "--", "-.", ":", (0, (3, 1, 1, 1))],
        # Okabe-Ito (color-blind safe) avoiding red-vs-green only
        "colors": ["#0072B2", "#E69F00", "#009E73", "#CC79A7",
                   "#56B4E9", "#D55E00", "#F0E442", "#000000"],
        # Markers for >3 series (DiB requires markers in addition to color)
        "markers": ["o", "s", "D", "^", "v", "<", ">", "P"],
        # Banned colormaps for heatmap-style plots (jet, hsv — not perceptually uniform)
        "banned_cmaps": ["jet", "hsv"],
        "recommended_cmap": "viridis",           # or "cividis"
    },
}


def apply_style(style: str):
    """Apply matplotlib rcParams for the given style."""
    if style not in STYLES:
        raise ValueError(f"Unknown style '{style}'. Available: {list(STYLES.keys())}")
    rcParams.update(STYLES[style]["rc"])


def get_style(style: str) -> Dict:
    if style not in STYLES:
        raise ValueError(f"Unknown style '{style}'. Available: {list(STYLES.keys())}")
    return STYLES[style]


# ============================================================
# Generic plotting helpers
# ============================================================
def _save_all_formats(fig, out_path_no_ext: Path, formats: Sequence[str]):
    """Save fig in all requested formats (png, pdf, svg)."""
    for fmt in formats:
        out = out_path_no_ext.with_suffix(f".{fmt}")
        fig.savefig(out, format=fmt, bbox_inches="tight")


def _series(history: List[Dict], key: str):
    epochs = [e["epoch"] for e in history if e.get(key) is not None]
    vals = [e[key] for e in history if e.get(key) is not None]
    return epochs, vals


def plot_loss(history, out_no_ext, style, formats):
    """Train + Val loss vs epoch."""
    cfg = get_style(style)
    fig, ax = plt.subplots(figsize=cfg["figsize"])
    train_x, train_y = _series(history, "train_loss")
    val_x, val_y = _series(history, "val_loss")
    if train_x:
        ax.plot(train_x, train_y, color=cfg["colors"][0], linestyle=cfg["linestyles"][0],
                label="Train Loss", marker="o", markersize=3)
    if val_x:
        ax.plot(val_x, val_y, color=cfg["colors"][1], linestyle=cfg["linestyles"][1],
                label="Val Loss", marker="s", markersize=3)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title("Training and Validation Loss")
    ax.legend(frameon=False)
    _save_all_formats(fig, out_no_ext, formats)
    plt.close(fig)


def plot_acc(history, out_no_ext, style, formats):
    """Train + Val accuracy vs epoch."""
    cfg = get_style(style)
    fig, ax = plt.subplots(figsize=cfg["figsize"])
    train_x, train_y = _series(history, "train_acc")
    val_x, val_y = _series(history, "val_acc")
    if train_x:
        ax.plot(train_x, train_y, color=cfg["colors"][0], linestyle=cfg["linestyles"][0],
                label="Train Acc", marker="o", markersize=3)
    if val_x:
        ax.plot(val_x, val_y, color=cfg["colors"][1], linestyle=cfg["linestyles"][1],
                label="Val Acc", marker="s", markersize=3)
    ax.set_xlabel("Epoch"); ax.set_ylabel("Accuracy")
    ax.set_title("Training and Validation Accuracy")
    ax.set_ylim(0, 1)
    ax.legend(frameon=False, loc="lower right")
    _save_all_formats(fig, out_no_ext, formats)
    plt.close(fig)


def plot_wer_cer(history, out_no_ext, style, formats):
    """WER + CER vs epoch (lower = better)."""
    cfg = get_style(style)
    fig, ax = plt.subplots(figsize=cfg["figsize"])
    wer_x, wer_y = _series(history, "wer")
    cer_x, cer_y = _series(history, "cer")
    if wer_x:
        ax.plot(wer_x, wer_y, color=cfg["colors"][0], linestyle=cfg["linestyles"][0],
                label="WER", marker="o", markersize=3)
    if cer_x:
        ax.plot(cer_x, cer_y, color=cfg["colors"][1], linestyle=cfg["linestyles"][1],
                label="CER", marker="s", markersize=3)
    ax.set_xlabel("Epoch"); ax.set_ylabel("Error rate")
    ax.set_title("Word and Character Error Rate")
    ax.legend(frameon=False, loc="upper right")
    _save_all_formats(fig, out_no_ext, formats)
    plt.close(fig)


def plot_lr(history, out_no_ext, style, formats):
    """Learning rate schedule vs epoch."""
    cfg = get_style(style)
    fig, ax = plt.subplots(figsize=cfg["figsize"])
    lr_x, lr_y = _series(history, "lr")
    if not lr_x:
        plt.close(fig); return
    ax.plot(lr_x, lr_y, color=cfg["colors"][0], linestyle=cfg["linestyles"][0],
            marker="o", markersize=3)
    ax.set_xlabel("Epoch"); ax.set_ylabel("Learning rate")
    ax.set_title("Learning rate schedule")
    if any(v > 0 for v in lr_y):
        ax.set_yscale("log")
    _save_all_formats(fig, out_no_ext, formats)
    plt.close(fig)


def plot_gpu(history, out_no_ext, style, formats):
    """Peak GPU MB vs epoch."""
    cfg = get_style(style)
    fig, ax = plt.subplots(figsize=cfg["figsize"])
    x, y = _series(history, "gpu_mb")
    if not x:
        plt.close(fig); return
    ax.plot(x, y, color=cfg["colors"][0], linestyle=cfg["linestyles"][0],
            marker="o", markersize=3)
    ax.set_xlabel("Epoch"); ax.set_ylabel("Peak GPU memory (MB)")
    ax.set_title("Peak GPU memory per epoch")
    _save_all_formats(fig, out_no_ext, formats)
    plt.close(fig)


def plot_throughput(history, out_no_ext, style, formats):
    cfg = get_style(style)
    fig, ax = plt.subplots(figsize=cfg["figsize"])
    x, y = _series(history, "throughput_samples_per_sec")
    if not x:
        plt.close(fig); return
    ax.plot(x, y, color=cfg["colors"][0], linestyle=cfg["linestyles"][0],
            marker="o", markersize=3)
    ax.set_xlabel("Epoch"); ax.set_ylabel("Throughput (samples / sec)")
    ax.set_title("Training throughput")
    _save_all_formats(fig, out_no_ext, formats)
    plt.close(fig)


def plot_combined_4panel(history, out_no_ext, style, formats):
    """4-panel summary (loss / acc / wer-cer / lr) for paper Figure 1."""
    cfg = get_style(style)
    fig, axes = plt.subplots(2, 2, figsize=cfg["figsize_double"])
    
    # Panel a: Loss
    ax = axes[0, 0]
    tx, ty = _series(history, "train_loss"); vx, vy = _series(history, "val_loss")
    if tx: ax.plot(tx, ty, color=cfg["colors"][0], linestyle=cfg["linestyles"][0],
                    label="Train", marker="o", markersize=3)
    if vx: ax.plot(vx, vy, color=cfg["colors"][1], linestyle=cfg["linestyles"][1],
                    label="Val", marker="s", markersize=3)
    ax.set_xlabel("Epoch"); ax.set_ylabel("Loss"); ax.set_title("(a) Loss")
    if tx or vx: ax.legend(frameon=False)
    
    # Panel b: Acc
    ax = axes[0, 1]
    tx, ty = _series(history, "train_acc"); vx, vy = _series(history, "val_acc")
    if tx: ax.plot(tx, ty, color=cfg["colors"][0], linestyle=cfg["linestyles"][0],
                    label="Train", marker="o", markersize=3)
    if vx: ax.plot(vx, vy, color=cfg["colors"][1], linestyle=cfg["linestyles"][1],
                    label="Val", marker="s", markersize=3)
    ax.set_xlabel("Epoch"); ax.set_ylabel("Accuracy"); ax.set_title("(b) Accuracy")
    ax.set_ylim(0, 1)
    if tx or vx: ax.legend(frameon=False, loc="lower right")
    
    # Panel c: WER + CER
    ax = axes[1, 0]
    wx, wy = _series(history, "wer"); cx, cy = _series(history, "cer")
    if wx: ax.plot(wx, wy, color=cfg["colors"][0], linestyle=cfg["linestyles"][0],
                    label="WER", marker="o", markersize=3)
    if cx: ax.plot(cx, cy, color=cfg["colors"][1], linestyle=cfg["linestyles"][1],
                    label="CER", marker="s", markersize=3)
    ax.set_xlabel("Epoch"); ax.set_ylabel("Error rate"); ax.set_title("(c) WER and CER")
    if wx or cx: ax.legend(frameon=False)
    
    # Panel d: LR
    ax = axes[1, 1]
    lx, ly = _series(history, "lr")
    if lx:
        ax.plot(lx, ly, color=cfg["colors"][0], linestyle=cfg["linestyles"][0],
                marker="o", markersize=3)
        if any(v > 0 for v in ly):
            ax.set_yscale("log")
    ax.set_xlabel("Epoch"); ax.set_ylabel("Learning rate"); ax.set_title("(d) LR schedule")
    
    plt.tight_layout()
    _save_all_formats(fig, out_no_ext, formats)
    plt.close(fig)


# ============================================================
# Main replot driver
# ============================================================
def replot_run(run_dir: Path, style: str = "plain",
               formats: Sequence[str] = ("png", "pdf"),
               out_dir: Optional[Path] = None,
               include_combined: bool = True) -> Dict[str, List[Path]]:
    """Re-plot all standard figures for a single model run.
    
    Args:
        run_dir: directory containing history.json
        style: one of STYLES.keys()
        formats: any subset of {png, pdf, svg, eps}
        out_dir: where to write (default: run_dir / f"plots_{style}")
        include_combined: also produce 4-panel summary
    
    Returns dict: {plot_name: [Path...]} of saved files.
    """
    run_dir = Path(run_dir)
    history_path = run_dir / "history.json"
    if not history_path.exists():
        raise FileNotFoundError(f"history.json not found in {run_dir}")
    with history_path.open(encoding="utf-8") as f:
        history = json.load(f)
    if isinstance(history, dict):
        history = history.get("epochs", [])
    
    if out_dir is None:
        out_dir = run_dir / f"plots_{style}"
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    apply_style(style)
    
    saved = {}
    plotters = [
        ("loss", plot_loss),
        ("acc", plot_acc),
        ("wer_cer", plot_wer_cer),
        ("lr", plot_lr),
        ("gpu_mb", plot_gpu),
        ("throughput", plot_throughput),
    ]
    if include_combined:
        plotters.append(("combined_4panel", plot_combined_4panel))
    
    for name, fn in plotters:
        try:
            base = out_dir / name
            fn(history, base, style, formats)
            saved[name] = [base.with_suffix(f".{fmt}") for fmt in formats]
        except Exception as e:
            print(f"  [warn] {name}: {e}")
    
    # Save replay metadata
    meta = {
        "run_dir": str(run_dir),
        "style": style,
        "formats": list(formats),
        "n_epochs": len(history),
        "history_path": str(history_path),
        "out_dir": str(out_dir),
    }
    (out_dir / "_replay_meta.json").write_text(
        json.dumps(meta, indent=2, default=str), encoding="utf-8")
    
    return saved


# ============================================================
# CLI
# ============================================================
def parse_args():
    p = argparse.ArgumentParser(description="Re-plot training history in journal style")
    p.add_argument("--run-dir", type=Path, default=None,
                   help="Run directory containing history.json (required unless --list-styles)")
    p.add_argument("--style", default="plain", choices=list(STYLES.keys()),
                   help="Journal style preset")
    p.add_argument("--formats", nargs="+", default=["png", "pdf"],
                   choices=["png", "pdf", "svg", "eps"])
    p.add_argument("--out-dir", type=Path, default=None,
                   help="Output dir (default: <run_dir>/plots_<style>)")
    p.add_argument("--no-combined", action="store_true",
                   help="Skip 4-panel combined plot")
    p.add_argument("--list-styles", action="store_true",
                   help="List available styles and exit")
    return p.parse_args()


def main():
    args = parse_args()
    if args.list_styles:
        print("Available journal styles:")
        for k, v in STYLES.items():
            print(f"  {k:10s}  {v['name']:50s}  figsize={v['figsize']}")
        return 0
    if args.run_dir is None:
        print("ERROR: --run-dir is required (use --list-styles to view styles)")
        return 2
    
    saved = replot_run(args.run_dir, style=args.style,
                       formats=args.formats, out_dir=args.out_dir,
                       include_combined=not args.no_combined)
    print(f"\n[journal-plot] Replotted {len(saved)} figures in '{args.style}' style:")
    for name, paths in saved.items():
        for p in paths:
            print(f"  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
