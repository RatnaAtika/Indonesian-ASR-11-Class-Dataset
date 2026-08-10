"""Unified Whisper fine-tune trainer (v2 — no datasets.map()).

CRITICAL FIX from v1: avoid datasets.map() which hangs on /mnt/c WSL2 Windows mount.
Use plain torch.utils.data.Dataset that loads audio + tokenizes on-the-fly.

Usage:
    python3 -m training.common.whisper_trainer \\
        --model-id openai/whisper-tiny \\
        --run-dir training/m01_whisper_tiny/runs/run_smoke_2ep \\
        --epochs 2 --max-train-samples 200 --max-val-samples 50
"""
from __future__ import annotations
import argparse, csv, json, os, sys, time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import torch
import jiwer
import soundfile as sf
from torch.utils.data import Dataset

# Ensure training package importable
TRAINING_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(TRAINING_ROOT))

from common.split_compat import resolve_validation_tsv
from common.utils import (
    compute_wer_cer, HistorySaver, regenerate_plots, GPUMonitor, EpochTimer,
    format_epoch_log, cer_to_token_acc_proxy, save_run_meta, unique_run_dir,
    BestCheckpointTracker, save_model_summary,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--model-id", default="openai/whisper-tiny")
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--data-root", type=Path,
                   default=TRAINING_ROOT.parent / "Processed_Balanced19_v7_natural_synth" / "Dataset_Balanced19")
    p.add_argument("--data-final", type=Path, default=TRAINING_ROOT / "data_final")
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--grad-accum", type=int, default=2)
    p.add_argument("--lr", type=float, default=1e-5)
    p.add_argument("--warmup-steps", type=int, default=100)
    p.add_argument("--max-train-samples", type=int, default=0)
    p.add_argument("--max-val-samples", type=int, default=0)
    p.add_argument("--language", default="indonesian")
    p.add_argument("--task", default="transcribe")
    p.add_argument("--gradient-checkpointing", action="store_true", default=False)
    p.add_argument("--num-workers", type=int, default=0,
                   help="DataLoader workers. Use 2-4 on Colab/local SSD to keep A100 fed; keep 0 for maximum compatibility.")
    p.add_argument("--disable-tqdm", action="store_true", default=False,
                   help="Disable tqdm/progress bars to keep Colab browser UI responsive; logs still go to file/report.")
    p.add_argument("--fp16", action="store_true", default=True)
    p.add_argument("--resume", nargs="?", const="auto", default=None,
                   help="Resume training: pass a checkpoint dir, or bare --resume to "
                        "auto-pick the latest checkpoint-* in run_dir/checkpoints.")
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def load_split_rows(tsv_path: Path, dataset_root: Path, max_samples: int = 0) -> List[Dict]:
    """Load split TSV into a list of dicts (no HF Dataset). Lightweight."""
    rows = []
    with tsv_path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            audio_path = dataset_root / r["audio_path"]
            if not audio_path.exists():
                continue
            rows.append({
                "audio_path": str(audio_path),
                "transcript": r["transcript"].strip(),
            })
            if max_samples > 0 and len(rows) >= max_samples:
                break
    return rows


def load_audio(path: str) -> np.ndarray:
    audio, sr = sf.read(path, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1).astype(np.float32)
    if sr != 16000:
        raise RuntimeError(f"unexpected sr {sr} for {path}")
    return audio


class WhisperASRDataset(Dataset):
    """torch Dataset that loads audio + tokenizes on-the-fly. NO HF map() / Arrow."""
    
    def __init__(self, rows: List[Dict], processor, max_label_length: int = 448):
        self.rows = rows
        self.processor = processor
        self.max_label_length = max_label_length
    
    def __len__(self):
        return len(self.rows)
    
    def __getitem__(self, idx):
        r = self.rows[idx]
        audio = load_audio(r["audio_path"])
        # Feature extractor
        feat = self.processor.feature_extractor(
            audio, sampling_rate=16000, return_tensors="np"
        ).input_features[0]
        # Tokenize labels
        labels = self.processor.tokenizer(r["transcript"], return_tensors="np").input_ids[0]
        if len(labels) > self.max_label_length:
            labels = labels[:self.max_label_length]
        return {
            "input_features": feat,
            "labels": labels.tolist(),
            "transcript": r["transcript"],
        }


def main() -> int:
    args = parse_args()
    # When resuming, keep the SAME run_dir (don't auto-timestamp a fresh one).
    if args.resume is None:
        args.run_dir = unique_run_dir(args.run_dir)
    args.run_dir.mkdir(parents=True, exist_ok=True)
    print(f"[whisper-trainer] resolved run_dir: {args.run_dir}")
    
    # Save config + reproducibility meta (for future replay/replotting)
    (args.run_dir / "config.json").write_text(
        json.dumps(vars(args), indent=2, default=str), encoding="utf-8"
    )
    save_run_meta(
        run_dir=args.run_dir, model_id=args.model_id,
        family="Whisper", era="2022",
        config=vars(args),
        dataset_info={"splits_dir": str(args.data_final),
                      "audio_root": str(args.data_root),
                      "language": args.language, "task": args.task},
        notes="Whisper FT trainer. Replot with: python3 -m common.journal_plotting --run-dir <this_dir> --style ieee",
    )
    
    # Set seeds
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    
    print(f"[whisper-trainer] model: {args.model_id}")
    print(f"[whisper-trainer] run_dir: {args.run_dir}")
    print(f"[whisper-trainer] epochs: {args.epochs}, batch_size: {args.batch_size}")
    
    from transformers import (
        WhisperForConditionalGeneration, WhisperProcessor,
        Seq2SeqTrainer, Seq2SeqTrainingArguments, TrainerCallback
    )
    from dataclasses import dataclass
    
    print("[whisper-trainer] loading processor + model ...")
    processor = WhisperProcessor.from_pretrained(args.model_id)
    processor.tokenizer.set_prefix_tokens(language=args.language, task=args.task)
    
    model = WhisperForConditionalGeneration.from_pretrained(args.model_id)
    # NOTE: do NOT call model.gradient_checkpointing_enable() here. The HF Trainer
    # enables it from training_args.gradient_checkpointing; enabling it twice (and
    # with the default reentrant autograd path) triggers
    # "Trying to backward through the graph a second time" on torch>=2.x.
    # We instead pass gradient_checkpointing_kwargs={'use_reentrant': False} to the
    # trainer below, and disable the KV cache (incompatible w/ checkpointing).
    if args.gradient_checkpointing:
        model.config.use_cache = False
    
    # Force language config
    model.generation_config.language = args.language
    model.generation_config.task = args.task
    model.generation_config.forced_decoder_ids = None
    
    n_params = sum(p.numel() for p in model.parameters())
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[whisper-trainer] params: total={n_params:,}, trainable={n_trainable:,}")
    try:
        # Whisper is seq2seq: torchinfo needs both encoder features + decoder ids.
        _df = torch.zeros(1, 80, 3000)
        _dd = torch.tensor([[model.config.decoder_start_token_id or 50258]], dtype=torch.long)
        save_model_summary(args.run_dir, model, args.model_id, n_params, n_trainable,
                           extra={"language": args.language, "task": args.task},
                           input_data={"input_features": _df, "decoder_input_ids": _dd})
    except Exception as _e:
        print(f"[whisper-trainer] model summary warn: {_e}")
    
    print("[whisper-trainer] loading splits ...")
    train_rows = load_split_rows(args.data_final / "train.tsv", args.data_root, args.max_train_samples)
    val_rows = load_split_rows(resolve_validation_tsv(args.data_final), args.data_root, args.max_val_samples)
    print(f"  train: {len(train_rows)}, val: {len(val_rows)}")
    
    train_ds = WhisperASRDataset(train_rows, processor)
    val_ds = WhisperASRDataset(val_rows, processor)
    
    @dataclass
    class WhisperDataCollator:
        processor: object
        def __call__(self, features):
            input_features = [{"input_features": f["input_features"]} for f in features]
            batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")
            label_features = [{"input_ids": f["labels"]} for f in features]
            labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")
            labels = labels_batch["input_ids"].masked_fill(
                labels_batch.attention_mask.ne(1), -100)
            if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
                labels = labels[:, 1:]
            batch["labels"] = labels
            return batch
    
    data_collator = WhisperDataCollator(processor)
    
    def compute_metrics(eval_pred):
        pred_ids = eval_pred.predictions
        label_ids = eval_pred.label_ids
        label_ids[label_ids == -100] = processor.tokenizer.pad_token_id
        pred_str = processor.tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
        label_str = processor.tokenizer.batch_decode(label_ids, skip_special_tokens=True)
        m = compute_wer_cer(pred_str, label_str)
        # val_acc proxy = 1 - char-error-rate (consistent across all our trainers)
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
        
        def on_epoch_begin(self, args_, state, control, **kwargs):
            timer.start_epoch()
            gpu_monitor.reset_peak()
        
        def on_log(self, args_, state, control, logs=None, **kwargs):
            if logs is None:
                return
            if "loss" in logs and "eval_loss" not in logs:
                self.epoch_train_loss = float(logs["loss"])
        
        def on_evaluate(self, args_, state, control, metrics=None, **kwargs):
            metrics = metrics or {}
            epoch = int(state.epoch) if state.epoch else 0
            elapsed = timer.end_epoch()
            gpu_mb = gpu_monitor.peak_mb()
            total = timer.total_elapsed()
            lr = state.log_history[-1].get("learning_rate", 0) if state.log_history else 0
            
            entry = {
                "train_loss": self.epoch_train_loss,
                "val_loss": float(metrics.get("eval_loss", 0)),
                "train_acc": None,  # filled below via train-subset teacher-forced eval
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
                    # Val sample preds (free-running generate)
                    for i in range(min(5, len(val_ds))):
                        item = val_ds[i]
                        feat = torch.tensor(item["input_features"]).unsqueeze(0).to(model.device, dtype=model.dtype)
                        ids = model.generate(feat, language=args.language, task=args.task, max_new_tokens=200)
                        pred = processor.tokenizer.decode(ids[0], skip_special_tokens=True).strip()
                        label = item["transcript"]
                        sample_preds.append((pred, label))
                    # Train Acc proxy: greedy decode on a small training sample (3-batch worth)
                    n_train_eval = min(15, len(train_ds))
                    for i in range(n_train_eval):
                        item = train_ds[i]
                        feat = torch.tensor(item["input_features"]).unsqueeze(0).to(model.device, dtype=model.dtype)
                        ids = model.generate(feat, language=args.language, task=args.task, max_new_tokens=200)
                        train_subset_preds.append(
                            processor.tokenizer.decode(ids[0], skip_special_tokens=True).strip())
                        train_subset_labels.append(item["transcript"])
                model.train()
            except Exception as e:
                print(f"[callback] sample pred error: {e}")
            
            # Train Acc from training subset CER
            if train_subset_preds:
                m_train = compute_wer_cer(train_subset_preds, train_subset_labels)
                entry["train_acc"] = cer_to_token_acc_proxy(m_train["cer"])
            
            history_saver.append_epoch(epoch, entry, sample_preds)
            
            # Save best model in our consistent naming convention (best_wer*_e*.pt + best.pt)
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
                    f"[Train] model={args.model_id} accuracy=1-CER (char-level proxy, free-running greedy)",
                ],
            )
            print(full_log, flush=True)
            with log_file.open("a", encoding="utf-8") as f:
                f.write(full_log + "\n")
            
            try:
                regenerate_plots(history_saver.history_path)
            except Exception as e:
                print(f"[callback] plot regen error: {e}")
    
    training_args = Seq2SeqTrainingArguments(
        output_dir=str(args.run_dir / "checkpoints"),
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        warmup_steps=args.warmup_steps,
        num_train_epochs=args.epochs,
        gradient_checkpointing=args.gradient_checkpointing,
        gradient_checkpointing_kwargs={"use_reentrant": False} if args.gradient_checkpointing else None,
        fp16=args.fp16 and torch.cuda.is_available(),
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        per_device_eval_batch_size=args.batch_size,
        predict_with_generate=True,
        generation_max_length=200,
        logging_steps=5,
        disable_tqdm=args.disable_tqdm,
        report_to=[],
        seed=args.seed,
        dataloader_num_workers=args.num_workers,
        remove_unused_columns=False,
        metric_for_best_model="wer",
        greater_is_better=False,
        load_best_model_at_end=True,
    )
    
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        processing_class=processor.tokenizer,
        callbacks=[FullLoggerCallback()],
    )
    
    print("[whisper-trainer] starting training ...")
    # Resume from checkpoint if requested (auto = latest checkpoint-* in run_dir)
    resume_arg = None
    if args.resume is not None:
        if args.resume == "auto":
            ckdirs = sorted((args.run_dir / "checkpoints").glob("checkpoint-*"),
                            key=lambda d: int(d.name.split("-")[-1]) if d.name.split("-")[-1].isdigit() else -1)
            resume_arg = str(ckdirs[-1]) if ckdirs else None
            print(f"[whisper-trainer] resume: auto -> {resume_arg or 'no checkpoint found, starting fresh'}")
        else:
            resume_arg = args.resume
            print(f"[whisper-trainer] resume: {resume_arg}")
    train_start = time.perf_counter()
    trainer.train(resume_from_checkpoint=resume_arg)
    train_elapsed = time.perf_counter() - train_start
    # Human-readable total training time (same style as m11/m12), logged to log.txt
    _h = int(train_elapsed // 3600); _m = int((train_elapsed % 3600) // 60); _s = int(train_elapsed % 60)
    total_str = f"{_h} jam, {_m} menit, {_s} detik"
    print(f"[whisper-trainer] training complete in {EpochTimer.format_seconds(train_elapsed)}")
    print(f"Total waktu training: {total_str}")
    with log_file.open("a", encoding="utf-8") as f:
        f.write(f"\nTotal waktu training: {total_str}\n")
    
    best = history_saver.get_best("wer")
    best_wer = best['wer'] if best else 'n/a'
    best_cer = best.get('cer', 'n/a') if best else 'n/a'
    best_ep = best['epoch'] if best else 'n/a'

    # Export the BEST model (load_best_model_at_end=True -> `model` is already best)
    # to a dedicated, directly-loadable HF directory: <run_dir>/best_model/
    best_dir = args.run_dir / "best_model"
    try:
        model.save_pretrained(str(best_dir))
        processor.save_pretrained(str(best_dir))
        (best_dir / "BEST_INFO.txt").write_text(
            f"model_id: {args.model_id}\nbest_wer: {best_wer}\nbest_cer: {best_cer}\n"
            f"best_epoch: {best_ep}\nload: WhisperForConditionalGeneration.from_pretrained('{best_dir}')\n",
            encoding="utf-8")
        print(f"[whisper-trainer] ★ best model saved -> {best_dir} (WER={best_wer})", flush=True)
    except Exception as _e:
        print(f"[whisper-trainer] best_model export warn: {_e}", flush=True)
    
    report = f"""# Training Report — {args.model_id}

**Run dir**: {args.run_dir}
**Generated**: {datetime.now().isoformat()}

## Config
- Model: {args.model_id}
- Epochs: {args.epochs}
- Batch size: {args.batch_size} (grad accum {args.grad_accum})
- Learning rate: {args.lr}
- Warmup steps: {args.warmup_steps}
- Train samples: {len(train_ds)}
- Val samples: {len(val_ds)}
- FP16: {args.fp16}
- DataLoader workers: {args.num_workers}
- Disable tqdm/progress bars: {args.disable_tqdm}
- Gradient checkpointing: {args.gradient_checkpointing}
- Seed: {args.seed}

## Model
- Total params: {n_params:,}
- Trainable params: {n_trainable:,}

## Final results
- Total training time: {EpochTimer.format_seconds(train_elapsed)}  ({total_str})
- Best WER: {best_wer if best else 'n/a'}
- Best CER: {best_cer if best else 'n/a'}
- Best at epoch: {best_ep if best else 'n/a'}

## Outputs
- History: `{args.run_dir / 'history.json'}`
- Log: `{args.run_dir / 'log.txt'}`
- Plots: `{args.run_dir / 'plots/'}`
- Predictions: `{args.run_dir / 'predictions/'}`
- Checkpoints: `{args.run_dir / 'checkpoints/'}`
"""
    (args.run_dir / "report.md").write_text(report, encoding="utf-8")
    print(f"[whisper-trainer] report saved: {args.run_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
