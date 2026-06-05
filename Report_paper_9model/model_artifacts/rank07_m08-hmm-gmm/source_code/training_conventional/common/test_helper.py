"""Shared test infrastructure untuk paper benchmark.

Setiap test.py per slot menulis JSON dengan schema TestResult (machine-readable
oleh AI agent untuk auto-generate paper report).

Schema:
    {
      "model_id": str,                  # e.g., "m07-bilstm-ctc"
      "family": str,                    # e.g., "Bi-LSTM CTC"
      "is_paper_model": bool,           # apakah masuk 9-model paper
      "is_user_novel": bool,            # apakah arsitektur user (m12)
      "checkpoint": str,                # path ke best.pt
      "checkpoint_filename": str,       # e.g., "best_wer0p2345_e012.pt"
      "best_train_wer": float,          # WER terbaik selama training (dari history)
      "best_train_epoch": int,          # epoch terbaik
      "test_set": {
        "split": "test",
        "n_samples": int,
        "audio_root": str,
        "feature_format": "raw" | "pkl"
      },
      "metrics": {
        "wer": float,                   # word error rate
        "cer": float,                   # character error rate
        "mer": float,                   # match error rate (jiwer)
        "wil": float,                   # word information lost (jiwer)
        "ser": float                    # sentence error rate (1 - exact-match rate)
      },
      "decoding": {
        "method": "greedy_ctc" | "greedy_ar" | "viterbi_template",
        "beam_size": int,
        "lm": null | str,
        "max_decode_len": int
      },
      "wall_time_sec": float,
      "throughput_samples_per_sec": float,
      "peak_gpu_mb": float,
      "predictions_csv": str,           # path ke CSV all predictions
      "sample_predictions": [           # 10 sample for paper appendix
        {"idx": 0, "audio": "...", "pred": "...", "label": "...",
         "per_sample_wer": float, "per_sample_cer": float}
      ],
      "config": {...},                  # training hyperparameters dari config.json
      "training_meta": {...},           # env snapshot dari meta.json
      "timestamp": str,                 # ISO 8601
      "test_environment": {...}         # current env snapshot
    }

Output ke <run_dir>/test_results/test_paper.json
"""
from __future__ import annotations
import csv, json, sys, time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable

import numpy as np
import jiwer

# Allow import dari training/common/utils
THIS = Path(__file__).parent
sys.path.insert(0, str(THIS.parent))


def compute_test_metrics(predictions: List[str], labels: List[str]) -> Dict[str, float]:
    """Compute WER + CER + MER + WIL + SER on entire test set."""
    if not predictions or not labels or len(predictions) != len(labels):
        return {"wer": 1.0, "cer": 1.0, "mer": 1.0, "wil": 1.0, "ser": 1.0}

    # Strip + lowercase for fair comparison (Indonesian text-norm)
    norm_p = [(p or "").strip().lower() for p in predictions]
    norm_l = [(l or "").strip().lower() for l in labels]

    # Filter empty pairs (avoid jiwer ZeroDivisionError)
    pairs = [(p, l) for p, l in zip(norm_p, norm_l) if l]
    if not pairs:
        return {"wer": 1.0, "cer": 1.0, "mer": 1.0, "wil": 1.0, "ser": 1.0}
    norm_p, norm_l = zip(*pairs)

    refs = list(norm_l)
    hyps = list(norm_p)
    try:
        # jiwer>=3/4 removed compute_measures(); process_words is the stable API.
        measures = jiwer.process_words(refs, hyps)
        wer = float(measures.wer)
        mer = float(measures.mer)
        wil = float(measures.wil)
    except Exception:
        try:
            wer = float(jiwer.wer(refs, hyps))
        except Exception:
            wer = 1.0
        try:
            mer = float(jiwer.mer(refs, hyps))
        except Exception:
            mer = wer
        try:
            wil = float(jiwer.wil(refs, hyps))
        except Exception:
            wil = wer

    try:
        cer = float(jiwer.cer(refs, hyps))
    except Exception:
        cer = 1.0

    # Sentence error rate (1 - exact-match rate)
    n_correct = sum(1 for p, l in zip(norm_p, norm_l) if p == l)
    ser = 1.0 - (n_correct / max(len(norm_p), 1))

    return {"wer": wer, "cer": cer, "mer": mer, "wil": wil, "ser": ser}


def per_sample_wer(pred: str, label: str) -> float:
    if not label or not label.strip():
        return 1.0 if pred.strip() else 0.0
    try:
        return float(jiwer.wer([label.lower().strip()], [pred.lower().strip()]))
    except Exception:
        return 1.0


def per_sample_cer(pred: str, label: str) -> float:
    if not label or not label.strip():
        return 1.0 if pred.strip() else 0.0
    try:
        return float(jiwer.cer([label.lower().strip()], [pred.lower().strip()]))
    except Exception:
        return 1.0


def find_best_checkpoint(run_dir: Path) -> Dict:
    """Locate the best checkpoint dalam run_dir/checkpoints/.

    Strategy:
    1. Cari `best.pt` (current pointer) jika ada
    2. Else cari `best_wer*_e*.pt` dengan WER terkecil
    3. Else cari `best_wer*_final.pkl` (HMM)
    4. Else fallback ke epoch terakhir

    Returns dict with: path, filename, format ('pt'|'pkl'), best_wer, best_epoch
    """
    ckpt_dir = run_dir / "checkpoints"
    if not ckpt_dir.exists():
        return {"path": None, "format": None, "error": "checkpoints/ not found"}

    # Strategy 1: best.pt or best.pkl
    for name in ("best.pt", "best.pkl"):
        p = ckpt_dir / name
        if p.exists():
            fmt = "pt" if name.endswith(".pt") else "pkl"
            return _resolve_best_meta(p, fmt, ckpt_dir)

    # Strategy 2: best_wer*_e*.pt with lowest WER
    best_pts = sorted(ckpt_dir.glob("best_wer*_e*.pt"))
    if best_pts:
        # Filename format: best_wer0p2345_e012.pt → wer 0.2345 epoch 12
        def _extract_wer(p):
            try:
                stem = p.stem  # best_wer0p2345_e012
                v = stem.split("_wer")[1].split("_e")[0].replace("p", ".")
                return float(v)
            except Exception:
                return float("inf")
        best_pt = min(best_pts, key=_extract_wer)
        return _resolve_best_meta(best_pt, "pt", ckpt_dir)

    # Strategy 3: best_wer*_final.pkl (HMM)
    final_pkls = sorted(ckpt_dir.glob("best_wer*_final.pkl"))
    if final_pkls:
        return _resolve_best_meta(final_pkls[0], "pkl", ckpt_dir)

    # Strategy 4: epoch_NNN.pt — pick the epoch with best (lowest) val WER from
    # history.json when available; else fall back to the last epoch. This protects
    # paper integrity when best.pt was not written (e.g. interrupted/legacy runs):
    # never report a worse-than-best checkpoint.
    epoch_pts = sorted(ckpt_dir.glob("epoch_*.pt"))
    if epoch_pts:
        chosen = epoch_pts[-1]
        hist_p = run_dir / "history.json"
        if hist_p.exists():
            try:
                import json as _json
                rows = _json.loads(hist_p.read_text(encoding="utf-8"))
                rows = rows if isinstance(rows, list) else rows.get("epochs", [])
                best_row = min((r for r in rows if r.get("wer") is not None),
                               key=lambda r: r["wer"], default=None)
                if best_row is not None:
                    cand = ckpt_dir / f"epoch_{int(best_row['epoch']):03d}.pt"
                    if cand.exists():
                        chosen = cand
            except Exception:
                pass
        return _resolve_best_meta(chosen, "pt", ckpt_dir)

    # Strategy 5: HF Trainer checkpoints (checkpoint-NNN/)
    hf_ckpts = sorted([d for d in ckpt_dir.iterdir() if d.is_dir() and d.name.startswith("checkpoint-")])
    if hf_ckpts:
        return {"path": str(hf_ckpts[-1]), "filename": hf_ckpts[-1].name,
                "format": "hf_dir", "best_wer": None, "best_epoch": None}

    return {"path": None, "format": None, "error": "no checkpoints found"}


def _resolve_best_meta(p: Path, fmt: str, ckpt_dir: Path) -> Dict:
    """Extract WER + epoch from filename pattern."""
    info = {"path": str(p), "filename": p.name, "format": fmt,
            "best_wer": None, "best_epoch": None}
    name = p.name
    if "best_wer" in name:
        try:
            v_str = name.split("_wer")[1].split("_")[0].replace("p", ".")
            info["best_wer"] = float(v_str)
        except Exception:
            pass
        if "_e" in name:
            try:
                e_str = name.split("_e")[1].split(".")[0]
                info["best_epoch"] = int(e_str)
            except Exception:
                pass
    return info


def load_history_summary(run_dir: Path) -> Dict:
    """Read history.json + meta.json untuk inject ke test results."""
    summary = {"best_train_wer": None, "best_train_epoch": None,
               "n_epochs_trained": 0, "training_meta": {}}

    h_path = run_dir / "history.json"
    if h_path.exists():
        try:
            with h_path.open() as f:
                h = json.load(f)
            entries = h if isinstance(h, list) else h.get("epochs", [])
            summary["n_epochs_trained"] = len(entries)
            valid_wers = [(e.get("wer"), e.get("epoch", 0))
                          for e in entries if e.get("wer") is not None]
            if valid_wers:
                best_wer, best_ep = min(valid_wers, key=lambda x: x[0])
                summary["best_train_wer"] = float(best_wer)
                summary["best_train_epoch"] = int(best_ep)
        except Exception:
            pass

    m_path = run_dir / "meta.json"
    if m_path.exists():
        try:
            with m_path.open() as f:
                summary["training_meta"] = json.load(f)
        except Exception:
            pass

    return summary


def capture_test_environment() -> Dict:
    """Snapshot env saat testing (untuk reproducibility section)."""
    import sys, platform
    env = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "timestamp": datetime.now().isoformat(),
    }
    for lib in ("torch", "transformers", "librosa", "soundfile",
                "sentencepiece", "hmmlearn", "jiwer", "numpy"):
        try:
            mod = __import__(lib)
            env[f"{lib}_version"] = getattr(mod, "__version__", "unknown")
        except ImportError:
            pass
    try:
        import torch as _t
        if _t.cuda.is_available():
            env["cuda_device"] = _t.cuda.get_device_name(0)
            env["cuda_version"] = getattr(_t.version, "cuda", "unknown")
    except Exception:
        pass
    return env


def write_test_results(out_dir: Path,
                       model_id: str, family: str,
                       is_paper_model: bool, is_user_novel: bool,
                       run_dir: Path,
                       checkpoint_info: Dict,
                       test_set_info: Dict,
                       metrics: Dict[str, float],
                       decoding_info: Dict,
                       wall_time_sec: float,
                       n_samples: int,
                       peak_gpu_mb: float,
                       predictions: List[Dict],
                       extra: Optional[Dict] = None) -> Path:
    """Write JSON + CSV + sample-preds.txt per-test-result.

    JSON path: <out_dir>/test_paper.json (single source of truth for AI agent)
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Read training history + meta
    history_summary = load_history_summary(run_dir)

    # Read training config
    cfg_path = run_dir / "config.json"
    config = {}
    if cfg_path.exists():
        try:
            with cfg_path.open() as f:
                config = json.load(f)
        except Exception:
            pass

    # Sample predictions for paper appendix (10 representative)
    sample_preds = []
    if predictions:
        # Take 10 evenly spaced samples
        n = min(10, len(predictions))
        if n > 0:
            indices = np.linspace(0, len(predictions) - 1, n).astype(int)
            for i in indices:
                p = predictions[i]
                sample_preds.append({
                    "idx": int(p.get("idx", i)),
                    "audio": p.get("audio", ""),
                    "pred": p.get("pred", ""),
                    "label": p.get("label", ""),
                    "per_sample_wer": float(p.get("per_sample_wer", 0)),
                    "per_sample_cer": float(p.get("per_sample_cer", 0)),
                })

    # Throughput
    throughput = round(n_samples / max(wall_time_sec, 1e-6), 2)

    # Build full result
    result = {
        "model_id": model_id,
        "family": family,
        "is_paper_model": is_paper_model,
        "is_user_novel": is_user_novel,
        "checkpoint": checkpoint_info.get("path"),
        "checkpoint_filename": checkpoint_info.get("filename"),
        "best_train_wer": history_summary.get("best_train_wer"),
        "best_train_epoch": history_summary.get("best_train_epoch"),
        "n_epochs_trained": history_summary.get("n_epochs_trained"),
        "test_set": test_set_info,
        "metrics": metrics,
        "decoding": decoding_info,
        "wall_time_sec": round(wall_time_sec, 2),
        "throughput_samples_per_sec": throughput,
        "peak_gpu_mb": round(peak_gpu_mb, 1),
        "predictions_csv": str(out_dir / "predictions.csv"),
        "sample_predictions": sample_preds,
        "config": config,
        "training_meta": history_summary.get("training_meta", {}),
        "timestamp": datetime.now().isoformat(),
        "test_environment": capture_test_environment(),
    }
    if extra:
        result.update(extra)

    # Save JSON (machine-readable, single source for AI agent)
    json_path = out_dir / "test_paper.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str, ensure_ascii=False)

    # Save predictions CSV
    csv_path = out_dir / "predictions.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        if predictions:
            writer = csv.DictWriter(f, fieldnames=list(predictions[0].keys()))
            writer.writeheader()
            writer.writerows(predictions)

    # Human-readable summary
    summary = (
        f"# Test Results — {model_id}\n\n"
        f"**Family**: {family}\n"
        f"**Paper model**: {'yes' if is_paper_model else 'no'}\n"
        f"**User novel**: {'yes ★' if is_user_novel else 'no'}\n\n"
        f"## Metrics (test set, n={n_samples}, greedy decoding, no LM)\n\n"
        f"- **WER**: {metrics['wer']:.4f}\n"
        f"- **CER**: {metrics['cer']:.4f}\n"
        f"- **MER**: {metrics['mer']:.4f}\n"
        f"- **WIL**: {metrics['wil']:.4f}\n"
        f"- **SER**: {metrics['ser']:.4f}\n\n"
        f"## Performance\n\n"
        f"- Wall time: {wall_time_sec:.1f} s ({wall_time_sec/60:.1f} min)\n"
        f"- Throughput: {throughput:.2f} samples/sec\n"
        f"- Peak GPU: {peak_gpu_mb:.0f} MB\n\n"
        f"## Checkpoint\n\n"
        f"- Path: `{checkpoint_info.get('path')}`\n"
        f"- Best train WER (during training): {history_summary.get('best_train_wer')}\n"
        f"- Best epoch: {history_summary.get('best_train_epoch')}\n"
        f"- Total epochs trained: {history_summary.get('n_epochs_trained')}\n\n"
        f"## Sample predictions (10 evenly-spaced)\n\n"
    )
    for sp in sample_preds:
        summary += (
            f"- `[{sp['idx']}]`\n"
            f"  - PRED: `{sp['pred'][:140]}`\n"
            f"  - LABEL: `{sp['label'][:140]}`\n"
            f"  - WER: {sp['per_sample_wer']:.3f} | CER: {sp['per_sample_cer']:.3f}\n\n"
        )
    summary += f"\nFull predictions in `predictions.csv`. Full JSON in `test_paper.json`.\n"

    (out_dir / "test_summary.md").write_text(summary, encoding="utf-8")

    return json_path
