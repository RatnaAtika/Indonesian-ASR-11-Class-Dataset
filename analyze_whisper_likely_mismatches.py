import argparse
import csv
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_RUN_DIR = PROJECT_ROOT / "Whisper_Verification" / "run_20260403_221557"
ANALYSIS_DIR_NAME = "likely_mismatch_analysis"


@dataclass
class MismatchRow:
    category: str
    respondent: str
    take: str
    wav_name: str
    wav_path: str
    expected_id: int
    expected_text: str
    predicted_text: str
    best_match_id: int
    best_match_text: str
    exact_normalized_match: bool
    expected_similarity: float
    best_similarity: float
    matches_expected_id: bool
    passes_threshold: bool
    likely_mismatch: bool
    status: str
    error_message: str


@dataclass
class TakePattern:
    category: str
    respondent: str
    take: str
    row_count: int
    min_expected_id: int
    max_expected_id: int
    dominant_offset: int
    dominant_offset_count: int
    offset_histogram: str
    max_consecutive_run: int
    classification: str
    probable_cause: str
    boundary_hint: str
    predicted_matches_best_count: int
    repeat_cue_count: int
    avg_expected_similarity: float
    avg_best_similarity: float
    avg_similarity_margin: float
    example_expected_text: str
    example_predicted_text: str
    example_best_match_text: str


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).lower().strip()
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = normalized.replace("_", " ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def as_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def as_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def as_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_mismatch_rows(run_dir: Path) -> List[MismatchRow]:
    mismatch_only = run_dir / "whisper_mismatch_only.csv"
    details = run_dir / "whisper_match_details.csv"
    raw_rows: List[Dict[str, str]]
    if mismatch_only.exists():
        raw_rows = read_csv_rows(mismatch_only)
    elif details.exists():
        raw_rows = [row for row in read_csv_rows(details) if row.get("likely_mismatch", "").strip().lower() == "true"]
    else:
        raise RuntimeError(f"Tidak menemukan whisper_mismatch_only.csv atau whisper_match_details.csv di {run_dir}")
    rows: List[MismatchRow] = []
    for row in raw_rows:
        best_match_id_raw = row.get("best_match_id", "")
        rows.append(
            MismatchRow(
                category=row.get("category", ""),
                respondent=row.get("respondent", ""),
                take=row.get("take", ""),
                wav_name=row.get("wav_name", ""),
                wav_path=row.get("wav_path", ""),
                expected_id=as_int(row.get("expected_id", "-1"), -1),
                expected_text=row.get("expected_text", ""),
                predicted_text=row.get("predicted_text", ""),
                best_match_id=as_int(best_match_id_raw, -1),
                best_match_text=row.get("best_match_text", ""),
                exact_normalized_match=as_bool(row.get("exact_normalized_match", "false")),
                expected_similarity=as_float(row.get("expected_similarity", "0"), 0.0),
                best_similarity=as_float(row.get("best_similarity", "0"), 0.0),
                matches_expected_id=as_bool(row.get("matches_expected_id", "false")),
                passes_threshold=as_bool(row.get("passes_threshold", "false")),
                likely_mismatch=as_bool(row.get("likely_mismatch", "false")),
                status=row.get("status", ""),
                error_message=row.get("error_message", ""),
            )
        )
    return rows


def predicted_matches_best(row: MismatchRow) -> bool:
    return normalize_text(row.predicted_text) == normalize_text(row.best_match_text)


def contains_repeat_cue(text: str) -> bool:
    normalized = normalize_text(text)
    cues = (
        "ulangi",
        "ulang",
        "sekali lagi",
        "maksud saya",
        "eh",
        "maaf",
    )
    return any(cue in normalized for cue in cues)


def offset_histogram_text(offsets: Iterable[int]) -> str:
    counter = Counter(offsets)
    return ", ".join(f"{offset:+d}:{count}" for offset, count in sorted(counter.items(), key=lambda item: (item[0], item[1])))


def max_consecutive_expected_run(expected_ids: Sequence[int]) -> int:
    if not expected_ids:
        return 0
    ordered = sorted(expected_ids)
    best = 1
    current = 1
    for previous, current_id in zip(ordered, ordered[1:]):
        if current_id == previous + 1:
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


def classification_label(items: Sequence[MismatchRow]) -> str:
    offsets = [row.best_match_id - row.expected_id for row in items]
    counter = Counter(offsets)
    dominant_offset, dominant_count = counter.most_common(1)[0]
    predicted_best_count = sum(int(predicted_matches_best(row)) for row in items)
    repeat_cue_count = sum(int(contains_repeat_cue(row.predicted_text)) for row in items)
    if len(items) >= 3 and dominant_count == len(items):
        return f"systematic_shift_{dominant_offset:+d}"
    if len(items) >= 4 and dominant_count / len(items) >= 0.8:
        return f"dominant_shift_{dominant_offset:+d}"
    if repeat_cue_count >= max(1, math.ceil(len(items) / 3)):
        return "speech_restart_or_repeat"
    if len(items) >= 2 and all(abs(offset) == 1 for offset in offsets):
        return "adjacent_sentence_confusion"
    if predicted_best_count >= max(2, math.ceil(len(items) / 2)):
        return "speaker_said_other_known_sentence"
    return "mixed_or_isolated_confusion"


def probable_cause_from_label(label: str) -> str:
    if label.startswith("systematic_shift_") or label.startswith("dominant_shift_"):
        return "Sangat mungkin ada pergeseran urutan isi audio terhadap nomor file dalam satu take, bukan kesalahan ASR acak."
    if label == "adjacent_sentence_confusion":
        return "Mayoritas tertukar dengan kalimat tetangga, mengindikasikan responden membaca prompt sebelum/sesudahnya atau ada offset pendek di urutan take."
    if label == "speaker_said_other_known_sentence":
        return "Prediksi Whisper cocok kuat ke kalimat transkrip lain yang valid, sehingga audio kemungkinan memang berisi kalimat lain dari kategori yang sama."
    if label == "speech_restart_or_repeat":
        return "Terdapat sinyal pengulangan atau restart ucapan yang berpotensi membuat isi file tidak lagi sesuai dengan ID semula."
    return "Kasus campuran atau terisolasi; perlu audit manual pada audio dan urutan prompt di take ini."


def boundary_hint(label: str, min_expected_id: int, max_expected_id: int, dominant_offset: int) -> str:
    if label.startswith("systematic_shift") or label.startswith("dominant_shift"):
        if dominant_offset == -1 and min_expected_id > 1:
            return "Pola ini konsisten dengan isi audio mulai bergeser satu langkah lebih awal dari file saat ini; cek apakah prompt awal hilang atau penomoran mulai terlambat."
        if dominant_offset == 1 and max_expected_id < 19:
            return "Pola ini konsisten dengan isi audio bergeser satu langkah lebih akhir; cek apakah ada pengulangan di awal atau prompt akhir hilang."
        if abs(dominant_offset) == 2:
            return "Pola dua langkah menunjukkan kemungkinan penggeseran urutan yang lebih besar atau dua prompt beruntun tertukar/hilang."
    return ""


def build_take_patterns(rows: Sequence[MismatchRow]) -> List[TakePattern]:
    by_take: Dict[Tuple[str, str, str], List[MismatchRow]] = defaultdict(list)
    for row in rows:
        by_take[(row.category, row.respondent, row.take)].append(row)
    patterns: List[TakePattern] = []
    for (category, respondent, take), items in sorted(by_take.items()):
        ordered_items = sorted(items, key=lambda item: item.expected_id)
        offsets = [item.best_match_id - item.expected_id for item in ordered_items]
        offset_counter = Counter(offsets)
        dominant_offset, dominant_offset_count = offset_counter.most_common(1)[0]
        label = classification_label(ordered_items)
        first = ordered_items[0]
        patterns.append(
            TakePattern(
                category=category,
                respondent=respondent,
                take=take,
                row_count=len(ordered_items),
                min_expected_id=min(item.expected_id for item in ordered_items),
                max_expected_id=max(item.expected_id for item in ordered_items),
                dominant_offset=dominant_offset,
                dominant_offset_count=dominant_offset_count,
                offset_histogram=offset_histogram_text(offsets),
                max_consecutive_run=max_consecutive_expected_run([item.expected_id for item in ordered_items]),
                classification=label,
                probable_cause=probable_cause_from_label(label),
                boundary_hint=boundary_hint(label, min(item.expected_id for item in ordered_items), max(item.expected_id for item in ordered_items), dominant_offset),
                predicted_matches_best_count=sum(int(predicted_matches_best(item)) for item in ordered_items),
                repeat_cue_count=sum(int(contains_repeat_cue(item.predicted_text)) for item in ordered_items),
                avg_expected_similarity=round(sum(item.expected_similarity for item in ordered_items) / len(ordered_items), 6),
                avg_best_similarity=round(sum(item.best_similarity for item in ordered_items) / len(ordered_items), 6),
                avg_similarity_margin=round(sum((item.best_similarity - item.expected_similarity) for item in ordered_items) / len(ordered_items), 6),
                example_expected_text=first.expected_text,
                example_predicted_text=first.predicted_text,
                example_best_match_text=first.best_match_text,
            )
        )
    patterns.sort(key=lambda item: (-item.row_count, item.category, item.respondent, item.take))
    return patterns


def enrich_rows(rows: Sequence[MismatchRow], take_patterns: Sequence[TakePattern]) -> List[Dict[str, object]]:
    pattern_by_take = {(item.category, item.respondent, item.take): item for item in take_patterns}
    enriched: List[Dict[str, object]] = []
    for row in rows:
        pattern = pattern_by_take[(row.category, row.respondent, row.take)]
        enriched.append(
            {
                "category": row.category,
                "respondent": row.respondent,
                "take": row.take,
                "wav_name": row.wav_name,
                "wav_path": row.wav_path,
                "expected_id": row.expected_id,
                "best_match_id": row.best_match_id,
                "offset": row.best_match_id - row.expected_id,
                "expected_text": row.expected_text,
                "predicted_text": row.predicted_text,
                "best_match_text": row.best_match_text,
                "expected_similarity": row.expected_similarity,
                "best_similarity": row.best_similarity,
                "similarity_margin": round(row.best_similarity - row.expected_similarity, 6),
                "predicted_matches_best": predicted_matches_best(row),
                "repeat_cue": contains_repeat_cue(row.predicted_text),
                "classification": pattern.classification,
                "probable_cause": pattern.probable_cause,
                "boundary_hint": pattern.boundary_hint,
            }
        )
    enriched.sort(key=lambda item: (item["classification"], item["category"], item["respondent"], item["take"], item["expected_id"]))
    return enriched


def maybe_load_summary(run_dir: Path) -> Dict[str, object]:
    path = run_dir / "whisper_summary.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def top_counter(counter: Counter, limit: int = 20) -> List[Dict[str, object]]:
    result: List[Dict[str, object]] = []
    for key, count in counter.most_common(limit):
        result.append({"key": key, "count": count})
    return result


def summarize(rows: Sequence[MismatchRow], patterns: Sequence[TakePattern], run_dir: Path) -> Dict[str, object]:
    summary_json = maybe_load_summary(run_dir)
    by_category = Counter(row.category for row in rows)
    by_respondent = Counter(row.respondent for row in rows)
    by_offset = Counter(row.best_match_id - row.expected_id for row in rows)
    by_pair = Counter((row.category, row.expected_id, row.best_match_id) for row in rows)
    by_class_rows = Counter(pattern.classification for pattern in patterns for _ in range(pattern.row_count))
    by_class_takes = Counter(pattern.classification for pattern in patterns)
    best_similarity_bins = Counter()
    for row in rows:
        if row.best_similarity >= 0.99:
            best_similarity_bins[">=0.99"] += 1
        elif row.best_similarity >= 0.95:
            best_similarity_bins["0.95-0.99"] += 1
        elif row.best_similarity >= 0.90:
            best_similarity_bins["0.90-0.95"] += 1
        elif row.best_similarity >= 0.80:
            best_similarity_bins["0.80-0.90"] += 1
        else:
            best_similarity_bins["<0.80"] += 1
    systematic_shift_rows = sum(
        pattern.row_count for pattern in patterns if pattern.classification.startswith("systematic_shift") or pattern.classification.startswith("dominant_shift")
    )
    systematic_shift_takes = sum(
        1 for pattern in patterns if pattern.classification.startswith("systematic_shift") or pattern.classification.startswith("dominant_shift")
    )
    adjacent_rows = sum(pattern.row_count for pattern in patterns if pattern.classification == "adjacent_sentence_confusion")
    speaker_other_rows = sum(pattern.row_count for pattern in patterns if pattern.classification == "speaker_said_other_known_sentence")
    repeat_rows = sum(pattern.row_count for pattern in patterns if pattern.classification == "speech_restart_or_repeat")
    summary = {
        "generated_at": datetime.now().isoformat(),
        "run_dir": str(run_dir),
        "source_summary": summary_json.get("summary", {}),
        "mismatch_summary": {
            "mismatch_rows": len(rows),
            "mismatch_takes": len(patterns),
            "avg_expected_similarity": round(sum(row.expected_similarity for row in rows) / len(rows), 6) if rows else 0.0,
            "avg_best_similarity": round(sum(row.best_similarity for row in rows) / len(rows), 6) if rows else 0.0,
            "avg_similarity_margin": round(sum(row.best_similarity - row.expected_similarity for row in rows) / len(rows), 6) if rows else 0.0,
            "predicted_matches_best_count": sum(int(predicted_matches_best(row)) for row in rows),
            "repeat_cue_count": sum(int(contains_repeat_cue(row.predicted_text)) for row in rows),
            "systematic_or_dominant_shift_rows": systematic_shift_rows,
            "systematic_or_dominant_shift_takes": systematic_shift_takes,
            "adjacent_sentence_confusion_rows": adjacent_rows,
            "speaker_said_other_known_sentence_rows": speaker_other_rows,
            "speech_restart_or_repeat_rows": repeat_rows,
        },
        "distributions": {
            "rows_by_category": top_counter(by_category, limit=len(by_category)),
            "rows_by_respondent": top_counter(by_respondent, limit=25),
            "rows_by_offset": top_counter(by_offset, limit=len(by_offset)),
            "rows_by_classification": top_counter(by_class_rows, limit=len(by_class_rows)),
            "takes_by_classification": top_counter(by_class_takes, limit=len(by_class_takes)),
            "top_expected_best_pairs": top_counter(by_pair, limit=25),
            "best_similarity_bins": top_counter(best_similarity_bins, limit=len(best_similarity_bins)),
        },
        "top_take_patterns": [pattern.__dict__ for pattern in patterns[:30]],
    }
    return summary


def write_csv(path: Path, rows: Sequence[Dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def make_text_report(summary: Dict[str, object], patterns: Sequence[TakePattern]) -> str:
    mismatch_summary = summary["mismatch_summary"]
    source_summary = summary.get("source_summary", {})
    distributions = summary["distributions"]
    lines: List[str] = []
    lines.append("LIKELY MISMATCH ANALYSIS REPORT")
    lines.append("")
    lines.append(f"run_dir={summary['run_dir']}")
    lines.append(f"generated_at={summary['generated_at']}")
    lines.append("")
    if source_summary:
        lines.append(f"source_likely_mismatch_count={source_summary.get('likely_mismatch_count', 'n/a')}")
        lines.append(f"source_best_match_expected_id_count={source_summary.get('best_match_expected_id_count', 'n/a')}")
        lines.append(f"source_pass_threshold_count={source_summary.get('pass_threshold_count', 'n/a')}")
        lines.append("")
    for key, value in mismatch_summary.items():
        lines.append(f"{key}={value}")
    lines.append("")
    lines.append("Top kategori mismatch:")
    for item in distributions["rows_by_category"][:11]:
        lines.append(f"- {item['key']}: {item['count']}")
    lines.append("")
    lines.append("Distribusi offset best_match_id - expected_id:")
    for item in distributions["rows_by_offset"]:
        lines.append(f"- {item['key']}: {item['count']}")
    lines.append("")
    lines.append("Klasifikasi penyebab (berdasarkan row):")
    for item in distributions["rows_by_classification"]:
        lines.append(f"- {item['key']}: {item['count']}")
    lines.append("")
    lines.append("Take paling bermasalah:")
    for pattern in patterns[:15]:
        lines.append(
            f"- {pattern.category}/{pattern.respondent}/{pattern.take}: rows={pattern.row_count} class={pattern.classification} dominant_offset={pattern.dominant_offset:+d} avg_margin={pattern.avg_similarity_margin} cause={pattern.probable_cause}"
        )
        if pattern.boundary_hint:
            lines.append(f"  hint={pattern.boundary_hint}")
    lines.append("")
    return "\n".join(lines)


def make_markdown_report(summary: Dict[str, object], patterns: Sequence[TakePattern]) -> str:
    mismatch_summary = summary["mismatch_summary"]
    distributions = summary["distributions"]
    lines: List[str] = []
    lines.append("# Likely Mismatch Analysis Report")
    lines.append("")
    lines.append(f"- Run dir: `{summary['run_dir']}`")
    lines.append(f"- Generated at: `{summary['generated_at']}`")
    lines.append("")
    lines.append("## Ringkasan")
    lines.append("")
    for key, value in mismatch_summary.items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Temuan Utama")
    lines.append("")
    lines.append(
        f"- **Mayoritas mismatch bukan error ASR acak**: `{mismatch_summary['systematic_or_dominant_shift_rows']}` dari `{mismatch_summary['mismatch_rows']}` row berada pada take yang menunjukkan pergeseran urutan sistematis atau dominan."
    )
    lines.append(
        "- **Offset paling dominan adalah tetangga langsung**: lihat distribusi offset, dengan dominasi `-1` dan `+1`, yang menunjukkan audio sering cocok ke kalimat sebelum/sesudah nomor file."
    )
    lines.append(
        f"- **Banyak kasus ber-confidence tinggi**: `predicted_matches_best_count={mismatch_summary['predicted_matches_best_count']}` dan distribusi `best_similarity` didominasi nilai sangat tinggi, sehingga audio kemungkinan memang berisi kalimat lain yang valid dalam kategori yang sama."
    )
    lines.append("")
    lines.append("## Distribusi Kategori")
    lines.append("")
    for item in distributions["rows_by_category"]:
        lines.append(f"- **{item['key']}**: `{item['count']}`")
    lines.append("")
    lines.append("## Distribusi Offset")
    lines.append("")
    for item in distributions["rows_by_offset"]:
        lines.append(f"- **{item['key']:+d}**: `{item['count']}`" if isinstance(item["key"], int) else f"- **{item['key']}**: `{item['count']}`")
    lines.append("")
    lines.append("## Klasifikasi Penyebab")
    lines.append("")
    for item in distributions["rows_by_classification"]:
        label = item["key"]
        lines.append(f"- **{label}**: `{item['count']}`")
        lines.append(f"  - {probable_cause_from_label(label)}")
    lines.append("")
    lines.append("## Take Paling Bermasalah")
    lines.append("")
    for pattern in patterns[:20]:
        lines.append(f"- **{pattern.category}/{pattern.respondent}/{pattern.take}**")
        lines.append(f"  - row_count: `{pattern.row_count}`")
        lines.append(f"  - classification: `{pattern.classification}`")
        lines.append(f"  - dominant_offset: `{pattern.dominant_offset:+d}` ({pattern.dominant_offset_count}/{pattern.row_count})")
        lines.append(f"  - offset_histogram: `{pattern.offset_histogram}`")
        lines.append(f"  - avg_similarity_margin: `{pattern.avg_similarity_margin}`")
        lines.append(f"  - probable_cause: `{pattern.probable_cause}`")
        if pattern.boundary_hint:
            lines.append(f"  - boundary_hint: `{pattern.boundary_hint}`")
        lines.append(f"  - example_expected: `{pattern.example_expected_text}`")
        lines.append(f"  - example_predicted: `{pattern.example_predicted_text}`")
        lines.append(f"  - example_best_match: `{pattern.example_best_match_text}`")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    return parser.parse_args()


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()
    run_dir = args.run_dir.resolve()
    if not run_dir.exists():
        raise RuntimeError(f"Run dir tidak ditemukan: {run_dir}")
    rows = load_mismatch_rows(run_dir)
    if not rows:
        raise RuntimeError(f"Tidak ada row likely mismatch ditemukan di {run_dir}")
    patterns = build_take_patterns(rows)
    summary = summarize(rows, patterns, run_dir)
    analysis_dir = run_dir / ANALYSIS_DIR_NAME
    ensure_directory(analysis_dir)
    enriched_rows = enrich_rows(rows, patterns)
    write_csv(analysis_dir / "likely_mismatch_rows_enriched.csv", enriched_rows)
    write_csv(analysis_dir / "likely_mismatch_take_patterns.csv", [pattern.__dict__ for pattern in patterns])
    (analysis_dir / "likely_mismatch_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (analysis_dir / "likely_mismatch_report.txt").write_text(make_text_report(summary, patterns), encoding="utf-8")
    (analysis_dir / "likely_mismatch_report.md").write_text(make_markdown_report(summary, patterns), encoding="utf-8")
    print("=== LIKELY MISMATCH ANALYSIS SUMMARY ===")
    for key, value in summary["mismatch_summary"].items():
        print(f"{key}: {value}")
    print(f"analysis_dir: {analysis_dir}")


if __name__ == "__main__":
    main()
