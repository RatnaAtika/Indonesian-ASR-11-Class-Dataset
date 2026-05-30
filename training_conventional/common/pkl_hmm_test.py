"""HMM family test runner — m08 HMM-GMM + m09 DNN-HMM + m10 GMM-HMM-DNN.

Loads `best.pkl` (HMM artifact dict) dari run_dir, jalan scoring pada
test pickle, save JSON test_paper.json.

Usage:
    # m08 HMM-GMM template classifier
    python3 training_conventional/common/pkl_hmm_test.py \\
        --mode hmm_gmm \\
        --run-dir training_conventional/m08_hmm_gmm/runs/run_paper_20260601

    # m09 DNN-HMM
    python3 training_conventional/common/pkl_hmm_test.py \\
        --mode dnn_hmm \\
        --run-dir training_conventional/m09_dnn_hmm/runs/run_paper_20260601
"""
from __future__ import annotations
import argparse, sys, time, pickle
from pathlib import Path

import numpy as np
import torch

THIS = Path(__file__).parent
TC_ROOT = THIS.parent
sys.path.insert(0, str(TC_ROOT))

from common.pkl_hmm_trainer import (
    load_pkl, FrameDNN, stack_context,
)
from common.test_helper import (
    compute_test_metrics, per_sample_wer, per_sample_cer,
    find_best_checkpoint, write_test_results,
)
import sentencepiece as spm


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["hmm_gmm", "dnn_hmm", "gmm_hmm_dnn"], required=True)
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, default=None)
    p.add_argument("--data-pkl-dir", type=Path,
                   default=TC_ROOT / "data_pkl")
    p.add_argument("--spm-model", type=Path,
                   default=TC_ROOT / "spm" / "spm_v7_char.model")
    p.add_argument("--checkpoint", type=Path, default=None,
                   help="Override path ke best.pkl (default: auto-detect)")
    p.add_argument("--max-test-samples", type=int, default=0)
    return p.parse_args()


def test_hmm_gmm(artifact, test_data, sp, t0):
    """Score test utterances via argmax log-likelihood across HMM templates."""
    models = artifact["models"]
    template_keys = list(models.keys())
    preds, labels = [], []
    n_total = len(test_data["X"])
    for i, (x, txt) in enumerate(zip(test_data["X"], test_data["text"])):
        scores = []
        for tk in template_keys:
            try:
                s = models[tk].score(x)
                scores.append((s, tk))
            except Exception:
                scores.append((-1e30, tk))
        scores.sort(reverse=True)
        preds.append(scores[0][1])
        labels.append(txt.strip().lower())
        if (i + 1) % 1000 == 0:
            print(f"  [hmm-gmm-test] {i+1}/{n_total}  "
                  f"rate={(i+1)/(time.perf_counter()-t0):.1f} samp/s")
    return preds, labels


def test_dnn_hmm(artifact, test_data, sp, args, t0):
    """CTC frame DNN: argmax per frame -> collapse repeats -> remove blank (id 0)."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    train_args = artifact.get("args", {})
    F_dim = test_data["X"][0].shape[1]
    ctx = train_args.get("dnn_context", 5)
    in_dim = F_dim * (2 * ctx + 1)
    hidden = train_args.get("dnn_hidden", 512)
    layers = train_args.get("dnn_layers", 4)
    vocab_size = sp.get_piece_size()
    
    model = FrameDNN(in_dim, hidden, layers, vocab_size).to(device)
    if artifact.get("model_state"):
        model.load_state_dict(artifact["model_state"])
    model.eval()
    
    preds, labels = [], []
    n_total = len(test_data["X"])
    with torch.no_grad():
        for i, (x, txt) in enumerate(zip(test_data["X"], test_data["text"])):
            ctx_x = stack_context(x, ctx)
            xt = torch.from_numpy(ctx_x).float().to(device)
            logits = model(xt)
            tok_ids = logits.argmax(dim=-1).cpu().tolist()
            decoded = []
            prev = -1
            for t in tok_ids:
                if t != prev and t not in (0, 1, 2, 3):
                    decoded.append(t)
                prev = t
            try:
                decoded_text = sp.decode(decoded).strip()
            except Exception:
                decoded_text = ""
            preds.append(decoded_text)
            labels.append(txt.strip())
            if (i + 1) % 1000 == 0:
                rate = (i + 1) / (time.perf_counter() - t0)
                print(f"  [dnn-hmm-test] {i+1}/{n_total}  rate={rate:.1f} samp/s")
    return preds, labels


def main():
    args = parse_args()
    args.out_dir = args.out_dir or (args.run_dir / "test_results")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[hmm-test] mode: {args.mode}, run_dir: {args.run_dir}")
    
    # Locate checkpoint. HMM artifacts are PICKLE files (carry mode/args/state in
    # the structure test_*() expects); the per-epoch best.pt written by
    # BestCheckpointTracker is a torch state_dict and must NOT be pickle-loaded.
    if args.checkpoint:
        ckpt_info = {"path": str(args.checkpoint), "filename": args.checkpoint.name,
                     "format": "pkl", "best_wer": None, "best_epoch": None}
    else:
        ckpt_dir = args.run_dir / "checkpoints"
        cand = None
        if (ckpt_dir / "best.pkl").exists():
            cand = ckpt_dir / "best.pkl"
        else:
            finals = sorted(ckpt_dir.glob("best_wer*_final.pkl"))
            if finals:
                cand = finals[0]
        if cand is None:
            print(f"[ERROR] No HMM pickle checkpoint (best.pkl / best_wer*_final.pkl) "
                  f"found in {ckpt_dir}"); return 1
        ckpt_info = {"path": str(cand), "filename": cand.name, "format": "pkl",
                     "best_wer": None, "best_epoch": None}
    if not ckpt_info.get("path"):
        print(f"[ERROR] No checkpoint found"); return 1
    print(f"[hmm-test] checkpoint: {ckpt_info['filename']}")
    
    # Load artifact
    with open(ckpt_info["path"], "rb") as f:
        artifact = pickle.load(f)
    saved_mode = artifact.get("mode", args.mode)
    if saved_mode != args.mode:
        print(f"[WARN] mode mismatch: cli={args.mode} vs saved={saved_mode}")
    
    sp = spm.SentencePieceProcessor(model_file=str(args.spm_model))
    
    # Load test data
    test_data = load_pkl(args.data_pkl_dir / "test.pkl")
    if args.max_test_samples > 0:
        for k, v in test_data.items():
            if isinstance(v, list):
                test_data[k] = v[:args.max_test_samples]
    print(f"[hmm-test] test samples: {len(test_data['X'])}")
    
    # Run inference
    t0 = time.perf_counter()
    if args.mode == "hmm_gmm":
        preds, labels = test_hmm_gmm(artifact, test_data, sp, t0)
        decode_method = "viterbi_template_argmax"
    elif args.mode in ("dnn_hmm", "gmm_hmm_dnn"):
        preds, labels = test_dnn_hmm(artifact, test_data, sp, args, t0)
        decode_method = "ctc_greedy_collapse"
    else:
        print(f"[ERROR] unknown mode: {args.mode}"); return 1
    
    wall_time = time.perf_counter() - t0
    print(f"[hmm-test] inference done in {wall_time:.1f}s")
    
    metrics = compute_test_metrics(preds, labels)
    print(f"[hmm-test] WER: {metrics['wer']:.4f}, CER: {metrics['cer']:.4f}")
    
    # Per-sample predictions
    fnames = test_data.get("fnames", [])
    predictions = []
    for i, (pred, label) in enumerate(zip(preds, labels)):
        predictions.append({
            "idx": i,
            "audio": fnames[i] if i < len(fnames) else "",
            "pred": pred, "label": label,
            "per_sample_wer": per_sample_wer(pred, label),
            "per_sample_cer": per_sample_cer(pred, label),
        })
    
    # Slot identification
    mode_to_slot = {
        "hmm_gmm":     ("m08-hmm-gmm", "HMM-GMM template classifier", True),
        "dnn_hmm":     ("m09-dnn-hmm", "DNN-HMM hybrid", True),
        "gmm_hmm_dnn": ("m10-gmm-hmm-dnn", "GMM-HMM-DNN 3-stage", True),
    }
    model_id, family, is_paper = mode_to_slot[args.mode]
    
    json_path = write_test_results(
        out_dir=args.out_dir,
        model_id=model_id, family=family,
        is_paper_model=is_paper, is_user_novel=False,
        run_dir=args.run_dir,
        checkpoint_info=ckpt_info,
        test_set_info={"split": "test", "n_samples": len(preds),
                       "audio_root": "data_pkl", "feature_format": "pkl_logmel80"},
        metrics=metrics,
        decoding_info={"method": decode_method, "beam_size": 1, "lm": None,
                       "max_decode_len": None},
        wall_time_sec=wall_time,
        n_samples=len(preds),
        peak_gpu_mb=0.0,  # HMM CPU-only; DNN may use GPU but we don't track here
        predictions=predictions,
    )
    print(f"[hmm-test] \u2713 {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
