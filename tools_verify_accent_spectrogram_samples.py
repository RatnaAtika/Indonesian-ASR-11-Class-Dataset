#!/usr/bin/env python3
"""Verify generated accent spectrogram sample package."""

from __future__ import annotations

import csv
import json
import wave
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
PKG = ROOT / "Report_paper_9model" / "spectrogram_logat"
EXPECTED_RESPONDENTS = {
    "M7": "Padang",
    "F4": "Medan",
    "M8": "Jawa",
    "M3": "Jawa",
    "F5": "Bengkulu",
    "F3": "Maluku",
    "F1": "Palembang",
    "F2": "Palembang",
    "M6": "Baturaja",
}
EXPECTED_TRANSCRIPT = "Saya membutuhkan rekomendasi tempat wisata di kota Palembang"


def fail(errors: list[str]) -> None:
    if errors:
        print("FAIL: accent spectrogram package verification")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)


def main() -> None:
    errors: list[str] = []
    manifest_path = PKG / "manifest.json"
    if not manifest_path.exists():
        fail([f"missing {manifest_path}"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    samples = manifest.get("samples", [])
    if len(samples) != 9:
        errors.append(f"expected 9 samples, found {len(samples)}")
    seen = {s.get("respondent"): s for s in samples}
    if set(seen) != set(EXPECTED_RESPONDENTS):
        errors.append(f"respondent set mismatch: {sorted(seen)}")
    transcripts = {s.get("transcript") for s in samples}
    if transcripts != {EXPECTED_TRANSCRIPT}:
        errors.append(f"transcript mismatch: {transcripts}")
    if manifest.get("sentence_type") != "Kalimat_Deklaratif":
        errors.append("sentence_type is not Kalimat_Deklaratif")
    if manifest.get("sentence_id") != "1":
        errors.append("sentence_id is not 1")

    for respondent, region in EXPECTED_RESPONDENTS.items():
        sample = seen.get(respondent)
        if not sample:
            continue
        if sample.get("accent_region") != region:
            errors.append(f"region mismatch for {respondent}: {sample.get('accent_region')} != {region}")
        source_audio = str(sample.get("source_audio", ""))
        source = ROOT / source_audio
        png = ROOT / sample["spectrogram_png"]
        pdf = ROOT / sample["spectrogram_pdf"]
        # Source paths are intentionally redacted in the public package to avoid
        # exposing original respondent names. Verify media artifacts and only
        # inspect source audio when a real local path is present.
        for label, path in [("PNG", png), ("PDF", pdf)]:
            if not path.exists():
                errors.append(f"missing {label} for {respondent}: {path}")
        if source_audio.startswith("private_original_wav/"):
            pass
        elif source.exists():
            with wave.open(source.as_posix(), "rb") as wav:
                if wav.getframerate() != int(sample["sample_rate_hz"]):
                    errors.append(f"sample rate mismatch for {respondent}")
                if wav.getnchannels() != int(sample["channels"]):
                    errors.append(f"channel mismatch for {respondent}")
        else:
            errors.append(f"missing source audio for {respondent}: {source}")
        if png.exists():
            im = Image.open(png)
            if im.size[0] < 1500 or im.size[1] < 800:
                errors.append(f"PNG resolution too small for {respondent}: {im.size}")
        if pdf.exists() and pdf.stat().st_size < 1000:
            errors.append(f"PDF too small for {respondent}: {pdf}")

    combined_png = ROOT / manifest["outputs"]["combined_png"]
    combined_pdf = ROOT / manifest["outputs"]["combined_pdf"]
    report_pdf = ROOT / manifest["outputs"]["report_pdf"]
    for label, path in [("combined PNG", combined_png), ("combined PDF", combined_pdf), ("report PDF", report_pdf)]:
        if not path.exists():
            errors.append(f"missing {label}: {path}")
    if combined_png.exists():
        im = Image.open(combined_png)
        if im.size[0] < 2400 or im.size[1] < 1500:
            errors.append(f"combined PNG resolution too small: {im.size}")
    table_csv = PKG / "tables" / "accent_spectrogram_samples.csv"
    if not table_csv.exists():
        errors.append(f"missing {table_csv}")
    else:
        with table_csv.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if len(rows) != 9:
            errors.append(f"CSV row count mismatch: {len(rows)}")

    report_md = PKG / "reports" / "accent_spectrogram_report.md"
    caption_md = PKG / "captions" / "sciencedirect_figure_caption.md"
    for path in [report_md, caption_md, PKG / "README.md"]:
        if not path.exists() or path.stat().st_size < 100:
            errors.append(f"missing or too small documentation file: {path}")
    if report_md.exists():
        text = report_md.read_text(encoding="utf-8")
        for term in ["qualitative", "same category", "same transcript", "not by itself prove"]:
            if term not in text:
                errors.append(f"self-review/caveat term missing from report: {term}")

    fail(errors)
    print("OK: accent spectrogram package verified (9 matched declarative samples, figures, reports, and caveats)")


if __name__ == "__main__":
    main()
