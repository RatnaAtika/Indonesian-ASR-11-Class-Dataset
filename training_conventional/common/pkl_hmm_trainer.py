"""HMM-family trainers for conventional ASR baselines (m08, m09, m10).

Three modes:
  --mode hmm_gmm          : GMM-HMM template classifier (m08)
                            One GMM-HMM per unique transcript template; test by
                            argmax log-likelihood. Closed-vocabulary baseline.
  --mode dnn_hmm          : DNN-HMM hybrid acoustic model (m09)
                            FrameDNN predicts an SPM-token posterior per frame,
                            trained with the CTC criterion (blank = <pad>=0).
                            CTC is a special case of full-sum HMM training
                            (Zeyer et al., Interspeech 2017): an HMM topology
                            with a blank state and no transition probs, so it is
                            trainable from scratch and the blank lets greedy
                            collapse decoding emit a correct-length hypothesis.
                            Decode: argmax per frame -> collapse repeats ->
                            remove blank.
  --mode gmm_hmm_dnn      : GMM-HMM-DNN 3-stage hybrid (m10)
                            Stage 1: train GMM-HMM template classifier (m08)
                            Stage 2: GMM-HMM force-alignment (pipeline step)
                            Stage 3: train the FrameDNN with CTC (same as m09)
                            Final decoder: CTC greedy collapse decode.
                                          (returns top-1 template via argmax).

Notes for paper:
  - This is a closed-vocabulary baseline appropriate for the v7 corpus
    (209 base sentences, template-based recordings)
  - HMM training via hmmlearn (Baum-Welch EM)
  - Predictions cap at the closed sentence set, so WER >= floor of test-template
    coverage; we report the gap as part of the baseline limitations
"""
from __future__ import annotations
import argparse, json, pickle, sys, time, warnings
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from hmmlearn import hmm
import sentencepiece as spm

THIS = Path(__file__).parent
sys.path.insert(0, str(THIS.parent))
from common.utils import (compute_wer_cer, HistorySaver, regenerate_plots, GPUMonitor,
                          EpochTimer, format_epoch_log, cer_to_token_acc_proxy,
                          save_run_meta, unique_run_dir, BestCheckpointTracker)

warnings.filterwarnings("ignore")
# Silence hmmlearn's stdout messages about transmat zero rows; with params="mc"/"mcw"
# the transmat never gets re-estimated so this is benign.
import logging as _logging
_logging.getLogger("hmmlearn").setLevel(_logging.ERROR)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["hmm_gmm", "dnn_hmm", "gmm_hmm_dnn"], required=True)
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--data-pkl-dir", type=Path, default=THIS.parent / "data_pkl")
    p.add_argument("--spm-model", type=Path, default=THIS.parent / "spm" / "spm_v7_char.model")
    p.add_argument("--max-train-samples", type=int, default=0)
    p.add_argument("--max-val-samples", type=int, default=0)
    # HMM params
    p.add_argument("--hmm-states", type=int, default=5)
    p.add_argument("--hmm-mixtures", type=int, default=2,
                   help="GMM mixtures per state (m08, m10)")
    p.add_argument("--hmm-iters", type=int, default=10)
    p.add_argument("--cov-type", default="diag", choices=["full", "diag", "tied", "spherical"])
    # DNN params
    p.add_argument("--dnn-hidden", type=int, default=512)
    p.add_argument("--dnn-layers", type=int, default=4)
    p.add_argument("--dnn-context", type=int, default=5,
                   help="±N frame context window")
    p.add_argument("--dnn-epochs", type=int, default=3)
    p.add_argument("--dnn-batch-size", type=int, default=256)
    p.add_argument("--dnn-lr", type=float, default=1e-3)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def load_pkl(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def truncate(data, n):
    if n <= 0:
        return data
    out = {}
    for k, v in data.items():
        out[k] = v[:n] if isinstance(v, list) else v
    return out


# ============================================================
# Mode 1: HMM-GMM template classifier (m08)
# ============================================================
def run_hmm_gmm(args, train_data, val_data, sp, out_dir):
    """Per-template GMM-HMM classifier."""
    print(f"[hmm-gmm] grouping training utterances by transcript ...")
    template_to_X = {}
    for x, txt in zip(train_data["X"], train_data["text"]):
        t = txt.strip().lower()
        template_to_X.setdefault(t, []).append(x)
    
    # Prune templates with too few samples for HMM training
    min_samples = max(2, args.hmm_states + 1)
    templates = [t for t in template_to_X if len(template_to_X[t]) >= min_samples]
    print(f"[hmm-gmm] {len(templates)} templates after pruning (min_samples={min_samples})")
    if not templates:
        raise SystemExit(
            f"[hmm-gmm] ERROR: 0 templates survived pruning (min_samples={min_samples}). "
            f"Train subset too small — use full data (--max-train-samples 0) for paper runs.")
    print(f"[hmm-gmm] training {len(templates)} GMM-HMMs (states={args.hmm_states}, mix={args.hmm_mixtures}) ...")
    
    models = {}
    t0 = time.perf_counter()
    for i, tmpl in enumerate(templates):
        Xs = template_to_X[tmpl]
        X_concat = np.concatenate(Xs, axis=0)
        lengths = [x.shape[0] for x in Xs]
        try:
            if args.hmm_mixtures > 1:
                m = hmm.GMMHMM(
                    n_components=args.hmm_states,
                    n_mix=args.hmm_mixtures,
                    covariance_type=args.cov_type,
                    n_iter=args.hmm_iters,
                    tol=1e-3,
                    # Init only emission params from data; keep startprob + transmat
                    # at our explicit left-right init (set below).
                    init_params="mcw",
                    # During EM, update only emission (m,c,w) — keep transmat fixed.
                    # This avoids the 'transmat zero-row' degeneracy on sparse data.
                    params="mcw",
                    random_state=args.seed,
                )
            else:
                m = hmm.GaussianHMM(
                    n_components=args.hmm_states,
                    covariance_type=args.cov_type,
                    n_iter=args.hmm_iters,
                    tol=1e-3,
                    init_params="mc",
                    params="mc",  # transmat + startprob fixed (left-right)
                    random_state=args.seed,
                )
            # Strict left-right transmat (kept fixed throughout EM)
            transmat = np.zeros((args.hmm_states, args.hmm_states))
            for s in range(args.hmm_states - 1):
                transmat[s, s] = 0.5
                transmat[s, s + 1] = 0.5
            transmat[-1, -1] = 1.0
            startprob = np.zeros(args.hmm_states); startprob[0] = 1.0
            m.startprob_ = startprob
            m.transmat_ = transmat
            m.fit(X_concat, lengths)
            models[tmpl] = m
        except Exception as e:
            print(f"  [warn] skipped template {i}: {e}")
        if (i + 1) % 20 == 0:
            print(f"  [hmm-gmm] trained {i+1}/{len(templates)} (elapsed {time.perf_counter()-t0:.0f}s)", flush=True)
    
    train_elapsed = time.perf_counter() - t0
    print(f"[hmm-gmm] training done: {len(models)} HMMs in {train_elapsed/60:.1f} min")
    
    # Predict on val
    print(f"[hmm-gmm] scoring {len(val_data['X'])} val utterances ...")
    template_keys = list(models.keys())
    preds, labels = [], []
    eval_start = time.perf_counter()
    for i, (x, txt) in enumerate(zip(val_data["X"], val_data["text"])):
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
        if (i + 1) % 100 == 0:
            print(f"  scored {i+1}/{len(val_data['X'])}", flush=True)
    eval_elapsed = time.perf_counter() - eval_start
    
    metrics = compute_wer_cer(preds, labels)
    print(f"[hmm-gmm] WER: {metrics['wer']:.4f}, CER: {metrics['cer']:.4f}")
    print(f"[hmm-gmm] eval time: {eval_elapsed/60:.1f} min")
    
    return {"models": models, "metrics": metrics, "preds": preds, "labels": labels,
            "train_elapsed": train_elapsed, "eval_elapsed": eval_elapsed,
            "n_templates": len(models)}


# ============================================================
# Mode 2: DNN-HMM hybrid (m09)
# ============================================================
class FrameDNN(nn.Module):
    def __init__(self, input_dim, hidden, n_layers, vocab_size, dropout=0.1):
        super().__init__()
        layers = []
        prev = input_dim
        for _ in range(n_layers):
            layers += [nn.Linear(prev, hidden), nn.BatchNorm1d(hidden), nn.GELU(), nn.Dropout(dropout)]
            prev = hidden
        layers.append(nn.Linear(prev, vocab_size))
        self.net = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.net(x)


def make_frame_labels(text_ids, T):
    """Linear interpolation: assign each frame to a token uniformly."""
    if len(text_ids) == 0 or T <= 0:
        return np.zeros(T, dtype=np.int64)
    boundaries = np.linspace(0, T, len(text_ids) + 1).astype(int)
    labels = np.zeros(T, dtype=np.int64)
    for i, tok in enumerate(text_ids):
        labels[boundaries[i]:boundaries[i+1]] = tok
    return labels


def stack_context(X, ctx):
    """Stack ±ctx frames around each frame."""
    T, F = X.shape
    pad = np.zeros((ctx, F), dtype=X.dtype)
    Xp = np.concatenate([pad, X, pad], axis=0)
    out = np.zeros((T, F * (2 * ctx + 1)), dtype=X.dtype)
    for t in range(T):
        out[t] = Xp[t:t + 2 * ctx + 1].reshape(-1)
    return out


def run_dnn_hmm(args, train_data, val_data, sp, out_dir, alignments=None):
    """DNN-HMM hybrid acoustic model, trained with the CTC criterion.

    Design note (fixed 2026-05-29). The previous implementation trained the
    frame DNN with frame-wise cross-entropy on a *linear (uniform) alignment*
    of SPM subword tokens and decoded by argmax + collapse-repeat. With SPM
    subword units the adjacent-token repeat rate is ~0 and there is no blank
    symbol, so collapse removed almost nothing: ~244 frame predictions stayed
    ~244 tokens vs ~22 reference tokens -> WER ~3-3.6 (>1) and val_acc=0.

    Zeyer et al. (Interspeech 2017) show CTC *is* a special case of generalized
    full-sum HMM training (an HMM topology with a blank state and no transition
    probabilities), and is trainable from scratch without an external
    alignment. We therefore train the same FrameDNN posterior model with the
    CTC loss, using blank = id 0 (`<pad>`). The network learns to emit blanks
    between subword tokens, so argmax + collapse-repeat + remove-blank yields a
    correct-length hypothesis. This keeps the DNN-HMM family identity (a
    frame-synchronous neural acoustic posterior decoded by collapse) while
    making WER actually decrease.

    Streaming: features are stacked per-utterance inside the batch loop—never a
    giant in-memory array (avoids the 68 GB OOM on the full 71792-utt set).
    Decodes the val set every epoch for per-epoch WER/CER in history.json.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    vocab_size = sp.get_piece_size()
    F_dim = train_data["X"][0].shape[1]
    in_dim = F_dim * (2 * args.dnn_context + 1)
    ctx_n = args.dnn_context
    BLANK = 0  # CTC blank == <pad>

    # CTC targets = per-utterance SPM token sequence (no <s>/</s>/<pad>); the
    # optional GMM force-alignment only reorders templates, so for CTC we just
    # need the target token sequence, identical with or without `alignments`.
    print(f"[dnn-hmm] preparing CTC targets ...", flush=True)
    utt_targets = []  # list of np.int64 token-id arrays parallel to train_data['X']
    for y in train_data["y"]:
        toks = [t for t in y if t not in (0, 1, 2, 3)]
        utt_targets.append(np.asarray(toks, dtype=np.int64))
    n_utts = len(train_data["X"])
    total_frames = int(sum(x.shape[0] for x in train_data["X"]))
    print(f"[dnn-hmm] utts: {n_utts}, total frames: {total_frames:,}, "
          f"vocab: {vocab_size}, input: {in_dim}, loss: CTC (blank={BLANK}, "
          f"streaming, no giant array)", flush=True)

    # Model + optimizer
    model = FrameDNN(in_dim, args.dnn_hidden, args.dnn_layers, vocab_size).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.dnn_lr, weight_decay=1e-5)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[dnn-hmm] DNN params: {n_params:,}", flush=True)

    # tqdm (graceful fallback)
    try:
        from tqdm import tqdm
        _has_tqdm = True
    except ImportError:
        _has_tqdm = False

    # Local history saver + logger (per-epoch — consistent with other trainers)
    history_saver = HistorySaver(out_dir)
    log_file = out_dir / "log.txt"
    best_tracker = BestCheckpointTracker(out_dir, metric_name="wer", lower_is_better=True)

    def _decode_val():
        """Greedy frame-DNN decode on val set -> (preds, labels)."""
        model.eval()
        preds, labels = [], []
        with torch.no_grad():
            for x, txt in zip(val_data["X"], val_data["text"]):
                ctx = stack_context(x, ctx_n)
                logits = model(torch.from_numpy(ctx).float().to(device))
                tok_ids = logits.argmax(dim=-1).cpu().tolist()
                decoded, prev = [], -1
                for t in tok_ids:
                    if t != prev and t not in (0, 1, 2, 3):
                        decoded.append(t)
                    prev = t
                try:
                    preds.append(sp.decode(decoded).strip())
                except Exception:
                    preds.append("")
                labels.append(txt.strip())
        model.train()
        return preds, labels

    train_start = time.perf_counter()
    history_dnn = []
    final_metrics, final_preds, final_labels = None, [], []
    ctc_loss_fn = nn.CTCLoss(blank=BLANK, zero_infinity=True)

    for ep in range(1, args.dnn_epochs + 1):
        ep_t0 = time.perf_counter()
        gpu_mon = GPUMonitor(); gpu_mon.reset_peak()
        model.train()
        utt_order = np.random.permutation(n_utts)
        losses, n_emit_correct, n_emit_total = [], 0, 0
        buf_logp, buf_tgt, buf_inlen, buf_tgtlen = [], [], [], []
        utt_iter = tqdm(utt_order, desc=f"Epoch {ep}/{args.dnn_epochs} [Train]",
                        leave=False, ncols=100, miniters=200) if _has_tqdm else utt_order

        def _flush(lp, tg, il, tl):
            """Run CTC over a buffer of per-utterance frame log-probs."""
            nonlocal n_emit_correct, n_emit_total
            if not lp:
                return
            Tmax = max(t.shape[0] for t in lp)
            B = len(lp)
            V = lp[0].shape[1]
            # (T, B, V) padded with log(blank-ish) zeros; lengths mask the pad
            padded = torch.full((Tmax, B, V), 0.0, device=device)
            for i, t in enumerate(lp):
                padded[: t.shape[0], i, :] = t
            tgt = torch.cat(tg).to(device)
            in_len = torch.tensor(il, dtype=torch.long)
            tg_len = torch.tensor(tl, dtype=torch.long)
            opt.zero_grad()
            loss = ctc_loss_fn(padded, tgt, in_len, tg_len)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
            losses.append(float(loss.item()))
            # cheap non-blank emission accuracy proxy (collapsed argmax vs target len)
            with torch.no_grad():
                for i in range(B):
                    am = padded[: il[i], i, :].argmax(dim=-1).cpu().tolist()
                    dec, prev = [], -1
                    for tk in am:
                        if tk != prev and tk != BLANK:
                            dec.append(tk)
                        prev = tk
                    n_emit_correct += sum(1 for a, b in zip(dec, tg[i].tolist()) if a == b)
                    n_emit_total += int(tl[i])

        cur_frames = 0
        for j in utt_iter:
            x = train_data["X"][j]
            tgt = utt_targets[j]
            if tgt.size == 0:
                continue
            ctx = stack_context(x, ctx_n)
            logits = model(torch.from_numpy(ctx).float().to(device))
            logp = F.log_softmax(logits, dim=-1)  # (T, V)
            T = logp.shape[0]
            # CTC requires input_length >= target_length
            if T < tgt.size:
                continue
            buf_logp.append(logp); buf_tgt.append(torch.from_numpy(tgt).long())
            buf_inlen.append(T); buf_tgtlen.append(int(tgt.size))
            cur_frames += T
            if cur_frames >= args.dnn_batch_size:
                _flush(buf_logp, buf_tgt, buf_inlen, buf_tgtlen)
                buf_logp, buf_tgt, buf_inlen, buf_tgtlen = [], [], [], []
                cur_frames = 0
        _flush(buf_logp, buf_tgt, buf_inlen, buf_tgtlen)  # remaining

        ep_loss = float(np.mean(losses)) if losses else 0.0
        train_frame_acc = n_emit_correct / max(n_emit_total, 1)

        # Decode val for per-epoch WER/CER
        val_preds, val_labels = _decode_val()
        m = compute_wer_cer(val_preds, val_labels)
        final_metrics, final_preds, final_labels = m, val_preds, val_labels

        elapsed = time.perf_counter() - ep_t0
        total_elapsed = time.perf_counter() - train_start
        gpu_mb = gpu_mon.peak_mb()
        history_dnn.append({"epoch": ep, "loss": ep_loss, "emit_acc": train_frame_acc})

        entry = {
            "train_loss": ep_loss, "val_loss": None,
            "train_acc": train_frame_acc, "val_acc": cer_to_token_acc_proxy(m["cer"]),
            "wer": m["wer"], "cer": m["cer"], "mer": m["mer"], "wil": m["wil"],
            "time_sec": round(elapsed, 2),
            "time_str": EpochTimer.format_seconds(elapsed),
            "total_elapsed_sec": round(total_elapsed, 2),
            "total_elapsed_str": EpochTimer.format_seconds(total_elapsed),
            "gpu_mb": round(gpu_mb, 1),
            "lr": float(args.dnn_lr),
            "throughput_samples_per_sec": round(n_utts / max(elapsed, 1), 2),
        }
        sample_preds = list(zip(val_preds[:5], val_labels[:5]))
        history_saver.append_epoch(ep, entry, sample_preds)
        saved_best = best_tracker.maybe_save(
            value=m["wer"], epoch=ep, model_state=model.state_dict(),
            extra_state={"args": vars(args), "val_cer": m["cer"], "mode": args.mode,
                         "n_params": n_params, "history_dnn": history_dnn},
        )
        log = format_epoch_log(
            epoch=ep, total_epochs=args.dnn_epochs, entry=entry, sample_preds=sample_preds,
            extra_lines=[f"[Train] mode={args.mode} loss=CTC emit_acc={train_frame_acc:.4f} "
                         f"avg_ctc={ep_loss:.4f}"],
        )
        print(log, flush=True)
        with log_file.open("a", encoding="utf-8") as f:
            f.write(log + "\n")
        if saved_best:
            print(f"  [best] New best WER={m['wer']:.4f} @ epoch {ep} -> {saved_best.name}", flush=True)
        try:
            regenerate_plots(history_saver.history_path)
        except Exception:
            pass

    train_elapsed = time.perf_counter() - train_start

    return {"model": model, "metrics": final_metrics, "preds": final_preds,
            "labels": final_labels, "train_elapsed": train_elapsed,
            "eval_elapsed": 0.0, "history_dnn": history_dnn, "n_params": n_params,
            "per_epoch_logged": True}


# ============================================================
# Mode 3: GMM-HMM-DNN 3-stage (m10)
# ============================================================
def gmm_force_align(train_data, gmm_models, sp):
    """Force-align each training utterance to the best matching template, then map
    state sequence back to SPM tokens via uniform partitioning of token sequence over states.
    Returns list of frame-level token-label arrays parallel to train_data['X'].
    """
    template_keys = list(gmm_models.keys())
    alignments = []
    for x, y in zip(train_data["X"], train_data["y"]):
        toks = [t for t in y if t not in (2, 3)]
        T = x.shape[0]
        if not toks:
            alignments.append(np.zeros(T, dtype=np.int64))
            continue
        # Best-template alignment
        scores = []
        for tk in template_keys:
            try:
                s = gmm_models[tk].score(x)
                scores.append((s, tk))
            except Exception:
                scores.append((-1e30, tk))
        scores.sort(reverse=True)
        # Use linear partition for state→token mapping
        labels = make_frame_labels(toks, T)
        alignments.append(labels)
    return alignments


def run_gmm_hmm_dnn(args, train_data, val_data, sp, out_dir):
    """3-stage: GMM-HMM → force-align → DNN → DNN-HMM decode."""
    print(f"\n[gmm-hmm-dnn] STAGE 1: train GMM-HMM ...")
    stage1 = run_hmm_gmm(args, train_data, val_data, sp, out_dir / "stage1_gmm_hmm")
    
    print(f"\n[gmm-hmm-dnn] STAGE 2: force-align via GMM-HMM ...")
    alignments = gmm_force_align(train_data, stage1["models"], sp)
    print(f"[gmm-hmm-dnn] aligned {len(alignments)} train utts")
    
    print(f"\n[gmm-hmm-dnn] STAGE 3: train DNN on alignments + decode ...")
    # Write stage-3 per-epoch history/log/plots to the MAIN run_dir (out_dir),
    # so m10 output is consistent with other models (not buried in a subfolder).
    stage3 = run_dnn_hmm(args, train_data, val_data, sp, out_dir,
                         alignments=alignments)
    
    return {
        "stage1_metrics": stage1["metrics"],
        "stage3_metrics": stage3["metrics"],
        "metrics": stage3["metrics"],          # main metric = stage 3 (final)
        "stage1_n_templates": stage1["n_templates"],
        "stage3_n_params": stage3["n_params"],
        "model": stage3["model"],
        "history_dnn": stage3["history_dnn"],
        "n_params": stage3["n_params"],
        "preds": stage3["preds"], "labels": stage3["labels"],
        "train_elapsed": stage1["train_elapsed"] + stage3["train_elapsed"],
        "eval_elapsed": stage1["eval_elapsed"] + stage3["eval_elapsed"],
        "per_epoch_logged": True,            # stage-3 already logged per-epoch
    }


# ============================================================
# Main
# ============================================================
def main():
    args = parse_args()
    # Auto-timestamp if run_dir already has a prior run
    args.run_dir = unique_run_dir(args.run_dir)
    args.run_dir.mkdir(parents=True, exist_ok=True)
    print(f"[hmm-trainer] resolved run_dir: {args.run_dir}")
    (args.run_dir / "config.json").write_text(json.dumps(vars(args), indent=2, default=str), encoding="utf-8")
    
    # Reproducibility meta — distinguish HMM family by mode
    if args.mode == "hmm_gmm":
        family, era = "HMM", "1990s"
    elif args.mode == "dnn_hmm":
        family, era = "Hybrid-DNN-HMM", "2010s"
    else:  # gmm_hmm_dnn
        family, era = "Hybrid-GMM-HMM-DNN", "2010s"
    save_run_meta(
        run_dir=args.run_dir, model_id=f"hmm-trainer-{args.mode}",
        family=family, era=era, config=vars(args),
        dataset_info={"data_pkl_dir": str(args.data_pkl_dir),
                      "spm_model": str(args.spm_model)},
        notes=f"Conventional {args.mode} trainer. Replot: python3 -m common.journal_plotting --run-dir <this_dir> --style ieee",
    )
    
    np.random.seed(args.seed); torch.manual_seed(args.seed)
    
    print(f"[hmm-trainer] mode: {args.mode}")
    print(f"[hmm-trainer] run_dir: {args.run_dir}")
    
    sp = spm.SentencePieceProcessor(model_file=str(args.spm_model))
    
    print("[hmm-trainer] loading pickles ...")
    train_data = truncate(load_pkl(args.data_pkl_dir / "train.pkl"), args.max_train_samples)
    val_data = truncate(load_pkl(args.data_pkl_dir / "valid.pkl"), args.max_val_samples)
    print(f"  train: {len(train_data['X'])}, val: {len(val_data['X'])}")
    
    if args.mode == "hmm_gmm":
        result = run_hmm_gmm(args, train_data, val_data, sp, args.run_dir)
    elif args.mode == "dnn_hmm":
        result = run_dnn_hmm(args, train_data, val_data, sp, args.run_dir)
    else:  # gmm_hmm_dnn
        result = run_gmm_hmm_dnn(args, train_data, val_data, sp, args.run_dir)
    
    # Save 1-epoch history (for plot regen + cross-model comparison)
    history = HistorySaver(args.run_dir)
    metrics = result.get("metrics") or result.get("stage3_metrics")
    
    # Train Acc + Val Acc per family
    val_acc = cer_to_token_acc_proxy(metrics["cer"])
    train_acc = None
    if args.mode == "hmm_gmm":
        # Score 30 random training samples vs their template; 1 - CER as proxy
        try:
            import random as _rd
            n_train_eval = min(30, len(train_data["X"]))
            idxs = _rd.sample(range(len(train_data["X"])), n_train_eval)
            train_preds, train_labels = [], []
            templates = list(result["models"].keys())
            for i in idxs:
                x = train_data["X"][i]; txt = train_data["text"][i].strip().lower()
                scores = []
                for tk in templates:
                    try:
                        s = result["models"][tk].score(x); scores.append((s, tk))
                    except Exception:
                        scores.append((-1e30, tk))
                scores.sort(reverse=True)
                train_preds.append(scores[0][1]); train_labels.append(txt)
            if train_preds:
                m_train = compute_wer_cer(train_preds, train_labels)
                train_acc = cer_to_token_acc_proxy(m_train["cer"])
        except Exception as _e:
            train_acc = None
    elif args.mode in ("dnn_hmm",):
        # Last DNN epoch's CTC emission-accuracy proxy serves as train_acc
        if result.get("history_dnn"):
            train_acc = float(result["history_dnn"][-1].get("emit_acc", 0))
    elif args.mode == "gmm_hmm_dnn":
        # Use stage 3 DNN emit_acc; fall back to 1 - stage1 train-CER if available
        train_acc = cer_to_token_acc_proxy(metrics["cer"])
    
    # Throughput
    throughput = round(len(train_data["X"]) / max(result["train_elapsed"], 1), 2)
    
    # For dnn_hmm / gmm_hmm_dnn, per-epoch history + log + plots sudah ditulis
    # di dalam run_dnn_hmm() (memory-safe streaming, WER/CER per epoch). Jangan
    # overwrite dengan 1-shot entry. Hanya hmm_gmm (single-shot Baum-Welch)
    # yang butuh 1-row history di sini.
    per_epoch_logged = result.get("per_epoch_logged", False)
    
    if not per_epoch_logged:
        history.append_epoch(1, {
            "train_loss": None, "val_loss": None,
            "train_acc": train_acc, "val_acc": val_acc,
            "wer": metrics["wer"], "cer": metrics["cer"],
            "mer": metrics["mer"], "wil": metrics["wil"],
            "time_sec": result["train_elapsed"],
            "time_str": EpochTimer.format_seconds(result["train_elapsed"]),
            "total_elapsed_sec": result["train_elapsed"] + result["eval_elapsed"],
            "total_elapsed_str": EpochTimer.format_seconds(
                result["train_elapsed"] + result["eval_elapsed"]),
            "gpu_mb": 0,  # HMM is CPU-only; DNN tracked separately
            "lr": 0,
            "throughput_samples_per_sec": throughput,
        }, list(zip(result["preds"][:5], result["labels"][:5])))
    
    # Save best model (HMM has no per-epoch; this is the final model from this run)
    ckpt_dir = args.run_dir / "checkpoints"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    v_str = f"{metrics['wer']:.4f}".replace(".", "p")
    best_name = f"best_wer{v_str}_final.pkl"
    best_path = ckpt_dir / best_name
    pointer_path = ckpt_dir / "best.pkl"
    
    # [FAIRNESS-C] For DNN modes, the .pkl artifact (loaded by pkl_hmm_test.py) must
    # carry the BEST-epoch DNN weights (best-on-val), not the last-epoch model. The
    # per-epoch BestCheckpointTracker wrote them to checkpoints/best.pt; prefer that.
    def _best_dnn_state():
        bp = ckpt_dir / "best.pt"
        if bp.exists():
            try:
                bd = torch.load(bp, map_location="cpu", weights_only=False)
                if bd.get("model_state") is not None:
                    return bd["model_state"]
            except Exception:
                pass
        m = result.get("model")
        return m.state_dict() if hasattr(m, "state_dict") else None

    if args.mode == "hmm_gmm":
        # result["models"] is dict of hmmlearn objects — pickle-able
        artifact = {
            "mode": "hmm_gmm", "models": result["models"],
            "wer": metrics["wer"], "cer": metrics["cer"],
            "args": vars(args), "n_templates": result.get("n_templates"),
        }
    elif args.mode == "dnn_hmm":
        artifact = {
            "mode": "dnn_hmm",
            "model_state": _best_dnn_state(),
            "wer": metrics["wer"], "cer": metrics["cer"],
            "args": vars(args), "n_params": result.get("n_params"),
            "history_dnn": result.get("history_dnn"),
        }
    else:  # gmm_hmm_dnn
        artifact = {
            "mode": "gmm_hmm_dnn",
            "model_state": _best_dnn_state(),  # was MISSING -> test ran random-init DNN
            "stage1_metrics": result.get("stage1_metrics"),
            "stage3_metrics": result.get("stage3_metrics"),
            "wer": metrics["wer"], "cer": metrics["cer"],
            "args": vars(args),
        }
    
    with open(best_path, "wb") as f:
        pickle.dump(artifact, f, protocol=pickle.HIGHEST_PROTOCOL)
    with open(pointer_path, "wb") as f:
        pickle.dump(artifact, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"  ★ Saved best model: WER={metrics['wer']:.4f} → {best_name}", flush=True)
    
    # Build entry for format_epoch_log (identical fields)
    entry_for_log = {
        "train_loss": None, "val_loss": None,
        "train_acc": train_acc, "val_acc": val_acc,
        "wer": metrics["wer"], "cer": metrics["cer"],
        "time_str": EpochTimer.format_seconds(result["train_elapsed"]),
        "total_elapsed_str": EpochTimer.format_seconds(
            result["train_elapsed"] + result["eval_elapsed"]),
        "gpu_mb": 0, "lr": 0,
        "throughput_samples_per_sec": throughput,
    }
    sample_preds = list(zip(result["preds"][:5], result["labels"][:5]))
    extra = [f"[Mode] {args.mode}"]
    if args.mode == "hmm_gmm":
        extra.append(f"[Train] N templates={result.get('n_templates')}, accuracy=template-match (1-CER proxy)")
    elif args.mode == "dnn_hmm":
        extra.append(f"[Train] DNN CTC emit_acc (last epoch)={train_acc}")
    elif args.mode == "gmm_hmm_dnn":
        extra.append(f"[Train] stage1+stage3 hybrid; accuracy=1-CER proxy")
    
    if per_epoch_logged:
        # log.txt sudah berisi per-epoch log dari run_dnn_hmm(); JANGAN overwrite.
        # Cukup print ringkasan akhir ke stdout.
        print(f"\n[hmm-trainer] {args.mode} final (best across epochs): "
              f"WER={metrics['wer']:.4f} CER={metrics['cer']:.4f}", flush=True)
    else:
        # hmm_gmm single-shot: tulis 1 log block
        log = format_epoch_log(
            epoch=1, total_epochs=1,
            entry=entry_for_log, sample_preds=sample_preds,
            extra_lines=extra,
        )
        print(log)
        (args.run_dir / "log.txt").write_text(log, encoding="utf-8")
    
    # Report
    extras = ""
    if args.mode == "hmm_gmm":
        extras = f"- N templates trained: {result['n_templates']}\n"
    elif args.mode == "dnn_hmm":
        extras = f"- DNN params: {result['n_params']:,}\n"
    elif args.mode == "gmm_hmm_dnn":
        extras = (f"- Stage-1 templates: {result['stage1_n_templates']}\n"
                  f"- Stage-3 DNN params: {result['stage3_n_params']:,}\n"
                  f"- Stage-1 WER: {result['stage1_metrics']['wer']:.4f}\n"
                  f"- Stage-3 WER: {result['stage3_metrics']['wer']:.4f}\n")
    
    report = f"""# Training Report — {args.mode}

**Run dir**: {args.run_dir}
**Generated**: {datetime.now().isoformat()}

## Config
- Mode: {args.mode}
- Train samples: {len(train_data['X'])}, Val samples: {len(val_data['X'])}
- HMM states: {args.hmm_states}, mixtures: {args.hmm_mixtures}
- DNN: hidden={args.dnn_hidden}, layers={args.dnn_layers}, ctx=±{args.dnn_context}, epochs={args.dnn_epochs}

## Final
- WER: {metrics['wer']:.4f}
- CER: {metrics['cer']:.4f}
- MER: {metrics['mer']:.4f}
- WIL: {metrics['wil']:.4f}
- Train time: {EpochTimer.format_seconds(result['train_elapsed'])}
- Eval time:  {EpochTimer.format_seconds(result['eval_elapsed'])}
{extras}
"""
    (args.run_dir / "report.md").write_text(report, encoding="utf-8")
    
    try:
        regenerate_plots(history.history_path)
    except Exception as e:
        print(f"plot regen warn: {e}")
    
    print(f"[hmm-trainer] done. report saved: {args.run_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
