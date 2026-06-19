# `session_20260524_125144_dataset_statistics_viz_elsevier/`

> Elsevier ScienceDirect-compliant version of
> `session_20260524_125144_dataset_statistics_viz/`. The original
> folder is preserved untouched. This folder is the version prepared
> for **submission to *Data in Brief*** (or, with the journal profile
> switch in `.agents/skills/sciencedirect-elsevier-format/templates/journal-profiles.yaml`,
> any other Elsevier journal).

Skill applied: **`sciencedirect-elsevier-format` v1.0.0**
(`/mnt/c/Users/wayandadang/AI/Dataset ASR/.agents/skills/sciencedirect-elsevier-format/`).

---

## Folder layout

```
session_20260524_125144_dataset_statistics_viz_elsevier/
├── README.md                                 ← this file
├── SUBMISSION_READINESS.md                   ← per-checkbox audit trail
├── 01_DATASET_STATISTICS_REPORT_elsevier.md  ← compliant report (Elsevier numeric refs)
├── Specifications_Table.md                   ← Data in Brief mandatory
├── Value_of_the_Data.md                      ← Data in Brief mandatory (5 bullets)
├── references.bib                            ← BibTeX (LTWA, DOIs, [dataset], [software])
├── regenerate_figures_elsevier.py            ← CSV → vector PDF + 600 dpi PNG
│
├── declarations/                             ← all Elsevier-required declarations
│   ├── Ethics_Statement.md
│   ├── CRediT_Statement.md
│   ├── Declaration_of_Competing_Interests.md
│   ├── Funding_Statement.md
│   └── GenAI_Disclosure.md
│
├── tex/                                      ← booktabs, no vertical rules
│   ├── T1_overview.tex
│   ├── T2_per_speaker.tex
│   ├── T3_per_category.tex
│   ├── T4_per_split.tex
│   ├── T5_statistical_tests.tex
│   └── G1_category_glossary.tex
│
├── figures/                                  ← vector PDF + 600 dpi raster
│   ├── F1_files_per_speaker_split.pdf        (vector)
│   ├── F2_duration_per_category.pdf
│   ├── F3_speaker_total_duration.pdf
│   ├── F4_sentence_length.pdf
│   ├── F5_word_frequency_pareto.pdf
│   ├── F6_heaps_law.pdf
│   ├── F7_speaker_category_heatmap.pdf
│   ├── F8_cumulative_hours.pdf
│   ├── F9_audio_uniformity.pdf
│   ├── F10_synthetic_disclosure.pdf
│   ├── F11_mel_spectrogram_exemplars.pdf     (halftone, 300 dpi)
│   ├── F12_audio_quality.pdf
│   ├── figure_manifest.csv                   ← required by the skill
│   └── png600/                               ← 600 dpi PNG fallback
│       └── F1..F12.png
│
└── stats/                                    ← immutable source CSV/JSON
    ├── per_speaker.csv      (20 rows)
    ├── per_category.csv     (11 rows)
    ├── per_split.csv        (3 rows)
    ├── word_frequency.csv   (top-1000)
    ├── statistical_tests.csv
    ├── audio_quality_sample.csv  (n = 297)
    └── dataset_stats.json
```

---

## How this differs from the original folder

| Area | Original | This folder |
|---|---|---|
| Figures | `figures/F*.png` only | **Vector PDF** + 600 dpi PNG (DPI metadata embedded) |
| Tables | `\hline` rules | `\toprule / \midrule / \bottomrule` (booktabs) |
| References | informal author–year list | numbered `[1]..[14]` + LTWA + DOIs + `[dataset]` / `[software]` tags |
| Spec table | absent | `Specifications_Table.md` (Data in Brief mandatory) |
| Value of Data | absent | `Value_of_the_Data.md` (5 bullets, no claims) |
| Declarations | absent | 5 separate templates in `declarations/` |
| Audit trail | absent | `SUBMISSION_READINESS.md` |
| Manifest | absent | `figures/figure_manifest.csv` |
| Banned-word check | n/a | title respects ban list |

The 12 figures are **regenerated from CSV** (not converted from PNG)
so the vector PDF is genuinely vector — text is selectable, lines
are scalable, and the file is small (typically 30–80 kB per PDF
versus 1.5–5 MB per PNG).

---

## Reproduce the figures

```bash
cd session_20260524_125144_dataset_statistics_viz_elsevier
python3 regenerate_figures_elsevier.py
```

Dependencies (system-installable):
```
numpy >= 1.22.4
pandas >= 2.0
matplotlib >= 3.5
seaborn >= 0.13
pillow
```

Outputs:
- `figures/F<N>.pdf` — vector source, drop into the LaTeX manuscript
  with `\includegraphics{figures/F1_files_per_speaker_split}`.
- `figures/png600/F<N>.png` — 600 dpi PNG fallback for Word
  manuscripts (or for journals that prefer raster).
- `figures/figure_manifest.csv` — auto-generated manifest required by
  the skill.

---

## Drop into a LaTeX manuscript

```latex
\documentclass[review,12pt,authoryear]{elsarticle}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{siunitx}
\usepackage{amsmath,amssymb}

\begin{document}

\title{Indonesian limited-data ASR corpus retake2026:
       corpus statistics, balance verification, and split integrity}

\author[1]{Author A}
\author[1]{Author B}
\author[1]{Author C\corref{cor1}}
\cortext[cor1]{Corresponding author. \texttt{author.c@example.org}}
\affiliation[1]{organization={Universitas X Speech Lab},
                city={Jakarta}, country={Indonesia}}

\begin{abstract}
% ... 250 words max ...
\end{abstract}

\begin{keyword}
ASR \sep Indonesian \sep speech-corpus \sep limited-data
       \sep balance \sep reproducibility
\end{keyword}

\maketitle

% Specifications Table
\input{Specifications_Table}     % rendered separately by Elsevier

\section*{Value of the Data}
\input{Value_of_the_Data}

\section{Data Description}
% ... \input the report body ...

\input{tex/T1_overview}
\input{tex/T2_per_speaker}
\input{tex/T3_per_category}
\input{tex/T4_per_split}
\input{tex/T5_statistical_tests}
\input{tex/G1_category_glossary}

\begin{figure}[!t]
  \centering
  \includegraphics[width=\linewidth]{figures/F1_files_per_speaker_split}
  \caption{F1. Per-speaker file count, stacked by train / dev / test split.}
  \label{fig:files-per-speaker}
\end{figure}
% ... and so on for F2..F12 ...

\section*{Declaration of Generative AI and AI-Assisted Technologies in the Manuscript Preparation Process}
% Insert content from declarations/GenAI_Disclosure.md here
% (this section MUST appear immediately before References).

\bibliographystyle{elsarticle-num}
\bibliography{references}

\end{document}
```

---

## Open action items before submission

See `SUBMISSION_READINESS.md` §9. Briefly:

1. Replace IRB reference number + approval date in
   `declarations/Ethics_Statement.md`.
2. Replace placeholder author names in `declarations/CRediT_Statement.md`.
3. Replace dataset DOI placeholder (`10.17632/PLACEHOLDER.v1`)
   everywhere once the corpus is published on Mendeley Data.
4. Choose Funding template 1 (with grant numbers) or template 2
   (no specific funding) in `declarations/Funding_Statement.md`.
5. Run the master submission checklist
   (`/mnt/c/Users/wayandadang/AI/Dataset ASR/.agents/skills/sciencedirect-elsevier-format/submission_checklist.md`)
   one last time before pressing "submit" in Editorial Manager.

---

## Skill provenance

This folder was produced by mechanically applying the
`sciencedirect-elsevier-format` skill (v1.0.0) to the original session
folder. The skill is the single source of truth for Elsevier format
rules; this folder is a *snapshot* of those rules applied to this
specific dataset article. When the skill is updated (e.g. when
Elsevier publishes a new edition of the Guide for Authors), re-run
the audit checklist on this folder to verify continued compliance.
