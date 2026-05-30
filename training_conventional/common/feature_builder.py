"""Build log-Mel + SPM feature pickles from v7 dataset.

Output format (compatible with root-level train_model_vanilla.py / train_model_vit.py):
    {
        "X":      list[np.ndarray (T, 80) float32],   # log-mel, mean-var per utt
        "y":      list[np.ndarray int64],             # token ids with <s>...</s>
        "fnames": list[str],
        "text":   list[str],
        "lengths": list[int],
    }

Usage:
    python3 feature_builder.py \\
        --audio-root .../Dataset_Balanced19 \\
        --splits-dir training/data_final \\
        --spm-model training_conventional/spm/spm_v7_char.model \\
        --out-dir training_conventional/data_pkl \\
        --max-train 0 --max-val 0 --max-test 0
"""
from __future__ import annotations
import argparse, csv, json, pickle, sys, time
from datetime import datetime
from pathlib import Path

import numpy as np
import soundfile as sf
import librosa
import sentencepiece as spm

PROJECT = Path(__file__).parent.parent.parent

DEFAULTS = {
    "audio_root": PROJECT / "Processed_Balanced19_v7_natural_synth" / "Dataset_Balanced19",
    "splits_dir": PROJECT / "training" / "data_final",
    "spm_model": PROJECT / "training_conventional" / "spm" / "spm_v7_char.model",
    "out_dir":   PROJECT / "training_conventional" / "data_pkl",
}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--audio-root", type=Path, default=DEFAULTS["audio_root"])
    p.add_argument("--splits-dir", type=Path, default=DEFAULTS["splits_dir"])
    p.add_argument("--spm-model", type=Path, default=DEFAULTS["spm_model"])
    p.add_argument("--out-dir", type=Path, default=DEFAULTS["out_dir"])
    p.add_argument("--max-train", type=int, default=0, help="0 = full")
    p.add_argument("--max-val", type=int, default=0)
    p.add_argument("--max-test", type=int, default=0)
    p.add_argument("--n-mels", type=int, default=80)
    p.add_argument("--n-fft", type=int, default=512)
    p.add_argument("--hop", type=int, default=256)
    p.add_argument("--pre-emphasis", type=float, default=0.97)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def pre_emph(x: np.ndarray, coeff: float = 0.97) -> np.ndarray:
    if x.size == 0:
        return x
    y = np.empty_like(x, dtype=np.float32)
    y[0] = x[0]
    y[1:] = x[1:] - coeff * x[:-1]
    return y


def compute_log_mel(wav: np.ndarray, sr: int, n_mels: int, n_fft: int, hop: int) -> np.ndarray:
    mel = librosa.feature.melspectrogram(
        y=wav, sr=sr, n_fft=n_fft, hop_length=hop, n_mels=n_mels, power=1.0,
    )
    log_mel = np.log(np.maximum(mel, 1e-7)).astype(np.float32)
    # Per-utterance global mean-var normalization
    mu = float(np.mean(log_mel))
    std = float(np.std(log_mel)) + 1e-10
    log_mel = (log_mel - mu) / std
    return log_mel.T  # (T, F)


def load_split(tsv: Path, audio_root: Path, max_n: int = 0):
    rows = []
    with tsv.open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            ap = audio_root / r["audio_path"]
            if not ap.exists():
                continue
            rows.append({"audio_path": str(ap), "rel_path": r["audio_path"],
                         "transcript": r["transcript"].strip()})
            if max_n > 0 and len(rows) >= max_n:
                break
    return rows


def build_split(rows, sp, args, split_name):
    Xs, ys, fnames, texts, lens = [], [], [], [], []
    n = len(rows)
    t0 = time.perf_counter()
    skipped = 0
    for i, r in enumerate(rows):
        try:
            wav, sr = sf.read(r["audio_path"], dtype="float32")
            if wav.ndim > 1:
                wav = wav.mean(axis=1).astype(np.float32)
            if sr != 16000:
                wav = librosa.resample(wav, orig_sr=sr, target_sr=16000)
                sr = 16000
            wav = pre_emph(wav, args.pre_emphasis)
            feat = compute_log_mel(wav, sr, args.n_mels, args.n_fft, args.hop)
            ids = [sp.bos_id()] + sp.encode_as_ids(r["transcript"]) + [sp.eos_id()]
            Xs.append(feat.astype(np.float32))
            ys.append(np.array(ids, dtype=np.int64))
            fnames.append(r["rel_path"])
            texts.append(r["transcript"])
            lens.append(int(feat.shape[0]))
        except Exception as e:
            skipped += 1
            if skipped < 5:
                print(f"  [warn] skipped {r['rel_path']}: {e}")
        if (i + 1) % 1000 == 0:
            elapsed = time.perf_counter() - t0
            rate = (i + 1) / elapsed
            eta_s = (n - (i + 1)) / max(rate, 1e-6)
            print(f"  [{split_name}] {i+1:,}/{n:,} ({100*(i+1)/n:.1f}%)  "
                  f"rate={rate:.1f}/s  eta={eta_s/60:.1f}min  skipped={skipped}", flush=True)
    elapsed = time.perf_counter() - t0
    print(f"  [{split_name}] done in {elapsed/60:.1f} min, skipped={skipped}")
    return {"X": Xs, "y": ys, "fnames": fnames, "text": texts, "lengths": lens}


def main():
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    np.random.seed(args.seed)
    
    print(f"[feature-builder] audio_root: {args.audio_root}")
    print(f"[feature-builder] splits_dir: {args.splits_dir}")
    print(f"[feature-builder] spm_model:  {args.spm_model}")
    print(f"[feature-builder] out_dir:    {args.out_dir}")
    print(f"[feature-builder] mel: n_fft={args.n_fft}, hop={args.hop}, n_mels={args.n_mels}, pre_emph={args.pre_emphasis}")
    
    sp = spm.SentencePieceProcessor(model_file=str(args.spm_model))
    print(f"[feature-builder] SPM vocab size: {sp.get_piece_size()}")
    
    splits = [
        ("train", args.splits_dir / "train.tsv", args.max_train, "train.pkl"),
        ("valid", args.splits_dir / "dev.tsv",   args.max_val,   "valid.pkl"),
        ("test",  args.splits_dir / "test.tsv",  args.max_test,  "test.pkl"),
    ]
    
    manifest = {"generated": datetime.now().isoformat(), "splits": {}}
    
    for split_name, tsv, max_n, out_name in splits:
        print(f"\n[feature-builder] === {split_name} ===")
        if not tsv.exists():
            print(f"  ⚠ skip: {tsv} not found"); continue
        rows = load_split(tsv, args.audio_root, max_n)
        print(f"  loaded rows: {len(rows):,}")
        if not rows:
            continue
        data = build_split(rows, sp, args, split_name)
        out_path = args.out_dir / out_name
        with out_path.open("wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"  ✓ saved: {out_path} ({out_path.stat().st_size/(1024*1024):.1f} MB)")
        manifest["splits"][split_name] = {
            "n_samples": len(data["X"]),
            "out_file": out_name,
            "size_mb": round(out_path.stat().st_size / (1024 * 1024), 2),
            "mean_T": float(np.mean(data["lengths"])),
            "max_T": int(max(data["lengths"])),
            "min_T": int(min(data["lengths"])),
        }
    
    manifest["spm"] = {
        "model_file": str(args.spm_model),
        "vocab_size": sp.get_piece_size(),
    }
    manifest["features"] = {
        "n_mels": args.n_mels, "n_fft": args.n_fft, "hop": args.hop,
        "sample_rate": 16000, "pre_emphasis": args.pre_emphasis,
        "norm": "per-utt global mean-var",
    }
    (args.out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    print(f"\n[feature-builder] manifest: {args.out_dir / 'manifest.json'}")
    print(f"[feature-builder] DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
