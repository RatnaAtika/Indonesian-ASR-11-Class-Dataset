"""From-scratch CTC test runner — m06 Conformer-CTC + m07 Bi-LSTM CTC.

Loads `best.pt` (or specified checkpoint) from a run_dir, runs greedy CTC
decoding on the v7 test split, computes WER/CER/MER/WIL/SER, saves
machine-readable JSON for AI-agent consumption.

Usage:
    # m07 Bi-LSTM
    python3 training/common/from_scratch_test.py \\
        --arch bilstm \\
        --run-dir training/m07_bilstm_ctc/runs/run_paper_20260601 \\
        --out-dir training/m07_bilstm_ctc/runs/run_paper_20260601/test_results

    # m06 Conformer
    python3 training/common/from_scratch_test.py \\
        --arch conformer \\
        --run-dir training/m06_conformer_ctc/runs/run_paper_20260601 \\
        --out-dir training/m06_conformer_ctc/runs/run_paper_20260601/test_results
"""
from __future__ import annotations
import argparse, sys, time, json
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

THIS = Path(__file__).parent
TRAINING_ROOT = THIS.parent
sys.path.insert(0, str(TRAINING_ROOT))

from common.from_scratch_trainer import (
    BiLSTMCTC, ConformerEncoder, CTCDataset, collate_fn,
    ctc_decode, ids_to_text, normalize_text, build_charvocab, load_split_rows,
)
from common.test_helper import (
    compute_test_metrics, per_sample_wer, per_sample_cer,
    find_best_checkpoint, write_test_results,
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--arch", choices=["bilstm", "conformer"], required=True)
    p.add_argument("--run-dir", type=Path, required=True,
                   help="Run dir berisi checkpoints/best.pt + history.json")
    p.add_argument("--out-dir", type=Path, default=None,
                   help="Output dir untuk test_paper.json (default: <run_dir>/test_results)")
    p.add_argument("--data-root", type=Path,
                   default=TRAINING_ROOT.parent / "Processed_Balanced19_v7_natural_synth" / "Dataset_Balanced19")
    p.add_argument("--data-final", type=Path, default=TRAINING_ROOT / "data_final")
    p.add_argument("--checkpoint", type=Path, default=None,
                   help="Override path ke checkpoint (default: auto-detect best.pt)")
    p.add_argument("--max-test-samples", type=int, default=0,
                   help="0 = full test set (recommended for paper)")
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--n-mels", type=int, default=80)
    return p.parse_args()


def main():
    args = parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    args.out_dir = args.out_dir or (args.run_dir / "test_results")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[from-scratch-test] arch: {args.arch}, run_dir: {args.run_dir}")

    # 1. Locate best checkpoint
    if args.checkpoint:
        ckpt_info = {"path": str(args.checkpoint), "filename": args.checkpoint.name,
                     "format": "pt", "best_wer": None, "best_epoch": None}
    else:
        ckpt_info = find_best_checkpoint(args.run_dir)
    if not ckpt_info.get("path"):
        print(f"[ERROR] No checkpoint found in {args.run_dir}/checkpoints/")
        return 1
    print(f"[from-scratch-test] checkpoint: {ckpt_info['filename']}")

    # 2. Load checkpoint + restore vocab
    ckpt = torch.load(ckpt_info["path"], map_location="cpu", weights_only=False)
    vocab = ckpt.get("vocab")
    if vocab is None:
        # Rebuild from training set if not stored
        train_rows = load_split_rows(args.data_final / "train.tsv", args.data_root, 0)
        vocab = build_charvocab(train_rows)
    print(f"[from-scratch-test] vocab size: {len(vocab)}")

    train_args = ckpt.get("args", {})
    hidden = train_args.get("hidden_size", 512)
    n_layers = train_args.get("num_layers", 4)
    dropout = train_args.get("dropout", 0.1)

    # 3. Build model + load weights
    if args.arch == "bilstm":
        model = BiLSTMCTC(args.n_mels, hidden, n_layers, len(vocab), dropout)
    else:
        model = ConformerEncoder(args.n_mels, hidden, n_layers, len(vocab), dropout)
    model.load_state_dict(ckpt["model_state"])
    model = model.to(device).eval()
    print(f"[from-scratch-test] params: {sum(p.numel() for p in model.parameters()):,}")

    # 4. Load test set
    print(f"[from-scratch-test] loading test set ...")
    test_rows = load_split_rows(args.data_final / "test.tsv", args.data_root, args.max_test_samples)
    print(f"[from-scratch-test] test samples: {len(test_rows)}")
    test_ds = CTCDataset(test_rows, vocab, args.n_mels)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False,
                             collate_fn=collate_fn, num_workers=0)

    # 5. Run inference
    all_preds, all_labels, all_audio_paths = [], [], []
    peak_gpu_mb = 0.0
    t0 = time.perf_counter()

    print(f"[from-scratch-test] running inference ...")
    with torch.no_grad():
        for i, batch in enumerate(test_loader):
            feats = batch["features"].to(device)
            feat_lens = batch["feat_lens"].to(device)
            logits, new_lens = model(feats, feat_lens)
            pred_ids = ctc_decode(logits, blank=0, lengths=new_lens)
            preds = [ids_to_text(p, vocab) for p in pred_ids]
            all_preds.extend(preds)
            for txt in batch["transcripts"]:
                all_labels.append(normalize_text(txt))
            if torch.cuda.is_available():
                peak_gpu_mb = max(peak_gpu_mb,
                                  torch.cuda.max_memory_allocated() / (1024 * 1024))
            if (i + 1) % 50 == 0:
                rate = (i + 1) * args.batch_size / (time.perf_counter() - t0)
                print(f"  [test] batch {i+1}/{len(test_loader)} rate={rate:.1f} samp/s")

    wall_time = time.perf_counter() - t0
    print(f"[from-scratch-test] inference done in {wall_time:.1f}s")

    # 6. Compute metrics
    metrics = compute_test_metrics(all_preds, all_labels)
    print(f"[from-scratch-test] WER: {metrics['wer']:.4f}, CER: {metrics['cer']:.4f}")

    # 7. Build per-sample predictions list
    predictions = []
    for i, (pred, label) in enumerate(zip(all_preds, all_labels)):
        # test_rows indices match all_preds order
        audio = test_rows[i]["rel_path"] if i < len(test_rows) else ""
        predictions.append({
            "idx": i, "audio": audio, "pred": pred, "label": label,
            "per_sample_wer": per_sample_wer(pred, label),
            "per_sample_cer": per_sample_cer(pred, label),
        })

    # 8. Slot identification
    arch_to_slot = {
        "bilstm": ("m07-bilstm-ctc", "Bi-LSTM CTC", True),
        "conformer": ("m06-conformer-ctc", "Conformer-CTC", True),
    }
    model_id, family, is_paper = arch_to_slot[args.arch]

    # 9. Write results
    json_path = write_test_results(
        out_dir=args.out_dir,
        model_id=model_id, family=family,
        is_paper_model=is_paper, is_user_novel=False,
        run_dir=args.run_dir,
        checkpoint_info=ckpt_info,
        test_set_info={"split": "test", "n_samples": len(all_preds),
                       "audio_root": str(args.data_root), "feature_format": "raw_audio"},
        metrics=metrics,
        decoding_info={"method": "greedy_ctc", "beam_size": 1, "lm": None,
                       "max_decode_len": None},
        wall_time_sec=wall_time,
        n_samples=len(all_preds),
        peak_gpu_mb=peak_gpu_mb,
        predictions=predictions,
    )
    print(f"[from-scratch-test] \u2713 {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
