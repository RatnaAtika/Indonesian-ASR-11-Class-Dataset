#!/usr/bin/env python3
"""Verify public HF speaker-label preparation files.

Checks only the committed public preparation package and HF upload plan, not the
whole repository (historical development files may contain respondent names).
"""

from __future__ import annotations

import csv
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
    PUBLIC_DIR / "speaker_label_gender_list.csv",
    PUBLIC_DIR / "synthetic_repair_targets_public.csv",
    PUBLIC_DIR / "hf_public_metadata_schema.md",
    PUBLIC_DIR / "speaker_anonymization_preparation_report.md",
    PLAN,
]


def metadata_stats() -> tuple[set[str], int, dict[str, list[str]], Counter[str], int, int, dict[str, list[str]]]:
    names: set[str] = set()
    total = 0
    gender_names: dict[str, set[str]] = {"Male": set(), "Female": set()}
    synth_targets_by_gender: dict[str, set[str]] = {"Male": set(), "Female": set()}
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
                synth_targets_by_gender.setdefault(gender, set()).add(speaker)
            else:
                real_total += 1
    return (
        names,
        total,
        {gender: sorted(values) for gender, values in gender_names.items()},
        synthetic_by_gender,
        real_total,
        synth_total,
        {gender: sorted(values) for gender, values in synth_targets_by_gender.items()},
    )


def expected_human_labels(gender_names: dict[str, list[str]]) -> dict[str, str]:
    expected: dict[str, str] = {}
    for gender, prefix in [("Male", "M"), ("Female", "F")]:
        for idx, name in enumerate(sorted(gender_names.get(gender, [])), start=1):
            expected[name] = f"{prefix}{idx}"
    return expected


def expected_synth_labels(synth_targets_by_gender: dict[str, list[str]]) -> dict[str, str]:
    expected: dict[str, str] = {}
    for gender, prefix in [("Male", "Ms"), ("Female", "Fs")]:
        for idx, name in enumerate(sorted(synth_targets_by_gender.get(gender, [])), start=1):
            expected[name] = f"{prefix}{idx}"
    return expected


def main() -> int:
    errors: list[str] = []
    original_names, total_rows, gender_names, synthetic_by_gender, real_total, synth_total, synth_targets_by_gender = metadata_stats()
    expected_human = set(expected_human_labels(gender_names).values())
    expected_synth = set(expected_synth_labels(synth_targets_by_gender).values())

    inv_csv = PUBLIC_DIR / "speaker_id_public_inventory.csv"
    if not inv_csv.exists():
        errors.append(f"missing {inv_csv}")
        public_rows = []
    else:
        public_rows = list(csv.DictReader(inv_csv.open(newline="", encoding="utf-8")))

    ids = [row.get("speaker_id", "") for row in public_rows]
    if len(ids) != len(set(ids)):
        errors.append("duplicate public speaker labels")

    human_rows = [row for row in public_rows if row.get("speaker_type") == "human"]
    synthetic_rows = [row for row in public_rows if row.get("speaker_type") == "synthetic"]
    human_ids = {row.get("speaker_id", "") for row in human_rows}
    synthetic_ids = {row.get("speaker_id", "") for row in synthetic_rows}

    if human_ids != expected_human:
        errors.append(f"human label set mismatch: {sorted(human_ids)} != {sorted(expected_human)}")
    if synthetic_ids != expected_synth:
        errors.append(f"synthetic label set mismatch: {sorted(synthetic_ids)} != {sorted(expected_synth)}")
    if len(human_rows) != len(original_names):
        errors.append(f"human label count mismatch: {len(human_rows)} != {len(original_names)}")
    if len(synthetic_rows) != len(expected_synth):
        errors.append(f"synthetic label count mismatch: {len(synthetic_rows)} != {len(expected_synth)}")
    if sum(int(row.get("file_count", 0)) for row in public_rows) != total_rows:
        errors.append("public inventory file_count sum does not match metadata row count")
    if sum(int(row.get("real_files", 0)) for row in public_rows) != real_total:
        errors.append("public inventory real_files sum does not match metadata real row count")
    if sum(int(row.get("synthetic_files", 0)) for row in public_rows) != synth_total:
        errors.append("public inventory synthetic_files sum does not match metadata synthetic row count")

    for row in human_rows:
        sid = row.get("speaker_id", "")
        gender = row.get("speaker_gender", "")
        if gender == "Male" and not re.fullmatch(r"M\d+", sid):
            errors.append(f"invalid male human label: {sid}")
            break
        if gender == "Female" and not re.fullmatch(r"F\d+", sid):
            errors.append(f"invalid female human label: {sid}")
            break
        if row.get("synthetic_voice_id") or row.get("repair_target_speaker_id"):
            errors.append(f"human row should not have synthetic fields populated: {sid}")
            break
    for row in synthetic_rows:
        sid = row.get("speaker_id", "")
        target = row.get("repair_target_speaker_id", "")
        gender = row.get("speaker_gender", "")
        if gender == "Male" and not re.fullmatch(r"Ms\d+", sid):
            errors.append(f"invalid male synthetic label: {sid}")
            break
        if gender == "Female" and not re.fullmatch(r"Fs\d+", sid):
            errors.append(f"invalid female synthetic label: {sid}")
            break
        if target not in human_ids:
            errors.append(f"synthetic target not in human labels: {target}")
            break
        if row.get("synthetic_voice_id") != sid:
            errors.append(f"synthetic_voice_id should equal synthetic speaker_id: {sid}")
            break

    label_csv = PUBLIC_DIR / "speaker_label_gender_list.csv"
    if label_csv.exists():
        label_rows = list(csv.DictReader(label_csv.open(newline="", encoding="utf-8")))
        if {row.get("speaker_id", "") for row in label_rows} != set(ids):
            errors.append("speaker_label_gender_list.csv label set does not match public inventory")
    else:
        errors.append(f"missing {label_csv}")

    target_csv = PUBLIC_DIR / "synthetic_repair_targets_public.csv"
    if target_csv.exists():
        target_rows = list(csv.DictReader(target_csv.open(newline="", encoding="utf-8")))
        if sum(int(row.get("synthetic_file_count", 0)) for row in target_rows) != synth_total:
            errors.append("synthetic repair target count sum does not match metadata synthetic row count")
        for row in target_rows:
            synth = row.get("synthetic_voice_id", "")
            target = row.get("repair_target_speaker_id", "")
            gender = row.get("speaker_gender", "")
            if gender == "Male" and not re.fullmatch(r"Ms\d+", synth):
                errors.append(f"invalid male synthetic target row: {synth}")
                break
            if gender == "Female" and not re.fullmatch(r"Fs\d+", synth):
                errors.append(f"invalid female synthetic target row: {synth}")
                break
            if target not in human_ids:
                errors.append(f"synthetic target row points to unknown human label: {target}")
                break
    else:
        errors.append(f"missing {target_csv}")

    # Public prep files and the HF upload plan should not leak original respondent names.
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
        print("HF speaker-label verification FAILED")
        for err in errors:
            print(f"- {err}")
        return 1
    print(
        "OK: HF speaker-label preparation verified "
        f"(human={len(human_rows)}, synthetic_labels={len(synthetic_rows)}, "
        f"rows={total_rows}, real={real_total}, synthetic={synth_total}, "
        f"synthetic_male={synthetic_by_gender.get('Male', 0)}, synthetic_female={synthetic_by_gender.get('Female', 0)})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
