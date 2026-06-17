#!/usr/bin/env python3
"""Create a copy-only small-files package for Hugging Face upload staging.

The source files remain in their original folders. This script copies only the
small, newly generated public HF-support artifacts into a tidy package folder
and writes manifests/notes for larger assets that must be uploaded from their
original locations.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT / "Report_paper_9model" / "hf_upload_small_files"
SMALL_LIMIT_BYTES = 10_000_000

COPY_SOURCES = [
    # Public anonymization / speaker-label package
    (ROOT / "Report_paper_9model" / "hf_anonymization", PACKAGE / "metadata" / "speaker_labels"),
    # Public full-scope dataset information package
    (ROOT / "Report_paper_9model" / "hf_dataset_information_public", PACKAGE / "paper" / "dataset_information"),
]

DOC_FILES = [
    # Do not copy the full local upload plan into the HF package because it
    # references private local crosswalk paths. Keep only public-facing reports.
    (ROOT / "Report_paper_9model" / "HF_DATASET_INFORMATION_SELECTION.md", PACKAGE / "docs" / "HF_DATASET_INFORMATION_SELECTION.md"),
    (ROOT / "Report_paper_9model" / "HF_DATASET_INFORMATION_FINAL_REPORT.md", PACKAGE / "docs" / "HF_DATASET_INFORMATION_FINAL_REPORT.md"),
    (ROOT / "Report_paper_9model" / "hf_dataset_information_selection.csv", PACKAGE / "docs" / "hf_dataset_information_selection.csv"),
    (ROOT / "Report_paper_9model" / "hf_dataset_information_selection.json", PACKAGE / "docs" / "hf_dataset_information_selection.json"),
]

LARGE_ASSET_NOTES = [
    {
        "asset": "Final processed ASR dataset",
        "local_source": "Processed_Balanced19_v3/Dataset_Balanced19/",
        "hf_target": "data/processed_balanced19_v3/Dataset_Balanced19/",
        "approx_size": "about 16 GB",
        "action": "Upload from original path during HF large-folder upload; do not move or modify source.",
    },
    {
        "asset": "Raw/original audio (optional, consent-gated)",
        "local_source": "Dataset_Ori/",
        "hf_target": "data/raw_original/",
        "approx_size": "about 17 GB",
        "action": "Upload only if consent/license allows; keep original folder unchanged.",
    },
    {
        "asset": "Final 9-model best artifacts",
        "local_source": "Report_paper_9model/model_artifacts/rank*/best_artifact/",
        "hf_target": "models/final_9model_benchmark/rank*/best_artifact/",
        "approx_size": "about 1.26 GB",
        "action": "Upload from original artifact package; do not commit large weights to GitHub.",
    },
    {
        "asset": "Full benchmark predictions CSV files",
        "local_source": "Final run directories test_results/predictions.csv",
        "hf_target": "models/final_9model_benchmark/rank*/run_outputs/predictions.csv",
        "approx_size": "about 23.4 MB total",
        "action": "Upload from original final run directories; GitHub intentionally skipped these >1 MB files.",
    },
    {
        "asset": "Paper-clean legacy statistics subset (optional)",
        "local_source": "reports/dataset_statistics_v7_paper9/",
        "hf_target": "paper/dataset_information/paper_clean_subset_optional/",
        "approx_size": "small/moderate",
        "action": "Upload only with clear label paper-clean/statistics subset; prefer regenerated full-scope package in this small-files folder.",
    },
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_file(src: Path, dst: Path) -> dict:
    if not src.exists():
        raise FileNotFoundError(src)
    size = src.stat().st_size
    if size > SMALL_LIMIT_BYTES:
        raise RuntimeError(f"Refusing to copy >{SMALL_LIMIT_BYTES} byte file: {src} ({size})")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return {
        "source_path": src.relative_to(ROOT).as_posix(),
        "package_path": dst.relative_to(ROOT).as_posix(),
        "hf_target_path": dst.relative_to(PACKAGE).as_posix(),
        "size_bytes": dst.stat().st_size,
        "sha256": sha256(dst),
    }


def main() -> None:
    if PACKAGE.exists():
        shutil.rmtree(PACKAGE)
    PACKAGE.mkdir(parents=True)

    rows: list[dict] = []
    for src_dir, dst_dir in COPY_SOURCES:
        for src in sorted(src_dir.rglob("*")):
            if src.is_file():
                rows.append(copy_file(src, dst_dir / src.relative_to(src_dir)))
    for src, dst in DOC_FILES:
        rows.append(copy_file(src, dst))

    generated_at = datetime.now().isoformat(timespec="seconds")
    total_bytes = sum(r["size_bytes"] for r in rows)

    manifest = {
        "generated_at": generated_at,
        "purpose": "Small public HF upload staging package. Files are copies; original source folders are unchanged.",
        "small_file_limit_bytes": SMALL_LIMIT_BYTES,
        "file_count": len(rows),
        "total_bytes": total_bytes,
        "total_human": f"{total_bytes / 1024:.1f} KB",
        "files": rows,
        "large_assets_to_upload_from_original_locations": LARGE_ASSET_NOTES,
    }
    (PACKAGE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with (PACKAGE / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["source_path", "package_path", "hf_target_path", "size_bytes", "sha256"]
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    large_md = ["# Large HF Assets — Upload From Original Locations", "", "The small-files package copies only newly generated small public artifacts. The following large assets stay in their original folders and should be included during the actual Hugging Face upload.", ""]
    for item in LARGE_ASSET_NOTES:
        large_md.extend([
            f"## {item['asset']}",
            "",
            f"- Local source: `{item['local_source']}`",
            f"- HF target: `{item['hf_target']}`",
            f"- Approx. size: {item['approx_size']}",
            f"- Action: {item['action']}",
            "",
        ])
    (PACKAGE / "LARGE_ASSETS_TO_UPLOAD_FROM_ORIGINAL_LOCATIONS.md").write_text("\n".join(large_md), encoding="utf-8")

    (PACKAGE / "README.md").write_text(
        f"""# HF Upload Small Files Package

Generated: {generated_at}

This folder is a tidy, copy-only staging package for small public artifacts that should be uploaded to Hugging Face.

- File count: {len(rows)}
- Total size: {total_bytes / 1024:.1f} KB
- Source folders are unchanged.
- Private crosswalks are not included.
- Large audio/model assets are not copied here; see `LARGE_ASSETS_TO_UPLOAD_FROM_ORIGINAL_LOCATIONS.md`.

Recommended HF upload placement: copy the contents of this folder into the root of the HF staging directory, then add the large assets from their original folders.
""",
        encoding="utf-8",
    )
    print(f"Created {PACKAGE} with {len(rows)} files ({total_bytes / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
