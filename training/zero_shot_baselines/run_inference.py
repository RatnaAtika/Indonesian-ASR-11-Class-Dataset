"""Zero-shot baseline runner.

Runs inference-only with frozen pretrained models on test set.
Models supported:
  - openai/whisper-large-v3
  - openai/whisper-medium
  - facebook/mms-1b-all (with target_lang=ind)

Saves predictions, history.json (1 epoch entry per model), report.md.

Usage:
    python3 training/zero_shot_baselines/run_inference.py \\
        --model-id openai/whisper-medium \\
        --run-dir training/zero_shot_baselines/runs/whisper_medium_smoke \\
        --max-samples 50
"""
from __future__ import annotations
import argparse, csv, json, sys, time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import soundfile as sf

TRAINING_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(TRAINING_ROOT))

from common.utils import compute_wer_cer, EpochTimer, GPUMonitor


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model-id", required=True)
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--data-root", type=Path,
                   default=TRAINING_ROOT.parent / "Processed_Balanced19_v7_natural_synth" / "Dataset_Balanced19")
    p.add_argument("--data-final", type=Path, default=TRAINING_ROOT / "data_final")
    p.add_argument("--split", default="test", choices=["test", "dev"])
    p.add_argument("--max-samples", type=int, default=0)
    p.add_argument("--target-lang", default=None)
    p.add_argument("--language", default="indonesian")
    return p.parse_args()


def load_split(tsv_path, dataset_root, max_samples=0):
    rows = []
    with open(tsv_path, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            ap = Path(dataset_root) / r["audio_path"]
            if not ap.exists():
                continue
            rows.append({"audio_path": str(ap), "transcript": r["transcript"].strip()})
            if max_samples > 0 and len(rows) >= max_samples:
                break
    return rows


def load_audio(path):
    a, sr = sf.read(path, dtype="float32")
    if a.ndim > 1:
        a = a.mean(axis=1).astype(np.float32)
    return a


def main():
    args = parse_args()
    args.run_dir.mkdir(parents=True, exist_ok=True)
    (args.run_dir / "config.json").write_text(json.dumps(vars(args), indent=2, default=str), encoding="utf-8")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    is_whisper = "whisper" in args.model_id.lower()
    is_mms = "mms" in args.model_id.lower()
    
    print(f"[zero-shot] model: {args.model_id}, device: {device}")
    print(f"[zero-shot] split: {args.split}")
    
    rows = load_split(args.data_final / f"{args.split}.tsv", args.data_root, args.max_samples)
    print(f"[zero-shot] samples: {len(rows)}")
    
    gpu_mon = GPUMonitor()
    
    if is_whisper:
        from transformers import WhisperForConditionalGeneration, WhisperProcessor
        processor = WhisperProcessor.from_pretrained(args.model_id)
        model = WhisperForConditionalGeneration.from_pretrained(args.model_id, torch_dtype=torch.float16 if device == "cuda" else torch.float32).to(device)
        model.eval()
        gen_kwargs = {"language": args.language, "task": "transcribe", "max_new_tokens": 200}
    elif is_mms:
        from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
        processor = Wav2Vec2Processor.from_pretrained(args.model_id, target_lang=args.target_lang or "ind")
        model = Wav2Vec2ForCTC.from_pretrained(args.model_id, target_lang=args.target_lang or "ind",
                                                ignore_mismatched_sizes=True).to(device)
        model.eval()
        gen_kwargs = {}
    else:
        raise ValueError(f"Unknown model family: {args.model_id}")
    
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[zero-shot] params: {n_params:,}")
    
    preds_dir = args.run_dir / "predictions"
    preds_dir.mkdir(exist_ok=True)
    pred_csv = preds_dir / f"predictions_{args.split}.csv"
    
    all_preds, all_labels = [], []
    start = time.perf_counter()
    
    with pred_csv.open("w", encoding="utf-8", newline="") as fout:
        writer = csv.writer(fout)
        writer.writerow(["idx", "audio_path", "label", "prediction"])
        
        with torch.no_grad():
            for i, r in enumerate(rows):
                audio = load_audio(r["audio_path"])
                if is_whisper:
                    feat = processor.feature_extractor(audio, sampling_rate=16000, return_tensors="pt").input_features.to(device, dtype=model.dtype)
                    ids = model.generate(feat, **gen_kwargs)
                    pred = processor.tokenizer.decode(ids[0], skip_special_tokens=True).strip()
                else:  # mms
                    inputs = processor(audio, sampling_rate=16000, return_tensors="pt").input_values.to(device)
                    logits = model(inputs).logits
                    pred_ids = logits.argmax(dim=-1)
                    pred = processor.batch_decode(pred_ids)[0].strip()
                all_preds.append(pred)
                all_labels.append(r["transcript"])
                writer.writerow([i, r["audio_path"], r["transcript"], pred])
                if (i + 1) % 10 == 0:
                    print(f"  [{i+1}/{len(rows)}] PRED: {pred[:60]}", flush=True)
    
    elapsed = time.perf_counter() - start
    gpu_mb = gpu_mon.peak_mb()
    
    metrics = compute_wer_cer(all_preds, all_labels)
    
    # Save 1-epoch history (so plots utility works)
    from common.utils import HistorySaver
    hs = HistorySaver(args.run_dir)
    sample_preds = list(zip(all_preds[:5], all_labels[:5]))
    hs.append_epoch(1, {
        "train_loss": None, "val_loss": None,
        "wer": metrics["wer"], "cer": metrics["cer"],
        "mer": metrics["mer"], "wil": metrics["wil"],
        "time_sec": round(elapsed, 2),
        "time_str": EpochTimer.format_seconds(elapsed),
        "total_elapsed_sec": round(elapsed, 2),
        "total_elapsed_str": EpochTimer.format_seconds(elapsed),
        "gpu_mb": round(gpu_mb, 1),
        "lr": 0.0,
        "throughput_samples_per_sec": round(len(rows) / max(elapsed, 1), 2),
    }, sample_preds)
    
    # Print summary
    summary = f"""
============================================================
Zero-shot {args.model_id} on {args.split}
Samples: {len(rows)}
WER: {metrics['wer']:.4f}  CER: {metrics['cer']:.4f}
MER: {metrics['mer']:.4f}  WIL: {metrics['wil']:.4f}
Time: {EpochTimer.format_seconds(elapsed)}
GPU: {gpu_mb:.0f} MB
Throughput: {len(rows)/max(elapsed,1):.2f} samples/sec
============================================================"""
    print(summary, flush=True)
    
    log_lines = [summary]
    log_lines.append("\n=== Sample predictions ===")
    for p, l in sample_preds:
        log_lines.append(f"PRED:  {p[:90]}")
        log_lines.append(f"LABEL: {l[:90]}\n")
    (args.run_dir / "log.txt").write_text("\n".join(log_lines), encoding="utf-8")
    
    report = f"""# Zero-shot Baseline Report — {args.model_id}

**Run dir**: {args.run_dir}
**Generated**: {datetime.now().isoformat()}
**Split**: {args.split}
**Samples**: {len(rows)}

## Model
- ID: {args.model_id}
- Total params: {n_params:,}
- Mode: zero-shot inference (no fine-tuning)
- Language: {args.language}

## Results
- WER: {metrics['wer']:.4f}
- CER: {metrics['cer']:.4f}
- MER: {metrics['mer']:.4f}
- WIL: {metrics['wil']:.4f}

## Performance
- Total time: {EpochTimer.format_seconds(elapsed)}
- Throughput: {len(rows)/max(elapsed,1):.2f} samples/sec
- Peak GPU: {gpu_mb:.0f} MB

## Artifacts
- Predictions CSV: `{pred_csv}`
- History JSON: `{args.run_dir / 'history.json'}`
- Log: `{args.run_dir / 'log.txt'}`
"""
    (args.run_dir / "report.md").write_text(report, encoding="utf-8")
    print(f"[zero-shot] report saved: {args.run_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
