#!/usr/bin/env python3
"""Generate and verify GitHub navigation for the internal Draft_Paper tree."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
DRAFT = ROOT / "Draft_Paper"
README = DRAFT / "README.md"
INDEX = DRAFT / "GITHUB_FILE_INDEX.md"
AUDIT = DRAFT / "GITHUB_LINK_AUDIT.json"

EXCLUDED_PARTS = {".cache", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".swp", ".tmp"}
SENSITIVE_DRAFT_PATHS = {
    "00_Source/Draft Jurnal Data In Brief NSS-ID_ver3.docx",
    "01_Extraction/media/image13.jpeg",
    "01_Extraction/media_contact_sheet.jpg",
}
LINKIFY_TOP_LEVEL = {"02_Evidence", "03_Review", "04_Revised_Draft", "99_Admin"}
REPO_ROOT_PREFIXES = {
    "Colab_ASR_A100_Training",
    "Draft_Paper",
    "Processed_Balanced19_v3",
    "Report_paper_9model",
    "Whisper_Verification_Sessions",
    "metadata",
    "reports",
    "splits",
    "training",
    "training_conventional",
}
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
LINKED_CODE_RE = re.compile(r"\[`([^`\n]+)`\]\(([^)\n]+)\)")
CODE_RE = re.compile(r"`([^`\n]+)`")
LINE_SPEC_RE = re.compile(r"^(?P<path>.+?):(?P<lines>\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*)$")
INDEX_ENTRY_RE = re.compile(r"^- \[`([^`]+)`\]\(([^)]+)\) — ", re.MULTILINE)
LINE_ANCHOR_RE = re.compile(r"^L(\d+)(?:-L(\d+))?$")


@dataclass(frozen=True)
class LinkifyResult:
    text: str
    linked: int
    unresolved: list[dict[str, str | int]]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_publishable(path: Path, draft_root: Path | None = None) -> bool:
    if any(part in EXCLUDED_PARTS for part in path.parts) or path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    if draft_root is not None:
        try:
            relative = path.resolve().relative_to(draft_root.resolve()).as_posix()
        except ValueError:
            return True
        if relative in SENSITIVE_DRAFT_PATHS:
            return False
    return True


def publishable_files(draft_root: Path = DRAFT) -> list[Path]:
    return sorted(path for path in draft_root.rglob("*") if path.is_file() and is_publishable(path, draft_root))


def tracked_repo_paths(repo_root: Path = ROOT) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return {item.decode("utf-8") for item in result.stdout.split(b"\0") if item}


def split_line_spec(value: str) -> tuple[str, str | None]:
    match = LINE_SPEC_RE.match(value)
    if not match:
        return value, None
    return match.group("path"), match.group("lines")


def line_anchor(spec: str | None) -> str:
    if not spec:
        return ""
    first = spec.split(",", 1)[0]
    if "-" in first:
        start, end = first.split("-", 1)
        return f"#L{start}-L{end}"
    return f"#L{first}"


def looks_like_repo_path(value: str) -> bool:
    if not value or "MATERIAL GAP" in value or value.startswith(("http://", "https://", "mailto:")):
        return False
    if any(token in value for token in ("*", "{", "}", "<", ">", "|", "...")):
        return False
    path_text, _ = split_line_spec(value)
    if path_text.startswith(("/", "~", "$")) or re.match(r"^[A-Za-z]:[\\/]", path_text):
        return False
    if "\n" in path_text or "\t" in path_text:
        return False
    return "/" in path_text or bool(re.search(r"\.(?:md|csv|json|txt|py|docx|xlsx|png|jpe?g|svg|pdf|cff|tsv)$", path_text, re.I))


def _within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_reference(
    value: str,
    source: Path,
    repo_root: Path,
    tracked: set[str],
    *,
    require_github_availability: bool = True,
) -> tuple[Path, str | None] | None:
    path_text, lines = split_line_spec(value)
    candidates: list[Path] = []
    first_part = Path(path_text).parts[0] if Path(path_text).parts else ""
    if first_part in REPO_ROOT_PREFIXES:
        candidates.append(repo_root / path_text)
    else:
        # Relative references must resolve beside the source. Falling back to
        # the repository root can create a misleading link (for example, a
        # conceptual package README accidentally linking to the project README).
        candidates.append(source.parent / path_text)

    for candidate in candidates:
        resolved = candidate.resolve()
        if not resolved.exists() or not _within(resolved, repo_root.resolve()) or not is_publishable(resolved, repo_root / "Draft_Paper"):
            continue
        if require_github_availability and not _within(resolved, (repo_root / "Draft_Paper").resolve()):
            relative = resolved.relative_to(repo_root.resolve()).as_posix()
            if relative not in tracked:
                continue
        return resolved, lines
    return None


def relative_url(source: Path, target: Path, line_spec: str | None = None) -> str:
    relative = Path(os.path.relpath(target, start=source.parent)).as_posix()
    return quote(relative, safe="/._-") + line_anchor(line_spec)


def _strip_relinkable_code_links(line: str) -> str:
    def replace(match: re.Match[str]) -> str:
        label, url = match.group(1), match.group(2)
        if url.startswith(("http://", "https://", "mailto:")):
            return match.group(0)
        return f"`{label}`"

    return LINKED_CODE_RE.sub(replace, line)


def linkify_markdown_text(text: str, source: Path, repo_root: Path, tracked: set[str]) -> LinkifyResult:
    output: list[str] = []
    unresolved: list[dict[str, str | int]] = []
    linked = 0
    in_fence = False

    for line_number, original in enumerate(text.splitlines(keepends=True), 1):
        stripped = original.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            output.append(original)
            continue
        if in_fence:
            output.append(original)
            continue

        line = _strip_relinkable_code_links(original)
        protected_ranges = [match.span() for match in LINK_RE.finditer(line)]

        def replace(match: re.Match[str]) -> str:
            nonlocal linked
            if any(start <= match.start() < end for start, end in protected_ranges):
                return match.group(0)
            value = match.group(1)
            if not looks_like_repo_path(value):
                return match.group(0)
            resolved = resolve_reference(value, source, repo_root, tracked)
            if resolved is None:
                unresolved.append({"source": source.relative_to(repo_root).as_posix(), "line": line_number, "reference": value})
                return match.group(0)
            target, line_spec = resolved
            linked += 1
            return f"[`{value}`]({relative_url(source, target, line_spec)})"

        output.append(CODE_RE.sub(replace, line))

    return LinkifyResult("".join(output), linked, unresolved)


def markdown_sources_to_linkify(draft_root: Path = DRAFT) -> list[Path]:
    files: list[Path] = []
    for path in draft_root.rglob("*.md"):
        relative = path.relative_to(draft_root)
        if relative.parts and relative.parts[0] in LINKIFY_TOP_LEVEL and is_publishable(path, draft_root):
            files.append(path)
    return sorted(files)


def linkify_source_tree(draft_root: Path = DRAFT, repo_root: Path = ROOT) -> tuple[int, list[dict[str, str | int]]]:
    tracked = tracked_repo_paths(repo_root)
    total = 0
    unresolved: list[dict[str, str | int]] = []
    for path in markdown_sources_to_linkify(draft_root):
        result = linkify_markdown_text(path.read_text(encoding="utf-8"), path, repo_root, tracked)
        if result.text != path.read_text(encoding="utf-8"):
            path.write_text(result.text, encoding="utf-8")
        total += result.linked
        unresolved.extend(result.unresolved)
    unique = {
        (str(item["source"]), int(item["line"]), str(item["reference"])): item for item in unresolved
    }
    return total, [unique[key] for key in sorted(unique)]


def find_resolvable_unlinked_references(draft_root: Path = DRAFT, repo_root: Path = ROOT) -> list[dict[str, str | int]]:
    tracked = tracked_repo_paths(repo_root)
    findings: list[dict[str, str | int]] = []
    for source in markdown_sources_to_linkify(draft_root):
        in_fence = False
        for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            linked_ranges = [match.span() for match in LINKED_CODE_RE.finditer(line)]
            for match in CODE_RE.finditer(line):
                if any(start <= match.start() < end for start, end in linked_ranges):
                    continue
                value = match.group(1)
                if looks_like_repo_path(value) and resolve_reference(value, source, repo_root, tracked):
                    findings.append({"source": source.relative_to(repo_root).as_posix(), "line": line_number, "reference": value})
    return findings


def _iter_markdown_links(path: Path):
    in_fence = False
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in LINK_RE.finditer(line):
            yield line_number, match.group(1)


def check_markdown_links(draft_root: Path = DRAFT, repo_root: Path = ROOT) -> list[dict[str, str | int]]:
    broken: list[dict[str, str | int]] = []
    for source in sorted(draft_root.rglob("*.md")):
        if not is_publishable(source, draft_root):
            continue
        for line_number, url in _iter_markdown_links(source):
            if url.startswith(("http://", "https://", "mailto:", "#")):
                continue
            split = urlsplit(url)
            if not split.path:
                continue
            target = (source.parent / unquote(split.path)).resolve()
            finding = {"source": source.relative_to(repo_root).as_posix(), "line": line_number, "url": url}
            if not _within(target, repo_root.resolve()) or not target.exists() or not is_publishable(target, draft_root):
                finding["reason"] = "missing_or_unpublishable_target"
                broken.append(finding)
                continue
            anchor = LINE_ANCHOR_RE.fullmatch(split.fragment)
            if anchor:
                try:
                    line_count = len(target.read_text(encoding="utf-8", errors="strict").splitlines())
                except (UnicodeDecodeError, OSError):
                    finding["reason"] = "line_anchor_on_non_text_target"
                    broken.append(finding)
                    continue
                start = int(anchor.group(1))
                end = int(anchor.group(2) or start)
                if start < 1 or end < start or end > line_count:
                    finding["reason"] = f"line_anchor_out_of_range:{line_count}"
                    broken.append(finding)
    return broken


def format_size(value: int) -> str:
    units = ["B", "KiB", "MiB", "GiB"]
    amount = float(value)
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.0f} {unit}" if unit == "B" else f"{amount:.1f} {unit}"
        amount /= 1024
    raise AssertionError("unreachable")


def write_readme(path: Path = README) -> None:
    path.write_text(
        """# NSS-ID Draft Paper — GitHub Navigation

> **PRIVATE INTERNAL REVIEW ONLY — NOT FOR SUBMISSION OR PUBLIC RELEASE**
>
> Repositori GitHub ini masih privat. Tautan di bawah memerlukan akun yang memiliki akses. `PASS_INTERNAL_ONLY` bukan izin untuk menyerahkan artikel atau membuka dataset ke publik.

## Mulai dari sini

| Kebutuhan | Tautan langsung |
|---|---|
| Naskah DOCX terbaru | [`NSS-ID_INTERNAL_NOT_FOR_SUBMISSION.docx`](05_Submission_Package/NSS-ID_INTERNAL_NOT_FOR_SUBMISSION.docx) |
| Naskah Markdown kanonis | [`06_DATA_IN_BRIEF_TEMPLATE_MANUSCRIPT.md`](04_Revised_Draft/06_DATA_IN_BRIEF_TEMPLATE_MANUSCRIPT.md) |
| Evidence master lengkap | [`04_INTERNAL_WORKING_MANUSCRIPT.md`](04_Revised_Draft/04_INTERNAL_WORKING_MANUSCRIPT.md) |
| Workbook tabel editable | [`NSS-ID_EDITABLE_TABLES_INTERNAL_NOT_FOR_SUBMISSION.xlsx`](05_Submission_Package/NSS-ID_EDITABLE_TABLES_INTERNAL_NOT_FOR_SUBMISSION.xlsx) |
| Preview 14 halaman dari Microsoft Word | [`rendered_preview.pdf`](01_Extraction/template_aligned_internal/rendered_preview.pdf) |
| Contact sheet audit visual | [`rendered_preview_contact_sheet.jpg`](01_Extraction/template_aligned_internal/rendered_preview_contact_sheet.jpg) |
| Paket internal lengkap | [`05_Submission_Package/`](05_Submission_Package/) |
| Indeks seluruh file | [`GITHUB_FILE_INDEX.md`](GITHUB_FILE_INDEX.md) |
| Audit tautan | [`GITHUB_LINK_AUDIT.json`](GITHUB_LINK_AUDIT.json) |

## Status saat ini

- Template: **Elsevier Data in Brief v.19 (December 2024)**.
- Verifikasi mekanis: **PASS_INTERNAL_ONLY**.
- G0–G5: **NO-GO**; G6: **UNASSESSED**.
- Seluruh 33 token `[MATERIAL GAP: ...]` sengaja dipertahankan.
- Dataset Hugging Face dan repository GitHub tetap privat.
- Tiga artefak sumber yang berpotensi mengandung citra responden tetap lokal dan sengaja tidak diunggah; lihat [`00_Source/README.md`](00_Source/README.md).

## Peta folder

| Folder | Isi |
|---|---|
| [`00_Source/`](00_Source/) | Catatan custody dan hash; DOCX sumber asli tetap lokal karena kontrol privasi. |
| [`01_Extraction/`](01_Extraction/) | Ekstraksi deterministik, media, inventaris template, dan hasil render Word. |
| [`02_Evidence/`](02_Evidence/) | Evidence registry, questionnaire, referensi, audit benchmark, dan snapshot HF publik-terbatas. |
| [`03_Review/`](03_Review/) | Review editorial, metodologi, privasi, kesiapan, dan konformitas template. |
| [`04_Revised_Draft/`](04_Revised_Draft/) | Sumber naskah terbaru, tabel CSV, dan figur PNG/SVG. |
| [`05_Submission_Package/`](05_Submission_Package/) | Paket internal kanonis dengan DOCX, XLSX, tabel, figur, evidence, dan manifest SHA-256. |
| [`99_Admin/`](99_Admin/) | Builder deterministik, verifier, pengujian, desain, dan rencana kerja. |

## Bukti dan tindakan utama

- [Questionnaire bukti metode untuk penulis/institusi](02_Evidence/AUTHOR_METHODS_EVIDENCE_QUESTIONNAIRE.md)
- [Methods evidence matrix](02_Evidence/METHODS_EVIDENCE_MATRIX.csv)
- [Prior-publication overlap assessment](02_Evidence/PRIOR_PUBLICATION_OVERLAP_ASSESSMENT.md)
- [Package verification report](03_Review/11_INTERNAL_PACKAGE_VERIFICATION_REPORT.md)
- [Final delivery summary](03_Review/12_FINAL_DELIVERY_SUMMARY.md)
- [Data in Brief template conformance report](03_Review/15_DATA_IN_BRIEF_TEMPLATE_CONFORMANCE_REPORT.md)
- [Independent final template review](03_Review/16_FINAL_DATA_IN_BRIEF_TEMPLATE_REVIEW.md)

## Kebijakan tautan

Semua tautan internal menggunakan relative Markdown URLs sehingga dapat diklik di GitHub dan tetap valid setelah branch digabungkan. Referensi path yang benar-benar tersedia di repository diubah menjadi tautan. Referensi ke data lokal/diabaikan, artefak privat, atau file yang belum dipublikasikan sengaja tidak dibuat menjadi dead link dan dicatat dalam [`GITHUB_LINK_AUDIT.json`](GITHUB_LINK_AUDIT.json). Snapshot ekstraksi tidak ditulis ulang agar bukti ekstraksi tetap utuh.

## Reproduksi dan verifikasi

```bash
python3 Draft_Paper/99_Admin/build_internal_docx_package.py
python3 Draft_Paper/99_Admin/github_navigation.py
python3 -m unittest discover -s Draft_Paper/99_Admin -p 'test_*.py'
python3 Draft_Paper/99_Admin/verify_internal_manuscript_package.py
python3 Draft_Paper/99_Admin/github_navigation.py --check
```

## Batasan keras

Jangan menghapus penanda internal, memublikasikan repository/dataset, membuat DOI, atau mengirim naskah sebelum bukti etika, consent, hak/lisensi, privasi, akses, reproducibility, overlap artikel sebelumnya, deklarasi, dan persetujuan seluruh penulis ditutup dan disahkan.
""",
        encoding="utf-8",
    )


def write_file_index(path: Path = INDEX, draft_root: Path = DRAFT) -> None:
    files = [item for item in publishable_files(draft_root) if item.resolve() != path.resolve()]
    groups: dict[str, list[Path]] = {}
    for item in files:
        relative = item.relative_to(draft_root)
        key = relative.parts[0] if len(relative.parts) > 1 else "Root"
        groups.setdefault(key, []).append(item)

    lines = [
        "# Complete Draft_Paper File Index",
        "",
        "> **PRIVATE INTERNAL REVIEW ONLY — NOT FOR SUBMISSION OR PUBLIC RELEASE**",
        "",
        f"This deterministic index links **{len(files)} repository-safe files**. Ephemeral caches, compiled Python files, and the three source-only privacy exclusions documented in [`00_Source/README.md`](00_Source/README.md) are excluded.",
        "",
        "[← Back to Draft Paper README](README.md)",
        "",
    ]
    for group in sorted(groups, key=lambda item: (item == "Root", item)):
        lines.extend((f"## {group}", ""))
        for item in groups[group]:
            relative = item.relative_to(draft_root).as_posix()
            url = quote(relative, safe="/._-")
            lines.append(f"- [`{relative}`]({url}) — {format_size(item.stat().st_size)} — `{sha256(item)}`")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def indexed_targets(index: Path = INDEX) -> list[str]:
    results: list[str] = []
    for _label, url in INDEX_ENTRY_RE.findall(index.read_text(encoding="utf-8")):
        results.append(unquote(urlsplit(url).path))
    return results


def write_audit(
    linked: int,
    unresolved: list[dict[str, str | int]],
    broken: list[dict[str, str | int]],
    path: Path = AUDIT,
    draft_root: Path = DRAFT,
) -> None:
    payload = {
        "schema": "github_navigation_audit_v1",
        "scope": "Draft_Paper",
        "status": "PASS" if not broken else "FAIL",
        "linked_reference_count": linked,
        "unresolved_reference_count": len(unresolved),
        "broken_link_count": len(broken),
        "publishable_file_count_excluding_index": len(
            [item for item in publishable_files(draft_root) if item.name != "GITHUB_FILE_INDEX.md"]
        ),
        "linkification_scope": sorted(LINKIFY_TOP_LEVEL),
        "preserved_snapshot_scope": ["01_Extraction", "05_Submission_Package generated evidence copies"],
        "excluded_ephemeral_parts": sorted(EXCLUDED_PARTS),
        "excluded_sensitive_paths": sorted(SENSITIVE_DRAFT_PATHS),
        "unresolved_references": unresolved,
        "broken_links": broken,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def generate(draft_root: Path = DRAFT, repo_root: Path = ROOT) -> None:
    write_readme(draft_root / "README.md")
    linked, unresolved = linkify_source_tree(draft_root, repo_root)
    write_audit(linked, unresolved, [], draft_root=draft_root)
    write_file_index(draft_root / "GITHUB_FILE_INDEX.md", draft_root)
    broken = check_markdown_links(draft_root, repo_root)
    write_audit(linked, unresolved, broken, draft_root=draft_root)
    write_file_index(draft_root / "GITHUB_FILE_INDEX.md", draft_root)
    print(
        json.dumps(
            {
                "status": "PASS" if not broken else "FAIL",
                "linked_references": linked,
                "unresolved_references": len(unresolved),
                "broken_links": len(broken),
                "indexed_files": len(indexed_targets(draft_root / "GITHUB_FILE_INDEX.md")),
            },
            indent=2,
        )
    )
    if broken:
        raise SystemExit(1)


def check(draft_root: Path = DRAFT, repo_root: Path = ROOT) -> None:
    broken = check_markdown_links(draft_root, repo_root)
    unlinked = find_resolvable_unlinked_references(draft_root, repo_root)
    expected = {
        path.relative_to(draft_root).as_posix()
        for path in publishable_files(draft_root)
        if path.name != "GITHUB_FILE_INDEX.md"
    }
    indexed = set(indexed_targets(draft_root / "GITHUB_FILE_INDEX.md"))
    problems = {
        "broken_links": broken,
        "resolvable_unlinked_references": unlinked,
        "missing_index_entries": sorted(expected - indexed),
        "unexpected_index_entries": sorted(indexed - expected),
    }
    print(json.dumps(problems, indent=2))
    if any(problems.values()):
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify without modifying files")
    args = parser.parse_args()
    check() if args.check else generate()


if __name__ == "__main__":
    main()
