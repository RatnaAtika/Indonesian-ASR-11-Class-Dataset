# Self-review / critique log for accent spectrogram package

Status: completed after two review passes.

## Review pass 1 — requirement fit

Checklist:

- [x] Exactly one sample per requested respondent: Harry, Elisa, Joni, Amri, Erlin, Bey, Anggi, Atika, Fito.
- [x] Same sentence for all respondents.
- [x] Sentence type is declarative (`Kalimat_Deklaratif`).
- [x] Selected transcript: "Saya membutuhkan rekomendasi tempat wisata di kota Palembang".
- [x] Regional mapping follows the user request: Harry=Padang, Elisa=Medan, Joni/Amri=Jawa, Erlin=Bengkulu, Bey=Maluku, Fito=Baturaja, Atika/Anggi=Palembang.
- [x] Outputs are stored in a dedicated folder: `Report_paper_9model/spectrogram_logat/`.
- [x] Each respondent has an individual spectrogram PNG and PDF.
- [x] A combined 3x3 paper-ready figure is available in PNG and PDF.
- [x] A report is available in Markdown, TXT, and PDF.
- [x] ScienceDirect-style figure caption is provided in Markdown and LaTeX.

Critique:

- The spectrograms are strong as qualitative illustrations, but they should not be framed as proof that each regional accent is separable from one sentence alone.
- The selected sentence is controlled across respondents, which is good for visual comparison, but a robust accent study should include multiple sentences per speaker and quantitative prosodic/acoustic features.

Action taken:

- Added explicit interpretation caveats in `reports/accent_spectrogram_report.md` and the figure caption.
- Kept all source paths and hashes in `manifest.json` and `tables/accent_spectrogram_samples.csv` for auditability.

## Review pass 2 — paper/reproducibility fit

Checklist:

- [x] All source WAV files exist and are original/non-synthetic in metadata.
- [x] All generated PNG files have high enough resolution for paper use.
- [x] All PDFs exist and are non-empty.
- [x] Combined figure exists and is suitable for appendix or paper figure placement.
- [x] Verification script passes: `python3 tools_verify_accent_spectrogram_samples.py`.
- [x] Existing report package checks still pass: `tools_verify_report_readability.py` and `tools_verify_report_model_artifacts.py`.

Critique:

- The current package uses SoX STFT spectrograms, not mel-spectrograms. This is appropriate for a visual acoustic appendix, but if the manuscript specifically needs mel-scale features, a second mel-spectrogram version should be generated with a compatible audio stack.
- PDFs are generated as support artifacts and may be heavier than needed for final submission. For final manuscript upload, the combined PNG/PDF and the caption are likely sufficient.

Action taken:

- Kept both individual and combined figures so the manuscript can choose between a compact 3x3 panel and respondent-level appendix pages.
- Added `tools_generate_accent_spectrogram_samples.py` and `tools_verify_accent_spectrogram_samples.py` so the package can be regenerated and checked reproducibly.
