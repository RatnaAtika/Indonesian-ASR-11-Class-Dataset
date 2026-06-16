#!/usr/bin/env python3
"""Verify Report_paper_9model/training_diagnostics package consistency."""

from __future__ import annotations

import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
PKG = ROOT / "Report_paper_9model" / "training_diagnostics"
MANIFEST = PKG / "training_diagnostics_manifest.json"

EXPECTED_MODELS = {
    "rank01_m02b-whisper-small-ft": ["plots/accuracy.png", "plots/loss.png", "plots/wer_cer.png", "model_summary.png", "report.md", "test_results/test_paper.json"],
    "rank02_m06-conformer-ctc": ["plots/accuracy.png", "plots/loss.png", "plots/wer_cer.png", "model_summary.png", "report.md", "test_results/test_paper.json"],
    "rank03_m12-vit-modified-ID": ["cer_vit.png", "char_accuracy_vit.png", "training_val_accuracy_vit.png", "training_val_loss_vit.png", "eval_greedy/summary_vit.png", "test_results/test_paper.json"],
    "rank04_m07-bilstm-ctc": ["plots/accuracy.png", "plots/loss.png", "plots/wer_cer.png", "model_summary.png", "report.md", "test_results/test_paper.json"],
    "rank05_m11-vanilla-transformer": ["cer.png", "char_accuracy.png", "training_val_accuracy.png", "training_val_loss.png", "eval_greedy/summary_vanilla.png", "test_results/test_paper.json"],
    "rank06_m13-wav2letter": ["plots/accuracy.png", "plots/loss.png", "plots/wer_cer.png", "model_summary.png", "report.md", "test_results/test_paper.json"],
    "rank07_m08-hmm-gmm": ["plots/accuracy.png", "plots/loss.png", "plots/wer_cer.png", "report.md", "test_results/test_paper.json"],
    "rank08_m10-gmm-hmm-dnn": ["plots/accuracy.png", "plots/loss.png", "plots/wer_cer.png", "report.md", "test_results/test_paper.json"],
    "rank09_m09-dnn-hmm": ["plots/accuracy.png", "plots/loss.png", "plots/wer_cer.png", "report.md", "test_results/test_paper.json"],
}

FORBIDDEN_PARTS = {"checkpoints", "best_model", "predictions"}
FORBIDDEN_SUFFIXES = {".pt", ".pth", ".pkl", ".safetensors", ".bin", ".ckpt", ".h5", ".keras"}


def main() -> None:
    errors: list[str] = []
    if not MANIFEST.exists():
        raise SystemExit(f"missing {MANIFEST}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    included = manifest.get("included_files", [])
    if manifest.get("included_count") != len(included):
        errors.append("included_count does not match included_files length")
    if len(included) < 100:
        errors.append(f"expected at least 100 included diagnostics, found {len(included)}")
    ranks = {item.get("rank_dir") for item in included}
    if ranks != set(EXPECTED_MODELS):
        errors.append(f"rank coverage mismatch: {sorted(ranks)}")
    package_paths = {item["package_path"] for item in included}
    for rank, required_rels in EXPECTED_MODELS.items():
        for rel in required_rels:
            expected_path = PKG / rank / rel
            expected_rel = expected_path.relative_to(ROOT).as_posix()
            if expected_rel not in package_paths or not expected_path.exists():
                errors.append(f"missing required diagnostic: {expected_rel}")
    for item in included:
        p = Path(item["package_path"])
        rel = Path(item["relative_path"])
        if not p.exists():
            errors.append(f"included path missing: {p}")
            continue
        if p.stat().st_size != item["size_bytes"]:
            errors.append(f"size mismatch: {p}")
        if any(part in FORBIDDEN_PARTS for part in rel.parts):
            if not rel.as_posix().startswith("test_results/"):
                errors.append(f"forbidden prediction/checkpoint path included: {rel}")
        if p.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"model/checkpoint file included: {p}")
        if p.stat().st_size > 10_000_000:
            errors.append(f"file over 10MB included: {p}")
        if p.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            try:
                im = Image.open(p)
                if im.size[0] < 200 or im.size[1] < 150:
                    errors.append(f"image too small: {p} {im.size}")
            except Exception as exc:
                errors.append(f"cannot open image {p}: {exc}")
    skipped_reasons = {item.get("reason") for item in manifest.get("skipped_files", [])}
    for required_reason in ["full_test_predictions_large_table_for_HuggingFace_or_external_artifact_storage", "model_or_checkpoint_artifact"]:
        if required_reason not in skipped_reasons:
            errors.append(f"expected skipped reason missing: {required_reason}")
    for doc in [PKG / "training_diagnostics_report.md", PKG / "training_diagnostics_report.pdf", PKG / "training_diagnostics_files.csv"]:
        if not doc.exists() or doc.stat().st_size == 0:
            errors.append(f"missing/empty documentation artifact: {doc}")
    if errors:
        print("FAIL: training diagnostics package verification")
        for error in errors[:80]:
            print("-", error)
        raise SystemExit(1)
    print(f"OK: training diagnostics package verified ({len(included)} files, {manifest.get('included_total_human')})")


if __name__ == "__main__":
    main()
