#!/usr/bin/env python3
"""Prepare public speaker-anonymization artifacts for the HF dataset upload.

Public policy:
- Real human audio uses anonymized respondent IDs: M1..Mn and F1..Fn.
- Synthetic repair audio uses acoustic-source IDs: MS1.. and FS1...
- Synthetic rows keep repair_target_speaker_id to show which anonymized human
  slot the synthetic item repairs, without exposing original respondent names.

This script writes only public, non-crosswalk artifacts by default. The private
original-name -> anonymized-ID crosswalk can be generated locally with
--private-crosswalk, but must not be committed or uploaded to Hugging Face.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_METADATA = ROOT / "metadata" / "dataset_metadata.csv"
DEFAULT_SPLIT_SUMMARY = ROOT / "splits" / "split_summary.json"
DEFAULT_OUTPUT_DIR = ROOT / "Report_paper_9model" / "hf_anonymization"
DEFAULT_PRIVATE_CROSSWALK = ROOT / "Report_paper_9model" / "hf_anonymization_private" / "speaker_crosswalk_PRIVATE_DO_NOT_UPLOAD.csv"

SYNTHETIC_VOICE_ID_BY_GENDER = {"Male": "MS1", "Female": "FS1"}
SYNTHETIC_SOURCE_BY_GENDER = {
    "Male": "male synthetic TTS voice",
    "Female": "female synthetic TTS voice",
}


def read_split_by_speaker(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    split_by_speaker: dict[str, str] = {}
    for split, speakers in data["speakers_by_split"].items():
        for speaker in speakers:
            split_by_speaker[speaker] = split
    return split_by_speaker


def collect_stats(metadata_path: Path) -> dict[str, Any]:
    human_stats: dict[str, dict[str, Any]] = {}
    synthetic_by_gender: dict[str, dict[str, Any]] = {}
    synthetic_targets: dict[tuple[str, str], dict[str, Any]] = {}
    source_voice_counts: Counter[tuple[str, str, str]] = Counter()
    total_rows = 0

    with metadata_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"speaker_id", "speaker_gender", "duration_sec", "is_synthetic", "synthesis_engine", "synthesis_voice", "synthesis_voice_label"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"Metadata missing required columns: {sorted(missing)}")
        for row in reader:
            total_rows += 1
            original_speaker = row["speaker_id"].strip()
            gender = row["speaker_gender"].strip()
            if not original_speaker or gender not in {"Male", "Female"}:
                raise SystemExit(f"Invalid speaker/gender row: {row}")
            duration = float(row.get("duration_sec") or 0.0)
            is_synthetic = str(row.get("is_synthetic", "")).strip().lower() == "true"

            human = human_stats.setdefault(
                original_speaker,
                {
                    "original_speaker": original_speaker,
                    "speaker_gender": gender,
                    "human_file_count": 0,
                    "synthetic_repair_file_count": 0,
                    "human_duration_sec": 0.0,
                    "synthetic_repair_duration_sec": 0.0,
                },
            )
            if human["speaker_gender"] != gender:
                raise SystemExit(f"Gender mismatch for speaker {original_speaker}: {human['speaker_gender']} vs {gender}")

            if is_synthetic:
                synth_id = SYNTHETIC_VOICE_ID_BY_GENDER[gender]
                synth = synthetic_by_gender.setdefault(
                    gender,
                    {
                        "speaker_id": synth_id,
                        "speaker_type": "synthetic",
                        "speaker_gender": gender,
                        "file_count": 0,
                        "duration_sec": 0.0,
                        "source_description": SYNTHETIC_SOURCE_BY_GENDER[gender],
                        "split_counts": Counter(),
                    },
                )
                synth["file_count"] += 1
                synth["duration_sec"] += duration
                source_voice_counts[(row.get("synthesis_engine", ""), row.get("synthesis_voice", ""), row.get("synthesis_voice_label", ""))] += 1
                human["synthetic_repair_file_count"] += 1
                human["synthetic_repair_duration_sec"] += duration
                synthetic_targets.setdefault(
                    (synth_id, original_speaker),
                    {
                        "synthetic_voice_id": synth_id,
                        "original_repair_target_private": original_speaker,
                        "speaker_gender": gender,
                        "synthetic_file_count": 0,
                        "synthetic_duration_sec": 0.0,
                    },
                )
                synthetic_targets[(synth_id, original_speaker)]["synthetic_file_count"] += 1
                synthetic_targets[(synth_id, original_speaker)]["synthetic_duration_sec"] += duration
            else:
                human["human_file_count"] += 1
                human["human_duration_sec"] += duration

    return {
        "human_stats": human_stats,
        "synthetic_by_gender": synthetic_by_gender,
        "synthetic_targets": synthetic_targets,
        "source_voice_counts": source_voice_counts,
        "total_rows": total_rows,
    }


def assign_human_ids(human_stats: dict[str, dict[str, Any]], split_by_speaker: dict[str, str]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    records: list[dict[str, Any]] = []
    private_name_to_id: dict[str, str] = {}
    for gender, prefix in [("Male", "M"), ("Female", "F")]:
        speakers = sorted(name for name, item in human_stats.items() if item["speaker_gender"] == gender)
        for idx, original_speaker in enumerate(speakers, start=1):
            item = human_stats[original_speaker]
            if original_speaker not in split_by_speaker:
                raise SystemExit(f"Speaker {original_speaker} missing from split summary")
            public_id = f"{prefix}{idx}"
            private_name_to_id[original_speaker] = public_id
            records.append(
                {
                    "speaker_id": public_id,
                    "speaker_type": "human",
                    "speaker_gender": gender,
                    "split": split_by_speaker[original_speaker],
                    "file_count": item["human_file_count"],
                    "real_files": item["human_file_count"],
                    "synthetic_files": 0,
                    "duration_sec": round(item["human_duration_sec"], 4),
                    "duration_hours": round(item["human_duration_sec"] / 3600.0, 4),
                    "synthetic_voice_id": "",
                    "repair_target_speaker_id": "",
                    "synthetic_repair_files_for_this_target": item["synthetic_repair_file_count"],
                    "_original_speaker_private": original_speaker,
                }
            )
    return records, private_name_to_id


def build_synthetic_records(
    synthetic_by_gender: dict[str, dict[str, Any]],
    synthetic_targets: dict[tuple[str, str], dict[str, Any]],
    private_name_to_id: dict[str, str],
    split_by_speaker: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    target_records: list[dict[str, Any]] = []
    split_counts_by_synth: dict[str, Counter[str]] = defaultdict(Counter)

    for (_synth_id, original_target), item in sorted(synthetic_targets.items(), key=lambda kv: (kv[0][0], private_name_to_id[kv[0][1]])):
        target_id = private_name_to_id[original_target]
        split = split_by_speaker[original_target]
        synth_id = item["synthetic_voice_id"]
        split_counts_by_synth[synth_id][split] += int(item["synthetic_file_count"])
        target_records.append(
            {
                "synthetic_voice_id": synth_id,
                "repair_target_speaker_id": target_id,
                "speaker_gender": item["speaker_gender"],
                "target_split": split,
                "synthetic_file_count": int(item["synthetic_file_count"]),
                "synthetic_duration_sec": round(item["synthetic_duration_sec"], 4),
                "synthetic_duration_hours": round(item["synthetic_duration_sec"] / 3600.0, 4),
            }
        )

    synthetic_records: list[dict[str, Any]] = []
    for gender in ["Male", "Female"]:
        if gender not in synthetic_by_gender:
            continue
        item = synthetic_by_gender[gender]
        synth_id = item["speaker_id"]
        split_counts = dict(sorted(split_counts_by_synth[synth_id].items()))
        split_label = "+".join(split_counts) if len(split_counts) > 1 else next(iter(split_counts), "")
        synthetic_records.append(
            {
                "speaker_id": synth_id,
                "speaker_type": "synthetic",
                "speaker_gender": gender,
                "split": split_label,
                "file_count": int(item["file_count"]),
                "real_files": 0,
                "synthetic_files": int(item["file_count"]),
                "duration_sec": round(item["duration_sec"], 4),
                "duration_hours": round(item["duration_sec"] / 3600.0, 4),
                "synthetic_voice_id": synth_id,
                "repair_target_speaker_id": "multiple",
                "synthetic_repair_files_for_this_target": "",
                "split_counts": split_counts,
            }
        )
    return synthetic_records, target_records


def write_public_outputs(
    human_records: list[dict[str, Any]],
    synthetic_records: list[dict[str, Any]],
    target_records: list[dict[str, Any]],
    source_voice_counts: Counter[tuple[str, str, str]],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    public_fields = [
        "speaker_id",
        "speaker_type",
        "speaker_gender",
        "split",
        "file_count",
        "real_files",
        "synthetic_files",
        "duration_sec",
        "duration_hours",
        "synthetic_voice_id",
        "repair_target_speaker_id",
        "synthetic_repair_files_for_this_target",
    ]
    public_rows = [{field: rec.get(field, "") for field in public_fields} for rec in [*human_records, *synthetic_records]]

    csv_path = output_dir / "speaker_id_public_inventory.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=public_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(public_rows)

    target_path = output_dir / "synthetic_repair_targets_public.csv"
    target_fields = [
        "synthetic_voice_id",
        "repair_target_speaker_id",
        "speaker_gender",
        "target_split",
        "synthetic_file_count",
        "synthetic_duration_sec",
        "synthetic_duration_hours",
    ]
    with target_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=target_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(target_records)

    voice_sources = [
        {
            "synthesis_engine": engine,
            "synthesis_voice": voice,
            "synthesis_voice_label": label,
            "file_count": count,
            "public_synthetic_voice_id": "MS1" if "Male" in label else "FS1" if "Female" in label else "",
        }
        for (engine, voice, label), count in sorted(source_voice_counts.items())
    ]

    json_path = output_dir / "speaker_id_public_inventory.json"
    json_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "purpose": "Public acoustic speaker/source inventory for HF upload. Contains anonymized IDs only; no original respondent names.",
                "id_policy": {
                    "human_male": "M1..M11",
                    "human_female": "F1..F9",
                    "synthetic_male": "MS1",
                    "synthetic_female": "FS1",
                    "note": "speaker_id is the acoustic source. Synthetic rows also carry repair_target_speaker_id at per-file metadata level.",
                },
                "speaker_source_count": len(public_rows),
                "human_speaker_count": len(human_records),
                "synthetic_voice_count": len(synthetic_records),
                "male_human_count": sum(1 for r in human_records if r["speaker_gender"] == "Male"),
                "female_human_count": sum(1 for r in human_records if r["speaker_gender"] == "Female"),
                "files_total": sum(int(r["file_count"]) for r in public_rows),
                "human_files_total": sum(int(r["real_files"]) for r in public_rows),
                "synthetic_files_total": sum(int(r["synthetic_files"]) for r in public_rows),
                "duration_hours_total": round(sum(float(r["duration_hours"]) for r in public_rows), 4),
                "speakers": public_rows,
                "synthetic_repair_targets": target_records,
                "source_voices": voice_sources,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    schema_path = output_dir / "hf_public_metadata_schema.md"
    schema_path.write_text(
        """# HF Public Metadata Schema for Anonymized Speaker IDs

This schema should be used when rewriting metadata for Hugging Face upload.

| Field | Meaning | Example |
|---|---|---|
| `speaker_id` | Final acoustic speaker/source ID. Human audio uses `M*`/`F*`; synthetic audio uses `MS*`/`FS*`. | `M1`, `F3`, `MS1`, `FS1` |
| `speaker_type` | Acoustic source type. | `human`, `synthetic` |
| `speaker_gender` | Gender category retained for stratified analysis if consent permits. | `Male`, `Female` |
| `is_synthetic` | Whether this row is synthetic repair audio. | `False`, `True` |
| `synthetic_voice_id` | Synthetic acoustic source ID; blank for human rows. | `MS1`, `FS1` |
| `repair_target_speaker_id` | Anonymized human slot repaired by this synthetic item; blank for human rows. | `M2`, `F4` |

## Per-row rule

- Human row: `speaker_id=M*/F*`, `speaker_type=human`, `synthetic_voice_id=`, `repair_target_speaker_id=`.
- Synthetic row: `speaker_id=MS1/FS1`, `speaker_type=synthetic`, `synthetic_voice_id=MS1/FS1`, `repair_target_speaker_id=M*/F*`.

This prevents users from mistaking synthetic repair audio for the original respondent's voice while still preserving the balancing/provenance target.
""",
        encoding="utf-8",
    )

    report_path = output_dir / "speaker_anonymization_preparation_report.md"
    male_ids = ", ".join(r["speaker_id"] for r in human_records if r["speaker_gender"] == "Male")
    female_ids = ", ".join(r["speaker_id"] for r in human_records if r["speaker_gender"] == "Female")
    synth_ids = ", ".join(r["speaker_id"] for r in synthetic_records)
    split_counts: dict[str, int] = defaultdict(int)
    for row in human_records:
        split_counts[str(row["split"])] += 1
    report_path.write_text(
        f"""# HF Speaker Anonymization Preparation Report

Status: **prepared for private-first HF upload**.

## Policy

The HF dataset package should not expose respondent names in public metadata, folder names, file paths, or dataset-card examples.

Use acoustic-source IDs:

- Human male IDs: `{male_ids}`
- Human female IDs: `{female_ids}`
- Synthetic voice IDs: `{synth_ids}`

For synthetic repair data, `speaker_id` is the synthetic acoustic source (`MS1` or `FS1`), while `repair_target_speaker_id` stores the anonymized human slot that the synthetic item repairs. This avoids falsely implying that synthetic TTS audio is the respondent's real voice.

The private original-name to anonymized-ID crosswalk is intentionally **not committed** and must not be uploaded to Hugging Face. If a crosswalk is required for internal auditing, generate it locally with:

```bash
python3 tools_prepare_hf_anonymization.py --private-crosswalk
```

The private file path is ignored by Git:

```text
Report_paper_9model/hf_anonymization_private/speaker_crosswalk_PRIVATE_DO_NOT_UPLOAD.csv
```

## Public inventory summary

- Human speaker IDs: {len(human_records)}
- Synthetic voice IDs: {len(synthetic_records)}
- Human male IDs: {sum(1 for r in human_records if r['speaker_gender'] == 'Male')}
- Human female IDs: {sum(1 for r in human_records if r['speaker_gender'] == 'Female')}
- Human files represented: {sum(int(r['real_files']) for r in public_rows):,}
- Synthetic files represented: {sum(int(r['synthetic_files']) for r in public_rows):,}
- Total files represented: {sum(int(r['file_count']) for r in public_rows):,}
- Total duration represented: {sum(float(r['duration_hours']) for r in public_rows):.4f} h
- Human split speaker counts: train={split_counts.get('train', 0)}, dev={split_counts.get('dev', 0)}, test={split_counts.get('test', 0)}

## Generated public files

- `Report_paper_9model/hf_anonymization/speaker_id_public_inventory.csv`
- `Report_paper_9model/hf_anonymization/speaker_id_public_inventory.json`
- `Report_paper_9model/hf_anonymization/synthetic_repair_targets_public.csv`
- `Report_paper_9model/hf_anonymization/hf_public_metadata_schema.md`
- `Report_paper_9model/hf_anonymization/speaker_anonymization_preparation_report.md`

## Required HF staging rewrite

When building the HF staging folder, rewrite fields/paths from original respondent names to anonymized IDs:

1. Human rows: `speaker_id` -> `M*`/`F*`.
2. Synthetic rows: `speaker_id` -> `MS1`/`FS1`.
3. Add `speaker_type`: `human` or `synthetic`.
4. Keep `speaker_gender` as `Male`/`Female` if approved by consent/ethics review.
5. Add `synthetic_voice_id`: blank for human rows; `MS1`/`FS1` for synthetic rows.
6. Add `repair_target_speaker_id`: blank for human rows; anonymized target `M*`/`F*` for synthetic rows.
7. `audio_path`: replace speaker directories and take-id prefixes with the final public `speaker_id`.
8. `audio_path_abs`: do not publish local absolute paths; replace with relative HF paths.
9. Dataset card examples should use only anonymized IDs.

## Hard rule

Do not upload or commit any file containing the original respondent-name crosswalk once the anonymized HF package is prepared.
""",
        encoding="utf-8",
    )


def write_private_crosswalk(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["original_speaker", "anonymized_speaker_id", "speaker_gender", "split", "human_file_count", "synthetic_repair_file_count"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for rec in records:
            writer.writerow(
                {
                    "original_speaker": rec["_original_speaker_private"],
                    "anonymized_speaker_id": rec["speaker_id"],
                    "speaker_gender": rec["speaker_gender"],
                    "split": rec["split"],
                    "human_file_count": rec["real_files"],
                    "synthetic_repair_file_count": rec["synthetic_repair_files_for_this_target"],
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

    split_by_speaker = read_split_by_speaker(args.split_summary)
    stats = collect_stats(args.metadata)
    human_records, private_name_to_id = assign_human_ids(stats["human_stats"], split_by_speaker)
    synthetic_records, target_records = build_synthetic_records(
        stats["synthetic_by_gender"],
        stats["synthetic_targets"],
        private_name_to_id,
        split_by_speaker,
    )
    write_public_outputs(human_records, synthetic_records, target_records, stats["source_voice_counts"], args.output_dir)
    if args.private_crosswalk:
        write_private_crosswalk(human_records, args.private_crosswalk_path)
        print(f"Wrote PRIVATE crosswalk: {args.private_crosswalk_path}")
    print(f"Prepared public anonymization artifacts in: {args.output_dir}")
    print(
        "Speaker sources: "
        f"human={len(human_records)}, synthetic={len(synthetic_records)}, "
        f"files={sum(int(r['file_count']) for r in [*human_records, *synthetic_records])}"
    )


if __name__ == "__main__":
    main()
