#!/usr/bin/env python3
"""Generate paper-ready accent spectrogram samples for the 9 named respondents.

The script deliberately uses targeted paths under Dataset_Ori/Kalimat_Deklaratif
and metadata/dataset_metadata_clean.csv; it does not scan the whole audio tree.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import wave
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image as PdfImage
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parent
DATASET_ROOT = ROOT / "Dataset_Ori" / "Kalimat_Deklaratif"
METADATA_CSV = ROOT / "metadata" / "dataset_metadata_clean.csv"
OUTPUT_DIR = ROOT / "Report_paper_9model" / "spectrogram_logat"

SENTENCE_ID = "1"
CATEGORY = "Kalimat_Deklaratif"
TRANSCRIPT_EXPECTED = "Saya membutuhkan rekomendasi tempat wisata di kota Palembang"

RESPONDENTS = [
    ("Harry", "Padang", "Padang representative"),
    ("Elisa", "Medan", "Medan representative"),
    ("Joni", "Jawa", "Javanese representative 1"),
    ("Amri", "Jawa", "Javanese representative 2"),
    ("Erlin", "Bengkulu", "Bengkulu representative"),
    ("Bey", "Maluku", "Maluku representative"),
    ("Anggi", "Palembang", "Palembang representative 1"),
    ("Atika", "Palembang", "Palembang representative 2"),
    ("Fito", "Baturaja", "Baturaja representative"),
]


@dataclass
class Sample:
    respondent: str
    accent_region: str
    category: str
    sentence_id: str
    transcript: str
    source_audio: str
    take_number: int
    duration_sec: float
    sample_rate_hz: int
    channels: int
    bits_per_sample: int
    frames: int
    file_size_bytes: int
    sha256_16: str
    spectrogram_png: str
    spectrogram_pdf: str


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def human_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(n)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} GB"


def take_number(path: Path) -> int:
    match = re.search(r"take\s*([0-9]+)", path.parent.name, flags=re.IGNORECASE)
    return int(match.group(1)) if match else 999


def preferred_audio_path(respondent: str) -> Path:
    base = DATASET_ROOT / respondent
    candidates = sorted(base.glob("**/01.wav"), key=lambda p: (take_number(p), str(p)))
    if not candidates:
        raise FileNotFoundError(f"No 01.wav candidates for {respondent} under {base}")
    return candidates[0]


def metadata_lookup() -> dict[tuple[str, str], dict[str, str]]:
    rows: dict[tuple[str, str], dict[str, str]] = {}
    with METADATA_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["category"] != CATEGORY:
                continue
            if row["sentence_id"] != SENTENCE_ID:
                continue
            if row["is_synthetic"] != "False":
                continue
            rows[(row["speaker_id"], row["wav_name"])] = row
    return rows


def wav_info(path: Path) -> dict[str, float | int]:
    with wave.open(path.as_posix(), "rb") as wav:
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        sample_rate = wav.getframerate()
        frames = wav.getnframes()
        return {
            "channels": channels,
            "sample_rate_hz": sample_rate,
            "bits_per_sample": sample_width * 8,
            "frames": frames,
            "duration_sec": frames / float(sample_rate),
        }


def sha256_16(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def run_sox_spectrogram(audio: Path, out_png: Path, title: str) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "sox",
        audio.as_posix(),
        "-n",
        "spectrogram",
        "-x",
        "1800",
        "-y",
        "900",
        "-z",
        "100",
        "-w",
        "Kaiser",
        "-t",
        title,
        "-c",
        "Sentence 01, declarative, original WAV; SoX STFT spectrogram",
        "-o",
        out_png.as_posix(),
    ]
    subprocess.run(cmd, check=True, cwd=ROOT)


def png_to_pdf(png: Path, pdf: Path, title: str) -> None:
    pdf.parent.mkdir(parents=True, exist_ok=True)
    if pdf.exists():
        pdf.unlink()
    doc = SimpleDocTemplate(pdf.as_posix(), pagesize=landscape(A4), rightMargin=1.0 * cm, leftMargin=1.0 * cm, topMargin=1.0 * cm, bottomMargin=1.0 * cm)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 0.3 * cm)]
    story.append(PdfImage(png.as_posix(), width=27.0 * cm, height=13.5 * cm))
    doc.build(story)


def make_grid(samples: list[Sample], grid_png: Path, grid_pdf: Path) -> None:
    images = [Image.open(ROOT / s.spectrogram_png).convert("RGB") for s in samples]
    # Crop a little vertical whitespace but keep axes/legend. Resize uniformly for 3x3 paper plate.
    cell_w, cell_h = 900, 520
    label_h = 56
    margin = 30
    grid_w = 3 * cell_w + 4 * margin
    grid_h = 3 * (cell_h + label_h) + 4 * margin
    canvas = Image.new("RGB", (grid_w, grid_h), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
        font_sub = ImageFont.truetype("DejaVuSans.ttf", 18)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
    for idx, (img, sample) in enumerate(zip(images, samples)):
        row, col = divmod(idx, 3)
        x = margin + col * (cell_w + margin)
        y = margin + row * (cell_h + label_h + margin)
        resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.BICUBIC)
        resized = img.resize((cell_w, cell_h), resample)
        canvas.paste(resized, (x, y + label_h))
        draw.text((x, y), f"{idx + 1}. {sample.respondent} — {sample.accent_region}", fill="black", font=font_title)
        draw.text((x, y + 28), f"{sample.duration_sec:.2f} s, {sample.sample_rate_hz/1000:.1f} kHz, sentence 01", fill="black", font=font_sub)
    grid_png.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(grid_png, dpi=(300, 300), optimize=True)
    png_to_pdf(grid_png, grid_pdf, "Figure. Accent spectrogram panel for matched Indonesian declarative utterance")


def write_csv(samples: list[Sample], csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(asdict(samples[0]).keys())
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for sample in samples:
            writer.writerow(asdict(sample))


def write_markdown_table(samples: list[Sample], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "| Respondent | Accent/region represented | Source audio | Duration (s) | Spectrogram |",
        "|---|---|---|---:|---|",
    ]
    for s in samples:
        lines.append(f"| {s.respondent} | {s.accent_region} | `{s.source_audio}` | {s.duration_sec:.3f} | `{s.spectrogram_png}` |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_tex_table(samples: list[Sample], path: Path) -> None:
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Matched declarative utterance samples used for regional-accent spectrogram inspection.}",
        r"\label{tab:accent-spectrogram-samples}",
        r"\begin{tabular}{llllr}",
        r"\hline",
        r"No. & Respondent & Region represented & Sentence ID & Duration (s) \\",
        r"\hline",
    ]
    for i, s in enumerate(samples, 1):
        lines.append(f"{i} & {s.respondent} & {s.accent_region} & {s.sentence_id} & {s.duration_sec:.3f} \\")
    lines.extend([r"\hline", r"\end{tabular}", r"\end{table}"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_caption_files(output_dir: Path) -> None:
    caption = (
        "Figure X. Representative spectrograms for one matched Indonesian declarative utterance "
        "('Saya membutuhkan rekomendasi tempat wisata di kota Palembang') spoken by nine respondents "
        "representing Padang, Medan, Jawa, Bengkulu, Maluku, Baturaja, and Palembang. "
        "All panels were generated from original WAV recordings using the same SoX STFT spectrogram "
        "settings, enabling visual comparison of accent-related acoustic patterns while holding lexical "
        "content constant. The figure is intended as qualitative evidence only; no dialect classification "
        "claim is made from this single-sentence sample."
    )
    (output_dir / "captions").mkdir(parents=True, exist_ok=True)
    (output_dir / "captions" / "sciencedirect_figure_caption.md").write_text(caption + "\n", encoding="utf-8")
    tex_caption = r"\caption{" + caption.replace("'", "`") + r"}" + "\n"
    (output_dir / "captions" / "sciencedirect_figure_caption.tex").write_text(tex_caption, encoding="utf-8")


def write_reports(samples: list[Sample], output_dir: Path, grid_png: Path, grid_pdf: Path) -> None:
    reports = output_dir / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Accent spectrogram sample report")
    lines.append("")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append("This package provides one spectrogram sample per selected respondent for a matched Indonesian declarative sentence. The goal is to support qualitative paper discussion of regional-accent variation while keeping sentence content and sentence type constant.")
    lines.append("")
    lines.append("## Matched utterance")
    lines.append("")
    lines.append(f"- Sentence type: declarative (`{CATEGORY}`)")
    lines.append(f"- Sentence ID: `{SENTENCE_ID}` / file `01.wav`")
    lines.append(f"- Transcript: **{TRANSCRIPT_EXPECTED}**")
    lines.append("- Source: original WAV files under `Dataset_Ori/Kalimat_Deklaratif/<Respondent>/.../01.wav`")
    lines.append("- Spectrogram generation: SoX STFT spectrogram, 1800 x 900 px individual panels, Kaiser window, common settings for all speakers.")
    lines.append("")
    lines.append("## Paper-ready outputs")
    lines.append("")
    lines.append(f"- Combined figure PNG: `{rel(grid_png)}`")
    lines.append(f"- Combined figure PDF: `{rel(grid_pdf)}`")
    lines.append("- Individual respondent PNG/PDF: `figures/individual/`")
    lines.append("- Sample metadata CSV/JSON/Markdown/LaTeX: `tables/` and `manifest.json`")
    lines.append("- ScienceDirect-style caption: `captions/sciencedirect_figure_caption.md` and `.tex`")
    lines.append("")
    lines.append("## Respondent mapping")
    lines.append("")
    lines.append("| No. | Respondent | Region represented | Audio source | Duration (s) | Sample rate |")
    lines.append("|---:|---|---|---|---:|---:|")
    for i, s in enumerate(samples, 1):
        lines.append(f"| {i} | {s.respondent} | {s.accent_region} | `{s.source_audio}` | {s.duration_sec:.3f} | {s.sample_rate_hz} Hz |")
    lines.append("")
    lines.append("## Interpretation guidance")
    lines.append("")
    lines.append("- Use these spectrograms as qualitative, illustrative material for a paper figure or appendix.")
    lines.append("- The matched sentence controls lexical content, but it does not by itself prove dialect/accent separability.")
    lines.append("- Any claim about accent should be phrased cautiously, e.g., 'representative examples of acoustic variation across respondent regions' rather than 'classifier-ready accent proof'.")
    lines.append("- For a stronger accent analysis, add multiple sentences per respondent and quantitative features such as F0 contour, formants, duration, energy, and spectral centroid.")
    lines.append("")
    lines.append("## Quality/self-review notes")
    lines.append("")
    lines.append("- All nine selected samples use the same category, same sentence ID, and same transcript.")
    lines.append("- All nine samples are original/non-synthetic WAV recordings according to `metadata/dataset_metadata_clean.csv`.")
    lines.append("- Individual and combined figures are generated with identical spectrogram settings.")
    lines.append("- Figures are suitable as paper/appendix assets; the final manuscript can choose either the 3x3 combined panel or individual respondent panels.")
    text = "\n".join(lines) + "\n"
    (reports / "accent_spectrogram_report.md").write_text(text, encoding="utf-8")
    (reports / "accent_spectrogram_report.txt").write_text(text, encoding="utf-8")
    write_report_pdf(samples, reports / "accent_spectrogram_report.pdf", grid_png)


def write_report_pdf(samples: list[Sample], pdf: Path, grid_png: Path) -> None:
    if pdf.exists():
        pdf.unlink()
    doc = SimpleDocTemplate(pdf.as_posix(), pagesize=A4, rightMargin=1.5 * cm, leftMargin=1.5 * cm, topMargin=1.4 * cm, bottomMargin=1.4 * cm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10))
    story = []
    story.append(Paragraph("Accent Spectrogram Sample Report", styles["Title"]))
    story.append(Paragraph("ScienceDirect/Data in Brief support artifact", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(f"Matched utterance: <b>{TRANSCRIPT_EXPECTED}</b>", styles["BodyText"]))
    story.append(Paragraph("Sentence type: declarative; source: original non-synthetic WAV files.", styles["BodyText"]))
    story.append(Spacer(1, 0.3 * cm))
    table_data = [["No.", "Respondent", "Region", "Duration", "Source"]]
    for i, s in enumerate(samples, 1):
        table_data.append([str(i), s.respondent, s.accent_region, f"{s.duration_sec:.3f} s", s.source_audio])
    table = Table(table_data, colWidths=[0.8 * cm, 2.4 * cm, 2.8 * cm, 1.8 * cm, 10.0 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAEAEA")),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
    ]))
    story.append(table)
    story.append(PageBreak())
    story.append(Paragraph("Combined 3x3 spectrogram panel", styles["Heading1"]))
    story.append(PdfImage(grid_png.as_posix(), width=18.0 * cm, height=12.0 * cm))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Caption: Representative spectrograms for one matched Indonesian declarative utterance spoken by nine respondents representing Padang, Medan, Jawa, Bengkulu, Maluku, Baturaja, and Palembang. The figure is qualitative and should not be interpreted as standalone dialect-classification evidence.", styles["Small"]))
    doc.build(story)


def write_readme(output_dir: Path) -> None:
    text = f"""# Spectrogram logat / accent samples

This folder contains paper-ready spectrogram assets for one matched declarative utterance spoken by nine respondents.

- Sentence: **{TRANSCRIPT_EXPECTED}**
- Category: `{CATEGORY}`
- Source type: original/non-synthetic WAV from `Dataset_Ori`
- Generation tool: `tools_generate_accent_spectrogram_samples.py` using SoX spectrogram + ReportLab PDF generation

## Where to start

1. Read `reports/accent_spectrogram_report.md` or `.pdf`.
2. Use `figures/combined/accent_spectrogram_grid.png` for a 3x3 paper figure.
3. Use `captions/sciencedirect_figure_caption.md` for the ScienceDirect-style caption.
4. Use `tables/accent_spectrogram_samples.csv` for metadata/provenance.

## Caveat

These figures are qualitative samples for paper illustration. They are not, by themselves, a statistical proof of regional accent separability.
"""
    (output_dir / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    if shutil.which("sox") is None:
        raise RuntimeError("sox is required to generate spectrogram PNG files")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for sub in ["figures/individual", "figures/combined", "tables", "reports", "captions"]:
        (OUTPUT_DIR / sub).mkdir(parents=True, exist_ok=True)

    meta = metadata_lookup()
    samples: list[Sample] = []
    for respondent, region, _note in RESPONDENTS:
        audio = preferred_audio_path(respondent)
        row = meta.get((respondent, "01.wav"))
        if not row:
            raise RuntimeError(f"No clean metadata row for {respondent} sentence {SENTENCE_ID}")
        if row["transcript"] != TRANSCRIPT_EXPECTED:
            raise RuntimeError(f"Transcript mismatch for {respondent}: {row['transcript']!r}")
        info = wav_info(audio)
        stem = f"{respondent.lower()}_{region.lower()}_declarative_sentence01"
        png = OUTPUT_DIR / "figures" / "individual" / f"{stem}_spectrogram.png"
        pdf = OUTPUT_DIR / "figures" / "individual" / f"{stem}_spectrogram.pdf"
        title = f"{respondent} ({region}) — declarative sentence 01"
        run_sox_spectrogram(audio, png, title)
        png_to_pdf(png, pdf, title)
        samples.append(Sample(
            respondent=respondent,
            accent_region=region,
            category=CATEGORY,
            sentence_id=SENTENCE_ID,
            transcript=TRANSCRIPT_EXPECTED,
            source_audio=rel(audio),
            take_number=take_number(audio),
            duration_sec=round(float(info["duration_sec"]), 4),
            sample_rate_hz=int(info["sample_rate_hz"]),
            channels=int(info["channels"]),
            bits_per_sample=int(info["bits_per_sample"]),
            frames=int(info["frames"]),
            file_size_bytes=audio.stat().st_size,
            sha256_16=sha256_16(audio),
            spectrogram_png=rel(png),
            spectrogram_pdf=rel(pdf),
        ))

    grid_png = OUTPUT_DIR / "figures" / "combined" / "accent_spectrogram_grid.png"
    grid_pdf = OUTPUT_DIR / "figures" / "combined" / "accent_spectrogram_grid.pdf"
    make_grid(samples, grid_png, grid_pdf)

    manifest = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "purpose": "Matched declarative-utterance spectrogram samples for regional-accent paper analysis.",
        "sentence_type": CATEGORY,
        "sentence_id": SENTENCE_ID,
        "transcript": TRANSCRIPT_EXPECTED,
        "selection_policy": "First available original Take1 01.wav per requested respondent; all share the same declarative transcript.",
        "spectrogram_method": "SoX STFT spectrogram, 1800x900 px individual panels, Kaiser window, z-range 100 dB.",
        "outputs": {
            "combined_png": rel(grid_png),
            "combined_pdf": rel(grid_pdf),
            "report_md": rel(OUTPUT_DIR / "reports" / "accent_spectrogram_report.md"),
            "report_pdf": rel(OUTPUT_DIR / "reports" / "accent_spectrogram_report.pdf"),
            "caption_md": rel(OUTPUT_DIR / "captions" / "sciencedirect_figure_caption.md"),
        },
        "samples": [asdict(s) for s in samples],
    }
    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(samples, OUTPUT_DIR / "tables" / "accent_spectrogram_samples.csv")
    write_markdown_table(samples, OUTPUT_DIR / "tables" / "accent_spectrogram_samples.md")
    write_tex_table(samples, OUTPUT_DIR / "tables" / "accent_spectrogram_samples.tex")
    write_caption_files(OUTPUT_DIR)
    write_reports(samples, OUTPUT_DIR, grid_png, grid_pdf)
    write_readme(OUTPUT_DIR)
    print(f"Generated {len(samples)} samples in {rel(OUTPUT_DIR)}")
    print(f"Combined figure: {rel(grid_png)}")
    print(f"Report PDF: {rel(OUTPUT_DIR / 'reports' / 'accent_spectrogram_report.pdf')}")


if __name__ == "__main__":
    main()
