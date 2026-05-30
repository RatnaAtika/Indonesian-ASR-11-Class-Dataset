# Value of the Data — Indonesian limited-data ASR corpus (v7_natural_synth)

> Mandatory section for *Data in Brief* (ISSN 2352-3409). Three to five
> bullets. Each bullet describes the **utility to others**, not the
> authors' own results. No interpretive claims, no conclusions.

- These data provide a **publicly accessible, format-uniform
  Indonesian-speech corpus** (102,544 WAV files, 130.65 h, 16 kHz /
  16-bit / mono) suitable for fine-tuning, benchmarking, and
  controlled-perturbation experiments on limited-data ASR.

- The corpus enables **fair benchmarking across 20 native speakers**
  (9 F / 11 M) and **11 sentence-type categories** under uniform
  acoustic conditions, addressing a documented gap in reproducible
  Indonesian-speech evaluation.

- The shipped train / dev / test split is **speaker-disjoint with zero
  leak** (14 / 3 / 3 speakers, 71,792 / 15,376 / 15,376 files), so
  downstream researchers can reuse the splits directly without having
  to re-derive a leakage-safe partition; the same frozen splits drive a
  nine-architecture fair-comparison benchmark.

- The synthetic-data fraction is **explicitly disclosed at every level**
  (corpus, split, speaker; total 0.129 %, only 0.013 % of the test
  set, mean Whisper-similarity 0.9941), enabling reuse for studies that
  need to control for TTS-contamination effects.

- A stratified audio-quality sample (n = 297 files, ≈ 27 per category)
  is shipped alongside the raw audio, giving a calibrated baseline for
  acoustic-quality audits and feature-extraction pipelines.
