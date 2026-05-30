# Dataset Statistics & Visualization Report — v7 corpus for the 9-model paper

**Status:** paper-ready (Data in Brief–aligned).
**Generated:** 2026-05-30.
**Single source of truth:** `metadata/dataset_metadata_clean.csv` (102,544 rows ×
23 columns) and the frozen `splits/{train,dev,test}_clean.tsv` splits
(71,792 / 15,376 / 15,376). All numbers below are reproducible from
`compute_stats.py` in this folder; machine-readable summary in
`stats/dataset_stats.json`.

> **Why this report exists.** The previous statistics session
> (`session_20260524_125144_dataset_statistics_viz_elsevier/`) was built before
> the 9-model fair-comparison pipeline (RUN_GUIDE.md, slots m02b/m06–m13) was
> finalized. This report re-derives every statistic from the **exact files the
> nine paper models read** (`*_clean.tsv` + `dataset_metadata_clean.csv`,
> `dataset_version = v7_natural_synth`), so the dataset paper and the benchmark
> paper cite identical figures.

---

## 0. Corpus ↔ pipeline binding (verified)

| Pipeline artifact | Value | Source |
|---|---|---|
| Metadata used by trainers | `metadata/dataset_metadata_clean.csv` | `training_conventional/common/utils.py:load_split`, `training/common/utils.py` |
| Train / dev / test TSV | `splits/{train,dev,test}_clean.tsv` | RUN_GUIDE.md, `data_final/` |
| Split sizes | **71,792 / 15,376 / 15,376** (Σ 102,544) | verified row counts |
| `dataset_version` (all rows) | **`v7_natural_synth`** | metadata column 23 |
| Tokenizer | SentencePiece char (`spm_v7_char`) | README §1 |
| Features | 80-bin log-mel, 25 ms / 10 ms, per-utt CMVN | README §1 |

The 9 paper models (m08 HMM-GMM, m09 DNN-HMM, m10 GMM-HMM-DNN, m11 Vanilla
Transformer, m12 ViT-modified-ID ★, m07 Bi-LSTM CTC, m06 Conformer-CTC,
m13 Wav2Letter, m02b Whisper-medium FT) all consume these exact splits with
greedy decoding and no LM (fair-comparison protocol C).

---

## 1. Corpus overview

| Item | Value |
|---|---|
| Total utterances (WAV files) | **102,544** |
| Total duration | **130.65 h** (470,357.4 s) |
| Mean utterance duration | 4.59 s (median 4.49 s; min 1.56 s, max 206.41 s¹) |
| Speakers | **20** native Indonesian (11 M + 9 F) |
| Sentence-type categories | **11** |
| Unique base sentences | **209** (19 per category × 11) |
| Audio format | **16 kHz / 16-bit / mono PCM**, 100 % uniform |
| Synthetic files | **132** (0.129 %), Microsoft Edge-TTS Neural |

¹ The 206 s maximum is a small number of concatenated/long takes; see §7
Limitations. The median is 4.49 s.

**Audio uniformity:** `sample_rate=16000`, `num_channels=1`,
`bits_per_sample=16` for **all 102,544 files with zero exceptions** —
front-end variability is eliminated as a confound for model comparison.

→ Figures: `F3_hours_per_category.pdf`, `F8_duration_histogram.pdf`.

---

## 2. Speaker characterization

20 speakers each contribute **5,125–5,132 files** (range 0.14 %).

| Balance metric | Value |
|---|---|
| Per-speaker normalised entropy `H/log₂n` | **0.99999998** |
| Per-speaker Gini | **0.000196** |

This is near-perfect per-speaker file balance. Per-speaker hours range
5.62–7.67 h. See `stats/per_speaker.csv`.

**Gender (speaker level):**
- **Male (11):** Afgan, Ammar, Amri, Baron, Fajar, Fito, Harry, Muhaimin, Pram, Risky, Robi
- **Female (9):** Anggi, Atika, Bey, Elisa, Erlin, Indah, Joni, Nanda, Uly

**Gender (file/hour level):**

| Gender | Files | Hours | Share (files) |
|---|---:|---:|---:|
| Male | 56,396 | 70.27 | 55.0 % |
| Female | 46,148 | 60.39 | 45.0 % |

→ Figures: `F1_files_per_speaker.pdf`, `F4_gender_distribution.pdf`.

---

## 3. Sentence-category characterization

The 11 categories are highly balanced (normalised entropy **0.99987**,
Gini **0.012**). Mean duration and length track the linguistic function of each
category (imperatives short, persuasives long).

| Category | Files | Hours | Mean dur (s) | Mean chars | Mean words | Synth |
|---|---:|---:|---:|---:|---:|---:|
| Kalimat_Deklaratif | 9,500 | 10.70 | 4.05 | 60.5 | 8.05 | 2 |
| Kalimat_Klarifikasi | 9,500 | 13.81 | 5.23 | 65.5 | 9.68 | 9 |
| Kalimat_Kondisional | 9,010 | 14.92 | 5.96 | 79.5 | 11.11 | 16 |
| Kalimat_Konfirmasi | 9,017 | 13.98 | 5.58 | 72.0 | 10.22 | 29 |
| Kalimat_Negasi | 9,500 | 9.43 | 3.57 | 53.5 | 7.16 | 11 |
| Kalimat_Penjadwalan | 9,500 | 13.11 | 4.97 | 57.9 | 8.26 | 4 |
| Kalimat_Perintah | 9,500 | 7.81 | 2.96 | 38.4 | 6.05 | 15 |
| Kalimat_Persuasif | 9,011 | 16.09 | 6.43 | 107.1 | 15.44 | 16 |
| Kalimat_Retoris | 9,500 | 10.41 | 3.95 | 63.6 | 8.63 | 17 |
| Kalimat_Seruan | 9,500 | 9.04 | 3.43 | 45.7 | 6.42 | 3 |
| Kalimat_Tanya | 9,006 | 11.35 | 4.54 | 46.4 | 6.83 | 10 |

(Four categories sit at ~9,010 files instead of 9,500 because one base
sentence was dropped during transcript-canonicalization; see §7.)

→ Figures: `F2_duration_per_category.pdf`, `F3_hours_per_category.pdf`.

---

## 4. Train / dev / test split

Splits are **at the speaker level with zero speaker leakage** (train/dev/test
speaker sets are disjoint).

| Split | Files | Speakers | Hours | Male | Female | Synth |
|---|---:|---:|---:|---:|---:|---:|
| train | 71,792 | 14 | 92.49 | 30,770 | 41,022 | 122 |
| dev | 15,376 | 3 | 19.74 | 15,376 | 0 | 8 |
| test | 15,376 | 3 | 18.43 | 10,250 | 5,126 | 2 |

- **train (14):** Afgan, Ammar, Anggi, Atika, Bey, Elisa, Erlin, Fito, Harry, Indah, Muhaimin, Nanda, Risky, Uly
- **dev (3):** Amri, Fajar, Pram — **all male** (disclosed limitation §7)
- **test (3):** Baron, Joni, Robi — mixed sex (2 M + 1 F)

→ Figures: `F6_split_gender.pdf`, `F7_synthetic_disclosure.pdf`.

---

## 5. Linguistic profile

| Item | Value |
|---|---|
| Vocabulary (unique word types, lowercased) | **786** |
| Total tokens | **908,472** |
| Type/token ratio | 8.65 × 10⁻⁴ |

**Top 15 words:** yang (26,500), kamu (24,000), apakah (21,017),
saya (19,500), jika (18,016), di (14,517), untuk (14,500), sudah (14,500),
kita (13,021), akan (12,511), ini (12,000), tolong (11,517), lebih (10,010),
dengan (9,523), ke (8,500). The rank–frequency relationship follows the
expected Zipfian log–linear decay.

→ Figure: `F5_word_frequency_zipf.pdf`. Full list: `stats/word_frequency.csv`.

---

## 6. Synthetic-data disclosure (method, full detail)

**132 files (0.129 % of the corpus)** are synthetic gap-fills generated to
replace dropped or unrecoverable speaker takes. They are flagged at every
level with `is_synthetic = True` and full provenance columns.

### 6.1 Generation method (authoritative)

Source: `Whisper_Verification_Sessions/session_20260521_132123_v7_natural_synth_metadata_splits/01_synthesize_v7_edge_tts.py` (+ `02_synthesize_residual_fix.py`).

1. **Engine:** Microsoft **Edge-TTS Neural** (`edge_tts` Python package),
   `synthesis_engine = "microsoft_edge_tts_neural"`.
2. **Gender-matched voices:** `id-ID-ArdiNeural` for the 11 male speakers,
   `id-ID-GadisNeural` for the 9 female speakers (voice gender matches the
   real speaker the file substitutes for).
3. **Pipeline:** TTS → MP3 → `ffmpeg -ar 16000 -ac 1 -sample_fmt s16` →
   16 kHz / mono / PCM-16 WAV (identical format to real audio).
4. **Two rounds:** `v7_initial` (124 files) + `v7_residual_fix` (8 files) = 132.
5. **Quality gate:** each synthetic WAV was transcribed with
   **Whisper-large-v3** and scored by text similarity to the target sentence.
   Acceptance threshold ≥ 0.70.

> **Important honesty note for the paper:** the voices are TTS, **not**
> speaker-cloned to the original respondent. The provenance CSV records a
> `recommend_retake = True` flag for paper-grade authenticity, but the files
> are kept and disclosed rather than hidden.

### 6.2 Quality verification result

| Metric | Value |
|---|---|
| Files generated | 132 / 132 (0 failures) |
| Whisper-similarity mean | **0.9941** |
| Whisper-similarity min | 0.9101 |
| Pass ≥ 0.90 | 132 / 132 (100 %) |

### 6.3 Distribution (evaluation integrity preserved)

| Split | Synth | % of split |
|---|---:|---:|
| train | 122 | 0.170 % |
| dev | 8 | 0.052 % |
| test | **2** | **0.013 %** |

Only 2 synthetic files reach the test split, so evaluation is effectively on
real speech. By gender: 73 male-voice + 59 female-voice. Most-affected
category is Konfirmasi (29); least is Deklaratif (2). The 8 dev-split synthetic
files all use the male voice (`id-ID-ArdiNeural`), consistent with the all-male
dev split.

→ Figure: `F7_synthetic_disclosure.pdf`.

---

## 7. Limitations (paper §-ready)

1. **Synthetic fraction.** 132 Edge-TTS files (0.129 %); TTS voices are not
   speaker-cloned. Disclosed per corpus/split/speaker (§6). Test split contains
   only 2 synthetic files.
2. **Dev split is all-male** (Amri, Fajar, Pram). Sex-conditional analyses
   should use the mixed-sex **test** split, not dev.
3. **Four categories slightly smaller** (~9,010 vs 9,500 files): one base
   sentence per affected category was dropped during transcript
   canonicalization (the 1,956-orphan Strategy-A cleanup, v7). Category balance
   remains excellent (Gini 0.012).
4. **Duration outliers.** A few utterances reach up to 206 s (long/merged
   takes). These survive the clean metadata; trainers cap/pad by feature
   length. The histogram in F8 is clipped at 20 s for readability.
5. **Audio-quality micro-stats** (SNR, silence ratio, spectral centroid) are
   not recomputed here — they exist in the prior elsevier session
   (`stats/audio_quality_sample.csv`, n = 297 stratified sample) and are not
   affected by the pipeline binding.

---

## 8. Reproducibility

```bash
# Regenerates every CSV, the master JSON, and all 8 figures (~20 s, no audio I/O)
python3 Whisper_Verification_Sessions/session_20260530_125618_dataset_stats_v7_paper9/compute_stats.py
```

Reads only `metadata/dataset_metadata_clean.csv` + `splits/*_clean.tsv`
(respects the project AGENTS.md scan rules — no audio-tree traversal).

**Outputs:**
- `stats/dataset_stats.json` — master machine-readable summary
- `stats/{per_category,per_speaker,per_split,word_frequency}.csv`
- `figures/F1…F8.{pdf,png}` — Data in Brief style (serif, 600 DPI PNG, vector
  PDF, Okabe-Ito color-blind-safe palette, `pdf.fonttype=42`)
- `figures/figure_manifest.csv`

---

## 9. Figure index

| Fig | Content | File |
|---|---|---|
| F1 | Files per speaker (gender-colored) | `figures/F1_files_per_speaker.pdf` |
| F2 | Mean duration per category | `figures/F2_duration_per_category.pdf` |
| F3 | Recording hours per category | `figures/F3_hours_per_category.pdf` |
| F4 | Files & hours by gender | `figures/F4_gender_distribution.pdf` |
| F5 | Zipf word rank–frequency | `figures/F5_word_frequency_zipf.pdf` |
| F6 | Split composition by gender | `figures/F6_split_gender.pdf` |
| F7 | Edge-TTS synthetic fraction per split | `figures/F7_synthetic_disclosure.pdf` |
| F8 | Utterance duration distribution | `figures/F8_duration_histogram.pdf` |
