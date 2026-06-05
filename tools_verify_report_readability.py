from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "Report_paper_9model"
MANUSCRIPT = OUT / "manuscript" / "ScienceDirect_style_paper_report.md"
PDF = OUT / "Report_paper_9model_FULL_DETAIL.pdf"
SUMMARY = OUT / "tables" / "paper_9model_evidence_summary.md"
GENERATOR = ROOT / "tools_generate_report_paper_9model.py"


def fail(errors: list[str]) -> int:
    if errors:
        print("FAIL")
        for err in errors:
            print(f"- {err}")
        return 1
    print("OK: report readability checks passed")
    return 0


def main() -> int:
    errors: list[str] = []
    if not MANUSCRIPT.exists():
        errors.append(f"missing {MANUSCRIPT}")
    else:
        text = MANUSCRIPT.read_text(encoding="utf-8")
        table_lines = [line for line in text.splitlines() if line.startswith("|")]
        if table_lines:
            errors.append(
                "ScienceDirect manuscript draft should not inline wide Markdown tables; "
                f"found {len(table_lines)} pipe-table lines"
            )
        required_phrases = [
            "## 4. Results summary",
            "## 5. Evidence-backed compute and provenance summary",
            "For full audit paths, see",
        ]
        for phrase in required_phrases:
            if phrase not in text:
                errors.append(f"manuscript missing readability phrase: {phrase}")

    if not SUMMARY.exists():
        errors.append(f"missing PDF-friendly evidence summary {SUMMARY}")
    else:
        text = SUMMARY.read_text(encoding="utf-8")
        if "## m02b-whisper-small-ft" not in text or "## m09-dnn-hmm" not in text:
            errors.append("evidence summary must include per-model headings for all ranked models")
        if text.count("Best artifact exists:") != 9:
            errors.append("evidence summary must contain 9 best-artifact status lines")

    if not PDF.exists():
        errors.append(f"missing {PDF}")
    elif PDF.read_bytes()[:4] != b"%PDF":
        errors.append(f"{PDF} does not start with %PDF")

    if GENERATOR.exists():
        src = GENERATOR.read_text(encoding="utf-8")
        forbidden_calls = [
            'text_page("Evidence and provenance table", "\\n".join(evidence_md)',
            'text_page("ScienceDirect/Data in Brief-style manuscript draft", manuscript',
        ]
        for call in forbidden_calls:
            if call in src:
                errors.append(f"generator still sends raw wide Markdown to PDF: {call}")

    return fail(errors)


if __name__ == "__main__":
    raise SystemExit(main())
