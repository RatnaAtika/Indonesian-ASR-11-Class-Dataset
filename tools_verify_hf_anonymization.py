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
from pathlib import Path

ROOT = Path(__file__).resolve().parent
METADATA = ROOT / "metadata" / "dataset_metadata.csv"
PUBLIC_DIR = ROOT / "Report_paper_9model" / "hf_anonymization"
PLAN = ROOT / "Report_paper_9model" / "HUGGINGFACE_DATASET_UPLOAD_PLAN.md"

TARGET_FILES = [
    PUBLIC_DIR / "speaker_id_public_inventory.csv",
    PUBLIC_DIR / "speaker_id_public_inventory.json",
    PUBLIC_DIR / "speaker_anonymization_preparation_report.md",
    PLAN,
]


def metadata_stats() -> tuple[set[str], int, dict[str, int]]:
    names: set[str] = set()
    total = 0
    gender_counts: dict[str, set[str]] = {"Male": set(), "Female": set()}
    with METADATA.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            total += 1
            speaker = row["speaker_id"].strip()
            gender = row["speaker_gender"].strip()
            names.add(speaker)
            gender_counts.setdefault(gender, set()).add(speaker)
    return names, total, {k: len(v) for k, v in gender_counts.items()}


def main() -> int:
    errors: list[str] = []
    original_names, total_rows, gender_counts = metadata_stats()

    inv_csv = TARGET_FILES[0]
    if not inv_csv.exists():
        errors.append(f"missing {inv_csv}")
        public_rows = []
    else:
        public_rows = list(csv.DictReader(inv_csv.open(newline="", encoding="utf-8")))

    ids = [row.get("anonymized_speaker_id", "") for row in public_rows]
    if len(ids) != len(set(ids)):
        errors.append("duplicate anonymized speaker IDs")
    if len(ids) != len(original_names):
        errors.append(f"speaker ID count mismatch: {len(ids)} != {len(original_names)}")
    if sum(int(row.get("file_count", 0)) for row in public_rows) != total_rows:
        errors.append("public inventory file_count sum does not match metadata row count")

    male_ids = sorted([x for x in ids if re.fullmatch(r"M\d+", x)], key=lambda x: int(x[1:]))
    female_ids = sorted([x for x in ids if re.fullmatch(r"F\d+", x)], key=lambda x: int(x[1:]))
    expected_male = [f"M{i}" for i in range(1, gender_counts.get("Male", 0) + 1)]
    expected_female = [f"F{i}" for i in range(1, gender_counts.get("Female", 0) + 1)]
    if male_ids != expected_male:
        errors.append(f"male ID sequence mismatch: {male_ids} != {expected_male}")
    if female_ids != expected_female:
        errors.append(f"female ID sequence mismatch: {female_ids} != {expected_female}")

    # The new public anonymization prep files and HF upload plan should not leak
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
        f"({len(ids)} speaker IDs, {total_rows} metadata rows, "
        f"male={len(male_ids)}, female={len(female_ids)})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
