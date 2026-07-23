#!/usr/bin/env python3
"""Deterministically extract manuscript content and structure from a DOCX."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

from docx import Document
from docx.document import Document as DocumentObject
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph
from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def repository_safe_path(path: Path) -> str:
    """Record a portable path without leaking a workstation location."""
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def iter_blocks(doc: DocumentObject):
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, doc)
        elif child.tag == qn("w:tbl"):
            yield Table(child, doc)


def paragraph_images(doc: DocumentObject, paragraph: Paragraph) -> list[str]:
    targets = []
    for element in paragraph._p.iter():
        if element.tag != qn("a:blip"):
            continue
        relation_id = element.get(qn("r:embed"))
        if relation_id and relation_id in doc.part.rels:
            targets.append(Path(doc.part.rels[relation_id].target_ref).name)
    return targets


def main(source: Path, destination: Path) -> None:
    source = source.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    media_dir = destination / "media"
    tables_dir = destination / "tables"
    media_dir.mkdir(exist_ok=True)
    tables_dir.mkdir(exist_ok=True)

    doc = Document(str(source))
    blocks = []
    markdown = [f"# Extracted manuscript — {source.name}", ""]
    raw_text = []
    style_counts = Counter()
    headings = []
    table_inventory = []
    paragraph_number = 0
    table_number = 0

    for block_number, block in enumerate(iter_blocks(doc), 1):
        if isinstance(block, Paragraph):
            paragraph_number += 1
            text = compact(block.text)
            style = block.style.name if block.style else ""
            images = paragraph_images(doc, block)
            style_counts[style] += 1
            blocks.append(
                {
                    "block": block_number,
                    "type": "paragraph",
                    "paragraph": paragraph_number,
                    "style": style,
                    "text": text,
                    "images": images,
                }
            )
            if not text:
                continue
            raw_text.append(text)
            if text.lower() in {"abstract", "a b s t r a c t"}:
                markdown.extend(["## Abstract", ""])
            elif re.match(r"^\d+(?:\.\d+)*\.?\s+", text):
                depth = min(2 + text.split()[0].count("."), 6)
                markdown.extend([f"{'#' * depth} {text}", ""])
                headings.append({"text": text, "style": style})
            elif style.lower().startswith("heading"):
                match = re.search(r"\d+", style)
                depth = min(int(match.group()) + 1 if match else 2, 6)
                markdown.extend([f"{'#' * depth} {text}", ""])
                headings.append({"text": text, "style": style})
            else:
                markdown.extend([text, ""])
        else:
            table_number += 1
            rows = [[compact(cell.text) for cell in row.cells] for row in block.rows]
            columns = max((len(row) for row in rows), default=0)
            rows = [row + [""] * (columns - len(row)) for row in rows]
            csv_path = tables_dir / f"table_{table_number:02d}.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as handle:
                csv.writer(handle).writerows(rows)
            blocks.append(
                {
                    "block": block_number,
                    "type": "table",
                    "table": table_number,
                    "rows": len(rows),
                    "columns": columns,
                    "preview": " | ".join(rows[0]) if rows else "",
                }
            )
            table_inventory.append(
                {"table": table_number, "rows": len(rows), "columns": columns, "file": str(csv_path.relative_to(destination))}
            )
            markdown.extend([f"### Extracted table {table_number}", ""])
            if rows:
                markdown.append("| " + " | ".join(cell.replace("|", "\\|") for cell in rows[0]) + " |")
                markdown.append("| " + " | ".join(["---"] * columns) + " |")
                for row in rows[1:]:
                    markdown.append("| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |")
                markdown.append("")
            raw_text.extend(" | ".join(row) for row in rows)

    archive_metrics = {}
    media_inventory = []
    with zipfile.ZipFile(source) as archive:
        for member in archive.namelist():
            if member.startswith("word/media/") and not member.endswith("/"):
                target = media_dir / Path(member).name
                target.write_bytes(archive.read(member))
                media_inventory.append({"file": target.name, "bytes": target.stat().st_size, "sha256": sha256(target)})
        document_xml = etree.fromstring(archive.read("word/document.xml"))
        archive_metrics = {
            "tracked_insertions": len(document_xml.xpath("//w:ins", namespaces=NS)),
            "tracked_deletions": len(document_xml.xpath("//w:del", namespaces=NS)),
            "hyperlinks": len(document_xml.xpath("//w:hyperlink", namespaces=NS)),
            "field_codes": len(document_xml.xpath("//w:instrText", namespaces=NS)),
            "comments_part": "word/comments.xml" in archive.namelist(),
            "footnotes_part": "word/footnotes.xml" in archive.namelist(),
            "endnotes_part": "word/endnotes.xml" in archive.namelist(),
        }

    text = "\n".join(raw_text)
    props = doc.core_properties
    inventory = {
        "source_file": source.name,
        "source_path": repository_safe_path(source),
        "source_bytes": source.stat().st_size,
        "source_sha256": sha256(source),
        "core_properties": {
            "title": props.title,
            "author": props.author,
            "last_modified_by": props.last_modified_by,
            "created": props.created.isoformat() if props.created else None,
            "modified": props.modified.isoformat() if props.modified else None,
        },
        "paragraph_count": paragraph_number,
        "nonempty_paragraph_count": sum(1 for item in blocks if item["type"] == "paragraph" and item["text"]),
        "word_count_approx": len(re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE)),
        "character_count": len(text),
        "table_count": table_number,
        "table_inventory": table_inventory,
        "inline_shape_count": len(doc.inline_shapes),
        "media_count": len(media_inventory),
        "media_inventory": media_inventory,
        "headings_detected": headings,
        "style_counts": dict(style_counts.most_common()),
        "section_count": len(doc.sections),
        "archive_metrics": archive_metrics,
    }

    (destination / "manuscript_text.md").write_text("\n".join(markdown).strip() + "\n", encoding="utf-8")
    (destination / "manuscript_raw.txt").write_text(text + "\n", encoding="utf-8")
    (destination / "block_sequence.json").write_text(json.dumps(blocks, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (destination / "document_inventory.json").write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (destination / "style_counts.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["style", "count"])
        writer.writerows(style_counts.most_common())
    print(json.dumps(inventory, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: extract_docx.py SOURCE.docx DESTINATION")
    main(Path(sys.argv[1]), Path(sys.argv[2]))
