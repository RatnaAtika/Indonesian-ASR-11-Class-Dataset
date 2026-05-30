from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
import time
from typing import Dict, List, Optional, Sequence, Tuple

# Heavy ML dependencies are imported lazily so --list-only diagnostics do not
# download/load Whisper or fail when the active shell is not the torch-gpu env.

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET_ROOT = PROJECT_ROOT / "Processed_Balanced19_v3" / "Dataset_Balanced19"
DEFAULT_TRANSCRIPT_DIR = PROJECT_ROOT / "Transkrip_ASR_Jurnal_Dataset"
DEFAULT_REPORT_BASE = PROJECT_ROOT / "Whisper_Verification"
SAFE_DEFAULT_MAX_FILES = 20
WAV_GLOB = "*.wav"
TRANSCRIPT_ENTRY_PATTERN = re.compile(r"^(\d{2})\|(.*)$")


@dataclass
class TranscriptSentence:
    sentence_id: int
    text: str
    normalized_text: str


@dataclass
class TranscriptCategory:
    category: str
    sentences: List[TranscriptSentence]

    @property
    def by_id(self) -> Dict[int, TranscriptSentence]:
        return {sentence.sentence_id: sentence for sentence in self.sentences}


@dataclass
class MatchResult:
    category: str
    respondent: str
    take: str
    wav_name: str
    wav_path: str
    expected_id: int
    expected_text: str
    predicted_text: str
    best_match_id: Optional[int]
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
class WhisperRuntime:
    model: object
    processor: object
    device: str
    dtype_name: str
    model_dtype: torch.dtype
    sampling_rate: int


class ProgressPrinter:
    def __init__(self, total: int, label: str) -> None:
        self.total = total
        self.label = label
        self.current = 0
        self.started_at = time.perf_counter()
        self.last_detail = ""

    def step(self, detail: str) -> None:
        self.current += 1
        self.last_detail = detail
        self.render()

    def render(self) -> None:
        total = max(self.total, 1)
        ratio = self.current / total
        filled = int(ratio * 28)
        bar = ("#" * filled).ljust(28, ".")
        elapsed = max(time.perf_counter() - self.started_at, 0.0)
        eta_seconds = 0.0
        if self.current > 0 and self.current < total:
            eta_seconds = (elapsed / self.current) * (total - self.current)
        detail = self.last_detail
        if len(detail) > 60:
            detail = "..." + detail[-57:]
        message = (
            f"\r{self.label} [{bar}] {self.current}/{total} "
            f"({ratio * 100:5.1f}%) elapsed={elapsed:6.1f}s eta={eta_seconds:6.1f}s {detail}"
        )
        print(message, end="", flush=True)
        if self.current >= total:
            print()


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).lower().strip()
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = normalized.replace("_", " ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_transcripts(transcript_dir: Path) -> Dict[str, TranscriptCategory]:
    transcript_map: Dict[str, TranscriptCategory] = {}
    for path in sorted(transcript_dir.glob("*.txt")):
        sentences: List[TranscriptSentence] = []
        for raw_line in read_text(path).splitlines():
            line = raw_line.strip()
            match = TRANSCRIPT_ENTRY_PATTERN.match(line)
            if match is None:
                continue
            sentence_id = int(match.group(1))
            text = match.group(2).strip()
            sentences.append(
                TranscriptSentence(
                    sentence_id=sentence_id,
                    text=text,
                    normalized_text=normalize_text(text),
                )
            )
        if not sentences:
            raise RuntimeError(f"Tidak ada entri transkrip valid di {path}")
        transcript_map[path.stem] = TranscriptCategory(category=path.stem, sentences=sentences)
    if not transcript_map:
        raise RuntimeError(f"Tidak ada file transkrip ditemukan di {transcript_dir}")
    return transcript_map


def parse_filter_values(raw_value: str) -> Optional[set[str]]:
    if not raw_value.strip():
        return None
    return {item.strip() for item in raw_value.split(",") if item.strip()}


def iter_dirs(root: Path) -> List[Path]:
    return sorted([path for path in root.iterdir() if path.is_dir()])


def matches_filter(name: str, allowed_values: Optional[set[str]]) -> bool:
    return allowed_values is None or name in allowed_values


def append_take_wavs(wav_paths: List[Path], take_dir: Path, max_files: int) -> bool:
    for wav_path in sorted(take_dir.glob(WAV_GLOB)):
        wav_paths.append(wav_path)
        if max_files > 0 and len(wav_paths) >= max_files:
            return True
    return False


def collect_wav_files(
    dataset_root: Path,
    category_filter: Optional[set[str]],
    respondent_filter: Optional[set[str]],
    take_filter: Optional[set[str]],
    max_files: int,
) -> List[Path]:
    wav_paths: List[Path] = []
    for category_dir in iter_dirs(dataset_root):
        if not matches_filter(category_dir.name, category_filter):
            continue
        for respondent_dir in iter_dirs(category_dir):
            if not matches_filter(respondent_dir.name, respondent_filter):
                continue
            for take_dir in iter_dirs(respondent_dir):
                if not matches_filter(take_dir.name, take_filter):
                    continue
                if append_take_wavs(wav_paths, take_dir, max_files):
                    return wav_paths
    return wav_paths


def build_whisper_pipeline(model_id: str):
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

    torch_device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id,
        dtype=torch_dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True,
    )
    model.to(torch_device)
    model.eval()
    processor = AutoProcessor.from_pretrained(model_id)
    return WhisperRuntime(
        model=model,
        processor=processor,
        device=torch_device,
        dtype_name=str(torch_dtype).replace("torch.", ""),
        model_dtype=torch_dtype,
        sampling_rate=processor.feature_extractor.sampling_rate,
    )


def compute_similarity(left: str, right: str) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    sequence_score = SequenceMatcher(None, left, right).ratio()
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    if not left_tokens or not right_tokens:
        token_score = 0.0
    else:
        token_score = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
    return (0.85 * sequence_score) + (0.15 * token_score)


def load_audio_samples(wav_path: Path, target_sampling_rate: int) -> "np.ndarray":
    import numpy as np
    import soundfile as sf

    audio_array, sampling_rate = sf.read(str(wav_path), dtype="float32")
    if isinstance(audio_array, np.ndarray) and audio_array.ndim > 1:
        audio_array = audio_array.mean(axis=1)
    if sampling_rate != target_sampling_rate:
        raise RuntimeError(
            f"Sampling rate WAV {wav_path} adalah {sampling_rate}, expected {target_sampling_rate}. "
            "Resampling otomatis tidak diaktifkan untuk menghindari dependency torchaudio/torchcodec."
        )
    return np.asarray(audio_array, dtype=np.float32)


def transcribe_wav(runtime: WhisperRuntime, wav_path: Path, language: str, task: str) -> str:
    import torch

    audio_array = load_audio_samples(wav_path, runtime.sampling_rate)
    processed = runtime.processor.feature_extractor(
        audio_array,
        sampling_rate=runtime.sampling_rate,
        return_tensors="pt",
        return_attention_mask=True,
    )
    generate_inputs = {
        "input_features": processed["input_features"].to(device=runtime.device, dtype=runtime.model_dtype)
    }
    attention_mask = processed.get("attention_mask")
    if attention_mask is not None:
        generate_inputs["attention_mask"] = attention_mask.to(device=runtime.device)
    generate_kwargs = {"task": task}
    if language:
        generate_kwargs["language"] = language
    with torch.inference_mode():
        generated_ids = runtime.model.generate(**generate_inputs, **generate_kwargs)
    predicted_text = runtime.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return str(predicted_text).strip()


def split_wav_location(wav_path: Path, dataset_root: Path) -> Tuple[str, str, str, str]:
    relative_parts = wav_path.relative_to(dataset_root).parts
    if len(relative_parts) < 4:
        raise RuntimeError(f"Struktur path WAV tidak sesuai: {wav_path}")
    return relative_parts[0], relative_parts[1], relative_parts[2], relative_parts[3]


def make_error_result(wav_path: Path, dataset_root: Path, error_message: str) -> MatchResult:
    try:
        category, respondent, take, wav_name = split_wav_location(wav_path, dataset_root)
    except Exception:
        category, respondent, take, wav_name = "", "", "", wav_path.name
    return MatchResult(
        category=category,
        respondent=respondent,
        take=take,
        wav_name=wav_name,
        wav_path=str(wav_path),
        expected_id=int(wav_path.stem) if wav_path.stem.isdigit() else -1,
        expected_text="",
        predicted_text="",
        best_match_id=None,
        best_match_text="",
        exact_normalized_match=False,
        expected_similarity=0.0,
        best_similarity=0.0,
        matches_expected_id=False,
        passes_threshold=False,
        likely_mismatch=False,
        status="error",
        error_message=error_message,
    )


def evaluate_wav(
    wav_path: Path,
    dataset_root: Path,
    transcript_map: Dict[str, TranscriptCategory],
    runtime: WhisperRuntime,
    language: str,
    task: str,
    similarity_threshold: float,
) -> MatchResult:
    category, respondent, take, wav_name = split_wav_location(wav_path, dataset_root)
    expected_id = int(wav_path.stem)
    transcript_info = transcript_map.get(category)
    if transcript_info is None:
        raise RuntimeError(f"Kategori transkrip '{category}' tidak ditemukan")
    expected_sentence = transcript_info.by_id.get(expected_id)
    if expected_sentence is None:
        raise RuntimeError(f"ID transkrip {expected_id:02d} tidak ditemukan untuk kategori {category}")
    predicted_text = transcribe_wav(runtime, wav_path, language=language, task=task)
    normalized_prediction = normalize_text(predicted_text)
    best_match: Optional[TranscriptSentence] = None
    best_similarity = -1.0
    for candidate in transcript_info.sentences:
        candidate_similarity = compute_similarity(normalized_prediction, candidate.normalized_text)
        if candidate_similarity > best_similarity:
            best_similarity = candidate_similarity
            best_match = candidate
    expected_similarity = compute_similarity(normalized_prediction, expected_sentence.normalized_text)
    best_match_id = best_match.sentence_id if best_match is not None else None
    best_match_text = best_match.text if best_match is not None else ""
    exact_normalized_match = normalized_prediction == expected_sentence.normalized_text
    matches_expected_id = best_match_id == expected_id
    passes_threshold = matches_expected_id and expected_similarity >= similarity_threshold
    likely_mismatch = best_match_id is not None and best_match_id != expected_id and best_similarity >= similarity_threshold
    return MatchResult(
        category=category,
        respondent=respondent,
        take=take,
        wav_name=wav_name,
        wav_path=str(wav_path),
        expected_id=expected_id,
        expected_text=expected_sentence.text,
        predicted_text=predicted_text,
        best_match_id=best_match_id,
        best_match_text=best_match_text,
        exact_normalized_match=exact_normalized_match,
        expected_similarity=round(expected_similarity, 6),
        best_similarity=round(best_similarity if best_similarity >= 0 else 0.0, 6),
        matches_expected_id=matches_expected_id,
        passes_threshold=passes_threshold,
        likely_mismatch=likely_mismatch,
        status="ok",
        error_message="",
    )


def evaluate_dataset(
    wav_paths: Sequence[Path],
    dataset_root: Path,
    transcript_map: Dict[str, TranscriptCategory],
    runtime: WhisperRuntime,
    language: str,
    task: str,
    similarity_threshold: float,
) -> List[MatchResult]:
    progress = ProgressPrinter(len(wav_paths), "Whisper verify")
    results: List[MatchResult] = []
    for wav_path in wav_paths:
        relative_path = str(wav_path.relative_to(dataset_root))
        try:
            result = evaluate_wav(
                wav_path=wav_path,
                dataset_root=dataset_root,
                transcript_map=transcript_map,
                runtime=runtime,
                language=language,
                task=task,
                similarity_threshold=similarity_threshold,
            )
        except Exception as exc:
            result = make_error_result(wav_path, dataset_root, str(exc))
        results.append(result)
        progress.step(relative_path)
    return results


def summarize_results(
    results: Sequence[MatchResult],
    similarity_threshold: float,
    model_id: str,
    dataset_root: Path,
    transcript_dir: Path,
    report_dir: Path,
    language: str,
    task: str,
) -> Dict[str, object]:
    ok_results = [result for result in results if result.status == "ok"]
    error_results = [result for result in results if result.status != "ok"]
    by_category: Dict[str, Dict[str, object]] = {}
    for result in results:
        category_summary = by_category.setdefault(
            result.category,
            {
                "files": 0,
                "ok": 0,
                "errors": 0,
                "exact_normalized_matches": 0,
                "best_match_expected_id": 0,
                "passes_threshold": 0,
                "likely_mismatches": 0,
                "avg_expected_similarity": 0.0,
                "avg_best_similarity": 0.0,
            },
        )
        category_summary["files"] += 1
        if result.status == "ok":
            category_summary["ok"] += 1
            category_summary["exact_normalized_matches"] += int(result.exact_normalized_match)
            category_summary["best_match_expected_id"] += int(result.matches_expected_id)
            category_summary["passes_threshold"] += int(result.passes_threshold)
            category_summary["likely_mismatches"] += int(result.likely_mismatch)
            category_summary["avg_expected_similarity"] += result.expected_similarity
            category_summary["avg_best_similarity"] += result.best_similarity
        else:
            category_summary["errors"] += 1
    for category_summary in by_category.values():
        ok_count = category_summary["ok"]
        if ok_count > 0:
            category_summary["avg_expected_similarity"] = round(category_summary["avg_expected_similarity"] / ok_count, 6)
            category_summary["avg_best_similarity"] = round(category_summary["avg_best_similarity"] / ok_count, 6)
    summary = {
        "config": {
            "model_id": model_id,
            "language": language,
            "task": task,
            "similarity_threshold": similarity_threshold,
            "dataset_root": str(dataset_root),
            "transcript_dir": str(transcript_dir),
            "report_dir": str(report_dir),
        },
        "summary": {
            "total_files": len(results),
            "ok_files": len(ok_results),
            "error_files": len(error_results),
            "exact_normalized_match_count": sum(int(result.exact_normalized_match) for result in ok_results),
            "best_match_expected_id_count": sum(int(result.matches_expected_id) for result in ok_results),
            "pass_threshold_count": sum(int(result.passes_threshold) for result in ok_results),
            "likely_mismatch_count": sum(int(result.likely_mismatch) for result in ok_results),
            "average_expected_similarity": round(
                sum(result.expected_similarity for result in ok_results) / len(ok_results), 6
            )
            if ok_results
            else 0.0,
            "average_best_similarity": round(
                sum(result.best_similarity for result in ok_results) / len(ok_results), 6
            )
            if ok_results
            else 0.0,
        },
        "by_category": by_category,
    }
    return summary


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: Sequence[MatchResult]) -> None:
    fieldnames = [field.name for field in MatchResult.__dataclass_fields__.values()]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def make_text_report(summary: Dict[str, object]) -> str:
    lines: List[str] = []
    config = summary["config"]
    aggregate = summary["summary"]
    lines.append("WHISPER VERIFICATION REPORT PAPER DATASET SOTA")
    lines.append("")
    lines.append(f"model_id={config['model_id']}")
    lines.append(f"language={config['language']}")
    lines.append(f"task={config['task']}")
    lines.append(f"similarity_threshold={config['similarity_threshold']}")
    lines.append(f"dataset_root={config['dataset_root']}")
    lines.append(f"transcript_dir={config['transcript_dir']}")
    lines.append(f"report_dir={config['report_dir']}")
    lines.append("")
    for key, value in aggregate.items():
        lines.append(f"{key}={value}")
    lines.append("")
    lines.append("Per kategori:")
    for category in sorted(summary["by_category"]):
        category_summary = summary["by_category"][category]
        lines.append(
            f"- {category}: files={category_summary['files']} ok={category_summary['ok']} errors={category_summary['errors']} exact={category_summary['exact_normalized_matches']} best_match_expected={category_summary['best_match_expected_id']} pass={category_summary['passes_threshold']} likely_mismatch={category_summary['likely_mismatches']} avg_expected_similarity={category_summary['avg_expected_similarity']} avg_best_similarity={category_summary['avg_best_similarity']}"
        )
    lines.append("")
    return "\n".join(lines)


def make_markdown_report(summary: Dict[str, object], mismatch_rows: Sequence[MatchResult]) -> str:
    config = summary["config"]
    aggregate = summary["summary"]
    lines: List[str] = []
    lines.append("# WHISPER VERIFICATION REPORT PAPER DATASET SOTA")
    lines.append("")
    lines.append(f"- Model: `{config['model_id']}`")
    lines.append(f"- Language: `{config['language']}`")
    lines.append(f"- Task: `{config['task']}`")
    lines.append(f"- Similarity threshold: `{config['similarity_threshold']}`")
    lines.append(f"- Dataset root: `{config['dataset_root']}`")
    lines.append(f"- Transcript dir: `{config['transcript_dir']}`")
    lines.append(f"- Report dir: `{config['report_dir']}`")
    lines.append("")
    lines.append("## Ringkasan")
    lines.append("")
    for key, value in aggregate.items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Per Kategori")
    lines.append("")
    for category in sorted(summary["by_category"]):
        category_summary = summary["by_category"][category]
        lines.append(f"- **{category}**")
        lines.append(f"  - files: `{category_summary['files']}`")
        lines.append(f"  - ok: `{category_summary['ok']}`")
        lines.append(f"  - errors: `{category_summary['errors']}`")
        lines.append(f"  - exact_normalized_matches: `{category_summary['exact_normalized_matches']}`")
        lines.append(f"  - best_match_expected_id: `{category_summary['best_match_expected_id']}`")
        lines.append(f"  - pass_threshold: `{category_summary['passes_threshold']}`")
        lines.append(f"  - likely_mismatch: `{category_summary['likely_mismatches']}`")
        lines.append(f"  - avg_expected_similarity: `{category_summary['avg_expected_similarity']}`")
        lines.append(f"  - avg_best_similarity: `{category_summary['avg_best_similarity']}`")
    lines.append("")
    lines.append("## Kandidat Mismatch")
    lines.append("")
    if not mismatch_rows:
        lines.append("- Tidak ada kandidat mismatch pada threshold saat ini.")
    else:
        for row in mismatch_rows[:50]:
            lines.append(
                f"- `{row.wav_path}` | expected `{row.expected_id:02d}` -> best `{(row.best_match_id if row.best_match_id is not None else -1):02d}` | expected_similarity `{row.expected_similarity}` | best_similarity `{row.best_similarity}`"
            )
    lines.append("")
    return "\n".join(lines)


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def make_report_dir(report_base: Path) -> Path:
    timestamp = datetime.now().strftime("run_%Y%m%d_%H%M%S")
    report_dir = report_base / timestamp
    ensure_directory(report_dir)
    return report_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--transcript-dir", type=Path, default=DEFAULT_TRANSCRIPT_DIR)
    parser.add_argument("--report-base", type=Path, default=DEFAULT_REPORT_BASE)
    parser.add_argument("--model-id", default="openai/whisper-large-v3")
    parser.add_argument("--language", default="indonesian")
    parser.add_argument("--task", default="transcribe")
    parser.add_argument("--similarity-threshold", type=float, default=0.75)
    parser.add_argument(
        "--max-files",
        type=int,
        default=SAFE_DEFAULT_MAX_FILES,
        help=f"Jumlah WAV yang diproses. Default aman: {SAFE_DEFAULT_MAX_FILES}. Gunakan --full-run untuk semua file.",
    )
    parser.add_argument("--full-run", action="store_true", help="Izinkan proses semua WAV. Mengganti max-files menjadi 0.")
    parser.add_argument("--list-only", action="store_true", help="Tampilkan file WAV yang akan diproses tanpa memuat Whisper.")
    parser.add_argument("--category", default="")
    parser.add_argument("--respondent", default="")
    parser.add_argument("--take", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset_root = args.dataset_root.resolve()
    transcript_dir = args.transcript_dir.resolve()
    report_base = args.report_base.resolve()
    if not dataset_root.exists():
        raise RuntimeError(f"Dataset root tidak ditemukan: {dataset_root}")
    if not transcript_dir.exists():
        raise RuntimeError(f"Transcript dir tidak ditemukan: {transcript_dir}")
    category_filter = parse_filter_values(args.category)
    respondent_filter = parse_filter_values(args.respondent)
    take_filter = parse_filter_values(args.take)
    max_files = 0 if args.full_run else args.max_files
    if max_files <= 0 and not args.full_run:
        raise RuntimeError("--max-files 0 sekarang wajib disertai --full-run agar tidak sengaja memproses seluruh dataset")
    transcript_map = load_transcripts(transcript_dir)
    wav_paths = collect_wav_files(
        dataset_root=dataset_root,
        category_filter=category_filter,
        respondent_filter=respondent_filter,
        take_filter=take_filter,
        max_files=max_files,
    )
    if not wav_paths:
        raise RuntimeError("Tidak ada file WAV yang cocok dengan filter yang diberikan")
    print(f"Collected WAV files: {len(wav_paths)}")
    if args.list_only:
        for wav_path in wav_paths[:100]:
            print(wav_path)
        if len(wav_paths) > 100:
            print(f"... {len(wav_paths) - 100} more")
        return
    report_dir = make_report_dir(report_base)
    runtime = build_whisper_pipeline(args.model_id)
    results = evaluate_dataset(
        wav_paths=wav_paths,
        dataset_root=dataset_root,
        transcript_map=transcript_map,
        runtime=runtime,
        language=args.language,
        task=args.task,
        similarity_threshold=args.similarity_threshold,
    )
    mismatch_rows = [row for row in results if row.status == "ok" and row.likely_mismatch]
    summary = summarize_results(
        results=results,
        similarity_threshold=args.similarity_threshold,
        model_id=args.model_id,
        dataset_root=dataset_root,
        transcript_dir=transcript_dir,
        report_dir=report_dir,
        language=args.language,
        task=args.task,
    )
    summary["runtime"] = {
        "device": runtime.device,
        "torch_dtype": runtime.dtype_name,
        "generated_at": datetime.now().isoformat(),
    }
    ensure_directory(report_dir)
    write_csv(report_dir / "whisper_match_details.csv", results)
    write_csv(report_dir / "whisper_mismatch_only.csv", mismatch_rows)
    write_json(report_dir / "whisper_summary.json", summary)
    (report_dir / "whisper_report.txt").write_text(make_text_report(summary), encoding="utf-8")
    (report_dir / "whisper_report.md").write_text(make_markdown_report(summary, mismatch_rows), encoding="utf-8")
    print("=== WHISPER VERIFY SUMMARY ===")
    for key, value in summary["summary"].items():
        print(f"{key}: {value}")
    print(f"device: {runtime.device}")
    print(f"torch_dtype: {runtime.dtype_name}")
    print(f"report_dir: {report_dir}")


if __name__ == "__main__":
    main()
