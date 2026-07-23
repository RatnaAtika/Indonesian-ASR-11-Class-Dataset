# Data-integrity review

## Review

- **Correct (observed):** The registry's main full-corpus aggregates are exact projections of the supplied public aggregate artifacts. `file_count=104500`, `human_recordings=104368`, `synthetic_recordings=132`, `duration_hours=134.1762`, and `word_types=714` at [`Draft_Paper/02_Evidence/evidence_registry.json:83-87,142`](../02_Evidence/evidence_registry.json#L83-L87) match [`Report_paper_9model/hf_dataset_information_public/dataset_stats_public.json:6-12`](../../Report_paper_9model/hf_dataset_information_public/dataset_stats_public.json#L6-L12). The registry's split, category, and synthetic-detail blocks also match their source CSV/JSON files exactly.
- **Correct (observed):** The corrected public human-speaker distribution is 20 humans, 12 male and 8 female: the eight `F*` human rows and twelve `M*` human rows are visible at [`Report_paper_9model/hf_dataset_information_public/per_speaker_public.csv:2-9,19-30`](../../Report_paper_9model/hf_dataset_information_public/per_speaker_public.csv#L2-L9). Their file counts sum to 104,368. The 18 synthetic labels (9 female, 9 male) sum to 132 files (`per_speaker_public.csv:10-18,31-39`). Registry fields at `evidence_registry.json:88-96` and claim C004 at `claim_evidence_matrix.csv:5` are correct for the corrected public metadata.
- **Correct (observed):** Public split rows sum to 104,500 files, and raw split seconds sum to 483,034.4982 s = 134.1762495 h, which rounds to 134.1762 h (`per_split_public.csv:2-4`). The apparent sum 134.1763 from the three already-rounded `duration_hours` cells is only a rounding artifact; 134.1762 is the publication-safe total.
- **Correct (observed):** All nine registry model rows are exact projections of `benchmark.json` for ID, rank, WER, CER, training time, inference time, parameters, and hardware. In particular, the evaluated model is **Whisper-small FT**, not medium (`benchmark.json:19-44,2089-2106`), and the proposed ViT model is rank 3 (`benchmark.json:61-72`). Claims C011-C012 use sensible four-decimal metric reporting (`claim_evidence_matrix.csv:13-14`).
- **Correct (observed):** Full-versus-benchmark scope is numerically separated: 104,500/134.1762 h for the release-target metadata and 102,544/130.6548 h for the frozen benchmark (`evidence_registry.json:83-87,533-537`; `dataset_stats.json:30-36`). The 1,956-row difference is consistent, including per-split deltas of 1,358 train, 299 dev, and 299 test.
- **Blocker (high, observed):** The phrase **“Full public corpus”** in C001-C006 (`claim_evidence_matrix.csv:2-8`) is publication-unsafe while the same registry records the HF repository as private and the DOI absent (`evidence_registry.json:448-452,724-727`; C015 at `claim_evidence_matrix.csv:17`). This is a terminology/accessibility contradiction. Until access is actually verified, use “104,500-row release-target corpus/HF metadata snapshot,” not “public corpus,” and do not claim public availability.
- **Blocker (high, observed):** C010 says all 15,376 test items are “held-out-speaker utterances” (`claim_evidence_matrix.csv:12`), but the benchmark test split includes 2 synthetic files (`evidence_registry.json:537-543`; `dataset_stats.json:141-147`), and the public synthetic table identifies those as female synthetic voice `Fs7` targeting male label `M8` (`per_speaker_public.csv:16`; `synthetic_data_stats_public.json:10-13,28`). The nine-model evaluation does cover 15,376 test items (`benchmark.json:2098-2106`, and all nine model `test_set.n_samples` values are 15,376), but only 15,374 are human recordings. Calling every item a held-out-speaker utterance overstates the human-recording scope.
- **Note (medium, observed):** The registry nests `blank_transcripts: 1956` under a scope described as “repaired public metadata” (`evidence_registry.json:10-15`) while separately recording zero blanks after HF repair (`evidence_registry.json:469-470`) and explaining the bridge at lines 678-681. The explanation makes the numbers reconcilable, but the field placement invites a direct contradiction in downstream prose. Rename/scope it as the **local pre-repair metadata snapshot**; reserve zero blanks for the repaired HF revision.
- **Note (medium, observed):** Two supplied aggregate artifacts contain stale demographic fields. `splits/split_summary.json:57-68` and benchmark `dataset_stats.json:57-88,141-151` encode the old 11-male/9-female assignment (including one female test speaker), whereas corrected public labels are 12 male/8 female and all three human test labels are male (`per_speaker_public.csv:19-30`; public gender-correction note at `dataset_stats_public.json:5`). The registry correctly uses corrected counts for the full release and avoids benchmark gender claims, but it should explicitly blacklist the old gender fields so they are not reused.
- **Note (medium, observed):** `dataset_stats.json:14-23` has a stale pipeline label “m02b Whisper-medium FT.” The authoritative benchmark says the present paper model is `m02b-whisper-small-ft`, while medium is a missing secondary model (`benchmark.json:19-44,2350-2358`). The registry is correct; publications must use `benchmark.json`, not the model list in `dataset_stats.json`.
- **Note (medium, observed):** C005 changes the auditable concept from **distinct `(category, sentence_id)` pairs** (`evidence_registry.json:31`) to “templates” (`claim_evidence_matrix.csv:6`; `evidence_registry.json:99`). The supplied targeted aggregates do not contain the full-corpus count 213; only the benchmark artifact supplies 209 “base sentences” (`dataset_stats.json:30-37`). Publication-safe wording is “213 distinct category–sentence-ID pairs in the release-target metadata,” conditional on attaching the row-level inventory that produced it. Do not imply 213 globally unique transcript texts without a text-deduplication audit.
- **Note (medium, observed):** C006’s full-corpus audio-format claim (`claim_evidence_matrix.csv:8`) is not attested by any supplied full-public aggregate. The only targeted artifact with 16 kHz/mono/16-bit counts covers the 102,544-row benchmark subset (`dataset_stats.json:46-55`). The registry asserts 104,500 rows at `evidence_registry.json:74-80`, but the targeted public stats file has no audio-format fields (`dataset_stats_public.json:1-14`). Keep C006 “pending direct full-corpus format audit” unless the cited row-level metadata fields or a complete header scan are packaged.
- **Note (medium, observed):** C013 and the registry’s “100% … / 206 unique test templates” statement (`claim_evidence_matrix.csv:15`; `evidence_registry.json:539-541`) are not supported by any of the targeted benchmark/statistics artifacts: the exact overlap statement appears only in the registry among the files audited. Speaker-separated split membership is supported (`dataset_stats.json:103-153`), but seen-script overlap needs its cited template-overlap audit attached and should be stated separately.
- **Note (low, observed):** C014’s `n=297` is supported (`dataset_stats_public.json:12`), but “stratified” is not established by that artifact. The registry correctly warns that it is not a corpus-wide scan (`evidence_registry.json:696-704`); the sampling frame and stratum counts remain necessary for the stronger adjective.
- **Note (low, inferred):** C007-C008 may be valid from their named remote/revision evidence, but they cannot be independently re-attested from the targeted artifacts in this audit. Their status should remain revision-pinned, especially because the HF repository is private.
- **Note (low, observed):** Raw WER/CER floats with 15-18 decimal places in `evidence_registry.json:549-572` exactly preserve machine output, but that precision should not appear in manuscript prose. C011-C012’s four decimal places are publication-safe. Likewise, use the raw-second-derived 134.1762 h total rather than summing rounded split hours.
- **Hypothesis:** None. No conclusion above depends on guessing at uninspected audio or large dataset folders.

## Publication-safe correction table

| Severity | Current field/claim | Publication-safe correction | Basis |
|---|---|---|---|
| High | C001-C006: “Full public corpus …” | “The 104,500-row release-target corpus/HF metadata snapshot …” until repository accessibility and persistent identifier are verified. | Registry says HF is private and DOI absent (`evidence_registry.json:448-452,724-727`). |
| High | C010: “Nine models were tested on 15,376 held-out-speaker utterances.” | “Nine models were evaluated on the 15,376-item speaker-separated test split, comprising 15,374 human recordings and 2 synthetic repair recordings.” | `dataset_stats.json:141-147`; `per_speaker_public.csv:16`; all benchmark models report 15,376 samples. |
| Medium | `local_source_validation.blank_transcripts=1956` under repaired-public scope | Rename to `local_pre_repair_snapshot.blank_transcripts=1956`; separately report `repaired_hf_revision.blank_transcripts=0`. | `evidence_registry.json:10-15,469-470,678-681`. |
| Medium | C004 / demographic reuse without source priority | Keep “20 retained human public speaker labels: corrected label counts 12 male, 8 female; participant uniqueness/provenance unverified”; explicitly mark gender fields in `split_summary.json` and `dataset_stats.json` stale/pre-correction. | Corrected `per_speaker_public.csv:2-9,19-30` conflicts with `dataset_stats.json:57-88`. |
| Medium | Any “Whisper-medium” paper-model label from dataset stats | “m02b Whisper-small FT”; treat medium as missing/non-paper secondary model. | `dataset_stats.json:14-23` versus `benchmark.json:19-44,2350-2358`. |
| Medium | C005: “213 … templates” | “213 distinct `(category, sentence_id)` pairs in the 104,500-row release-target metadata,” with the row-level inventory cited; avoid “unique texts.” | Count is asserted at `evidence_registry.json:31,99` but absent from targeted full aggregates. |
| Medium | C006: all 104,500 files are 16 kHz/mono/PCM16, status `verified` | Mark “verification pending for full corpus” unless a complete 104,500-row format inventory or audio-header audit is archived; the benchmark-only statement may remain verified for 102,544 files. | Only `dataset_stats.json:46-55` supplies targeted format counts. |
| Medium | C013: held-out speakers reading seen scripts | Split into: (1) “speaker-separated train/dev/test partitions” (supported); (2) exact template overlap, conditional on attaching the overlap audit. | `dataset_stats.json:103-153`; exact 100%/206 statement lacks targeted support. |
| Low | C014: “stratified n=297” | “Audio-quality diagnostics were computed for 297 sampled rows”; add “stratified” only with sampling-frame/stratum evidence. | `dataset_stats_public.json:12` supports only sample size. |
| Low | Raw model metrics at full float precision | Preserve raw floats in machine registry; report WER/CER to four decimals (or 0.85%/0.19% for Whisper, with declared rounding) in prose/tables. | Raw `benchmark.json:22-23,64-65`; rounded C011-C012. |

## Residual risks

1. **Observed:** This was an aggregate-artifact audit, not a row-level transcript, template, or audio-header audit. Therefore the full 213-pair count, zero-blank remote revision, and full 104,500-file format assertion were not independently recomputed.
2. **Observed:** No immutable hashes are recorded in the registry for the evidence files. Several artifacts have different generation dates and known corrected/stale fields, so future regeneration could silently change provenance.
3. **Observed:** The private HF state and absent DOI remain publication blockers independent of the numeric consistency of the local artifacts.
4. **Observed:** Two synthetic test recordings have a voice/repair-target gender mismatch. Their inclusion is numerically disclosed, but publication text must not describe them as human held-out-speaker recordings.
5. **Inferred:** If demographic analyses are later added for the benchmark, they require regeneration from corrected public labels; old benchmark statistics cannot safely supply those results.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Concrete severity-tagged findings cite registry/matrix and authoritative artifact paths with line numbers; the correction table and residual-risks section provide publication-safe resolutions."
    }
  ],
  "changedFiles": [
    "Draft_Paper/03_Review/02_data_integrity_review.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "wc -l on the ten targeted artifacts; targeted git status",
      "result": "passed",
      "summary": "Confirmed bounded artifact sizes and avoided recursive dataset scans."
    },
    {
      "command": "Python JSON/CSV projection and arithmetic checks",
      "result": "passed",
      "summary": "All files parsed; registry public aggregate blocks and nine-model ranking exactly matched source projections; raw durations and speaker/synthetic totals reconciled."
    },
    {
      "command": "Targeted nl/grep inspection of registry, matrix, public stats, split stats, and benchmark",
      "result": "passed",
      "summary": "Established line-level evidence for scope leakage, stale gender/model fields, synthetic test inclusion, and unsupported targeted claims."
    }
  ],
  "validationOutput": [
    "Public totals: 104,500 files; 104,368 human; 132 synthetic; 483,034.4982 s = 134.1762495 h (134.1762 h rounded).",
    "Corrected public humans: 20 labels = 12 male + 8 female; synthetic labels: 18 = 9 male + 9 female.",
    "Benchmark: all nine model records use a 15,376-item test set; registry model projection exactly equals benchmark ranking fields.",
    "Full-minus-benchmark rows: 1,956, split as 1,358 train + 299 dev + 299 test."
  ],
  "residualRisks": [
    "Full-corpus format, 213 category-sentence-ID pairs, remote zero blanks, and sampling stratification were not independently recomputed from row/audio-level evidence.",
    "Private HF access and absent DOI remain publication blockers.",
    "Known stale gender and model-name fields remain in older authoritative-looking aggregate artifacts."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added only the required review artifact; no project source or evidence files were modified.",
  "reviewFindings": [
    "blocker: Draft_Paper/02_Evidence/claim_evidence_matrix.csv:2-8 - 'public corpus' conflicts with private HF/no DOI state.",
    "blocker: Draft_Paper/02_Evidence/claim_evidence_matrix.csv:12 - 15,376 test items include two synthetic files, so not all are held-out-speaker utterances.",
    "medium: Draft_Paper/02_Evidence/evidence_registry.json:10-15 - pre-repair 1,956 blanks are nested under repaired-public scope.",
    "medium: reports/dataset_statistics_v7_paper9/stats/dataset_stats.json:57-88 - demographic fields are stale relative to corrected public labels.",
    "medium: reports/dataset_statistics_v7_paper9/stats/dataset_stats.json:14-23 - model list incorrectly says Whisper-medium; benchmark confirms Whisper-small.",
    "medium: Draft_Paper/02_Evidence/claim_evidence_matrix.csv:6,8,15 - 213 templates, full-corpus audio format, and exact text overlap lack support in the targeted aggregate set."
  ],
  "manualNotes": "Read-only audit was bounded to the requested files; no large dataset directories were traversed."
}
```
