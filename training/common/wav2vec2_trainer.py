"""Unified wav2vec2 / MMS fine-tune trainer (CTC-based).

Works for:
  - facebook/wav2vec2-xls-r-300m
  - cahya/wav2vec2-large-xlsr-indonesian (already FT-ed)
  - facebook/mms-1b-all (with --target-lang ind for adapter mode)

Bypasses datasets.map() — uses custom torch Dataset.

Usage:
    # wav2vec2-XLS-R-300M
    python3 -m training.common.wav2vec2_trainer \\
        --model-id facebook/wav2vec2-xls-r-300m \\
        --run-dir training/m03_wav2vec2_xlsr_300m/runs/run_smoke

    # MMS adapter mode
    python3 -m training.common.wav2vec2_trainer \\
        --model-id facebook/mms-1b-all \\
        --target-lang ind \\
        --adapter-only \\
        --run-dir training/m05_mms_1b_adapter/runs/run_smoke
"""
from __future__ import annotations
import argparse, csv, json, os, re, sys, time, unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
import jiwer
import soundfile as sf
from torch.utils.data import Dataset

TRAINING_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(TRAINING_ROOT))

from common.utils import (
    compute_wer_cer, HistorySaver, regenerate_plots, GPUMonitor, EpochTimer,
    format_epoch_log, cer_to_token_acc_proxy, save_run_meta, unique_run_dir,
    BestCheckpointTracker,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--model-id", default="facebook/wav2vec2-xls-r-300m")
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--data-root", type=Path,
                   default=TRAINING_ROOT.parent / "Processed_Balanced19_v7_natural_synth" / "Dataset_Balanced19")
    p.add_argument("--data-final", type=Path, default=TRAINING_ROOT / "data_final")
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--grad-accum", type=int, default=2)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--warmup-steps", type=int, default=100)
    p.add_argument("--max-train-samples", type=int, default=0)
    p.add_argument("--max-val-samples", type=int, default=0)
    p.add_argument("--target-lang", default=None,
                   help="MMS adapter target language code (e.g., 'ind')")
    p.add_argument("--adapter-only", action="store_true",
                   help="MMS: train only adapter (freeze base)")
    p.add_argument("--gradient-checkpointing", action="store_true", default=False)
    p.add_argument("--fp16", action="store_true", default=True)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


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


def load_audio(path):
    a, sr = sf.read(path, dtype="float32")
    if a.ndim > 1:
        a = a.mean(axis=1).astype(np.float32)
    if sr != 16000:
        raise RuntimeError(f"unexpected sr {sr}")
    return a


def normalize_text(t):
    """Lowercase + strip punctuation, keep alphanum + spaces."""
    t = unicodedata.normalize("NFKC", t).lower()
    t = re.sub(r"[^a-z\s']", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def build_vocab(rows, blank_token="[PAD]", unk_token="[UNK]"):
    """Build char-level vocab from training texts."""
    chars = set()
    for r in rows:
        for c in normalize_text(r["transcript"]):
            chars.add(c)
    vocab = {blank_token: 0, unk_token: 1, "|": 2}  # | = word delimiter
    for c in sorted(chars):
        if c == " ":
            continue
        if c not in vocab:
            vocab[c] = len(vocab)
    return vocab


class CTCDataset(Dataset):
    def __init__(self, rows, processor, max_input_length=480000):  # 30s @ 16kHz
        self.rows = rows
        self.processor = processor
        self.max_input_length = max_input_length
    
    def __len__(self):
        return len(self.rows)
    
    def __getitem__(self, idx):
        r = self.rows[idx]
        audio = load_audio(r["audio_path"])
        if len(audio) > self.max_input_length:
            audio = audio[:self.max_input_length]
        # Feature extractor (no need normalize_text; HF wav2vec2 tokenizer handles)
        norm = normalize_text(r["transcript"])
        inputs = self.processor(audio, sampling_rate=16000, return_tensors="np")
        labels = self.processor.tokenizer(norm, return_tensors="np").input_ids[0]
        return {
            "input_values": inputs.input_values[0],
            "labels": labels.tolist(),
            "transcript": r["transcript"],
        }


def main() -> int:
    args = parse_args()
    # Auto-timestamp if run_dir already contains a previous run
    args.run_dir = unique_run_dir(args.run_dir)
    args.run_dir.mkdir(parents=True, exist_ok=True)
    print(f"[w2v2-trainer] resolved run_dir: {args.run_dir}")
    
    (args.run_dir / "config.json").write_text(
        json.dumps(vars(args), indent=2, default=str), encoding="utf-8")
    
    # Reproducibility meta for future replay/replotting
    family = "MMS" if "mms" in args.model_id.lower() else "wav2vec2"
    era = "2023" if "mms" in args.model_id.lower() else "2021"
    save_run_meta(
        run_dir=args.run_dir, model_id=args.model_id,
        family=family, era=era,
        config=vars(args),
        dataset_info={"splits_dir": str(args.data_final),
                      "audio_root": str(args.data_root),
                      "target_lang": args.target_lang,
                      "adapter_only": args.adapter_only},
        notes=f"{family} CTC FT trainer. Replot: python3 -m common.journal_plotting --run-dir <this_dir> --style ieee",
    )
    
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    
    print(f"[w2v2-trainer] model: {args.model_id}")
    print(f"[w2v2-trainer] run_dir: {args.run_dir}")
    
    from transformers import (
        Wav2Vec2ForCTC, Wav2Vec2Processor, Wav2Vec2CTCTokenizer,
        Wav2Vec2FeatureExtractor, Trainer, TrainingArguments, TrainerCallback
    )
    from dataclasses import dataclass
    
    print("[w2v2-trainer] loading splits ...")
    train_rows = load_split_rows(args.data_final / "train.tsv", args.data_root, args.max_train_samples)
    val_rows = load_split_rows(args.data_final / "dev.tsv", args.data_root, args.max_val_samples)
    print(f"  train: {len(train_rows)}, val: {len(val_rows)}")
    
    # Setup processor: build vocab from training data
    print("[w2v2-trainer] loading processor + model ...")
    
    is_mms = "mms" in args.model_id.lower()
    is_pretrained_id = "cahya" in args.model_id.lower()  # cahya already has tokenizer
    
    if is_mms and args.target_lang:
        processor = Wav2Vec2Processor.from_pretrained(args.model_id, target_lang=args.target_lang)
    elif is_pretrained_id:
        processor = Wav2Vec2Processor.from_pretrained(args.model_id)
    else:
        # Build vocab from train data (XLS-R-300M base)
        vocab = build_vocab(train_rows)
        vocab_path = args.run_dir / "vocab.json"
        vocab_path.write_text(json.dumps(vocab, ensure_ascii=False), encoding="utf-8")
        tokenizer = Wav2Vec2CTCTokenizer(
            str(vocab_path), unk_token="[UNK]", pad_token="[PAD]", word_delimiter_token="|"
        )
        feature_extractor = Wav2Vec2FeatureExtractor(
            feature_size=1, sampling_rate=16000, padding_value=0.0,
            do_normalize=True, return_attention_mask=True
        )
        processor = Wav2Vec2Processor(feature_extractor=feature_extractor, tokenizer=tokenizer)
        processor.save_pretrained(args.run_dir / "processor")
    
    # Load model
    if is_mms and args.target_lang:
        model = Wav2Vec2ForCTC.from_pretrained(
            args.model_id, target_lang=args.target_lang,
            ignore_mismatched_sizes=True
        )
        if args.adapter_only:
            model.init_adapter_layers()
            model.freeze_base_model()
            # Make adapter trainable
            adapter_weights = model._get_adapters()
            for k, v in adapter_weights.items():
                v.requires_grad = True
    elif is_pretrained_id:
        model = Wav2Vec2ForCTC.from_pretrained(args.model_id)
    else:
        model = Wav2Vec2ForCTC.from_pretrained(
            args.model_id,
            ctc_loss_reduction="mean",
            pad_token_id=processor.tokenizer.pad_token_id,
            vocab_size=len(processor.tokenizer),
        )
    
    if args.gradient_checkpointing:
        model.gradient_checkpointing_enable()
    
    n_params = sum(p.numel() for p in model.parameters())
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[w2v2-trainer] params: total={n_params:,}, trainable={n_trainable:,}")
    
    train_ds = CTCDataset(train_rows, processor)
    val_ds = CTCDataset(val_rows, processor)
    
    @dataclass
    class CTCDataCollator:
        processor: object
        def __call__(self, features):
            input_values = [{"input_values": f["input_values"]} for f in features]
            batch = self.processor.feature_extractor.pad(input_values, return_tensors="pt")
            labels = [{"input_ids": f["labels"]} for f in features]
            labels_batch = self.processor.tokenizer.pad(labels, return_tensors="pt")
            labels = labels_batch["input_ids"].masked_fill(
                labels_batch.attention_mask.ne(1), -100)
            batch["labels"] = labels
            return batch
    
    data_collator = CTCDataCollator(processor)
    
    def compute_metrics(eval_pred):
        pred_logits = eval_pred.predictions
        pred_ids = np.argmax(pred_logits, axis=-1)
        label_ids = eval_pred.label_ids
        label_ids[label_ids == -100] = processor.tokenizer.pad_token_id
        pred_str = processor.tokenizer.batch_decode(pred_ids)
        label_str = processor.tokenizer.batch_decode(label_ids, group_tokens=False)
        m = compute_wer_cer(pred_str, label_str)
        val_acc = cer_to_token_acc_proxy(m["cer"])
        return {"wer": m["wer"], "cer": m["cer"], "mer": m["mer"],
                "wil": m["wil"], "val_acc": val_acc}
    
    history_saver = HistorySaver(args.run_dir)
    best_tracker = BestCheckpointTracker(args.run_dir, metric_name="wer", lower_is_better=True)
    gpu_monitor = GPUMonitor()
    timer = EpochTimer()
    log_file = args.run_dir / "log.txt"
    
    class FullLoggerCallback(TrainerCallback):
        def __init__(self):
            self.epoch_train_loss = None
        
        def on_epoch_begin(self, a, s, c, **kwargs):
            timer.start_epoch(); gpu_monitor.reset_peak()
        
        def on_log(self, a, s, c, logs=None, **kwargs):
            if logs and "loss" in logs and "eval_loss" not in logs:
                self.epoch_train_loss = float(logs["loss"])
        
        def on_evaluate(self, a, s, c, metrics=None, **kwargs):
            metrics = metrics or {}
            epoch = int(s.epoch) if s.epoch else 0
            elapsed = timer.end_epoch()
            gpu_mb = gpu_monitor.peak_mb()
            total = timer.total_elapsed()
            lr = s.log_history[-1].get("learning_rate", 0) if s.log_history else 0
            
            entry = {
                "train_loss": self.epoch_train_loss,
                "val_loss": float(metrics.get("eval_loss", 0)),
                "train_acc": None,  # filled below
                "val_acc": float(metrics.get("eval_val_acc", 0)) if "eval_val_acc" in metrics else None,
                "wer": float(metrics.get("eval_wer", 0)) if "eval_wer" in metrics else None,
                "cer": float(metrics.get("eval_cer", 0)) if "eval_cer" in metrics else None,
                "mer": float(metrics.get("eval_mer", 0)) if "eval_mer" in metrics else None,
                "wil": float(metrics.get("eval_wil", 0)) if "eval_wil" in metrics else None,
                "time_sec": round(elapsed, 2),
                "time_str": EpochTimer.format_seconds(elapsed),
                "total_elapsed_sec": round(total, 2),
                "total_elapsed_str": EpochTimer.format_seconds(total),
                "gpu_mb": round(gpu_mb, 1),
                "lr": float(lr),
                "throughput_samples_per_sec": round(len(train_ds) / max(elapsed, 1), 2),
            }
            
            sample_preds = []
            train_subset_preds = []
            train_subset_labels = []
            try:
                model.eval()
                with torch.no_grad():
                    for i in range(min(5, len(val_ds))):
                        item = val_ds[i]
                        iv = torch.tensor(item["input_values"]).unsqueeze(0).to(model.device, dtype=model.dtype)
                        logits = model(iv).logits
                        pred_ids = logits.argmax(dim=-1)
                        pred = processor.tokenizer.batch_decode(pred_ids)[0]
                        sample_preds.append((pred.strip(), item["transcript"]))
                    # Train Acc proxy: greedy decode on small training subset
                    n_train_eval = min(15, len(train_ds))
                    for i in range(n_train_eval):
                        item = train_ds[i]
                        iv = torch.tensor(item["input_values"]).unsqueeze(0).to(model.device, dtype=model.dtype)
                        logits = model(iv).logits
                        pred_ids = logits.argmax(dim=-1)
                        train_subset_preds.append(processor.tokenizer.batch_decode(pred_ids)[0].strip())
                        train_subset_labels.append(item["transcript"])
                model.train()
            except Exception as e:
                print(f"[callback] sample pred error: {e}")
            
            if train_subset_preds:
                m_train = compute_wer_cer(train_subset_preds, train_subset_labels)
                entry["train_acc"] = cer_to_token_acc_proxy(m_train["cer"])
            
            history_saver.append_epoch(epoch, entry, sample_preds)
            
            # Save best model in our consistent naming convention
            if entry["wer"] is not None:
                saved_best = best_tracker.maybe_save(
                    value=entry["wer"], epoch=epoch,
                    model_state=model.state_dict(),
                    extra_state={"args": vars(args), "val_cer": entry["cer"]},
                )
                if saved_best:
                    print(f"  ★ New best WER={entry['wer']:.4f} @ epoch {epoch} → {saved_best.name}",
                          flush=True)
            
            full_log = format_epoch_log(
                epoch=epoch, total_epochs=args.epochs,
                entry=entry, sample_preds=sample_preds,
                extra_lines=[
                    f"[Train] model={args.model_id} accuracy=1-CER (char-level proxy, greedy CTC)",
                ],
            )
            print(full_log, flush=True)
            with log_file.open("a", encoding="utf-8") as f:
                f.write(full_log + "\n")
            
            try:
                regenerate_plots(history_saver.history_path)
            except Exception as e:
                print(f"[callback] plot regen error: {e}")
    
    training_args = TrainingArguments(
        output_dir=str(args.run_dir / "checkpoints"),
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        warmup_steps=args.warmup_steps,
        num_train_epochs=args.epochs,
        gradient_checkpointing=args.gradient_checkpointing,
        fp16=args.fp16 and torch.cuda.is_available(),
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        per_device_eval_batch_size=args.batch_size,
        logging_steps=5,
        report_to=[],
        seed=args.seed,
        dataloader_num_workers=0,
        remove_unused_columns=False,
        metric_for_best_model="wer",
        greater_is_better=False,
        load_best_model_at_end=True,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        processing_class=processor.tokenizer,
        callbacks=[FullLoggerCallback()],
    )
    
    print("[w2v2-trainer] starting training ...")
    train_start = time.perf_counter()
    trainer.train()
    train_elapsed = time.perf_counter() - train_start
    print(f"[w2v2-trainer] complete in {EpochTimer.format_seconds(train_elapsed)}")
    
    best = history_saver.get_best("wer")
    best_wer = best.get('wer', 'n/a') if best else 'n/a'
    best_cer = best.get('cer', 'n/a') if best else 'n/a'
    best_ep = best.get('epoch', 'n/a') if best else 'n/a'
    
    report = f"""# Training Report — {args.model_id}

**Run dir**: {args.run_dir}
**Generated**: {datetime.now().isoformat()}

## Config
- Model: {args.model_id}
- Target lang: {args.target_lang or 'n/a'}
- Adapter only: {args.adapter_only}
- Epochs: {args.epochs}
- Batch size: {args.batch_size} × grad_accum {args.grad_accum}
- Learning rate: {args.lr}
- Train samples: {len(train_ds)}, Val: {len(val_ds)}

## Model
- Total params: {n_params:,}
- Trainable params: {n_trainable:,}

## Final results
- Total time: {EpochTimer.format_seconds(train_elapsed)}
- Best WER: {best_wer}
- Best CER: {best_cer}
- Best epoch: {best_ep}
"""
    (args.run_dir / "report.md").write_text(report, encoding="utf-8")
    print(f"[w2v2-trainer] report saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
