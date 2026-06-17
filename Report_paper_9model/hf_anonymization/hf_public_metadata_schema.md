# HF Public Metadata Schema for Anonymized Speaker IDs

This schema should be used when rewriting metadata for Hugging Face upload.

| Field | Meaning | Example |
|---|---|---|
| `speaker_id` | Final acoustic speaker/source ID. Human audio uses `M*`/`F*`; synthetic audio uses `MS*`/`FS*`. | `M1`, `F3`, `MS1`, `FS1` |
| `speaker_type` | Acoustic source type. | `human`, `synthetic` |
| `speaker_gender` | Gender category retained for stratified analysis if consent permits. | `Male`, `Female` |
| `is_synthetic` | Whether this row is synthetic repair audio. | `False`, `True` |
| `synthetic_voice_id` | Synthetic acoustic source ID; blank for human rows. | `MS1`, `FS1` |
| `repair_target_speaker_id` | Anonymized human slot repaired by this synthetic item; blank for human rows. | `M2`, `F4` |

## Per-row rule

- Human row: `speaker_id=M*/F*`, `speaker_type=human`, `synthetic_voice_id=`, `repair_target_speaker_id=`.
- Synthetic row: `speaker_id=MS1/FS1`, `speaker_type=synthetic`, `synthetic_voice_id=MS1/FS1`, `repair_target_speaker_id=M*/F*`.

This prevents users from mistaking synthetic repair audio for the original respondent's voice while still preserving the balancing/provenance target.
