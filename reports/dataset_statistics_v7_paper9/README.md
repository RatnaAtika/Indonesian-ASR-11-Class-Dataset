# Session: Dataset statistics & visualization — v7 corpus for the 9-model paper

**Date:** 2026-05-30 · **Status:** final, paper-ready.

Re-derives all dataset statistics from the **exact files the nine paper models
train on** (`metadata/dataset_metadata_clean.csv` + `splits/*_clean.tsv`,
`dataset_version = v7_natural_synth`), replacing the pre-pipeline numbers in
`session_20260524_125144_dataset_statistics_viz_elsevier/`.

## Deliverables

| File | Purpose |
|---|---|
| `01_DATASET_STATISTICS_REPORT_v7_paper9.md` | Full paper-grade report (corpus, speakers, categories, splits, linguistics, synthetic method, limitations, reproducibility) |
| `GITHUB_DATASET_NARRATIVE.md` | Short README/dataset-card narrative (hours, categories, M/F, words, synthetic count + method) |
| `compute_stats.py` | Single reproducible script (reads metadata + clean splits only; no audio-tree traversal) |
| `stats/dataset_stats.json` | Master machine-readable summary |
| `stats/{per_category,per_speaker,per_split,word_frequency}.csv` | Per-stratum tables |
| `figures/F1…F8.{pdf,png}` | Data-in-Brief figures (serif, 600 DPI, Okabe-Ito palette, `pdf.fonttype=42`) |
| `figures/figure_manifest.csv` | Figure index |

## Headline numbers (verified, all reconcile)

- **102,544** utterances · **130.65 h** · **20** speakers (11 M + 9 F) · **11** categories · **209** base sentences.
- Files by gender: **Male 56,396 (55.0 %)** / **Female 46,148 (45.0 %)**.
- Splits: train **71,792** / dev **15,376** / test **15,376** (speaker-disjoint, zero leak).
- Audio: **16 kHz / 16-bit / mono**, 100 % uniform.
- Vocabulary: **786** types over **908,472** tokens (Zipfian).
- Synthetic: **132** files (0.129 %), Microsoft Edge-TTS Neural (Ardi/Gadis, gender-matched), Whisper-verified (mean sim 0.9941); only **2** in test split.

## Reproduce

```bash
python3 Whisper_Verification_Sessions/session_20260530_125618_dataset_stats_v7_paper9/compute_stats.py
```

## Reconciliation notes vs the earlier elsevier session

- Synthetic method confirmed as **Microsoft Edge-TTS Neural** (not the unrelated
  `synthesize_duplicate_wavs.py` augmentation script in the parent `Dataset ASR/`
  folder, which targets a different corpus). Authoritative source:
  `session_20260521_132123_v7_natural_synth_metadata_splits/01_synthesize_v7_edge_tts.py`.
- **209 base sentences** clarified as 19 unique sentences × 11 categories
  (the `sentence_id` metadata column is a per-category index 1–20).
- Vocabulary here is **786** types (raw lowercased tokens over all 102,544 rows);
  the earlier session reported 711 after additional filtering. Both are disclosed.
