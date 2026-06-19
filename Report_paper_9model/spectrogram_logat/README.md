# Spectrogram logat / accent samples

This folder contains paper-ready spectrogram assets for one matched declarative utterance spoken by nine respondents.

- Sentence: **Saya membutuhkan rekomendasi tempat wisata di kota Palembang**
- Category: `Kalimat_Deklaratif`
- Source type: original/non-synthetic WAV from `Dataset_Ori`
- Generation tool: `tools_generate_accent_spectrogram_samples.py` using SoX spectrogram + ReportLab PDF generation

## Where to start

1. Read `reports/accent_spectrogram_report.md` or `.pdf`.
2. Use `figures/combined/accent_spectrogram_grid.png` for a 3x3 paper figure.
3. Use `captions/sciencedirect_figure_caption.md` for the ScienceDirect-style caption.
4. Use `tables/accent_spectrogram_samples.csv` for metadata/provenance.

## Caveat

These figures are qualitative samples for paper illustration. They are not, by themselves, a statistical proof of regional accent separability.
## Privacy/anonymization note

All respondent labels in this package use public Hugging Face speaker IDs (`M*`/`F*`). Original respondent names and source-name crosswalks are intentionally excluded from the public paper artifact.
