# Submission Readiness — Data in Brief (v7, 9-model paper)

Audit of the grand dataset-statistics package against the
`sciencedirect-elsevier-format` skill (v1.0.0, Data in Brief profile,
ISSN 2352-3409). Guide for Authors:
<https://www.sciencedirect.com/journal/data-in-brief/publish/guide-for-authors>

## Mandatory data-article sections

| Section | Present | File |
|---|:---:|---|
| Title (no banned words) | ✓ | report §title |
| Specifications Table | ✓ | `Specifications_Table.md` |
| Value of the Data (3–5 bullets) | ✓ | `Value_of_the_Data.md` (5) |
| Data Description | ✓ | report §1 |
| Experimental Design, Materials & Methods | ✓ | report §2 |
| Limitations | ✓ | report §3 |
| Ethics Statement | ✓ | `declarations/Ethics_Statement.md` |
| CRediT Author Statement | ✓ | `declarations/CRediT_Statement.md` |
| Declaration of Competing Interests | ✓ | `declarations/Declaration_of_Competing_Interests.md` |
| Funding | ✓ | `declarations/Funding_Statement.md` |
| GenAI Disclosure (before References) | ✓ | `declarations/GenAI_Disclosure.md` |
| References (numeric, LTWA, DOIs) | ✓ | report §9 + `references.bib` |

## Figures (Elsevier artwork rules)

| Rule | Status |
|---|:---:|
| Vector format for line plots (`.pdf`) | ✓ 12 PDFs |
| Raster fallback ≥ 300 dpi (`.png` @ 600 dpi) | ✓ `figures/png600/` |
| Color-blind-safe palette (Okabe-Ito) | ✓ |
| Colormap not jet (viridis for heatmap) | ✓ F7 |
| PDF font embed (`pdf.fonttype=42`) | ✓ |
| Serif body font, 8–10 pt | ✓ |
| No AI-generated images (all matplotlib) | ✓ |
| Figure manifest | ✓ `figures/figure_manifest.csv` |

## Tables (Elsevier rules)

| Rule | Status |
|---|:---:|
| Editable text, never images | ✓ `tex/*.tex` (booktabs) |
| No vertical rules / shading | ✓ `\toprule/\midrule/\bottomrule` |
| Verified v7 numbers (11 M / 9 F, 786 vocab) | ✓ regenerated from metadata |

## Grand PDF report

| Item | Value |
|---|---|
| File | `01_DATASET_STATISTICS_REPORT_v7_paper9_elsevier.pdf` |
| Pages | 12 |
| Size | ≈ 3.0 MB (compressed; well under GitHub 100 MB) |
| All 12 figures inlined | ✓ |
| Key numbers verified in text layer | ✓ (102,544 / 130.65 h / 20 (11/9) / 786 / 132) |

> The PDF is a **convenience grand report**, not the Elsevier submission
> source. Data in Brief requires an editable source (`.docx` / `.tex`); the
> `.md` + `tex/*.tex` + `references.bib` are the editable masters.

## Action items before actual submission (placeholders)

- [ ] Replace Mendeley Data DOI `10.17632/PLACEHOLDER.v1`.
- [ ] Replace `<IRB-REF-PLACEHOLDER>` / `<DATE-PLACEHOLDER>` in Ethics.
- [ ] Replace placeholder author names in CRediT.
- [ ] Confirm Funding statement (Template 1 vs 2).
- [ ] Convert declarations to `.docx` for Editorial Manager upload.

## Correction log vs earlier elsevier draft

| Item | Earlier draft | This package (verified) |
|---|---|---|
| Gender | 10 F / 10 M | **9 F / 11 M** |
| Vocabulary | 711 | **786** (raw lowercased) |
| Synthesis engine tag | `edge-tts` | `microsoft_edge_tts_neural` |
| Pipeline binding | implicit | explicit 9-model §0 table |
| Statistical tests | reused | recomputed (η²=0.594, V=0.008, D=0.076) |
