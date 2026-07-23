# Benchmark scoring comparability audit

**Status:** internal evidence artifact; **NOT FOR SUBMISSION**  
**Scope:** existing predictions for the frozen 102,544-file benchmark; test set `n=15,376`  
**Uniform normalizer:** `nssid_project_uniform_v1`

## Finding

**Observed:** The historical run-native WER/CER values did not use one reference normalization or one denominator across all nine recipes. Consequently, the historical run-native ranking is not publication-comparable and must not be used in Supplementary Table S6 or adjacent claims.

- Native references for 7 recipe(s) used **136,211 words / 960,674 characters**: DNN-HMM (hybrid); GMM-HMM-DNN (3-stage); HMM-GMM (classical); Vanilla Transformer; ViT-modified-ID; Wav2Letter-style CNN-CTC; Whisper-small FT.
- Native references for 2 recipe(s) used **135,911 words / 942,599 characters**: Bi-LSTM CTC; Conformer-CTC.

The discrepancy arises because Conformer-CTC and Bi-LSTM CTC stored references after the project NFKC/lowercase/punctuation-removal rule, while the other seven prediction files stored strip/lowercase references. All files contain the same 15,376 canonical test items and normalize to the same canonical references under the corrective rule.

## Corrective protocol

1. Canonical reference manifest: `splits/test_clean.tsv` (`SHA-256 a4a423582a60c40d19627cbd93eed01adda0bd07cbd4b4cee8a392d86c7dd429`).
2. Normalization: Unicode NFKC; lowercase; replace non-[a-z whitespace apostrophe] with spaces; collapse whitespace; strip.
3. Shared denominators: **135,911 words / 942,599 characters**.
4. Each prediction row is matched by canonical index and, when populated, relative audio path; every normalized stored label must equal the canonical normalized transcript.
5. WER/CER use summed per-utterance exact Levenshtein edit distance divided by the shared word/character denominator.
6. Existing prediction files are rescored; no model inference is rerun.

## Uniform diagnostic rescore

| Model | WER (%) | CER (%) | Parameters |
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

## Interpretation boundary

Uniform scoring repairs the reference-normalization/denominator defect. It does not make the recipes a controlled architecture, pretraining, tokenizer, decoder, hardware, fairness, speed, or efficiency comparison. The complete nine-row display is Supplementary Table S6 unless every method-card and interpretation gate closes and the display is globally renumbered for main-text promotion. Historical run-native values remain provenance only.

## Reproduction

```bash
python3 Draft_Paper/99_Admin/rescore_nine_model_predictions.py
python3 -m unittest Draft_Paper/99_Admin/test_unified_benchmark_rescore.py
```
