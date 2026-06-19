# Public Artifact Anonymization Cleanup — 2026-06-19

## Goal

Replace remaining original respondent names with public Hugging Face speaker IDs in public-facing paper artifacts, focusing on:

```text
Report_paper_9model/spectrogram_logat/
Whisper_Verification_Sessions/session_20260524_125144_dataset_statistics_viz_elsevier/
```

Public IDs follow the mapping already used by `Report_paper_9model/hf_anonymization/`:

```text
M1..M12 = human male speakers
F1..F8  = human female speakers
```

## Changes made

### 1. Spectrogram/logat package

Updated:

```text
Report_paper_9model/spectrogram_logat/
```

Actions:

- Regenerated individual spectrogram PNG/PDF files with public IDs in filenames and panel titles.
- Rebuilt the combined 3x3 spectrogram grid using public IDs only.
- Rewrote `manifest.json`, CSV/Markdown/LaTeX sample tables, report Markdown/TXT/PDF, README, and self-review notes to use public IDs.
- Redacted original local source paths in public metadata as `private_original_wav/<speaker_id>/declarative_sentence01.wav`.
- Removed old individual figure filenames that contained respondent names.

Current public spectrogram speaker IDs:

```text
M7, F4, M8, M3, F5, F3, F1, F2, M6
```

### 2. Elsevier dataset-statistics visualization session

Updated:

```text
Whisper_Verification_Sessions/session_20260524_125144_dataset_statistics_viz_elsevier/
```

Actions:

- Replaced original names with public speaker IDs in text/statistical files.
- Updated `stats/per_speaker.csv`, `stats/per_split.csv`, and `stats/audio_quality_sample.csv` to use public IDs.
- Rebuilt/sanitized figures that display speaker labels:
  - `F1_files_per_speaker_split`
  - `F3_speaker_total_duration`
  - `F7_speaker_category_heatmap`
  - `F11_mel_spectrogram_exemplars`
- `F11` was replaced with a sanitized anonymization panel rather than copying the older exploratory raster, because the original source image could contain private respondent labels.
- Updated `figures/figure_manifest.csv`.

## Repeated audit results

Verification commands run:

```bash
python3 tools_verify_accent_spectrogram_samples.py
python3 tools_audit_public_anonymization_artifacts.py
python3 tools_audit_public_anonymization_artifacts.py
python3 - <<'PY'
# Semantic consistency audit for public IDs and redacted source paths
PY
```

Results:

```text
OK: accent spectrogram package verified (9 matched declarative samples, figures, reports, and caveats)
```

Anonymization audit, repeated twice:

```json
{
  "checked": {
    "filenames": 92,
    "text_files": 36,
    "pdf_text": 23
  },
  "errors": [],
  "target_count": 2
}
```

Semantic audit:

```text
semantic_errors: []
spectrogram_ids: ['F1', 'F2', 'F3', 'F4', 'F5', 'M3', 'M6', 'M7', 'M8']
elsevier_speaker_count: 20
```

## Notes and limitations

- The audit checks filenames, text-like files, and extractable PDF text for original respondent-name leakage.
- PNG pixel text is not OCR-scanned, but newly generated PNG/PDF figure titles and labels were produced from public IDs only.
- The original private name ↔ public ID crosswalk remains outside GitHub/HF and is not included in these public artifacts.
