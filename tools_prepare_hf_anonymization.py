#!/usr/bin/env python3
"""Prepare public speaker-label artifacts for the HF dataset upload.

Policy:
- Human respondent labels use gender prefixes and alphabetical numbering after
  approved corrections: Male => M1..Mn, Female => F1..Fn.
- Synthetic repair labels describe the **actual synthetic acoustic voice gender**:
  Male synthetic voice => Ms1..Msn, Female synthetic voice => Fs1..Fsn.
- Synthetic rows also keep `repair_target_speaker_id` and
  `repair_target_speaker_gender` so cross-gender synthetic repairs are visible.
- The private original-name -> public-label crosswalk can be generated locally
  with --private-crosswalk, but must not be committed or uploaded to HF.
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

# Approved correction from project owner: Joni is Male.
GENDER_CORRECTIONS = {"Joni": "Male"}
HUMAN_PREFIX = {"Male": "M", "Female": "F"}
SYNTH_PREFIX = {"Male": "Ms", "Female": "Fs"}


def corrected_target_gender(name: str, raw_gender: str) -> str:
    return GENDER_CORRECTIONS.get(name, raw_gender)


def infer_synthetic_voice_gender(row: dict[str, str], target_gender: str) -> str:
    label = (row.get("synthesis_voice_label") or row.get("synthesis_voice") or "").lower()
    if "female" in label or "gadis" in label:
        return "Female"
    if "male" in label or "ardi" in label:
        return "Male"
    return target_gender


def read_split_by_speaker(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {speaker: split for split, speakers in data["speakers_by_split"].items() for speaker in speakers}


def collect_stats(metadata_path: Path) -> dict[str, Any]:
    human_stats: dict[str, dict[str, Any]] = {}
    synthetic_targets: dict[str, dict[str, Any]] = {}
    source_voice_counts: Counter[tuple[str, str, str, str]] = Counter()
    total_rows = 0
    correction_rows = 0

    with metadata_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"speaker_id", "speaker_gender", "duration_sec", "is_synthetic", "synthesis_engine", "synthesis_voice", "synthesis_voice_label"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"Metadata missing required columns: {sorted(missing)}")
        for row in reader:
            total_rows += 1
            name = row["speaker_id"].strip()
            raw_gender = row["speaker_gender"].strip()
            target_gender = corrected_target_gender(name, raw_gender)
            if target_gender != raw_gender:
                correction_rows += 1
            if not name or target_gender not in {"Male", "Female"}:
                raise SystemExit(f"Invalid speaker/gender row: {row}")
            duration = float(row.get("duration_sec") or 0.0)
            is_synth = str(row.get("is_synthetic", "")).strip().lower() == "true"

            human = human_stats.setdefault(
                name,
                {
                    "original_speaker": name,
                    "speaker_gender": target_gender,
                    "raw_gender_values": Counter(),
                    "human_file_count": 0,
                    "synthetic_repair_file_count": 0,
                    "human_duration_sec": 0.0,
                    "synthetic_repair_duration_sec": 0.0,
                },
            )
            human["raw_gender_values"][raw_gender] += 1
            if human["speaker_gender"] != target_gender:
                raise SystemExit(f"Corrected gender mismatch for speaker {name}")

            if is_synth:
                synth_gender = infer_synthetic_voice_gender(row, target_gender)
                human["synthetic_repair_file_count"] += 1
                human["synthetic_repair_duration_sec"] += duration
                synth = synthetic_targets.setdefault(
                    name,
                    {
                        "original_repair_target_private": name,
                        "repair_target_speaker_gender": target_gender,
                        "synthetic_speaker_gender": synth_gender,
                        "synthetic_file_count": 0,
                        "synthetic_duration_sec": 0.0,
                    },
                )
                if synth["synthetic_speaker_gender"] != synth_gender:
                    raise SystemExit(f"Multiple synthetic voice genders for target {name}")
                synth["synthetic_file_count"] += 1
                synth["synthetic_duration_sec"] += duration
                source_voice_counts[(synth_gender, row.get("synthesis_engine", ""), row.get("synthesis_voice", ""), row.get("synthesis_voice_label", ""))] += 1
            else:
                human["human_file_count"] += 1
                human["human_duration_sec"] += duration

    return {
        "human_stats": human_stats,
        "synthetic_targets": synthetic_targets,
        "source_voice_counts": source_voice_counts,
        "total_rows": total_rows,
        "correction_rows": correction_rows,
    }


def assign_human_codes(human_stats: dict[str, dict[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for gender in ["Male", "Female"]:
        names = sorted(name for name, row in human_stats.items() if row["speaker_gender"] == gender)
        for idx, name in enumerate(names, start=1):
            result[name] = f"{HUMAN_PREFIX[gender]}{idx}"
    if len(result) != len(set(result.values())):
        raise SystemExit("Human label generation produced duplicates")
    return result


def assign_synthetic_codes(synthetic_targets: dict[str, dict[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for gender in ["Male", "Female"]:
        names = sorted(name for name, row in synthetic_targets.items() if row["synthetic_speaker_gender"] == gender)
        for idx, name in enumerate(names, start=1):
            result[name] = f"{SYNTH_PREFIX[gender]}{idx}"
    if len(result) != len(set(result.values())):
        raise SystemExit("Synthetic label generation produced duplicates")
    return result


def assign_human_records(human_stats: dict[str, dict[str, Any]], split_by_speaker: dict[str, str], human_code: dict[str, str]) -> list[dict[str, Any]]:
    def sort_key(name: str) -> tuple[str, int]:
        c = human_code[name]
        return (c[0], int(c[1:]))
    rows = []
    for name in sorted(human_stats, key=sort_key):
        item = human_stats[name]
        rows.append({
            "speaker_id": human_code[name],
            "speaker_type": "human",
            "speaker_gender": item["speaker_gender"],
            "split": split_by_speaker[name],
            "file_count": item["human_file_count"],
            "real_files": item["human_file_count"],
            "synthetic_files": 0,
            "duration_sec": round(item["human_duration_sec"], 4),
            "duration_hours": round(item["human_duration_sec"] / 3600, 4),
            "synthetic_voice_id": "",
            "repair_target_speaker_id": "",
            "repair_target_speaker_gender": "",
            "voice_gender_matches_target": "",
            "synthetic_repair_files_for_this_target": item["synthetic_repair_file_count"],
            "_original_speaker_private": name,
        })
    return rows


def build_synthetic_records(synthetic_targets: dict[str, dict[str, Any]], human_code: dict[str, str], synth_code: dict[str, str], split_by_speaker: dict[str, str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    def sort_key(name: str) -> tuple[str, int]:
        c = synth_code[name]
        prefix = "Ms" if c.startswith("Ms") else "Fs"
        return (prefix, int(c[len(prefix):]))
    rows, targets = [], []
    for name in sorted(synthetic_targets, key=sort_key):
        item = synthetic_targets[name]
        sid = synth_code[name]
        target = human_code[name]
        match = item["synthetic_speaker_gender"] == item["repair_target_speaker_gender"]
        row = {
            "speaker_id": sid,
            "speaker_type": "synthetic",
            "speaker_gender": item["synthetic_speaker_gender"],
            "split": split_by_speaker[name],
            "file_count": int(item["synthetic_file_count"]),
            "real_files": 0,
            "synthetic_files": int(item["synthetic_file_count"]),
            "duration_sec": round(item["synthetic_duration_sec"], 4),
            "duration_hours": round(item["synthetic_duration_sec"] / 3600, 4),
            "synthetic_voice_id": sid,
            "repair_target_speaker_id": target,
            "repair_target_speaker_gender": item["repair_target_speaker_gender"],
            "voice_gender_matches_target": str(match),
            "synthetic_repair_files_for_this_target": "",
        }
        rows.append(row)
        targets.append({
            "synthetic_voice_id": sid,
            "repair_target_speaker_id": target,
            "speaker_gender": item["synthetic_speaker_gender"],
            "repair_target_speaker_gender": item["repair_target_speaker_gender"],
            "voice_gender_matches_target": str(match),
            "target_split": split_by_speaker[name],
            "synthetic_file_count": int(item["synthetic_file_count"]),
            "synthetic_duration_sec": round(item["synthetic_duration_sec"], 4),
            "synthetic_duration_hours": round(item["synthetic_duration_sec"] / 3600, 4),
        })
    return rows, targets


def write_public_outputs(human_records: list[dict[str, Any]], synthetic_records: list[dict[str, Any]], target_records: list[dict[str, Any]], source_voice_counts: Counter[tuple[str, str, str, str]], correction_rows: int, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fields = ["speaker_id", "speaker_type", "speaker_gender", "split", "file_count", "real_files", "synthetic_files", "duration_sec", "duration_hours", "synthetic_voice_id", "repair_target_speaker_id", "repair_target_speaker_gender", "voice_gender_matches_target", "synthetic_repair_files_for_this_target"]
    public_rows = [{f: r.get(f, "") for f in fields} for r in [*human_records, *synthetic_records]]
    for filename, rows, use_fields in [
        ("speaker_id_public_inventory.csv", public_rows, fields),
        ("speaker_label_gender_list.csv", [{k: r[k] for k in ["speaker_id", "speaker_type", "speaker_gender", "split"]} for r in public_rows], ["speaker_id", "speaker_type", "speaker_gender", "split"]),
    ]:
        with (output_dir / filename).open("w", newline="", encoding="utf-8") as h:
            w = csv.DictWriter(h, fieldnames=use_fields, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    target_fields = ["synthetic_voice_id", "repair_target_speaker_id", "speaker_gender", "repair_target_speaker_gender", "voice_gender_matches_target", "target_split", "synthetic_file_count", "synthetic_duration_sec", "synthetic_duration_hours"]
    with (output_dir / "synthetic_repair_targets_public.csv").open("w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=target_fields, lineterminator="\n"); w.writeheader(); w.writerows(target_records)

    voice_sources = [{"speaker_gender": g, "synthesis_engine": e, "synthesis_voice": v, "synthesis_voice_label": l, "file_count": c} for (g, e, v, l), c in sorted(source_voice_counts.items())]
    mismatch_files = sum(int(r["synthetic_file_count"]) for r in target_records if r["voice_gender_matches_target"] == "False")
    (output_dir / "speaker_id_public_inventory.json").write_text(json.dumps({
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "purpose": "Public speaker/source label inventory for HF upload. No original respondent names.",
        "gender_correction_note": "One respondent label was corrected from the source metadata before public M/F label assignment.",
        "corrected_metadata_rows": correction_rows,
        "id_policy": {
            "human_male": "M1..M12, assigned alphabetically by corrected respondent gender within Male group",
            "human_female": "F1..F8, assigned alphabetically by corrected respondent gender within Female group",
            "synthetic_male": "Ms*, assigned alphabetically by original repair target among actual male synthetic voices",
            "synthetic_female": "Fs*, assigned alphabetically by original repair target among actual female synthetic voices",
            "note": "speaker_id is the public acoustic source label. Synthetic rows carry repair_target_speaker_id and voice_gender_matches_target.",
        },
        "label_count": len(public_rows),
        "human_speaker_count": len(human_records),
        "synthetic_label_count": len(synthetic_records),
        "human_files_total": sum(int(r["real_files"]) for r in public_rows),
        "synthetic_files_total": sum(int(r["synthetic_files"]) for r in public_rows),
        "synthetic_voice_target_gender_mismatch_files": mismatch_files,
        "files_total": sum(int(r["file_count"]) for r in public_rows),
        "duration_hours_total": round(sum(float(r["duration_hours"]) for r in public_rows), 4),
        "speakers": public_rows,
        "synthetic_repair_targets": target_records,
        "source_tts_voices": voice_sources,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    (output_dir / "hf_public_metadata_schema.md").write_text("""# HF Public Metadata Schema for M/F and Ms/Fs Speaker Labels

| Field | Meaning | Example |
|---|---|---|
| `speaker_id` | Public acoustic row label. Human audio uses `M*`/`F*`; synthetic repair audio uses `Ms*`/`Fs*` according to actual synthetic voice gender. | `M1`, `F1`, `Ms1`, `Fs1` |
| `speaker_type` | Acoustic source type. | `human`, `synthetic` |
| `speaker_gender` | Public acoustic-source gender after correction/inference. | `Male`, `Female` |
| `is_synthetic` | Whether this row is synthetic repair audio. | `False`, `True` |
| `synthetic_voice_id` | Synthetic public row label; blank for human rows. | `Ms1`, `Fs1` |
| `repair_target_speaker_id` | Public human target repaired by this synthetic item; blank for human rows. | `M2`, `F4` |
| `repair_target_speaker_gender` | Corrected gender of the repaired human target. | `Male`, `Female` |
| `voice_gender_matches_target` | Whether synthetic voice gender matches target gender. | `True`, `False` |

Rows with `voice_gender_matches_target=False` must be reviewed before public HF release; they are preserved explicitly rather than hidden.
""", encoding="utf-8")

    male_h = ", ".join(r["speaker_id"] for r in human_records if r["speaker_gender"] == "Male")
    female_h = ", ".join(r["speaker_id"] for r in human_records if r["speaker_gender"] == "Female")
    male_s = ", ".join(r["speaker_id"] for r in synthetic_records if r["speaker_gender"] == "Male")
    female_s = ", ".join(r["speaker_id"] for r in synthetic_records if r["speaker_gender"] == "Female")
    split_counts = Counter(r["split"] for r in human_records)
    (output_dir / "speaker_anonymization_preparation_report.md").write_text(f"""# HF Speaker Label Preparation Report

Status: **prepared with corrected gender labels and synthetic voice cross-check**.

- Human male labels: `{male_h}`
- Human female labels: `{female_h}`
- Synthetic male labels: `{male_s}`
- Synthetic female labels: `{female_s}`

Corrections and cross-checks:

- Source metadata rows corrected for public label assignment: **{correction_rows}**.
- Synthetic files whose TTS voice gender does not match the corrected repair-target gender: **{mismatch_files}**.
- Such rows are flagged with `voice_gender_matches_target=False` in `synthetic_repair_targets_public.csv`; regenerate or exclude them before public HF release if strict gender-matched synthetic repair data is required.

Public inventory summary:

- Human labels: {len(human_records)}
- Synthetic repair labels: {len(synthetic_records)}
- Human files represented: {sum(int(r['real_files']) for r in public_rows):,}
- Synthetic files represented: {sum(int(r['synthetic_files']) for r in public_rows):,}
- Total files represented: {sum(int(r['file_count']) for r in public_rows):,}
- Human split speaker counts: train={split_counts.get('train', 0)}, dev={split_counts.get('dev', 0)}, test={split_counts.get('test', 0)}

Private original-name crosswalks are not committed and must not be uploaded to Hugging Face.
""", encoding="utf-8")


def write_private_crosswalk(human_records: list[dict[str, Any]], synth_code: dict[str, str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["original_speaker", "public_speaker_id", "synthetic_public_speaker_id", "speaker_gender", "split", "human_file_count", "synthetic_repair_file_count"]
    with path.open("w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=fields, lineterminator="\n"); w.writeheader()
        for r in human_records:
            name = r["_original_speaker_private"]
            w.writerow({"original_speaker": name, "public_speaker_id": r["speaker_id"], "synthetic_public_speaker_id": synth_code.get(name, ""), "speaker_gender": r["speaker_gender"], "split": r["split"], "human_file_count": r["real_files"], "synthetic_repair_file_count": r["synthetic_repair_files_for_this_target"]})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--split-summary", type=Path, default=DEFAULT_SPLIT_SUMMARY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--private-crosswalk", action="store_true")
    parser.add_argument("--private-crosswalk-path", type=Path, default=DEFAULT_PRIVATE_CROSSWALK)
    args = parser.parse_args()

    split_by = read_split_by_speaker(args.split_summary)
    stats = collect_stats(args.metadata)
    human_code = assign_human_codes(stats["human_stats"])
    synth_code = assign_synthetic_codes(stats["synthetic_targets"])
    human_records = assign_human_records(stats["human_stats"], split_by, human_code)
    synthetic_records, target_records = build_synthetic_records(stats["synthetic_targets"], human_code, synth_code, split_by)
    write_public_outputs(human_records, synthetic_records, target_records, stats["source_voice_counts"], stats["correction_rows"], args.output_dir)
    if args.private_crosswalk:
        write_private_crosswalk(human_records, synth_code, args.private_crosswalk_path)
        print(f"Wrote PRIVATE crosswalk: {args.private_crosswalk_path}")
    print(f"Prepared public speaker-label artifacts in: {args.output_dir}")
    print(f"Labels: human={len(human_records)}, synthetic={len(synthetic_records)}, files={sum(int(r['file_count']) for r in [*human_records, *synthetic_records])}")


if __name__ == "__main__":
    main()
