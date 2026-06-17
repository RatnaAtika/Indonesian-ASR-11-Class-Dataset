#!/usr/bin/env python3
"""Prepare public speaker-label artifacts for the HF dataset upload.

Public policy:
- Real human audio uses short two-letter respondent codes derived from the
  internal respondent name (for example, first two letters when unique).
- If first-two-letter codes collide, use a deterministic collision fallback:
  first letter + last letter; if still colliding, first letter + running number.
- Synthetic repair audio uses the target public code plus "-s".
- Public files contain labels and gender/type metadata only. The private
  original-name -> public-code crosswalk can be generated locally with
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


def make_public_codes(names: list[str]) -> dict[str, str]:
    """Return deterministic two-character public codes.

    Rule:
    1. Start with first two letters, title-cased.
    2. For any collision group, replace colliding codes with first+last.
    3. If first+last still collides, use first letter + deterministic number.
    """
    names = sorted(names)
    first_two: dict[str, str] = {name: name[:2].title() for name in names}
    by_code: dict[str, list[str]] = defaultdict(list)
    for name, code in first_two.items():
        by_code[code].append(name)

    result = dict(first_two)
    used: set[str] = set()
    for code, group in sorted(by_code.items()):
        if len(group) == 1:
            used.add(code)
            continue
        # Free the colliding first-two code, then use first+last for each name.
        for name in sorted(group):
            fallback = (name[0] + name[-1]).title()
            if fallback in used or fallback in result.values() and fallback not in {result[g] for g in group}:
                # Last-resort deterministic fallback; keep short and stable.
                idx = 1
                while True:
                    fallback = f"{name[0].upper()}{idx}"
                    if fallback not in used and fallback not in result.values():
                        break
                    idx += 1
            result[name] = fallback
            used.add(fallback)

    # Validate uniqueness after all replacements.
    values = list(result.values())
    if len(values) != len(set(values)):
        duplicates = [code for code, count in Counter(values).items() if count > 1]
        raise SystemExit(f"Public code generation produced duplicates: {duplicates}")
    return result


def assign_human_records(
    human_stats: dict[str, dict[str, Any]],
    split_by_speaker: dict[str, str],
    private_name_to_code: dict[str, str],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for original_speaker in sorted(human_stats):
        item = human_stats[original_speaker]
        if original_speaker not in split_by_speaker:
            raise SystemExit(f"Speaker {original_speaker} missing from split summary")
        records.append(
            {
                "speaker_id": private_name_to_code[original_speaker],
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
    return sorted(records, key=lambda r: r["speaker_id"])


def build_synthetic_records(
    synthetic_targets: dict[str, dict[str, Any]],
    private_name_to_code: dict[str, str],
    split_by_speaker: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    synthetic_records: list[dict[str, Any]] = []
    target_records: list[dict[str, Any]] = []
    for original_target in sorted(synthetic_targets, key=lambda name: private_name_to_code[name]):
        item = synthetic_targets[original_target]
        target_id = private_name_to_code[original_target]
        synthetic_id = f"{target_id}-s"
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
            "note": "source TTS voice; public per-row synthetic labels use <target_id>-s",
        }
        for (gender, engine, voice, label), count in sorted(source_voice_counts.items())
    ]

    json_path = output_dir / "speaker_id_public_inventory.json"
    json_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "purpose": "Public speaker/source label inventory for HF upload. Contains short public labels only; no original respondent names.",
                "id_policy": {
                    "human": "Two-character public respondent code derived deterministically from the internal name. First two letters are used when unique; first+last resolves first-two-letter collisions.",
                    "synthetic": "Synthetic repair rows use the repaired target public code plus '-s'.",
                    "example_shape": {"human": "At", "synthetic": "At-s"},
                    "note": "speaker_id is the acoustic row label used in public metadata. synthetic rows also carry repair_target_speaker_id.",
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
        """# HF Public Metadata Schema for Short Speaker Labels

This schema should be used when rewriting metadata for Hugging Face upload.

| Field | Meaning | Example |
|---|---|---|
| `speaker_id` | Final public acoustic row label. Human audio uses a short two-letter respondent code; synthetic repair audio uses the target code plus `-s`. | `At`, `Ai`, `Ai-s` |
| `speaker_type` | Acoustic source type. | `human`, `synthetic` |
| `speaker_gender` | Gender label retained for stratified analysis and documented in `speaker_label_gender_list.csv`. | `Male`, `Female` |
| `is_synthetic` | Whether this row is synthetic repair audio. | `False`, `True` |
| `synthetic_voice_id` | Synthetic public row label; blank for human rows. | `Ai-s` |
| `repair_target_speaker_id` | Public human target repaired by this synthetic item; blank for human rows. | `Ai` |

## Per-row rule

- Human row: `speaker_id=<two-letter code>`, `speaker_type=human`, `synthetic_voice_id=`, `repair_target_speaker_id=`.
- Synthetic row: `speaker_id=<target-code>-s`, `speaker_type=synthetic`, `synthetic_voice_id=<target-code>-s`, `repair_target_speaker_id=<target-code>`.

This prevents users from mistaking synthetic repair audio for a real respondent recording while still preserving which public respondent slot the synthetic item repairs.
""",
        encoding="utf-8",
    )

    report_path = output_dir / "speaker_anonymization_preparation_report.md"
    male_human = ", ".join(r["speaker_id"] for r in human_records if r["speaker_gender"] == "Male")
    female_human = ", ".join(r["speaker_id"] for r in human_records if r["speaker_gender"] == "Female")
    synth_ids = ", ".join(r["speaker_id"] for r in synthetic_records)
    split_counts: dict[str, int] = defaultdict(int)
    for row in human_records:
        split_counts[str(row["split"])] += 1
    report_path.write_text(
        f"""# HF Speaker Label Preparation Report

Status: **prepared for private-first HF upload**.

## Policy

The HF dataset package should not expose respondent names in public metadata, folder names, file paths, or dataset-card examples.

Use short public labels:

- Human male labels: `{male_human}`
- Human female labels: `{female_human}`
- Synthetic repair labels: `{synth_ids}`

Human labels are two-character codes. Synthetic repair labels append `-s` to the repaired human target label. For example, if a public human target is `Ai`, synthetic repair rows for that target use `Ai-s` and also store `repair_target_speaker_id=Ai`.

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

1. Human rows: `speaker_id` -> two-letter public label.
2. Synthetic rows: `speaker_id` -> `<repair_target_speaker_id>-s`.
3. Add `speaker_type`: `human` or `synthetic`.
4. Keep `speaker_gender` as `Male`/`Female` and document labels in `speaker_label_gender_list.csv`.
5. Add `synthetic_voice_id`: blank for human rows; `<target-label>-s` for synthetic rows.
6. Add `repair_target_speaker_id`: blank for human rows; target public label for synthetic rows.
7. `audio_path`: replace speaker directories and take-id prefixes with the final public `speaker_id`.
8. `audio_path_abs`: do not publish local absolute paths; replace with relative HF paths.
9. Dataset card examples should use only public labels.

## Hard rule

Do not upload or commit any file containing the original respondent-name crosswalk once the HF package is prepared.
""",
        encoding="utf-8",
    )


def write_private_crosswalk(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["original_speaker", "public_speaker_id", "synthetic_public_speaker_id", "speaker_gender", "split", "human_file_count", "synthetic_repair_file_count"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for rec in records:
            writer.writerow(
                {
                    "original_speaker": rec["_original_speaker_private"],
                    "public_speaker_id": rec["speaker_id"],
                    "synthetic_public_speaker_id": f"{rec['speaker_id']}-s" if int(rec["synthetic_repair_files_for_this_target"]) else "",
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
    private_name_to_code = make_public_codes(list(stats["human_stats"]))
    human_records = assign_human_records(stats["human_stats"], split_by_speaker, private_name_to_code)
    synthetic_records, target_records = build_synthetic_records(stats["synthetic_targets"], private_name_to_code, split_by_speaker)
    write_public_outputs(human_records, synthetic_records, target_records, stats["source_voice_counts"], args.output_dir)
    if args.private_crosswalk:
        write_private_crosswalk(human_records, args.private_crosswalk_path)
        print(f"Wrote PRIVATE crosswalk: {args.private_crosswalk_path}")
    print(f"Prepared public speaker-label artifacts in: {args.output_dir}")
    print(
        "Labels: "
        f"human={len(human_records)}, synthetic={len(synthetic_records)}, "
        f"files={sum(int(r['file_count']) for r in [*human_records, *synthetic_records])}"
    )


if __name__ == "__main__":
    main()
