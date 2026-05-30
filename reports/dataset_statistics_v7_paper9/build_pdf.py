#!/usr/bin/env python3
"""Build the grand PDF report from the Elsevier MD.

- Substitutes \input{tex/*.tex} placeholders with markdown tables built from
  stats/*.csv (Elsevier requires editable tables; we render readable versions).
- Inlines all 12 figures (600 dpi PNG) after their first "Figure FN" mention.
- Renders to PDF via markdown_pdf.
"""
import csv, re
from pathlib import Path
from markdown_pdf import MarkdownPdf, Section

HERE = Path(__file__).resolve().parent
MD_IN = HERE / "01_DATASET_STATISTICS_REPORT_v7_paper9_elsevier.md"
PDF_OUT = HERE / "01_DATASET_STATISTICS_REPORT_v7_paper9_elsevier.pdf"
PNG = HERE / "figures" / "png_pdf"
STATS = HERE / "stats"

def csv_to_md(path, cols=None):
    rows = list(csv.reader(path.open(encoding="utf-8")))
    if not rows: return ""
    head, body = rows[0], rows[1:]
    out = "| " + " | ".join(head) + " |\n| " + " | ".join("---" for _ in head) + " |\n"
    for r in body:
        out += "| " + " | ".join(r) + " |\n"
    return out

# table substitutions: \input{tex/NAME.tex} -> markdown table
TABLES = {
    "tex/T1_overview.tex": ("**Table T1.** Corpus-level headline statistics (v7).", None),
    "tex/T2_per_speaker.tex": ("**Table T2.** Per-speaker descriptive statistics (full 20 rows).", STATS/"per_speaker.csv"),
    "tex/T3_per_category.tex": ("**Table T3.** Per-category descriptive statistics.", STATS/"per_category.csv"),
    "tex/T4_per_split.tex": ("**Table T4.** Train / dev / test split statistics.", STATS/"per_split.csv"),
    "tex/T5_statistical_tests.tex": ("**Table T5.** Statistical tests (Bonferroni family size 4).", STATS/"statistical_tests.csv"),
    "tex/G1_category_glossary.tex": ("**Table G1.** Glossary of the 11 sentence-type categories.", None),
}
T1_MD = """| Property | Value |
| --- | --- |
| Audio files | 102,544 |
| Total duration (h) | 130.65 |
| Speakers (M / F) | 20 (11 / 9) |
| Sentence categories | 11 |
| Base sentences | 209 (19 × 11) |
| Audio format (uniform) | 16 kHz / 16-bit / mono |
| Real-speech files | 102,412 (99.871%) |
| Synthetic files (Edge-TTS Neural) | 132 (0.129%) |
| Vocabulary size | 786 unique words |
| Total tokens | 908,472 |
| Mean tokens / file | 8.86 |
"""
G1_MD = """| Indonesian label | English gloss | Function |
| --- | --- | --- |
| Kalimat_Deklaratif | Declarative | Statement that asserts a fact |
| Kalimat_Klarifikasi | Clarification | Request to clarify or rephrase |
| Kalimat_Kondisional | Conditional | If–then construction |
| Kalimat_Konfirmasi | Confirmation | Yes/no confirmation request |
| Kalimat_Negasi | Negation | Negated assertion (tidak / bukan) |
| Kalimat_Penjadwalan | Scheduling | Time-related plan or appointment |
| Kalimat_Perintah | Command / Imperative | Direct instruction (telegraphic) |
| Kalimat_Persuasif | Persuasive | Multi-clause argumentation, longest |
| Kalimat_Retoris | Rhetorical | Question whose answer is implied |
| Kalimat_Seruan | Exclamation | Surprise / emphasis |
| Kalimat_Tanya | Interrogative | Information-seeking question |
"""

md = MD_IN.read_text(encoding="utf-8")
for key, (cap, csvp) in TABLES.items():
    if csvp is not None:
        table = csv_to_md(csvp)
    elif "T1" in key:
        table = T1_MD
    else:
        table = G1_MD
    md = md.replace(f"`\\input{{{key}}}`", f"{cap}\n\n{table}")

# inline figures after first mention of "Figure FN" / "(Figure FN" or the Figure index
inlined = set()
def fig_path(tag):
    hits = sorted(PNG.glob(f"{tag}_*.png"))
    return hits[0].name if hits else None

out_lines = []
in_index = False
for line in md.splitlines():
    if line.startswith("## Figure index"):
        in_index = True
    out_lines.append(line)
    if in_index:
        continue  # don't inline inside the index table
    for m in re.finditer(r"\bF(\d{1,2})\b", line):
        tag = "F" + m.group(1)
        if tag in inlined: continue
        fn = fig_path(tag)
        if fn:
            out_lines += ["", f"![{tag}]({fn})", ""]
            inlined.add(tag)

md_final = "\n".join(out_lines)
(HERE / "01_DATASET_STATISTICS_REPORT_v7_paper9_elsevier_with_figures.md").write_text(md_final, encoding="utf-8")

pdf = MarkdownPdf(toc_level=2)
pdf.add_section(Section(md_final, root=str(PNG), toc=True),
    user_css=("h1{color:#003366;} h2{color:#1a4d7a;border-bottom:1px solid #ccc;padding-bottom:4px;} "
              "h3{color:#2e6da4;} table{border-collapse:collapse;font-size:8.5pt;margin:8pt 0;} "
              "th,td{border:1px solid #999;padding:3px 6px;text-align:left;} th{background:#f0f4f8;} "
              "code{background:#f5f5f5;padding:1px 4px;border-radius:3px;} "
              "pre{background:#f5f5f5;padding:8px;border-radius:4px;font-size:8pt;} "
              "img{max-width:100%;height:auto;margin:8pt 0;} p{line-height:1.4;}"))
pdf.meta["title"] = "Indonesian ASR Corpus v7 — Dataset Statistics (Data in Brief)"
pdf.meta["author"] = "Ratna Dadang et al."
pdf.save(str(PDF_OUT))
print(f"PDF: {PDF_OUT} ({PDF_OUT.stat().st_size/1024:.0f} KB), figures inlined: {sorted(inlined)}")
