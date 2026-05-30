from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List

EXPECTED_IDS = list(range(1, 21))
WAV_GLOB = "*.wav"
EXPECTED_SOURCE_WAVS_PER_TAKE = 20
EXPECTED_OUTPUT_WAVS_PER_TAKE = 19


@dataclass
class TranscriptInfo:
    category: str
    kept_ids: List[int]
    dropped_ids_from_entries: List[int]
    note_lines: List[str]
    note_leading_ids: List[int]
    note_matches_entries: bool
    entries: List[Dict[str, str]]


class ProgressBar:
    def __init__(self, total: int, prefix: str, width: int = 28) -> None:
        self.total = max(int(total), 1)
        self.prefix = prefix
        self.width = width
        self.current = 0
        self.started_at = time.time()
        self._render(0)

    def step(self, suffix: str = "") -> None:
        self.current += 1
        self._render(self.current, suffix=suffix)
        if self.current >= self.total:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def _render(self, value: int, suffix: str = "") -> None:
        value = min(max(value, 0), self.total)
        ratio = value / self.total
        filled = int(self.width * ratio)
        bar = "#" * filled + "." * (self.width - filled)
        elapsed = time.time() - self.started_at
        msg = f"\r{self.prefix} [{bar}] {value}/{self.total} ({ratio * 100:5.1f}%) elapsed={elapsed:6.1f}s"
        if suffix:
            msg += f" {suffix}"
        sys.stdout.write(msg)
        sys.stdout.flush()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_transcript_file(path: Path) -> TranscriptInfo:
    raw_lines = read_text(path).splitlines()
    entries: List[Dict[str, str]] = []
    note_lines: List[str] = []
    note_leading_ids: List[int] = []
    in_note = False
    for raw in raw_lines:
        line = raw.strip()
        if not line:
            continue
        if line.lower().startswith("note"):
            in_note = True
            continue
        if in_note:
            note_lines.append(line)
            m = re.match(r"^(\d{1,2})\b", line)
            if m:
                note_leading_ids.append(int(m.group(1)))
            continue
        m = re.match(r"^(\d{2})\|(.*)$", line)
        if m:
            entries.append({"id": int(m.group(1)), "text": m.group(2).strip()})
    kept_ids = [int(item["id"]) for item in entries]
    dropped_ids = [idx for idx in EXPECTED_IDS if idx not in kept_ids]
    note_matches_entries = not note_leading_ids or note_leading_ids[0] in dropped_ids
    return TranscriptInfo(
        category=path.stem,
        kept_ids=kept_ids,
        dropped_ids_from_entries=dropped_ids,
        note_lines=note_lines,
        note_leading_ids=note_leading_ids,
        note_matches_entries=note_matches_entries,
        entries=entries,
    )


def load_transcripts(transcript_dir: Path) -> Dict[str, TranscriptInfo]:
    files = sorted(transcript_dir.glob("*.txt"))
    progress = ProgressBar(len(files), "Parsing transcripts")
    result: Dict[str, TranscriptInfo] = {}
    for path in files:
        info = parse_transcript_file(path)
        result[info.category] = info
        progress.step(path.stem)
    return result


def audit_dataset(dataset_dir: Path) -> Dict[str, object]:
    category_dirs = sorted([p for p in dataset_dir.iterdir() if p.is_dir()])
    progress = ProgressBar(len(category_dirs), "Auditing dataset")
    categories: Dict[str, object] = {}
    take_rows: List[Dict[str, object]] = []
    bad_take_rows: List[Dict[str, object]] = []
    padding_styles: List[str] = []
    total_wavs = 0
    strict_valid_take_count = 0
    for category_dir in category_dirs:
        respondent_dirs = sorted([p for p in category_dir.iterdir() if p.is_dir()])
        respondent_take_counts: List[int] = []
        take_wav_counts: List[int] = []
        take_padding_styles: List[str] = []
        bad_respondents: List[Dict[str, object]] = []
        bad_takes: List[Dict[str, object]] = []
        strict_valid_takes_for_category = 0
        for respondent_dir in respondent_dirs:
            take_dirs = sorted([p for p in respondent_dir.iterdir() if p.is_dir()])
            respondent_take_counts.append(len(take_dirs))
            if len(take_dirs) != 25:
                bad_respondents.append(
                    {
                        "respondent": respondent_dir.name,
                        "take_count": len(take_dirs),
                    }
                )
            for take_dir in take_dirs:
                inventory = inspect_wav_inventory(take_dir, EXPECTED_IDS)
                wav_count = inventory["wav_count"]
                total_wavs += wav_count
                take_wav_counts.append(wav_count)
                take_padding_styles.append(inventory["padding_style"])
                padding_styles.append(inventory["padding_style"])
                row = {
                    "category": category_dir.name,
                    "respondent": respondent_dir.name,
                    "take": take_dir.name,
                    "wav_count": wav_count,
                    "numeric_wav_count": inventory["numeric_wav_count"],
                    "padding_style": inventory["padding_style"],
                    "is_strict_1_to_20": int(inventory["is_expected_complete"]),
                    "missing_ids": format_id_list(inventory["missing_ids"]),
                    "extra_ids": format_id_list(inventory["extra_ids"]),
                    "duplicate_ids": format_id_list(inventory["duplicate_ids"]),
                    "non_numeric_files": ",".join(inventory["non_numeric_files"]),
                }
                take_rows.append(row)
                if inventory["is_expected_complete"]:
                    strict_valid_take_count += 1
                    strict_valid_takes_for_category += 1
                else:
                    bad_row = {
                        "category": category_dir.name,
                        "respondent": respondent_dir.name,
                        "take": take_dir.name,
                        "wav_count": wav_count,
                        "numeric_wav_count": inventory["numeric_wav_count"],
                        "padding_style": inventory["padding_style"],
                        "missing_ids": format_id_list(inventory["missing_ids"]),
                        "extra_ids": format_id_list(inventory["extra_ids"]),
                        "duplicate_ids": format_id_list(inventory["duplicate_ids"]),
                        "non_numeric_files": ",".join(inventory["non_numeric_files"]),
                    }
                    bad_takes.append(bad_row)
                    bad_take_rows.append(bad_row)
        categories[category_dir.name] = {
            "respondent_count": len(respondent_dirs),
            "take_count_distribution": dict(sorted(Counter(respondent_take_counts).items())),
            "wav_count_distribution": dict(sorted(Counter(take_wav_counts).items())),
            "padding_style_distribution": dict(sorted(Counter(take_padding_styles).items())),
            "strict_valid_take_count": strict_valid_takes_for_category,
            "strict_invalid_take_count": len(bad_takes),
            "bad_respondents": bad_respondents,
            "bad_takes": bad_takes,
        }
        progress.step(category_dir.name)
    return {
        "category_count": len(category_dirs),
        "total_wavs": total_wavs,
        "expected_total_wavs": 11 * 20 * 25 * EXPECTED_SOURCE_WAVS_PER_TAKE,
        "strict_valid_take_count": strict_valid_take_count,
        "strict_invalid_take_count": len(bad_take_rows),
        "padding_style_distribution": dict(sorted(Counter(padding_styles).items())),
        "categories": categories,
        "take_rows": take_rows,
        "bad_take_rows": bad_take_rows,
    }


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, data: object) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def format_id_list(ids: Iterable[int]) -> str:
    return ",".join(f"{idx:02d}" for idx in ids)


def inspect_wav_inventory(take_dir: Path, expected_ids: Iterable[int]) -> Dict[str, object]:
    wav_paths = sorted(take_dir.glob(WAV_GLOB))
    ordered_expected_ids = list(expected_ids)
    expected_id_set = set(ordered_expected_ids)
    indexed: Dict[int, Path] = {}
    duplicate_ids: List[int] = []
    non_numeric_files: List[str] = []
    padded_count = 0
    unpadded_count = 0
    for wav_path in wav_paths:
        stem = wav_path.stem
        if re.fullmatch(r"\d{2}", stem):
            padded_count += 1
        elif re.fullmatch(r"\d+", stem):
            unpadded_count += 1
        else:
            non_numeric_files.append(wav_path.name)
            continue
        wav_id = int(stem)
        existing = indexed.get(wav_id)
        if existing is not None:
            duplicate_ids.append(wav_id)
            if len(stem) <= len(existing.stem):
                continue
        indexed[wav_id] = wav_path
    if padded_count and unpadded_count:
        padding_style = "mixed_numeric"
    elif padded_count:
        padding_style = "zero_padded_2_digit"
    elif unpadded_count:
        padding_style = "unpadded_numeric"
    elif non_numeric_files:
        padding_style = "non_numeric"
    else:
        padding_style = "empty"
    numeric_ids = sorted(indexed)
    missing_ids = [idx for idx in ordered_expected_ids if idx not in indexed]
    extra_ids = [idx for idx in numeric_ids if idx not in expected_id_set]
    is_expected_complete = (
        len(wav_paths) == len(ordered_expected_ids)
        and len(indexed) == len(ordered_expected_ids)
        and not missing_ids
        and not extra_ids
        and not non_numeric_files
        and not duplicate_ids
    )
    return {
        "wav_count": len(wav_paths),
        "numeric_wav_count": len(indexed),
        "numeric_ids": numeric_ids,
        "indexed_files": indexed,
        "padding_style": padding_style,
        "missing_ids": missing_ids,
        "extra_ids": extra_ids,
        "duplicate_ids": sorted(set(duplicate_ids)),
        "non_numeric_files": non_numeric_files,
        "is_expected_complete": is_expected_complete,
    }


def build_dataset(
    source_dataset_dir: Path,
    output_dataset_dir: Path,
    transcript_map: Dict[str, TranscriptInfo],
) -> Dict[str, object]:
    category_dirs = sorted([p for p in source_dataset_dir.iterdir() if p.is_dir()])
    total_takes = 0
    for category_dir in category_dirs:
        for respondent_dir in sorted([p for p in category_dir.iterdir() if p.is_dir()]):
            total_takes += len([p for p in respondent_dir.iterdir() if p.is_dir()])
    progress = ProgressBar(total_takes, "Building balanced dataset")
    build_rows: List[Dict[str, object]] = []
    problem_rows: List[Dict[str, object]] = []
    total_copied = 0
    total_skipped = 0
    for category_dir in category_dirs:
        transcript_info = transcript_map.get(category_dir.name)
        if transcript_info is None:
            raise RuntimeError(f"Transcript for category '{category_dir.name}' not found")
        kept_ids = set(transcript_info.kept_ids)
        dropped_ids = set(transcript_info.dropped_ids_from_entries)
        expected_copied_wavs = len(transcript_info.kept_ids)
        for respondent_dir in sorted([p for p in category_dir.iterdir() if p.is_dir()]):
            for take_dir in sorted([p for p in respondent_dir.iterdir() if p.is_dir()]):
                dest_take_dir = output_dataset_dir / category_dir.name / respondent_dir.name / take_dir.name
                ensure_dir(dest_take_dir)
                inventory = inspect_wav_inventory(take_dir, EXPECTED_IDS)
                wav_files = inventory["indexed_files"]
                copied_here = 0
                skipped_here = 0
                missing_kept = []
                for idx in EXPECTED_IDS:
                    output_name = f"{idx:02d}.wav"
                    src = wav_files.get(idx)
                    if idx in kept_ids:
                        if src is None:
                            missing_kept.append(output_name)
                            continue
                        shutil.copy2(src, dest_take_dir / output_name)
                        copied_here += 1
                    elif idx in dropped_ids:
                        skipped_here += 1
                total_copied += copied_here
                total_skipped += skipped_here
                row = {
                    "category": category_dir.name,
                    "respondent": respondent_dir.name,
                    "take": take_dir.name,
                    "copied_wavs": copied_here,
                    "expected_copied_wavs": expected_copied_wavs,
                    "skipped_wavs": skipped_here,
                    "missing_kept_wavs": ",".join(missing_kept),
                    "source_padding_style": inventory["padding_style"],
                    "source_is_strict_1_to_20": int(inventory["is_expected_complete"]),
                    "source_missing_ids": format_id_list(inventory["missing_ids"]),
                    "source_extra_ids": format_id_list(inventory["extra_ids"]),
                    "source_duplicate_ids": format_id_list(inventory["duplicate_ids"]),
                    "source_non_numeric_files": ",".join(inventory["non_numeric_files"]),
                }
                build_rows.append(row)
                if copied_here != expected_copied_wavs or missing_kept:
                    problem_rows.append(row)
                progress.step(f"{category_dir.name}/{respondent_dir.name}/{take_dir.name}")
    return {
        "total_takes": total_takes,
        "total_copied_wavs": total_copied,
        "total_skipped_wavs": total_skipped,
        "expected_output_wavs": 11 * 20 * 25 * EXPECTED_OUTPUT_WAVS_PER_TAKE,
        "problem_take_count": len(problem_rows),
        "normalized_output_name_style": "zero_padded_2_digit",
        "build_rows": build_rows,
        "problem_rows": problem_rows,
    }


def verify_output_dataset(output_dataset_dir: Path, transcript_map: Dict[str, TranscriptInfo]) -> Dict[str, object]:
    category_dirs = sorted([p for p in output_dataset_dir.iterdir() if p.is_dir()]) if output_dataset_dir.exists() else []
    progress = ProgressBar(len(category_dirs), "Verifying output")
    total_wavs = 0
    take_rows: List[Dict[str, object]] = []
    bad_takes: List[Dict[str, object]] = []
    fully_valid_take_count = 0
    all_zero_padded_take_count = 0
    for category_dir in category_dirs:
        transcript_info = transcript_map.get(category_dir.name)
        if transcript_info is None:
            raise RuntimeError(f"Transcript for category '{category_dir.name}' not found during verification")
        expected_names = {f"{idx:02d}.wav" for idx in transcript_info.kept_ids}
        for respondent_dir in sorted([p for p in category_dir.iterdir() if p.is_dir()]):
            for take_dir in sorted([p for p in respondent_dir.iterdir() if p.is_dir()]):
                wav_names = sorted(p.name for p in take_dir.glob(WAV_GLOB))
                wav_count = len(wav_names)
                total_wavs += wav_count
                actual_name_set = set(wav_names)
                missing_expected_names = sorted(expected_names - actual_name_set)
                unexpected_names = sorted(actual_name_set - expected_names)
                all_zero_padded_names = all(re.fullmatch(r"\d{2}\.wav", name) for name in wav_names)
                row = {
                    "category": category_dir.name,
                    "respondent": respondent_dir.name,
                    "take": take_dir.name,
                    "wav_count": wav_count,
                    "expected_wav_count": len(expected_names),
                    "all_zero_padded_names": int(all_zero_padded_names),
                    "missing_expected_names": ",".join(missing_expected_names),
                    "unexpected_names": ",".join(unexpected_names),
                }
                take_rows.append(row)
                if all_zero_padded_names:
                    all_zero_padded_take_count += 1
                if wav_count == len(expected_names) and not missing_expected_names and not unexpected_names and all_zero_padded_names:
                    fully_valid_take_count += 1
                else:
                    bad_takes.append(row)
        progress.step(category_dir.name)
    return {
        "category_count": len(category_dirs),
        "total_wavs": total_wavs,
        "expected_total_wavs": 11 * 20 * 25 * EXPECTED_OUTPUT_WAVS_PER_TAKE,
        "fully_valid_take_count": fully_valid_take_count,
        "all_zero_padded_take_count": all_zero_padded_take_count,
        "bad_takes": bad_takes,
        "take_rows": take_rows,
    }


def copy_transcripts(source_transcript_dir: Path, output_transcript_dir: Path) -> None:
    files = sorted(source_transcript_dir.glob("*.txt"))
    progress = ProgressBar(len(files), "Copying transcripts")
    ensure_dir(output_transcript_dir)
    for path in files:
        shutil.copy2(path, output_transcript_dir / path.name)
        progress.step(path.name)


def make_report_text(
    transcript_map: Dict[str, TranscriptInfo],
    dataset_audit: Dict[str, object],
    build_summary: Dict[str, object],
    output_verify: Dict[str, object],
) -> str:
    lines: List[str] = []
    lines.append("RINGKASAN PROSES PAPER DATASET SOTA")
    lines.append("")
    lines.append("Audit transkrip:")
    for category in sorted(transcript_map):
        info = transcript_map[category]
        lines.append(
            f"- {category}: kept={len(info.kept_ids)}, dropped={info.dropped_ids_from_entries}, note_ids={info.note_leading_ids}, note_ok={info.note_matches_entries}"
        )
    lines.append("")
    lines.append("Audit dataset asli:")
    lines.append(f"- category_count={dataset_audit['category_count']}")
    lines.append(f"- total_wavs={dataset_audit['total_wavs']}")
    lines.append(f"- expected_total_wavs={dataset_audit['expected_total_wavs']}")
    lines.append(f"- strict_valid_take_count={dataset_audit['strict_valid_take_count']}")
    lines.append(f"- strict_invalid_take_count={dataset_audit['strict_invalid_take_count']}")
    lines.append(f"- padding_style_distribution={dataset_audit['padding_style_distribution']}")
    for category in sorted(dataset_audit["categories"]):
        info = dataset_audit["categories"][category]
        lines.append(
            f"- {category}: respondents={info['respondent_count']}, take_dist={info['take_count_distribution']}, wav_dist={info['wav_count_distribution']}, strict_invalid={info['strict_invalid_take_count']}, padding_styles={info['padding_style_distribution']}"
        )
    lines.append("")
    lines.append("Hasil build dataset balance 19:")
    lines.append(f"- total_takes={build_summary['total_takes']}")
    lines.append(f"- total_copied_wavs={build_summary['total_copied_wavs']}")
    lines.append(f"- total_skipped_wavs={build_summary['total_skipped_wavs']}")
    lines.append(f"- expected_output_wavs={build_summary['expected_output_wavs']}")
    lines.append(f"- problem_take_count={build_summary['problem_take_count']}")
    lines.append(f"- normalized_output_name_style={build_summary['normalized_output_name_style']}")
    lines.append("")
    lines.append("Verifikasi output:")
    lines.append(f"- output_category_count={output_verify['category_count']}")
    lines.append(f"- output_total_wavs={output_verify['total_wavs']}")
    lines.append(f"- output_expected_total_wavs={output_verify['expected_total_wavs']}")
    lines.append(f"- output_bad_take_count={len(output_verify['bad_takes'])}")
    lines.append(f"- output_fully_valid_take_count={output_verify['fully_valid_take_count']}")
    lines.append(f"- output_all_zero_padded_take_count={output_verify['all_zero_padded_take_count']}")
    return "\n".join(lines) + "\n"


def make_report_md(
    transcript_map: Dict[str, TranscriptInfo],
    dataset_audit: Dict[str, object],
    build_summary: Dict[str, object],
    output_verify: Dict[str, object],
    output_root: Path,
) -> str:
    lines: List[str] = []
    lines.append("# PAPER DATASET SOTA PROCESS REPORT")
    lines.append("")
    lines.append(f"- Root kerja: `{output_root.parent}`")
    lines.append(f"- Output hasil: `{output_root}`")
    lines.append("")
    lines.append("## Audit Transkrip")
    lines.append("")
    for category in sorted(transcript_map):
        info = transcript_map[category]
        lines.append(f"- **{category}**")
        lines.append(f"  - kept_ids: `{info.kept_ids}`")
        lines.append(f"  - dropped_ids_from_entries: `{info.dropped_ids_from_entries}`")
        lines.append(f"  - note_leading_ids: `{info.note_leading_ids}`")
        lines.append(f"  - note_matches_entries: `{info.note_matches_entries}`")
    lines.append("")
    lines.append("## Audit Dataset Asli")
    lines.append("")
    lines.append(f"- total kategori: `{dataset_audit['category_count']}`")
    lines.append(f"- total wav asli: `{dataset_audit['total_wavs']}`")
    lines.append(f"- total wav ekspektasi: `{dataset_audit['expected_total_wavs']}`")
    lines.append(f"- take source valid ketat 1-20: `{dataset_audit['strict_valid_take_count']}`")
    lines.append(f"- take source bermasalah: `{dataset_audit['strict_invalid_take_count']}`")
    lines.append(f"- distribusi gaya penomoran source: `{dataset_audit['padding_style_distribution']}`")
    lines.append("")
    lines.append("## Hasil Build")
    lines.append("")
    lines.append(f"- total takes diproses: `{build_summary['total_takes']}`")
    lines.append(f"- total wav dicopy: `{build_summary['total_copied_wavs']}`")
    lines.append(f"- total wav di-skip: `{build_summary['total_skipped_wavs']}`")
    lines.append(f"- total wav output ekspektasi: `{build_summary['expected_output_wavs']}`")
    lines.append(f"- take build bermasalah: `{build_summary['problem_take_count']}`")
    lines.append(f"- gaya nama output ternormalisasi: `{build_summary['normalized_output_name_style']}`")
    lines.append("")
    lines.append("## Verifikasi Output")
    lines.append("")
    lines.append(f"- total kategori output: `{output_verify['category_count']}`")
    lines.append(f"- total wav output aktual: `{output_verify['total_wavs']}`")
    lines.append(f"- total wav output ekspektasi: `{output_verify['expected_total_wavs']}`")
    lines.append(f"- jumlah take bermasalah: `{len(output_verify['bad_takes'])}`")
    lines.append(f"- take output valid penuh: `{output_verify['fully_valid_take_count']}`")
    lines.append(f"- take output zero-padded: `{output_verify['all_zero_padded_take_count']}`")
    lines.append("")
    lines.append("## Catatan Penting")
    lines.append("")
    lines.append("- File yang dihapus mengikuti ID yang hilang dari transkrip aktif 01-20, bukan hasil ekstraksi semua angka di note.")
    lines.append("- Pendekatan ini mencegah salah baca note seperti `20 sengaja dibuang untuk penyetaraan 19 kalimat`, yang jika diparse sembarang bisa keliru menangkap `19` juga.")
    lines.append("- Semua file output dinamai ulang konsisten ke format `01.wav` s.d. `20.wav` sesuai ID aktif yang dipertahankan.")
    lines.append("- Struktur folder sumber tidak diubah; hasil disimpan ke folder output baru yang terisolasi.")
    lines.append("")
    return "\n".join(lines) + "\n"


def make_final_resume_md(
    transcript_map: Dict[str, TranscriptInfo],
    dataset_audit: Dict[str, object],
    build_summary: Dict[str, object],
    output_verify: Dict[str, object],
    output_root: Path,
) -> str:
    target_matched = (
        dataset_audit["strict_invalid_take_count"] == 0
        and build_summary["problem_take_count"] == 0
        and output_verify["total_wavs"] == output_verify["expected_total_wavs"]
        and len(output_verify["bad_takes"]) == 0
    )
    lines: List[str] = []
    lines.append("# FINAL RESUME PAPER DATASET SOTA V3")
    lines.append("")
    lines.append(f"- Output root: `{output_root}`")
    lines.append(f"- Status target akhir tercapai: `{target_matched}`")
    lines.append("")
    lines.append("## Ringkasan Audit Source")
    lines.append("")
    lines.append(f"- Kategori: `{dataset_audit['category_count']}`")
    lines.append(f"- Total take: `{11 * 20 * 25}`")
    lines.append(f"- Total wav source: `{dataset_audit['total_wavs']}`")
    lines.append(f"- Take source valid 1-20: `{dataset_audit['strict_valid_take_count']}`")
    lines.append(f"- Take source bermasalah: `{dataset_audit['strict_invalid_take_count']}`")
    lines.append(f"- Distribusi gaya penomoran source: `{dataset_audit['padding_style_distribution']}`")
    lines.append("")
    lines.append("## Ringkasan Aturan Transkrip")
    lines.append("")
    for category in sorted(transcript_map):
        info = transcript_map[category]
        lines.append(f"- `{category}`: keep `{len(info.kept_ids)}` kalimat, drop `{info.dropped_ids_from_entries}`")
    lines.append("")
    lines.append("## Ringkasan Build V3")
    lines.append("")
    lines.append(f"- Total take diproses: `{build_summary['total_takes']}`")
    lines.append(f"- Total wav dicopy: `{build_summary['total_copied_wavs']}`")
    lines.append(f"- Total wav diskip: `{build_summary['total_skipped_wavs']}`")
    lines.append(f"- Target wav output: `{build_summary['expected_output_wavs']}`")
    lines.append(f"- Take build bermasalah: `{build_summary['problem_take_count']}`")
    lines.append(f"- Format nama output: `{build_summary['normalized_output_name_style']}`")
    lines.append("")
    lines.append("## Ringkasan Verifikasi Output")
    lines.append("")
    lines.append(f"- Total wav output aktual: `{output_verify['total_wavs']}`")
    lines.append(f"- Total wav output ekspektasi: `{output_verify['expected_total_wavs']}`")
    lines.append(f"- Take output valid penuh: `{output_verify['fully_valid_take_count']}`")
    lines.append(f"- Take output zero-padded: `{output_verify['all_zero_padded_take_count']}`")
    lines.append(f"- Take output bermasalah: `{len(output_verify['bad_takes'])}`")
    lines.append("")
    lines.append("## Artefak Report")
    lines.append("")
    lines.append("- `reports/PROCESS_SUMMARY.txt`")
    lines.append("- `reports/PROCESS_REPORT.md`")
    lines.append("- `reports/dataset_audit_before.json`")
    lines.append("- `reports/build_summary.json`")
    lines.append("- `reports/output_verify.json`")
    lines.append("- `reports/dataset_take_audit.csv`")
    lines.append("- `reports/dataset_bad_take_audit.csv`")
    lines.append("- `reports/build_take_audit.csv`")
    lines.append("- `reports/build_problem_take_audit.csv`")
    lines.append("- `reports/output_take_verify.csv`")
    lines.append("- `reports/output_bad_take_verify.csv`")
    lines.append("")
    return "\n".join(lines) + "\n"


def to_serializable_transcript_map(transcript_map: Dict[str, TranscriptInfo]) -> Dict[str, object]:
    return {key: asdict(value) for key, value in transcript_map.items()}


def print_cli_summary(
    transcript_map: Dict[str, TranscriptInfo],
    dataset_audit: Dict[str, object],
    build_summary: Dict[str, object],
    output_verify: Dict[str, object],
    output_root: Path,
) -> None:
    print("\n=== SUMMARY ===")
    print(f"Output root           : {output_root}")
    print(f"Transcript categories : {len(transcript_map)}")
    print(f"Source total wavs     : {dataset_audit['total_wavs']}")
    print(f"Output total wavs     : {build_summary['total_copied_wavs']}")
    print(f"Skipped wavs          : {build_summary['total_skipped_wavs']}")
    print(f"Verified output wavs  : {output_verify['total_wavs']}")
    print(f"Source bad takes      : {dataset_audit['strict_invalid_take_count']}")
    print(f"Build problem takes   : {build_summary['problem_take_count']}")
    print(f"Bad output takes      : {len(output_verify['bad_takes'])}")
    for category in sorted(transcript_map):
        info = transcript_map[category]
        print(
            f"- {category}: kept={len(info.kept_ids)} dropped={info.dropped_ids_from_entries} note_ids={info.note_leading_ids} note_ok={info.note_matches_entries}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=str, default=str(Path(__file__).resolve().parent))
    parser.add_argument("--dataset-dir", type=str, default="Dataset_Ori")
    parser.add_argument("--transcript-dir", type=str, default="Transkrip_ASR_Jurnal_Dataset")
    parser.add_argument("--output-root", type=str, default="Processed_Balanced19")
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    dataset_dir = (root / args.dataset_dir).resolve()
    transcript_dir = (root / args.transcript_dir).resolve()
    output_root = (root / args.output_root).resolve()
    reports_dir = output_root / "reports"
    output_dataset_dir = output_root / "Dataset_Balanced19"
    output_transcript_dir = output_root / "Transkrip_ASR_Jurnal_Dataset"

    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset dir not found: {dataset_dir}")
    if not transcript_dir.exists():
        raise FileNotFoundError(f"Transcript dir not found: {transcript_dir}")
    if not args.skip_build and output_dataset_dir.exists() and any(output_dataset_dir.rglob(WAV_GLOB)):
        raise RuntimeError(f"Output dataset dir already contains wav files: {output_dataset_dir}")

    transcript_map = load_transcripts(transcript_dir)
    dataset_audit = audit_dataset(dataset_dir)

    build_summary: Dict[str, object]
    if args.skip_build:
        build_summary = {
            "total_takes": 0,
            "total_copied_wavs": 0,
            "total_skipped_wavs": 0,
            "expected_output_wavs": 11 * 20 * 25 * EXPECTED_OUTPUT_WAVS_PER_TAKE,
            "problem_take_count": 0,
            "normalized_output_name_style": "zero_padded_2_digit",
            "build_rows": [],
            "problem_rows": [],
        }
        output_verify = {
            "category_count": 0,
            "total_wavs": 0,
            "expected_total_wavs": 11 * 20 * 25 * EXPECTED_OUTPUT_WAVS_PER_TAKE,
            "fully_valid_take_count": 0,
            "all_zero_padded_take_count": 0,
            "bad_takes": [],
            "take_rows": [],
        }
    else:
        ensure_dir(output_root)
        copy_transcripts(transcript_dir, output_transcript_dir)
        build_summary = build_dataset(dataset_dir, output_dataset_dir, transcript_map)
        output_verify = verify_output_dataset(output_dataset_dir, transcript_map)

    transcript_json = to_serializable_transcript_map(transcript_map)
    audit_json = {
        "dataset_summary": {
            "category_count": dataset_audit["category_count"],
            "total_wavs": dataset_audit["total_wavs"],
            "expected_total_wavs": dataset_audit["expected_total_wavs"],
            "strict_valid_take_count": dataset_audit["strict_valid_take_count"],
            "strict_invalid_take_count": dataset_audit["strict_invalid_take_count"],
            "padding_style_distribution": dataset_audit["padding_style_distribution"],
        },
        "categories": dataset_audit["categories"],
    }
    build_json = {
        "summary": {
            key: value
            for key, value in build_summary.items()
            if key not in {"build_rows", "problem_rows"}
        }
    }
    verify_json = {
        "summary": {
            "category_count": output_verify["category_count"],
            "total_wavs": output_verify["total_wavs"],
            "expected_total_wavs": output_verify["expected_total_wavs"],
            "fully_valid_take_count": output_verify["fully_valid_take_count"],
            "all_zero_padded_take_count": output_verify["all_zero_padded_take_count"],
            "bad_take_count": len(output_verify["bad_takes"]),
        }
    }

    write_json(reports_dir / "transcript_map.json", transcript_json)
    write_json(reports_dir / "dataset_audit_before.json", audit_json)
    write_json(reports_dir / "build_summary.json", build_json)
    write_json(reports_dir / "output_verify.json", verify_json)
    write_csv(
        reports_dir / "dataset_take_audit.csv",
        dataset_audit["take_rows"],
        [
            "category",
            "respondent",
            "take",
            "wav_count",
            "numeric_wav_count",
            "padding_style",
            "is_strict_1_to_20",
            "missing_ids",
            "extra_ids",
            "duplicate_ids",
            "non_numeric_files",
        ],
    )
    write_csv(
        reports_dir / "dataset_bad_take_audit.csv",
        dataset_audit["bad_take_rows"],
        [
            "category",
            "respondent",
            "take",
            "wav_count",
            "numeric_wav_count",
            "padding_style",
            "missing_ids",
            "extra_ids",
            "duplicate_ids",
            "non_numeric_files",
        ],
    )
    write_csv(
        reports_dir / "build_take_audit.csv",
        build_summary["build_rows"],
        [
            "category",
            "respondent",
            "take",
            "copied_wavs",
            "expected_copied_wavs",
            "skipped_wavs",
            "missing_kept_wavs",
            "source_padding_style",
            "source_is_strict_1_to_20",
            "source_missing_ids",
            "source_extra_ids",
            "source_duplicate_ids",
            "source_non_numeric_files",
        ],
    )
    write_csv(
        reports_dir / "build_problem_take_audit.csv",
        build_summary["problem_rows"],
        [
            "category",
            "respondent",
            "take",
            "copied_wavs",
            "expected_copied_wavs",
            "skipped_wavs",
            "missing_kept_wavs",
            "source_padding_style",
            "source_is_strict_1_to_20",
            "source_missing_ids",
            "source_extra_ids",
            "source_duplicate_ids",
            "source_non_numeric_files",
        ],
    )
    write_csv(
        reports_dir / "output_take_verify.csv",
        output_verify["take_rows"],
        [
            "category",
            "respondent",
            "take",
            "wav_count",
            "expected_wav_count",
            "all_zero_padded_names",
            "missing_expected_names",
            "unexpected_names",
        ],
    )
    write_csv(
        reports_dir / "output_bad_take_verify.csv",
        output_verify["bad_takes"],
        [
            "category",
            "respondent",
            "take",
            "wav_count",
            "expected_wav_count",
            "all_zero_padded_names",
            "missing_expected_names",
            "unexpected_names",
        ],
    )
    text_report = make_report_text(transcript_map, dataset_audit, build_summary, output_verify)
    md_report = make_report_md(transcript_map, dataset_audit, build_summary, output_verify, output_root)
    final_resume_md = make_final_resume_md(transcript_map, dataset_audit, build_summary, output_verify, output_root)
    write_text(reports_dir / "PROCESS_SUMMARY.txt", text_report)
    write_text(reports_dir / "PROCESS_REPORT.md", md_report)
    write_text(output_root / "FINAL_RESUME.md", final_resume_md)
    print_cli_summary(transcript_map, dataset_audit, build_summary, output_verify, output_root)


if __name__ == "__main__":
    main()
