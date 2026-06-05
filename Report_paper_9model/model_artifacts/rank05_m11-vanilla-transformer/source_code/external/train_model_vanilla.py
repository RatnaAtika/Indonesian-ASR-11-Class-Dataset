import os
import pickle
import torch
from torch.utils.data import Dataset, DataLoader
import random

def collate_fn_pad(batch):
    """
    batch: list of tuple (x, y)
    x: [time, feat], y: [seq]
    """
    xs, ys = zip(*batch)
    xs = torch.stack(xs, dim=0)
    # Padding label sequences
    max_len = max([len(y) for y in ys])
    ys_pad = torch.zeros((len(ys), max_len), dtype=torch.long)
    for i, y in enumerate(ys):
        ys_pad[i, :len(y)] = y
    return xs, ys_pad

def seed_everything(seed: int, deterministic: bool = False) -> None:
    import numpy as np
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
import sentencepiece as spm
from transformer_model_vanilla import TransformerASR
from tqdm import tqdm
import time
import argparse
from typing import List, Tuple


# ========== HYPERPARAMETERS ==========
EPOCHS = 80
BATCH_SIZE = 16
LEARNING_RATE = 5e-4
VALID_RATIO = 0.0
D_MODEL = 192
NHEAD = 4
NUM_LAYERS = 2
DIM_FEEDFORWARD = 256
DROPOUT = 0.1
INPUT_DIM = 80
# =====================================

class ASRDataset(Dataset):
    def __init__(self, data):
        self.X = data['X']
        self.y = data['y']

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        x = torch.tensor(self.X[idx], dtype=torch.float32)
        y = torch.tensor(self.y[idx], dtype=torch.long)  # Sudah subword id
        return x, y

def _prepare_targets(ys: List[torch.Tensor], pad_id: int, bos_id: int, eos_id: int) -> Tuple[torch.Tensor, torch.Tensor]:
    proc: List[torch.Tensor] = []
    max_len = 0
    for y in ys:
        seq = y.tolist()
        if len(seq) == 0:
            seq = [eos_id]
        # remove leading BOS if present
        if seq[0] == bos_id:
            seq = seq[1:]
        # ensure EOS at end
        if seq[-1] != eos_id:
            seq = seq + [eos_id]
        t = torch.tensor(seq, dtype=torch.long)
        proc.append(t)
        max_len = max(max_len, len(seq))
    ys_in = torch.full((len(proc), max_len), pad_id, dtype=torch.long)
    ys_out = torch.full((len(proc), max_len), pad_id, dtype=torch.long)
    for i, t in enumerate(proc):
        L = t.size(0)
        ys_in[i, 0] = bos_id
        if L > 1:
            ys_in[i, 1:L] = t[:-1]
        ys_out[i, :L] = t
    return ys_in, ys_out

def collate_fn_seq2seq(batch, pad_id=0, bos_id=2, eos_id=3):
    # Pad variable-length acoustic features and build masks
    xs, ys = zip(*batch)
    xs_list = [x for x in xs]  # each [T, F]
    lengths = torch.tensor([t.size(0) for t in xs_list], dtype=torch.long)
    T_max = int(lengths.max())
    F = xs_list[0].size(1)
    xs_pad = torch.zeros((len(xs_list), T_max, F), dtype=torch.float32)
    for i, x in enumerate(xs_list):
        xs_pad[i, :x.size(0)] = x
    src_key_padding_mask = torch.ones((len(xs_list), T_max), dtype=torch.bool)
    for i, L in enumerate(lengths.tolist()):
        src_key_padding_mask[i, :L] = False
    ys_in, ys_out = _prepare_targets(list(ys), pad_id, bos_id, eos_id)
    return xs_pad, src_key_padding_mask, ys_in, ys_out

# --- Masking util ---
def create_tgt_mask(sz):
    # Generate a causal mask for decoder (no peek ahead)
    mask = torch.triu(torch.ones(sz, sz), diagonal=1).bool()
    return mask


def collate_fn(batch):
    xs, ys = zip(*batch)
    xs = torch.stack(xs)
    ys = [y for y in ys]
    return xs, ys

from torch.utils.data import random_split
import numpy as np

def cer(pred, target):
    # Character Error Rate sederhana
    import editdistance
    return editdistance.eval(pred, target) / max(1, len(target))

def wer(pred, target):
    # Word Error Rate sederhana (token = whitespace-split word)
    import editdistance
    pred_words = pred.split()
    target_words = target.split()
    return editdistance.eval(pred_words, target_words) / max(1, len(target_words))

def decode_ctc_subword(log_probs, sp):
    # Greedy decoding CTC untuk subword (SentencePiece)
    pred = log_probs.argmax(-1).cpu().numpy()
    results = []
    for seq in pred:
        prev = -1
        tokens = []
        for i in seq:
            if i != prev and i != 0:
                tokens.append(int(i))
            prev = i
        # Perbaikan: pastikan tokens adalah list of int dan tidak kosong
        if len(tokens) == 0:
            results.append("")
        else:
            results.append(sp.decode(tokens))
    return results

def train():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    # CLI args
    parser = argparse.ArgumentParser()
    parser.add_argument('--train-pkl', default='features/train.pkl')
    parser.add_argument('--val-pkl', default='features/valid.pkl')
    parser.add_argument('--test-pkl', default='features/test.pkl')
    parser.add_argument('--spm-model', default='spm/spm_char_fixed.model')
    parser.add_argument('--outdir', default='runs/vanilla', help='Output directory for plots and last checkpoint')
    parser.add_argument('--epochs', type=int, default=EPOCHS)
    parser.add_argument('--batch-size', type=int, default=BATCH_SIZE)
    parser.add_argument('--lr', type=float, default=LEARNING_RATE)
    parser.add_argument('--d-model', type=int, default=D_MODEL)
    parser.add_argument('--nhead', type=int, default=NHEAD)
    parser.add_argument('--num-layers', type=int, default=NUM_LAYERS)
    parser.add_argument('--ff', type=int, default=DIM_FEEDFORWARD)
    parser.add_argument('--dropout', type=float, default=DROPOUT)
    parser.add_argument('--input-dim', type=int, default=INPUT_DIM)
    parser.add_argument('--specaug', action='store_true')
    parser.add_argument('--amp', action='store_true')
    parser.add_argument('--patience', type=int, default=12)
    parser.add_argument('--checkpoint', default='checkpoints/best-transformer-asr.pth')
    parser.add_argument('--seed', type=int, default=1337, help='random seed for reproducibility')
    parser.add_argument('--deterministic', action='store_true', help='use deterministic cudnn (slower)')
    args = parser.parse_args()

    seed_everything(args.seed, deterministic=args.deterministic)
    print(f"[Seed] seed={args.seed} deterministic={args.deterministic}")

    os.makedirs(args.outdir, exist_ok=True)

    print("[Config] train_model_vanilla")
    print(f"[Config] train_pkl={args.train_pkl}")
    print(f"[Config] val_pkl={args.val_pkl}")
    print(f"[Config] spm_model={args.spm_model}")
    print(f"[Config] outdir={args.outdir}")
    print(f"[Config] checkpoint={args.checkpoint}")
    print(f"[Config] epochs={args.epochs} batch_size={args.batch_size} lr={args.lr}")
    print(f"[Config] d_model={args.d_model} nhead={args.nhead} num_layers={args.num_layers} ff={args.ff} dropout={args.dropout}")
    print(f"[Config] amp={args.amp} specaug={args.specaug}")

    # Load SentencePiece
    sp = spm.SentencePieceProcessor(model_file=args.spm_model)
    print('Mapping token id:')
    print(f'PAD (0): {sp.id_to_piece(0)}')
    print(f'UNK (1): {sp.id_to_piece(1)}')
    print(f'BOS (2): {sp.id_to_piece(2)}')
    print(f'EOS (3): {sp.id_to_piece(3)}')
    # Load dataset pickle hasil preprocessing subword
    with open(args.train_pkl, 'rb') as f:
        train_data = pickle.load(f)
    with open(args.val_pkl, 'rb') as f:
        val_data = pickle.load(f)
    # test set optional
    train_set = ASRDataset(train_data)
    val_set = ASRDataset(val_data)
    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True, collate_fn=lambda b: collate_fn_seq2seq(b, pad_id=0, bos_id=2, eos_id=3))
    val_loader = DataLoader(val_set, batch_size=args.batch_size, shuffle=False, collate_fn=lambda b: collate_fn_seq2seq(b, pad_id=0, bos_id=2, eos_id=3))
    model = TransformerASR(
        input_dim=args.input_dim,
        sp_model_path=args.spm_model,
        d_model=args.d_model,
        nhead=args.nhead,
        num_encoder_layers=args.num_layers,
        num_decoder_layers=args.num_layers,
        dim_feedforward=args.ff,
        dropout=args.dropout
    ).to(device)
    # Set bias output layer ke nol (antisuppress token collapse)
    if hasattr(model, 'classifier') and hasattr(model.classifier, 'bias'):
        nn.init.zeros_(model.classifier.bias)
    elif hasattr(model, 'output_layer') and hasattr(model.output_layer, 'bias'):
        nn.init.zeros_(model.output_layer.bias)
    else:
        print('WARNING: Tidak ditemukan classifier/output_layer.bias, pastikan output layer model Anda bernama "classifier" atau "output_layer".')
    # Print model summary
    try:
        from torchinfo import summary
        # Buat data dummy dengan masking yang sesuai
        dummy_src = torch.randn(args.batch_size, 100, args.input_dim).to(next(model.parameters()).device)
        dummy_tgt = torch.ones(args.batch_size, 50, dtype=torch.long).to(next(model.parameters()).device)
        # Gunakan input_data=(src, tgt) sesuai signature vanilla TransformerASR
        import traceback
        try:
            model_summary = summary(
                model,
                input_data=(dummy_src, dummy_tgt),
                depth=3,
                col_names=["input_size", "output_size", "num_params"]
            )
            print(model_summary)
            # Simpan ke PNG/PDF seperti sebelumnya
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.axis('off')
            ax.text(0, 1, str(model_summary), fontsize=8, family='monospace', verticalalignment='top')
            plt.savefig(os.path.join(args.outdir, 'model_summary.png'), bbox_inches='tight')
            plt.savefig(os.path.join(args.outdir, 'model_summary.pdf'), bbox_inches='tight')
            plt.close(fig)
        except Exception as e:
            print(f"[ERROR] torchinfo.summary gagal: {e}")
            traceback.print_exc()
            print("Summary gagal. Pastikan shape input dummy sesuai dan model mendukung summary.")
    except Exception as e:
        print(f"Summary gagal: {e}. Install torchinfo dan pastikan model support summary dengan input_data. Jika model seq2seq, gunakan input_data=(src, tgt, ...) sesuai signature model.")
    # Print jumlah parameter
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total Parameters: {total_params:,}")
    # Best practice: AdamW, label smoothing, grad clipping, scheduler
    criterion = nn.CrossEntropyLoss(ignore_index=0, label_smoothing=0.0)
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-2)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5, min_lr=1e-5)
    scaler = torch.cuda.amp.GradScaler(enabled=args.amp)
    train_losses, val_losses, train_accuracies, val_accuracies = [], [], [], []
    train_cers, val_cers = [], []
    train_wers, val_wers = [], []
    best_val_loss = float('inf')
    patience = args.patience
    patience_counter = 0
    start_time = time.time()
    for epoch in range(1, args.epochs+1):
        print(f"Epoch {epoch} | Current LR: {optimizer.param_groups[0]['lr']:.6f}")
        # --- Training ---
        model.train()
        total_train_loss = 0
        train_iter = tqdm(train_loader, desc=f"Epoch {epoch}/{args.epochs} [Train]", leave=False)
        total_train_cer = 0
        total_train_wer = 0
        n_train_items = 0
        for batch_idx, (x, src_key_padding_mask, y_in, y_out) in enumerate(train_iter):
            x = x.to(device)
            src_key_padding_mask = src_key_padding_mask.to(device)
            y_in = y_in.to(device)
            y_out = y_out.to(device)
            tgt_mask = create_tgt_mask(y_in.size(1)).to(device)
            tgt_key_padding_mask = (y_in == 0)
            optimizer.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=args.amp):
                logits = model(x, y_in, src_key_padding_mask=src_key_padding_mask, tgt_mask=tgt_mask, tgt_key_padding_mask=tgt_key_padding_mask)
                loss = criterion(logits.view(-1, logits.size(-1)), y_out.view(-1))
            scaler.scale(loss).backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            total_train_loss += loss.item()
            # Greedy decoding & CER training
            pred_tokens = logits.argmax(-1).detach().cpu().numpy()
            y_out_cpu = y_out.detach().cpu().numpy()
            for i in range(pred_tokens.shape[0]):
                # Greedy decoding: stop at <eos> (id=3), ignore pad (0)
                pred_seq = []
                for idx in pred_tokens[i]:
                    if idx == 0:  # pad
                        continue
                    if idx == 3:  # <eos>
                        break
                    pred_seq.append(int(idx))
                pred_str = sp.decode(pred_seq)
                target_seq = [int(idx) for idx in y_out_cpu[i] if idx != 0 and idx != 3]
                target_str = sp.decode(target_seq)
                total_train_cer += cer(pred_str, target_str)
                total_train_wer += wer(pred_str, target_str)
                n_train_items += 1
            train_iter.set_postfix(loss=loss.item())
        avg_train_loss = total_train_loss / max(1, len(train_loader))
        avg_train_cer = total_train_cer / n_train_items if n_train_items > 0 else 1.0
        avg_train_wer = total_train_wer / n_train_items if n_train_items > 0 else 1.0
        train_char_acc = max(0.0, 1.0 - avg_train_cer)
        train_losses.append(avg_train_loss)
        train_accuracies.append(train_char_acc)
        train_cers.append(avg_train_cer)
        train_wers.append(avg_train_wer)
        # --- Validation ---
        model.eval()
        total_val_loss = 0
        total_val_cer = 0
        total_val_wer = 0
        n_val_items = 0
        val_iter = tqdm(val_loader, desc=f"Epoch {epoch}/{args.epochs} [Val]", leave=False)
        val_pred_tokens = []
        val_label_tokens = []
        val_pred_strs = []
        val_label_strs = []
        with torch.no_grad():
            for x, src_key_padding_mask, y_in, y_out in val_iter:
                x = x.to(device)
                src_key_padding_mask = src_key_padding_mask.to(device)
                y_in = y_in.to(device)
                y_out = y_out.to(device)
                tgt_mask = create_tgt_mask(y_in.size(1)).to(device)
                tgt_key_padding_mask = (y_in == 0)
                logits = model(x, y_in, src_key_padding_mask=src_key_padding_mask, tgt_mask=tgt_mask, tgt_key_padding_mask=tgt_key_padding_mask)
                val_loss = criterion(logits.view(-1, logits.size(-1)), y_out.view(-1))
                total_val_loss += val_loss.item()
                # Greedy decoding & CER validasi
                pred_tokens = logits.argmax(-1).detach().cpu().numpy()
                y_out_cpu = y_out.detach().cpu().numpy()
                for i in range(pred_tokens.shape[0]):
                    # Greedy decoding: stop at <eos> (id=3), ignore pad (0)
                    pred_seq = []
                    for idx in pred_tokens[i]:
                        if idx == 0:  # pad
                            continue
                        if idx == 3:  # <eos>
                            break
                        pred_seq.append(int(idx))
                    pred_str = sp.decode(pred_seq)
                    target_seq = [int(idx) for idx in y_out_cpu[i] if idx != 0 and idx != 3]
                    target_str = sp.decode(target_seq)
                    total_val_cer += cer(pred_str, target_str)
                    total_val_wer += wer(pred_str, target_str)
                    n_val_items += 1
                    val_pred_tokens.append(pred_tokens[i])
                    val_label_tokens.append(y_out_cpu[i])
                    val_pred_strs.append(pred_str)
                    val_label_strs.append(target_str)
                val_iter.set_postfix(loss=val_loss.item())
        avg_val_loss = total_val_loss / max(1, len(val_loader))
        avg_val_cer = total_val_cer / n_val_items if n_val_items > 0 else 1.0
        avg_val_wer = total_val_wer / n_val_items if n_val_items > 0 else 1.0
        val_char_acc = max(0.0, 1.0 - avg_val_cer)
        val_losses.append(avg_val_loss)
        val_accuracies.append(val_char_acc)
        val_cers.append(avg_val_cer)
        val_wers.append(avg_val_wer)
        old_lr = optimizer.param_groups[0]['lr']
        scheduler.step(avg_val_loss)
        new_lr = optimizer.param_groups[0]['lr']
        if new_lr != old_lr:
            print(f"[Scheduler] Learning rate changed: {old_lr} -> {new_lr}")
        print(f"Epoch {epoch}: Train Loss={avg_train_loss:.4f} | Val Loss={avg_val_loss:.4f} | Train Acc={train_char_acc:.4f} | Val Acc={val_char_acc:.4f} | Val WER={avg_val_wer:.4f} | Val CER={avg_val_cer:.4f}")
        # Save best
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            patience_counter = 0
            os.makedirs(os.path.dirname(args.checkpoint), exist_ok=True)
            torch.save({'model': model.state_dict(), 'args': vars(args)}, args.checkpoint)
            print(f"[Checkpoint] Saved best model to {args.checkpoint}")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch} (no improvement for {patience} epochs)")
                break
        # Tampilkan contoh prediksi vs label string (maks 5 sample)
        print("=== Contoh prediksi vs label (val) ===")
        for pred, label in zip(val_pred_strs[:5], val_label_strs[:5]):
            print(f"PRED: {pred}\nLABEL: {label}\n")
    torch.save(model.state_dict(), os.path.join(args.outdir, 'transformer_asr_last.pth'))
    end_time = time.time()
    total_sec = int(end_time - start_time)
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    seconds = total_sec % 60
    print(f"Total waktu training: {hours} jam, {minutes} menit, {seconds} detik")
    plt.figure(figsize=(10,5))
    plt.plot(train_losses, label='Train Loss')
    plt.plot(val_losses, label='Val Loss')
    plt.legend()
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training & Validation Loss')
    plt.savefig(os.path.join(args.outdir, 'training_val_loss.png'))

    plt.figure(figsize=(10,5))
    plt.plot(train_accuracies, label='Train Char Accuracy')
    plt.plot(val_accuracies, label='Val Char Accuracy')
    plt.legend()
    plt.xlabel('Epoch')
    plt.ylabel('Char Accuracy')
    plt.title('Training & Validation Char Accuracy')
    plt.savefig(os.path.join(args.outdir, 'training_val_accuracy.png'))
    plt.ylabel('Char Accuracy')
    plt.title('Training & Validation Character Accuracy')
    plt.savefig(os.path.join(args.outdir, 'char_accuracy.png'))

    plt.figure(figsize=(10,5))
    plt.plot(train_cers, label='Train CER')
    plt.plot(val_cers, label='Val CER')
    plt.plot(train_wers, label='Train WER', linestyle='--')
    plt.plot(val_wers, label='Val WER', linestyle='--')
    plt.legend()
    plt.xlabel('Epoch')
    plt.ylabel('CER')
    plt.title('Training & Validation CER')
    plt.savefig(os.path.join(args.outdir, 'cer.png'))

if __name__ == '__main__':
    train()
