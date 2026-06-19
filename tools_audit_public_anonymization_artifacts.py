#!/usr/bin/env python3
"""Audit public paper artifacts for original respondent-name leakage.

Scope is intentionally limited to the two user-requested public artifact folders:
- Report_paper_9model/spectrogram_logat
- Whisper_Verification_Sessions/session_20260524_125144_dataset_statistics_viz_elsevier
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGETS = [
    ROOT / "Report_paper_9model" / "spectrogram_logat",
    ROOT / "Whisper_Verification_Sessions" / "session_20260524_125144_dataset_statistics_viz_elsevier",
]
ORIGINAL_NAMES = [
    "Afgan", "Ammar", "Amri", "Baron", "Fajar", "Fito", "Harry", "Joni",
    "Muhaimin", "Pram", "Risky", "Robi", "Anggi", "Atika", "Bey", "Elisa",
    "Erlin", "Indah", "Nanda", "Uly", "Uli",
]
TEXT_SUFFIXES = {".md", ".csv", ".json", ".tex", ".bib", ".py", ".txt"}
NAME_RE = re.compile(r"(?<![A-Za-z])(" + "|".join(re.escape(n) for n in ORIGINAL_NAMES) + r")(?![A-Za-z])", re.IGNORECASE)


def scan_text(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [m.group(1) for m in NAME_RE.finditer(text)]


def scan_pdf_text(path: Path) -> list[str]:
    if not shutil_which("pdftotext"):
        return []
    try:
        text = subprocess.check_output(["pdftotext", path.as_posix(), "-"], stderr=subprocess.DEVNULL, timeout=30).decode("utf-8", "ignore")
    except Exception:
        return []
    return [m.group(1) for m in NAME_RE.finditer(text)]


def shutil_which(cmd: str) -> str | None:
    from shutil import which
    return which(cmd)


def main() -> None:
    errors: list[dict[str, object]] = []
    checked = {"filenames": 0, "text_files": 0, "pdf_text": 0}
    for target in TARGETS:
        if not target.exists():
            errors.append({"type": "missing_target", "path": target.as_posix()})
            continue
        for path in target.rglob("*"):
            rel = path.relative_to(ROOT).as_posix()
            if NAME_RE.search(path.name):
                errors.append({"type": "filename", "path": rel, "matches": NAME_RE.findall(path.name)})
            checked["filenames"] += 1
            if not path.is_file():
                continue
            if path.suffix.lower() in TEXT_SUFFIXES:
                checked["text_files"] += 1
                matches = scan_text(path)
                if matches:
                    errors.append({"type": "text", "path": rel, "matches": sorted(set(matches))})
            elif path.suffix.lower() == ".pdf":
                checked["pdf_text"] += 1
                matches = scan_pdf_text(path)
                if matches:
                    errors.append({"type": "pdf_text", "path": rel, "matches": sorted(set(matches))})
    summary = {"checked": checked, "errors": errors, "target_count": len(TARGETS)}
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
