"""Common utilities for all 7 training scripts.

Shared modules:
  - DatasetLoader      : load TSV → HF Dataset with audio
  - MetricsComputer    : WER, CER, MER, WIL via jiwer
  - HistorySaver       : per-epoch history → history.json
  - PlotGenerator      : regenerable plots from history.json
  - LoggingCallback    : HF Trainer callback for per-epoch logging
  - GPU monitor        : peak VRAM tracking

Usage:
    from training.common.utils import (
        load_split, compute_metrics, save_history, regenerate_plots,
        EpochLoggerCallback, GPUMonitor
    )
"""
from __future__ import annotations
import csv, json, os, time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import jiwer
import soundfile as sf
from datasets import Dataset
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt


# ============================================================
# 1. DATASET LOADER (manual audio loading, NO torchcodec)
# ============================================================

def load_split(tsv_path: Path, dataset_root: Path, max_samples: int = 0,
               cache_audio: bool = False) -> Dataset:
    """Load split TSV → HF Dataset with audio loaded via soundfile (no torchcodec).

    Returns Dataset with 'audio_path' (str) and metadata; audio loaded lazily.
    Caller should map() this with their own audio loader.
    """
    rows = []
    with tsv_path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            audio_path = dataset_root / r["audio_path"]
            if not audio_path.exists():
                continue
            rows.append({
                "audio_path": str(audio_path),
                "transcript": r["transcript"],
                "speaker_id": r["speaker_id"],
                "category": r["category"],
                "is_synthetic": r["is_synthetic"],
                "duration_sec": float(r["duration_sec"]),
            })
            if max_samples > 0 and len(rows) >= max_samples:
                break
    return Dataset.from_list(rows)


def load_audio_array(path: str) -> np.ndarray:
    """Read WAV via soundfile, return float32 numpy array (16 kHz mono)."""
    audio, sr = sf.read(path, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1).astype(np.float32)
    if sr != 16000:
        # We control the dataset = always 16 kHz, but safety check
        raise RuntimeError(f"unexpected sr {sr} for {path}; expected 16000")
    return audio


# ============================================================
# 2. METRICS
# ============================================================

def compute_wer_cer(preds: List[str], refs: List[str]) -> Dict[str, float]:
    """Compute WER, CER, MER, WIL via jiwer."""
    # Filter empty refs (would crash jiwer)
    pairs = [(p, r) for p, r in zip(preds, refs) if r.strip()]
    if not pairs:
        return {"wer": 0.0, "cer": 0.0, "mer": 0.0, "wil": 0.0}
    preds_clean, refs_clean = zip(*pairs)
    return {
        "wer": jiwer.wer(list(refs_clean), list(preds_clean)),
        "cer": jiwer.cer(list(refs_clean), list(preds_clean)),
        "mer": jiwer.mer(list(refs_clean), list(preds_clean)),
        "wil": jiwer.wil(list(refs_clean), list(preds_clean)),
    }


def bootstrap_wer_ci(preds: List[str], refs: List[str], n_bootstrap: int = 1000,
                     ci: float = 0.95, seed: int = 42) -> Dict[str, float]:
    """Bootstrap CI for WER."""
    rng = np.random.default_rng(seed)
    n = len(preds)
    if n < 2:
        return {"wer_mean": 0.0, "wer_lower": 0.0, "wer_upper": 0.0}
    wers = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        try:
            wer = jiwer.wer([refs[i] for i in idx], [preds[i] for i in idx])
            wers.append(wer)
        except Exception:
            pass
    if not wers:
        return {"wer_mean": 0.0, "wer_lower": 0.0, "wer_upper": 0.0}
    alpha = (1 - ci) / 2
    return {
        "wer_mean": float(np.mean(wers)),
        "wer_lower": float(np.percentile(wers, alpha * 100)),
        "wer_upper": float(np.percentile(wers, (1 - alpha) * 100)),
    }


# ============================================================
# 3. HISTORY MANAGER
# ============================================================

class HistorySaver:
    """Save per-epoch metrics to history.json. Format compatible dengan plot regen."""

    def __init__(self, run_dir: Path):
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.run_dir / "history.json"
        self.predictions_dir = self.run_dir / "predictions"
        self.predictions_dir.mkdir(exist_ok=True)
        self.history: List[Dict] = []
        if self.history_path.exists():
            try:
                self.history = json.loads(self.history_path.read_text(encoding="utf-8"))
            except Exception:
                self.history = []

    def append_epoch(self, epoch: int, metrics: Dict, predictions_sample: Optional[List[Tuple[str, str]]] = None):
        """Add one epoch entry. metrics keys: train_loss, val_loss, train_acc, val_acc, wer, cer, time_sec, gpu_mb, lr."""
        entry = {
            "epoch": epoch,
            "timestamp": datetime.now().isoformat(),
            **metrics,
        }
        self.history.append(entry)
        self.history_path.write_text(
            json.dumps(self.history, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        if predictions_sample is not None:
            sample_path = self.predictions_dir / f"epoch_{epoch:03d}.json"
            sample_path.write_text(
                json.dumps(
                    [{"pred": p, "label": l} for p, l in predictions_sample],
                    indent=2, ensure_ascii=False
                ),
                encoding="utf-8"
            )

    def get_best(self, metric: str = "wer", lower_better: bool = True) -> Optional[Dict]:
        if not self.history:
            return None
        valid = [h for h in self.history if metric in h]
        if not valid:
            return None
        return min(valid, key=lambda h: h[metric]) if lower_better else max(valid, key=lambda h: h[metric])


# ============================================================
# 4. PLOT GENERATOR (regenerable!)
# ============================================================

def regenerate_plots(history_path: Path, plots_dir: Optional[Path] = None,
                      title_suffix: str = "", style: Dict = None) -> Dict[str, Path]:
    """Regenerate all standard plots from history.json. Run anytime to update plots."""
    history_path = Path(history_path)
    if plots_dir is None:
        plots_dir = history_path.parent / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    history = json.loads(history_path.read_text(encoding="utf-8"))
    if not history:
        return {}

    epochs = [h["epoch"] for h in history]
    style = style or {}
    fontsize = style.get("fontsize", 11)
    figsize = style.get("figsize", (8, 5))
    dpi = style.get("dpi", 150)

    paths = {}

    # 1. Loss plot
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    if any("train_loss" in h for h in history):
        ax.plot(epochs, [h.get("train_loss", np.nan) for h in history], "o-", label="Train Loss")
    if any("val_loss" in h for h in history):
        ax.plot(epochs, [h.get("val_loss", np.nan) for h in history], "s-", label="Val Loss")
    ax.set_xlabel("Epoch", fontsize=fontsize)
    ax.set_ylabel("Loss", fontsize=fontsize)
    ax.set_title(f"Training Loss{title_suffix}", fontsize=fontsize + 1)
    ax.legend(fontsize=fontsize - 1)
    ax.grid(alpha=0.3)
    p = plots_dir / "loss.png"
    fig.tight_layout(); fig.savefig(p); plt.close(fig)
    paths["loss"] = p

    # 2. Accuracy plot (if available)
    if any("train_acc" in h or "val_acc" in h for h in history):
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        if any("train_acc" in h for h in history):
            ax.plot(epochs, [h.get("train_acc", np.nan) for h in history], "o-", label="Train Acc")
        if any("val_acc" in h for h in history):
            ax.plot(epochs, [h.get("val_acc", np.nan) for h in history], "s-", label="Val Acc")
        ax.set_xlabel("Epoch", fontsize=fontsize)
        ax.set_ylabel("Accuracy", fontsize=fontsize)
        ax.set_title(f"Training Accuracy{title_suffix}", fontsize=fontsize + 1)
        ax.legend(fontsize=fontsize - 1)
        ax.grid(alpha=0.3)
        p = plots_dir / "accuracy.png"
        fig.tight_layout(); fig.savefig(p); plt.close(fig)
        paths["accuracy"] = p

    # 3. WER + CER plot
    if any("wer" in h or "cer" in h for h in history):
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        if any("wer" in h for h in history):
            ax.plot(epochs, [h.get("wer", np.nan) for h in history], "o-", label="WER")
        if any("cer" in h for h in history):
            ax.plot(epochs, [h.get("cer", np.nan) for h in history], "s-", label="CER")
        ax.set_xlabel("Epoch", fontsize=fontsize)
        ax.set_ylabel("Error Rate", fontsize=fontsize)
        ax.set_title(f"Validation WER / CER{title_suffix}", fontsize=fontsize + 1)
        ax.legend(fontsize=fontsize - 1)
        ax.grid(alpha=0.3)
        p = plots_dir / "wer_cer.png"
        fig.tight_layout(); fig.savefig(p); plt.close(fig)
        paths["wer_cer"] = p

    # 4. Learning rate plot
    if any("lr" in h for h in history):
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        ax.plot(epochs, [h.get("lr", np.nan) for h in history], "o-", color="purple")
        ax.set_xlabel("Epoch", fontsize=fontsize)
        ax.set_ylabel("Learning Rate", fontsize=fontsize)
        ax.set_yscale("log")
        ax.set_title(f"Learning Rate Schedule{title_suffix}", fontsize=fontsize + 1)
        ax.grid(alpha=0.3, which="both")
        p = plots_dir / "lr.png"
        fig.tight_layout(); fig.savefig(p); plt.close(fig)
        paths["lr"] = p

    # 5. GPU memory
    if any("gpu_mb" in h for h in history):
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        ax.plot(epochs, [h.get("gpu_mb", np.nan) for h in history], "o-", color="green")
        ax.set_xlabel("Epoch", fontsize=fontsize)
        ax.set_ylabel("GPU Memory (MB)", fontsize=fontsize)
        ax.set_title(f"Peak GPU Memory per Epoch{title_suffix}", fontsize=fontsize + 1)
        ax.grid(alpha=0.3)
        p = plots_dir / "gpu_mb.png"
        fig.tight_layout(); fig.savefig(p); plt.close(fig)
        paths["gpu_mb"] = p

    return paths


# ============================================================
# 5. GPU MONITOR
# ============================================================

class GPUMonitor:
    """Track peak VRAM during training. Reset between epochs."""

    def __init__(self):
        self.device_idx = 0
        self.has_cuda = torch.cuda.is_available()

    def reset_peak(self):
        if self.has_cuda:
            torch.cuda.reset_peak_memory_stats(self.device_idx)

    def peak_mb(self) -> float:
        if not self.has_cuda:
            return 0.0
        return torch.cuda.max_memory_allocated(self.device_idx) / 1024 / 1024


# ============================================================
# 6. EPOCH TIMER
# ============================================================

class EpochTimer:
    def __init__(self):
        self.epoch_start = None
        self.run_start = time.perf_counter()

    def start_epoch(self):
        self.epoch_start = time.perf_counter()

    def end_epoch(self) -> float:
        if self.epoch_start is None:
            return 0.0
        elapsed = time.perf_counter() - self.epoch_start
        self.epoch_start = None
        return elapsed

    def total_elapsed(self) -> float:
        return time.perf_counter() - self.run_start

    @staticmethod
    def format_seconds(s: float) -> str:
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sec = int(s % 60)
        return f"{h:02d}:{m:02d}:{sec:02d}"


# ============================================================
# Shared rich-format epoch log
# ============================================================
def format_epoch_log(epoch: int, total_epochs: int, entry: Dict,
                     sample_preds: Optional[List] = None,
                     extra_lines: Optional[List[str]] = None) -> str:
    """Produce per-epoch log block matching the user's reference (Bi-LSTM/T-RCNN style).

    Format:
        [HH:MM:SS] Epoch N/Total | Current LR: 0.xxxxxx
        Current Learning Rate: 0.xxxxxxxxxx
        Train Loss: x.xxxxxx
        Validation Loss: x.xxxxxx
        Train Accuracy: 0.xxxxxx
        Validation Accuracy: 0.xxxxxx
        WER: 0.xxxxxx
        CER: 0.xxxxxx
        (extra_lines, e.g. "[Train] avg_rpn=...")
        Durasi epoch: 00:MM:SS
        Total elapsed time: HH:MM:SS
        GPU memory usage: XXX MB
        Throughput: XXX.XX samples/sec
        === Contoh prediksi vs label (val) ===
        PRED: ...
        LABEL: ...
        ...
        Epoch N: Train Loss=X | Val Loss=Y | Train Acc=Z | Val Acc=W | WER=A | CER=B | Time=00:MM:SS | GPU=XMb
    """
    from datetime import datetime as _dt

    def _f(v, p=4, default="n/a"):
        if v is None: return default
        try: return f"{float(v):.{p}f}"
        except Exception: return default

    def _f_int(v, default="n/a"):
        if v is None: return default
        try: return f"{float(v):.0f}"
        except Exception: return default

    tl = entry.get("train_loss")
    vl = entry.get("val_loss")
    ta = entry.get("train_acc")
    va = entry.get("val_acc")
    wer = entry.get("wer")
    cer = entry.get("cer")
    lr  = entry.get("lr")
    gpu = entry.get("gpu_mb")
    tput = entry.get("throughput_samples_per_sec")
    time_str = entry.get("time_str", "00:00:00")
    total_elapsed_str = entry.get("total_elapsed_str", "00:00:00")

    lines = []
    lines.append("=" * 60)
    lines.append(f"[{_dt.now().strftime('%H:%M:%S')}] Epoch {epoch}/{total_epochs} "
                 f"| Current LR: {_f(lr, 6)}")
    lines.append(f"Current Learning Rate: {_f(lr, 10)}")
    lines.append(f"Train Loss: {_f(tl, 6)}")
    lines.append(f"Validation Loss: {_f(vl, 6)}")
    lines.append(f"Train Accuracy: {_f(ta, 6)}")
    lines.append(f"Validation Accuracy: {_f(va, 6)}")
    lines.append(f"WER: {_f(wer, 6)}")
    lines.append(f"CER: {_f(cer, 6)}")
    if extra_lines:
        for el in extra_lines:
            lines.append(el)
    lines.append(f"Durasi epoch: {time_str}")
    lines.append(f"Total elapsed time: {total_elapsed_str}")
    lines.append(f"GPU memory usage: {_f_int(gpu)} MB")
    lines.append(f"Throughput: {_f(tput, 2)} samples/sec")
    lines.append("=== Contoh prediksi vs label (val) ===")
    if sample_preds:
        for pred, label in sample_preds[:5]:
            lines.append(f"PRED: {str(pred)[:120]}")
            lines.append(f"LABEL: {str(label)[:120]}")
            lines.append("")
    else:
        lines.append("(no sample predictions captured this epoch)")

    # One-line summary (parser-friendly)
    summary = (
        f"Epoch {epoch}: "
        f"Train Loss={_f(tl)} | Val Loss={_f(vl)} | "
        f"Train Acc={_f(ta)} | Val Acc={_f(va)} | "
        f"WER={_f(wer)} | CER={_f(cer)} | "
        f"Time={time_str} | GPU={_f_int(gpu)}MB"
    )
    lines.append(summary)
    lines.append("")
    return "\n".join(lines)


def token_accuracy_from_logits(logits: "torch.Tensor", labels: "torch.Tensor",
                                ignore_index: int = -100) -> float:
    """Per-token classification accuracy on padded label sequences.

    logits: (B, T, V) or (T, B, V) — auto-detect via labels shape
    labels: (B, T) or (T, B) — int64 with ignore_index for pad
    Returns scalar in [0,1].
    """
    import torch as _t
    if logits.dim() != 3 or labels.dim() != 2:
        return 0.0
    # Align shape: assume (B, T) for labels, (B, T, V) for logits
    if logits.shape[0] == labels.shape[1] and logits.shape[1] == labels.shape[0]:
        # (T, B, V) -> (B, T, V)
        logits = logits.transpose(0, 1)
    pred = logits.argmax(dim=-1)
    mask = labels != ignore_index
    if mask.sum().item() == 0:
        return 0.0
    correct = ((pred == labels) & mask).sum().item()
    total = mask.sum().item()
    return correct / max(total, 1)


def unique_run_dir(base: Path, sentinel_files: tuple = (
    # Standard artifacts dari trainers our-own (whisper, wav2vec2, from_scratch, pkl_*)
    "history.json", "meta.json", "config.json", "log.txt",
    # Root-script artifacts (m11/m12 wrappers ke train_model_vanilla.py / train_model_vit.py)
    "transformer_asr_last.pth", "cer.png", "cer_vit.png",
    "char_accuracy.png", "char_accuracy_vit.png",
    "training_val_loss.png", "training_val_loss_vit.png",
    "training_val_accuracy.png", "training_val_accuracy_vit.png",
    "model_summary.png", "model_summary_vit.png",
    "model_summary.pdf", "model_summary_vit.pdf",
)) -> Path:
    """Auto-pick a non-colliding run directory.

    Behavior:
      - If `base` does not exist OR contains no sentinel file, return `base` as-is.
      - Otherwise, append `_HHMMSS` to avoid overwriting a prior run.
      - If that also collides (sub-second re-run), append numeric counter.

    Protects history.json, log.txt, predictions, plots, checkpoints from
    accidental overwrite.
    """
    import datetime as _dt
    base = Path(base)
    if not base.exists():
        return base
    has_real_run = any((base / s).exists() for s in sentinel_files)
    if not has_real_run:
        return base
    stamp = _dt.datetime.now().strftime("%H%M%S")
    candidate = base.parent / f"{base.name}_{stamp}"
    n = 2
    while candidate.exists() and any((candidate / s).exists() for s in sentinel_files):
        candidate = base.parent / f"{base.name}_{stamp}_{n}"
        n += 1
        if n > 100:
            raise RuntimeError(f"Cannot find unique run dir after 100 attempts: {base}")
    return candidate


def cer_to_token_acc_proxy(cer: Optional[float]) -> Optional[float]:
    """For CTC trainers where teacher-forcing accuracy is not naturally available,
    use 1 - CER as a proxy 'character-level accuracy' to keep log format consistent.
    Returns None if cer is None."""
    if cer is None:
        return None
    return max(0.0, min(1.0, 1.0 - float(cer)))


class BestCheckpointTracker:
    """Track + save best model. Frozen historical bests + always-current pointer.

    File naming convention dalam <run_dir>/checkpoints/:
      - `epoch_NNN.pt` — per-epoch checkpoint (sudah disimpan trainer secara default)
      - `best_<metric><value>_e<N>.pt` — frozen historical best (kept forever,
         tidak dioverwrite sehingga user bisa compare multiple bests dari
         berbagai run / tuning iteration)
      - `best.pt` — always points to the LATEST best in this run (rewrite each
         time a new best is found)

    Metric assumed lower-is-better (WER, CER) by default.
    """

    def __init__(self, run_dir: Path, metric_name: str = "wer",
                 lower_is_better: bool = True):
        self.run_dir = Path(run_dir)
        self.ckpt_dir = self.run_dir / "checkpoints"
        self.ckpt_dir.mkdir(parents=True, exist_ok=True)
        self.metric_name = metric_name
        self.lower_is_better = lower_is_better
        self.best_value = float("inf") if lower_is_better else float("-inf")
        self.best_epoch = -1
        self.best_path = None

    def is_better(self, value: float) -> bool:
        if value is None:
            return False
        return value < self.best_value if self.lower_is_better else value > self.best_value

    def maybe_save(self, value: float, epoch: int,
                   model_state, extra_state: Optional[Dict] = None) -> Optional[Path]:
        """Save best checkpoint if `value` improves over previous best.

        Returns Path to saved frozen checkpoint, or None if no improvement.
        """
        import torch as _t

        if not self.is_better(value):
            return None

        prev_best = self.best_value
        self.best_value = value
        self.best_epoch = epoch

        # Frozen historical best (never overwritten)
        v_str = f"{value:.4f}".replace(".", "p")  # 0.2362 → 0p2362
        frozen_name = f"best_{self.metric_name}{v_str}_e{epoch:03d}.pt"
        frozen_path = self.ckpt_dir / frozen_name

        # Always-current pointer
        current_path = self.ckpt_dir / "best.pt"

        ckpt_data = {
            "epoch": epoch,
            "model_state": model_state,
            f"best_{self.metric_name}": value,
            "prev_best": prev_best if prev_best != float("inf") and prev_best != float("-inf") else None,
            **(extra_state or {}),
        }

        # Save frozen checkpoint
        _t.save(ckpt_data, frozen_path)
        # Update best.pt pointer (copy, not symlink — portable across filesystems)
        _t.save(ckpt_data, current_path)

        self.best_path = frozen_path
        return frozen_path

    def summary(self) -> Dict:
        return {
            "metric_name": self.metric_name,
            "best_value": self.best_value if self.best_value not in (float("inf"), float("-inf")) else None,
            "best_epoch": self.best_epoch if self.best_epoch >= 0 else None,
            "best_path": str(self.best_path) if self.best_path else None,
        }


def save_run_meta(run_dir: Path, model_id: str, family: str, era: str,
                  config: Dict, dataset_info: Optional[Dict] = None,
                  notes: str = "") -> Path:
    """Save meta.json with all reproducibility context for future replotting.

    Captures:
      - model identity (id, family, era)
      - full training config snapshot
      - dataset version + splits used
      - environment (Python, key library versions, GPU info)
      - timestamp
      - replay instructions (how to re-plot from history.json)
    """
    import sys, platform, datetime

    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    env = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "timestamp": datetime.datetime.now().isoformat(),
    }
    # Capture key library versions if available
    for lib in ["torch", "transformers", "librosa", "soundfile",
                "sentencepiece", "hmmlearn", "jiwer", "numpy", "scipy",
                "pandas", "matplotlib", "seaborn"]:
        try:
            mod = __import__(lib)
            env[f"{lib}_version"] = getattr(mod, "__version__", "unknown")
        except ImportError:
            pass
    # GPU info if torch is available
    try:
        import torch as _t
        if _t.cuda.is_available():
            env["cuda_device"] = _t.cuda.get_device_name(0)
            env["cuda_version"] = getattr(_t.version, "cuda", "unknown")
            env["cudnn_version"] = _t.backends.cudnn.version() if _t.backends.cudnn.is_available() else None
        else:
            env["cuda_device"] = "cpu-only"
    except Exception:
        pass

    meta = {
        "model_id": model_id,
        "family": family,
        "era": era,
        "notes": notes,
        "config": {k: str(v) if isinstance(v, Path) else v for k, v in config.items()},
        "dataset_info": dataset_info or {},
        "environment": env,
        "replay": {
            "history_path": str(run_dir / "history.json"),
            "log_path": str(run_dir / "log.txt"),
            "predictions_dir": str(run_dir / "predictions"),
            "replot_command": (
                f"python3 -m common.journal_plotting --run-dir '{run_dir}' "
                f"--style ieee --formats png pdf"
            ),
            "available_styles": ["ieee", "acm", "springer", "elsevier", "thesis", "plain"],
            "available_formats": ["png", "pdf", "svg", "eps"],
        },
    }

    out = run_dir / "meta.json"
    out.write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")
    return out


def save_model_summary(run_dir: Path, model, arch: str, n_params: int,
                       n_trainable: Optional[int] = None, extra: Optional[Dict] = None,
                       input_data=None, input_size=None) -> Optional[Path]:
    """Render model_summary.png + model_summary.pdf via torchinfo (same format as
    m11/m12 root scripts): a Layer/Input/Output/Param# table drawn to a figure.

    Written at training start so a summary exists even if the run is interrupted.
    Falls back to a plain-text figure if torchinfo/forward fails.
    """
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if n_trainable is None:
        try:
            n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        except Exception:
            n_trainable = n_params
    header = [f"Model: {arch}",
             f"Total params: {n_params:,}   Trainable: {n_trainable:,}"]
    for k, v in (extra or {}).items():
        header.append(f"{k}: {v}")
    body = ""
    try:
        from torchinfo import summary
        kw = {"depth": 3, "col_names": ["input_size", "output_size", "num_params"],
              "verbose": 0}
        if input_data is not None:
            s = summary(model, input_data=input_data, **kw)
        elif input_size is not None:
            s = summary(model, input_size=input_size, **kw)
        else:
            s = summary(model, verbose=0)
        body = str(s)
    except Exception as e:
        body = f"[torchinfo unavailable/failed: {e}]\n\n{model}"
    text = "\n".join(header) + "\n\n" + body
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(12, max(8, text.count(chr(10)) * 0.16)))
        ax.axis("off")
        ax.text(0, 1, text, fontsize=8, family="monospace", verticalalignment="top")
        png = run_dir / "model_summary.png"
        plt.savefig(png, bbox_inches="tight", dpi=150)
        plt.savefig(run_dir / "model_summary.pdf", bbox_inches="tight")
        plt.close(fig)
        return png
    except Exception:
        (run_dir / "model_summary.txt").write_text(text, encoding="utf-8")
        return run_dir / "model_summary.txt"


# ============================================================
# 7. LOGGING CALLBACK FOR HF TRAINER
# ============================================================

try:
    from transformers import TrainerCallback

    class EpochLoggerCallback(TrainerCallback):
        """Logs per-epoch metrics in the format requested by user."""

        def __init__(self, history_saver: HistorySaver, gpu_monitor: GPUMonitor,
                     timer: EpochTimer, log_file: Path,
                     compute_predictions_sample=None):
            self.history_saver = history_saver
            self.gpu_monitor = gpu_monitor
            self.timer = timer
            self.log_file = Path(log_file)
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            self.compute_predictions_sample = compute_predictions_sample

        def on_epoch_begin(self, args, state, control, **kwargs):
            self.timer.start_epoch()
            self.gpu_monitor.reset_peak()

        def on_evaluate(self, args, state, control, metrics=None, **kwargs):
            metrics = metrics or {}
            epoch = int(state.epoch) if state.epoch else 0
            elapsed = self.timer.end_epoch()
            gpu_mb = self.gpu_monitor.peak_mb()
            total_elapsed = self.timer.total_elapsed()

            entry = {
                "train_loss": float(state.log_history[-2]["loss"]) if len(state.log_history) >= 2 and "loss" in state.log_history[-2] else None,
                "val_loss": float(metrics.get("eval_loss", 0)),
                "wer": float(metrics.get("eval_wer", 0)) if "eval_wer" in metrics else None,
                "cer": float(metrics.get("eval_cer", 0)) if "eval_cer" in metrics else None,
                "time_sec": round(elapsed, 2),
                "time_str": EpochTimer.format_seconds(elapsed),
                "total_elapsed_sec": round(total_elapsed, 2),
                "total_elapsed_str": EpochTimer.format_seconds(total_elapsed),
                "gpu_mb": round(gpu_mb, 1),
                "lr": state.log_history[-1].get("learning_rate", 0) if state.log_history else 0,
            }

            sample = None
            if self.compute_predictions_sample is not None:
                try:
                    sample = self.compute_predictions_sample()
                except Exception as e:
                    print(f"[callback] sample prediction error: {e}")

            self.history_saver.append_epoch(epoch, entry, sample)

            # Use the shared rich-format epoch log
            log_line = format_epoch_log(epoch, self.total_epochs, entry, sample)
            print(log_line)
            with self.log_file.open("a", encoding="utf-8") as f:
                f.write(log_line)

            # Regenerate plots after each epoch
            try:
                regenerate_plots(self.history_saver.history_path)
            except Exception as e:
                print(f"[callback] plot regen error: {e}")

except ImportError:
    EpochLoggerCallback = None
