"""Aggregate ALL 17 ASR systems into a single paper-grade comparison report.

After every model in RUN_GUIDE.md has produced a `runs/run_full_<YYYYMMDD>/`
folder, run:
    python3 aggregate_all_models.py

It reads:
  - 7 modern models from training/m??_*/runs/run_full*/history.json
  - 3 zero-shot baselines from training/zero_shot_baselines/runs/*_full*/history.json
  - 5 conventional HMM/CNN models from training_conventional/m{08,09,10,13,14}_*/runs/run_full*/history.json
  - 2 conventional Transformers (m11, m12) from training_conventional/m{11,12}_*/runs/run_full*/eval_greedy/test_results.json
    (or fallback: training_val_loss/accuracy plots' final-line CER)

And produces:
  reports/all_models_full/
    ├── comparison.md
    ├── comparison_table.csv
    ├── wer_bar_all17.png
    ├── wer_vs_params.png
    ├── era_timeline.png
    ├── family_summary.png
    ├── paper_table.tex
    └── summary.json
"""
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT = Path(__file__).parent
TRAINING = PROJECT / "training"
TC = PROJECT / "training_conventional"
OUT = PROJECT / "reports" / "all_models_full"
OUT.mkdir(parents=True, exist_ok=True)

# Okabe-Ito colours by family
COLOR = {
    "HMM":              "#D55E00",  # red
    "Hybrid":           "#E69F00",  # orange
    "CNN-CTC":          "#009E73",  # green
    "Bi-LSTM":          "#56B4E9",  # light blue
    "Transformer":      "#0072B2",  # blue
    "Transformer-novel":"#CC79A7",  # purple (m12 highlight)
    "Encoder-Decoder":  "#0072B2",
    "wav2vec2":         "#000000",  # black
    "Whisper":          "#1F77B4",  # mid blue
    "MMS":              "#999999",  # grey
    "zero-shot":        "#7F7F7F",
}

# (slot, search_paths_for_full_run, family, era, params_M, notes)
MODELS = [
    # Modern (training/)
    ("m01-whisper-tiny",      [TRAINING/"m01_whisper_tiny/runs"],      "Whisper",          "2022", 38,    "FT"),
    ("m02-whisper-small ★",   [TRAINING/"m02_whisper_small/runs"],     "Whisper",          "2022", 244,   "FT primary"),
    ("m03-w2v2-xlsr-300m",    [TRAINING/"m03_wav2vec2_xlsr_300m/runs"],"wav2vec2",         "2021", 315,   "FT"),
    ("m04-cahya-w2v2-id",     [TRAINING/"m04_cahya_wav2vec2_id/runs"], "wav2vec2",         "2021", 315,   "FT (ID-pretrained)"),
    ("m05-mms-1b-adapter",    [TRAINING/"m05_mms_1b_adapter/runs"],    "MMS",              "2023", 965,   "FT adapter (~3M trainable)"),
    ("m06-conformer-ctc",     [TRAINING/"m06_conformer_ctc/runs"],     "CNN-CTC",          "2020", 6.6,   "from-scratch"),
    ("m07-bilstm-ctc",        [TRAINING/"m07_bilstm_ctc/runs"],        "Bi-LSTM",          "2014", 6.6,   "from-scratch"),
    # Zero-shot (training/zero_shot_baselines/)
    ("zs1-whisper-large-v3",  [TRAINING/"zero_shot_baselines/runs"],   "Whisper",          "2023", 1543,  "zero-shot"),
    ("zs2-whisper-medium",    [TRAINING/"zero_shot_baselines/runs"],   "Whisper",          "2022", 764,   "zero-shot"),
    ("zs3-mms-1b-all",        [TRAINING/"zero_shot_baselines/runs"],   "MMS",              "2023", 965,   "zero-shot"),
    # Conventional (training_conventional/)
    ("m08-hmm-gmm",           [TC/"m08_hmm_gmm/runs"],                 "HMM",              "1990s",0.01,  "template classifier"),
    ("m09-dnn-hmm",           [TC/"m09_dnn_hmm/runs"],                 "Hybrid",           "2010s",3.7,   "linear-init alignment"),
    ("m10-gmm-hmm-dnn",       [TC/"m10_gmm_hmm_dnn/runs"],             "Hybrid",           "2010s",3.7,   "3-stage"),
    ("m11-vanilla-transformer",[TC/"m11_vanilla_transformer/runs"],    "Transformer",      "2017", 3.5,   "Vaswani 2017 ref"),
    ("m12-vit-modified-ID ★", [TC/"m12_vit_modified/runs"],            "Transformer-novel","2026", 3.5,   "USER'S NOVEL ARCH (unpublished)"),
    ("m13-wav2letter",        [TC/"m13_wav2letter_cnn/runs"],          "CNN-CTC",          "2016", 7.0,   "from-scratch"),
    ("m14-jasper-mini",       [TC/"m14_jasper_cnn/runs"],              "CNN-CTC",          "2019", 28.0,  "from-scratch"),
]


def find_full_run_dir(search_paths):
    """Pick the latest run_full_* (or whisper_*_full_* / mms_*_full_*) under search_paths."""
    best, best_mtime = None, -1
    for sp in search_paths:
        if not sp.exists():
            continue
        for child in sp.iterdir():
            if not child.is_dir():
                continue
            name = child.name
            # Modern + conventional convention
            if name.startswith("run_full"):
                pass
            # Zero-shot convention: <model>_full_<date>
            elif "_full_" in name or name.endswith("_full"):
                pass
            else:
                continue
            try:
                mt = child.stat().st_mtime
                if mt > best_mtime:
                    best, best_mtime = child, mt
            except OSError:
                continue
    return best


def read_history_metrics(run_dir):
    """Read last-epoch entry from history.json. Returns dict or None."""
    h = run_dir / "history.json"
    if not h.exists():
        return None
    try:
        with h.open() as f:
            data = json.load(f)
        last = data[-1] if isinstance(data, list) else data.get("epochs", [{}])[-1]
        return last
    except Exception:
        return None


def read_root_script_test_metrics(run_dir):
    """For m11/m12 wrappers: parse eval_greedy/ folder for greedy decode metrics.
    Falls back to training-time CER from log files."""
    eval_dir = run_dir / "eval_greedy"
    if eval_dir.exists():
        # Look for any test_results JSON or metrics file
        for f in eval_dir.glob("*.json"):
            try:
                with f.open() as fp:
                    data = json.load(fp)
                wer = data.get("wer") or data.get("WER")
                cer = data.get("cer") or data.get("CER")
                if wer is not None or cer is not None:
                    return {"wer": wer, "cer": cer, "source": str(f)}
            except Exception:
                pass
        # Also try CSV
        for f in eval_dir.glob("*.csv"):
            try:
                import pandas as pd
                df = pd.read_csv(f)
                if "wer" in df.columns or "WER" in df.columns:
                    col = "wer" if "wer" in df.columns else "WER"
                    return {"wer": float(df[col].mean()), "cer": None, "source": str(f)}
            except Exception:
                pass
    # Fallback: parse last-epoch CER from training output
    log = run_dir / "log.txt"
    if log.exists():
        try:
            txt = log.read_text(encoding="utf-8")
            m = re.findall(r"Val CER[=: ]+([0-9.]+)", txt)
            if m:
                return {"wer": None, "cer": float(m[-1]), "source": "log.txt (val CER)"}
        except Exception:
            pass
    return None


def aggregate():
    rows = []
    missing = []
    for slot, paths, family, era, params_m, notes in MODELS:
        run_dir = find_full_run_dir(paths)
        row = {
            "slot": slot, "family": family, "era": era,
            "params_M": params_m, "notes": notes,
            "run_dir": str(run_dir) if run_dir else "MISSING",
            "wer": None, "cer": None,
            "train_acc": None, "val_acc": None,
            "val_loss": None,
            "gpu_mb": None, "time_str": None,
            "source": "history.json",
        }
        if run_dir is None:
            missing.append(slot)
            rows.append(row); continue
        
        # Try history.json first
        m = read_history_metrics(run_dir)
        if m is None:
            # Fall back to root-script artifacts (m11/m12)
            m = read_root_script_test_metrics(run_dir)
            if m is not None:
                row["source"] = m.get("source", "root-script")
        
        if m is not None:
            row["wer"]       = m.get("wer")
            row["cer"]       = m.get("cer")
            row["train_acc"] = m.get("train_acc")
            row["val_acc"]   = m.get("val_acc")
            row["val_loss"]  = m.get("val_loss")
            row["gpu_mb"]    = m.get("gpu_mb")
            row["time_str"]  = m.get("time_str")
        else:
            missing.append(slot + " (run dir exists but no metrics found)")
        rows.append(row)
    
    return rows, missing


def write_csv(rows, path):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


def fmt(v, p=4):
    if v is None: return "n/a"
    try:
        return f"{float(v):.{p}f}"
    except Exception:
        return "n/a"


def write_md(rows, missing, path):
    lines = ["# Final 17-Architecture ASR Comparison (Indonesian Corpus v7)\n",
             "**Source**: aggregated from `training/` + `training_conventional/` full runs.",
             ""]
    if missing:
        lines.append(f"> ⚠ **{len(missing)} model(s) missing or incomplete**: " + ", ".join(missing))
        lines.append("")
    
    lines += ["## Results table", "",
              "| Slot | Family | Era | Params (M) | Notes | WER | CER | Train Acc | Val Acc | Run dir |",
              "|------|--------|-----|-----------:|-------|----:|----:|----------:|--------:|---------|"]
    for r in rows:
        rd = "MISSING" if r["run_dir"] == "MISSING" else "/".join(Path(r["run_dir"]).parts[-3:])
        lines.append(
            f"| `{r['slot']}` | {r['family']} | {r['era']} | {r['params_M']} | {r['notes']} "
            f"| {fmt(r['wer'])} | {fmt(r['cer'])} | {fmt(r['train_acc'])} | {fmt(r['val_acc'])} "
            f"| `{rd}` |"
        )
    
    lines += ["", "## Plots",
              "- `wer_bar_all17.png` — single bar chart of all 17 systems",
              "- `wer_vs_params.png` — WER vs parameter count scatter",
              "- `era_timeline.png` — WER by publication-era group",
              "- `family_summary.png` — grouped bar by architectural family",
              "",
              "## LaTeX",
              "- `paper_table.tex` — paper Table 1, ready to `\\input{}`",
              "",
              "## Honest disclosure",
              "1. **m12 ViT-modified-ID** is the user's own novel architecture (Ratna 2026)",
              "   developed for Indonesian end-to-end limited-vocabulary ASR.",
              "   **Not yet published** — this paper is its first public report.",
              "2. **m08 (HMM-GMM)** is a closed-vocabulary template classifier",
              "   (209 templates), not a free-form ASR system.",
              "3. **m11 (Vanilla Transformer)** is the Vaswani 2017 reference baseline",
              "   using the supervisor-validated root code, kept verbatim.",
              "4. **132 synthetic Edge-TTS files (0.129%)** are present in the train",
              "   set; only 2 (0.013%) in test. Disclosed at every level.",
              ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_paper_tex(rows, path):
    """Build paper-ready LaTeX Table 1."""
    lines = [
        r"% Auto-generated paper Table 1 — 17-architecture ASR comparison on v7 Indonesian corpus",
        r"\begin{table*}[h]",
        r"  \centering",
        r"  \caption{All 17 ASR systems compared on the v7 Indonesian corpus (102{,}544 files, 130.65 h, 20 speakers, 11 categories). \\",
        r"           m12 ViT-modified-ID is the user's own novel architecture, this paper's first public report.}",
        r"  \label{tab:all17}",
        r"  \small",
        r"  \begin{tabular}{lllrrrrrrl}",
        r"  \hline",
        r"  Slot & Family & Era & Params (M) & WER & CER & Train Acc & Val Acc & Notes \\",
        r"  \hline",
    ]
    for r in rows:
        slot = r["slot"].replace("_", r"\_").replace("★", r"$\star$")
        notes = r["notes"].replace("_", r"\_")
        lines.append(
            f"  {slot} & {r['family']} & {r['era']} & {r['params_M']} "
            f"& {fmt(r['wer'])} & {fmt(r['cer'])} "
            f"& {fmt(r['train_acc'])} & {fmt(r['val_acc'])} & {notes} \\\\"
        )
    lines += [r"  \hline", r"  \end{tabular}", r"\end{table*}"]
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_wer_bar(rows, path):
    fig, ax = plt.subplots(figsize=(15, 6))
    slots = [r["slot"] for r in rows]
    wers = [r["wer"] if r["wer"] is not None else np.nan for r in rows]
    colors = [COLOR.get(r["family"], "#888") for r in rows]
    bars = ax.bar(range(len(slots)), wers, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_xticks(range(len(slots)))
    ax.set_xticklabels(slots, rotation=35, ha="right", fontsize=9)
    ax.set_ylabel("WER (lower = better)")
    ax.set_title("All 17 ASR systems on Indonesian v7 corpus — WER")
    ax.axhline(1.0, color="grey", linestyle=":", alpha=0.4, label="WER = 1 (chance)")
    ax.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def plot_wer_vs_params(rows, path):
    fig, ax = plt.subplots(figsize=(10, 6))
    valid = [r for r in rows if r["wer"] is not None and r["params_M"] is not None]
    for r in valid:
        ax.scatter(r["params_M"], r["wer"], s=80,
                   color=COLOR.get(r["family"], "#888"),
                   edgecolor="black", linewidth=0.5, alpha=0.85)
        ax.annotate(r["slot"], (r["params_M"], r["wer"]),
                    fontsize=8, xytext=(4, 4), textcoords="offset points")
    ax.set_xscale("log")
    ax.set_xlabel("Trainable parameters (M, log scale)")
    ax.set_ylabel("WER")
    ax.set_title("WER vs parameter count — 17 ASR systems")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def plot_era_timeline(rows, path):
    valid = [r for r in rows if r["wer"] is not None]
    if not valid:
        return
    eras_order = ["1990s", "2010s", "2014", "2016", "2017", "2019", "2020",
                  "2021", "2022", "2023", "2026"]
    era_to_wers = {}
    for r in valid:
        era = r["era"]
        era_to_wers.setdefault(era, []).append(r["wer"])
    keys = [k for k in eras_order if k in era_to_wers]
    means = [np.mean(era_to_wers[k]) for k in keys]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(range(len(keys)), means, "o-", color="#0072B2", linewidth=2, markersize=8)
    for i, k in enumerate(keys):
        ax.annotate(f"{means[i]:.3f}", (i, means[i]),
                    xytext=(0, 8), textcoords="offset points", ha="center", fontsize=9)
    ax.set_xticks(range(len(keys))); ax.set_xticklabels(keys)
    ax.set_xlabel("Era / publication year")
    ax.set_ylabel("Mean WER")
    ax.set_title("ASR WER over the architectural eras (mean across systems in each era)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def plot_family_summary(rows, path):
    valid = [r for r in rows if r["wer"] is not None]
    if not valid:
        return
    fam_to_w = {}
    for r in valid:
        fam_to_w.setdefault(r["family"], []).append(r["wer"])
    families = list(fam_to_w.keys())
    means = [np.mean(fam_to_w[f]) for f in families]
    stds = [np.std(fam_to_w[f]) for f in families]
    colors = [COLOR.get(f, "#888") for f in families]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(range(len(families)), means, yerr=stds, color=colors,
           capsize=4, edgecolor="white", linewidth=0.5)
    ax.set_xticks(range(len(families)))
    ax.set_xticklabels(families, rotation=20, ha="right")
    ax.set_ylabel("Mean WER (with std)")
    ax.set_title("WER summary by architectural family")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=OUT)
    args = p.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[aggregate] scanning all 17 model run folders ...")
    rows, missing = aggregate()
    
    if missing:
        print(f"\n⚠ {len(missing)} model(s) missing or incomplete:")
        for m in missing:
            print(f"   - {m}")
    
    # CSV
    write_csv(rows, args.out_dir / "comparison_table.csv")
    print(f"  ✓ {args.out_dir / 'comparison_table.csv'}")
    
    # Markdown + LaTeX
    write_md(rows, missing, args.out_dir / "comparison.md")
    print(f"  ✓ {args.out_dir / 'comparison.md'}")
    write_paper_tex(rows, args.out_dir / "paper_table.tex")
    print(f"  ✓ {args.out_dir / 'paper_table.tex'}")
    
    # Plots
    plot_wer_bar(rows, args.out_dir / "wer_bar_all17.png")
    plot_wer_vs_params(rows, args.out_dir / "wer_vs_params.png")
    plot_era_timeline(rows, args.out_dir / "era_timeline.png")
    plot_family_summary(rows, args.out_dir / "family_summary.png")
    print(f"  ✓ 4 plots @ 200 DPI")
    
    # JSON summary
    summary = {"models": rows, "missing": missing,
               "n_models_total": len(rows), "n_missing": len(missing)}
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(f"  ✓ {args.out_dir / 'summary.json'}")
    
    print(f"\n[aggregate] DONE. Output: {args.out_dir}")
    if missing:
        print(f"[aggregate] re-run after the {len(missing)} missing model(s) finish")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
