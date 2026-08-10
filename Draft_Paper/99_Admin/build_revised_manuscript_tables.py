#!/usr/bin/env python3
"""Build editable, scope-qualified tables for the internal NSS-ID manuscript.

All outputs are working artifacts marked NOT FOR SUBMISSION by their package context.
The builder intentionally keeps release-target, frozen-benchmark, and sampled scopes
separate and leaves author-owned facts as explicit material gaps.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from split_schema import canonical_split
DEFAULT_OUTPUT = ROOT / "Draft_Paper" / "04_Revised_Draft" / "tables"
EVIDENCE_PATH = ROOT / "Draft_Paper" / "02_Evidence" / "evidence_registry.json"
REMOTE_FILES_PATH = ROOT / "Draft_Paper" / "02_Evidence" / "hf_dataset_remote_files.json"
TEMPLATE_STATS_PATH = ROOT / "Draft_Paper" / "02_Evidence" / "transcript_template_stats.csv"
TRANSCRIPT_INVENTORY_PATH = (
    ROOT
    / "Draft_Paper"
    / "02_Evidence"
    / "hf_remote_snapshot"
    / "metadata"
    / "transcript_sentence_inventory_public.csv"
)
SYNTHETIC_ROWS_PATH = (
    ROOT
    / "Report_paper_9model"
    / "hf_dataset_information_public"
    / "synthetic_repair_rows_public.csv"
)

CATEGORY_ENGLISH = {
    "Kalimat_Deklaratif": "Declarative",
    "Kalimat_Klarifikasi": "Clarification",
    "Kalimat_Kondisional": "Conditional",
    "Kalimat_Konfirmasi": "Confirmation",
    "Kalimat_Negasi": "Negation",
    "Kalimat_Penjadwalan": "Scheduling",
    "Kalimat_Perintah": "Imperative",
    "Kalimat_Persuasif": "Persuasive",
    "Kalimat_Retoris": "Rhetorical",
    "Kalimat_Seruan": "Exclamatory",
    "Kalimat_Tanya": "Interrogative",
}
ENGLISH_TO_INTERNAL = {value: key for key, value in CATEGORY_ENGLISH.items()}

MODEL_FAMILY = {
    "m02b-whisper-small-ft": "Whisper-small FT",
    "m06-conformer-ctc": "Conformer-CTC",
    "m12-vit-modified-ID": "ViT-modified-ID",
    "m07-bilstm-ctc": "Bi-LSTM CTC",
    "m11-vanilla-transformer": "Vanilla Transformer",
    "m13-wav2letter": "Wav2Letter-style CNN-CTC",
    "m08-hmm-gmm": "HMM-GMM (classical)",
    "m10-gmm-hmm-dnn": "GMM-HMM-DNN (3-stage)",
    "m09-dnn-hmm": "DNN-HMM (hybrid)",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for field in ("split", "target_split"):
            if row.get(field):
                row[field] = canonical_split(row[field])
    return rows


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def remote_entry(entries: list[dict], path: str) -> dict:
    for entry in entries:
        if entry.get("path") == path:
            return entry
    return {}


def build_specifications_table(output_dir: Path) -> None:
    """Build the seven fixed rows required by Data in Brief template v.19."""

    rows = [
        {
            "item": "Subject",
            "description": "Computer Science",
            "evidence_status": "Working classification; author/journal confirmation required",
        },
        {
            "item": "Specific subject area",
            "description": "Automatic speech recognition and curated Indonesian read-speech data",
            "evidence_status": "Supported by corpus content; within the template's 150-character limit",
        },
        {
            "item": "Type of data",
            "description": "Raw PCM WAV audio; processed TAR archives; UTF-8 CSV/TSV/JSON metadata and manifests; analyzed CSV source values; PNG/SVG figures; Python scripts",
            "evidence_status": "Release-package inventory must be frozen and checksummed",
        },
        {
            "item": "Data collection",
            "description": "Repository artifacts organize prompted recordings under 20 retained human public speaker labels and 11 functional categories. The audited build inspected 110,000 source WAVs, retained 19 numbered items per category, zero-padded filenames, and produced 104,500 files; 132 rows are flagged Edge-TTS repairs. Metadata records final audio as 16-kHz mono PCM16. Recruitment, equipment, session, and QC evidence remain open.",
            "evidence_status": "[MATERIAL GAP: participant recruitment and inclusion/exclusion]; [MATERIAL GAP: recording dates and session protocol]; [MATERIAL GAP: verified microphone, interface, operating system, and recording software/version]; [MATERIAL GAP: microphone distance, gain/calibration, monitoring, and prompt presentation]; [MATERIAL GAP: repetition, replacement, re-recording, and rejection rules]",
        },
        {
            "item": "Data source location",
            "description": "Sriwijaya State Polytechnic, Palembang, Indonesia (provisional source-draft assertion)",
            "evidence_status": "Primary collection-location record and approved public geographic granularity remain pending",
        },
        {
            "item": "Data accessibility",
            "description": "Private Hugging Face staging at revision 830a2069416707e3f38c06c507255889513cdf4b; not publicly accessible; licence recorded as other; persistent dataset DOI unavailable",
            "evidence_status": "[MATERIAL GAP: repository, exact version, persistent DOI, direct URL, checksums, and access date]; [MATERIAL GAP: exact dataset licence or component-specific licences]; [MATERIAL GAP: approved controlled-access mechanism, if applicable]",
        },
        {
            "item": "Related research article",
            "description": "R. Atika, S. Dwijayanti, B.Y. Suprapto, Improving speech-to-text for the Indonesian language using a modified transformer, Eastern-European Journal of Enterprise Technologies 1(9 (139)) (2026) 78–90. https://doi.org/10.15587/1729-4061.2026.350949",
            "evidence_status": "Bibliographic record verified; [MATERIAL GAP: related 2026 article citation and data/result overlap assessment] remains open for eligibility determination",
        },
    ]
    write_csv(output_dir / "Specifications_Table.csv", ["item", "description", "evidence_status"], rows)


def build_table_1(output_dir: Path, evidence: dict, remote_files: list[dict]) -> None:
    hf = evidence["hf_repository"]
    metadata = remote_entry(remote_files, "metadata/dataset_metadata_public.csv")
    metadata_sha = metadata.get("lfs", {}).get("sha256", "")
    rows = [
        {
            "component": "Category audio shards",
            "path_or_archive_member": "data/audio_shards/by_category/*.tar",
            "format": "11 TAR archives containing PCM WAV files",
            "rows_or_files": "11 shards / 104500 WAV files",
            "purpose": "Bulk audio delivery by English public category",
            "scope": "Release target",
            "checksum_or_version": f"{hf['audio_tar_bytes']} bytes; per-shard SHA-256 in audio_shards_manifest.csv; HF revision {hf['revision']}",
            "package_state": "Present in private staging; release not authorized",
        },
        {
            "component": "Recording-level metadata",
            "path_or_archive_member": "metadata/dataset_metadata_public.csv",
            "format": "CSV",
            "rows_or_files": str(hf["metadata_rows_at_pinned_revision"]),
            "purpose": "Paths, public IDs, transcript, category, sentence ID, split, duration, audio-format fields, and synthetic provenance",
            "scope": "Release target",
            "checksum_or_version": metadata_sha or f"HF revision {hf['revision']}",
            "package_state": "Present in private staging; repaired metadata has zero blank transcripts",
        },
        {
            "component": "Category transcript lists",
            "path_or_archive_member": "data/transcripts/*.txt",
            "format": "UTF-8 text",
            "rows_or_files": "11 files / 213 distinct (category, sentence_id) pairs",
            "purpose": "Public prompt inventory with stable original IDs",
            "scope": "Release target",
            "checksum_or_version": f"HF revision {hf['revision']}",
            "package_state": "Present in private staging; numbering gaps are intentional",
        },
        {
            "component": "Sentence-ID inventory",
            "path_or_archive_member": "metadata/transcript_sentence_inventory_public.csv",
            "format": "CSV",
            "rows_or_files": "11 category rows",
            "purpose": "Available and intentionally absent original sentence IDs",
            "scope": "Release target",
            "checksum_or_version": f"HF revision {hf['revision']}",
            "package_state": "Present in private staging",
        },
        {
            "component": "Public identifier schema",
            "path_or_archive_member": "metadata/speaker_labels/hf_public_metadata_schema.md",
            "format": "Markdown",
            "rows_or_files": "Field dictionary",
            "purpose": "Defines pseudonymous M/F and synthetic Ms/Fs labels and repair-target fields",
            "scope": "Release target / privacy",
            "checksum_or_version": f"HF revision {hf['revision']}",
            "package_state": "Present; private identity crosswalk excluded",
        },
        {
            "component": "Split manifests",
            "path_or_archive_member": "splits/speaker_split_assignment_public.csv; splits/split_summary_public.json; final row manifests [pending]",
            "format": "CSV/JSON/TSV",
            "rows_or_files": "20 human public IDs; 104500 row assignments in final manifest [pending]",
            "purpose": "Fixed train/development/test assignments",
            "scope": "Release target",
            "checksum_or_version": "Seed 42 recorded; [MATERIAL GAP: split-generation algorithm, candidate order, library/version, and exact assignments]",
            "package_state": "Summary present; publication-grade generator and immutable row manifests pending",
        },
        {
            "component": "Synthetic repair manifest",
            "path_or_archive_member": "paper/dataset_information/synthetic_repair_rows_public.csv",
            "format": "CSV",
            "rows_or_files": "132 rows",
            "purpose": "Allows synthetic rows to be identified and filtered",
            "scope": "Release target",
            "checksum_or_version": f"HF revision {hf['revision']}",
            "package_state": "Present; disposition of two source/target mismatches pending",
        },
        {
            "component": "Descriptive source values",
            "path_or_archive_member": "paper/dataset_information/*.csv; paper/dataset_information/*.json",
            "format": "CSV/JSON",
            "rows_or_files": "Category, split, speaker, synthetic, lexical, and 297-file sampled diagnostic values",
            "purpose": "Editable tables and reproducible figure inputs",
            "scope": "Release target or sampled diagnostics, explicitly labelled",
            "checksum_or_version": f"HF revision {hf['revision']}",
            "package_state": "Partly present; regenerated main-figure source package pending",
        },
        {
            "component": "Frozen benchmark artifacts",
            "path_or_archive_member": "Draft_Paper/02_Evidence/unified_benchmark_rescore/; Report_paper_9model/benchmark/benchmark.json; model cards",
            "format": "CSV/JSON/Markdown/model artifacts",
            "rows_or_files": "9 uniformly rescored prediction records / 102544-audio-row benchmark",
            "purpose": "Seen-script, held-out-human-speaker technical validation; run-native metrics retained only as provenance",
            "scope": "Frozen benchmark",
            "checksum_or_version": "Prediction hashes recorded; benchmark manifest hashes pending; [MATERIAL GAP: exact benchmark template-overlap audit]",
            "package_state": "Uniform rescore present; per-recipe method cards and final supplement/checksum package pending",
        },
        {
            "component": "Validation and reproduction scripts",
            "path_or_archive_member": "scripts/ and manuscript-facing audit scripts [final paths pending]",
            "format": "Python/shell",
            "rows_or_files": "Multiple scripts",
            "purpose": "Rebuild statistics, figures, integrity checks, and benchmark summaries",
            "scope": "All scopes",
            "checksum_or_version": "Pending: frozen code revision and environment lockfiles.",
            "package_state": "Local scripts exist; final minimal release bundle pending",
        },
        {
            "component": "Package checksum manifest",
            "path_or_archive_member": "checksums/SHA256SUMS [planned]",
            "format": "Text/CSV",
            "rows_or_files": "One record per deposited artifact",
            "purpose": "Immutable release verification",
            "scope": "Final deposit",
            "checksum_or_version": "Pending: final archive checksums; see the canonical repository/version/checksum gate.",
            "package_state": "Not yet generated because the release package is not frozen",
        },
    ]
    write_csv(
        output_dir / "Table_1_package_inventory.csv",
        [
            "component",
            "path_or_archive_member",
            "format",
            "rows_or_files",
            "purpose",
            "scope",
            "checksum_or_version",
            "package_state",
        ],
        rows,
    )


def build_table_2(output_dir: Path, evidence: dict) -> None:
    release = evidence["release_target_dataset"]
    benchmark = evidence["benchmark_subset"]
    bridge = evidence["scope_bridge"]
    rows = [
        {"field": "Files", "release_target": release["file_count"], "frozen_benchmark": benchmark["file_count"], "evidence_control": "Distinct current release-target and frozen-benchmark scopes"},
        {"field": "Duration (h)", "release_target": release["duration_hours"], "frozen_benchmark": benchmark["duration_hours"], "evidence_control": "Computed within each scope"},
        {"field": "Train / development / test files", "release_target": "73150 / 15675 / 15675", "frozen_benchmark": "71792 / 15376 / 15376", "evidence_control": "Do not substitute one split definition for the other"},
        {"field": "Human recordings", "release_target": release["human_recordings"], "frozen_benchmark": "102412", "evidence_control": "Frozen scope contains the same 132 synthetic rows"},
        {"field": "Synthetic repairs", "release_target": release["synthetic_recordings"], "frozen_benchmark": benchmark["synthetic_files"], "evidence_control": "Synthetic provenance must remain explicit"},
        {"field": "Human speakers", "release_target": release["human_speakers"], "frozen_benchmark": "20", "evidence_control": "Human public IDs are partition-disjoint; TTS voice identity is not guaranteed disjoint"},
        {"field": "Distinct (category, sentence_id) pairs", "release_target": release["distinct_category_sentence_pairs"], "frozen_benchmark": benchmark["local_source_validation"]["distinct_category_sentence_pairs"], "evidence_control": "Pairs are not asserted to be globally unique transcript texts"},
        {"field": "Transcript state", "release_target": "Repaired private HF metadata: 0 blank transcript fields", "frozen_benchmark": "Frozen before transcript repair; excludes rows blank at freeze time", "evidence_control": "Audio shards did not change during metadata repair"},
        {"field": "Rows present only in release target", "release_target": bridge["rows_present_in_release_target_but_not_benchmark"], "frozen_benchmark": "0 (excluded)", "evidence_control": "1956-row repair bridge requires an immutable publication attachment"},
        {"field": "Test composition", "release_target": "15675 items = 15673 human + 2 synthetic", "frozen_benchmark": "15376 items = 15374 human + 2 synthetic", "evidence_control": "Do not call every test item human"},
        {"field": "Intended role in article", "release_target": "Corpus description, package, provenance, and reuse", "frozen_benchmark": "Nine-model technical validation only", "evidence_control": "Benchmark does not validate every release-target row"},
        {"field": "Availability", "release_target": "Private HF staging; licence other; persistent DOI unavailable", "frozen_benchmark": "Local frozen evidence package; deposit mapping pending", "evidence_control": "Neither scope is presently submission-compliant public data"},
    ]
    write_csv(output_dir / "Table_2_scope_bridge.csv", ["field", "release_target", "frozen_benchmark", "evidence_control"], rows)


def build_table_3(output_dir: Path, evidence: dict) -> None:
    release = evidence["release_target_dataset"]
    template_rows = {row["category"]: row for row in load_csv(TEMPLATE_STATS_PATH)}
    inventory_rows = {row["category"]: row for row in load_csv(TRANSCRIPT_INVENTORY_PATH)}
    replacements: dict[str, list[dict]] = defaultdict(list)
    for item in release["partial_replacement_sentence_pairs"]:
        replacements[CATEGORY_ENGLISH[item["category"]]].append(item)

    rows = []
    for source in release["category_rows"]:
        internal = source["category"]
        english = CATEGORY_ENGLISH[internal]
        template = template_rows[english]
        inventory = inventory_rows[english]
        if replacements.get(english):
            detail = ", ".join(f"{item['sentence_id']}={item['rows']} rows" for item in replacements[english])
            note = f"Partial replacement pair: {detail}; stable original IDs retained"
        elif inventory["intentionally_absent_sentence_ids"] != "none":
            note = f"Intentional original-ID gap: {inventory['intentionally_absent_sentence_ids']}; do not renumber"
        else:
            note = "Complete original IDs 01–20"
        rows.append(
            {
                "category_english": english,
                "source_category_label": internal,
                "files": source["file_count"],
                "duration_hours": source["duration_hours"],
                "mean_duration_sec": source["mean_duration_sec"],
                "synthetic_files": source["synthetic_files"],
                "distinct_category_sentence_id_pairs": template["templates"],
                "sentence_id_note": note,
                "scope": "Release target (104500 files)",
            }
        )
    rows.sort(key=lambda row: row["category_english"])
    write_csv(
        output_dir / "Table_3_release_target_category_composition.csv",
        [
            "category_english",
            "source_category_label",
            "files",
            "duration_hours",
            "mean_duration_sec",
            "synthetic_files",
            "distinct_category_sentence_id_pairs",
            "sentence_id_note",
            "scope",
        ],
        rows,
    )


def build_table_4(output_dir: Path, evidence: dict) -> None:
    release = evidence["release_target_dataset"]
    speaker_rows = load_csv(ROOT / "Report_paper_9model" / "hf_dataset_information_public" / "per_speaker_public.csv")
    human_by_split: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in speaker_rows:
        if row["speaker_type"].lower() == "human":
            human_by_split[row["split"]].append(row)

    notes = {
        "train": "Six male-label and eight female-label natural human speakers; synthetic repairs are explicitly flagged.",
        "val": "Three male-label natural human speakers; zero female-source files and no natural female evaluation speaker.",
        "test": "Three male-label natural human speakers; the two female-source files are synthetic, target M8, and remain an unresolved mismatch; no natural female evaluation speaker.",
    }
    rows = []
    for source in release["split_rows"]:
        split = canonical_split(source["split"])
        humans = human_by_split[split]
        gender_counts = Counter(row["speaker_gender"] for row in humans)
        total_files = int(source["file_count"])
        synthetic_files = int(source["synthetic_files"])
        rows.append(
            {
                "split": split,
                "human_speakers": len(humans),
                "human_speaker_labels_male_female": f"{gender_counts.get('Male', 0)} / {gender_counts.get('Female', 0)}",
                "files": total_files,
                "human_recordings": total_files - synthetic_files,
                "synthetic_files": synthetic_files,
                "duration_hours": source["duration_hours"],
                "male_source_files": source["male_source_files"],
                "female_source_files": source["female_source_files"],
                "interpretation_note": notes[split],
                "scope": "Release target",
            }
        )
    rows.append(
        {
            "split": "Total",
            "human_speakers": release["human_speakers"],
            "human_speaker_labels_male_female": "12 / 8",
            "files": release["file_count"],
            "human_recordings": release["human_recordings"],
            "synthetic_files": release["synthetic_recordings"],
            "duration_hours": release["duration_hours"],
            "male_source_files": sum(int(row["male_source_files"]) for row in release["split_rows"]),
            "female_source_files": sum(int(row["female_source_files"]) for row in release["split_rows"]),
            "interpretation_note": "Public labels are pseudonymous. [MATERIAL GAP: sex/gender label definition and provenance]. This partition is unsuitable for gender-balanced evaluation.",
            "scope": "Release target",
        }
    )
    write_csv(
        output_dir / "Table_4_release_target_split_source_composition.csv",
        [
            "split",
            "human_speakers",
            "human_speaker_labels_male_female",
            "files",
            "human_recordings",
            "synthetic_files",
            "duration_hours",
            "male_source_files",
            "female_source_files",
            "interpretation_note",
            "scope",
        ],
        rows,
    )


def build_table_5(output_dir: Path, evidence: dict) -> None:
    release = evidence["release_target_dataset"]
    synthetic_rows = load_csv(SYNTHETIC_ROWS_PATH)
    total_duration = sum(float(row["duration_sec"]) for row in synthetic_rows)
    split_counts = Counter(row["split"] for row in synthetic_rows)
    category_counts = Counter(row["category"] for row in synthetic_rows)
    gender_counts = Counter(row["speaker_gender"] for row in synthetic_rows)
    mismatch_count = sum(row["voice_gender_matches_target"].lower() == "false" for row in synthetic_rows)
    rows = [
        {
            "dimension": "Total",
            "value": "Synthetic repairs",
            "files": len(synthetic_rows),
            "duration_sec": f"{total_duration:.4f}",
            "percent_of_release_target": f"{release['synthetic_fraction_percent']:.4f}",
            "note": "All rows must remain explicitly filterable; totals may change after mismatch disposition.",
            "source_scope": "Release target",
        },
        {
            "dimension": "Generation",
            "value": "Edge-TTS neural voices",
            "files": len(synthetic_rows),
            "duration_sec": "",
            "percent_of_release_target": "",
            "note": "Documented voice IDs: id-ID-ArdiNeural and id-ID-GadisNeural; [MATERIAL GAP: Edge-TTS version/date/configuration and redistribution-rights review].",
            "source_scope": "Release target",
        },
        {
            "dimension": "Generation assertion",
            "value": "No-cloning statement",
            "files": "",
            "duration_sec": "",
            "percent_of_release_target": "",
            "note": "The source author draft states that speaker cloning was not used; an immutable generation log and technical confirmation remain pending.",
            "source_scope": "Source-draft assertion; not a measured release-target count",
        },
        {
            "dimension": "Voice source",
            "value": "Male-source",
            "files": gender_counts["Male"],
            "duration_sec": "",
            "percent_of_release_target": "",
            "note": "Acoustic TTS voice source, not the sex/gender of a human participant.",
            "source_scope": "Release target",
        },
        {
            "dimension": "Voice source",
            "value": "Female-source",
            "files": gender_counts["Female"],
            "duration_sec": "",
            "percent_of_release_target": "",
            "note": "Acoustic TTS voice source, not the sex/gender of a human participant.",
            "source_scope": "Release target",
        },
    ]
    for split in ("train", "val", "test"):
        rows.append(
            {
                "dimension": "Split",
                "value": split,
                "files": split_counts[split],
                "duration_sec": "",
                "percent_of_release_target": "",
                "note": "Synthetic rows occur in this partition.",
                "source_scope": "Release target",
            }
        )
    for internal, count in sorted(category_counts.items(), key=lambda item: CATEGORY_ENGLISH[item[0]]):
        rows.append(
            {
                "dimension": "Category",
                "value": CATEGORY_ENGLISH[internal],
                "files": count,
                "duration_sec": "",
                "percent_of_release_target": "",
                "note": "English public category name.",
                "source_scope": "Release target",
            }
        )
    rows.extend(
        [
            {
                "dimension": "Mismatch",
                "value": "Female-source / male-target",
                "files": mismatch_count,
                "duration_sec": f"{sum(float(row['duration_sec']) for row in synthetic_rows if row['voice_gender_matches_target'].lower() == 'false'):.4f}",
                "percent_of_release_target": "",
                "note": "Targets public label M8; [MATERIAL GAP: disposition of two female-source/male-target synthetic rows].",
                "source_scope": "Release target / unresolved",
            },
            {
                "dimension": "Filtering",
                "value": "is_synthetic and provenance fields",
                "files": len(synthetic_rows),
                "duration_sec": "",
                "percent_of_release_target": "",
                "note": "Users can exclude synthetic rows with is_synthetic and inspect source/target fields.",
                "source_scope": "Release target",
            },
        ]
    )
    write_csv(
        output_dir / "Table_5_synthetic_repair_provenance.csv",
        ["dimension", "value", "files", "duration_sec", "percent_of_release_target", "note", "source_scope"],
        rows,
    )


def build_table_6(output_dir: Path, evidence: dict) -> None:
    """Build the compact main-text table from the uniform diagnostic rescore.

    Run-native metrics and their historical rank remain provenance-only in the
    evidence registry because they used non-identical reference normalization.
    """

    benchmark = evidence["benchmark_subset"]
    rows = [
        {
            "model_family": MODEL_FAMILY[model["model_id"]],
            "wer_percent": f"{model['wer'] * 100:.3f}",
            "cer_percent": f"{model['cer'] * 100:.3f}",
            "parameters": model["parameters"],
        }
        for model in benchmark["models"]
    ]
    rows.sort(key=lambda row: row["model_family"])
    write_csv(
        output_dir / "Table_S6_frozen_benchmark_validation.csv",
        ["model_family", "wer_percent", "cer_percent", "parameters"],
        rows,
    )


def build_all(output_dir: Path) -> None:
    evidence = load_json(EVIDENCE_PATH)
    remote_files = load_json(REMOTE_FILES_PATH)
    output_dir.mkdir(parents=True, exist_ok=True)
    build_specifications_table(output_dir)
    build_table_1(output_dir, evidence, remote_files)
    build_table_2(output_dir, evidence)
    build_table_3(output_dir, evidence)
    build_table_4(output_dir, evidence)
    build_table_5(output_dir, evidence)
    build_table_6(output_dir, evidence)
    print(f"Wrote 7 editable CSV tables to {output_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_all(args.output_dir.resolve())


if __name__ == "__main__":
    main()
