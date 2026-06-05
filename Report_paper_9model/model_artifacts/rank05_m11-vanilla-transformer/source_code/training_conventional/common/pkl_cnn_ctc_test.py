"""PKL CNN-CTC test runner — m13 Wav2Letter + m14 Jasper.

Loads `best.pt` dari run_dir, jalan greedy CTC pada test pickle,
save JSON test_paper.json untuk AI-agent.

Usage:
    python3 training_conventional/common/pkl_cnn_ctc_test.py \\
        --arch wav2letter \\
        --run-dir training_conventional/m13_wav2letter_cnn/runs/run_paper_20260601
"""
from __future__ import annotations
import argparse, sys, time, pickle
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
import sentencepiece as spm
from torch.utils.data import DataLoader

THIS = Path(__file__).parent
TC_ROOT = THIS.parent
sys.path.insert(0, str(TC_ROOT))

from common.pkl_cnn_ctc_trainer import (
    Wav2Letter, JasperMini, PklCTCDataset, collate_fn,
    ctc_greedy_decode, ids_to_text,
)
from common.test_helper import (
    compute_test_metrics, per_sample_wer, per_sample_cer,
    find_best_checkpoint, write_test_results,
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--arch", choices=["wav2letter", "jasper"], required=True)
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, default=None)
    p.add_argument("--data-pkl-dir", type=Path,
                   default=TC_ROOT / "data_pkl")
    p.add_argument("--spm-model", type=Path,
                   default=TC_ROOT / "spm" / "spm_v7_char.model")
    p.add_argument("--checkpoint", type=Path, default=None)
    p.add_argument("--max-test-samples", type=int, default=0)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--input-dim", type=int, default=80)
    return p.parse_args()


def main():
    args = parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    args.out_dir = args.out_dir or (args.run_dir / "test_results")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[cnn-ctc-test] arch: {args.arch}, run_dir: {args.run_dir}")

    # Locate best checkpoint
    if args.checkpoint:
        ckpt_info = {"path": str(args.checkpoint), "filename": args.checkpoint.name,
                     "format": "pt", "best_wer": None, "best_epoch": None}
    else:
        ckpt_info = find_best_checkpoint(args.run_dir)
    if not ckpt_info.get("path"):
        print(f"[ERROR] No checkpoint found"); return 1
    print(f"[cnn-ctc-test] checkpoint: {ckpt_info['filename']}")

    # Load checkpoint
    ckpt = torch.load(ckpt_info["path"], map_location="cpu", weights_only=False)
    train_args = ckpt.get("args", {})
    vocab_size = ckpt.get("vocab_size") or 400
    dropout = train_args.get("dropout", 0.1)

    # Load SPM
    sp = spm.SentencePieceProcessor(model_file=str(args.spm_model))
    blank_id = 0

    # Build model + load weights
    if args.arch == "wav2letter":
        model = Wav2Letter(args.input_dim, vocab_size, dropout)
    else:
        model = JasperMini(args.input_dim, vocab_size, dropout)
    model.load_state_dict(ckpt["model_state"])
    model = model.to(device).eval()
    print(f"[cnn-ctc-test] params: {sum(p.numel() for p in model.parameters()):,}")

    # Load test pickle
    print(f"[cnn-ctc-test] loading test pickle ...")
    test_ds = PklCTCDataset(args.data_pkl_dir / "test.pkl", args.max_test_samples, blank_id)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False,
                             collate_fn=collate_fn, num_workers=0)
    print(f"[cnn-ctc-test] test samples: {len(test_ds)}")

    # Inference
    all_preds, all_labels = [], []
    peak_gpu_mb = 0.0
    t0 = time.perf_counter()

    with torch.no_grad():
        for i, batch in enumerate(test_loader):
            feats = batch["features"].to(device)
            feat_lens = batch["feat_lens"].to(device)
            logits, new_lens = model(feats, feat_lens)
            pred_ids = ctc_greedy_decode(logits, blank=blank_id, lengths=new_lens)
            preds = [ids_to_text(p, sp) for p in pred_ids]
            all_preds.extend(preds)
            all_labels.extend(batch["transcripts"])
            if torch.cuda.is_available():
                peak_gpu_mb = max(peak_gpu_mb,
                                  torch.cuda.max_memory_allocated() / (1024 * 1024))
            if (i + 1) % 50 == 0:
                rate = (i + 1) * args.batch_size / (time.perf_counter() - t0)
                print(f"  [test] batch {i+1}/{len(test_loader)} rate={rate:.1f} samp/s")

    wall_time = time.perf_counter() - t0
    print(f"[cnn-ctc-test] inference done in {wall_time:.1f}s")

    metrics = compute_test_metrics(all_preds, all_labels)
    print(f"[cnn-ctc-test] WER: {metrics['wer']:.4f}, CER: {metrics['cer']:.4f}")

    # Build per-sample preds with audio paths
    fnames = test_ds.rows = None  # PklCTCDataset doesn't expose fnames directly
    # Try to read fnames from pickle directly
    try:
        with (args.data_pkl_dir / "test.pkl").open("rb") as f:
            test_data = pickle.load(f)
        fnames = test_data.get("fnames", [])
    except Exception:
        fnames = []

    predictions = []
    for i, (pred, label) in enumerate(zip(all_preds, all_labels)):
        predictions.append({
            "idx": i,
            "audio": fnames[i] if i < len(fnames) else "",
            "pred": pred, "label": label,
            "per_sample_wer": per_sample_wer(pred, label),
            "per_sample_cer": per_sample_cer(pred, label),
        })

    # Slot identification
    arch_to_slot = {
        "wav2letter": ("m13-wav2letter", "Wav2Letter CNN-CTC", True),
        "jasper":     ("m14-jasper-mini", "Jasper-mini CNN-CTC", False),  # not paper-9
    }
    model_id, family, is_paper = arch_to_slot[args.arch]

    json_path = write_test_results(
        out_dir=args.out_dir,
        model_id=model_id, family=family,
        is_paper_model=is_paper, is_user_novel=False,
        run_dir=args.run_dir,
        checkpoint_info=ckpt_info,
        test_set_info={"split": "test", "n_samples": len(all_preds),
                       "audio_root": "data_pkl", "feature_format": "pkl_logmel80"},
        metrics=metrics,
        decoding_info={"method": "greedy_ctc", "beam_size": 1, "lm": None,
                       "max_decode_len": None},
        wall_time_sec=wall_time,
        n_samples=len(all_preds),
        peak_gpu_mb=peak_gpu_mb,
        predictions=predictions,
    )
    print(f"[cnn-ctc-test] \u2713 {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
