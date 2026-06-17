# HF Public Metadata Schema for M/F and Ms/Fs Speaker Labels

| Field | Meaning | Example |
|---|---|---|
| `speaker_id` | Public acoustic row label. Human audio uses `M*`/`F*`; synthetic repair audio uses `Ms*`/`Fs*` according to actual synthetic voice gender. | `M1`, `F1`, `Ms1`, `Fs1` |
| `speaker_type` | Acoustic source type. | `human`, `synthetic` |
| `speaker_gender` | Public acoustic-source gender after correction/inference. | `Male`, `Female` |
| `is_synthetic` | Whether this row is synthetic repair audio. | `False`, `True` |
| `synthetic_voice_id` | Synthetic public row label; blank for human rows. | `Ms1`, `Fs1` |
| `repair_target_speaker_id` | Public human target repaired by this synthetic item; blank for human rows. | `M2`, `F4` |
| `repair_target_speaker_gender` | Corrected gender of the repaired human target. | `Male`, `Female` |
| `voice_gender_matches_target` | Whether synthetic voice gender matches target gender. | `True`, `False` |

Rows with `voice_gender_matches_target=False` must be reviewed before public HF release; they are preserved explicitly rather than hidden.
