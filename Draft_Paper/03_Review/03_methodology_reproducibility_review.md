# Methodology and Reproducibility Review

## Review

### Correct

- **The evidence package now supports a clear two-scope account.** It distinguishes the released-target corpus (104,500 rows, 134.1762 h, 213 category–sentence-ID pairs) from the frozen benchmark subset (102,544 rows, 130.6548 h, 209 pairs) and explains that 1,956 rows with blank transcripts in the earlier local snapshot were excluded from the benchmark ([`Draft_Paper/02_Evidence/evidence_registry.json:10-16,83-99,480-501,678-681`](../02_Evidence/evidence_registry.json#L10-L16)). This distinction is essential but is not yet carried into the manuscript.
- **The principal audio-format and composition totals are internally supported:** 104,368 natural recordings plus 132 synthetic files, all 16-kHz, 16-bit, mono ([`Draft_Paper/02_Evidence/evidence_registry.json:74-87`](../02_Evidence/evidence_registry.json#L74-L87)). The body’s 0.126% synthetic fraction is consistent with the registry.
- **The supplied evidence supports speaker-disjoint human partitions and a common frozen test set for the nine models.** The frozen subset has 71,792/15,376/15,376 train/dev/test files, three test speakers, and all nine benchmark entries use the 15,376-file test set ([`Draft_Paper/02_Evidence/evidence_registry.json:533-543`](../02_Evidence/evidence_registry.json#L533-L543); [`Report_paper_9model/benchmark/benchmark.md:1-6,20-32`](../../Report_paper_9model/benchmark/benchmark.md#L1-L6)).
- **The transcript maintenance work is auditable at the operation-count level.** The cleanup report records 1,956 blanks before, 1,956 filled, zero after, no audio-shard changes, and a commit (`reports/hf_transcript_cleanup_execution_20260618.md:3-15,23-41`). The numbering note also correctly preserves original collection IDs and warns users not to renumber gaps (`reports/hf_transcript_numbering_note_20260618.md:39-61`).
- **The Colab result is appropriately characterized in the evidence as an execution smoke test, not an accuracy reproduction.** It used only 256 training and 64 validation examples for one epoch (`reports/colab_cli_m12_vit_modified_1epoch_20260619.md:70-95,97-116`; [`Draft_Paper/02_Evidence/evidence_registry.json:683-690`](../02_Evidence/evidence_registry.json#L683-L690)).

### Blockers / major issues

1. **Major — The manuscript conflates the full released corpus with the frozen benchmark subset.**
   - The draft repeatedly describes the corpus as 209 sentences and says every speaker read every sentence 25 times ([`Draft_Paper/01_Extraction/manuscript_text.md:48,56`](../01_Extraction/manuscript_text.md#L48)), whereas the repaired full corpus has 213 category–sentence-ID pairs and several partial replacement pairs; only the frozen benchmark has 209 pairs ([`Draft_Paper/02_Evidence/evidence_registry.json:31-72,99-140,480-523`](../02_Evidence/evidence_registry.json#L31-L72)). The evidence registry explicitly says the “every speaker … exactly 25 times” claim must be revised ([`Draft_Paper/02_Evidence/evidence_registry.json:731`](../02_Evidence/evidence_registry.json#L731)).
   - The benchmark table is presented without saying that it covers 102,544 rather than 104,500 files ([`Draft_Paper/01_Extraction/manuscript_text.md:84-96`](../01_Extraction/manuscript_text.md#L84-L96)). This makes the results appear to validate the released corpus as currently described.
   - **Required action:** add an explicit scope bridge before any benchmark results and use scope-qualified counts everywhere.

2. **Major — The collection protocol is not reproducible, and several asserted acquisition facts remain unverified or contradictory.**
   - The draft gives microphone/software/distance and room construction ([`Draft_Paper/01_Extraction/manuscript_text.md:29,42,76`](../01_Extraction/manuscript_text.md#L29)) but omits collection dates, session structure, prompt presentation and ordering, whether repetitions were blocked or randomized, speaker instructions defining intonation/tempo/volume conditions, input gain/calibration, monitoring, operator role, segmentation procedure, file naming, restart/re-record rules, rejection criteria, and how the 5–10 cm distance was maintained.
   - The age range is 25–38 in the data description but 22–38 in Methods ([`Draft_Paper/01_Extraction/manuscript_text.md:54,78`](../01_Extraction/manuscript_text.md#L54)). The evidence also says age, room dimensions, microphone, distance, Audacity version, and protocol still require primary-record confirmation ([`Draft_Paper/02_Evidence/evidence_registry.json:730,733-734`](../02_Evidence/evidence_registry.json#L730)).
   - “Controlled variations” are asserted but not operationalized ([`Draft_Paper/01_Extraction/manuscript_text.md:38,48,56`](../01_Extraction/manuscript_text.md#L38)), so they cannot be reproduced or treated as balanced experimental factors.
   - **Required action:** verify against primary records, then supply the missing procedural details. Until then, remove exact unverified claims rather than harmonizing them by guesswork.

3. **Major — “Validated transcription” is unsupported, and the 1,956-row repair is not methodologically documented.**
   - The abstract calls every transcript validated ([`Draft_Paper/01_Extraction/manuscript_text.md:15`](../01_Extraction/manuscript_text.md#L15)), but the supplied cleanup report documents only blank counts and regenerated files; it does not state how text was inferred, which keys were used, how normalization was defined, whether audio was listened to, who checked the repair, or the observed audit error rate (`reports/hf_transcript_cleanup_execution_20260618.md:3-15,17-42`).
   - Because the benchmark excluded exactly those 1,956 formerly blank rows, transcript repair changed the released metadata but did not retroactively change the frozen benchmark ([`Draft_Paper/02_Evidence/evidence_registry.json:678-681`](../02_Evidence/evidence_registry.json#L678-L681)). This provenance must be explicit.
   - Sentence-ID gaps reflect curation/removal and must remain stable (`reports/hf_transcript_numbering_note_20260618.md:41-45`); the manuscript currently gives no construction/curation history.
   - **Required action:** publish the repair algorithm/script, input/output hashes or pinned revisions, normalization rules, repaired-row manifest, and a manual audio–text audit protocol/result. Replace “validated” unless that process can be evidenced.

4. **Major — The split tests unseen human speakers but not unseen text, and gender is completely confounded with the partition.**
   - Every dev/test row uses a transcript represented in training; 206 unique test templates occur in training ([`Draft_Paper/02_Evidence/evidence_registry.json:538-543`](../02_Evidence/evidence_registry.json#L538-L543)). Thus the benchmark is a fixed-prompt, seen-text speaker-generalization test, not open-vocabulary or unseen-utterance ASR.
   - All 41,800 female-source files are in training; development has no female files, and test contains 15,673 male-source plus only two female-source synthetic files ([`Draft_Paper/02_Evidence/evidence_registry.json:143-170`](../02_Evidence/evidence_registry.json#L143-L170)). Consequently there is no natural female evaluation speaker. Claims of robust evaluation across gender, dialect, or real-world language are not supported.
   - A seed alone does not reproduce a split without the candidate speaker order, stratification algorithm/library version, and exact assignment; manifests help reproduce usage but not generation ([`Draft_Paper/01_Extraction/manuscript_text.md:15,48,58`](../01_Extraction/manuscript_text.md#L15)).
   - **Required action:** report exact speaker counts/IDs by split, the generation algorithm and manifests, gender composition, and complete text overlap. Ideally provide a second text-disjoint evaluation and a gender-inclusive held-out set; otherwise sharply limit the claim.

5. **Major — Synthetic gap filling weakens both the speaker-disjoint claim and benchmark purity.**
   - The full corpus includes 122/8/2 synthetic files in train/dev/test ([`Draft_Paper/01_Extraction/manuscript_text.md:60`](../01_Extraction/manuscript_text.md#L60); [`Draft_Paper/02_Evidence/evidence_registry.json:143-170`](../02_Evidence/evidence_registry.json#L143-L170)). The two Edge-TTS acoustic voices can therefore recur across partitions even though target human labels are disjoint. Partition disjointness is strictly supportable only for the 20 retained human public speaker labels—not verified participant identities or TTS voice identities.
   - Two female-voice synthetic files target a male public speaker label ([`Draft_Paper/02_Evidence/evidence_registry.json:289-290,717-736`](../02_Evidence/evidence_registry.json#L289-L290)). The authors must resolve or explicitly flag this mismatch.
   - Synthetic test items should not be included silently in a natural-speech accuracy estimate, even though there are only two.
   - **Required action:** report generator, voice IDs, generation date/API or engine version, parameters, post-processing, selection rule, repair-target mapping, and QC. Publish benchmark metrics with all 132 synthetic files excluded from training/dev/test as a sensitivity analysis, and at minimum recalculate test metrics after removing the two synthetic test files.

6. **Major — Section 4.2 is a placeholder, so the nine-model experiment is not reproducible or fairly interpretable.**
   - The method consists only of “Model konvensional dan deep learning” followed by a ranking ([`Draft_Paper/01_Extraction/manuscript_text.md:80-96`](../01_Extraction/manuscript_text.md#L80-L96)). Missing items include preprocessing/normalization, feature extraction, vocabulary/tokenizer fitting scope, architectures, initialization/pretraining, augmentation, optimizer/schedule, batch size, stopping/checkpoint selection, random seeds, software versions, and evaluation code/version.
   - Whisper is a 241.7M-parameter pretrained model trained for five epochs on an A100, while the proposed 4.35M model was trained for 30 epochs on an unrecorded CUDA device and decoded differently ([`Report_paper_9model/data/paper_9model_interpretation_metrics.json:23-37,47-88`](../../Report_paper_9model/data/paper_9model_interpretation_metrics.json#L23-L37)). The table’s common split/no-LM/greedy condition is useful, but it does not create matched training budgets or isolate architecture effects.
   - The three classical/hybrid systems have WER around 96–97% ([`Report_paper_9model/benchmark/benchmark.md:30-32`](../../Report_paper_9model/benchmark/benchmark.md#L30-L32)), which warrants convergence/tokenization/decoder diagnostics before they are treated as meaningful baselines.
   - **Required action:** add a complete per-model protocol and state that rankings are descriptive outcomes under heterogeneous training and pretraining regimes, not controlled architecture comparisons.

7. **Major — Hardware confounds efficiency claims, and the m12 smoke test cannot fill the provenance gap.**
   - Training and inference were run across A100 and RTX 4060 platforms; exact training hardware for m12 and m11 is absent ([`Report_paper_9model/benchmark/benchmark.md:24-32`](../../Report_paper_9model/benchmark/benchmark.md#L24-L32)). Therefore train time, test wall time, throughput, and GPU memory must not be ranked as model efficiency on a common basis.
   - The L4 run is only a one-epoch 256/64-sample smoke test and produced validation WER 1.0 (`reports/colab_cli_m12_vit_modified_1epoch_20260619.md:70-108`). It proves executability, not reproduction of the reported 1.78% WER or 3:44:58 training time.
   - **Required action:** either benchmark inference on one device with the same batch size/software/warm-up protocol or remove cross-hardware speed comparisons. Label the L4 run separately as a smoke test.

8. **Major — WER/CER interpretation lacks denominators, uncertainty, dependence-aware analysis, and error analysis.**
   - Table values are unlabeled proportions: 0.0085 means 0.85% WER, not 0.0085% ([`Draft_Paper/01_Extraction/manuscript_text.md:86-96`](../01_Extraction/manuscript_text.md#L86-L96)). The draft gives neither normalization/scoring rules nor word/character denominators.
   - Point estimates and relative improvements are reported without confidence intervals ([`Report_paper_9model/data/paper_9model_interpretation_metrics.json:90-94`](../../Report_paper_9model/data/paper_9model_interpretation_metrics.json#L90-L94)). With only three test speakers, 25-like repetitions and repeated text templates, utterances are strongly clustered; a naive 15,376-row iid interval would be overconfident.
   - Required analyses are per-speaker and per-category WER/CER, insertion/deletion/substitution counts, sentence error rate, error examples, performance with synthetic items removed, and paired model differences. With only three speakers, even speaker-level uncertainty will be weak and must be acknowledged.
   - **Required action:** report point estimates as percentages plus numerator/denominator counts; add paired block/hierarchical bootstrap intervals over speaker–template blocks, per-speaker results, and no significance claim where the three-speaker design cannot support one.

9. **Major — Sampled acoustic-quality evidence is too limited to support corpus-wide quality claims.**
   - Only 297 files were assessed, using dynamic range, silence ratio, and spectral centroid ([`Draft_Paper/02_Evidence/evidence_registry.json:696-704`](../02_Evidence/evidence_registry.json#L696-L704)). The sample is described as “paper-clean stratified,” but the supplied materials do not define the sampling frame/seed, allocation, inclusion criteria, thresholds, or whether selection occurred after quality screening.
   - These metrics do not directly establish clipping rate, SNR/noise level, reverberation, transcript correctness, or file integrity. The manuscript’s controlled-room and quality-language should not imply a full-corpus scan.
   - **Required action:** describe this strictly as a stratified diagnostic sample, publish its manifest and selection code, give distributions and threshold failures with uncertainty, and avoid extrapolating to all 104,500 files. Prefer a full automated integrity/clipping scan plus a blinded listening audit.

10. **Blocker — The dataset is not presently accessible under publication-ready reuse terms.**
    - The manuscript still contains DOI/URL placeholders ([`Draft_Paper/01_Extraction/manuscript_text.md:31`](../01_Extraction/manuscript_text.md#L31)). The evidence says the HF repository is private and its license is merely “other” ([`Draft_Paper/02_Evidence/evidence_registry.json:448-452,724-727`](../02_Evidence/evidence_registry.json#L448-L452)). Ethics approval and consent for public release of identifiable voice biometrics are also unverified ([`Draft_Paper/02_Evidence/evidence_registry.json:728-729`](../02_Evidence/evidence_registry.json#L728-L729)).
    - **Required action:** before submission, provide a persistent public archive/version, exact license, checksums, access date, ethics decision/reference, and consent scope appropriate to voice data.

### Minor issues

- **Minor — Numeric inconsistencies:** the abstract reports 0.129% synthetic while the supported value is 0.1263% ([`Draft_Paper/01_Extraction/manuscript_text.md:15`](../01_Extraction/manuscript_text.md#L15); [`Draft_Paper/02_Evidence/evidence_registry.json:83-87`](../02_Evidence/evidence_registry.json#L83-L87)). The manuscript reports 711 word types while the full-public normalization yields 714 ([`Draft_Paper/01_Extraction/manuscript_text.md:70`](../01_Extraction/manuscript_text.md#L70); [`Draft_Paper/02_Evidence/evidence_registry.json:142`](../02_Evidence/evidence_registry.json#L142)). State the tokenizer/normalizer used for any vocabulary count.
- **Minor — “104,500 audio files were recorded from 20 respondents” is false as written** because 132 are synthesized ([`Draft_Paper/01_Extraction/manuscript_text.md:44,52`](../01_Extraction/manuscript_text.md#L44)). Use “the corpus contains” and separately count natural and synthetic files.
- **Minor — Representativeness is overstated.** A controlled read-speech corpus with 20 adults and 213 fixed templates cannot by itself establish “realistic linguistic characteristics,” everyday-language representativeness, dialect robustness, or real-time service-robot performance ([`Draft_Paper/01_Extraction/manuscript_text.md:36-40,68-70`](../01_Extraction/manuscript_text.md#L36-L40)). Recast these as intended use cases or hypotheses.
- **Minor — Descriptive interpretation overreaches.** Longer persuasive prompts may reflect how the prompt set was authored, not an intrinsic property of the communicative category ([`Draft_Paper/01_Extraction/manuscript_text.md:66-68`](../01_Extraction/manuscript_text.md#L66-L68)).
- **Minor — Editorial completeness:** Methods switches language, Figure/Table references and repository paths are incomplete, and Table 2 is actually the model ranking ([`Draft_Paper/01_Extraction/manuscript_text.md:58,64,72-96`](../01_Extraction/manuscript_text.md#L58)). These defects impede review and reproduction.

## Exact manuscript wording recommendations

The following text can be inserted verbatim after authors replace bracketed fields with verified primary-record information.

### 1. Replace the corpus/benchmark scope description

> **Dataset and benchmark scopes.** The released NSS-ID corpus contains 104,500 audio files (134.1762 h): 104,368 natural recordings and 132 explicitly flagged Edge-TTS gap-fill recordings (0.1263%). The repaired publication metadata contains 213 distinct category–sentence-ID pairs. The nine-model experiment used an earlier frozen clean subset of 102,544 files (130.6548 h; 71,792 train, 15,376 development, and 15,376 test), which excluded 1,956 rows whose transcript fields were blank in the local metadata snapshot at benchmark freeze time. That benchmark contains 209 category–sentence-ID pairs. Full-corpus descriptive statistics and benchmark results are therefore reported separately and must not be interchanged.

### 2. Replace “validated transcription” in the abstract

> Each file is paired with a normalized reference transcript and provenance metadata; the transcript construction, normalization, and post-freeze repair procedures are described explicitly below.

Use “validated” only if an evidenced validation protocol and result are added.

### 3. Add a collection-protocol paragraph

> Recordings were collected during [dates] in [verified room dimensions and treatment]. A BOYA BY-MM1+ microphone [confirm model] was connected through [interface] and recorded with Audacity [verified version] on Windows [version] at 16 kHz, 16-bit PCM, mono. Input gain was [setting/calibration procedure], and the mouth-to-microphone distance was maintained at [verified distance and method]. Prompts were presented [method] in [fixed/randomized] order. For each prompt, speakers were instructed to [operational instructions for rate, intonation, and level]. Sessions lasted [duration], with [break schedule]. [Operator/automatic procedure] segmented and named files using [rule]. Recordings were repeated or rejected when [predefined criteria]; [number] files were rerecorded and [number] natural recordings remained missing. These details describe elicited variation and should not be interpreted as independently randomized experimental factors unless the corresponding labels are supplied.

### 4. Add transcript construction and repair provenance

> References were constructed by [verbatim transcription / prompt lookup—select the verified method] and normalized using [published rules for case, punctuation, numerals, abbreviations, and non-speech events]. On 18 June 2026, 1,956 blank transcript cells in the 104,500-row publication metadata were filled by [exact algorithm and join keys] from [source inventory/version]; no audio files were changed. We verified the repair by [automated checks] and by listening to a [sampling design, n] audit sample, for which [result/error count] was observed. The repaired-row manifest, script, checksums, and repository revision are [persistent paths]. The frozen nine-model benchmark was not regenerated and excludes these 1,956 rows.

### 5. Add the numbering note

> Sentence IDs preserve the original 01–20 collection numbering within each category. Gaps are intentional consequences of curation or removal and do not indicate missing uploads. IDs must not be renumbered; the row-level publication metadata and transcript inventory are the sources of truth.

### 6. Replace the split/generalization claim

> Human speakers are disjoint across train, development, and test partitions. The frozen benchmark has [verified speaker counts] speakers in train, [count] in development, and three in test. However, it is not text-template-disjoint: every development and test row uses a reference transcript represented in training, and 206 unique test templates occur in training. The benchmark therefore measures recognition of seen prompts from held-out human speakers, not generalization to unseen sentences or open-vocabulary speech. All natural female-speaker recordings occur in training; development and test contain no natural female speaker. Gender-robustness conclusions cannot be drawn from these partitions.

### 7. Add synthetic-data limitations

> The 132 synthetic gap-fill files were produced with Microsoft Edge-TTS using id-ID-ArdiNeural (73 files) and id-ID-GadisNeural (59 files), without speaker cloning, and are identified by a synthetic-status field. Their split distribution is 122/8/2 for train/development/test. Human speaker IDs are partition-disjoint, but the two TTS voice identities may recur across partitions; accordingly, “speaker-disjoint” refers only to human speakers. Two female-voice files are mapped to a male repair-target label and are [regenerated/excluded/retained with an explicit mismatch flag]. We report a sensitivity analysis excluding synthetic files, including test metrics after removal of the two synthetic test items.

### 8. Add benchmark comparability language

> All nine systems were scored on the same frozen 15,376-file test manifest using normalized references, greedy decoding, and no external language model. The comparison is nevertheless descriptive: systems differ in pretraining, parameter count, tokenizer/decoder, epoch budget, stopping rule, and hardware. The results therefore compare complete training recipes on this seen-text, held-out-speaker benchmark and do not isolate architecture effects. Training time, inference wall time, throughput, and memory are not compared as hardware-normalized efficiency measures.

### 9. Replace the metric-table lead-in

> WER and CER are reported as percentages (errors divided by the total reference word or character count after [normalization]). On the 15,376-file frozen test set, Whisper-small FT achieved 0.852% WER and 0.186% CER, while ViT-modified-ID achieved 1.777% WER and 1.301% CER. Table X also reports word/character denominators, insertion/deletion/substitution counts, sentence error rate, per-speaker and per-category results, and paired [block/hierarchical bootstrap] 95% confidence intervals. Because the test set contains only three speakers and repeated templates, uncertainty and generalization are assessed at speaker–template blocks rather than by treating utterances as independent.

### 10. Add sampled-quality wording

> Acoustic diagnostics were computed for a stratified sample of 297 files, selected using [frame, strata, allocation, seed, and inclusion criteria]. The diagnostics comprised dynamic range, silence ratio, and spectral centroid. These sampled results are descriptive and are not a full-corpus quality scan; they do not by themselves establish SNR, reverberation, clipping, or transcript correctness for all 104,500 files. The sample manifest, code, distributions, and threshold-failure counts are provided at [path].

### 11. Replace accessibility placeholders

> **Data availability.** Version [version] of NSS-ID is publicly archived at [repository and DOI], corresponding to revision [commit/hash], under the [exact license] license. File checksums and split manifests are provided at [paths]. Access was verified on [date]. Ethics review/waiver [committee and reference] and written participant consent covered public distribution and reuse of identifiable voice recordings [state verified scope].

## Residual risks

- Primary collection records may not exist at sufficient detail to verify the age range, room dimensions, hardware, distance, or elicitation protocol.
- The three-speaker, natural-male-only test design cannot support strong population, gender, dialect, or unseen-text generalization even after improved reporting.
- Post hoc transcript repair cannot be considered validated until its reconstruction logic and audio-based audit are available.
- A fair efficiency comparison requires new same-hardware measurements; existing wall times remain provenance records only.
- Public release remains blocked until access, persistent DOI/versioning, license, ethics, and voice-consent terms are resolved.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Review provides severity-ranked findings with line-cited paths, exact replacement wording, and a residual-risk section covering corpus scope, transcripts, synthetic data, splits, benchmark interpretation, hardware, uncertainty, and acoustic sampling."
    }
  ],
  "changedFiles": [
    "Draft_Paper/03_Review/03_methodology_reproducibility_review.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "Targeted read/nl/rg inspection of the seven requested evidence files",
      "result": "passed",
      "summary": "Verified manuscript claims against corpus, repair, benchmark, metric, and smoke-test evidence with line locations."
    },
    {
      "command": "git diff --cached --quiet",
      "result": "passed",
      "summary": "Exit code 0; no staged changes were present."
    }
  ],
  "validationOutput": [
    "Full corpus verified as 104,500 rows/134.1762 h/213 category-sentence pairs; frozen benchmark verified as 102,544 rows/130.6548 h/209 pairs.",
    "Transcript operation report verified 1,956 blanks filled and zero remaining, but no repair algorithm or listening-audit evidence was supplied.",
    "Benchmark verified as speaker-disjoint but not text-template-disjoint, with all development/test references represented in training and only three test speakers.",
    "Acoustic evidence verified as a 297-file sample, not a full-corpus scan."
  ],
  "residualRisks": [
    "Collection facts and participant age remain unverified and internally inconsistent.",
    "Natural female speech is absent from development/test, and test text is fully seen during training.",
    "Synthetic acoustic voices cross partitions and two files have a voice/target-gender mismatch.",
    "No dependence-aware confidence intervals or paired error analysis are available.",
    "Repository access, DOI, exact license, ethics reference, and voice-release consent remain unresolved."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added only the requested read-only review artifact; no manuscript or evidence source was modified.",
  "reviewFindings": [
    "major: Draft_Paper/01_Extraction/manuscript_text.md:48,56,84-96 - full 104,500-row corpus is conflated with the frozen 102,544-row benchmark.",
    "major: Draft_Paper/01_Extraction/manuscript_text.md:54,76-78 - collection protocol is incomplete and age/acquisition details conflict or remain unverified.",
    "major: Draft_Paper/01_Extraction/manuscript_text.md:15 and reports/hf_transcript_cleanup_execution_20260618.md:3-15 - validated-transcript claim is unsupported by a documented repair/validation method.",
    "major: Draft_Paper/02_Evidence/evidence_registry.json:538-543,143-170 - benchmark has complete text-template overlap and no natural female dev/test speech.",
    "major: Draft_Paper/01_Extraction/manuscript_text.md:80-96 - model methods, uncertainty, and error analysis are absent.",
    "blocker: Draft_Paper/01_Extraction/manuscript_text.md:31 and Draft_Paper/02_Evidence/evidence_registry.json:724-729 - persistent access, license, ethics, and consent are unresolved."
  ],
  "manualNotes": "Review was evidence-only. Bracketed replacement text intentionally requires author verification rather than guessing missing primary facts."
}
```
