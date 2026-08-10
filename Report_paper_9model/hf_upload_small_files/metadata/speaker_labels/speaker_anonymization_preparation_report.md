# HF Speaker Label Preparation Report

Status: **prepared with corrected gender labels and synthetic voice cross-check**.

- Human male labels: `M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, M12`
- Human female labels: `F1, F2, F3, F4, F5, F6, F7, F8`
- Synthetic male labels: `Ms1, Ms2, Ms3, Ms4, Ms5, Ms6, Ms7, Ms8, Ms9`
- Synthetic female labels: `Fs1, Fs2, Fs3, Fs4, Fs5, Fs6, Fs7, Fs8, Fs9`

Corrections and cross-checks:

- Source metadata rows corrected for public label assignment: **5225**.
- Synthetic files whose TTS voice gender does not match the corrected repair-target gender: **2**.
- Such rows are flagged with `voice_gender_matches_target=False` in `synthetic_repair_targets_public.csv`; regenerate or exclude them before public HF release if strict gender-matched synthetic repair data is required.

Public inventory summary:

- Human labels: 20
- Synthetic repair labels: 18
- Human files represented: 104,368
- Synthetic files represented: 132
- Total files represented: 104,500
- Human split speaker counts: train=14, val=3, test=3

Private original-name crosswalks are not committed and must not be uploaded to Hugging Face.
