# Consolidated Gap Analysis

**Target venue:** Elsevier *Data in Brief*  
**Evidence snapshot:** 2026-07-22  
**Inputs:** the six independent reviews in this directory plus [`Draft_Paper/02_Evidence/EVIDENCE_REGISTRY.md`](../../02_Evidence/EVIDENCE_REGISTRY.md) and `evidence_registry.json`

## Executive verdict

**Submission: NO-GO. Public audio release: NO-GO. Internal evidence-led revision: GO.**

All six reviews agree that NSS-ID is potentially suitable for a *Data in Brief* article, but the current manuscript should not be submitted and the private Hugging Face repository should not be made public. The required work is a major evidence-led rebuild, not copyediting.

The principal stop-ship issues are:

1. unverified ethics determination and consent for public release and reuse of identifiable voice recordings;
2. private repository, absent persistent dataset DOI, and undefined dataset licence;
3. conflation of the 104,500-row release target with the 102,544-row frozen benchmark;
4. incomplete release governance, privacy minimization, and package-wide leakage verification;
5. unresolved treatment of two synthetic female-voice recordings mapped to a male repair target;
6. incomplete collection, transcript, quality-control, split, and benchmark methods;
7. an incomplete manuscript with unsupported generalization claims and missing declarations.

No editorial revision can close author-, institution-, or rights-holder-owned gaps. Those fields must remain explicit `[MATERIAL GAP]` items until primary evidence is supplied.

## Mandatory scope guardrail

| Concept | Publication-safe description now | Prohibited inference |
|---|---|---|
| Release-target corpus | A **104,500-row / 134.1762-h HF metadata and release target**, comprising 104,368 human recordings and 132 synthetic recordings (0.1263%). It contains 20 retained human public speaker labels and 213 distinct `(category, sentence_id)` pairs across 11 categories; primary recruitment records are still required to verify participant uniqueness. | Do not call it public, open, or DOI-citable while access remains private. Do not call the 213 pairs globally unique transcript texts without a text-deduplication audit. |
| Accessibility state | HF revision `830a2069416707e3f38c06c507255889513cdf4b` is private; the card licence is `other`; no final persistent dataset DOI is available. | Public-safe labels or a path containing `public` do not establish public accessibility or lawful reuse. |
| Frozen benchmark | A distinct **102,544-row / 130.6548-h** subset with 71,792 train, 15,376 development, and 15,376 test items and 209 category–sentence pairs. The test set contains 15,374 human recordings and 2 synthetic repairs. | Do not present benchmark results as validation of every release-target row. Do not describe all test items as human held-out-speaker utterances. |
| Benchmark interpretation | Human speaker IDs are separated across partitions, but scripts are seen across splits. The current registry records that all development/test references occur in training and 206 test templates are represented in training; the underlying overlap audit must be attached before final sign-off. | Do not infer unseen-text, open-vocabulary, dialect, gender, population, field, or conversational generalization. |
| Acoustic diagnostics | Diagnostics cover **297 sampled files** and measure dynamic range, silence ratio, and spectral centroid. | Do not describe them as a corpus-wide acoustic audit. Use “stratified” only after the sampling frame, allocation, and seed are attached. |

## Consolidated gap register

### P0 — stop-ship and upstream decisions

| ID | Gap | Why it blocks | Evidence required to close | Owner |
|---|---|---|---|---|
| P0.1 | Ethics determination and public voice-release consent | Raw voice is biometric and pseudonymous labels do not anonymize it. The committee decision/reference/date and consent scope are unverified. | Primary approval, exemption, or waiver record; exact committee, reference, and date; retained consent or another documented lawful basis covering the intended audio, metadata, access mode, redistribution, derivative research, and model training as applicable. If unavailable, obtain institutional/journal guidance and do not imply permission. | Authors + institution/ethics office |
| P0.2 | Access, persistent identifier, licence, and redistribution rights | HF is private, the licence is `other`, and DOI/URL fields are placeholders. A data article needs reviewer-accessible, citable data and defined reuse terms. | Rights review for audio, prompts/text, transcripts/metadata, code, and Edge-TTS outputs; approved component-specific licences; frozen archive; persistent DOI; checksums; tested non-privileged access; matching dataset citation. P0.1 must pass before public activation. | Authors + institution/legal + repository owner |
| P0.3 | Privacy minimization and release governance | Fine-grained demographics plus stable IDs and raw voice raise re-identification risk. Withdrawal, retention, takedown, versioning, controller/contact, and maintenance policies are absent. Prior cleanup did not OCR image pixels. | Approved public schema and demographic-minimization decision; label provenance; controller/contact; crosswalk controls; withdrawal/retention/takedown/versioning policy; responsible-use statement; whole-package audit covering filenames, metadata, archives, images/OCR, document properties, PDF layers, notebooks/logs, audio tags, and embedded paths. | Authors + institution/data controller |
| P0.4 | Single source of truth and scope freeze | The manuscript mixes 104,500/213 with 102,544/209 and incorrectly claims universal 25-fold repetition. Older files contain stale gender and model-name fields. | Versioned scope bridge; row manifests for both scopes; repaired-row manifest; attached 213-pair inventory; preserved numbering gaps; source-priority/blacklist table; immutable hashes; scope-qualified claim matrix. | Data curator + corresponding author |
| P0.5 | Synthetic mismatch and benchmark treatment | Two female-source synthetic files target male label M8; synthetic audio also occurs in development/test, and TTS voices may recur across partitions. | Author decision to regenerate, exclude, or retain with explicit row-level mismatch flags; pinned provider/voice/version/date/configuration; QC; refreshed manifests/statistics; human-only and at least synthetic-test-excluded sensitivity results. | Data curator + benchmark lead |
| P0.6 | Prior-publication eligibility | A related 2026 article is cited, but raw-data and result overlap has not been mapped. Substantial prior publication could make the data article ineligible. | Verified citation/DOI; itemized overlap and release chronology; documented eligibility decision; clear separation between the data article and any model paper. | Corresponding author + journal/editor if needed |

### P1 — scientific validity and reproducibility

| ID | Gap | Required revision/evidence |
|---|---|---|
| P1.1 | Collection protocol and participant facts | Reconstruct recruitment, inclusion/exclusion, collection dates, session structure, prompt presentation/order, repetition/replacement logic, instructions, calibration/gain, operator role, segmentation, naming, re-record/rejection rules, and missing-file handling from primary records. Resolve or omit age, room dimensions, microphone, distance, Audacity version, and regional claims. Never harmonize conflicting facts by guesswork. |
| P1.2 | Transcript construction, normalization, repair, and validation | Publish the reconstruction algorithm/script, join keys, source inventory, normalization rules, repaired-row manifest, hashes/revisions, automated checks, and an audio–text audit with sampling design and observed results. Until then, remove “validated transcription” and state only that normalized reference transcripts are supplied. |
| P1.3 | Split generation and design limitations | Attach the split generator, candidate speaker order, seed, library/version, exact manifests, and validation. Report human speaker/source-gender/synthetic counts by split and attach the text-overlap audit. State that the benchmark is seen-script held-out-human-label evaluation with only three human public labels in test and no natural female-label development/test recording source; do not upgrade labels to verified distinct participants. |
| P1.4 | Nine-model protocol and metric interpretation | A post-draft audit found that historical run-native WER/CER used two reference normalizations/denominator sets (136,211 words/960,674 characters for seven recipes versus 135,911/942,599 for Conformer and Bi-LSTM), so the historical ranking is not publication-comparable. A corrective uniform diagnostic rescore of all existing prediction CSVs now uses `splits/test_clean.tsv`, `nssid_project_uniform_v1`, 135,911 words, and 942,599 characters; use only those values in publication-facing tables. Still provide per-model preprocessing, tokenizer, architecture, initialization/pretraining, augmentation, optimization, checkpoint selection, seed, software, decoder, and evaluation provenance; add error analysis and dependence-aware uncertainty if available. Uniform scoring does not make the recipes a controlled architecture or efficiency comparison. |
| P1.5 | Direct evidence audits and immutable provenance | Archive a hashed evidence manifest, 213-pair inventory, full release-target audio-header audit, template-overlap report, transcript-repair audit, and the 297-file sample manifest/selection code. Explicitly blacklist stale demographic/model fields. |
| P1.6 | Demographic, dialect, representativeness, and intended-use claims | Describe controlled closed-prompt Indonesian read speech from the observed sample. Remove claims of national/dialect representativeness, conversational or everyday-language coverage, gender fairness, bias reduction, real-world robustness, and field accuracy. Add privacy-aware intended-use boundaries and misuse warnings. |
| P1.7 | Complete scientific rebuild | Rewrite the paper in English around data construction, description, quality, access, reuse, and limitations. Insert a scope bridge before technical validation. Keep the nine-model comparison compact and subordinate, move details to supplement, or remove it if protocol gaps cannot be closed. |

### P2 — submission-package completeness

| ID | Gap | Required output |
|---|---|---|
| P2.1 | Reusable data description | Repository inventory, data dictionary, category and split tables, synthetic provenance/filtering guidance, checksums, and source data for every figure/table. |
| P2.2 | Author-owned declarations | Verified corresponding author/contact, CRediT roles, funding/sponsor role, competing interests, acknowledgements, ethics/consent, all-author approval, exclusivity, and author-attested GenAI-use determination. Do not infer any declaration. |
| P2.3 | References and identifiers | Verified related article, dataset citation, journal-fit literature, methods/software/model references, DOI, licence, revision, and access date. Every citation must support its adjacent claim. |
| P2.4 | Final assets and journal checks | Editable DOCX, separate artwork, editable tables, captions, supplements, permissions, current journal checklist, clean-session link tests, DOCX re-extraction, metadata sanitization, and final quantitative/privacy/citation audit. |

### P3 — final editorial normalization

1. Use **0.1263%**, not 0.129%; **714 normalized word types**, not 711; and **Whisper-small FT**, not Whisper-medium.
2. Say “the corpus contains” rather than implying all 104,500 files were human-recorded.
3. Use “pseudonymous public speaker ID” and “speaker-independent ASR evaluation,” not anonymous/anonymized identity language.
4. Finalize a precise read-speech title, fact-checked abstract, 1–7 English keywords, and 3–5 Value-of-the-Data bullets.
5. Repair unfinished sentences, table/figure numbering, source-data references, captions, decimal separators, units, author punctuation, and language consistency only after data and evidence are frozen.

## Preserved material-gap ledger

None of the following is closed by manuscript drafting:

- [MATERIAL GAP] Final dataset DOI or another persistent archive DOI is not available.
- [MATERIAL GAP] HF repository is private; *Data in Brief* accessibility remains unresolved.
- [MATERIAL GAP] Dataset licence is recorded only as `other`; exact reuse terms require author/legal confirmation.
- [MATERIAL GAP] Ethics committee name, approval/reference number, and approval date are unverified.
- [MATERIAL GAP] Written consent scope for public release of identifiable voice biometrics is unverified.
- [MATERIAL GAP] Participant age range conflicts across old drafts and has no authoritative public-safe source.
- [MATERIAL GAP] Four categories contain paired low-count replacement IDs; the universal 25-repetitions statement is false as written.
- [MATERIAL GAP] Regional-origin/dialect claims require a consent/privacy decision and a verified public-safe source.
- [MATERIAL GAP] Recording-room dimensions conflict between narrative text and embedded diagrams.
- [MATERIAL GAP] Microphone model, acquisition distance, Audacity version, and room protocol require primary-record confirmation.
- [MATERIAL GAP] Corresponding-author details, CRediT roles, funding, and competing interests require author approval.
- [MATERIAL GAP] The two female-voice/male-target synthetic recordings require an author-owned disposition.
- [MATERIAL GAP] Prior-publication overlap and third-party redistribution rights require verification.
- [MATERIAL GAP] A whole-package release leakage audit and lifecycle governance record are not yet available.

## Work that may proceed now

- draft a complete English **internal working manuscript** with visible `[MATERIAL GAP]` markers;
- build scope-qualified tables and claim–evidence mappings;
- attach direct row-level/header-level audits and immutable hashes;
- reconstruct methods from existing primary records;
- prepare public-safe figures without activating the repository;
- verify references and journal requirements;
- prepare a DOCX clearly marked **NOT FOR SUBMISSION** until all stop-ship gates pass.

## Work that must not proceed now

- making the audio repository public;
- claiming public/open availability, a DOI, or a licence not yet approved;
- asserting ethics approval, exemption, or consent scope;
- submitting the manuscript or preparing a cover letter that implies readiness;
- using deployment/OOD recordings as corpus accuracy;
- adding demographic, dialect, field, gender, unseen-text, or population-generalization claims;
- treating cross-hardware timing as controlled efficiency evidence;
- exposing or searching for the private speaker-name crosswalk.

## Consensus conclusion

The project has a defensible data-article path only if ethical releasability, rights, privacy governance, scope integrity, and reproducibility are resolved with primary evidence. Until then, the correct deliverable is an internally auditable working package—not a public release or submission-ready article.
