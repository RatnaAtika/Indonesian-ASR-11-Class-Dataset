#!/usr/bin/env python3
"""Build the synthetic-data PDF report (inlines S1-S4 figures), compressed."""
import re, fitz
from pathlib import Path
from PIL import Image
from markdown_pdf import MarkdownPdf, Section

HERE = Path(__file__).resolve().parent
MD = HERE / "SYNTHETIC_DATA_REPORT_elsevier.md"
PDF = HERE / "SYNTHETIC_DATA_REPORT_elsevier.pdf"
FIG = HERE / "figures"
PDFDIR = FIG / "png_pdf"; PDFDIR.mkdir(exist_ok=True)

# downscale PNGs for light PDF embedding
for p in sorted(FIG.glob("S*.png")):
    im = Image.open(p); w, h = im.size
    if w > 1400: im = im.resize((1400, int(h * 1400 / w)))
    im.save(PDFDIR / p.name, optimize=True)

md = MD.read_text(encoding="utf-8")
inlined = set(); out = []; in_index = False
for line in md.splitlines():
    if line.startswith("## Figure index"): in_index = True
    out.append(line)
    if in_index: continue
    for m in re.finditer(r"\bS(\d)\b", line):
        tag = "S" + m.group(1)
        if tag in inlined: continue
        hits = sorted(PDFDIR.glob(f"{tag}_*.png"))
        if hits:
            out += ["", f"![{tag}]({hits[0].name})", ""]; inlined.add(tag)
final = "\n".join(out)

pdf = MarkdownPdf(toc_level=2)
pdf.add_section(Section(final, root=str(PDFDIR), toc=True),
    user_css=("h1{color:#003366;} h2{color:#1a4d7a;border-bottom:1px solid #ccc;padding-bottom:4px;} "
              "table{border-collapse:collapse;font-size:8.5pt;} th,td{border:1px solid #999;padding:3px 6px;} "
              "th{background:#f0f4f8;} img{max-width:100%;height:auto;margin:8pt 0;} p{line-height:1.4;}"))
pdf.meta["title"] = "Synthetic-data characterization — Indonesian ASR corpus v7"
pdf.meta["author"] = "Ratna Atika et al."
pdf.save(str(PDF))

d = fitz.open(str(PDF)); d.save(str(PDF).replace(".pdf", "_c.pdf"), garbage=4, deflate=True, clean=True); d.close()
Path(str(PDF).replace(".pdf", "_c.pdf")).replace(PDF)
print(f"PDF: {PDF} ({PDF.stat().st_size/1024:.0f} KB), inlined: {sorted(inlined)}")
