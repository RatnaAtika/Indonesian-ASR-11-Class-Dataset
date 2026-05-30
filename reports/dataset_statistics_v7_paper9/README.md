# `session_20260530_125618_dataset_stats_v7_paper9/`

**Grand dataset-statistics package** for the v7 corpus that feeds the
nine-model fair-comparison paper. Merges and supersedes the two reference
sessions (`..._dataset_statistics_viz` and `..._dataset_statistics_viz_elsevier`),
re-derived from the **exact files the 9 paper models train on**
(`metadata/dataset_metadata_clean.csv` + `splits/*_clean.tsv`,
`dataset_version = v7_natural_synth`), with all earlier draft errors corrected.

Skill applied: **`sciencedirect-elsevier-format` v1.0.0** (Data in Brief
profile). Guide for Authors:
<https://www.sciencedirect.com/journal/data-in-brief/publish/guide-for-authors>

## Folder layout

```
session_20260530_125618_dataset_stats_v7_paper9/
├── README.md                                            ← this file
├── SUBMISSION_READINESS.md                              ← per-checkbox audit + correction log
├── 01_DATASET_STATISTICS_REPORT_v7_paper9_elsevier.md   ← Elsevier-compliant grand report
├── 01_DATASET_STATISTICS_REPORT_v7_paper9_elsevier.pdf  ← grand PDF report (12 pp, all figs inlined)
├── 01_DATASET_STATISTICS_REPORT_v7_paper9.md            ← plain (non-Elsevier) variant
├── GITHUB_DATASET_NARRATIVE.md                          ← short README / dataset-card narrative
├── Specifications_Table.md                              ← Data in Brief mandatory
├── Value_of_the_Data.md                                 ← Data in Brief mandatory (5 bullets)
├── references.bib                                       ← BibTeX (numeric, LTWA, DOIs)
├── regenerate_all_elsevier.py                           ← rebuilds stats + tex + figures (no audio scan)
├── build_pdf.py                                         ← rebuilds the grand PDF
│
├── declarations/   Ethics, CRediT, Competing Interests, Funding, GenAI
├── tex/            T1..T5 + G1 booktabs tables (verified v7 numbers)
├── figures/        F1..F12 vector PDF + png600/ (600 dpi) + png_pdf/ (PDF-embed) + manifest
└── stats/          dataset_stats.json + per_*.csv + word_frequency.csv
                    + statistical_tests.csv + audio_quality_sample.csv (n=297)
```

## Headline numbers (verified, all reconcile)

- **102,544** utterances · **130.65 h** · **20** speakers (**11 M + 9 F**)
  · **11** categories · **209** base sentences.
- Files by gender: Male 56,396 (55.0 %) / Female 46,148 (45.0 %).
- Splits: train **71,792** / dev **15,376** / test **15,376** (speaker-disjoint).
- Audio: **16 kHz / 16-bit / mono**, 100 % uniform.
- Vocabulary **786** types over **908,472** tokens (Zipfian).
- Synthetic **132** (0.129 %) via Microsoft **Edge-TTS Neural** (Ardi/Gadis,
  gender-matched, Whisper-verified mean 0.9941); only **2** in test.
- Statistical tests: KW duration~category η²=0.594; KW duration~speaker
  η²=0.057; χ² category V=0.008; KS train-vs-test D=0.076.

## Reproduce

```bash
# stats + tex + figures (≈30 s, no audio-tree traversal)
python3 reports/dataset_statistics_v7_paper9/regenerate_all_elsevier.py
# grand PDF
python3 reports/dataset_statistics_v7_paper9/build_pdf.py
```

## What this merges from the two reference sessions

| From `..._viz` (plain) | From `..._viz_elsevier` | New here |
|---|---|---|
| analyze + PDF grand report | declarations, Spec Table, Value of Data | 9-model pipeline binding (§0) |
| critique iterations | tex booktabs tables, references.bib | corrected 11 M/9 F, vocab 786 |
| F1..F12 figure set | vector PDF + 600 dpi + statistical tests | `microsoft_edge_tts_neural` provenance |

> Corrections vs the earlier elsevier draft are logged in
> `SUBMISSION_READINESS.md` (gender 10/10→11/9; vocab 711→786; engine tag).
