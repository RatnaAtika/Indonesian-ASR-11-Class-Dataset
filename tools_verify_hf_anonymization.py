#!/usr/bin/env python3
"""Verify public HF anonymization preparation files.

Checks only the committed anonymization preparation package and HF upload plan,
not the whole repository (the repository still contains historical development
materials that may mention respondent names).
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
METADATA = ROOT / "metadata" / "dataset_metadata.csv"
PUBLIC_DIR = ROOT / "Report_paper_9model" / "hf_anonymization"
PLAN = ROOT / "Report_paper_9model" / "HUGGINGFACE_DATASET_UPLOAD_PLAN.md"

TARGET_FILES = [
    PUBLIC_DIR / "speaker_id_public_inventory.csv",
    PUBLIC_DIR / "speaker_id_public_inventory.json",
    PUBLIC_DIR / "synthetic_repair_targets_public.csv",
    PUBLIC_DIR / "hf_public_metadata_schema.md",
    PUBLIC_DIR / "speaker_anonymization_preparation_report.md",
    PLAN,
]


def metadata_stats() -> tuple[set[str], int, dict[str, set[str]], Counter[str], int, int]:
    names: set[str] = set()
    total = 0
    gender_names: dict[str, set[str]] = {"Male": set(), "Female": set()}
    synthetic_by_gender: Counter[str] = Counter()
    real_total = 0
    synth_total = 0
    with METADATA.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            total += 1
            speaker = row["speaker_id"].strip()
            gender = row["speaker_gender"].strip()
            is_synth = str(row.get("is_synthetic", "")).strip().lower() == "true"
            names.add(speaker)
            gender_names.setdefault(gender, set()).add(speaker)
            if is_synth:
                synthetic_by_gender[gender] += 1
                synth_total += 1
            else:
                real_total += 1
    return names, total, gender_names, synthetic_by_gender, real_total, synth_total


def main() -> int:
    errors: list[str] = []
    original_names, total_rows, gender_names, synthetic_by_gender, real_total, synth_total = metadata_stats()

    inv_csv = TARGET_FILES[0]
    if not inv_csv.exists():
        errors.append(f"missing {inv_csv}")
        public_rows = []
    else:
        public_rows = list(csv.DictReader(inv_csv.open(newline="", encoding="utf-8")))

    ids = [row.get("speaker_id", "") for row in public_rows]
    if len(ids) != len(set(ids)):
        errors.append("duplicate public speaker/source IDs")

    human_rows = [row for row in public_rows if row.get("speaker_type") == "human"]
    synthetic_rows = [row for row in public_rows if row.get("speaker_type") == "synthetic"]
    if len(human_rows) != len(original_names):
        errors.append(f"human speaker ID count mismatch: {len(human_rows)} != {len(original_names)}")
    if {row.get("speaker_id") for row in synthetic_rows} != {"MS1", "FS1"}:
        errors.append(f"synthetic speaker IDs mismatch: {sorted(row.get('speaker_id') for row in synthetic_rows)}")

    if sum(int(row.get("file_count", 0)) for row in public_rows) != total_rows:
        errors.append("public inventory file_count sum does not match metadata row count")
    if sum(int(row.get("real_files", 0)) for row in public_rows) != real_total:
        errors.append("public inventory real_files sum does not match metadata real row count")
    if sum(int(row.get("synthetic_files", 0)) for row in public_rows) != synth_total:
        errors.append("public inventory synthetic_files sum does not match metadata synthetic row count")

    male_ids = sorted([row["speaker_id"] for row in human_rows if row.get("speaker_gender") == "Male"], key=lambda x: int(x[1:]))
    female_ids = sorted([row["speaker_id"] for row in human_rows if row.get("speaker_gender") == "Female"], key=lambda x: int(x[1:]))
    expected_male = [f"M{i}" for i in range(1, len(gender_names.get("Male", set())) + 1)]
    expected_female = [f"F{i}" for i in range(1, len(gender_names.get("Female", set())) + 1)]
    if male_ids != expected_male:
        errors.append(f"male ID sequence mismatch: {male_ids} != {expected_male}")
    if female_ids != expected_female:
        errors.append(f"female ID sequence mismatch: {female_ids} != {expected_female}")

    synth_counts = {row["speaker_id"]: int(row.get("synthetic_files", 0)) for row in synthetic_rows}
    if synth_counts.get("MS1") != synthetic_by_gender.get("Male", 0):
        errors.append(f"MS1 count mismatch: {synth_counts.get('MS1')} != {synthetic_by_gender.get('Male', 0)}")
    if synth_counts.get("FS1") != synthetic_by_gender.get("Female", 0):
        errors.append(f"FS1 count mismatch: {synth_counts.get('FS1')} != {synthetic_by_gender.get('Female', 0)}")

    target_csv = PUBLIC_DIR / "synthetic_repair_targets_public.csv"
    if target_csv.exists():
        target_rows = list(csv.DictReader(target_csv.open(newline="", encoding="utf-8")))
        if sum(int(row.get("synthetic_file_count", 0)) for row in target_rows) != synth_total:
            errors.append("synthetic repair target count sum does not match metadata synthetic row count")
        for row in target_rows:
            target = row.get("repair_target_speaker_id", "")
            if not re.fullmatch(r"[MF]\d+", target):
                errors.append(f"invalid repair target ID: {target}")
                break
    else:
        errors.append(f"missing {target_csv}")

    # The public anonymization prep files and HF upload plan should not leak
    # original respondent names. Use token boundaries to avoid accidental partials.
    for path in TARGET_FILES:
        if not path.exists():
            errors.append(f"missing target file: {path}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for name in sorted(original_names, key=len, reverse=True):
            if re.search(rf"(?<![A-Za-z]){re.escape(name)}(?![A-Za-z])", text):
                errors.append(f"original respondent name appears in public prep file: {path}: {name}")
                break
        if path != PLAN and "/mnt/c/" in text:
            errors.append(f"local absolute path appears in public prep file: {path}")

    private_dir = ROOT / "Report_paper_9model" / "hf_anonymization_private"
    if private_dir.exists():
        errors.append(f"private crosswalk directory exists locally; verify it is ignored and do not commit/upload: {private_dir}")

    if errors:
        print("HF anonymization verification FAILED")
        for err in errors:
            print(f"- {err}")
        return 1
    print(
        "OK: HF anonymization preparation verified "
        f"(human={len(human_rows)}, synthetic_sources={len(synthetic_rows)}, "
        f"rows={total_rows}, real={real_total}, synthetic={synth_total}, "
        f"MS1={synthetic_by_gender.get('Male', 0)}, FS1={synthetic_by_gender.get('Female', 0)})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
