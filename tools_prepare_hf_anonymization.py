#!/usr/bin/env python3
"""Prepare public speaker-label artifacts for the HF dataset upload.

Current public policy:
- Human respondent labels use gender prefixes and alphabetical numbering:
  Male => M1..Mn, Female => F1..Fn.
- Synthetic repair labels use synthetic gender prefixes and alphabetical target
  numbering: Male synthetic => Ms1..Msn, Female synthetic => Fs1..Fsn.
- The numbering is deterministic: sort original respondent names alphabetically
  inside each gender group, then assign the next number. Synthetic labels are
  assigned only to respondents that have synthetic repair rows, sorted by the
  original target name inside each gender group.
- Public files contain labels and gender/type metadata only. The private
  original-name -> public-label crosswalk can be generated locally with
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

HUMAN_PREFIX = {"Male": "M", "Female": "F"}
SYNTH_PREFIX = {"Male": "Ms", "Female": "Fs"}


def read_split_by_speaker(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    split_by_speaker: dict[str, str] = {}
    for split, speakers in data["speakers_by_split"].items():
        for speaker in speakers:
            split_by_speaker[speaker] = split
    return split_by_speaker


def collect_stats(metadata_path: Path) -> dict[str, Any]:
    human_stats: dict[str, dict[str, Any]] = {}
    synthetic_targets: dict[str, dict[str, Any]] = {}
    source_voice_counts: Counter[tuple[str, str, str, str]] = Counter()
    total_rows = 0

    with metadata_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {
            "speaker_id",
            "speaker_gender",
            "duration_sec",
            "is_synthetic",
            "synthesis_engine",
            "synthesis_voice",
            "synthesis_voice_label",
        }
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
                human["synthetic_repair_file_count"] += 1
                human["synthetic_repair_duration_sec"] += duration
                synth = synthetic_targets.setdefault(
                    original_speaker,
                    {
                        "original_repair_target_private": original_speaker,
                        "speaker_gender": gender,
                        "synthetic_file_count": 0,
                        "synthetic_duration_sec": 0.0,
                    },
                )
                synth["synthetic_file_count"] += 1
                synth["synthetic_duration_sec"] += duration
                source_voice_counts[
                    (
                        gender,
                        row.get("synthesis_engine", ""),
                        row.get("synthesis_voice", ""),
                        row.get("synthesis_voice_label", ""),
                    )
                ] += 1
            else:
                human["human_file_count"] += 1
                human["human_duration_sec"] += duration

    return {
        "human_stats": human_stats,
        "synthetic_targets": synthetic_targets,
        "source_voice_counts": source_voice_counts,
        "total_rows": total_rows,
    }


def assign_human_codes(human_stats: dict[str, dict[str, Any]]) -> dict[str, str]:
    """Assign M/F labels by alphabetical order within each gender."""
    result: dict[str, str] = {}
    for gender in ["Male", "Female"]:
        names = sorted(name for name, row in human_stats.items() if row["speaker_gender"] == gender)
        prefix = HUMAN_PREFIX[gender]
        for idx, name in enumerate(names, start=1):
            result[name] = f"{prefix}{idx}"
    if len(result) != len(set(result.values())):
        raise SystemExit("Human label generation produced duplicates")
    return result


def assign_synthetic_codes(synthetic_targets: dict[str, dict[str, Any]]) -> dict[str, str]:
    """Assign Ms/Fs labels by alphabetical order of original repair targets."""
    result: dict[str, str] = {}
    for gender in ["Male", "Female"]:
        names = sorted(name for name, row in synthetic_targets.items() if row["speaker_gender"] == gender)
        prefix = SYNTH_PREFIX[gender]
        for idx, name in enumerate(names, start=1):
            result[name] = f"{prefix}{idx}"
    if len(result) != len(set(result.values())):
        raise SystemExit("Synthetic label generation produced duplicates")
    return result


def assign_human_records(
    human_stats: dict[str, dict[str, Any]],
    split_by_speaker: dict[str, str],
    private_name_to_human_code: dict[str, str],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    def sort_key(name: str) -> tuple[str, int]:
        code = private_name_to_human_code[name]
        return (code[0], int(code[1:]))

    for original_speaker in sorted(human_stats, key=sort_key):
        item = human_stats[original_speaker]
        if original_speaker not in split_by_speaker:
            raise SystemExit(f"Speaker {original_speaker} missing from split summary")
        records.append(
            {
                "speaker_id": private_name_to_human_code[original_speaker],
                "speaker_type": "human",
                "speaker_gender": item["speaker_gender"],
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
    return records


def build_synthetic_records(
    synthetic_targets: dict[str, dict[str, Any]],
    private_name_to_human_code: dict[str, str],
    private_name_to_synth_code: dict[str, str],
    split_by_speaker: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    synthetic_records: list[dict[str, Any]] = []
    target_records: list[dict[str, Any]] = []

    def sort_key(name: str) -> tuple[str, int]:
        code = private_name_to_synth_code[name]
        prefix = "Ms" if code.startswith("Ms") else "Fs"
        return (prefix, int(code[len(prefix):]))

    for original_target in sorted(synthetic_targets, key=sort_key):
        item = synthetic_targets[original_target]
        target_id = private_name_to_human_code[original_target]
        synthetic_id = private_name_to_synth_code[original_target]
        split = split_by_speaker[original_target]
        row = {
            "speaker_id": synthetic_id,
            "speaker_type": "synthetic",
            "speaker_gender": item["speaker_gender"],
            "split": split,
            "file_count": int(item["synthetic_file_count"]),
            "real_files": 0,
            "synthetic_files": int(item["synthetic_file_count"]),
            "duration_sec": round(item["synthetic_duration_sec"], 4),
            "duration_hours": round(item["synthetic_duration_sec"] / 3600.0, 4),
            "synthetic_voice_id": synthetic_id,
            "repair_target_speaker_id": target_id,
            "synthetic_repair_files_for_this_target": "",
        }
        synthetic_records.append(row)
        target_records.append(
            {
                "synthetic_voice_id": synthetic_id,
                "repair_target_speaker_id": target_id,
                "speaker_gender": item["speaker_gender"],
                "target_split": split,
                "synthetic_file_count": int(item["synthetic_file_count"]),
                "synthetic_duration_sec": round(item["synthetic_duration_sec"], 4),
                "synthetic_duration_hours": round(item["synthetic_duration_sec"] / 3600.0, 4),
            }
        )
    return synthetic_records, target_records


def write_public_outputs(
    human_records: list[dict[str, Any]],
    synthetic_records: list[dict[str, Any]],
    target_records: list[dict[str, Any]],
    source_voice_counts: Counter[tuple[str, str, str, str]],
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

    label_path = output_dir / "speaker_label_gender_list.csv"
    label_fields = ["speaker_id", "speaker_type", "speaker_gender", "split"]
    with label_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=label_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in label_fields} for row in public_rows])

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
            "speaker_gender": gender,
            "synthesis_engine": engine,
            "synthesis_voice": voice,
            "synthesis_voice_label": label,
            "file_count": count,
            "note": "source TTS voice; public synthetic labels use Ms*/Fs* per repair target",
        }
        for (gender, engine, voice, label), count in sorted(source_voice_counts.items())
    ]

    json_path = output_dir / "speaker_id_public_inventory.json"
    json_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "purpose": "Public speaker/source label inventory for HF upload. Contains public labels only; no original respondent names.",
                "id_policy": {
                    "human_male": "M1..M11, assigned alphabetically by original respondent name within Male group",
                    "human_female": "F1..F9, assigned alphabetically by original respondent name within Female group",
                    "synthetic_male": "Ms1..Msn, assigned alphabetically by original repair target name within Male synthetic group",
                    "synthetic_female": "Fs1..Fsn, assigned alphabetically by original repair target name within Female synthetic group",
                    "note": "speaker_id is the public acoustic row label. Synthetic rows also carry repair_target_speaker_id.",
                },
                "label_count": len(public_rows),
                "human_speaker_count": len(human_records),
                "synthetic_label_count": len(synthetic_records),
                "human_files_total": sum(int(r["real_files"]) for r in public_rows),
                "synthetic_files_total": sum(int(r["synthetic_files"]) for r in public_rows),
                "files_total": sum(int(r["file_count"]) for r in public_rows),
                "duration_hours_total": round(sum(float(r["duration_hours"]) for r in public_rows), 4),
                "speakers": public_rows,
                "synthetic_repair_targets": target_records,
                "source_tts_voices": voice_sources,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    schema_path = output_dir / "hf_public_metadata_schema.md"
    schema_path.write_text(
        """# HF Public Metadata Schema for M/F and Ms/Fs Speaker Labels

This schema should be used when rewriting metadata for Hugging Face upload.

| Field | Meaning | Example |
|---|---|---|
| `speaker_id` | Final public acoustic row label. Human audio uses `M*`/`F*`; synthetic repair audio uses `Ms*`/`Fs*`. | `M1`, `F1`, `Ms1`, `Fs1` |
| `speaker_type` | Acoustic source type. | `human`, `synthetic` |
| `speaker_gender` | Gender label retained for stratified analysis and documented in `speaker_label_gender_list.csv`. | `Male`, `Female` |
| `is_synthetic` | Whether this row is synthetic repair audio. | `False`, `True` |
| `synthetic_voice_id` | Synthetic public row label; blank for human rows. | `Ms1`, `Fs1` |
| `repair_target_speaker_id` | Public human target repaired by this synthetic item; blank for human rows. | `M2`, `F4` |

## Per-row rule

- Human row: `speaker_id=M*` or `F*`, `speaker_type=human`, `synthetic_voice_id=`, `repair_target_speaker_id=`.
- Synthetic row: `speaker_id=Ms*` or `Fs*`, `speaker_type=synthetic`, `synthetic_voice_id=Ms*` or `Fs*`, `repair_target_speaker_id=M*` or `F*`.

The `repair_target_speaker_id` keeps the anonymized human slot provenance for each synthetic repair item without exposing original respondent names.
""",
        encoding="utf-8",
    )

    report_path = output_dir / "speaker_anonymization_preparation_report.md"
    male_human = ", ".join(r["speaker_id"] for r in human_records if r["speaker_gender"] == "Male")
    female_human = ", ".join(r["speaker_id"] for r in human_records if r["speaker_gender"] == "Female")
    male_synth = ", ".join(r["speaker_id"] for r in synthetic_records if r["speaker_gender"] == "Male")
    female_synth = ", ".join(r["speaker_id"] for r in synthetic_records if r["speaker_gender"] == "Female")
    split_counts: dict[str, int] = defaultdict(int)
    for row in human_records:
        split_counts[str(row["split"])] += 1
    report_path.write_text(
        f"""# HF Speaker Label Preparation Report

Status: **prepared for private-first HF upload**.

## Policy

The HF dataset package should not expose respondent names in public metadata, folder names, file paths, or dataset-card examples.

Use public labels:

- Human male labels: `{male_human}`
- Human female labels: `{female_human}`
- Synthetic male labels: `{male_synth}`
- Synthetic female labels: `{female_synth}`

Human labels use `M`/`F` plus alphabetic order number within each gender group. Synthetic repair labels use `Ms`/`Fs` plus alphabetic order number within each synthetic target gender group. Synthetic rows also store `repair_target_speaker_id` so users know which anonymized human slot the synthetic item repairs.

The private original-name to public-label crosswalk is intentionally **not committed** and must not be uploaded to Hugging Face. If a crosswalk is required for internal auditing, generate it locally with:

```bash
python3 tools_prepare_hf_anonymization.py --private-crosswalk
```

The private file path is ignored by Git:

```text
Report_paper_9model/hf_anonymization_private/speaker_crosswalk_PRIVATE_DO_NOT_UPLOAD.csv
```

## Public inventory summary

- Human labels: {len(human_records)}
- Synthetic repair labels: {len(synthetic_records)}
- Human male labels: {sum(1 for r in human_records if r['speaker_gender'] == 'Male')}
- Human female labels: {sum(1 for r in human_records if r['speaker_gender'] == 'Female')}
- Human files represented: {sum(int(r['real_files']) for r in public_rows):,}
- Synthetic files represented: {sum(int(r['synthetic_files']) for r in public_rows):,}
- Total files represented: {sum(int(r['file_count']) for r in public_rows):,}
- Total duration represented: {sum(float(r['duration_hours']) for r in public_rows):.4f} h
- Human split speaker counts: train={split_counts.get('train', 0)}, dev={split_counts.get('dev', 0)}, test={split_counts.get('test', 0)}

## Generated public files

- `Report_paper_9model/hf_anonymization/speaker_id_public_inventory.csv`
- `Report_paper_9model/hf_anonymization/speaker_id_public_inventory.json`
- `Report_paper_9model/hf_anonymization/speaker_label_gender_list.csv`
- `Report_paper_9model/hf_anonymization/synthetic_repair_targets_public.csv`
- `Report_paper_9model/hf_anonymization/hf_public_metadata_schema.md`
- `Report_paper_9model/hf_anonymization/speaker_anonymization_preparation_report.md`

## Required HF staging rewrite

When building the HF staging folder, rewrite fields/paths from original respondent names to public labels:

1. Human rows: `speaker_id` -> `M*`/`F*`.
2. Synthetic rows: `speaker_id` -> `Ms*`/`Fs*`.
3. Add `speaker_type`: `human` or `synthetic`.
4. Keep `speaker_gender` as `Male`/`Female` and document labels in `speaker_label_gender_list.csv`.
5. Add `synthetic_voice_id`: blank for human rows; `Ms*`/`Fs*` for synthetic rows.
6. Add `repair_target_speaker_id`: blank for human rows; target public human label for synthetic rows.
7. `audio_path`: replace speaker directories and take-id prefixes with the final public `speaker_id`.
8. `audio_path_abs`: do not publish local absolute paths; replace with relative HF paths.
9. Dataset card examples should use only public labels.

## Hard rule

Do not upload or commit any file containing the original respondent-name crosswalk once the HF package is prepared.
""",
        encoding="utf-8",
    )


def write_private_crosswalk(
    human_records: list[dict[str, Any]],
    private_name_to_synth_code: dict[str, str],
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["original_speaker", "public_speaker_id", "synthetic_public_speaker_id", "speaker_gender", "split", "human_file_count", "synthetic_repair_file_count"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for rec in human_records:
            original = rec["_original_speaker_private"]
            writer.writerow(
                {
                    "original_speaker": original,
                    "public_speaker_id": rec["speaker_id"],
                    "synthetic_public_speaker_id": private_name_to_synth_code.get(original, ""),
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
    private_name_to_human_code = assign_human_codes(stats["human_stats"])
    private_name_to_synth_code = assign_synthetic_codes(stats["synthetic_targets"])
    human_records = assign_human_records(stats["human_stats"], split_by_speaker, private_name_to_human_code)
    synthetic_records, target_records = build_synthetic_records(
        stats["synthetic_targets"],
        private_name_to_human_code,
        private_name_to_synth_code,
        split_by_speaker,
    )
    write_public_outputs(human_records, synthetic_records, target_records, stats["source_voice_counts"], args.output_dir)
    if args.private_crosswalk:
        write_private_crosswalk(human_records, private_name_to_synth_code, args.private_crosswalk_path)
        print(f"Wrote PRIVATE crosswalk: {args.private_crosswalk_path}")
    print(f"Prepared public speaker-label artifacts in: {args.output_dir}")
    print(
        "Labels: "
        f"human={len(human_records)}, synthetic={len(synthetic_records)}, "
        f"files={sum(int(r['file_count']) for r in [*human_records, *synthetic_records])}"
    )


if __name__ == "__main__":
    main()
