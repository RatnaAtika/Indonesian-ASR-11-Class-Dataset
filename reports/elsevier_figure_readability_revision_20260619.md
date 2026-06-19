# Elsevier figure readability revision — 2026-06-19

## Request

The previous English-category Elsevier figure revision preserved ScienceDirect/Elsevier resolution metadata, but the rendered labels were visually too small in several data-visualization figures. This pass enlarged figure typography and reviewed all `F1`–`F12` paper-facing figures in:

```text
Whisper_Verification_Sessions/session_20260524_125144_dataset_statistics_viz_elsevier/
```

## Elsevier/Data in Brief guidance applied

The Data in Brief Guide for Authors points to Elsevier artwork guidance. The relevant sizing rule is that artwork lettering should be readable at final printed size, with normal lettering around 7 pt and not below about 6 pt. Oversized raster canvases can be downscaled by production systems, which makes text unreadable; therefore this pass uses approximately full-page-width PNG dimensions at 600 DPI.

## Changes made

- Rewrote `regenerate_figures_elsevier.py` as a Pillow-only renderer so it works in the current environment without the broken matplotlib/NumPy stack.
- Regenerated all public figure PNG/PDF artifacts `F1`–`F12` with enlarged titles, axis labels, ticks, and category/speaker labels.
- Converted dense category x-axis labels in several figures to horizontal-bar layouts where appropriate for readability.
- Reoriented long y-axis titles bottom-to-top so labels no longer extend off the left canvas edge in `F1`, `F5`, `F6`, `F8`, and `F10`.
- Regenerated `F11_mel_spectrogram_exemplars` with the original 4-column/3-row spectrogram style, but with larger English category titles, public speaker IDs only, and simplified readable axes; the overlapping `Hz` label was removed so the `2048` tick does not collide with other text.
- Updated `SUBMISSION_READINESS.md` with the new figure dimensions.
- Extended `tools_audit_elsevier_public_paper_artifacts.py` to catch future oversized physical widths that would shrink labels during publisher scaling and future non-white pixels touching image edges, which indicates possible clipping.

## Final figure dimensions

```text
F1   4500x2800 @ 600 DPI
F2   4500x3000 @ 600 DPI
F3   4500x3300 @ 600 DPI
F4   4500x3300 @ 600 DPI
F5   4500x2800 @ 600 DPI
F6   4500x2800 @ 600 DPI
F7   4500x3400 @ 600 DPI
F8   4500x2800 @ 600 DPI
F9   4500x2300 @ 600 DPI
F10  4500x2700 @ 600 DPI
F11  4470x3000 @ 600 DPI
F12  4500x3500 @ 600 DPI
```

## Verification commands

```bash
python3 Whisper_Verification_Sessions/session_20260524_125144_dataset_statistics_viz_elsevier/regenerate_figures_elsevier.py
python3 tools_audit_elsevier_public_paper_artifacts.py
python3 tools_audit_public_anonymization_artifacts.py
python3 tools_verify_accent_spectrogram_samples.py
```

## Result

- English category labels remain in the paper-facing figures.
- Original respondent names remain excluded from paths, text files, PDF text, and figure labels.
- All PNGs remain below the 10 MB guardrail.
- All public figures now use full-page-width 600 DPI raster dimensions, reducing the risk of unreadable downscaled labels.
- The targeted left-edge clipping issues in `F1`, `F5`, `F6`, `F8`, and `F10` are fixed by vertical y-axis titles.
- The `F11` left-panel `2048` tick no longer overlaps an axis-unit label.
