#!/usr/bin/env python3
"""Audit Elsevier public paper artifacts for anonymized speaker IDs and English category labels."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from shutil import which

from PIL import Image

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "Whisper_Verification_Sessions" / "session_20260524_125144_dataset_statistics_viz_elsevier"
ORIGINAL_NAMES = [
    "Afgan", "Ammar", "Amri", "Baron", "Fajar", "Fito", "Harry", "Joni",
    "Muhaimin", "Pram", "Risky", "Robi", "Anggi", "Atika", "Bey", "Elisa",
    "Erlin", "Indah", "Nanda", "Uly", "Uli",
]
INDONESIAN_CATEGORY_TERMS = [
    "Kalimat_", "Deklaratif", "Klarifikasi", "Kondisional", "Konfirmasi",
    "Negasi", "Penjadwalan", "Perintah", "Persuasif", "Retoris", "Seruan",
    "Tanya",
]
TEXT_SUFFIXES = {".md", ".csv", ".json", ".tex", ".bib", ".py", ".txt"}
NAME_RE = re.compile(r"(?<![A-Za-z])(" + "|".join(map(re.escape, ORIGINAL_NAMES)) + r")(?![A-Za-z])", re.IGNORECASE)
CAT_RE = re.compile("|".join(map(re.escape, INDONESIAN_CATEGORY_TERMS)), re.IGNORECASE)


def text_from_pdf(path: Path) -> str:
    if not which("pdftotext"):
        return ""
    try:
        return subprocess.check_output(["pdftotext", path.as_posix(), "-"], stderr=subprocess.DEVNULL, timeout=30).decode("utf-8", "ignore")
    except Exception:
        return ""


def dark_pixels_touch_edge(im: Image.Image, strip_px: int = 4) -> dict[str, int]:
    """Detect likely text/axis clipping at the canvas boundary."""
    rgb = im.convert("RGB")
    w, h = rgb.size
    strips = {
        "left": rgb.crop((0, 0, strip_px, h)),
        "right": rgb.crop((w - strip_px, 0, w, h)),
        "top": rgb.crop((0, 0, w, strip_px)),
        "bottom": rgb.crop((0, h - strip_px, w, h)),
    }
    hits: dict[str, int] = {}
    for edge, crop in strips.items():
        n = sum(1 for px in crop.getdata() if min(px) < 245)
        if n > 10:
            hits[edge] = n
    return hits


def load_manifest_kinds() -> dict[str, str]:
    manifest = BASE / "figures" / "figure_manifest.csv"
    if not manifest.exists():
        return {}
    rows = manifest.read_text(encoding="utf-8", errors="ignore").splitlines()
    out: dict[str, str] = {}
    for line in rows[1:]:
        parts = line.split(",")
        if len(parts) >= 4:
            out[parts[2].split("/")[-1]] = parts[3]
    return out


def main() -> None:
    errors: list[dict[str, object]] = []
    checked = {"paths": 0, "text_files": 0, "pdf_text": 0, "png_images": 0}
    manifest_kinds = load_manifest_kinds()
    for path in BASE.rglob("*"):
        rel = path.relative_to(ROOT).as_posix()
        checked["paths"] += 1
        if NAME_RE.search(path.name):
            errors.append({"type": "name_in_filename", "path": rel})
        if CAT_RE.search(path.name):
            errors.append({"type": "indonesian_category_in_filename", "path": rel})
        if not path.is_file():
            continue
        text = ""
        if path.suffix.lower() in TEXT_SUFFIXES:
            checked["text_files"] += 1
            text = path.read_text(encoding="utf-8", errors="ignore")
        elif path.suffix.lower() == ".pdf":
            checked["pdf_text"] += 1
            text = text_from_pdf(path)
        if text:
            if NAME_RE.search(text):
                errors.append({"type": "name_in_text", "path": rel})
            if CAT_RE.search(text):
                errors.append({"type": "indonesian_category_in_text", "path": rel})
        if path.suffix.lower() == ".png":
            checked["png_images"] += 1
            if path.stat().st_size > 10_000_000:
                errors.append({"type": "png_larger_than_10mb", "path": rel, "size": path.stat().st_size})
            try:
                im = Image.open(path)
                dpi = im.info.get("dpi", (0, 0))[0] or 0
                # F11 is a halftone-style spectrogram panel; 300 DPI is enough,
                # but this package now uses 600 DPI for all public figures.
                min_dpi = 299 if "F11_mel_spectrogram" in path.name else 590
                if dpi < min_dpi:
                    errors.append({"type": "dpi_too_low", "path": rel, "dpi": dpi, "min_dpi": min_dpi})
                kind = manifest_kinds.get(path.name, "halftone" if "F11_mel_spectrogram" in path.name else "line")
                min_width_px = 2244 if kind == "halftone" else 3740
                if im.width < min_width_px:
                    errors.append({"type": "pixel_width_too_low_for_full_page", "path": rel, "width": im.width, "min_width": min_width_px, "kind": kind})
                physical_width_in = im.width / dpi if dpi else 0
                # Oversized physical width tends to be downscaled by publishers,
                # shrinking text.  Keep public figures near Elsevier full-page
                # width (190 mm = 7.48 in), with a small tolerance.
                if physical_width_in > 8.0:
                    errors.append({"type": "physical_width_too_large_for_readable_full_page", "path": rel, "width_in": round(physical_width_in, 2)})
                edge_hits = dark_pixels_touch_edge(im)
                if edge_hits:
                    errors.append({"type": "possible_text_or_axis_clipping_at_image_edge", "path": rel, "edge_hits": edge_hits})
            except Exception as exc:
                errors.append({"type": "image_open_failed", "path": rel, "error": str(exc)})
    summary = {"base": BASE.relative_to(ROOT).as_posix(), "checked": checked, "errors": errors}
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
