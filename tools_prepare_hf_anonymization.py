#!/usr/bin/env python3
"""Prepare public speaker-anonymization artifacts for the HF dataset upload.

This script intentionally writes only public, non-crosswalk artifacts by default.
The private original-name -> anonymized-ID crosswalk can be generated locally with
--private-crosswalk, but must not be committed or uploaded to Hugging Face.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_METADATA = ROOT / "metadata" / "dataset_metadata.csv"
DEFAULT_SPLIT_SUMMARY = ROOT / "splits" / "split_summary.json"
DEFAULT_OUTPUT_DIR = ROOT / "Report_paper_9model" / "hf_anonymization"
DEFAULT_PRIVATE_CROSSWALK = ROOT / "Report_paper_9model" / "hf_anonymization_private" / "speaker_crosswalk_PRIVATE_DO_NOT_UPLOAD.csv"


def read_split_by_speaker(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    split_by_speaker: dict[str, str] = {}
    for split, speakers in data["speakers_by_split"].items():
        for speaker in speakers:
            split_by_speaker[speaker] = split
    return split_by_speaker


def collect_speaker_stats(metadata_path: Path) -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = {}
    with metadata_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"speaker_id", "speaker_gender", "duration_sec", "is_synthetic"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"Metadata missing required columns: {sorted(missing)}")
        for row in reader:
            speaker = row["speaker_id"].strip()
            gender = row["speaker_gender"].strip()
            if not speaker or gender not in {"Male", "Female"}:
                raise SystemExit(f"Invalid speaker/gender row: {row}")
            entry = stats.setdefault(
                speaker,
                {
                    "original_speaker": speaker,
                    "speaker_gender": gender,
                    "file_count": 0,
                    "real_files": 0,
                    "synthetic_files": 0,
                    "duration_sec": 0.0,
                },
            )
            if entry["speaker_gender"] != gender:
                raise SystemExit(f"Gender mismatch for speaker {speaker}: {entry['speaker_gender']} vs {gender}")
            entry["file_count"] += 1
            entry["duration_sec"] += float(row.get("duration_sec") or 0.0)
            is_synth = str(row.get("is_synthetic", "")).strip().lower() == "true"
            if is_synth:
                entry["synthetic_files"] += 1
            else:
                entry["real_files"] += 1
    return stats


def assign_ids(stats: dict[str, dict[str, Any]], split_by_speaker: dict[str, str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for gender, prefix in [("Male", "M"), ("Female", "F")]:
        speakers = sorted(name for name, item in stats.items() if item["speaker_gender"] == gender)
        for idx, speaker in enumerate(speakers, start=1):
            item = stats[speaker]
            if speaker not in split_by_speaker:
                raise SystemExit(f"Speaker {speaker} missing from split summary")
            records.append(
                {
                    "anonymized_speaker_id": f"{prefix}{idx}",
                    "speaker_gender": gender,
                    "split": split_by_speaker[speaker],
                    "file_count": item["file_count"],
                    "real_files": item["real_files"],
                    "synthetic_files": item["synthetic_files"],
                    "duration_sec": round(item["duration_sec"], 4),
                    "duration_hours": round(item["duration_sec"] / 3600.0, 4),
                    "_original_speaker_private": speaker,
                }
            )
    return records


def write_public_outputs(records: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    public_fields = [
        "anonymized_speaker_id",
        "speaker_gender",
        "split",
        "file_count",
        "real_files",
        "synthetic_files",
        "duration_sec",
        "duration_hours",
    ]
    public_rows = [{field: rec[field] for field in public_fields} for rec in records]

    csv_path = output_dir / "speaker_id_public_inventory.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=public_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(public_rows)

    json_path = output_dir / "speaker_id_public_inventory.json"
    json_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "purpose": "Public speaker inventory for HF upload. Contains anonymized IDs only; no original respondent names.",
                "id_policy": "Male speakers use M1..Mn; female speakers use F1..Fn. Private deterministic crosswalk is generated locally and is not for Git/HF upload.",
                "speaker_count": len(public_rows),
                "male_count": sum(1 for r in public_rows if r["speaker_gender"] == "Male"),
                "female_count": sum(1 for r in public_rows if r["speaker_gender"] == "Female"),
                "files_total": sum(int(r["file_count"]) for r in public_rows),
                "duration_hours_total": round(sum(float(r["duration_hours"]) for r in public_rows), 4),
                "speakers": public_rows,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    report_path = output_dir / "speaker_anonymization_preparation_report.md"
    male_ids = ", ".join(r["anonymized_speaker_id"] for r in public_rows if r["speaker_gender"] == "Male")
    female_ids = ", ".join(r["anonymized_speaker_id"] for r in public_rows if r["speaker_gender"] == "Female")
    split_counts: dict[str, int] = defaultdict(int)
    for row in public_rows:
        split_counts[str(row["split"])] += 1
    report_path.write_text(
        f"""# HF Speaker Anonymization Preparation Report

Status: **prepared for private-first HF upload**.

## Policy

The HF dataset package should not expose respondent names in public metadata, folder names, file paths, or dataset-card examples. Respondents will be represented only by gender-coded IDs:

- Male IDs: `{male_ids}`
- Female IDs: `{female_ids}`

The private original-name to anonymized-ID crosswalk is intentionally **not committed** and must not be uploaded to Hugging Face. If a crosswalk is required for internal auditing, generate it locally with:

```bash
python3 tools_prepare_hf_anonymization.py --private-crosswalk
```

The private file path is ignored by Git:

```text
Report_paper_9model/hf_anonymization_private/speaker_crosswalk_PRIVATE_DO_NOT_UPLOAD.csv
```

## Public inventory summary

- Public speaker IDs: {len(public_rows)}
- Male IDs: {sum(1 for r in public_rows if r['speaker_gender'] == 'Male')}
- Female IDs: {sum(1 for r in public_rows if r['speaker_gender'] == 'Female')}
- Total files represented: {sum(int(r['file_count']) for r in public_rows):,}
- Total duration represented: {sum(float(r['duration_hours']) for r in public_rows):.4f} h
- Split speaker counts: train={split_counts.get('train', 0)}, dev={split_counts.get('dev', 0)}, test={split_counts.get('test', 0)}

## Generated public files

- `Report_paper_9model/hf_anonymization/speaker_id_public_inventory.csv`
- `Report_paper_9model/hf_anonymization/speaker_id_public_inventory.json`
- `Report_paper_9model/hf_anonymization/speaker_anonymization_preparation_report.md`

## Required HF staging rewrite

When building the HF staging folder, rewrite these fields/paths from original respondent names to anonymized IDs:

1. `speaker_id` -> `anonymized_speaker_id` only.
2. Keep `speaker_gender` as `Male`/`Female` if approved by consent/ethics review.
3. `audio_path`: replace the speaker directory and take-id prefix with the anonymized ID.
4. `audio_path_abs`: do not publish local absolute paths; replace with relative HF paths.
5. `take_id`: replace original-name prefix with anonymized ID.
6. Audio folder paths under `data/processed_balanced19_v3/Dataset_Balanced19/<category>/<speaker>/...` must use `M*`/`F*` folders only.
7. Dataset card examples should use only anonymized IDs.

## Hard rule

Do not upload or commit any file containing the original respondent-name crosswalk once the anonymized HF package is prepared.
""",
        encoding="utf-8",
    )


def write_private_crosswalk(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["original_speaker", "anonymized_speaker_id", "speaker_gender", "split", "file_count", "duration_hours"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for rec in records:
            writer.writerow(
                {
                    "original_speaker": rec["_original_speaker_private"],
                    "anonymized_speaker_id": rec["anonymized_speaker_id"],
                    "speaker_gender": rec["speaker_gender"],
                    "split": rec["split"],
                    "file_count": rec["file_count"],
                    "duration_hours": rec["duration_hours"],
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--split-summary", type=Path, default=DEFAULT_SPLIT_SUMMARY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--private-crosswalk", action="store_true", help="Also write the private original-name crosswalk. Do not commit/upload it.")
    parser.add_argument("--private-crosswalk-path", type=Path, default=DEFAULT_PRIVATE_CROSSWALK)
    args = parser.parse_args()

    stats = collect_speaker_stats(args.metadata)
    split_by_speaker = read_split_by_speaker(args.split_summary)
    records = assign_ids(stats, split_by_speaker)
    write_public_outputs(records, args.output_dir)
    if args.private_crosswalk:
        write_private_crosswalk(records, args.private_crosswalk_path)
        print(f"Wrote PRIVATE crosswalk: {args.private_crosswalk_path}")
    print(f"Prepared public anonymization artifacts in: {args.output_dir}")
    print(f"Speakers: {len(records)}; male={sum(1 for r in records if r['speaker_gender']=='Male')}; female={sum(1 for r in records if r['speaker_gender']=='Female')}")


if __name__ == "__main__":
    main()
