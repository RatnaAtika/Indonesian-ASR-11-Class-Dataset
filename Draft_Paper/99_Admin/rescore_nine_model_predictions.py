#!/usr/bin/env python3
"""Uniformly rescore all nine frozen-benchmark prediction CSVs.

The historical benchmark table contains run-native metrics whose reference labels
were not normalized identically across all recipes. This script does not rerun
inference. It matches every existing prediction row to ``splits/test_clean.tsv``,
applies one frozen project normalizer to both references and hypotheses, computes
corpus-level WER/CER with exact Levenshtein distance, and writes a hashed audit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Hashable, Sequence

ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_PATH = ROOT / "Report_paper_9model" / "benchmark" / "benchmark.json"
CANONICAL_TEST_PATH = ROOT / "splits" / "test_clean.tsv"
DEFAULT_OUTPUT = ROOT / "Draft_Paper" / "02_Evidence" / "unified_benchmark_rescore"
NORMALIZER_ID = "nssid_project_uniform_v1"

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


def normalize_text(text: str | None) -> str:
    """Apply the frozen project comparison normalizer.

    This is the rule already used by ``training/common/from_scratch_trainer.py``:
    Unicode NFKC, lowercase, retain ASCII letters/whitespace/apostrophes, replace
    every other run with spaces, collapse whitespace, and strip.
    """

    value = unicodedata.normalize("NFKC", text or "").lower()
    value = re.sub(r"[^a-z\s']", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def basic_native_normalize(text: str | None) -> str:
    return (text or "").strip().lower()


def levenshtein_distance(left: Sequence[Hashable], right: Sequence[Hashable]) -> int:
    """Exact Levenshtein distance using Myers' bit-vector algorithm."""

    if left == right:
        return 0
    pattern_length = len(left)
    if pattern_length == 0:
        return len(right)
    if len(right) == 0:
        return pattern_length

    equality_masks: dict[Hashable, int] = {}
    for index, item in enumerate(left):
        equality_masks[item] = equality_masks.get(item, 0) | (1 << index)

    full_mask = (1 << pattern_length) - 1
    highest_bit = 1 << (pattern_length - 1)
    positive_vertical = full_mask
    negative_vertical = 0
    score = pattern_length

    for item in right:
        equality = equality_masks.get(item, 0)
        horizontal_input = equality | negative_vertical
        horizontal = (((equality & positive_vertical) + positive_vertical) ^ positive_vertical) | equality
        positive_horizontal = negative_vertical | ~(horizontal | positive_vertical)
        negative_horizontal = positive_vertical & horizontal

        if positive_horizontal & highest_bit:
            score += 1
        if negative_horizontal & highest_bit:
            score -= 1

        positive_horizontal = ((positive_horizontal << 1) | 1) & full_mask
        negative_horizontal = (negative_horizontal << 1) & full_mask
        positive_vertical = (negative_horizontal | ~(horizontal_input | positive_horizontal)) & full_mask
        negative_vertical = (positive_horizontal & horizontal_input) & full_mask

    return score


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_project_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"Artifact is outside the project root: {path}") from exc


def resolve_project_artifact(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    relative_project_path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def load_canonical_test() -> list[dict[str, str]]:
    with CANONICAL_TEST_PATH.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 15376:
        raise ValueError(f"Expected 15376 canonical test rows, found {len(rows)}")
    return rows


def load_prediction_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    required = {"idx", "pred", "label"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"Missing required columns in {path}: {required}")
    if len(rows) != 15376:
        raise ValueError(f"Expected 15376 predictions in {path}, found {len(rows)}")
    for expected, row in enumerate(rows):
        if int(row["idx"]) != expected:
            raise ValueError(f"Noncanonical idx at row {expected} in {path}: {row['idx']}")
    return rows


def score_model(
    model: dict,
    canonical_rows: list[dict[str, str]],
    parameter_map: dict[str, int],
    native_metric_map: dict[str, dict],
) -> dict[str, object]:
    model_id = model["model_id"]
    prediction_path = resolve_project_artifact(model["predictions_csv"])
    prediction_rows = load_prediction_rows(prediction_path)

    reference_words = 0
    reference_characters = 0
    word_errors = 0
    character_errors = 0
    native_reference_words = 0
    native_reference_characters = 0
    canonical_reference_match = True
    audio_path_match = True

    for canonical, prediction in zip(canonical_rows, prediction_rows):
        canonical_reference = normalize_text(canonical["transcript"])
        prediction_reference = normalize_text(prediction["label"])
        hypothesis = normalize_text(prediction["pred"])

        if prediction_reference != canonical_reference:
            canonical_reference_match = False
        prediction_audio = (prediction.get("audio") or "").strip()
        if prediction_audio and prediction_audio != canonical["audio_path"]:
            audio_path_match = False

        reference_tokens = canonical_reference.split()
        hypothesis_tokens = hypothesis.split()
        reference_words += len(reference_tokens)
        reference_characters += len(canonical_reference)
        word_errors += levenshtein_distance(reference_tokens, hypothesis_tokens)
        character_errors += levenshtein_distance(canonical_reference, hypothesis)

        native_reference = basic_native_normalize(prediction["label"])
        native_reference_words += len(native_reference.split())
        native_reference_characters += len(native_reference)

    if not canonical_reference_match:
        raise ValueError(f"Normalized prediction labels do not match canonical references for {model_id}")
    if not audio_path_match:
        raise ValueError(f"Prediction audio order/path does not match canonical manifest for {model_id}")

    native = native_metric_map[model_id]
    return {
        "model_id": model_id,
        "model_family": MODEL_FAMILY[model_id],
        "normalizer_id": NORMALIZER_ID,
        "n_test_items": len(canonical_rows),
        "reference_words": reference_words,
        "word_errors": word_errors,
        "wer": word_errors / reference_words,
        "wer_percent": (word_errors / reference_words) * 100,
        "reference_characters": reference_characters,
        "character_errors": character_errors,
        "cer": character_errors / reference_characters,
        "cer_percent": (character_errors / reference_characters) * 100,
        "parameters": parameter_map[model_id],
        "canonical_reference_match": canonical_reference_match,
        "audio_path_match": audio_path_match,
        "predictions_csv": relative_project_path(prediction_path),
        "predictions_sha256": sha256_file(prediction_path),
        "native_wer": native["wer"],
        "native_cer": native["cer"],
        "native_reference_words": native_reference_words,
        "native_reference_characters": native_reference_characters,
        "native_metric_status": "run-native; do not compare or rank across recipes",
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = [
        "model_id",
        "model_family",
        "normalizer_id",
        "n_test_items",
        "reference_words",
        "word_errors",
        "wer",
        "wer_percent",
        "reference_characters",
        "character_errors",
        "cer",
        "cer_percent",
        "parameters",
        "canonical_reference_match",
        "audio_path_match",
        "predictions_csv",
        "predictions_sha256",
        "native_wer",
        "native_cer",
        "native_reference_words",
        "native_reference_characters",
        "native_metric_status",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            serialized = dict(row)
            for key in ("wer", "cer", "native_wer", "native_cer"):
                serialized[key] = f"{float(serialized[key]):.15g}"
            for key in ("wer_percent", "cer_percent"):
                serialized[key] = f"{float(serialized[key]):.6f}"
            writer.writerow(serialized)


def write_markdown_report(path: Path, payload: dict[str, object]) -> None:
    models = payload["models"]
    denominator_groups: dict[tuple[int, int], list[str]] = {}
    for model in models:
        key = (int(model["native_reference_words"]), int(model["native_reference_characters"]))
        denominator_groups.setdefault(key, []).append(str(model["model_family"]))

    lines = [
        "# Benchmark scoring comparability audit",
        "",
        "**Status:** internal evidence artifact; **NOT FOR SUBMISSION**  ",
        "**Scope:** existing predictions for the frozen 102,544-file benchmark; test set `n=15,376`  ",
        f"**Uniform normalizer:** `{payload['normalizer_id']}`",
        "",
        "## Finding",
        "",
        "**Observed:** The historical run-native WER/CER values did not use one reference normalization or one denominator across all nine recipes. Consequently, the historical run-native ranking is not publication-comparable and must not be used in Supplementary Table S6 or adjacent claims.",
        "",
    ]
    for (words, characters), families in sorted(denominator_groups.items(), reverse=True):
        lines.append(
            f"- Native references for {len(families)} recipe(s) used **{words:,} words / {characters:,} characters**: "
            + "; ".join(sorted(families))
            + "."
        )
    lines.extend(
        [
            "",
            "The discrepancy arises because Conformer-CTC and Bi-LSTM CTC stored references after the project NFKC/lowercase/punctuation-removal rule, while the other seven prediction files stored strip/lowercase references. All files contain the same 15,376 canonical test items and normalize to the same canonical references under the corrective rule.",
            "",
            "## Corrective protocol",
            "",
            f"1. Canonical reference manifest: `{payload['canonical_reference_manifest']}` (`SHA-256 {payload['canonical_reference_sha256']}`).",
            f"2. Normalization: {payload['normalizer_definition']}.",
            f"3. Shared denominators: **{payload['reference_words']:,} words / {payload['reference_characters']:,} characters**.",
            "4. Each prediction row is matched by canonical index and, when populated, relative audio path; every normalized stored label must equal the canonical normalized transcript.",
            "5. WER/CER use summed per-utterance exact Levenshtein edit distance divided by the shared word/character denominator.",
            "6. Existing prediction files are rescored; no model inference is rerun.",
            "",
            "## Uniform diagnostic rescore",
            "",
            "| Model | WER (%) | CER (%) | Parameters |",
            "|---|---:|---:|---:|",
        ]
    )
    for model in models:
        lines.append(
            f"| {model['model_family']} | {float(model['wer_percent']):.3f} | "
            f"{float(model['cer_percent']):.3f} | {int(model['parameters']):,} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "Uniform scoring repairs the reference-normalization/denominator defect. It does not make the recipes a controlled architecture, pretraining, tokenizer, decoder, hardware, fairness, speed, or efficiency comparison. The complete nine-row display is Supplementary Table S6 unless every method-card and interpretation gate closes and the display is globally renumbered for main-text promotion. Historical run-native values remain provenance only.",
            "",
            "## Reproduction",
            "",
            "```bash",
            "python3 Draft_Paper/99_Admin/rescore_nine_model_predictions.py",
            "python3 -m unittest Draft_Paper/99_Admin/test_unified_benchmark_rescore.py",
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_rescore(output_dir: Path) -> tuple[Path, Path, Path]:
    benchmark = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    canonical_rows = load_canonical_test()
    parameter_map = {
        row["model_id"]: int(row["n_params"])
        for row in benchmark["paper_models_ranked_by_wer"]
    }
    native_metric_map = {
        row["model_id"]: {"wer": row["wer"], "cer": row["cer"]}
        for row in benchmark["paper_models_ranked_by_wer"]
    }

    models = sorted(benchmark["paper_models"], key=lambda row: MODEL_FAMILY[row["model_id"]].lower())
    scored = [score_model(model, canonical_rows, parameter_map, native_metric_map) for model in models]

    reference_word_counts = {int(row["reference_words"]) for row in scored}
    reference_character_counts = {int(row["reference_characters"]) for row in scored}
    if reference_word_counts != {135911} or reference_character_counts != {942599}:
        raise ValueError(
            f"Unexpected canonical denominators: words={reference_word_counts}, characters={reference_character_counts}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "unified_nine_model_metrics.csv"
    json_path = output_dir / "unified_nine_model_metrics.json"
    write_csv(csv_path, scored)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "uniform diagnostic rescore of existing predictions; no inference rerun",
        "scope": "frozen 102544-file benchmark; test set only",
        "canonical_reference_manifest": relative_project_path(CANONICAL_TEST_PATH),
        "canonical_reference_sha256": sha256_file(CANONICAL_TEST_PATH),
        "benchmark_source": relative_project_path(BENCHMARK_PATH),
        "benchmark_source_sha256": sha256_file(BENCHMARK_PATH),
        "normalizer_id": NORMALIZER_ID,
        "normalizer_definition": "Unicode NFKC; lowercase; replace non-[a-z whitespace apostrophe] with spaces; collapse whitespace; strip",
        "metric_definition": "corpus WER/CER = summed per-utterance exact Levenshtein edit distance divided by total canonical reference words/characters; characters include normalized inter-word spaces",
        "n_test_items": len(canonical_rows),
        "reference_words": 135911,
        "reference_characters": 942599,
        "ordering_rule": "alphabetical by model_family; no performance rank",
        "interpretation": "Uniform scoring makes the displayed error rates share references and denominators. Recipe, pretraining, tokenizer, optimization, decoder, and hardware heterogeneity remains; this is not a controlled architecture or efficiency comparison.",
        "models": scored,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path = output_dir / "BENCHMARK_SCORING_COMPARABILITY_AUDIT.md"
    write_markdown_report(report_path, payload)
    return csv_path, json_path, report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_path, json_path, report_path = build_rescore(args.output_dir.resolve())
    print(f"Wrote {csv_path}")
    print(f"Wrote {json_path}")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
