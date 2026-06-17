# HF Speaker Label Preparation Report

Status: **prepared for private-first HF upload**.

## Policy

The HF dataset package should not expose respondent names in public metadata, folder names, file paths, or dataset-card examples.

Use public labels:

- Human male labels: `M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11`
- Human female labels: `F1, F2, F3, F4, F5, F6, F7, F8, F9`
- Synthetic male labels: `Ms1, Ms2, Ms3, Ms4, Ms5, Ms6, Ms7, Ms8, Ms9`
- Synthetic female labels: `Fs1, Fs2, Fs3, Fs4, Fs5, Fs6, Fs7, Fs8, Fs9`

Human labels use `M`/`F` plus alphabetic order number within each gender group. Synthetic repair labels use `Ms`/`Fs` plus alphabetic order number within each synthetic target gender group. Synthetic rows also store `repair_target_speaker_id` so users know which anonymized human slot the synthetic item repairs.

The private original-name to public-label crosswalk is intentionally **not committed** and must not be uploaded to Hugging Face. If a crosswalk is required for internal auditing, generate it locally with:

```bash
python3 tools_prepare_hf_anonymization.py --private-crosswalk
```

The private file path is ignored by Git:

```text
Report_paper_9model/hf_anonymization_private/speaker_crosswalk_PRIVATE_DO_NOT_UPLOAD.csv
```

## Public inventory summary

- Human labels: 20
- Synthetic repair labels: 18
- Human male labels: 11
- Human female labels: 9
- Human files represented: 104,368
- Synthetic files represented: 132
- Total files represented: 104,500
- Total duration represented: 134.1762 h
- Human split speaker counts: train=14, dev=3, test=3

## Generated public files

- `Report_paper_9model/hf_anonymization/speaker_id_public_inventory.csv`
- `Report_paper_9model/hf_anonymization/speaker_id_public_inventory.json`
- `Report_paper_9model/hf_anonymization/speaker_label_gender_list.csv`
- `Report_paper_9model/hf_anonymization/synthetic_repair_targets_public.csv`
- `Report_paper_9model/hf_anonymization/hf_public_metadata_schema.md`
- `Report_paper_9model/hf_anonymization/speaker_anonymization_preparation_report.md`

## Required HF staging rewrite

When building the HF staging folder, rewrite fields/paths from original respondent names to public labels:

1. Human rows: `speaker_id` -> `M*`/`F*`.
2. Synthetic rows: `speaker_id` -> `Ms*`/`Fs*`.
3. Add `speaker_type`: `human` or `synthetic`.
4. Keep `speaker_gender` as `Male`/`Female` and document labels in `speaker_label_gender_list.csv`.
5. Add `synthetic_voice_id`: blank for human rows; `Ms*`/`Fs*` for synthetic rows.
6. Add `repair_target_speaker_id`: blank for human rows; target public human label for synthetic rows.
7. `audio_path`: replace speaker directories and take-id prefixes with the final public `speaker_id`.
8. `audio_path_abs`: do not publish local absolute paths; replace with relative HF paths.
9. Dataset card examples should use only public labels.

## Hard rule

Do not upload or commit any file containing the original respondent-name crosswalk once the HF package is prepared.
