# Indonesian 11-Class ASR Dataset (v7) — Corpus Summary

> Short narrative for the repository README / dataset card. Every number is
> derived from `metadata/dataset_metadata_clean.csv` (the exact file the nine
> paper models train on) and reproducible via `compute_stats.py` in this folder.

## At a glance

This is a balanced, speaker-disjoint **Indonesian read-speech corpus** built for
fair head-to-head ASR benchmarking. It contains **102,544 utterances** totalling
**130.65 hours** of 16 kHz / 16-bit / mono audio from **20 native-Indonesian
speakers**, spanning **11 sentence-type categories** drawn from **209 base
sentences** (19 per category). The corpus is the frozen `v7_natural_synth`
release that drives the 9-model SOTA benchmark in this repository.

## Speakers & gender balance

| | Speakers | Files | Hours |
|---|---:|---:|---:|
| **Male** | 11 | 56,396 (55.0 %) | 70.27 |
| **Female** | 9 | 46,148 (45.0 %) | 60.39 |
| **Total** | **20** | **102,544** | **130.65** |

Per-speaker file balance is near-perfect: every speaker contributes
5,125–5,132 files (0.14 % spread; normalised entropy 0.99999998, Gini 0.0002).

## Categories (11 sentence types)

Each category holds ~9,000–9,500 utterances and is highly balanced
(normalised entropy 0.99987, Gini 0.012):
Deklaratif, Klarifikasi, Kondisional, Konfirmasi, Negasi, Penjadwalan,
Perintah, Persuasif, Retoris, Seruan, Tanya. Mean utterance length tracks
linguistic function — imperatives (*Perintah*) are shortest at 2.96 s, and
persuasives (*Persuasif*) are longest at 6.43 s.

## Splits (speaker-disjoint, zero leakage)

| Split | Utterances | Speakers | Hours | M / F files |
|---|---:|---:|---:|---|
| train | 71,792 | 14 | 92.49 | 30,770 / 41,022 |
| dev | 15,376 | 3 | 19.74 | 15,376 / 0 |
| test | 15,376 | 3 | 18.43 | 10,250 / 5,126 |

Note: the dev split is all-male (Amri, Fajar, Pram); use the mixed-sex **test**
split for any sex-conditional evaluation.

## Vocabulary & word distribution

- **786** unique word types over **908,472** tokens.
- Follows a Zipfian distribution. Most frequent words: *yang* (26.5k),
  *kamu* (24.0k), *apakah* (21.0k), *saya* (19.5k), *jika* (18.0k),
  *di* (14.5k), *untuk* (14.5k), *sudah* (14.5k), *kita* (13.0k), *akan* (12.5k).

## Synthetic data — count & method (fully disclosed)

**132 utterances (0.129 %)** are synthetic gap-fills that replace dropped or
unrecoverable speaker takes. They are flagged in metadata
(`is_synthetic = True`).

- **Engine:** Microsoft **Edge-TTS Neural** (`microsoft_edge_tts_neural`).
- **Voices (gender-matched):** `id-ID-ArdiNeural` (male, 73 files) and
  `id-ID-GadisNeural` (female, 59 files).
- **Pipeline:** TTS → MP3 → `ffmpeg` resample → 16 kHz / mono / PCM-16 WAV
  (bit-identical format to real recordings).
- **Two rounds:** 124 initial + 8 residual-fix = 132.
- **Quality gate:** every synthetic file was transcribed with Whisper-large-v3
  and required text-similarity ≥ 0.70 to the target sentence — all 132 passed
  (mean similarity **0.9941**, min 0.9101).
- **Evaluation integrity:** only **2** synthetic files land in the test split
  (0.013 %), 8 in dev, 122 in train. The TTS voices are *not* speaker-cloned;
  this is disclosed rather than hidden.

## Audio format

100 % uniform: **16 kHz sample rate, 16-bit depth, mono**, no exceptions across
all 102,544 files — front-end variability is removed as a confounder for model
comparison.

## Reproduce these numbers

```bash
python3 Whisper_Verification_Sessions/session_20260530_125618_dataset_stats_v7_paper9/compute_stats.py
# → stats/dataset_stats.json + per_*.csv + 8 Data-in-Brief figures (figures/F1..F8)
```
