# Elsevier Public Category English Revision — 2026-06-19

## Scope

Revised the public ScienceDirect/Elsevier artifact folder:

```text
Whisper_Verification_Sessions/session_20260524_125144_dataset_statistics_viz_elsevier/
```

Goals:

1. Convert remaining Indonesian category labels such as `Kalimat_Deklaratif`, `Klarifikasi`, `Penjadwalan`, etc. into English category names in paper-facing files.
2. Regenerate category figures, especially `F2_duration_per_category`, so image labels are English.
3. Replace the placeholder/sanitized `F11` panel with an actual spectrogram-style multi-panel figure that matches the original `session_20260524_125144_dataset_statistics_viz/figures/F11_mel_spectrogram_exemplars.png` layout, while keeping public anonymized speaker IDs.
4. Preserve ScienceDirect-style deliverables: PDF figures plus high-resolution PNG fallbacks and a figure manifest.

## English category names used

```text
Declarative
Clarification
Conditional
Confirmation
Negation
Scheduling
Imperative
Persuasive
Rhetorical
Exclamatory
Interrogative
```

## Files/data updated

Updated text/stat files:

```text
01_DATASET_STATISTICS_REPORT_elsevier.md
stats/audio_quality_sample.csv
stats/per_category.csv
stats/word_frequency.csv
tex/G1_category_glossary.tex
tex/T3_per_category.tex
```

Regenerated figures with English labels:

```text
figures/F2_duration_per_category.pdf
figures/F4_sentence_length.pdf
figures/F7_speaker_category_heatmap.pdf
figures/F11_mel_spectrogram_exemplars.pdf
figures/F12_audio_quality.pdf
figures/png600/F2_duration_per_category.png
figures/png600/F4_sentence_length.png
figures/png600/F7_speaker_category_heatmap.png
figures/png600/F11_mel_spectrogram_exemplars.png
figures/png600/F12_audio_quality.png
```

## F11 correction

The previous placeholder anonymization panel was replaced. The new `F11`:

- uses the same 4-column/3-row exemplar layout as the original exploratory F11,
- displays actual spectrogram-style panels from the same sampled audio policy,
- uses English category titles,
- uses public speaker IDs only, e.g. `M10`, `F2`, `M8`, instead of original names,
- keeps a halftone-compatible PNG at approximately 300 DPI, consistent with the original F11 halftone rule.

## Verification

Commands/run checks:

```bash
rg -n "Kalimat_|Deklaratif|Klarifikasi|Kondisional|Konfirmasi|Negasi|Penjadwalan|Perintah|Persuasif|Retoris|Seruan|Tanya" \
  Whisper_Verification_Sessions/session_20260524_125144_dataset_statistics_viz_elsevier -g '!*.png' -g '!*.pdf'

python3 tools_audit_elsevier_public_paper_artifacts.py
python3 tools_audit_public_anonymization_artifacts.py
```

Results:

```text
Remaining Indonesian category text hits: none
PDF text category hits: none
Files >10 MB in target: none
```

Image format check:

```text
F2_duration_per_category.png:      6600x3200, ~600 DPI
F4_sentence_length.png:            6600x3300, ~600 DPI
F7_speaker_category_heatmap.png:   6600x4200, ~600 DPI
F11_mel_spectrogram_exemplars.png: 4470x2766, ~300 DPI, 7.9 MB
F12_audio_quality.png:             6600x3300, ~600 DPI
```

The dedicated audit script reported no errors for filenames, text files, PDF text, PNG size, or DPI thresholds.
