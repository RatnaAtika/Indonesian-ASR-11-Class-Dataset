"""CNN-CTC trainer for Wav2Letter and Jasper architectures (paper baselines).

Reads .pkl features (already log-Mel + SPM-tokenized) from training_conventional/data_pkl/.

Architectures:
  - wav2letter:  10-block 1-D CNN with kernels 7..29 + GLU activations + CTC head (Collobert+ 2016)
  - jasper:      "Jasper-mini" 5-block × 3-sub-block residual 1-D CNN + CTC head (Li+ 2019)

Usage:
    python3 pkl_cnn_ctc_trainer.py --arch wav2letter --run-dir m13_wav2letter_cnn/runs/run_smoke
    python3 pkl_cnn_ctc_trainer.py --arch jasper     --run-dir m14_jasper_cnn/runs/run_smoke
"""
from __future__ import annotations
import argparse, json, pickle, sys, time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import sentencepiece as spm
from torch.utils.data import Dataset, DataLoader

THIS = Path(__file__).parent
sys.path.insert(0, str(THIS.parent))
from common.utils import (compute_wer_cer, HistorySaver, regenerate_plots, GPUMonitor,
                          EpochTimer, format_epoch_log, cer_to_token_acc_proxy,
                          save_run_meta, unique_run_dir, BestCheckpointTracker)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--arch", choices=["wav2letter", "jasper"], required=True)
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--data-pkl-dir", type=Path,
                   default=THIS.parent / "data_pkl")
    p.add_argument("--spm-model", type=Path,
                   default=THIS.parent / "spm" / "spm_v7_char.model")
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--warmup-pct", type=float, default=0.1)
    p.add_argument("--max-train-samples", type=int, default=0)
    p.add_argument("--max-val-samples", type=int, default=0)
    p.add_argument("--input-dim", type=int, default=80)
    p.add_argument("--dropout", type=float, default=0.1)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--fp16", action="store_true", default=True)
    p.add_argument("--grad-clip", type=float, default=5.0)
    return p.parse_args()


# ============================================================
# Dataset
# ============================================================
class PklCTCDataset(Dataset):
    def __init__(self, pkl_path, max_n=0, blank_id=0):
        with open(pkl_path, "rb") as f:
            data = pickle.load(f)
        self.X = data["X"]
        self.y = data["y"]
        self.text = data["text"]
        self.lengths = data["lengths"]
        self.blank_id = blank_id
        if max_n > 0:
            self.X = self.X[:max_n]
            self.y = self.y[:max_n]
            self.text = self.text[:max_n]
            self.lengths = self.lengths[:max_n]
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        x = torch.from_numpy(self.X[idx])  # (T, F)
        # Strip <s> and </s> from y for CTC (CTC doesn't need them)
        y = self.y[idx]
        # Strip BOS=2 and EOS=3
        y_ctc = [t for t in y if t not in (2, 3)]
        return {"feat": x, "labels": torch.tensor(y_ctc, dtype=torch.long), "text": self.text[idx]}


def collate_fn(batch):
    feats = [b["feat"] for b in batch]
    labels = [b["labels"] for b in batch]
    texts = [b["text"] for b in batch]
    feat_lens = torch.tensor([f.shape[0] for f in feats], dtype=torch.long)
    label_lens = torch.tensor([l.shape[0] for l in labels], dtype=torch.long)
    T_max = max(f.shape[0] for f in feats)
    F_dim = feats[0].shape[1]
    feat_pad = torch.zeros(len(feats), T_max, F_dim)
    for i, f in enumerate(feats):
        feat_pad[i, :f.shape[0]] = f
    labels_concat = torch.cat(labels)
    return {
        "features": feat_pad.transpose(1, 2),  # (B, F, T) for CNN
        "feat_lens": feat_lens,
        "labels": labels_concat,
        "label_lens": label_lens,
        "transcripts": texts,
    }


# ============================================================
# Models
# ============================================================
class Wav2Letter(nn.Module):
    """Wav2Letter-style 1-D CNN with CTC.
    
    Reference: Collobert et al. 2016 "Wav2Letter: an End-to-End ConvNet-based Speech
    Recognition System". We use GLU activations as in their paper.
    """
    def __init__(self, input_dim, vocab_size, dropout=0.1):
        super().__init__()
        self.layers = nn.Sequential(
            # Initial frontend: stride 2 conv (downsample 2x)
            nn.Conv1d(input_dim, 250, kernel_size=48, stride=2, padding=23),
            nn.BatchNorm1d(250), nn.GLU(dim=-1) if False else nn.GELU(),
            # 7 dilated/wide conv blocks
            self._block(250, 250, 7, dropout),
            self._block(250, 250, 7, dropout),
            self._block(250, 250, 7, dropout),
            self._block(250, 250, 7, dropout),
            self._block(250, 250, 7, dropout),
            self._block(250, 250, 7, dropout),
            self._block(250, 250, 7, dropout),
            # Wider context block
            nn.Conv1d(250, 2000, kernel_size=32, padding=16),
            nn.BatchNorm1d(2000), nn.GELU(), nn.Dropout(dropout),
            # 1x1 transition
            nn.Conv1d(2000, 2000, kernel_size=1),
            nn.BatchNorm1d(2000), nn.GELU(), nn.Dropout(dropout),
            # Output
            nn.Conv1d(2000, vocab_size, kernel_size=1),
        )
    
    def _block(self, c_in, c_out, k, dropout):
        return nn.Sequential(
            nn.Conv1d(c_in, c_out, kernel_size=k, padding=k // 2),
            nn.BatchNorm1d(c_out), nn.GELU(), nn.Dropout(dropout)
        )
    
    def forward(self, x, x_lens):
        # x: (B, F, T)
        out = self.layers(x)  # (B, V, T')
        T_actual = out.shape[2]
        new_lens = torch.div(x_lens + 1, 2, rounding_mode="floor").clamp(max=T_actual)
        return out.transpose(1, 2), new_lens  # (B, T', V)


class JasperMini(nn.Module):
    """Jasper-mini: 5 blocks × 3 sub-blocks with residual + dense connections + CTC.
    
    Lightweight variant of Jasper-DR-10x4 (Li+ 2019 "Jasper: An End-to-End
    Convolutional Neural Acoustic Model"). Uses residual connections for trainability.
    """
    def __init__(self, input_dim, vocab_size, dropout=0.2):
        super().__init__()
        # Frontend (stride 2)
        self.prologue = nn.Sequential(
            nn.Conv1d(input_dim, 256, kernel_size=11, stride=2, padding=5),
            nn.BatchNorm1d(256), nn.GELU(), nn.Dropout(dropout),
        )
        # 5 blocks with growing kernel sizes
        self.blocks = nn.ModuleList([
            JasperBlock(256, 256, 11, sub_blocks=3, dropout=dropout),
            JasperBlock(256, 384, 13, sub_blocks=3, dropout=dropout),
            JasperBlock(384, 512, 17, sub_blocks=3, dropout=dropout),
            JasperBlock(512, 640, 21, sub_blocks=3, dropout=dropout),
            JasperBlock(640, 768, 25, sub_blocks=3, dropout=dropout),
        ])
        # Epilogue
        self.epilogue = nn.Sequential(
            nn.Conv1d(768, 896, kernel_size=29, padding=14),
            nn.BatchNorm1d(896), nn.GELU(), nn.Dropout(dropout),
            nn.Conv1d(896, 1024, kernel_size=1),
            nn.BatchNorm1d(1024), nn.GELU(), nn.Dropout(dropout),
            nn.Conv1d(1024, vocab_size, kernel_size=1),
        )
    
    def forward(self, x, x_lens):
        out = self.prologue(x)
        for blk in self.blocks:
            out = blk(out)
        out = self.epilogue(out)
        T_actual = out.shape[2]
        new_lens = torch.div(x_lens + 1, 2, rounding_mode="floor").clamp(max=T_actual)
        return out.transpose(1, 2), new_lens


class JasperBlock(nn.Module):
    """Single Jasper block: N sub-blocks with residual."""
    def __init__(self, c_in, c_out, kernel, sub_blocks=3, dropout=0.2):
        super().__init__()
        layers = []
        for i in range(sub_blocks):
            in_c = c_in if i == 0 else c_out
            layers.append(nn.Conv1d(in_c, c_out, kernel, padding=kernel // 2))
            layers.append(nn.BatchNorm1d(c_out))
            if i < sub_blocks - 1:
                layers.append(nn.GELU())
                layers.append(nn.Dropout(dropout))
        self.body = nn.Sequential(*layers)
        # Residual (1x1 if channels differ)
        self.residual = (nn.Identity() if c_in == c_out
                         else nn.Conv1d(c_in, c_out, kernel_size=1))
        self.act = nn.Sequential(nn.GELU(), nn.Dropout(dropout))
    
    def forward(self, x):
        out = self.body(x) + self.residual(x)
        return self.act(out)


# ============================================================
# CTC decode + train loop
# ============================================================
def ctc_greedy_decode(logits, blank=0, lengths=None):
    """Greedy CTC: collapse repeats + remove blanks.

    `logits` is (B, T, V) over the PADDED time axis. When `lengths` (per-sample
    valid output frame counts, e.g. from the model's `new_lens`) is given, each
    sequence is truncated to its own length BEFORE collapsing — otherwise the
    padded tail frames emit spurious tokens, producing over-long hypotheses that
    inflate WER/CER above 1.0 even when the model is correct.
    """
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


def ids_to_text(ids, sp):
    if not ids:
        return ""
    try:
        return sp.decode(ids).strip()
    except Exception:
        return ""


def main():
    args = parse_args()
    # Auto-timestamp if run_dir already has a prior run
    args.run_dir = unique_run_dir(args.run_dir)
    args.run_dir.mkdir(parents=True, exist_ok=True)
    print(f"[cnn-ctc] resolved run_dir: {args.run_dir}")
    (args.run_dir / "config.json").write_text(json.dumps(vars(args), indent=2, default=str), encoding="utf-8")
    
    family = "CNN-CTC"
    era = "2016" if args.arch == "wav2letter" else "2019"
    save_run_meta(
        run_dir=args.run_dir, model_id=f"cnn-ctc-{args.arch}",
        family=family, era=era, config=vars(args),
        dataset_info={"data_pkl_dir": str(args.data_pkl_dir),
                      "spm_model": str(args.spm_model)},
        notes=f"{args.arch} CTC trainer. Replot: python3 -m common.journal_plotting --run-dir <this_dir> --style ieee",
    )
    
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"[cnn-ctc] arch: {args.arch}, run_dir: {args.run_dir}, device: {device}")
    
    # Load SPM
    sp = spm.SentencePieceProcessor(model_file=str(args.spm_model))
    vocab_size = sp.get_piece_size()
    blank_id = 0  # we use <pad> as blank
    print(f"[cnn-ctc] vocab size: {vocab_size}, blank_id: {blank_id}")
    
    # Datasets
    print("[cnn-ctc] loading pickles ...")
    train_ds = PklCTCDataset(args.data_pkl_dir / "train.pkl", args.max_train_samples, blank_id)
    val_ds = PklCTCDataset(args.data_pkl_dir / "valid.pkl", args.max_val_samples, blank_id)
    print(f"  train: {len(train_ds)}, val: {len(val_ds)}")
    
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              collate_fn=collate_fn, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                            collate_fn=collate_fn, num_workers=0)
    
    # Model
    if args.arch == "wav2letter":
        model = Wav2Letter(args.input_dim, vocab_size, args.dropout)
    else:
        model = JasperMini(args.input_dim, vocab_size, args.dropout)
    model = model.to(device)
    
    n_params = sum(p.numel() for p in model.parameters())
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[cnn-ctc] params: total={n_params:,}, trainable={n_trainable:,}")
    
    # Optim + scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-5)
    total_steps = max(1, args.epochs * len(train_loader))
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=args.lr, total_steps=total_steps,
        pct_start=args.warmup_pct, anneal_strategy="cos"
    )
    
    history = HistorySaver(args.run_dir)
    best_tracker = BestCheckpointTracker(args.run_dir, metric_name="wer", lower_is_better=True)
    gpu_mon = GPUMonitor()
    timer = EpochTimer()
    log_file = args.run_dir / "log.txt"
    use_amp = args.fp16 and device == "cuda"
    scaler = torch.amp.GradScaler("cuda") if use_amp else None
    
    try:
        from tqdm import tqdm
        _has_tqdm = True
    except ImportError:
        _has_tqdm = False
        print("[cnn-ctc] tqdm not available; running without progress bar")
    
    train_start = time.perf_counter()
    n_train_batches = len(train_loader)
    n_val_batches = len(val_loader)
    print(f"[cnn-ctc] train batches/epoch: {n_train_batches}, val batches/epoch: {n_val_batches}")
    
    for epoch in range(1, args.epochs + 1):
        timer.start_epoch(); gpu_mon.reset_peak()
        
        # Train
        model.train()
        train_losses = []
        train_iter = tqdm(train_loader, desc=f"Epoch {epoch}/{args.epochs} [Train]",
                          leave=False, ncols=100, miniters=10) if _has_tqdm else train_loader
        epoch_start_t = time.perf_counter()
        
        for step, batch in enumerate(train_iter):
            feats = batch["features"].to(device)
            feat_lens = batch["feat_lens"].to(device)
            labels = batch["labels"].to(device)
            label_lens = batch["label_lens"].to(device)
            
            optimizer.zero_grad()
            optimizer_step_skipped = False
            if use_amp:
                with torch.amp.autocast("cuda"):
                    logits, new_lens = model(feats, feat_lens)
                    log_probs = F.log_softmax(logits, dim=-1).transpose(0, 1)  # (T, B, V)
                    loss = F.ctc_loss(log_probs, labels, new_lens, label_lens,
                                      blank=blank_id, zero_infinity=True)
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
                scale_before = scaler.get_scale()
                scaler.step(optimizer); scaler.update()
                optimizer_step_skipped = scaler.get_scale() < scale_before
            else:
                logits, new_lens = model(feats, feat_lens)
                log_probs = F.log_softmax(logits, dim=-1).transpose(0, 1)
                loss = F.ctc_loss(log_probs, labels, new_lens, label_lens,
                                  blank=blank_id, zero_infinity=True)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
                optimizer.step()
            
            if not optimizer_step_skipped:
                scheduler.step()
            train_losses.append(float(loss.item()))
            
            if _has_tqdm:
                train_iter.set_postfix(loss=f"{loss.item():.3f}",
                                       lr=f"{scheduler.get_last_lr()[0]:.2e}")
            
            if step == 0 and epoch == 1:
                first_batch_t = time.perf_counter() - epoch_start_t
                est_epoch_s = first_batch_t * n_train_batches
                print(f"\n[cnn-ctc] first batch OK in {first_batch_t:.1f}s; "
                      f"estimated epoch time: {est_epoch_s/60:.1f} min "
                      f"({est_epoch_s*args.epochs/3600:.1f} h total for {args.epochs} epochs)\n",
                      flush=True)
            
            if (step + 1) % 100 == 0 and not _has_tqdm:
                rate = (step + 1) / (time.perf_counter() - epoch_start_t)
                eta = (n_train_batches - (step + 1)) / max(rate, 1e-6)
                print(f"  [E{epoch} step {step+1}/{n_train_batches}] "
                      f"loss={loss.item():.4f} rate={rate:.2f}/s eta={eta/60:.1f}min", flush=True)
        
        # Eval
        model.eval()
        val_losses, all_preds, all_labels = [], [], []
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
                                  blank=blank_id, zero_infinity=True)
                val_losses.append(float(loss.item()))
                pred_ids = ctc_greedy_decode(logits, blank=blank_id, lengths=new_lens)
                preds = [ids_to_text(p, sp) for p in pred_ids]
                all_preds.extend(preds)
                all_labels.extend(batch["transcripts"])
        
        m = compute_wer_cer(all_preds, all_labels)
        train_loss = float(np.mean(train_losses)) if train_losses else 0
        val_loss = float(np.mean(val_losses)) if val_losses else 0
        
        # Train Acc proxy: 1 - CER computed on a few train batches via greedy decode
        train_acc_proxy = None
        try:
            t_preds, t_labels = [], []
            model.eval()
            with torch.no_grad():
                for j, batch in enumerate(train_loader):
                    if j >= 3: break
                    feats_t = batch["features"].to(device)
                    feat_lens_t = batch["feat_lens"].to(device)
                    logits_t, new_lens_t = model(feats_t, feat_lens_t)
                    pred_t = ctc_greedy_decode(logits_t, blank=blank_id, lengths=new_lens_t)
                    t_preds.extend([ids_to_text(p, sp) for p in pred_t])
                    t_labels.extend(batch["transcripts"])
            if t_preds:
                m_t = compute_wer_cer(t_preds, t_labels)
                train_acc_proxy = cer_to_token_acc_proxy(m_t["cer"])
            model.train()
        except Exception:
            pass
        val_acc = cer_to_token_acc_proxy(m["cer"])
        
        elapsed = timer.end_epoch()
        gpu_mb = gpu_mon.peak_mb()
        total = timer.total_elapsed()
        lr_now = scheduler.get_last_lr()[0]
        
        entry = {
            "train_loss": train_loss, "val_loss": val_loss,
            "train_acc": train_acc_proxy, "val_acc": val_acc,
            "wer": m["wer"], "cer": m["cer"], "mer": m["mer"], "wil": m["wil"],
            "time_sec": round(elapsed, 2),
            "time_str": EpochTimer.format_seconds(elapsed),
            "total_elapsed_sec": round(total, 2),
            "total_elapsed_str": EpochTimer.format_seconds(total),
            "gpu_mb": round(gpu_mb, 1),
            "lr": float(lr_now),
            "throughput_samples_per_sec": round(len(train_ds) / max(elapsed, 1), 2),
        }
        sample_preds = list(zip(all_preds[:5], all_labels[:5]))
        history.append_epoch(epoch, entry, sample_preds)
        
        log = format_epoch_log(
            epoch=epoch, total_epochs=args.epochs,
            entry=entry, sample_preds=sample_preds,
            extra_lines=[f"[Train] arch={args.arch} ctc_decode=greedy blank_id={blank_id}"],
        )
        print(log, flush=True)
        with log_file.open("a", encoding="utf-8") as f:
            f.write(log + "\n")
        
        try:
            regenerate_plots(history.history_path)
        except Exception as e:
            print(f"plot regen warn: {e}")
        
        # Save per-epoch checkpoint (always)
        ckpt_dir = args.run_dir / "checkpoints"
        ckpt_dir.mkdir(exist_ok=True)
        torch.save({
            "epoch": epoch, "arch": args.arch,
            "model_state": model.state_dict(),
            "optim_state": optimizer.state_dict(),
            "args": vars(args),
            "vocab_size": vocab_size,
        }, ckpt_dir / f"epoch_{epoch:03d}.pt")
        
        # Save best model if val WER improved
        saved_best = best_tracker.maybe_save(
            value=m["wer"], epoch=epoch,
            model_state=model.state_dict(),
            extra_state={"arch": args.arch, "args": vars(args),
                         "vocab_size": vocab_size, "val_cer": m["cer"]},
        )
        if saved_best:
            print(f"  ★ New best WER={m['wer']:.4f} @ epoch {epoch} → {saved_best.name}", flush=True)
    
    train_elapsed = time.perf_counter() - train_start
    best = history.get_best("wer")
    
    report = f"""# Training Report — {args.arch} (CNN-CTC)

**Run dir**: {args.run_dir}
**Generated**: {datetime.now().isoformat()}

## Config
- Architecture: {args.arch}
- Epochs: {args.epochs}, Batch: {args.batch_size}, LR: {args.lr}
- Train samples: {len(train_ds)}, Val: {len(val_ds)}
- Vocab size: {vocab_size}

## Model
- Total params: {n_params:,}
- Trainable params: {n_trainable:,}

## Final
- Total time: {EpochTimer.format_seconds(train_elapsed)}
- Best WER: {best.get('wer', 'n/a') if best else 'n/a'}
- Best CER: {best.get('cer', 'n/a') if best else 'n/a'}
- Best epoch: {best.get('epoch', 'n/a') if best else 'n/a'}
"""
    (args.run_dir / "report.md").write_text(report, encoding="utf-8")
    print(f"[cnn-ctc] complete. report saved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
