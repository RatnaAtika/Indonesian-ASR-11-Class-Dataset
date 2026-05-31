"""From-scratch training (Bi-LSTM CTC, Conformer-CTC small) untuk paper baseline.

Both use char-level vocab + log-Mel features + CTC loss.

Usage:
    # Bi-LSTM CTC (DeepSpeech-2 style)
    python3 -m training.common.from_scratch_trainer \\
        --arch bilstm \\
        --run-dir training/m07_bilstm_ctc/runs/run_smoke

    # Conformer-CTC small
    python3 -m training.common.from_scratch_trainer \\
        --arch conformer \\
        --run-dir training/m06_conformer_ctc/runs/run_smoke
"""
from __future__ import annotations
import argparse, csv, json, math, os, re, sys, time, unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchaudio
import jiwer
import soundfile as sf
from torch.utils.data import Dataset, DataLoader

TRAINING_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(TRAINING_ROOT))

from common.utils import (
    compute_wer_cer, HistorySaver, regenerate_plots, GPUMonitor, EpochTimer,
    format_epoch_log, cer_to_token_acc_proxy, save_run_meta, unique_run_dir,
    BestCheckpointTracker,
)


# ============================================================
# Args
# ============================================================
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--arch", choices=["bilstm", "conformer"], required=True)
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--data-root", type=Path,
                   default=TRAINING_ROOT.parent / "Processed_Balanced19_v7_natural_synth" / "Dataset_Balanced19")
    p.add_argument("--data-final", type=Path, default=TRAINING_ROOT / "data_final")
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--grad-accum", type=int, default=1,
                   help="Gradient accumulation steps (effective batch = batch_size * grad_accum). "
                        "Use --batch-size 16 --grad-accum 4 for effective 64 on 8 GB VRAM.")
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--max-train-samples", type=int, default=0)
    p.add_argument("--max-val-samples", type=int, default=0)
    p.add_argument("--n-mels", type=int, default=80)
    p.add_argument("--hidden-size", type=int, default=512)
    p.add_argument("--num-layers", type=int, default=4)
    p.add_argument("--dropout", type=float, default=0.1)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--fp16", action="store_true", default=True)
    return p.parse_args()


# ============================================================
# Utils
# ============================================================
def load_split_rows(tsv_path, dataset_root, max_samples=0):
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


def normalize_text(t):
    t = unicodedata.normalize("NFKC", t).lower()
    t = re.sub(r"[^a-z\s']", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def build_charvocab(rows, blank_id=0, unk_id=1):
    chars = set()
    for r in rows:
        for c in normalize_text(r["transcript"]):
            chars.add(c)
    vocab = ["<blank>", "<unk>"]
    for c in sorted(chars):
        vocab.append(c)
    return vocab


def text_to_ids(text, vocab):
    char2id = {c: i for i, c in enumerate(vocab)}
    return [char2id.get(c, 1) for c in normalize_text(text)]


def ids_to_text(ids, vocab):
    return "".join(vocab[i] if i < len(vocab) and vocab[i] not in ("<blank>", "<unk>") else "" for i in ids)


def ctc_decode(logits, blank=0, lengths=None):
    """Greedy CTC decode. When `lengths` (per-sample valid output frames) is given,
    truncate each sequence before collapsing so padded-tail frames don't emit
    spurious tokens (which inflate WER/CER above 1.0 early in training)."""
    pred = logits.argmax(dim=-1).cpu().tolist()
    if lengths is not None:
        lengths = [int(x) for x in lengths]
    out = []
    for i, seq in enumerate(pred):
        if lengths is not None:
            seq = seq[: lengths[i]]
        prev = blank
        result = []
        for tok in seq:
            if tok != prev and tok != blank:
                result.append(tok)
            prev = tok
        out.append(result)
    return out


# ============================================================
# Dataset
# ============================================================
class CTCDataset(Dataset):
    def __init__(self, rows, vocab, n_mels=80):
        self.rows = rows
        self.vocab = vocab
        self.mel = torchaudio.transforms.MelSpectrogram(
            sample_rate=16000, n_fft=400, win_length=400, hop_length=160, n_mels=n_mels)
    
    def __len__(self):
        return len(self.rows)
    
    def __getitem__(self, idx):
        r = self.rows[idx]
        audio, sr = sf.read(r["audio_path"], dtype="float32")
        if audio.ndim > 1:
            audio = audio.mean(axis=1).astype(np.float32)
        audio_t = torch.tensor(audio).unsqueeze(0)
        feats = self.mel(audio_t).squeeze(0)  # (n_mels, T)
        feats = torch.log1p(feats)
        # Normalize
        feats = (feats - feats.mean()) / (feats.std() + 1e-8)
        labels = torch.tensor(text_to_ids(r["transcript"], self.vocab), dtype=torch.long)
        return {"features": feats, "labels": labels, "transcript": r["transcript"]}


def collate_fn(batch):
    feats = [b["features"] for b in batch]
    labels = [b["labels"] for b in batch]
    transcripts = [b["transcript"] for b in batch]
    feat_lens = torch.tensor([f.shape[1] for f in feats], dtype=torch.long)
    label_lens = torch.tensor([l.shape[0] for l in labels], dtype=torch.long)
    # Pad features to (B, n_mels, T_max)
    T_max = max(f.shape[1] for f in feats)
    n_mels = feats[0].shape[0]
    feat_pad = torch.zeros(len(feats), n_mels, T_max)
    for i, f in enumerate(feats):
        feat_pad[i, :, :f.shape[1]] = f
    labels_concat = torch.cat(labels)
    return {
        "features": feat_pad,
        "feat_lens": feat_lens,
        "labels": labels_concat,
        "label_lens": label_lens,
        "transcripts": transcripts,
    }


# ============================================================
# Models
# ============================================================
class BiLSTMCTC(nn.Module):
    """DeepSpeech-2 style: 2-layer CNN frontend + Bi-LSTM stack + CTC."""
    
    def __init__(self, n_mels, hidden_size, num_layers, vocab_size, dropout=0.1):
        super().__init__()
        # CNN frontend (1x downsample 4x along time)
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=(11, 41), stride=(2, 2), padding=(5, 20)),
            nn.BatchNorm2d(32),
            nn.GELU(),
            nn.Conv2d(32, 32, kernel_size=(11, 21), stride=(1, 2), padding=(5, 10)),
            nn.BatchNorm2d(32),
            nn.GELU(),
        )
        # After 2 conv strides 2,2: time reduced 4x; freq reduced 4x
        self.cnn_out_freq = ((n_mels + 2*20) // 2 + 0)  # rough
        # Compute exact via dummy
        with torch.no_grad():
            dummy = torch.zeros(1, 1, n_mels, 100)
            out = self.cnn(dummy)
            cnn_feat = out.shape[1] * out.shape[2]  # channels * freq
        self.lstm = nn.LSTM(
            input_size=cnn_feat, hidden_size=hidden_size,
            num_layers=num_layers, bidirectional=True,
            dropout=dropout, batch_first=True
        )
        self.classifier = nn.Linear(hidden_size * 2, vocab_size)
    
    def forward(self, x, x_lens):
        # x: (B, n_mels, T)
        x = x.unsqueeze(1)  # (B, 1, n_mels, T)
        x = self.cnn(x)  # (B, 32, n_mels', T')
        B, C, F_, T = x.shape
        x = x.permute(0, 3, 1, 2).reshape(B, T, C * F_)
        out, _ = self.lstm(x)
        logits = self.classifier(out)  # (B, T, V)
        # Cap new_lens to actual T (CNN with kernel/padding may give T != x_lens/2 exactly)
        new_lens = torch.div(x_lens + 1, 2, rounding_mode="floor").clamp(max=T)
        return logits, new_lens


class ConformerEncoder(nn.Module):
    """Compact Conformer encoder."""
    
    def __init__(self, n_mels, hidden_size, num_layers, vocab_size, dropout=0.1, num_heads=4, conv_kernel=31):
        super().__init__()
        # Subsample 4x
        self.subsample = nn.Sequential(
            nn.Conv2d(1, hidden_size, 3, stride=2, padding=1),
            nn.GELU(),
            nn.Conv2d(hidden_size, hidden_size, 3, stride=2, padding=1),
            nn.GELU(),
        )
        self.input_proj = nn.Linear(hidden_size * (n_mels // 4), hidden_size)
        self.layers = nn.ModuleList([
            ConformerBlock(hidden_size, num_heads, conv_kernel, dropout)
            for _ in range(num_layers)
        ])
        self.classifier = nn.Linear(hidden_size, vocab_size)
    
    def forward(self, x, x_lens):
        x = x.unsqueeze(1)
        x = self.subsample(x)
        B, C, F_, T = x.shape
        x = x.permute(0, 3, 1, 2).reshape(B, T, C * F_)
        x = self.input_proj(x)
        for layer in self.layers:
            x = layer(x)
        logits = self.classifier(x)
        T_actual = logits.shape[1]
        new_lens = torch.div(x_lens + 3, 4, rounding_mode="floor").clamp(max=T_actual)
        return logits, new_lens


class ConformerBlock(nn.Module):
    def __init__(self, dim, heads, conv_kernel, dropout):
        super().__init__()
        self.ff1 = nn.Sequential(
            nn.LayerNorm(dim), nn.Linear(dim, dim * 4), nn.GELU(),
            nn.Dropout(dropout), nn.Linear(dim * 4, dim), nn.Dropout(dropout)
        )
        self.attn_norm = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, heads, dropout=dropout, batch_first=True)
        self.attn_drop = nn.Dropout(dropout)
        self.conv = nn.Sequential(
            nn.LayerNorm(dim),
        )
        self.conv_layer = nn.Sequential(
            nn.Conv1d(dim, dim * 2, 1),
            nn.GLU(dim=1),
            nn.Conv1d(dim, dim, conv_kernel, padding=conv_kernel // 2, groups=dim),
            nn.BatchNorm1d(dim),
            nn.GELU(),
            nn.Conv1d(dim, dim, 1),
            nn.Dropout(dropout),
        )
        self.ff2 = nn.Sequential(
            nn.LayerNorm(dim), nn.Linear(dim, dim * 4), nn.GELU(),
            nn.Dropout(dropout), nn.Linear(dim * 4, dim), nn.Dropout(dropout)
        )
        self.norm = nn.LayerNorm(dim)
    
    def forward(self, x):
        x = x + 0.5 * self.ff1(x)
        h = self.attn_norm(x)
        h, _ = self.attn(h, h, h, need_weights=False)
        x = x + self.attn_drop(h)
        c = self.conv(x).transpose(1, 2)
        c = self.conv_layer(c).transpose(1, 2)
        x = x + c
        x = x + 0.5 * self.ff2(x)
        return self.norm(x)


# ============================================================
# Train loop
# ============================================================
def main():
    args = parse_args()
    # Auto-timestamp if run_dir already has a prior run
    args.run_dir = unique_run_dir(args.run_dir)
    args.run_dir.mkdir(parents=True, exist_ok=True)
    print(f"[from-scratch] resolved run_dir: {args.run_dir}")
    (args.run_dir / "config.json").write_text(
        json.dumps(vars(args), indent=2, default=str), encoding="utf-8")
    
    family = "Conformer-CTC" if args.arch == "conformer" else "Bi-LSTM"
    era = "2020" if args.arch == "conformer" else "2014"
    save_run_meta(
        run_dir=args.run_dir, model_id=f"from-scratch-{args.arch}",
        family=family, era=era, config=vars(args),
        dataset_info={"splits_dir": str(args.data_final),
                      "audio_root": str(args.data_root)},
        notes=f"{family} from-scratch trainer. Replot: python3 -m common.journal_plotting --run-dir <this_dir> --style ieee",
    )
    
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"[from-scratch] arch: {args.arch}, run_dir: {args.run_dir}, device: {device}")
    
    # Load data
    print("[from-scratch] loading splits ...")
    train_rows = load_split_rows(args.data_final / "train.tsv", args.data_root, args.max_train_samples)
    val_rows = load_split_rows(args.data_final / "dev.tsv", args.data_root, args.max_val_samples)
    print(f"  train: {len(train_rows)}, val: {len(val_rows)}")
    
    vocab = build_charvocab(train_rows)
    vocab_path = args.run_dir / "vocab.json"
    vocab_path.write_text(json.dumps(vocab, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[from-scratch] vocab size: {len(vocab)}")
    
    train_ds = CTCDataset(train_rows, vocab, args.n_mels)
    val_ds = CTCDataset(val_rows, vocab, args.n_mels)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              collate_fn=collate_fn, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                            collate_fn=collate_fn, num_workers=0)
    
    # Build model
    if args.arch == "bilstm":
        model = BiLSTMCTC(args.n_mels, args.hidden_size, args.num_layers, len(vocab), args.dropout)
    else:
        model = ConformerEncoder(args.n_mels, args.hidden_size, args.num_layers, len(vocab), args.dropout)
    model = model.to(device)
    
    n_params = sum(p.numel() for p in model.parameters())
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[from-scratch] params: total={n_params:,}, trainable={n_trainable:,}")
    
    # Optimizer + scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-5)
    # OneCycleLR sees fewer steps when grad_accum > 1 (scheduler.step() only after optimizer.step)
    total_steps = args.epochs * (len(train_loader) // args.grad_accum + 1)
    # pct_start=0.3 (default) avoids torch 2.10 zero-division bug for small total_steps
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=args.lr, total_steps=max(total_steps, 4),
        pct_start=0.3, anneal_strategy="cos"
    )
    
    history_saver = HistorySaver(args.run_dir)
    best_tracker = BestCheckpointTracker(args.run_dir, metric_name="wer", lower_is_better=True)
    gpu_monitor = GPUMonitor()
    timer = EpochTimer()
    log_file = args.run_dir / "log.txt"
    
    use_amp = args.fp16 and device == "cuda"
    scaler = torch.amp.GradScaler("cuda") if use_amp else None
    
    # tqdm import (graceful fallback if not available)
    try:
        from tqdm import tqdm
        _has_tqdm = True
    except ImportError:
        _has_tqdm = False
        print("[from-scratch] tqdm not available; running without progress bar")
    
    train_start = time.perf_counter()
    n_train_batches = len(train_loader)
    n_val_batches = len(val_loader)
    print(f"[from-scratch] train batches/epoch: {n_train_batches}, val batches/epoch: {n_val_batches}")
    print(f"[from-scratch] data on /mnt/c (Windows mount); first batch may take ~5–10s for warmup")
    
    for epoch in range(1, args.epochs + 1):
        timer.start_epoch()
        gpu_monitor.reset_peak()
        
        # Train
        model.train()
        train_losses = []
        train_correct, train_total = 0, 0
        train_iter = tqdm(train_loader, desc=f"Epoch {epoch}/{args.epochs} [Train]",
                          leave=False, ncols=100, miniters=10) if _has_tqdm else train_loader
        epoch_start_t = time.perf_counter()
        
        for step, batch in enumerate(train_iter):
            feats = batch["features"].to(device)
            feat_lens = batch["feat_lens"].to(device)
            labels = batch["labels"].to(device)
            label_lens = batch["label_lens"].to(device)
            
            # Zero grads only at start of accumulation cycle
            if step % args.grad_accum == 0:
                optimizer.zero_grad()
            optimizer_step_skipped = False
            do_optimizer_step = ((step + 1) % args.grad_accum == 0) or (step + 1 == n_train_batches)
            
            try:
                if use_amp:
                    with torch.amp.autocast("cuda"):
                        logits, new_lens = model(feats, feat_lens)
                        log_probs = F.log_softmax(logits, dim=-1).transpose(0, 1)
                        loss = F.ctc_loss(log_probs, labels, new_lens, label_lens,
                                          blank=0, zero_infinity=True)
                        loss = loss / args.grad_accum  # scale for accumulation
                    scaler.scale(loss).backward()
                    if do_optimizer_step:
                        scaler.unscale_(optimizer)
                        torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
                        # Track if scaler.step actually performed optimizer.step (it skips on inf/nan)
                        scale_before = scaler.get_scale()
                        scaler.step(optimizer)
                        scaler.update()
                        # If scaler downgraded scale, optimizer.step was SKIPPED
                        optimizer_step_skipped = scaler.get_scale() < scale_before
                else:
                    logits, new_lens = model(feats, feat_lens)
                    log_probs = F.log_softmax(logits, dim=-1).transpose(0, 1)
                    loss = F.ctc_loss(log_probs, labels, new_lens, label_lens,
                                      blank=0, zero_infinity=True)
                    loss = loss / args.grad_accum
                    loss.backward()
                    if do_optimizer_step:
                        torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
                        optimizer.step()
            except torch.cuda.OutOfMemoryError as oom:
                print("\n[OOM] CUDA out of memory at first batch.")
                print("  Suggested fix: reduce --batch-size and use --grad-accum to keep effective batch.")
                print(f"  Current: batch_size={args.batch_size} grad_accum={args.grad_accum}")
                print(f"  Try:     --batch-size {max(1, args.batch_size//2)} --grad-accum {args.grad_accum*2}")
                print(f"  Or:      --batch-size {max(1, args.batch_size//4)} --grad-accum {args.grad_accum*4}")
                print(f"  Also try: PYTORCH_ALLOC_CONF=expandable_segments:True python3 ...")
                raise
            
            # Only step scheduler when optimizer actually stepped
            if do_optimizer_step and not optimizer_step_skipped:
                scheduler.step()
            
            train_losses.append(loss.item() * args.grad_accum)  # un-scale for logging
            
            if _has_tqdm:
                train_iter.set_postfix(loss=f"{loss.item():.3f}",
                                       lr=f"{scheduler.get_last_lr()[0]:.2e}")
            
            # First-batch timing diagnostic (epoch 1 only)
            if step == 0 and epoch == 1:
                first_batch_t = time.perf_counter() - epoch_start_t
                est_epoch_s = first_batch_t * n_train_batches
                print(f"\n[from-scratch] first batch OK in {first_batch_t:.1f}s; "
                      f"estimated epoch time: {est_epoch_s/60:.1f} min "
                      f"({est_epoch_s*args.epochs/3600:.1f} h total for {args.epochs} epochs)\n",
                      flush=True)
            
            # Periodic ETA log every 100 batches if no tqdm
            if (step + 1) % 100 == 0 and not _has_tqdm:
                rate = (step + 1) / (time.perf_counter() - epoch_start_t)
                eta = (n_train_batches - (step + 1)) / max(rate, 1e-6)
                print(f"  [E{epoch} step {step+1}/{n_train_batches}] "
                      f"loss={loss.item():.4f} rate={rate:.2f}/s eta={eta/60:.1f}min", flush=True)
        
        # Val
        model.eval()
        val_losses = []
        all_preds, all_labels = [], []
        val_iter = tqdm(val_loader, desc=f"Epoch {epoch}/{args.epochs} [Val]",
                        leave=False, ncols=100, miniters=10) if _has_tqdm else val_loader
        with torch.no_grad():
            for batch in val_iter:
                feats = batch["features"].to(device)
                feat_lens = batch["feat_lens"].to(device)
                labels = batch["labels"].to(device)
                label_lens = batch["label_lens"].to(device)
                logits, new_lens = model(feats, feat_lens)
                log_probs = F.log_softmax(logits, dim=-1).transpose(0, 1)
                loss = F.ctc_loss(log_probs, labels, new_lens, label_lens,
                                  blank=0, zero_infinity=True)
                val_losses.append(loss.item())
                pred_ids = ctc_decode(logits, blank=0, lengths=new_lens)
                preds = [ids_to_text(p, vocab) for p in pred_ids]
                all_preds.extend(preds)
                all_labels.extend(batch["transcripts"])
        
        # Metrics
        m_val = compute_wer_cer(all_preds, [normalize_text(l) for l in all_labels])
        train_loss = float(np.mean(train_losses)) if train_losses else 0
        val_loss = float(np.mean(val_losses)) if val_losses else 0
        # Train Acc proxy: 1 - (avg train CTC loss normalized via running token-level error from val)
        # For CTC scratch training, true teacher-forcing accuracy is undefined; we use
        # a CER-based proxy on a small training sub-batch.
        train_acc_proxy = None
        try:
            # Quick char-level acc on first 5 train batches' greedy decode vs label text
            train_subset_preds, train_subset_labels = [], []
            model.eval()
            with torch.no_grad():
                for j, batch in enumerate(train_loader):
                    if j >= 3:
                        break
                    feats_t = batch["features"].to(device)
                    feat_lens_t = batch["feat_lens"].to(device)
                    logits_t, new_lens_t = model(feats_t, feat_lens_t)
                    pred_t = ctc_decode(logits_t, blank=0, lengths=new_lens_t)
                    train_subset_preds.extend([ids_to_text(p, vocab) for p in pred_t])
                    train_subset_labels.extend([normalize_text(l) for l in batch["transcripts"]])
            if train_subset_preds:
                m_train_proxy = compute_wer_cer(train_subset_preds, train_subset_labels)
                train_acc_proxy = cer_to_token_acc_proxy(m_train_proxy["cer"])
            model.train()
        except Exception as _e:
            train_acc_proxy = None
        val_acc = cer_to_token_acc_proxy(m_val["cer"])
        
        elapsed = timer.end_epoch()
        gpu_mb = gpu_monitor.peak_mb()
        total = timer.total_elapsed()
        lr = scheduler.get_last_lr()[0]
        
        entry = {
            "train_loss": train_loss, "val_loss": val_loss,
            "train_acc": train_acc_proxy, "val_acc": val_acc,
            "wer": m_val["wer"], "cer": m_val["cer"], "mer": m_val["mer"], "wil": m_val["wil"],
            "time_sec": round(elapsed, 2),
            "time_str": EpochTimer.format_seconds(elapsed),
            "total_elapsed_sec": round(total, 2),
            "total_elapsed_str": EpochTimer.format_seconds(total),
            "gpu_mb": round(gpu_mb, 1),
            "lr": float(lr),
            "throughput_samples_per_sec": round(len(train_ds) / max(elapsed, 1), 2),
        }
        
        sample_preds = list(zip(all_preds[:5], [normalize_text(l) for l in all_labels[:5]]))
        history_saver.append_epoch(epoch, entry, sample_preds)
        
        # Rich-format epoch log (matches Bi-LSTM/T-RCNN style)
        log = format_epoch_log(
            epoch=epoch, total_epochs=args.epochs,
            entry=entry, sample_preds=sample_preds,
            extra_lines=[f"[Train] arch={args.arch} ctc_decode=greedy"],
        )
        print(log, flush=True)
        with log_file.open("a", encoding="utf-8") as f:
            f.write(log + "\n")
        
        try:
            regenerate_plots(history_saver.history_path)
        except Exception as e:
            print(f"plot regen error: {e}")
        
        # Save per-epoch checkpoint (always)
        ckpt_dir = args.run_dir / "checkpoints"
        ckpt_dir.mkdir(exist_ok=True)
        torch.save({
            "epoch": epoch, "model_state": model.state_dict(),
            "optim_state": optimizer.state_dict(), "vocab": vocab, "args": vars(args)
        }, ckpt_dir / f"epoch_{epoch:03d}.pt")
        
        # Save best model if val WER improved
        saved_best = best_tracker.maybe_save(
            value=m_val["wer"], epoch=epoch,
            model_state=model.state_dict(),
            extra_state={"vocab": vocab, "args": vars(args), "val_cer": m_val["cer"]},
        )
        if saved_best:
            print(f"  ★ New best WER={m_val['wer']:.4f} @ epoch {epoch} → {saved_best.name}", flush=True)
    
    train_elapsed = time.perf_counter() - train_start
    best = history_saver.get_best("wer")
    
    report = f"""# Training Report — {args.arch} (from-scratch)

**Run dir**: {args.run_dir}
**Generated**: {datetime.now().isoformat()}

## Config
- Architecture: {args.arch}
- Hidden size: {args.hidden_size}, Layers: {args.num_layers}
- Epochs: {args.epochs}, Batch: {args.batch_size}, LR: {args.lr}
- Train samples: {len(train_ds)}, Val: {len(val_ds)}
- Vocab size: {len(vocab)}

## Model
- Total params: {n_params:,}

## Final
- Total time: {EpochTimer.format_seconds(train_elapsed)}
- Best WER: {best.get('wer', 'n/a') if best else 'n/a'}
- Best CER: {best.get('cer', 'n/a') if best else 'n/a'}
- Best epoch: {best.get('epoch', 'n/a') if best else 'n/a'}
"""
    (args.run_dir / "report.md").write_text(report, encoding="utf-8")
    print(f"[from-scratch] complete. report saved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
