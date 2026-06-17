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


def metadata_stats() -> tuple[set[str], int, dict[str, set[str]], Counter[str], int, int, set[str]]:
    names: set[str] = set()
    total = 0
    gender_names: dict[str, set[str]] = {"Male": set(), "Female": set()}
    synthetic_by_gender: Counter[str] = Counter()
    real_total = 0
    synth_total = 0
    synth_targets: set[str] = set()
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
                synth_targets.add(speaker)
            else:
                real_total += 1
    return names, total, gender_names, synthetic_by_gender, real_total, synth_total, synth_targets


def main() -> int:
    errors: list[str] = []
    original_names, total_rows, _gender_names, synthetic_by_gender, real_total, synth_total, synth_targets = metadata_stats()

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

    if len(human_rows) != len(original_names):
        errors.append(f"human label count mismatch: {len(human_rows)} != {len(original_names)}")
    if len(synthetic_rows) != len(synth_targets):
        errors.append(f"synthetic label count mismatch: {len(synthetic_rows)} != {len(synth_targets)}")
    if sum(int(row.get("file_count", 0)) for row in public_rows) != total_rows:
        errors.append("public inventory file_count sum does not match metadata row count")
    if sum(int(row.get("real_files", 0)) for row in public_rows) != real_total:
        errors.append("public inventory real_files sum does not match metadata real row count")
    if sum(int(row.get("synthetic_files", 0)) for row in public_rows) != synth_total:
        errors.append("public inventory synthetic_files sum does not match metadata synthetic row count")

    for row in human_rows:
        sid = row.get("speaker_id", "")
        if not re.fullmatch(r"[A-Z][a-z0-9]", sid):
            errors.append(f"invalid two-character human label: {sid}")
            break
        if row.get("synthetic_voice_id") or row.get("repair_target_speaker_id"):
            errors.append(f"human row should not have synthetic fields populated: {sid}")
            break
    for row in synthetic_rows:
        sid = row.get("speaker_id", "")
        target = row.get("repair_target_speaker_id", "")
        if not re.fullmatch(r"[A-Z][a-z0-9]-s", sid):
            errors.append(f"invalid synthetic label: {sid}")
            break
        if sid != f"{target}-s":
            errors.append(f"synthetic label/target mismatch: {sid} vs {target}-s")
            break
        if target not in human_ids:
            errors.append(f"synthetic target not in human labels: {target}")
            break
        if row.get("synthetic_voice_id") != sid:
            errors.append(f"synthetic_voice_id should equal synthetic speaker_id: {sid}")
            break

    # Required collision behavior from project decision.
    required_human_labels = {"Ai", "Ar"}
    if not required_human_labels.issubset(human_ids):
        errors.append(f"expected collision-resolved labels missing: {sorted(required_human_labels - human_ids)}")
    if {"Ai-s", "Ar-s"} & synthetic_ids and not {"Ai", "Ar"}.issubset(human_ids):
        errors.append("synthetic collision labels present without matching human labels")

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
            if synth != f"{target}-s":
                errors.append(f"invalid synthetic target row: {synth} / {target}")
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
