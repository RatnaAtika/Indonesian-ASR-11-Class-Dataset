# HF Speaker Anonymization Preparation Report

Status: **prepared for private-first HF upload**.

## Policy

The HF dataset package should not expose respondent names in public metadata, folder names, file paths, or dataset-card examples. Respondents will be represented only by gender-coded IDs:

- Male IDs: `M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11`
- Female IDs: `F1, F2, F3, F4, F5, F6, F7, F8, F9`

The private original-name to anonymized-ID crosswalk is intentionally **not committed** and must not be uploaded to Hugging Face. If a crosswalk is required for internal auditing, generate it locally with:

```bash
python3 tools_prepare_hf_anonymization.py --private-crosswalk
```

The private file path is ignored by Git:

```text
Report_paper_9model/hf_anonymization_private/speaker_crosswalk_PRIVATE_DO_NOT_UPLOAD.csv
```

## Public inventory summary

- Public speaker IDs: 20
- Male IDs: 11
- Female IDs: 9
- Total files represented: 104,500
- Total duration represented: 134.1762 h
- Split speaker counts: train=14, dev=3, test=3

## Generated public files

- `Report_paper_9model/hf_anonymization/speaker_id_public_inventory.csv`
- `Report_paper_9model/hf_anonymization/speaker_id_public_inventory.json`
- `Report_paper_9model/hf_anonymization/speaker_anonymization_preparation_report.md`

## Required HF staging rewrite

When building the HF staging folder, rewrite these fields/paths from original respondent names to anonymized IDs:

1. `speaker_id` -> `anonymized_speaker_id` only.
2. Keep `speaker_gender` as `Male`/`Female` if approved by consent/ethics review.
3. `audio_path`: replace the speaker directory and take-id prefix with the anonymized ID.
4. `audio_path_abs`: do not publish local absolute paths; replace with relative HF paths.
5. `take_id`: replace original-name prefix with anonymized ID.
6. Audio folder paths under `data/processed_balanced19_v3/Dataset_Balanced19/<category>/<speaker>/...` must use `M*`/`F*` folders only.
7. Dataset card examples should use only anonymized IDs.

## Hard rule

Do not upload or commit any file containing the original respondent-name crosswalk once the anonymized HF package is prepared.
