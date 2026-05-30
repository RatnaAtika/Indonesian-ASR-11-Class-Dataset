"""Multi-model overlay plots in journal style.

Reads multiple history.json files and overlays their curves on the same axes
for paper Figure 2 (training-curve comparison) and Figure 3 (final-metric bars).

Usage:
    # Overlay Whisper-tiny vs ViT vs Vanilla Transformer training curves (IEEE style)
    python3 replot_compare.py \\
        --runs training/m01_whisper_tiny/runs/run_full_20260601 \\
                training_conventional/m11_vanilla_transformer/runs/run_full_20260601 \\
                training_conventional/m12_vit_modified/runs/run_full_20260601 \\
        --labels "Whisper-tiny" "Vanilla TF" "ViT-modified-ID" \\
        --style ieee --out reports/paper_compare_ieee/transformer_vs_modern.png \\
        --metrics loss wer cer

    # All 14 models WER-by-epoch overlay (might be busy; consider --max-models 5)
    python3 replot_compare.py --auto-discover --metric wer \\
        --style thesis --out reports/all14_wer_thesis.pdf
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

THIS = Path(__file__).parent
sys.path.insert(0, str(THIS / "training"))
sys.path.insert(0, str(THIS / "training_conventional"))
from common.journal_plotting import STYLES, apply_style, get_style


def load_history(run_dir: Path):
    h = run_dir / "history.json"
    if not h.exists():
        return None
    with h.open(encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get("epochs", [])


def get_label(run_dir: Path) -> str:
    """Auto-derive label from meta.json or run path."""
    m = run_dir / "meta.json"
    if m.exists():
        try:
            with m.open() as f:
                meta = json.load(f)
            return f"{meta.get('model_id', run_dir.parent.parent.name)}"
        except Exception:
            pass
    return run_dir.parent.parent.name  # slot folder name


def discover_all_runs(pattern: str = "run_full*") -> List[Path]:
    found = []
    for root_name in ("training", "training_conventional"):
        root = THIS / root_name
        if not root.exists():
            continue
        for slot in sorted(root.iterdir()):
            if not slot.is_dir():
                continue
            runs = slot / "runs"
            if not runs.exists():
                continue
            for r in sorted(runs.glob(pattern)):
                if (r / "history.json").exists():
                    found.append(r)
    return found


def overlay_metric(histories, labels, metric: str, ax, cfg):
    """Overlay one metric (e.g. 'wer') across all histories on one axis."""
    n = len(histories)
    for i, (h, lab) in enumerate(zip(histories, labels)):
        xs, ys = [], []
        for e in h:
            v = e.get(metric)
            if v is not None:
                xs.append(e["epoch"]); ys.append(v)
        if not xs:
            continue
        color = cfg["colors"][i % len(cfg["colors"])]
        ls = cfg["linestyles"][i % len(cfg["linestyles"])]
        ax.plot(xs, ys, color=color, linestyle=ls, label=lab,
                marker="o", markersize=3)
    ax.set_xlabel("Epoch")
    pretty_metric = {
        "wer": "WER", "cer": "CER",
        "train_loss": "Train Loss", "val_loss": "Val Loss",
        "train_acc": "Train Acc", "val_acc": "Val Acc",
        "lr": "Learning rate", "gpu_mb": "GPU MB",
    }.get(metric, metric)
    ax.set_ylabel(pretty_metric)
    ax.legend(frameon=False, fontsize=cfg["rc"].get("legend.fontsize", 8))


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--runs", nargs="*", type=Path, default=None,
                   help="One or more run directories (each must contain history.json)")
    p.add_argument("--labels", nargs="*", default=None,
                   help="Optional labels parallel to --runs (auto-derived if omitted)")
    p.add_argument("--auto-discover", action="store_true",
                   help="Auto-discover all runs matching --pattern (overrides --runs)")
    p.add_argument("--pattern", default="run_full*")
    p.add_argument("--metrics", nargs="+",
                   default=["wer", "cer", "train_loss", "val_loss"],
                   help="Metrics to overlay (one panel per metric)")
    p.add_argument("--style", default="plain", choices=list(STYLES.keys()))
    p.add_argument("--formats", nargs="+", default=["png", "pdf"])
    p.add_argument("--out", type=Path, required=True,
                   help="Output file path (extension overridden by --formats)")
    p.add_argument("--title", default=None,
                   help="Optional figure title")
    return p.parse_args()


def main():
    args = parse_args()
    
    if args.auto_discover:
        runs = discover_all_runs(args.pattern)
    else:
        runs = list(args.runs or [])
    
    if not runs:
        print("[replot-compare] no runs to plot. Use --runs or --auto-discover.")
        return 1
    
    histories, labels = [], []
    for i, r in enumerate(runs):
        h = load_history(Path(r))
        if not h:
            print(f"  [warn] no history in {r}, skipping")
            continue
        histories.append(h)
        if args.labels and i < len(args.labels):
            labels.append(args.labels[i])
        else:
            labels.append(get_label(Path(r)))
    
    if not histories:
        print("[replot-compare] no usable histories found")
        return 1
    
    print(f"[replot-compare] overlaying {len(histories)} models on {len(args.metrics)} metric(s):")
    for h, lab in zip(histories, labels):
        print(f"  - {lab} ({len(h)} epochs)")
    
    apply_style(args.style)
    cfg = get_style(args.style)
    
    n_metrics = len(args.metrics)
    if n_metrics == 1:
        fig, ax = plt.subplots(figsize=cfg["figsize"])
        overlay_metric(histories, labels, args.metrics[0], ax, cfg)
        if args.title:
            ax.set_title(args.title)
    else:
        cols = min(n_metrics, 2)
        rows = (n_metrics + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols,
                                 figsize=(cfg["figsize_double"][0],
                                          cfg["figsize_double"][1] * rows / 1.2))
        axes = axes.flatten() if hasattr(axes, "flatten") else [axes]
        for i, metric in enumerate(args.metrics):
            overlay_metric(histories, labels, metric, axes[i], cfg)
            axes[i].set_title(f"({chr(ord('a')+i)}) {metric}")
        for j in range(len(args.metrics), len(axes)):
            axes[j].axis("off")
        if args.title:
            fig.suptitle(args.title)
    plt.tight_layout()
    
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    base = out.with_suffix("")
    for fmt in args.formats:
        target = base.with_suffix(f".{fmt}")
        fig.savefig(target, format=fmt, bbox_inches="tight")
        print(f"  ✓ {target}")
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
