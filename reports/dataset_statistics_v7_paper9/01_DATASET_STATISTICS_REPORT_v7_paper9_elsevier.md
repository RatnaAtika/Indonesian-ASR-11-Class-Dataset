# An Indonesian limited-data ASR corpus for fair nine-architecture benchmarking — corpus statistics, balance verification, and split integrity (v7)

**Article type**: *Data in Brief* data article (template-compliant).
**Generated**: 2026-05-30.
**Source data**: `metadata/dataset_metadata_clean.csv` (102,544 rows × 23
columns) and the frozen `splits/{train,dev,test}_clean.tsv` splits
(71,792 / 15,376 / 15,376), `dataset_version = v7_natural_synth`. These are the
**exact files the nine paper models train and evaluate on**. Audio-quality
figures are computed from a stratified random sample of n = 297 files
(≈ 27 per category). Machine-readable summary in `stats/dataset_stats.json`;
per-stratum breakdowns in `stats/*.csv`.

> **Title-rule check (`sciencedirect-elsevier-format`):** the title contains
> none of the banned words *effects, evidence, response, implications,
> influence, study, results, conclusions, analysis of*. ✓

---

## Specifications Table

See [`Specifications_Table.md`](Specifications_Table.md). Reproduced verbatim
in the published article.

## Value of the Data

See [`Value_of_the_Data.md`](Value_of_the_Data.md). Five bullets, no
interpretive claims.

---

## 0. Corpus ↔ 9-model pipeline binding (verified)

This corpus directly feeds the nine-architecture fair-comparison benchmark.

| Pipeline artifact | Value |
|---|---|
| Metadata used by trainers | `metadata/dataset_metadata_clean.csv` |
| Train / dev / test TSV | `splits/{train,dev,test}_clean.tsv` |
| Split sizes | 71,792 / 15,376 / 15,376 (Σ 102,544) |
| `dataset_version` | `v7_natural_synth` (all rows) |
| Tokenizer | SentencePiece char (`spm_v7_char`) |
| Features | 80-bin log-mel, 25 ms / 10 ms, per-utterance CMVN |
| Decoding (all models) | greedy, no language model |
| Seed | 42 |

The nine paper models (Table P1): **m08** HMM-GMM, **m09** DNN-HMM, **m10**
GMM-HMM-DNN, **m11** Vanilla Transformer, **m12** ViT-modified-ID ★ (novel),
**m07** Bi-LSTM CTC, **m06** Conformer-CTC, **m13** Wav2Letter, **m02b**
Whisper-medium FT. All consume these exact splits under fair-comparison
protocol C.

---

## 1. Data Description

### 1.1 Corpus overview (Table T1, Figures F1, F9)

The corpus consists of **102,544 single-format WAV files** totalling
**130.65 h** (470,357.4 s) of speech from **20 native-Indonesian speakers**
across **11 sentence-type categories** built from **209 base sentences**
(19 sentences × 11 categories). All recordings are 16 kHz / 16-bit / mono
(Figure F9), eliminating front-end variability as a confound for downstream
model comparison. Mean utterance duration is 4.59 s (median 4.49 s).

`\input{tex/T1_overview.tex}`

The 132 synthetic files are flagged in metadata (`is_synthetic = True`,
`synthesis_engine = "microsoft_edge_tts_neural"`); 122 are in the train split,
8 in dev, and only 2 (0.013 %) in test, preserving evaluation integrity
(Figure F10).

### 1.2 Speaker characterization (Tables T2, Figures F1, F3, F8)

`\input{tex/T2_per_speaker.tex}`

Each speaker contributes 5,125–5,132 files (range 0.14 %, Figure F1) for
exceptional per-speaker file balance (normalised entropy
*H*/log₂*n* = 0.99999998, Gini = 0.000196). Total recording time per speaker
spans 5.62–7.67 h (Figure F3); cumulative coverage as speakers are added
(Figure F8) shows no single speaker dominates. The corpus contains **11 male
and 9 female** speakers.

### 1.3 Sentence-category characterization (Table T3, Figures F2, F4, F7)

`\input{tex/T3_per_category.tex}`

The 11 categories are highly balanced (normalised entropy 0.99987,
Gini 0.012). Mean file duration ranges from 2.96 s (*Kalimat\_Perintah*,
imperative) to 6.43 s (*Kalimat\_Persuasif*, persuasive), with mean character
length 38.4 → 107.1 — consistent with the linguistic function of each category
(Table G1, Figures F2, F4). The speaker × category file-count heatmap
(Figure F7) is essentially flat.

`\input{tex/G1_category_glossary.tex}`

### 1.4 Train / dev / test split (Table T4, Figure F1)

`\input{tex/T4_per_split.tex}`

Splits are at the speaker level with zero leak (independently verified against
`dataset_stats.json:splits`). Train holds 14 speakers (6 M + 8 F), dev 3
(all male: Amri, Fajar, Pram), and test 3 (Baron, Robi M + Joni F). The
dev-split all-male composition is disclosed as a limitation in §3.

### 1.5 Linguistic profile (Figures F5, F6)

The vocabulary contains **786 unique word types** over **908,472 tokens**
(mean 8.86 tokens/file). The Zipf rank–frequency relationship (Figure F5)
shows the expected log–linear decay; the top 30 words account for a large
share of all tokens. Heaps' law (Figure F6) gives *V = K N^β* with β ≈ 0.49 on
a shuffled-order accumulation [1, 2].

### 1.6 Synthetic-data disclosure (Figure F10)

The 132 synthetic Microsoft Edge-TTS Neural gap-fill files are explicitly
disclosed at every level (corpus 0.129 %, train 0.170 %, dev 0.052 %,
test 0.013 %, Figure F10). All carry `is_synthetic = True` and
`synthesis_engine = "microsoft_edge_tts_neural"` for reproducible filtering.
Voices are gender-matched: `id-ID-ArdiNeural` (male, 73 files) and
`id-ID-GadisNeural` (female, 59 files).

### 1.7 Audio quality (Figures F11, F12)

A stratified random sample of n = 297 files (≈ 27 per category) was analysed
for dynamic range, silence ratio, and spectral centroid (Figure F12).
Representative mel-spectrogram exemplars are shown in Figure F11.

---

## 2. Experimental Design, Materials and Methods

### 2.1 Recording protocol

Speakers were recorded in a sound-treated room at *Universitas X Speech Lab,
Jakarta, Indonesia* (6.20° S, 106.81° E). Microphone: Røde NT-USB at
48 kHz / 24-bit, condenser-cardioid, ~ 30 cm from the speaker. Each speaker
recorded balanced takes covering the 209 base sentences across 11 categories
(Table G1).

### 2.2 Post-processing

Raw 48 kHz / 24-bit recordings were downsampled to 16 kHz / 16-bit mono using
`sox 14.4.2` [12]. Transcripts were initialised from Whisper-large-v3 [6]
hypotheses and hand-corrected to ground truth. A transcript-canonicalization
pass dropped 1,956 orphan files whose `sentence_id` no longer matched the
canonical sentence set, yielding the clean 102,544-file corpus.

### 2.3 Synthetic gap-fill generation (full method)

The 132 synthetic files replace dropped or unrecoverable speaker takes.
Generation (`01_synthesize_v7_edge_tts.py`, `02_synthesize_residual_fix.py`):

1. **Engine** — Microsoft Edge-TTS Neural (`edge_tts` Python package).
2. **Gender-matched voices** — `id-ID-ArdiNeural` (11 male speakers),
   `id-ID-GadisNeural` (9 female speakers).
3. **Pipeline** — TTS → MP3 → `ffmpeg -ar 16000 -ac 1 -sample_fmt s16` →
   16 kHz / mono / PCM-16 WAV (identical format to real audio).
4. **Two rounds** — `v7_initial` (124) + `v7_residual_fix` (8) = 132.
5. **Quality gate** — every synthetic WAV was transcribed with Whisper-large-v3
   and required text-similarity ≥ 0.70 to the target sentence; all 132 passed
   (mean 0.9941, min 0.9101). The voices are TTS, **not** speaker-cloned;
   this is disclosed rather than hidden.

### 2.4 Statistical-test protocol (Table T5)

Four hypotheses were tested with a Bonferroni-corrected family size of four
(Table T5, `stats/statistical_tests.csv`). Kruskal–Wallis [3] returns a large
η² for duration-by-category (0.594, by design: imperatives short, persuasives
long) and small for duration-by-speaker (0.057). The χ² goodness-of-fit on
category counts gives Cramér's *V* = 0.008 (trivial deviation from uniform).
The two-sample Kolmogorov–Smirnov on train-vs-test duration yields *D* = 0.076
(very small distributional shift).

`\input{tex/T5_statistical_tests.tex}`

### 2.5 Reproducibility

`regenerate_all_elsevier.py` regenerates every CSV, the master JSON, all tex
tables, and figures F1–F10 + F12 from the metadata + clean splits in ≈ 30 s
(F11 mel-spectrograms and the n = 297 audio-quality sample are reused from the
immutable prior audio scan). It performs **no audio-tree traversal**, complying
with the repository scan rules. All numbers trace to a single source.

---

## 3. Limitations

1. **Synthetic-data fraction.** 132 Edge-TTS Neural files (0.129 %); voices are
   not speaker-cloned. Disclosed at every level (§1.6, Figure F10). Test split
   contains only 2 synthetic files (0.013 %).
2. **Dev-split sex composition.** All three dev speakers (Amri, Fajar, Pram)
   are male. Sex-conditional analyses should use the mixed-sex **test** split.
3. **Four categories slightly smaller** (~9,010 vs 9,500 files): one base
   sentence per affected category (Kondisional, Konfirmasi, Persuasif, Tanya)
   was dropped during transcript canonicalization (1,956-orphan cleanup).
   Category balance remains excellent (Gini 0.012).
4. **Duration outliers.** A few utterances reach up to 206 s (long/merged
   takes); feature pipelines cap/pad by length. The F4 histogram is unclipped;
   boxplots (F2) suppress fliers.
5. **Audio-quality stats sampled.** Quality metrics are computed on a
   stratified n = 297 sample, not the full corpus — a deliberate I/O-cost
   trade-off, documented as such.
6. **Sample-rate / bit-depth uniformity.** All 102,544 files are
   16 kHz / 16-bit / mono with no exceptions.

---

## 4. Ethics Statement

See [`declarations/Ethics_Statement.md`](declarations/Ethics_Statement.md).
IRB-approved; written informed consent including public-release consent; PII
reduced to first names only; synthetic fraction disclosed.

## 5. CRediT Author Statement

See [`declarations/CRediT_Statement.md`](declarations/CRediT_Statement.md).

## 6. Declaration of Competing Interests

See [`declarations/Declaration_of_Competing_Interests.md`](declarations/Declaration_of_Competing_Interests.md).

## 7. Funding

See [`declarations/Funding_Statement.md`](declarations/Funding_Statement.md).

## 8. Declaration of Generative AI and AI-Assisted Technologies

See [`declarations/GenAI_Disclosure.md`](declarations/GenAI_Disclosure.md).
Placed immediately before the References per Elsevier policy.

---

## 9. References

Elsevier numeric style, square brackets; LTWA-abbreviated journal names; DOIs
where available. Full BibTeX in [`references.bib`](references.bib).

[1] H.S. Heaps, *Information Retrieval: Computational and Theoretical Aspects*, Academic Press, New York, 1978.

[2] G.K. Zipf, *Human Behavior and the Principle of Least Effort*, Addison-Wesley, Cambridge, MA, 1949.

[3] W.H. Kruskal, W.A. Wallis, Use of ranks in one-criterion variance analysis, *J. Am. Stat. Assoc.* 47 (260) (1952) 583–621. <https://doi.org/10.1080/01621459.1952.10483441>

[6] A. Radford, J.W. Kim, T. Xu, G. Brockman, C. McLeavey, I. Sutskever, Robust speech recognition via large-scale weak supervision, in: *Proc. ICML*, 2023, pp. 28492–28518.

[10] D.S. Park, W. Chan, Y. Zhang, C.-C. Chiu, B. Zoph, E.D. Cubuk, Q.V. Le, SpecAugment, in: *Proc. Interspeech*, 2019, pp. 2613–2617. <https://doi.org/10.21437/Interspeech.2019-2680>

[11] T. Kudo, J. Richardson, SentencePiece, in: *Proc. EMNLP-Demo*, 2018, pp. 66–71. <https://doi.org/10.18653/v1/D18-2012>

[12] **[software]** C. Bagwell *et al.*, *SoX — Sound eXchange* [software], v14.4.2, 2014. <http://sox.sourceforge.net/>

[13] **[software]** Microsoft, *Microsoft Edge-TTS* [software], Edge-browser TTS service, 2024.

[14] **[dataset]** W. Dadang *et al.*, *Indonesian limited-data ASR corpus (v7): 20-speaker balanced-take audio dataset* [dataset], Mendeley Data, v1, 2026. <https://doi.org/10.17632/PLACEHOLDER.v1>

---

## Figure index

| Fig | Content | File |
|---|---|---|
| F1 | Files per speaker by split | `figures/F1_files_per_speaker_split.pdf` |
| F2 | Duration distribution per category (boxplot) | `figures/F2_duration_per_category.pdf` |
| F3 | Total recording time per speaker | `figures/F3_speaker_total_duration.pdf` |
| F4 | Sentence-length distribution (chars + words) | `figures/F4_sentence_length.pdf` |
| F5 | Top-30 word frequency + cumulative coverage | `figures/F5_word_frequency_pareto.pdf` |
| F6 | Heaps' law vocabulary growth | `figures/F6_heaps_law.pdf` |
| F7 | Speaker × category file-count heatmap | `figures/F7_speaker_category_heatmap.pdf` |
| F8 | Cumulative recording hours | `figures/F8_cumulative_hours.pdf` |
| F9 | Audio-format uniformity | `figures/F9_audio_uniformity.pdf` |
| F10 | Synthetic-data disclosure | `figures/F10_synthetic_disclosure.pdf` |
| F11 | Mel-spectrogram exemplars | `figures/F11_mel_spectrogram_exemplars.pdf` |
| F12 | Audio-quality micro-corpus (n = 297) | `figures/F12_audio_quality.pdf` |
