# Adversarial Data in Brief Review — NSS-ID

## Inherited decisions

- Treat the 104,500-row released dataset and 102,544-row frozen benchmark as distinct scopes.
- Frame benchmarking only as technical validation, not the article’s novelty.
- Disclose transcript repairs, synthetic files, numbering gaps, split composition, and sampled-diagnostic limits.
- Do not invent ethics, consent, licence, DOI, funding, or demographic facts.
- Do not expose private speaker identities.
- The intended article is an evidence-led dataset paper, not a model-development paper ([`Draft_Paper/99_Admin/BMAD_SUPERPOWERS_WORKFLOW.md:14-23`](../99_Admin/BMAD_SUPERPOWERS_WORKFLOW.md#L14-L23)).

## Rejection simulation

**Recommendation: Reject in present form; reconsider only after fundamental data-access, ethics, and corpus-definition problems are resolved.**

The manuscript does not yet establish that its central research object is publicly reusable, ethically releasable, or consistently described. The claimed repository remains private, no persistent dataset DOI is available, and the licence is recorded only as “other,” while the manuscript contains repository placeholders ([`Draft_Paper/01_Extraction/manuscript_text.md:31`](../01_Extraction/manuscript_text.md#L31); [`Draft_Paper/02_Evidence/evidence_registry.json:449-452,724-729`](../02_Evidence/evidence_registry.json#L449-L452)). For a *Data in Brief* article, this defeats the primary purpose of publication.

Consent for public release of identifiable voice recordings and ethics approval or exemption are unverified. Voice pseudonyms do not anonymize the biometric signal. If appropriate consent was not originally obtained and cannot be renewed, this is not repairable through better wording.

The corpus is also materially mischaracterized. It is a controlled, closed-prompt read-speech collection from only 20 adults, with intended prompts repeated 25 times—not broadly representative Indonesian speech. The released inventory has 213 category–sentence pairs, whereas the frozen benchmark has 209; 1,956 rows excluded from benchmarking were subsequently repaired in public metadata (`evidence_registry.json:679-681`). The manuscript nevertheless presents a single 209-sentence story and claims every speaker read every sentence exactly 25 times (`manuscript_text.md:56`). It does not explain the scope bridge.

The extraordinarily low WER values are not evidence of general Indonesian ASR performance. The split is speaker-disjoint but not text-disjoint: every development/test row uses a transcript represented in training, covering 206 test templates (`evidence_registry.json:538-543`). This is closed-template speaker generalization. Moreover, development has zero female-source files and test has only 2 of 15,675, alongside 2 synthetic test files; the split is effectively male-only outside training (`evidence_registry.json:143-171`). Sex composition is therefore confounded with split membership.

The manuscript’s nine-model ranking, especially the “proposed model” framing, shifts the article toward model comparison without documenting sufficient benchmark methods. It also risks overlap with the cited related model paper. In its current form the benchmark both distracts from the dataset and encourages overinterpretation of template-leaked results.

## Diagnosis: concrete findings

### Fatal blockers at submission

1. **Critical — Data are not accessible under defined reuse terms.**  
   `manuscript_text.md:31` contains DOI and URL placeholders; `evidence_registry.json:451-452,725-727` records a private repository, no persistent DOI, and licence “other.” A data article cannot be accepted without reviewer-accessible data, a stable identifier, and an explicit licence.

2. **Critical — Ethics and voice-release consent are unverified.**  
   `evidence_registry.json:728-729` lacks verified ethics review/exemption and written consent covering public release of identifiable voice biometrics. This may be irreparable if participants cannot be re-consented.

3. **Critical as written — The published corpus is not the corpus described.**  
   `manuscript_text.md:56` claims 209 sentences and exact 25-fold repetition; `evidence_registry.json:99,679-681,731` establishes 213 public category–sentence pairs and a separate 209-template benchmark after excluding 1,956 formerly blank-transcript rows. Readers cannot reproduce counts or understand repairs from the current account.

### Major but repairable weaknesses

4. **Major — Benchmark leakage is undisclosed.**  
   The manuscript emphasizes speaker-disjoint splitting (`manuscript_text.md:15,58`) but omits that text templates are not disjoint and all dev/test rows have transcripts seen during training (`evidence_registry.json:540-541`). Near-zero WER must not be framed as open-vocabulary or real-world ASR accuracy.

5. **Major — Split composition undermines generalization claims.**  
   Train contains 41,800 female-source rows, development contains none, and test contains only 2 (`evidence_registry.json:143-171`). Claims about evaluation across male and female speech or general speaker robustness are unsupported.

6. **Major — Representativeness is overstated.**  
   Claims of dialect diversity, everyday-language realism, and real-world utility (`manuscript_text.md:36-40,54,66-70`) are not supported by 20 controlled-booth readers, repeated prompts, and only 714 normalized word types (`evidence_registry.json:142`). Regional origin is not proof of dialect use, and the regional metadata itself awaits a privacy/consent decision (`evidence_registry.json:732`).

7. **Major — Methods and quality control are incomplete.**  
   The methods remain partly Indonesian and end in undeveloped headings (`manuscript_text.md:72-82`). Recruitment, sentence selection, recording sessions, segmentation, transcription validation, normalization, rejection criteria, repair provenance, and synthetic gap-fill criteria are inadequately described. Hardware and room details also await primary-record confirmation (`evidence_registry.json:733-734`).

8. **Major — “Validated transcription” is unsupported.**  
   The abstract makes this claim (`manuscript_text.md:15`), but no validation protocol, annotator count, agreement measure, or audit result is reported. The prior 1,956 blank metadata transcripts make transparent repair provenance essential.

9. **Major — Benchmark scope is absent from the table.**  
   The nine-model table does not say it uses 102,544 rows and a 15,376-item test set rather than the full 104,500-row release. The distinction required by `BMAD_SUPERPOWERS_WORKFLOW.md:19-23` is therefore not implemented.

10. **Moderate — Synthetic files contaminate evaluation and speaker labels.**  
    Two synthetic files occur in test, and two female synthetic-voice recordings target a male public speaker label (`evidence_registry.json:289,722,735`). They should be excluded from evaluation, regenerated, or explicitly flagged and sensitivity-tested.

11. **Moderate — Internal numerical and demographic inconsistencies remain.**  
    The abstract reports 0.129% synthetic rather than the supported 0.1263%; word types are reported as 711 rather than 714; and ages conflict between 25–38 and 22–38 (`manuscript_text.md:15,54,70,78`; `evidence_registry.json:730`). Line 44 also calls all 104,500 files “recorded” despite 132 being synthesized.

12. **Moderate — The draft is editorially incomplete.**  
    Broken sentences and missing artifact references occur at `manuscript_text.md:60,64`; Table 1 is ambiguously reused; Figure labels are inconsistent; and the English manuscript contains an Indonesian methods section.

## Drift / contradiction check

The current draft has not implemented the governing workflow:

- It mixes the full-release and benchmark narratives instead of bridging them.
- It presents unknown DOI, licence, ethics, and consent fields as omissions rather than explicit material gaps.
- It promotes a model ranking despite the decision to keep validation subordinate.
- It quietly changes “regional origin” into demonstrated “dialect variation.”
- It treats speaker-disjointness as sufficient while omitting prompt leakage and severe sex-by-split imbalance.
- It implies full-corpus audio-quality characterization although the registry supports only a stratified sample of 297 files (`evidence_registry.json:437-438`).

## Minimum viable revision strategy

1. **Stop submission until the three fatal gates close:** deposit the exact release in a persistent repository, obtain a DOI, assign explicit reuse terms, and document verified ethics approval/exemption plus consent covering public voice release. Do not release audio until the consent question is settled.

2. **Recast the central story:** describe NSS-ID as a **controlled, closed-prompt Indonesian read-speech corpus for repeated-utterance and unseen-speaker experiments**. Remove claims of national representativeness, natural conversational speech, or demonstrated robot-field performance.

3. **Create one explicit scope-bridge table:**  
   - Public release: 104,500 files, 134.1762 h, 213 category–sentence pairs, repaired metadata.  
   - Frozen benchmark: 102,544 files, 130.6548 h, 209 templates.  
   - Difference: 1,956 rows formerly excluded for blank transcript metadata.  
   State that audio shards did not change and publish repair provenance.

4. **Demote the nine-model benchmark:** retain at most a compact technical-validation table in the main article and move full model rankings/methods to supplementary material or the related research article. Label results as closed-template, speaker-disjoint performance. Do not claim open-vocabulary accuracy or compare hardware-dependent speed as a fair ranking.

5. **Disclose leakage and split composition prominently:** report test speakers, transcript overlap, sex/source counts, and synthetic counts by split. Exclude synthetic test items or provide natural-only sensitivity results. Do not claim gender generalization.

6. **Rewrite Methods from primary records:** cover recruitment, consent, prompt design, dialect-status definition, repetition protocol, recording sessions, equipment, segmentation, file naming, transcription/normalization, QC, missing-data repairs, Edge-TTS generation, and manifest generation. Mark unresolved facts as `[MATERIAL GAP]`.

7. **Add a candid limitations section:** 20 speakers, narrow adult age range, controlled booth, repeated prompts, limited vocabulary, no text-disjoint test, geographic convenience sampling, sex-imbalanced evaluation, sampled-only acoustic diagnostics, and synthetic replacements.

8. **Perform a final evidence audit:** reconcile 0.1263%, 714 word types, age range, 209/213 terminology, all figure values, repository paths, and the two synthetic gender mismatches before regenerating the manuscript.

## Risks

- Consent may not permit public biometric release; failure to re-consent could end the publication in its present form.
- A corrected scope bridge may reveal additional metadata/audio inconsistencies.
- Dialect claims may need removal if no linguistically verified labels exist.
- Retaining the benchmark without strong caveats may still be viewed as duplicate or misleading model publication.
- Merely disclosing the current split will not make it suitable for gender-generalization evaluation.

## Need from main agent

No review decision is required. Before revision can proceed to submission, the authors must supply authoritative decisions or records for repository/DOI/licence, ethics and consent, demographic scope, acquisition protocol, and treatment of the two synthetic gender-mismatch files.

## Suggested execution prompt

No executor handoff is warranted for this read-only review. Revision should begin only after the author-owned fatal blockers are resolved.