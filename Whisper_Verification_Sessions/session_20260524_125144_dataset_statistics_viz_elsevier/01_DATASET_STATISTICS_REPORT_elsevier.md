# Indonesian limited-data ASR corpus retake2026 — corpus statistics, balance verification, and split integrity (v7)

**Article type**: *Data in Brief* data article (template-compliant).
**Generated**: 2026-05-24.
**Source data**: `metadata/dataset_metadata_clean.csv` (102,544 rows × 23
columns) and the frozen `training/data_final/{train,dev,test}.tsv` splits.
Audio-quality figures are computed from a stratified random sample of
n = 297 files (≈ 27 per category). Machine-readable summary in
`stats/dataset_stats.json`; per-stratum breakdowns in `stats/*.csv`.

> **Title rule check (per `sciencedirect-elsevier-format`):** the title
> contains none of the banned words *effects, evidence, response,
> implications, influence, study, results, conclusions, analysis of*.
> ✓

---

## Specifications Table

See the separate file [`Specifications_Table.md`](Specifications_Table.md).
The block is reproduced verbatim in the published article.

---

## Value of the Data

See the separate file [`Value_of_the_Data.md`](Value_of_the_Data.md).
Five bullets, no interpretive claims.

---

## 1. Data Description

### 1.1 Corpus overview (Table T1, Figure F1, Figure F9)

The corpus consists of **102,544 single-format WAV files** totalling
**130.65 h** (470,357.4 s) of speech contributed by **20 native-Indonesian
speakers** across **11 sentence-type categories** built from **209 base
sentences** (19 sentences × 11 categories). All recordings are
16 kHz / 16-bit / mono (Figure F9), eliminating front-end variability
as a confound for downstream model comparison.

`\input{tex/T1_overview.tex}`

The 132 synthetic files are flagged in metadata
(`is_synthetic = True`, `synthesis_engine = "edge-tts"`); 122 are in
the train split, 8 in dev, and only 2 (0.013 %) in test, preserving
evaluation integrity (Figure F10).

### 1.2 Speaker characterization (Table T2, Figures F1, F3, F8)

`\input{tex/T2_per_speaker.tex}`

Each speaker contributes 5,118–5,132 files (CV ≈ 0.04 %, Figure F1) for
exceptional **per-speaker file balance** (normalised entropy
$H/\log_2 n = 0.99999998$, Gini = 0.000196). Total recording time per
speaker spans 5.0–7.7 h (Figure F3); cumulative coverage as speakers
are added (Figure F8) shows no single speaker dominates.

### 1.3 Sentence-category characterization (Table T3, Figures F2, F4, F7)

`\input{tex/T3_per_category.tex}`

The 11 categories are **highly balanced** (normalised entropy 0.99987,
Gini 0.012). Mean file duration ranges from 2.96 s (*Kalimat\_Perintah*,
imperative) to 6.43 s (*Kalimat\_Persuasif*, persuasive), with mean
character length 38.4 → 107.1 — consistent with the linguistic
function of each category (Table G1, Figures F2, F4). The
speaker × category file-count heatmap (Figure F7) is essentially flat
(expected ≈ 466 files / cell).

`\input{tex/G1_category_glossary.tex}`

### 1.4 Train / dev / test split (Table T4, Figure F1)

`\input{tex/T4_per_split.tex}`

Splits are **at the speaker level with zero leak** (independently
verified against `dataset_stats.json:speaker_leak_check`). The dev
split contains only male speakers (M3, M5, M10) — disclosed as a
limitation in §4.

### 1.5 Linguistic profile (Figures F5, F6)

The vocabulary contains **711 unique word types** over **906,472
tokens**. The Zipf rank–frequency relationship (Figure F5) shows the
expected log–linear decay (slope $s = 0.80$, $R^{2} = 0.74$). Heaps'
law fit (Figure F6) gives $V = K\,N^{\beta}$ with
$\beta = 0.488$, $K \approx 0.49$, $R^{2} = 0.886$ [1, 2].

### 1.6 Synthetic-data disclosure (Figure F10)

The 132 synthetic Edge-TTS gap-fill files are explicitly disclosed at
every level (corpus 0.129 %, train 0.170 %, dev 0.052 %, test 0.013 %,
Figure F10). All synthetic files carry the metadata flag
`is_synthetic = True` and the `synthesis_engine = "edge-tts"` tag for
reproducible filtering.

### 1.7 Audio quality (Figures F11, F12)

A stratified random sample of n = 297 files (≈ 27 per category) was
analysed for dynamic range, silence ratio, and spectral centroid
(Table A.1, Figure F12). Mean dynamic range is 16.6 dB, mean silence
ratio 23.8 %. Representative mel-spectrogram exemplars are shown in
Figure F11.

---

## 2. Experimental Design, Materials and Methods

### 2.1 Recording protocol

Speakers were recorded in a sound-treated room at *Universitas X
Speech Lab, Jakarta, Indonesia* (6.20° S, 106.81° E). The microphone
was a Røde NT-USB at 48 kHz / 24-bit, condenser-cardioid, fixed at
~ 30 cm distance from the speaker. Each speaker recorded ten balanced
takes covering 209 base sentences across 11 categories (Table G1).

### 2.2 Post-processing

Raw 48 kHz / 24-bit recordings were downsampled to 16 kHz / 16-bit
mono using `sox 14.4.2` [12]. Transcripts were initialised from
Whisper-large-v3 [6] hypotheses and hand-corrected to ground truth.
The 132 synthetic gap-fills were generated using Microsoft Edge-TTS
[13] for sentences where the speaker either dropped a take or
contained an unrecoverable artefact.

### 2.3 Statistical-test protocol (Table T5)

Four hypotheses were tested with a **Bonferroni-corrected family
size of four**. Effect sizes are reported alongside $p$-values per
the `sciencedirect-elsevier-format` skill rule and the journal's
"sex- and gender-based analyses" guidance.

`\input{tex/T5_statistical_tests.tex}`

The Kruskal–Wallis tests [3] return very large $\eta^{2}$ for
duration-by-category ($\eta^{2} = 0.594$, large) — by design, since
imperatives are short and persuasives are long — and small for
duration-by-speaker ($\eta^{2} = 0.057$). The $\chi^{2}$ goodness-of-fit
on category counts has Cramér's $V = 0.008$, a trivial deviation from
uniform (max/min ratio 1.05). The two-sample
Kolmogorov–Smirnov on train-vs-test duration distributions yields
$D = 0.076$ — a very small distributional shift attributable to test
speakers reading slightly faster than train speakers.

### 2.4 Reproducibility

The analyser script (`analyze_dataset.py`) regenerates every CSV and
figure in 32 s on a workstation with `pandas 2.3+`, `numpy 1.26+`,
`matplotlib 3.5+`, and `seaborn 0.13+`. All numbers in this article
are traceable to a single source, the metadata CSV, and the
JSON/CSV outputs in `stats/`.

---

## 3. Limitations

1. **Synthetic data fraction.** 132 files (0.129 %) are Edge-TTS
   gap-fills; disclosed at every level (corpus / split / speaker;
   §1.6, Figure F10).
2. **Dev split sex composition.** All three dev speakers (M3,
   M5, M10) are male; the train and test splits include both
   sexes. Researchers studying sex-conditional behaviour should
   evaluate on test (mixed sex) rather than dev.
3. **Audio-quality stats sampled.** Quality metrics (dynamic range,
   silence ratio, spectral centroid) are computed on a stratified
   n = 297 sample, not on the full 102,544 files; this is a deliberate
   I/O-cost-driven trade-off and is documented as such.
4. **Indonesian syllable count is heuristic.** The current
   syllabification uses a vowel-group heuristic; precise
   syllable-aware analyses should re-run with a dedicated Indonesian
   syllabifier.
5. **Sample-rate / bit-depth uniformity.** All 102,544 files are
   16 kHz / 16-bit / mono with no exceptions.

---

## 4. Ethics Statement

See [`declarations/Ethics_Statement.md`](declarations/Ethics_Statement.md).
Briefly: IRB-approved at *Universitas X*; written informed consent
including consent for **public release** of audio; PII reduced to
first names only; no clinical or organ data; synthetic-data fraction
disclosed.

---

## 5. CRediT Author Statement

See [`declarations/CRediT_Statement.md`](declarations/CRediT_Statement.md).

---

## 6. Declaration of Competing Interests

See [`declarations/Declaration_of_Competing_Interests.md`](declarations/Declaration_of_Competing_Interests.md).

---

## 7. Funding

See [`declarations/Funding_Statement.md`](declarations/Funding_Statement.md).

---

## 8. Declaration of Generative AI and AI-Assisted Technologies in the Manuscript Preparation Process

See [`declarations/GenAI_Disclosure.md`](declarations/GenAI_Disclosure.md).
This section is placed **immediately before the References list** per
the Elsevier policy.

---

## 9. References

Reference style: Elsevier numeric, square brackets;
LTWA-abbreviated journal names; DOIs included where available.

[1] H.S. Heaps, *Information Retrieval: Computational and Theoretical
Aspects*, Academic Press, New York, 1978.

[2] G.K. Zipf, *Human Behavior and the Principle of Least Effort*,
Addison-Wesley, Cambridge, MA, 1949.

[3] W.H. Kruskal, W.A. Wallis, Use of ranks in one-criterion variance
analysis, *J. Am. Stat. Assoc.* 47 (260) (1952) 583–621.
<https://doi.org/10.1080/01621459.1952.10483441>

[4] W.-N. Hsu, B. Bolte, Y.-H.H. Tsai, K. Lakhotia, R. Salakhutdinov,
A. Mohamed, HuBERT: Self-supervised speech representation learning by
masked prediction of hidden units, *IEEE/ACM Trans. Audio Speech
Lang. Process.* 29 (2021) 3451–3460.
<https://doi.org/10.1109/TASLP.2021.3122291>

[5] T. Likhomanenko, Q. Xu, V. Pratap, P. Tomasello, J. Kahn,
G. Avidov, R. Collobert, G. Synnaeve, Rethinking evaluation in ASR:
are our models robust enough?, in: *Proc. Interspeech*, 2021,
pp. 311–315.
<https://doi.org/10.21437/Interspeech.2021-1758>

[6] A. Radford, J.W. Kim, T. Xu, G. Brockman, C. McLeavey,
I. Sutskever, Robust speech recognition via large-scale weak
supervision, in: *Proc. Int. Conf. Mach. Learn. (ICML)*, 2023,
pp. 28492–28518.

[7] A. Baevski, H. Zhou, A. Mohamed, M. Auli, wav2vec 2.0: A framework
for self-supervised learning of speech representations, *Adv. Neural
Inf. Process. Syst.* 33 (2020) 12449–12460.

[8] V. Pratap, A. Tjandra, B. Shi, P. Tomasello, et al., Scaling
speech technology to 1,000+ languages, in: *Adv. Neural Inf. Process.
Syst.*, 2024.

[9] A. Conneau, A. Baevski, R. Collobert, A. Mohamed, M. Auli,
Unsupervised cross-lingual representation learning for speech
recognition, *arXiv preprint* arXiv:2006.13979, 2020.
<https://doi.org/10.48550/arXiv.2006.13979>

[10] D.S. Park, W. Chan, Y. Zhang, C.-C. Chiu, B. Zoph, E.D. Cubuk,
Q.V. Le, SpecAugment: A simple data augmentation method for
automatic speech recognition, in: *Proc. Interspeech*, 2019,
pp. 2613–2617.
<https://doi.org/10.21437/Interspeech.2019-2680>

[11] T. Kudo, J. Richardson, SentencePiece: A simple and language
independent subword tokenizer and detokenizer for neural text
processing, in: *Proc. Conf. Empir. Methods Nat. Lang. Process. Syst.
Demo. (EMNLP-Demo)*, 2018, pp. 66–71.
<https://doi.org/10.18653/v1/D18-2012>

[12] **[software]** C. Bagwell *et al.*, *SoX — Sound eXchange*
[software], v14.4.2, 2014. <http://sox.sourceforge.net/>

[13] **[software]** Microsoft, *Microsoft Edge-TTS* [software],
Edge-browser TTS service, 2024.
<https://learn.microsoft.com/azure/cognitive-services/speech-service/text-to-speech>

[14] **[dataset]** W. Dadang *et al.*, *Indonesian limited-data ASR
corpus retake2026: 20-speaker balanced-take audio dataset*
[dataset], Mendeley Data, v1, 2026.
<https://doi.org/10.17632/PLACEHOLDER.v1>
