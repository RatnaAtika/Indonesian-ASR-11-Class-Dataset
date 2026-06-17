# HF Public Metadata Schema for M/F and Ms/Fs Speaker Labels

This schema should be used when rewriting metadata for Hugging Face upload.

| Field | Meaning | Example |
|---|---|---|
| `speaker_id` | Final public acoustic row label. Human audio uses `M*`/`F*`; synthetic repair audio uses `Ms*`/`Fs*`. | `M1`, `F1`, `Ms1`, `Fs1` |
| `speaker_type` | Acoustic source type. | `human`, `synthetic` |
| `speaker_gender` | Gender label retained for stratified analysis and documented in `speaker_label_gender_list.csv`. | `Male`, `Female` |
| `is_synthetic` | Whether this row is synthetic repair audio. | `False`, `True` |
| `synthetic_voice_id` | Synthetic public row label; blank for human rows. | `Ms1`, `Fs1` |
| `repair_target_speaker_id` | Public human target repaired by this synthetic item; blank for human rows. | `M2`, `F4` |

## Per-row rule

- Human row: `speaker_id=M*` or `F*`, `speaker_type=human`, `synthetic_voice_id=`, `repair_target_speaker_id=`.
- Synthetic row: `speaker_id=Ms*` or `Fs*`, `speaker_type=synthetic`, `synthetic_voice_id=Ms*` or `Fs*`, `repair_target_speaker_id=M*` or `F*`.

The `repair_target_speaker_id` keeps the anonymized human slot provenance for each synthetic repair item without exposing original respondent names.
