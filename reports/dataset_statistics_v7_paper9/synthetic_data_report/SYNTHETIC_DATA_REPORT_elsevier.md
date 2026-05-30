# Synthetic-data characterization and per-category distribution — Indonesian ASR corpus (v7)

**Article-supplement type**: *Data in Brief* synthetic-data disclosure
(Elsevier `sciencedirect-elsevier-format`, ISSN 2352-3409).
**Generated**: 2026-05-30.
**Source**: `metadata/dataset_metadata_clean.csv` (102,544 rows),
`dataset_version = v7_natural_synth`; reproducible via
`build_synthetic_report.py` (no audio-tree traversal). Machine-readable
summary in `synthetic_data_stats.json`; per-category table in
`synthetic_per_category.csv`.

> This supplement gives the **full, per-category distribution** of the
> synthetic gap-fill files used in the corpus that feeds the nine-model
> fair-comparison benchmark. It complements §1.6 / §2.3 of the main
> dataset-statistics report and Figure F10 (corpus-level disclosure).

---

## 1. Overview

| Property | Value |
|---|---|
| Synthetic files | **132** of 102,544 (**0.129 %** of corpus) |
| Synthetic duration | 0.176 h (632.5 s) |
| Generation engine | Microsoft **Edge-TTS Neural** (`microsoft_edge_tts_neural`) |
| Voices (gender-matched) | `id-ID-ArdiNeural` (male, 73) / `id-ID-GadisNeural` (female, 59) |
| Speaker-cloned | **No** — TTS voices only, disclosed (not impersonating speakers) |
| Synthesis rounds | `v7_initial` (124) + `v7_residual_fix` (8) |
| Speakers with ≥ 1 synthetic | 18 / 20 |
| Zero-synthetic speakers | **Baron, Robi** (both in the test split → clean evaluation) |

Synthetic files replace dropped or unrecoverable speaker takes. Each was
transcribed with Whisper-large-v3 and required text-similarity ≥ 0.70 to
the target sentence before acceptance.

---

## 2. Quality verification (Figure S4)

| Metric | Value |
|---|---|
| Similarity metric | Whisper-large-v3 text-similarity to target (0–1) |
| Acceptance threshold | ≥ 0.70 |
| Mean / median | **0.9941** / 1.0000 |
| Min / max | 0.9101 / 1.0000 |
| Pass ≥ 0.90 | 132 / 132 (100 %) |
| Pass ≥ 0.95 | 125 / 132 (94.7 %) |
| Exactly 1.00 | 114 / 132 (86.4 %) |

All 132 files clear the acceptance threshold; the lowest-quality file
(0.9101, in *Kalimat_Perintah*) still exceeds 0.90.

---

## 3. Per-category distribution (Table S1, Figures S1–S3)

The 132 synthetic files are not uniformly distributed: *Kalimat_Konfirmasi*
(confirmation) holds the most (29 files, 21.97 % of all synthetic), while
*Kalimat_Deklaratif* holds the fewest (2). Even the most-affected category is
only **0.32 % synthetic** of its own 9,017 files.

**Table S1.** Per-category synthetic-file distribution. `%cat` = synthetic
share within that category; `%all` = share of all 132 synthetic files;
`M/F` = TTS voice gender (Ardi/Gadis); `tr/dv/te` = train/dev/test counts;
`init/fix` = v7_initial / v7_residual_fix rounds.

| Category | n | %cat | %all | M/F | tr/dv/te | init/fix | q̄ | q-min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Kalimat_Konfirmasi | 29 | 0.322 | 21.97 | 11/18 | 25/2/2 | 28/1 | 0.9878 | 0.9553 |
| Kalimat_Retoris | 17 | 0.179 | 12.88 | 10/7 | 15/2/0 | 17/0 | 1.0000 | 1.0000 |
| Kalimat_Kondisional | 16 | 0.178 | 12.12 | 9/7 | 16/0/0 | 14/2 | 1.0000 | 1.0000 |
| Kalimat_Persuasif | 16 | 0.178 | 12.12 | 9/7 | 16/0/0 | 15/1 | 1.0000 | 1.0000 |
| Kalimat_Perintah | 15 | 0.158 | 11.36 | 13/2 | 13/2/0 | 12/3 | 0.9894 | 0.9101 |
| Kalimat_Negasi | 11 | 0.116 | 8.33 | 8/3 | 10/1/0 | 10/1 | 1.0000 | 1.0000 |
| Kalimat_Tanya | 10 | 0.111 | 7.58 | 6/4 | 10/0/0 | 10/0 | 0.9886 | 0.9430 |
| Kalimat_Klarifikasi | 9 | 0.095 | 6.82 | 2/7 | 9/0/0 | 9/0 | 0.9886 | 0.9489 |
| Kalimat_Penjadwalan | 4 | 0.042 | 3.03 | 3/1 | 3/1/0 | 4/0 | 0.9873 | 0.9493 |
| Kalimat_Seruan | 3 | 0.032 | 2.27 | 1/2 | 3/0/0 | 3/0 | 1.0000 | 1.0000 |
| Kalimat_Deklaratif | 2 | 0.021 | 1.52 | 1/1 | 2/0/0 | 2/0 | 1.0000 | 1.0000 |

→ Figure S1 (per-category by voice gender), Figure S2 (synthetic fraction
within each category), Figure S3 (per-category split distribution).

---

## 4. Per-split distribution

| Split | Synthetic | Split total | % of split |
|---|---:|---:|---:|
| train | 122 | 71,792 | 0.170 % |
| dev | 8 | 15,376 | 0.052 % |
| test | **2** | 15,376 | **0.013 %** |

Only 2 synthetic files (both in *Kalimat_Konfirmasi*) reach the test split,
so the held-out evaluation that scores the nine models is effectively on
real speech.

---

## 5. Per-speaker distribution

Synthetic files span 18 of 20 speakers (max 17 = Afgan; min 2 = Amri, Joni).
Test speakers **Baron** and **Robi** carry zero synthetic files; the third
test speaker (Joni) carries 2. Full counts in
`synthetic_data_stats.json:by_speaker`.

---

## 6. Reproducibility

```bash
python3 synthetic_data_report/build_synthetic_report.py
# → synthetic_data_stats.json, synthetic_per_category.csv,
#   SYNTHETIC_DATA_REPORT.txt, figures/S1..S4.{pdf,png}, this .md, .pdf
```

Outputs in five formats: **PDF** (this report), **PNG + PDF** (figures
S1–S4, 600 dpi / vector, Okabe-Ito palette, `pdf.fonttype=42`), **JSON**
(`synthetic_data_stats.json`), **TXT** (`SYNTHETIC_DATA_REPORT.txt`), and
**MD** (this file). All numbers trace to `metadata/dataset_metadata_clean.csv`.

---

## Figure index

| Fig | Content | File |
|---|---|---|
| S1 | Synthetic files per category, by TTS voice gender | `figures/S1_synth_per_category_voice.pdf` |
| S2 | Synthetic fraction within each category | `figures/S2_synth_fraction_per_category.pdf` |
| S3 | Synthetic-file split distribution per category | `figures/S3_synth_split_per_category.pdf` |
| S4 | Synthetic-audio Whisper-similarity quality | `figures/S4_synth_quality.pdf` |
