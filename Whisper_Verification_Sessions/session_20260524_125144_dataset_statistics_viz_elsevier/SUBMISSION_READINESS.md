# Submission Readiness — `session_20260524_125144_dataset_statistics_viz_elsevier/`

> **Compliance gate** for ScienceDirect / Elsevier submission.
> Profile: **Data in Brief** (default; ISSN 2352-3409). Skill applied:
> `.agents/skills/sciencedirect-elsevier-format/`.
> This folder is the **Elsevier-compliant version** of the original
> `session_20260524_125144_dataset_statistics_viz/`. The original is
> kept untouched.

This document records, item-by-item, how this folder satisfies the
format rules captured in the `sciencedirect-elsevier-format` skill.
Use it as the audit trail attached to the submission package.

---

## 1. What was wrong in the original folder

| # | Issue | Severity | Original folder | This folder |
|---|---|---|---|---|
| 1 | Figures saved as PNG only — line/bar/scatter plots violate Elsevier's vector-source rule for line drawings | **HIGH** | `figures/F*.png` (PNG only @ 300 dpi) | `figures/F*.pdf` (vector) + `figures/png600/F*.png` (600 dpi raster fallback) |
| 2 | `figures_pdf/*.png` raster fallback had no embedded DPI metadata (`dpi=None`) | MED | yes | DPI = 600 embedded on every PNG |
| 3 | LaTeX tables used `\hline` instead of booktabs `\toprule/\midrule/\bottomrule` | **HIGH** | `tex/T1..T5,G1` use `\hline` | `tex/T1..T5,G1` use booktabs |
| 4 | `\textless\,1$\times$10$^{-300}$` workaround in T5 | LOW | yes | replaced with `${<}10^{-300}$` |
| 5 | No formal Elsevier numeric `[1]` references | **HIGH** | informal author-year prose | numbered `[1]..[14]` + LTWA + DOIs |
| 6 | No Specifications Table (mandatory for Data in Brief) | **HIGH** | absent | `Specifications_Table.md` |
| 7 | No Value of the Data (3–5 bullets, mandatory for DiB) | **HIGH** | absent | `Value_of_the_Data.md` |
| 8 | No Ethics / CRediT / Funding / Declaration of Competing Interests / GenAI disclosure | **HIGH** | absent | `declarations/` (5 templates) |
| 9 | No `figure_manifest.csv` | LOW | absent | `figures/figure_manifest.csv` |
| 10 | No audit trail file | LOW | absent | this file |
| 11 | Title contained banned word "Statistical Characterization and Visual Analysis" — *analysis* is borderline; in any case, restructured | LOW | yes | new title respects ban list |

---

## 2. File-format compliance (skill §1)

| Asset | Format | Editable source? | Pass? |
|---|---|---|---|
| `01_DATASET_STATISTICS_REPORT_elsevier.md` | Markdown | yes (pandoc) | ✅ |
| `Specifications_Table.md` | Markdown | yes | ✅ |
| `Value_of_the_Data.md` | Markdown | yes | ✅ |
| `references.bib` | BibTeX | yes | ✅ |
| `tex/T1..T5,G1.tex` | LaTeX | yes — drop into manuscript | ✅ |
| `figures/F*.pdf` | vector PDF | yes (re-renderable from CSV) | ✅ |
| `figures/png600/F*.png` | raster fallback @ 600 dpi (300 dpi for F11) | yes (re-renderable) | ✅ |
| `figures/figure_manifest.csv` | CSV | yes | ✅ |
| `stats/*.csv`, `stats/dataset_stats.json` | tabular / JSON | yes | ✅ |
| `regenerate_figures_elsevier.py` | Python source | yes | ✅ |
| `declarations/*.md` | Markdown templates | yes | ✅ |
| `README.md`, `SUBMISSION_READINESS.md` | Markdown | yes | ✅ |

**No PDF is submitted as the manuscript source.** All artifacts are
in editable text form.

---

## 3. Figures (skill `checklists/figures.md`)

| Figure | Kind | Vector source | Raster fallback | DPI | Pass |
|---|---|---|---|---|---|
| F1 — files per speaker × split | line | `F1_files_per_speaker_split.pdf` | 5580 × 2831 PNG | 600 | ✅ |
| F2 — duration per category | line | `F2_duration_per_category.pdf` | 5452 × 3022 PNG | 600 | ✅ |
| F3 — speaker total duration | line | `F3_speaker_total_duration.pdf` | 5630 × 2783 PNG | 600 | ✅ |
| F4 — sentence length | line | `F4_sentence_length.pdf` | 6061 × 3055 PNG | 600 | ✅ |
| F5 — Zipf word-frequency | line | `F5_word_frequency_pareto.pdf` | 5525 × 2784 PNG | 600 | ✅ |
| F6 — Heaps' law | line | `F6_heaps_law.pdf` | 4142 × 2783 PNG | 600 | ✅ |
| F7 — speaker × category heatmap | combination | `F7_speaker_category_heatmap.pdf` | 5304 × 3484 PNG | 600 | ✅ (≥ 500 dpi rule for combinations) |
| F8 — cumulative hours | line | `F8_cumulative_hours.pdf` | 4142 × 2783 PNG | 600 | ✅ |
| F9 — audio uniformity | line | `F9_audio_uniformity.pdf` | 6148 × 2321 PNG | 600 | ✅ |
| F10 — synthetic disclosure | line | `F10_synthetic_disclosure.pdf` | 5558 × 2215 PNG | 600 | ✅ |
| F11 — mel spectrograms | **halftone** | raster-in-PDF wrapper | 4470 × 2766 PNG | 300 | ✅ (≥ 300 dpi rule for halftones) |
| F12 — audio quality | line | `F12_audio_quality.pdf` | 5960 × 2752 PNG | 600 | ✅ |

**Color accessibility (`figures.md` §3):**

- All plots use the **Okabe–Ito** palette (color-blind safe by
  construction).
- The heatmap (F7) uses **viridis**, not jet — perceptually uniform
  and color-blind safe.
- Line styles plus colors are used together in F4 / F12 to support
  monochrome printing.

**No AI-generated images.** No image was synthesised by GenAI; AI is
not part of the research method itself for this artifact (skill §3
exception does not apply).

---

## 4. Tables (skill `checklists/tables.md`)

- ✅ All tables (T1–T5, G1) are **editable LaTeX** (`tex/*.tex`),
  not images.
- ✅ Use `\toprule / \midrule / \bottomrule` from booktabs;
  no vertical bars; no shading.
- ✅ Captions placed **above** the table; numbered consecutively.
- ✅ Numeric columns are aligned on the decimal point.
- ✅ Units in column headers (h, s, %, etc.).
- ✅ Caption explains every abbreviation used.
- ✅ Cited in the running text (Tables T1–T5, Glossary G1).

---

## 5. Math, units, nomenclature (skill `checklists/math-and-units.md`)

- ✅ All math is editable text (LaTeX `$$` / `\begin{equation}`,
  Markdown `$...$`); no equation rasterised.
- ✅ All units SI: kHz, Hz, s, ms, dB, h, %.
- ✅ Variables italic ($H$, $\eta^{2}$, $V$, $D$, $N$); function names
  roman (e.g. `\log`).
- ✅ T5 uses `${<}10^{-300}$` instead of `\textless\,1$\times$10$^{-300}$`.
- ✅ Statistical-test report includes **effect sizes** alongside
  $p$-values and **Bonferroni-adjusted $p$-values** (family size 4).
- ✅ Heaps' law $V = K N^{\beta}$ written with proper italics.

---

## 6. References (skill `checklists/references.md`)

- ✅ Numeric square-bracket style: `[1]`, `[2]`, …
- ✅ Numbered in the order they first appear in the text.
- ✅ Journal names **LTWA-abbreviated**: *J. Am. Stat. Assoc.*,
  *IEEE/ACM Trans. Audio Speech Lang. Process.*, *Proc. Int. Conf.
  Mach. Learn. (ICML)*, *Adv. Neural Inf. Process. Syst.*, etc.
- ✅ DOIs included for every journal article.
- ✅ Dataset reference tagged `[dataset]` (entry 14).
- ✅ Software references tagged `[software]` (entries 12 and 13).
- ✅ No Wikipedia / Stack Overflow / blog references.
- ✅ References mirror in `references.bib` for `elsarticle-num`
  bibliography style.

---

## 7. Data in Brief mandatory sections (skill `checklists/data-in-brief-template.md`)

Section ordering, names, and contents as required by the
*Data in Brief* template:

| Section | File | Status |
|---|---|---|
| Title (no banned words) | `01_DATASET_STATISTICS_REPORT_elsevier.md` §title | ✅ |
| Abstract / Article body | (in parent paper) | inherits |
| Keywords | (in parent paper, ≤ 7) | inherits |
| **Specifications Table** | `Specifications_Table.md` | ✅ |
| **Value of the Data** (3–5 bullets) | `Value_of_the_Data.md` | ✅ (5 bullets) |
| Background | folded into report intro | ✅ |
| **Data Description** | `01_DATASET_STATISTICS_REPORT_elsevier.md` §1 | ✅ |
| **Experimental Design, Materials and Methods** | report §2 | ✅ |
| **Limitations** | report §3 | ✅ |
| **Ethics Statement** | `declarations/Ethics_Statement.md` | ✅ |
| **CRediT** | `declarations/CRediT_Statement.md` | ✅ |
| **Declaration of Competing Interests** | `declarations/Declaration_of_Competing_Interests.md` | ✅ |
| **GenAI Disclosure** | `declarations/GenAI_Disclosure.md` (placed **before** References) | ✅ |
| **Funding** | `declarations/Funding_Statement.md` | ✅ |
| **References** | report §9 | ✅ |

**Banned section names** (`Conclusion`, `Discussion`, `Summary`,
`Results`) — none present. ✅

**Banned title words** (`effects`, `evidence`, `response`,
`implications`, `influence`, `study`, `results`, `conclusions`,
`analysis of`) — none present. ✅

---

## 8. Master submission checklist (skill `submission_checklist.md`)

| Master checklist box | Status here |
|---|---|
| §0 Journal profile = data_in_brief | ✅ |
| §1 File formats: editable source, no PDF source | ✅ |
| §2 Title page (deferred to parent) | inherits |
| §3 Abstract (deferred to parent; report has descriptive intro) | inherits |
| §4 Keywords (deferred to parent) | inherits |
| §5 Specifications Table | ✅ |
| §6 Value of the Data (3–5) | ✅ |
| §7 Figures (vector source, color-blind safe, manifest) | ✅ |
| §8 Tables (booktabs, no vertical rules, captions) | ✅ |
| §9 Math / units / SI / equation numbering | ✅ |
| §10 References (numeric, LTWA, DOI, [dataset], [software]) | ✅ |
| §11 CRediT / COI / Funding / Ethics / GenAI declarations | ✅ |
| §12 Data deposit | ⚠️ DOI placeholder pending |
| §13 Cross-reference / orphan check | ✅ |
| §14 Spell + grammar | ✅ (American English) |
| §15 Submission system upload | pending Editorial Manager step |

---

## 9. Open items before final submission

- [ ] Replace `<IRB-REF-PLACEHOLDER>` and `<DATE-PLACEHOLDER>` in
      `declarations/Ethics_Statement.md` with real IRB number + date.
- [ ] Replace `Author A`, `Author B`, … in `declarations/CRediT_Statement.md`
      with real author names.
- [ ] Replace the **dataset DOI placeholder** (`10.17632/PLACEHOLDER.v1`)
      everywhere (`Specifications_Table.md`, `references.bib`,
      report §9) once the corpus is published on Mendeley Data.
- [ ] Confirm the Funding statement (Template 1 with grant numbers vs.
      Template 2 "no specific funding"). Default in this folder is
      Template 2.
- [ ] Confirm whether the methods paper is co-submitted (changes the
      *Related research article* field of the Specifications Table).

---

## 10. Skill version

| Field | Value |
|---|---|
| Skill applied | `sciencedirect-elsevier-format` |
| Skill version | 1.0.0 |
| Bundle revision | `session_..._elsevier/` 1.0.0 |
| Audit date | 2026-05-24 |
| Auditor | author + AI-assisted (Anthropic Claude Sonnet, disclosure required) |
