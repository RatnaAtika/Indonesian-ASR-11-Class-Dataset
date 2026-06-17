# HF Public Metadata Schema for Short Speaker Labels

This schema should be used when rewriting metadata for Hugging Face upload.

| Field | Meaning | Example |
|---|---|---|
| `speaker_id` | Final public acoustic row label. Human audio uses a short two-letter respondent code; synthetic repair audio uses the target code plus `-s`. | `At`, `Ai`, `Ai-s` |
| `speaker_type` | Acoustic source type. | `human`, `synthetic` |
| `speaker_gender` | Gender label retained for stratified analysis and documented in `speaker_label_gender_list.csv`. | `Male`, `Female` |
| `is_synthetic` | Whether this row is synthetic repair audio. | `False`, `True` |
| `synthetic_voice_id` | Synthetic public row label; blank for human rows. | `Ai-s` |
| `repair_target_speaker_id` | Public human target repaired by this synthetic item; blank for human rows. | `Ai` |

## Per-row rule

- Human row: `speaker_id=<two-letter code>`, `speaker_type=human`, `synthetic_voice_id=`, `repair_target_speaker_id=`.
- Synthetic row: `speaker_id=<target-code>-s`, `speaker_type=synthetic`, `synthetic_voice_id=<target-code>-s`, `repair_target_speaker_id=<target-code>`.

This prevents users from mistaking synthetic repair audio for a real respondent recording while still preserving which public respondent slot the synthetic item repairs.
