"""Whisper-medium FT test entry point — m02b paper model #9.

Loads HF Trainer-saved checkpoint dari run_dir, jalan generate() pada test
set v7, save JSON test_paper.json.

Usage:
    python3 training/m02b_whisper_medium_ft/test.py
    python3 training/m02b_whisper_medium_ft/test.py \\
      --run-dir training/m02b_whisper_medium_ft/runs/run_paper_20260601
"""
import sys, argparse, csv, time, logging
from pathlib import Path

import numpy as np
import torch
import soundfile as sf

HERE = Path(__file__).parent
TRAINING = HERE.parent
sys.path.insert(0, str(TRAINING))

from common.test_helper import (
    compute_test_metrics, per_sample_wer, per_sample_cer,
    find_best_checkpoint, write_test_results,
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--run-dir", type=Path, default=None)
    p.add_argument("--data-root", type=Path,
                   default=TRAINING.parent / "Processed_Balanced19_v7_natural_synth" / "Dataset_Balanced19")
    p.add_argument("--data-final", type=Path, default=TRAINING / "data_final")
    p.add_argument("--language", default="indonesian")
    p.add_argument("--task", default="transcribe")
    p.add_argument("--max-test-samples", type=int, default=0)
    p.add_argument("--max-new-tokens", type=int, default=200)
    p.add_argument("--batch-size", type=int, default=16,
                   help="Batch size for batched Whisper generate() during test. Use 16-32 on A100, lower if OOM.")
    p.add_argument("--checkpoint", type=Path, default=None,
                   help="HF checkpoint dir (overrides auto-detect)")
    p.add_argument("--model-id-fallback", default="openai/whisper-medium",
                   help="Fallback model id if checkpoint dir invalid")
    return p.parse_args()


def auto_pick_run(slot_runs: Path) -> Path:
    cands = sorted([d for d in slot_runs.glob("run_paper_*") if d.is_dir()],
                   key=lambda d: d.stat().st_mtime, reverse=True)
    if not cands:
        cands = sorted([d for d in slot_runs.glob("run_full_*") if d.is_dir()],
                       key=lambda d: d.stat().st_mtime, reverse=True)
    return cands[0] if cands else None


def load_split_rows(tsv_path: Path, audio_root: Path, max_n: int = 0):
    rows = []
    with tsv_path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            ap = audio_root / r["audio_path"]
            if not ap.exists():
                continue
            rows.append({"audio_path": str(ap), "rel_path": r["audio_path"],
                         "transcript": r["transcript"].strip()})
            if max_n > 0 and len(rows) >= max_n:
                break
    return rows


def main():
    args = parse_args()
    if args.run_dir is None:
        args.run_dir = auto_pick_run(HERE / "runs")
        if args.run_dir is None:
            print(f"[m02b-test] ERROR: no run found in {HERE / 'runs'}")
            return 1
    print(f"[m02b-test] run_dir: {args.run_dir}")
    
    # Find HF Trainer checkpoint dir (best loaded automatically by load_best_model_at_end=True)
    if args.checkpoint:
        ckpt_path = args.checkpoint
    elif (args.run_dir / "best_model").exists():
        ckpt_path = args.run_dir / "best_model"   # dedicated best-model dir (preferred)
    else:
        ckpt_info = find_best_checkpoint(args.run_dir)
        if ckpt_info.get("format") == "hf_dir" and ckpt_info.get("path"):
            ckpt_path = Path(ckpt_info["path"])
        else:
            ckpt_path = args.run_dir / "checkpoints"
    print(f"[m02b-test] checkpoint: {ckpt_path}")
    
    # Load model
    from transformers import WhisperForConditionalGeneration, WhisperProcessor
    logging.getLogger("transformers.generation.utils").setLevel(logging.ERROR)
    
    try:
        processor = WhisperProcessor.from_pretrained(str(ckpt_path))
    except Exception:
        processor = WhisperProcessor.from_pretrained(args.model_id_fallback)
    processor.tokenizer.set_prefix_tokens(language=args.language, task=args.task)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    
    try:
        model = WhisperForConditionalGeneration.from_pretrained(str(ckpt_path), torch_dtype=dtype)
    except Exception as e:
        print(f"[m02b-test] WARN: ckpt load fail ({e}), falling back to base model {args.model_id_fallback}")
        model = WhisperForConditionalGeneration.from_pretrained(args.model_id_fallback, torch_dtype=dtype)
    model = model.to(device).eval()
    model.generation_config.language = args.language
    model.generation_config.task = args.task
    model.generation_config.forced_decoder_ids = None
    
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[m02b-test] params: {n_params:,}")
    
    # Load test set
    test_rows = load_split_rows(args.data_final / "test.tsv", args.data_root,
                                 args.max_test_samples)
    print(f"[m02b-test] test samples: {len(test_rows)}")
    
    preds_list, labels_list = [], []
    predictions = []
    peak_gpu_mb = 0.0
    t0 = time.perf_counter()
    
    print(f"[m02b-test] running batched greedy generate ... batch_size={args.batch_size}")
    with torch.no_grad():
        for start in range(0, len(test_rows), args.batch_size):
            batch_rows = test_rows[start:start + args.batch_size]
            audios = []
            for r in batch_rows:
                audio, sr = sf.read(r["audio_path"], dtype="float32")
                if audio.ndim > 1:
                    audio = audio.mean(axis=1).astype(np.float32)
                audios.append(audio)
            feat = processor.feature_extractor(
                audios, sampling_rate=16000, return_tensors="pt", padding=True
            ).input_features
            feat = feat.to(device, dtype=dtype)
            ids = model.generate(
                feat, language=args.language, task=args.task,
                max_new_tokens=args.max_new_tokens
            )
            batch_preds = processor.tokenizer.batch_decode(ids, skip_special_tokens=True)
            for j, (r, pred) in enumerate(zip(batch_rows, batch_preds)):
                i = start + j
                pred = pred.strip()
                label = r["transcript"]
                preds_list.append(pred); labels_list.append(label)
                predictions.append({
                    "idx": i, "audio": r["rel_path"],
                    "pred": pred, "label": label,
                    "per_sample_wer": per_sample_wer(pred, label),
                    "per_sample_cer": per_sample_cer(pred, label),
                })
            if torch.cuda.is_available():
                peak_gpu_mb = max(peak_gpu_mb,
                                  torch.cuda.max_memory_allocated() / (1024 * 1024))
            done = min(start + len(batch_rows), len(test_rows))
            if done % 256 == 0 or done == len(test_rows):
                rate = done / (time.perf_counter() - t0)
                print(f"  [m02b-test] {done}/{len(test_rows)} rate={rate:.2f} samp/s")
    
    wall_time = time.perf_counter() - t0
    print(f"[m02b-test] inference done in {wall_time:.1f}s ({wall_time/60:.1f} min)")
    
    metrics = compute_test_metrics(preds_list, labels_list)
    print(f"[m02b-test] WER: {metrics['wer']:.4f}, CER: {metrics['cer']:.4f}")
    
    out_dir = args.run_dir / "test_results"
    json_path = write_test_results(
        out_dir=out_dir,
        model_id="m02b-whisper-medium-ft",
        family="Whisper-medium FT (Radford 2022)",
        is_paper_model=True, is_user_novel=False,
        run_dir=args.run_dir,
        checkpoint_info={"path": str(ckpt_path), "filename": ckpt_path.name,
                         "format": "hf_dir", "best_wer": None, "best_epoch": None},
        test_set_info={"split": "test", "n_samples": len(preds_list),
                       "audio_root": str(args.data_root), "feature_format": "raw_audio"},
        metrics=metrics,
        decoding_info={"method": "greedy_ar_batched", "beam_size": 1, "lm": None,
                       "max_decode_len": args.max_new_tokens,
                       "batch_size": args.batch_size},
        wall_time_sec=wall_time,
        n_samples=len(preds_list),
        peak_gpu_mb=peak_gpu_mb,
        predictions=predictions,
    )
    print(f"[m02b-test] \u2713 {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
