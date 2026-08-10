# Display and Supplement Plan

**Status:** internal planning document; **NOT FOR SUBMISSION OR PUBLIC RELEASE**  
**DOCX target:** supplied Data in Brief article template v.19 (December 2024)

The template-based DOCX embeds the seven-row Specifications Table, numbered Tables 1–5, and Figures 1–3. Supplementary Table S6 remains editable in CSV/XLSX but is not embedded as a sixth main-text table. Figure 4 remains blocked.

## Selection principles

1. Main-text displays must directly help readers understand, filter, reproduce, or reuse the dataset.
2. Every display must declare its scope: release target (104,500), frozen benchmark (102,544), or sampled diagnostics (297).
3. Every figure/table must have deposited source values and a reproducible generation path.
4. Existing benchmark-scope plots must not be relabelled as release-target plots.
5. Model timing is excluded from comparative displays because hardware and execution environments differ.
6. Public speaker IDs may appear; private names and the crosswalk may not.
7. Tables remain editable; figures are separate files with self-contained captions.

## Main-text tables

### Specifications Table — journal template

**Disposition:** retain and completely rebuild.

**Purpose:** populate the seven fixed v.19 rows: Subject, Specific subject area, Type of data, Data collection, Data source location, Data accessibility, and Related research article.

**Limits:** Specific subject area ≤150 characters excluding spaces; Data collection ≤600 characters excluding spaces.

**Blocked fields:** equipment/software/distance, recruitment/session/QC, access/DOI/licence, related-paper overlap, and any demographic detail requiring author verification.

### Table 1 — Archive and package inventory

**Disposition:** main text.

**Columns:** component, path/archive member, format, rows/files, purpose, scope, checksum/version.

**Include:**

- 11 category tar shards;
- recording-level metadata;
- transcript inventory;
- split manifests;
- schema/data dictionary;
- synthetic repair manifest;
- figure/table source values;
- validation/reproduction scripts;
- checksum manifest.

**Current evidence:** `hf_dataset_remote_files.json`, private HF snapshot, reports, and final release manifest. Final DOI/access fields remain blocked.

### Table 2 — Release-target and frozen-benchmark scope bridge

**Disposition:** main text and cited before any benchmark result.

| Field | Release target | Frozen benchmark |
|---|---:|---:|
| Files | 104,500 | 102,544 |
| Duration | 134.1762 h | 130.6548 h |
| Train/val/test | 73,150 / 15,675 / 15,675 | 71,792 / 15,376 / 15,376 |
| Distinct `(category, sentence_id)` pairs | 213 | 209 |
| Transcript state | Repaired private HF staging has zero blanks | Frozen before repair; excludes 1,956 rows |
| Intended use in article | Corpus description | Nine-model technical validation |

**Mandatory note:** audio shards did not change during the metadata repair.

### Table 3 — Release-target category composition

**Disposition:** main text.

**Source:** [`Report_paper_9model/hf_dataset_information_public/per_category_public.csv`](../../../Report_paper_9model/hf_dataset_information_public/per_category_public.csv).

**Columns:** English public category, files, duration (h), mean duration (s), synthetic files, distinct `(category, sentence_id)` pairs or replacement note.

**Control:** use authoritative release-target means (e.g., Persuasive 6.5202 s, Conditional 6.0519 s, Confirmation 5.6065 s), not the older benchmark means 6.43/5.96/5.58 s.

### Table 4 — Release-target split and source composition

**Disposition:** main text.

**Source:** `per_split_public.csv`, corrected `per_speaker_public.csv`, and synthetic summary.

**Columns:** split, human speakers, files, duration (h), synthetic files, male-source files, female-source files, interpretation note.

**Mandatory notes:**

- retained human public speaker-label counts are 14/3/3;
- development has zero female-source files;
- the two female-source test files are synthetic and target M8;
- there is no natural female development/test speaker;
- “speaker-disjoint” applies to human public IDs, not necessarily recurring TTS voices.

### Table 5 — Synthetic repair provenance

**Disposition:** main text, compact.

**Source:** `synthetic_data_stats_public.json` and public repair-row manifest.

**Rows/blocks:** total and percentage, duration, provider/voices, male/female source counts, train/val/test counts, category counts, source-draft no-cloning assertion with technical-confirmation status, filtering field, and mismatch status.

**Gate:** finalize only after authors decide whether to regenerate, exclude, or retain the two mismatch rows. Any changed data require regenerated totals and tables.

### Supplementary Table S6 — Frozen-benchmark technical validation

**Disposition:** supplementary and subordinate to dataset description. If editors later require a main-text table and every per-recipe method card, sensitivity result, and interpretation gate is adequate, rename the display globally to the next main-table number and remove the S6 identity.

**Columns:** model family, uniformly rescored WER (%), and uniformly rescored CER (%). Keep parameter counts in supplementary method cards because the HMM-GMM template-bank count is not comparable with neural trainable parameters.

**Metric source:** the uniform diagnostic rescore in [`Draft_Paper/02_Evidence/unified_benchmark_rescore/`](../../02_Evidence/unified_benchmark_rescore). Historical run-native values and their ranking are provenance only because reference normalization and denominators differed across recipes.

**Include:** all nine models together or move all nine to the supplement; do not cherry-pick rows. Do not include a performance-rank, timing, or superiority column.

**Caption controls:**

- frozen 102,544-file scope;
- 15,376-item test set = 15,374 human + 2 synthetic;
- held-out human speaker IDs but seen scripts;
- one canonical reference manifest, one named normalizer, and shared word/character denominators;
- diagnostic rescore of existing predictions, not an inference rerun;
- heterogeneous training/pretraining/tokenizer/decoder conditions;
- no speed/efficiency comparison;
- WER/CER are percentages with declared rounding.

## Main-text figures

### Figure 1 — NSS-ID construction and package flow

**Disposition:** new main figure.

**Content:**

```text
recruitment/consent evidence [MATERIAL GAP / gate]
        ↓
11-category prompt inventory and stable sentence IDs
        ↓
prompted read-speech source tree (20 retained human labels)
        ↓                         ↘ 132 labelled TTS repairs
segmentation/transcript assignment/structural QC
        ↓
pre-transcript-repair 104,500-row metadata state
        ├─ transcript repair → 104,500-row release target → package/private staging
        └─ blank-row exclusion → 102,544-row frozen benchmark
```

**Style:** factual schematic created with deterministic drawing tools, not generative AI. No names, private paths, unverified equipment, or unsupported counts. No arrow may run from the repaired release-target node to the earlier frozen benchmark node.

### Figure 2 — Release-target duration by category

**Disposition:** regenerate for main text from Tier-A data.

**Source values:** `per_category_public.csv`.

**Do not reuse as-is:** `Whisper_Verification_Sessions/.../F2_duration_per_category.png` was generated from the 102,544-row benchmark statistics and contains stale category means for the release-target narrative.

**Caption:** total and mean duration for each of 11 categories in the 104,500-row release target; 9,500 files per category; descriptive only, with no causal linguistic-complexity interpretation.

### Figure 3 — Release-target split/source composition

**Disposition:** new main figure or, if redundant with Table 4, omit from the main text.

**Source values:** `per_split_public.csv` plus corrected speaker counts.

**Design:** three grouped panels or stacked bars for files/hours, human speakers, and male/female acoustic-source files; overlay synthetic counts explicitly.

**Caption:** state that female-source development count is zero and the two female-source test files are synthetic; no gender-generalization inference.

### Figure 4 — Acoustic diagnostics for 297 sampled files

**Disposition:** conditional main figure; move to supplement unless the sample frame, allocation, seed, and inclusion criteria are attached.

**Source:** `audio_quality_sample_public.csv`.

**Metrics:** dynamic range, silence ratio, spectral centroid.

**Do not reuse without audit:** existing `F12_audio_quality.png` derives from an earlier analysis package. Regenerate from the public-safe row sample and add the exact scope to the caption.

**Caption controls:** sampled diagnostic only; does not establish corpus-wide SNR, clipping, reverberation, integrity, or transcript accuracy.

## Supplementary tables

| ID | Content | Source / gate |
|---|---|---|
| Table S1 | Full recording-level metadata dictionary | Public schema; verify exact final archive fields |
| Table S2 | Complete 213 `(category, sentence_id)` release-target inventory | `transcript_template_stats.csv` and pinned remote transcript inventory |
| Table S3 | Partial replacement pairs and intentional numbering gaps | Row-level inventory and numbering note |
| Table S4 | Public per-speaker files, duration, split, and source-label fields | Corrected `per_speaker_public.csv`; omit region/age unless consented and verified |
| Table S5 | Complete synthetic repair-target and row inventory | Public repair manifest; finalize after mismatch decision |
| Table S6 | Full nine-model protocol, uniform-rescore scores, run-native provenance, parameters, and decoding | Model cards, configs, `unified_benchmark_rescore/`, and `benchmark.json`; no historical run-native or timing ranking |
| Table S7 | Benchmark split and template-overlap audit | Attach exact overlap report and manifest hashes |
| Table S8 | Transcript-repair manifest and audit summary | Repair script, join keys, hashes, manual audit result |
| Table S9 | 297-file sampling frame, strata/allocation, seed, and summary | Sampling code/manifest; unavailable fields remain a gap |
| Table S10 | Evidence and checksum manifest | SHA-256 of every manuscript-facing data/table/figure input |

## Supplementary figures

| Existing figure | Proposed disposition | Reason / required change |
|---|---|---|
| F1 files per speaker/split | Supplement, regenerate from corrected Tier-A public labels | Useful balance view but Table 4 is more important; avoid implying population balance |
| F3 speaker total duration | Supplement, regenerate from Tier-A data | Reuse aid; no speaker-dominance or generalization claim |
| F4 sentence length | Supplement, regenerate/re-audit scope | Descriptive prompt-set property, not inherent category complexity |
| F5 word-frequency Pareto | Supplement only | Can describe prompted vocabulary; cannot establish everyday-language representativeness |
| F6 Heaps law | Supplement or exclude | Limited interpretive value for repeated closed prompts; no natural-corpus claim |
| F7 speaker-category heatmap | Supplement, corrected labels only | Useful for coverage; dense and redundant in main text |
| F8 cumulative hours | Supplement or exclude | Descriptive but low reuse value once tables give hours |
| F9 audio uniformity | Supplement after direct header audit | Do not use as corpus-quality proof |
| F10 synthetic disclosure | Supplement; Table 5 remains main | Tiny fraction is clearer in a table; retain graphic only if labels and source data are self-contained |
| F11 mel-spectrogram exemplars | Supplement | Visually useful examples, but selection method and exact source files must be documented |
| F12 sampled audio quality | Main only after sample-provenance gate; otherwise supplement | Sample-limited technical-validation evidence |

## Excluded displays and evidence

1. **All stale benchmark-scope descriptive figures presented as full-corpus figures.** Existing Elsevier figures were generated from `metadata/dataset_metadata_clean.csv` unless explicitly regenerated from Tier A.
2. **FG1–FG3 gender figures from the old 11-male/9-female assignment.** They conflict with corrected 12-male/8-female public labels.
3. **Any plot of training or inference time ranking.** Hardware, pretraining, batches, and execution environments are heterogeneous.
4. **Robot/live/OOD accuracy plots.** References are Whisper-derived/development-only and do not establish corpus or field accuracy.
5. **Regional/dialect maps or demographic cross-tabs.** Consent/privacy and authoritative-source gates are unresolved.
6. **Private speaker-name tables or figures.** The crosswalk remains outside Git, HF, and manuscript artifacts.
7. **Model architecture screenshots as primary article figures.** They shift the article toward a model paper; retain only reproducible schematics in the benchmark supplement if necessary.
8. **Old submission-readiness charts or declarations.** They contain stale values/placeholders and are Tier-E evidence only.

## Caption checklist

Every main and supplementary caption must state, as applicable:

- population/scope and exact `n`;
- units;
- human versus synthetic treatment;
- release target versus benchmark versus sample;
- source-value file deposited with the dataset;
- any limitation needed to prevent overinterpretation;
- public labels only;
- no unsupported causal or generalization language.

## File-production rule

Final table source CSV/DOCX files and figure source CSV/script files will be generated under [`Draft_Paper/04_Revised_Draft/`](../../04_Revised_Draft) and copied to [`Draft_Paper/05_Submission_Package/`](..) only after scope, privacy, and checksum verification. Existing figures are evidence inputs, not automatically approved submission assets.
