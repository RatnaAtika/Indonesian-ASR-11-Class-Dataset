# Accent spectrogram sample report

Generated: 2026-06-16T19:59:54

## Purpose

This package provides one spectrogram sample per selected respondent for a matched Indonesian declarative sentence. The goal is to support qualitative paper discussion of regional-accent variation while keeping sentence content and sentence type constant.

## Matched utterance

- Sentence type: declarative (`Kalimat_Deklaratif`)
- Sentence ID: `1` / file `01.wav`
- Transcript: **Saya membutuhkan rekomendasi tempat wisata di kota Palembang**
- Source: original WAV files under `Dataset_Ori/Kalimat_Deklaratif/<Respondent>/.../01.wav`
- Spectrogram generation: SoX STFT spectrogram, 1800 x 900 px individual panels, Kaiser window, common settings for all speakers.

## Paper-ready outputs

- Combined figure PNG: `Report_paper_9model/spectrogram_logat/figures/combined/accent_spectrogram_grid.png`
- Combined figure PDF: `Report_paper_9model/spectrogram_logat/figures/combined/accent_spectrogram_grid.pdf`
- Individual respondent PNG/PDF: `figures/individual/`
- Sample metadata CSV/JSON/Markdown/LaTeX: `tables/` and `manifest.json`
- ScienceDirect-style caption: `captions/sciencedirect_figure_caption.md` and `.tex`

## Respondent mapping

| No. | Respondent | Region represented | Audio source | Duration (s) | Sample rate |
|---:|---|---|---|---:|---:|
| 1 | Harry | Padang | `Dataset_Ori/Kalimat_Deklaratif/Harry/Harry_Deklaratif_take1/01.wav` | 4.283 | 16000 Hz |
| 2 | Elisa | Medan | `Dataset_Ori/Kalimat_Deklaratif/Elisa/Elisa_Deklaratif_Take1/01.wav` | 7.688 | 16000 Hz |
| 3 | Joni | Jawa | `Dataset_Ori/Kalimat_Deklaratif/Joni/Joni_Deklaratif_take1/01.wav` | 4.105 | 16000 Hz |
| 4 | Amri | Jawa | `Dataset_Ori/Kalimat_Deklaratif/Amri/Amri_Deklaratif_take1/01.wav` | 4.599 | 16000 Hz |
| 5 | Erlin | Bengkulu | `Dataset_Ori/Kalimat_Deklaratif/Erlin/Erlin_Deklaratif_Take1/01.wav` | 4.229 | 16000 Hz |
| 6 | Bey | Maluku | `Dataset_Ori/Kalimat_Deklaratif/Bey/Bey_Deklaratif_Take1/01.wav` | 5.444 | 16000 Hz |
| 7 | Anggi | Palembang | `Dataset_Ori/Kalimat_Deklaratif/Anggi/Anggi_deklaratif_take1/01.wav` | 4.083 | 16000 Hz |
| 8 | Atika | Palembang | `Dataset_Ori/Kalimat_Deklaratif/Atika/Atika_Deklaratif_Take1/01.wav` | 4.613 | 16000 Hz |
| 9 | Fito | Baturaja | `Dataset_Ori/Kalimat_Deklaratif/Fito/Fito_Deklaratif_take1/01.wav` | 4.448 | 16000 Hz |

## Interpretation guidance

- Use these spectrograms as qualitative, illustrative material for a paper figure or appendix.
- The matched sentence controls lexical content, but it does not by itself prove dialect/accent separability.
- Any claim about accent should be phrased cautiously, e.g., 'representative examples of acoustic variation across respondent regions' rather than 'classifier-ready accent proof'.
- For a stronger accent analysis, add multiple sentences per respondent and quantitative features such as F0 contour, formants, duration, energy, and spectral centroid.

## Quality/self-review notes

- All nine selected samples use the same category, same sentence ID, and same transcript.
- All nine samples are original/non-synthetic WAV recordings according to `metadata/dataset_metadata_clean.csv`.
- Individual and combined figures are generated with identical spectrogram settings.
- Figures are suitable as paper/appendix assets; the final manuscript can choose either the 3x3 combined panel or individual respondent panels.
