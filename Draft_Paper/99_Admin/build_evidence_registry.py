#!/usr/bin/env python3
"""Build a public-safe evidence registry from authoritative project artifacts."""
from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from split_schema import canonical_split
OUT = ROOT / "Draft_Paper" / "02_Evidence"
ROBOT_OOD = Path(
    os.environ.get(
        "NSSID_ROBOT_OOD_JSON",
        str(ROOT.parent / "deploy_robot_asr/deploy_dual_model_web/analysis/live_ood_aggregate.json"),
    )
)


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def read_csv(relative: str) -> list[dict[str, str]]:
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def aggregate_metadata(relative: str) -> dict:
    rows = 0
    duration = 0.0
    blanks = 0
    synthetic = 0
    categories = Counter()
    sentence_pairs = Counter()
    formats = Counter()
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            rows += 1
            duration += float(row["duration_sec"])
            blanks += int(not row["transcript"].strip())
            synthetic += int(row["is_synthetic"].strip().lower() == "true")
            categories[row["category"]] += 1
            sentence_pairs[(row["category"], str(row["sentence_id"]).zfill(2))] += 1
            formats[(int(row["sample_rate"]), int(row["num_channels"]), int(row["bits_per_sample"]))] += 1
    return {
        "rows": rows,
        "duration_hours": round(duration / 3600.0, 4),
        "blank_transcripts": blanks,
        "synthetic_rows": synthetic,
        "category_count": len(categories),
        "category_rows": dict(sorted(categories.items())),
        "distinct_category_sentence_pairs": len(sentence_pairs),
        "non_500_row_sentence_pairs": [
            {"category": key[0], "sentence_id": key[1], "rows": count}
            for key, count in sorted(sentence_pairs.items()) if count != 500
        ],
        "audio_formats": [
            {"sample_rate": key[0], "channels": key[1], "bits_per_sample": key[2], "rows": count}
            for key, count in formats.items()
        ],
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    full_local = aggregate_metadata("metadata/dataset_metadata.csv")
    clean_local = aggregate_metadata("metadata/dataset_metadata_clean.csv")
    full_public = load_json("Report_paper_9model/hf_dataset_information_public/dataset_stats_public.json")
    synthetic_public = load_json("Report_paper_9model/hf_dataset_information_public/synthetic_data_stats_public.json")
    split_public = read_csv("Report_paper_9model/hf_dataset_information_public/per_split_public.csv")
    category_public = read_csv("Report_paper_9model/hf_dataset_information_public/per_category_public.csv")
    speaker_public = read_csv("Report_paper_9model/hf_dataset_information_public/per_speaker_public.csv")
    clean_stats = load_json("reports/dataset_statistics_v7_paper9/stats/dataset_stats.json")
    clean_stats["splits"] = {
        canonical_split(split): values
        for split, values in clean_stats["splits"].items()
    }
    benchmark = load_json("Report_paper_9model/benchmark/benchmark.json")
    interpretation = load_json("Report_paper_9model/data/paper_9model_interpretation_metrics.json")
    unified_rescore = load_json(
        "Draft_Paper/02_Evidence/unified_benchmark_rescore/unified_nine_model_metrics.json"
    )
    hf_remote = load_json("Draft_Paper/02_Evidence/hf_dataset_remote_info.json")
    hf_files_data = load_json("Draft_Paper/02_Evidence/hf_dataset_remote_files.json")
    hf_card = load_json("Draft_Paper/02_Evidence/hf_dataset_card_metadata.json")
    ood = json.loads(ROBOT_OOD.read_text(encoding="utf-8"))
    colab_smoke = load_json(
        "training_conventional/m12_vit_modified/runs/run_1epoch_colab-cli_20260619_112212_l4_test/colab_cli_summary.json"
    )

    hf_items = hf_files_data if isinstance(hf_files_data, list) else hf_files_data.get("items", hf_files_data.get("files", []))
    shard_items = [item for item in hf_items if isinstance(item, dict) and str(item.get("path", "")).endswith(".tar")]
    human_speakers = [row for row in speaker_public if row["speaker_type"] == "human"]
    synthetic_speakers = [row for row in speaker_public if row["speaker_type"] == "synthetic"]
    human_gender = Counter(row["speaker_gender"] for row in human_speakers)
    synthetic_gender = Counter(row["speaker_gender"] for row in synthetic_speakers)

    run_native_ranked = []
    for item in benchmark["paper_models_ranked_by_wer"]:
        run_native_ranked.append(
            {
                "rank": item["rank"],
                "model_id": item["model_id"],
                "family": item["family"],
                "wer": item["wer"],
                "cer": item["cer"],
                "training_time_hours": item.get("training_time_hours"),
                "inference_time_sec": item.get("inference_time_sec"),
                "parameters": item.get("n_params"),
                "hardware_label": item.get("hardware_label"),
                "metric_status": "run-native; non-identical reference normalization/denominators; not publication-comparable",
            }
        )

    uniform_models = [
        {
            "model_id": item["model_id"],
            "family": item["model_family"],
            "normalizer_id": item["normalizer_id"],
            "n_test_items": item["n_test_items"],
            "reference_words": item["reference_words"],
            "word_errors": item["word_errors"],
            "wer": item["wer"],
            "reference_characters": item["reference_characters"],
            "character_errors": item["character_errors"],
            "cer": item["cer"],
            "parameters": item["parameters"],
            "predictions_sha256": item["predictions_sha256"],
            "metric_status": "uniform diagnostic rescore of existing predictions",
        }
        for item in unified_rescore["models"]
    ]

    registry = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_policy": {
            "tier_a": "Full 104,500-row release-target metadata and private HF staging artifacts",
            "tier_b": "Frozen 102,544-row benchmark subset and nine-model test artifacts",
            "tier_c": "Sampled acoustic/figure diagnostics",
            "tier_d": "Local deployment/OOD diagnostics; not publication accuracy",
            "tier_e": "Older narrative drafts; require cross-check",
        },
        "release_target_dataset": {
            "scope": "104,500 release-target audio rows; local pre-repair metadata snapshot plus repaired private HF staging metadata",
            "local_pre_repair_metadata_snapshot": full_local,
            "file_count": full_public["file_count"],
            "human_recordings": full_public["human_real_files"],
            "synthetic_recordings": full_public["synthetic_files"],
            "synthetic_fraction_percent": round(100.0 * full_public["synthetic_files"] / full_public["file_count"], 4),
            "duration_hours": full_public["duration_hours_total"],
            "human_speakers": len(human_speakers),
            "human_gender_counts_corrected": dict(human_gender),
            "synthetic_voice_labels": len(synthetic_speakers),
            "synthetic_label_gender_counts": dict(synthetic_gender),
            "categories": 11,
            "distinct_category_sentence_pairs": full_local["distinct_category_sentence_pairs"],
            "partial_replacement_sentence_pairs": full_local["non_500_row_sentence_pairs"],
            "word_types_release_target_normalization": full_public["word_type_count"],
            "split_rows": split_public,
            "category_rows": category_public,
            "synthetic_details": synthetic_public,
            "audio_quality_sample_rows": full_public["audio_quality_sample_rows"],
            "audio_quality_scope": "297 sampled files; sampling frame, allocation, seed, and inclusion criteria require attached provenance; not a full-corpus scan",
            "source_artifacts": [
                "metadata/dataset_metadata.csv",
                "Report_paper_9model/hf_dataset_information_public/dataset_stats_public.json",
                "Report_paper_9model/hf_dataset_information_public/per_split_public.csv",
                "Report_paper_9model/hf_dataset_information_public/per_category_public.csv",
                "Report_paper_9model/hf_dataset_information_public/per_speaker_public.csv",
                "Report_paper_9model/HF_DATASET_INFORMATION_FINAL_REPORT.md",
            ],
        },
        "hf_repository": {
            "repo_id": hf_remote.get("id"),
            "revision": hf_remote.get("sha"),
            "private": hf_remote.get("private"),
            "access_status": "private staging; not publicly accessible",
            "persistent_dataset_doi_available": False,
            "card_license": hf_card.get("license"),
            "remote_file_entries": len(hf_items),
            "audio_tar_shards": len(shard_items),
            "audio_tar_bytes": sum(int(item.get("size", 0)) for item in shard_items),
            "public_category_names": [
                "Clarification", "Conditional", "Confirmation", "Declarative", "Exclamatory", "Imperative",
                "Interrogative", "Negation", "Persuasive", "Rhetorical", "Scheduling",
            ],
            "metadata_rows_at_pinned_revision": 104500,
            "blank_transcripts_after_repair": 0,
            "numbering_policy": "Original 01-20 collection IDs are preserved; documented gaps must not be renumbered.",
            "source_artifacts": [
                "Draft_Paper/02_Evidence/hf_dataset_remote_info.json",
                "Draft_Paper/02_Evidence/hf_dataset_remote_files.json",
                "reports/hf_transcript_cleanup_execution_20260618.md",
                "reports/hf_transcript_numbering_note_20260618.md",
                "reports/hf_english_category_rename_20260619.md",
            ],
        },
        "benchmark_subset": {
            "scope": "Frozen clean subset used by all nine paper models",
            "local_source_validation": clean_local,
            "file_count": clean_stats["corpus"]["n_files"],
            "duration_hours": clean_stats["corpus"]["total_hours"],
            "train_files": clean_stats["splits"]["train"]["n_files"],
            "val_files": clean_stats["splits"]["val"]["n_files"],
            "test_files": clean_stats["splits"]["test"]["n_files"],
            "test_speakers": clean_stats["splits"]["test"]["n_speakers"],
            "speaker_disjoint": True,
            "text_template_disjoint": False,
            "test_transcripts_seen_in_train": "100% of val/test rows; 206 unique test templates are represented in train",
            "synthetic_files": clean_stats["synthetic"]["n_files"],
            "synthetic_test_files": clean_stats["splits"]["test"]["n_synthetic"],
            "publication_metric_source": "Draft_Paper/02_Evidence/unified_benchmark_rescore/unified_nine_model_metrics.json",
            "uniform_normalizer_id": unified_rescore["normalizer_id"],
            "uniform_metric_definition": unified_rescore["metric_definition"],
            "models": uniform_models,
            "models_run_native": run_native_ranked,
            "run_native_metric_comparability": "Run-native WER/CER used non-identical reference normalizations and denominators across recipes; the historical run-native ranking is not comparable and must not be used for publication claims.",
            "historical_run_native_best_model": {
                **{
                    key: interpretation["best_model"].get(key)
                    for key in ("rank", "model_id", "family", "wer", "cer", "n_params", "training_time_hhmmss", "inference_time_sec", "n_test_samples", "decoding_method")
                },
                "metric_status": "historical run-native interpretation only; do not use as publication ranking",
            },
            "historical_run_native_novel_model": {
                **{
                    key: interpretation["novel_model"].get(key)
                    for key in ("rank", "model_id", "family", "wer", "cer", "n_params", "training_time_hhmmss", "inference_time_sec", "n_test_samples", "decoding_method")
                },
                "metric_status": "historical run-native interpretation only; do not use as publication ranking",
            },
            "source_artifacts": [
                "metadata/dataset_metadata_clean.csv",
                "splits/train_clean.tsv", "splits/val_clean.tsv", "splits/test_clean.tsv",
                "Report_paper_9model/benchmark/benchmark.json",
                "Report_paper_9model/data/paper_9model_interpretation_metrics.json",
                "Draft_Paper/02_Evidence/unified_benchmark_rescore/unified_nine_model_metrics.csv",
                "Draft_Paper/02_Evidence/unified_benchmark_rescore/unified_nine_model_metrics.json",
            ],
        },
        "scope_bridge": {
            "rows_present_in_release_target_but_not_benchmark": full_local["rows"] - clean_local["rows"],
            "reason": "The frozen benchmark subset excluded 1,956 rows with blank transcript values in the local metadata snapshot at benchmark freeze time. It therefore contains 209 distinct (category, sentence_id) pairs. The repaired private HF staging metadata retains those rows and four low-count replacement sentence IDs, yielding 213 distinct (category, sentence_id) pairs without changing audio shards.",
            "publication_rule": "Report release-target descriptive statistics and 213 distinct (category, sentence_id) pairs on 104,500 rows; report the 209-pair nine-model benchmark only on the frozen 102,544-row subset. Do not imply public accessibility until ethics, consent, rights, licence, and DOI gates pass.",
        },
        "reproducibility": {
            "hf_audio_shards": 11,
            "nine_model_artifacts_present": benchmark["n_paper_models_present"],
            "m12_colab_smoke_returncode": colab_smoke["returncode"],
            "m12_colab_smoke_gpu": "NVIDIA L4",
            "m12_colab_smoke_train_samples": 256,
            "m12_colab_smoke_validation_samples": 64,
            "m12_colab_smoke_scope": "one-epoch execution smoke test only; not a performance result",
            "public_figure_audits": [
                "reports/elsevier_figure_readability_revision_20260619.md",
                "reports/public_artifact_anonymization_cleanup_20260619.md",
            ],
        },
        "sampled_diagnostics": {
            "audio_quality_rows": 297,
            "quality_metrics": ["dynamic range", "silence ratio", "spectral centroid"],
            "spectrogram_categories": 11,
            "scope_warning": "Do not describe the n=297 sample as a full 104,500-file quality scan.",
        },
        "deployment_ood_diagnostics": {
            "recordings": ood["recordings"]["unique_canonical"],
            "distinct_commands": ood["recordings"]["distinct_inferred_templates"],
            "robot_default_agreement": ood["profiles"]["vit_sota_arch"]["gradio_default"]["exact_template_accuracy"],
            "robot_no_preemphasis_agreement": ood["profiles"]["vit_sota_arch"]["no_trim_no_preemphasis"]["exact_template_accuracy"],
            "paper_default_agreement": ood["profiles"]["vit_paper_dataset_sota"]["gradio_default"]["exact_template_accuracy"],
            "paper_no_preemphasis_agreement": ood["profiles"]["vit_paper_dataset_sota"]["no_trim_no_preemphasis"]["exact_template_accuracy"],
            "status": "development-only, Whisper-inferred references, reused recordings",
            "publication_rule": "Use only to motivate a generalization limitation or future validation protocol; do not report as field accuracy.",
            "source_artifact": "deploy_robot_asr/deploy_dual_model_web/ANALYSIS_LIVE_OOD_20260714.md",
        },
        "privacy": {
            "human_public_labels": "M1..M12 and F1..F8",
            "synthetic_public_labels": "Ms1..Ms9 and Fs1..Fs9",
            "private_crosswalk_location": "outside Git/HF; never include in manuscript package",
            "public_name_leak_audit_errors": 0,
            "synthetic_voice_target_gender_mismatch_files": full_public["synthetic_voice_target_gender_mismatch_files"],
        },
        "material_gaps": [
            "Final dataset DOI or another persistent archive DOI is not available.",
            "HF repository is private; Data in Brief accessibility must be resolved before submission.",
            "Dataset licence is recorded only as 'other'; exact reuse terms require author/legal confirmation.",
            "Ethics committee name, approval/reference number, and approval date are unverified.",
            "Written consent scope for public release of identifiable voice biometrics is unverified.",
            "Participant age range conflicts across old drafts and has no authoritative public-safe source.",
            "The claim that every speaker read every sentence exactly 25 times must be revised: four categories contain paired low-count replacement sentence IDs, and the release-target inventory has 213 rather than 209 distinct (category, sentence_id) pairs.",
            "Regional-origin/dialect claims require a consent/privacy decision and a verified public-safe table.",
            "Recording-room dimensions conflict between narrative text and embedded diagrams.",
            "Microphone model, acquisition distance, Audacity version, and room protocol require author confirmation against primary records.",
            "Corresponding-author email, CRediT roles, funding statement, and competing-interest confirmation require author approval.",
            "Two synthetic female-voice recordings target a male public speaker label; authors must decide whether to regenerate, exclude, or retain them with an explicit mismatch flag.",
            "Prior-publication overlap with the related 2026 article and third-party redistribution rights require verification.",
            "A whole-package release leakage audit and lifecycle governance record are not yet available.",
            "The transcript-repair algorithm, immutable repair manifest, and audio-text validation audit are not yet publication-attached.",
            "The exact benchmark template-overlap audit and the 297-file sampling design must be attached before final sign-off.",
        ],
    }

    (OUT / "evidence_registry.json").write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    claims = [
        ("C001", "Release-target corpus contains 104,500 audio rows", "release_target", "verified", "metadata/dataset_metadata.csv direct row-level audit; dataset_stats_public.json"),
        ("C002", "Release-target duration is 134.1762 h", "release_target", "verified", "metadata/dataset_metadata.csv direct row-level audit; dataset_stats_public.json"),
        ("C003", "Release target contains 104,368 human and 132 synthetic recordings", "release_target", "verified", "dataset_stats_public.json"),
        ("C004", "Release target contains 20 retained human public speaker labels: 12 male and 8 female after metadata correction; participant uniqueness and label provenance remain unverified", "release_target", "verified label counts; participant uniqueness/provenance gap", "per_speaker_public.csv; HF final report; METHODS_EVIDENCE_MATRIX.csv"),
        ("C005", "Release-target metadata has 11 categories and 213 distinct (category, sentence_id) pairs", "release_target", "verified", "metadata/dataset_metadata.csv direct row-level inventory; transcript_template_stats.csv"),
        ("C005B", "Frozen benchmark subset has 209 distinct (category, sentence_id) pairs", "benchmark", "verified", "dataset_metadata_clean.csv direct row-level inventory; dataset_stats.json"),
        ("C006", "All 104,500 release-target metadata rows report 16 kHz, mono, PCM16 audio", "release_target", "verified metadata audit", "metadata/dataset_metadata.csv direct 104,500-row audit via build_evidence_registry.py; package a direct audio-header audit before submission"),
        ("C007", "Pinned private HF metadata has zero blank transcripts after repair", "HF_private_staging", "revision-pinned", "hf_transcript_cleanup_execution report; pinned private HF revision"),
        ("C008", "Private HF staging uses 11 English-category tar shards", "HF_private_staging", "revision-pinned", "remote file listing; English rename report"),
        ("C009", "Benchmark subset has 102,544 files and 130.6548 h", "benchmark", "verified", "dataset_metadata_clean.csv; dataset_stats.json"),
        ("C010", "Nine models were evaluated on a 15,376-item speaker-separated test split containing 15,374 human recordings and 2 synthetic repairs", "benchmark", "verified", "benchmark.json; dataset_stats.json; synthetic_data_stats_public.json"),
        ("C011", "Under the uniform project normalizer, existing Whisper-small FT predictions rescore to WER 0.0018615/CER 0.0014014", "benchmark", "verified uniform diagnostic rescore", "unified_nine_model_metrics.json; canonical test manifest; hashed prediction CSV"),
        ("C012", "Under the uniform project normalizer, existing ViT-modified-ID predictions rescore to WER 0.0176145/CER 0.0129790", "benchmark", "verified uniform diagnostic rescore", "unified_nine_model_metrics.json; canonical test manifest; hashed prediction CSV"),
        ("C012B", "Historical run-native nine-model WER/CER values used non-identical reference normalization and denominators", "benchmark", "verified comparability defect; historical ranking prohibited", "uniform rescore audit; prediction-label denominator audit; benchmark.json retained as provenance"),
        ("C013", "Benchmark measures held-out human speakers reading seen scripts", "benchmark", "registry-backed limitation; audit attachment required", "split manifests; attach the exact template-overlap audit before final sign-off"),
        ("C014", "Audio-quality diagnostics were computed for 297 sampled rows", "sample", "verified sample count; sampling design pending", "dataset_stats_public.json; audio_quality_sample_public.csv; attach sampling frame/allocation/seed"),
        ("C015", "Dataset is publicly accessible with DOI", "access", "not supported", "HF private; DOI absent"),
        ("C016", "Ethics and public-release consent are complete", "ethics", "material gap", "old declarations contain placeholders"),
        ("C017", "Open-microphone field accuracy is established", "deployment", "must not claim", "development-only OOD audit"),
    ]
    with (OUT / "claim_evidence_matrix.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["claim_id", "claim", "scope", "status", "evidence"])
        writer.writerows(claims)

    lines = [
        "# Authoritative evidence registry", "",
        "## Scope and access rule", "",
        f"- Release-target corpus: **{registry['release_target_dataset']['file_count']:,} files / {registry['release_target_dataset']['duration_hours']:.4f} h**.",
        f"- Frozen benchmark subset: **{registry['benchmark_subset']['file_count']:,} files / {registry['benchmark_subset']['duration_hours']:.4f} h**.",
        f"- Difference: **{registry['scope_bridge']['rows_present_in_release_target_but_not_benchmark']:,} rows**; see scope bridge in JSON.",
        "- The release target is not currently public: HF staging is private, the licence is `other`, and no persistent dataset DOI is available.",
        "- Deployment/OOD diagnostics are development evidence only.", "",
        "## Release-target corpus and private HF staging", "",
        f"- Human recordings: {registry['release_target_dataset']['human_recordings']:,}; synthetic: {registry['release_target_dataset']['synthetic_recordings']} ({registry['release_target_dataset']['synthetic_fraction_percent']:.4f}%).",
        f"- Human speakers: 20 ({human_gender['Male']} male, {human_gender['Female']} female).",
        f"- Distinct `(category, sentence_id)` pairs: {registry['release_target_dataset']['distinct_category_sentence_pairs']}; frozen benchmark pairs: {registry['benchmark_subset']['local_source_validation']['distinct_category_sentence_pairs']}.",
        f"- HF revision: `{registry['hf_repository']['revision']}`; private: `{registry['hf_repository']['private']}`; licence: `{registry['hf_repository']['card_license']}`; persistent DOI available: `{registry['hf_repository']['persistent_dataset_doi_available']}`.",
        f"- Remote tar shards in private staging: {registry['hf_repository']['audio_tar_shards']}; bytes: {registry['hf_repository']['audio_tar_bytes']:,}.", "",
        "## Nine-model technical validation", "",
        "- Publication-facing values below are a uniform diagnostic rescore of existing prediction CSVs against one canonical test manifest and one normalizer.",
        "- The historical run-native ranking must not be used: its WER/CER values used non-identical reference normalization and denominators.",
        "- Uniform scoring does not make heterogeneous recipes, pretraining, tokenizers, decoders, or hardware a controlled architecture or efficiency comparison.", "",
        "| Model | Uniform WER (%) | Uniform CER (%) | Parameters |", "|---|---:|---:|---:|",
    ]
    for item in uniform_models:
        lines.append(f"| {item['family']} | {100 * item['wer']:.3f} | {100 * item['cer']:.3f} | {item['parameters']:,} |")
    lines.extend(["", "## Material gaps", ""])
    lines.extend(f"- [MATERIAL GAP] {gap}" for gap in registry["material_gaps"])
    (OUT / "EVIDENCE_REGISTRY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"registry": str(OUT / 'evidence_registry.json'), "claims": len(claims), "models": len(uniform_models)}, indent=2))


if __name__ == "__main__":
    main()
