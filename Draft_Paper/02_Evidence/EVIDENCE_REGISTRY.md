# Authoritative evidence registry

## Scope and access rule

- Release-target corpus: **104,500 files / 134.1762 h**.
- Frozen benchmark subset: **102,544 files / 130.6548 h**.
- Difference: **1,956 rows**; see scope bridge in JSON.
- The release target is not currently public: HF staging is private, the licence is `other`, and no persistent dataset DOI is available.
- Deployment/OOD diagnostics are development evidence only.

## Release-target corpus and private HF staging

- Human recordings: 104,368; synthetic: 132 (0.1263%).
- Human speakers: 20 (12 male, 8 female).
- Canonical balanced sentence slots: 209.
- HF revision: `830a2069416707e3f38c06c507255889513cdf4b`; private: `True`; licence: `other`; persistent DOI available: `False`.
- Remote tar shards in private staging: 11; bytes: 15,623,106,560.

## Nine-model technical validation

- Publication-facing values below are a uniform diagnostic rescore of existing prediction CSVs against one canonical test manifest and one normalizer.
- The historical run-native ranking must not be used: its WER/CER values used non-identical reference normalization and denominators.
- Uniform scoring does not make heterogeneous recipes, pretraining, tokenizers, decoders, or hardware a controlled architecture or efficiency comparison.

| Model | Uniform WER (%) | Uniform CER (%) | Parameters |
|---|---:|---:|---:|
| Bi-LSTM CTC | 4.012 | 1.322 | 32,825,659 |
| Conformer-CTC | 1.194 | 0.432 | 11,048,219 |
| DNN-HMM (hybrid) | 94.903 | 84.494 | 1,448,336 |
| GMM-HMM-DNN (3-stage) | 95.552 | 85.117 | 1,448,336 |
| HMM-GMM (classical) | 95.966 | 72.020 | 511,005 |
| Vanilla Transformer | 4.369 | 3.270 | 4,212,688 |
| ViT-modified-ID | 1.761 | 1.298 | 4,353,248 |
| Wav2Letter-style CNN-CTC | 8.884 | 5.154 | 24,840,900 |
| Whisper-small FT | 0.186 | 0.140 | 241,734,912 |

## Material gaps

- [MATERIAL GAP] Final dataset DOI or another persistent archive DOI is not available.
- [MATERIAL GAP] HF repository is private; Data in Brief accessibility must be resolved before submission.
- [MATERIAL GAP] Dataset licence is recorded only as 'other'; exact reuse terms require author/legal confirmation.
- [MATERIAL GAP] Ethics committee name, approval/reference number, and approval date are unverified.
- [MATERIAL GAP] Written consent scope for public release of identifiable voice biometrics is unverified.
- [MATERIAL GAP] Participant age range conflicts across old drafts and has no authoritative public-safe source.
- [MATERIAL GAP] The claim that every speaker completed every canonical sentence slot exactly 25 times requires primary protocol evidence; report the 209-slot balanced design and preserve replacement provenance separately.
- [MATERIAL GAP] Regional-origin/dialect claims require a consent/privacy decision and a verified public-safe table.
- [MATERIAL GAP] Recording-room dimensions conflict between narrative text and embedded diagrams.
- [MATERIAL GAP] Microphone model, acquisition distance, Audacity version, and room protocol require author confirmation against primary records.
- [MATERIAL GAP] Corresponding-author email, CRediT roles, funding statement, and competing-interest confirmation require author approval.
- [MATERIAL GAP] Two synthetic female-voice recordings target a male public speaker label; authors must decide whether to regenerate, exclude, or retain them with an explicit mismatch flag.
- [MATERIAL GAP] Prior-publication overlap with the related 2026 article and third-party redistribution rights require verification.
- [MATERIAL GAP] A whole-package release leakage audit and lifecycle governance record are not yet available.
- [MATERIAL GAP] The transcript-repair algorithm, immutable repair manifest, and audio-text validation audit are not yet publication-attached.
- [MATERIAL GAP] The exact benchmark template-overlap audit and the 297-file sampling design must be attached before final sign-off.
