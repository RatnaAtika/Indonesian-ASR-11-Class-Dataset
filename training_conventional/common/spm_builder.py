"""Build a SentencePiece char-subword model from v7 transcripts.

Compatible with the existing root-level `spm/spm_char_fixed.model` API:
  - vocab_size 400 default
  - special tokens: <pad>=0 <unk>=1 <s>=2 </s>=3 <noise>=4 <laugh>=5 <hes>=6
  - char_coverage 1.0
  - model_type unigram (matches existing model)

Output:
  spm/spm_v7_char.model
  spm/spm_v7_char.vocab
  spm/spm_corpus.txt
"""
from __future__ import annotations
import argparse, csv, re, unicodedata
from pathlib import Path

import sentencepiece as spm

try:
    from .split_compat import resolve_validation_tsv
except ImportError:  # direct script execution
    from split_compat import resolve_validation_tsv

PROJECT = Path(__file__).parent.parent.parent
DEFAULTS = {
    "splits_dir": PROJECT / "training" / "data_final",
    "out_dir": PROJECT / "training_conventional" / "spm",
    "vocab_size": 400,
    "model_type": "unigram",
    "char_coverage": 1.0,
}


def normalize_for_spm(t: str) -> str:
    """Light normalization: keep punctuation that affects tokenization minimal."""
    t = unicodedata.normalize("NFKC", str(t))
    return t.strip()


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--splits-dir", type=Path, default=DEFAULTS["splits_dir"])
    p.add_argument("--out-dir", type=Path, default=DEFAULTS["out_dir"])
    p.add_argument("--vocab-size", type=int, default=DEFAULTS["vocab_size"])
    p.add_argument("--model-type", default=DEFAULTS["model_type"])
    p.add_argument("--char-coverage", type=float, default=DEFAULTS["char_coverage"])
    p.add_argument("--prefix", default="spm_v7_char")
    return p.parse_args()


def main():
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    
    # Build corpus from train + validation (not test, to avoid contamination)
    corpus_path = args.out_dir / "spm_corpus.txt"
    n_lines = 0
    split_paths = (
        ("train", args.splits_dir / "train.tsv"),
        ("val", resolve_validation_tsv(args.splits_dir)),
    )
    with corpus_path.open("w", encoding="utf-8") as out:
        for split, tsv in split_paths:
            with tsv.open(encoding="utf-8") as f:
                for r in csv.DictReader(f, delimiter="\t"):
                    txt = normalize_for_spm(r["transcript"])
                    if txt:
                        out.write(txt + "\n")
                        n_lines += 1
    print(f"[spm] wrote corpus: {corpus_path} ({n_lines:,} lines)")
    
    # Train SPM
    out_prefix = str(args.out_dir / args.prefix)
    spm.SentencePieceTrainer.train(
        input=str(corpus_path),
        model_prefix=out_prefix,
        vocab_size=args.vocab_size,
        model_type=args.model_type,
        character_coverage=args.char_coverage,
        pad_id=0, unk_id=1, bos_id=2, eos_id=3,
        pad_piece="<pad>", unk_piece="<unk>", bos_piece="<s>", eos_piece="</s>",
        user_defined_symbols=["<noise>", "<laugh>", "<hes>"],
        normalization_rule_name="identity",  # we already normalize
    )
    print(f"[spm] trained: {out_prefix}.model + {out_prefix}.vocab")
    
    # Verify
    sp = spm.SentencePieceProcessor(model_file=f"{out_prefix}.model")
    print(f"[spm] vocab size: {sp.get_piece_size()}")
    print(f"[spm] specials: pad={sp.id_to_piece(0)} unk={sp.id_to_piece(1)} "
          f"bos={sp.id_to_piece(2)} eos={sp.id_to_piece(3)}")
    print(f"[spm] first 30 pieces: {[sp.id_to_piece(i) for i in range(30)]}")
    
    sample = "berapa temperatur udara di indralaya saat ini"
    ids = sp.encode_as_ids(sample)
    pieces = sp.encode_as_pieces(sample)
    decoded = sp.decode(ids)
    print(f"[spm] sample input : '{sample}'")
    print(f"[spm] sample pieces: {pieces}")
    print(f"[spm] sample ids   : {ids}")
    print(f"[spm] sample decode: '{decoded}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
