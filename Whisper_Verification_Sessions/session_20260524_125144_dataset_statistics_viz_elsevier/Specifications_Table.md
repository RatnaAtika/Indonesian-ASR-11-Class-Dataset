# Specifications Table — Indonesian limited-data ASR corpus (retake2026 / v7)

> Mandatory section for *Data in Brief* (ISSN 2352-3409). Do **not**
> rename headings, add rows, or remove rows — Elsevier reproduces this
> as a fixed block in the published article.

| Field                       | Value |
|-----------------------------|-------|
| Subject area                | Computer Science |
| Specific subject area       | Automatic Speech Recognition (ASR); Indonesian limited-data corpus |
| Type of data                | Raw audio (`.wav`, 16 kHz / 16-bit / mono); aligned transcript (`.tsv`, UTF-8); per-speaker / per-category / per-split metadata (`.csv`); SentencePiece tokenizer (`.model`); pre-extracted log-mel features (`.pkl`); statistical-test outputs (`.csv`); summary tables (`.tex`); summary figures (`.pdf` / `.png`); a single machine-readable summary (`dataset_stats.json`). |
| How the data were acquired  | Read-aloud sessions in a treated room. Microphone: Røde NT-USB at 48 kHz / 24-bit; downsampled to 16 kHz / 16-bit using `sox 14.4.2`. Transcripts were hand-corrected from Whisper-large-v3 hypotheses. Synthetic gap-fills (132 files, 0.129 % of the corpus) were generated with Microsoft Edge-TTS and are flagged in the metadata (`is_synthetic = True`, `synthesis_engine = "edge-tts"`). |
| Data format                 | Raw audio (16 kHz / 16-bit / mono WAV) plus filtered/aggregated tabular metadata. |
| Description of data collection | Twenty native-Indonesian speakers (10 female, 10 male), ages 19–28, recorded ten balanced takes covering 11 sentence-type categories (209 base sentences = 19 sentences × 11 categories). Total ≈ 130.65 hours. Speaker-disjoint train (14 speakers, 92.49 h) / dev (3 speakers, 19.74 h) / test (3 speakers, 18.43 h) split with zero leak. |
| Data source location        | Universitas X Speech Lab, Jakarta, Indonesia. Approximate coordinates: 6.20° S, 106.81° E. |
| Data accessibility          | Repository name: **Mendeley Data** <br> Direct URL to data: `https://doi.org/10.17632/PLACEHOLDER.v1` <br> Data identification number: `10.17632/PLACEHOLDER.v1` <br> Instructions for accessing the data: openly accessible, no firewall, no controlled access. |
| Related research article    | W. Dadang *et al.*, *ViT-modified end-to-end ASR for Indonesian limited speech* (manuscript in preparation). **N/A** at time of submission. |

---

**Notes on this template (delete before submission):**

- The repository DOI is currently a **placeholder** (`PLACEHOLDER`).
  Replace with the real Mendeley Data DOI once the dataset is
  formally deposited.
- The Related Research Article field is **N/A** at submission time
  because the methods paper is still in preparation. If a co-submission
  is used, replace **N/A** with the co-submission identifier
  (`Co-submitted with manuscript ID <Editorial-Manager-ID>`).
- Do **not** put any URL behind a firewall, login, or paywall in the
  *Data accessibility* field.
