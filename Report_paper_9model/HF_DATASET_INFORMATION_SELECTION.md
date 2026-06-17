# HF Dataset Information Package Selection

Purpose: choose the most useful dataset-information artifacts to include in the Hugging Face Dataset repo, while avoiding respondent-name leakage and avoiding noisy/internal build files.

Status: **optimized selection prepared and public-safe full-scope package generated**.

New preferred package for HF upload:

```text
Report_paper_9model/hf_dataset_information_public/
```

This package is generated from the full HF target metadata (`metadata/dataset_metadata.csv`, 104,500 files), uses public labels only, corrects the speaker-gender assignment requested by the project owner, and regenerates the per-speaker figures with public labels.

## Critical finding from cross-check

There are two related but not identical dataset scopes in the repository:

1. **Full HF dataset scope** — `metadata/dataset_metadata.csv`, 104,500 files. This is the current target for HF dataset upload and speaker-label preparation.
2. **Paper-clean statistics scope** — `reports/dataset_statistics_v7_paper9/`, generated from `metadata/dataset_metadata_clean.csv`, 102,544 files. This package is valuable because it contains word distribution, duration/category/speaker statistics, audio uniformity, synthetic disclosure, and Data in Brief-ready figures, but it must be labeled as the **paper-clean/statistics subset** unless regenerated from the 104,500-file HF metadata.

Therefore, do **not** upload the old statistics package blindly as if it described the whole 104,500-file HF dataset. The preferred action has now been completed: generate a new public-safe HF statistics package from the final 104,500-file metadata:

```text
Report_paper_9model/hf_dataset_information_public/
```

The old `reports/dataset_statistics_v7_paper9/` package can still be uploaded only as a clearly labeled paper-clean/statistics subset if needed.

## Recommended HF folder layout

```text
paper/dataset_information/
  README.md
  dataset_information_selection.md
  README.md
  dataset_stats_public.json
  word_frequency_public.csv
  per_category_public.csv
  per_split_public.csv
  per_speaker_public.csv
  synthetic_repair_rows_public.csv
  figures/
    F1_files_per_speaker_split_public.pdf/png
    F3_speaker_total_duration_public.pdf/png
    F7_speaker_category_heatmap_public.pdf/png
  paper_clean_subset_optional/
    word_frequency.csv
    per_category.csv
    statistical_tests.csv
    non-speaker figures, if clearly labeled as paper-clean subset
```

## Optimized include list

### Preferred include: regenerated full-scope public package

Upload these generated files first because they are aligned with the 104,500-file HF target and use public labels only:

| Source | HF target | Why include |
|---|---|---|
| `Report_paper_9model/hf_dataset_information_public/README.md` | `paper/dataset_information/README.md` | Explains full-scope public dataset information package. |
| `Report_paper_9model/hf_dataset_information_public/dataset_stats_public.json` | `paper/dataset_information/dataset_stats_public.json` | Full 104,500-file public summary. |
| `Report_paper_9model/hf_dataset_information_public/word_frequency_public.csv` | `paper/dataset_information/word_frequency_public.csv` | Word distribution from full HF metadata. |
| `Report_paper_9model/hf_dataset_information_public/per_category_public.csv` | `paper/dataset_information/per_category_public.csv` | Category counts/durations from full HF metadata. |
| `Report_paper_9model/hf_dataset_information_public/per_split_public.csv` | `paper/dataset_information/per_split_public.csv` | Split counts/durations with corrected labels. |
| `Report_paper_9model/hf_dataset_information_public/per_speaker_public.csv` | `paper/dataset_information/per_speaker_public.csv` | Public-label speaker/source statistics. |
| `Report_paper_9model/hf_dataset_information_public/synthetic_repair_rows_public.csv` | `paper/dataset_information/synthetic_repair_rows_public.csv` | Per-row synthetic repair disclosure with mismatch flags. |
| `Report_paper_9model/hf_dataset_information_public/figures_public/F1_files_per_speaker_split_public.pdf` | `paper/dataset_information/figures/F1_files_per_speaker_split_public.pdf` | Regenerated per-speaker figure with public labels. |
| `Report_paper_9model/hf_dataset_information_public/figures_public/F3_speaker_total_duration_public.pdf` | `paper/dataset_information/figures/F3_speaker_total_duration_public.pdf` | Regenerated per-speaker duration figure with public labels. |
| `Report_paper_9model/hf_dataset_information_public/figures_public/F7_speaker_category_heatmap_public.pdf` | `paper/dataset_information/figures/F7_speaker_category_heatmap_public.pdf` | Regenerated heatmap with public labels. |


### Include as-is, high value, public-safe

These files are small, directly useful, and do not expose respondent names based on text scan:

| Source | HF target | Why include |
|---|---|---|
| `reports/dataset_statistics_v7_paper9/README.md` | `paper/dataset_information/README_paper_clean_stats.md` | Explains statistics package and reproducibility commands. |
| `reports/dataset_statistics_v7_paper9/stats/word_frequency.csv` | `paper/dataset_information/word_frequency.csv` | Word distribution requested by user; useful for LM/vocabulary analysis. |
| `reports/dataset_statistics_v7_paper9/stats/per_category.csv` | `paper/dataset_information/per_category.csv` | Category balance, durations, and counts. |
| `reports/dataset_statistics_v7_paper9/stats/per_split.csv` | `paper/dataset_information/per_split.csv` | Train/dev/test counts and duration summary. |
| `reports/dataset_statistics_v7_paper9/stats/statistical_tests.csv` | `paper/dataset_information/statistical_tests.csv` | Compact statistical evidence. |
| `reports/dataset_statistics_v7_paper9/synthetic_data_report/synthetic_per_category.csv` | `paper/dataset_information/synthetic_per_category.csv` | Synthetic disclosure by category. |
| `Processed_Balanced19_v3/reports/build_summary.json` | `provenance/processed_balanced19_v3/build_summary.json` | Build counts; no detailed speaker-name paths. |
| `Processed_Balanced19_v3/reports/output_verify.json` | `provenance/processed_balanced19_v3/output_verify.json` | Output verification summary. |
| `Processed_Balanced19_v3/reports/PROCESS_SUMMARY.txt` | `provenance/processed_balanced19_v3/PROCESS_SUMMARY.txt` | Human-readable processing summary. |
| `Processed_Balanced19_v3/reports/PROCESS_REPORT.md` | `provenance/processed_balanced19_v3/PROCESS_REPORT.md` | Processing report for users. |
| `Processed_Balanced19_v3/reports/transcript_map.json` | `provenance/processed_balanced19_v3/transcript_map.json` | Sentence/category transcript map. |

### Include as-is, figures likely public-safe

These figures should be useful for end users and avoid per-speaker name labels:

| Source | HF target | Why include |
|---|---|---|
| `reports/dataset_statistics_v7_paper9/figures/F2_duration_per_category.pdf` | `paper/dataset_information/figures/F2_duration_per_category.pdf` | Category duration distribution. |
| `reports/dataset_statistics_v7_paper9/figures/F4_sentence_length.pdf` | `paper/dataset_information/figures/F4_sentence_length.pdf` | Sentence-length distribution. |
| `reports/dataset_statistics_v7_paper9/figures/F5_word_frequency_pareto.pdf` | `paper/dataset_information/figures/F5_word_frequency_pareto.pdf` | Word-frequency Pareto plot. |
| `reports/dataset_statistics_v7_paper9/figures/F6_heaps_law.pdf` | `paper/dataset_information/figures/F6_heaps_law.pdf` | Vocabulary growth / Heaps' law. |
| `reports/dataset_statistics_v7_paper9/figures/F8_cumulative_hours.pdf` | `paper/dataset_information/figures/F8_cumulative_hours.pdf` | Cumulative hours summary. |
| `reports/dataset_statistics_v7_paper9/figures/F9_audio_uniformity.pdf` | `paper/dataset_information/figures/F9_audio_uniformity.pdf` | Sample-rate/channel/bit-depth uniformity. |
| `reports/dataset_statistics_v7_paper9/figures/F10_synthetic_disclosure.pdf` | `paper/dataset_information/figures/F10_synthetic_disclosure.pdf` | Synthetic fraction disclosure. |
| `reports/dataset_statistics_v7_paper9/figures/F12_audio_quality.pdf` | `paper/dataset_information/figures/F12_audio_quality.pdf` | Audio quality sample distribution. |
| `reports/dataset_statistics_v7_paper9/synthetic_data_report/figures/S1_synth_per_category_voice.pdf` | `paper/dataset_information/figures/S1_synth_per_category_voice.pdf` | Synthetic voice/category breakdown. |
| `reports/dataset_statistics_v7_paper9/synthetic_data_report/figures/S2_synth_fraction_per_category.pdf` | `paper/dataset_information/figures/S2_synth_fraction_per_category.pdf` | Synthetic fraction by category. |
| `reports/dataset_statistics_v7_paper9/synthetic_data_report/figures/S3_synth_split_per_category.pdf` | `paper/dataset_information/figures/S3_synth_split_per_category.pdf` | Synthetic split/category distribution. |
| `reports/dataset_statistics_v7_paper9/synthetic_data_report/figures/S4_synth_quality.pdf` | `paper/dataset_information/figures/S4_synth_quality.pdf` | Synthetic quality distribution. |

## Include only after anonymization/regeneration

These are important but currently contain original respondent names or likely per-speaker labels. They should be regenerated with `M*`, `F*`, `Ms*`, `Fs*` labels before public HF upload:

| Source | Why not upload as-is | Required action |
|---|---|---|
| `reports/dataset_statistics_v7_paper9/stats/dataset_stats.json` | Contains original speaker names in gender/split/synthetic fields. | Create `dataset_stats_public.json` with public labels and 104,500-vs-102,544 scope clearly marked. |
| `reports/dataset_statistics_v7_paper9/stats/per_speaker.csv` | Contains original speaker names. | Create `per_speaker_public.csv` with `M*`/`F*` labels. |
| `reports/dataset_statistics_v7_paper9/stats/audio_quality_sample.csv` | Contains original speaker names and sample paths. | Create public sample CSV with public labels and relative HF paths only. |
| `reports/dataset_statistics_v7_paper9/synthetic_data_report/synthetic_data_stats.json` | Contains original speaker names in by-speaker and zero-synth lists. | Create `synthetic_data_stats_public.json` with `Ms*`/`Fs*` and `repair_target_speaker_id`. |
| `reports/dataset_statistics_v7_paper9/01_DATASET_STATISTICS_REPORT_v7_paper9*.md/pdf` | Markdown scans show original names; PDFs may have embedded per-speaker labels. | Regenerate public report or upload only under private review until anonymized. |
| `reports/dataset_statistics_v7_paper9/figures/F1_files_per_speaker_split.pdf` | Per-speaker figure likely displays original speaker names. | Regenerate with public speaker labels. |
| `reports/dataset_statistics_v7_paper9/figures/F3_speaker_total_duration.pdf` | Per-speaker figure likely displays original speaker names. | Regenerate with public speaker labels. |
| `reports/dataset_statistics_v7_paper9/figures/F7_speaker_category_heatmap.pdf` | Per-speaker heatmap likely displays original speaker names. | Regenerate with public speaker labels. |
| `reports/dataset_statistics_v7_paper9/figures/F11_mel_spectrogram_exemplars.pdf/png` | Needs visual/manual privacy check; exemplar labels may include speaker names or file paths. | Regenerate or manually inspect before upload. |

## Exclude from HF public upload

These are too noisy, internal, or privacy-risky for public users:

| Source | Reason |
|---|---|
| `Processed_Balanced19_v3/reports/build_take_audit.csv` | Contains detailed take paths with original respondent names; internal audit detail. |
| `Processed_Balanced19_v3/reports/dataset_take_audit.csv` | Contains detailed take paths with original respondent names; large/noisy. |
| `Processed_Balanced19_v3/reports/output_take_verify.csv` | Contains detailed take paths with original respondent names; large/noisy. |
| `reports/dataset_duration_20260520_235655/audio_format_anomalies.csv` | Older/draft anomaly file; large and not optimized for final public package. |
| `Whisper_Verification_Sessions/session_*` duplicate statistics folders | Duplicate provenance/session working dirs; prefer curated `reports/dataset_statistics_v7_paper9/`. |
| Build scripts under statistics folders | Useful for internal rebuild, but can be in GitHub; HF users mainly need data, stats, figures, and manifests. |

## Required final checks before HF upload

1. Run text scan against selected public files using respondent-name list from `metadata/dataset_metadata.csv`.
2. Visually inspect or regenerate any figure with per-speaker axes.
3. Ensure the HF dataset card states whether statistics are for the 104,500-file full package or 102,544-file paper-clean subset.
4. Prefer generating a new `paper/dataset_information/README.md` in HF staging that links:
   - `word_frequency.csv`
   - `per_category.csv`
   - `per_split.csv`
   - `speaker_label_gender_list.csv`
   - `synthetic_repair_targets_public.csv`
5. Do not upload original respondent-name files or private crosswalks.
