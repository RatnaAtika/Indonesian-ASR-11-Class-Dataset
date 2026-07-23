# INTERNAL WORKING MANUSCRIPT — NOT FOR SUBMISSION

**Target journal:** *Data in Brief*  
**Role of this file:** comprehensive evidence master; the canonical v.19 template-aligned source is [`06_DATA_IN_BRIEF_TEMPLATE_MANUSCRIPT.md`](06_DATA_IN_BRIEF_TEMPLATE_MANUSCRIPT.md)  
**Article status:** evidence-led internal draft; public release and submission are **NO-GO**  
**Quantitative snapshot:** 2026-07-22  
**Control:** values affected by the unresolved two-file synthetic mismatch are current working values, not a final release freeze

# NSS-ID: An Indonesian read-speech dataset spanning 11 communicative sentence categories

**Provisional author line from the source manuscript:** Ratna Atika; Suci Dwijayanti; Bhakti Yudho Suprapto  
**Author control:** `[MATERIAL GAP: final author order and affiliations]`  
**Correspondence:** `[MATERIAL GAP: corresponding author name and current email]`

The provisional names above are retained only to preserve source-manuscript continuity. Author order, affiliation wording, ORCID identifiers, postal details, and the corresponding-author designation require explicit human approval.

## Abstract

NSS-ID is a controlled Indonesian read-speech resource organized into 11 communicative sentence categories. Its current release target contains 104,500 audio files totaling 134.1762 h, comprising 104,368 human recordings and 132 explicitly labelled synthetic repairs (0.1263%). The human-recording inventory uses 20 retained public speaker labels; primary recruitment records are still required to verify participant uniqueness and eligibility. The recording-level inventory contains 213 distinct `(category, sentence_id)` pairs; this count is not asserted to represent 213 globally unique transcript texts. Metadata records the audio as 16-kHz, mono, 16-bit PCM WAV, while a publication-grade direct header audit remains pending. The planned package combines category-level audio shards, reference transcripts, pseudonymous public speaker labels, fixed split manifests, synthetic-source and repair-target fields, descriptive source values, and reproducibility scripts. Original sentence identifiers are retained, including documented intentional gaps and partial replacement pairs, so downstream users can preserve stable joins. A separate, pre-transcript-repair frozen subset of 102,544 files was used for nine-model technical validation and must not be conflated with the release target. Human public speaker identifiers are separated across benchmark partitions, but prompt scripts are represented across training, development, and test data. NSS-ID therefore supports reproducible filtering, controlled repeated-prompt analysis, ASR recipe evaluation, and seen-script held-out-human-speaker recognition. It does not establish performance for unseen text, conversation, open microphones, demographic groups, dialects, field conditions, or service-robot deployment.

**Keywords:** Indonesian; read speech; automatic speech recognition; speech corpus; speaker-independent recognition; synthetic speech

## Specifications Table

The editable source is [`tables/Specifications_Table.csv`](tables/Specifications_Table.csv).

| Item | Working description | Evidence status |
|---|---|---|
| Subject | Computer Science | Working classification; author/journal confirmation required |
| Specific subject area | Automatic speech recognition; Indonesian read-speech data; speech and language processing | Supported by corpus content |
| Type of data | PCM WAV audio; UTF-8 transcripts and metadata; JSON/CSV/TSV manifests; source-value tables; scripts | Final inventory and checksums pending |
| Data format | Raw audio (WAV); TAR archives; tabular/structured metadata (CSV, TSV, JSON); analysed source values (CSV) | Metadata records 16-kHz, mono, 16-bit PCM; full direct header audit pending |
| How data were acquired | Final files are organized under 20 retained human speaker labels and 132 labelled synthetic repairs; the source draft describes prompted read-speech collection | `[MATERIAL GAP: participant recruitment and inclusion/exclusion]`; `[MATERIAL GAP: verified microphone, interface, operating system, and recording software/version]`; `[MATERIAL GAP: microphone distance, gain/calibration, monitoring, and prompt presentation]` |
| Description of data collection | Read-speech prompts were organized into 11 communicative categories and retained stable original sentence identifiers | `[MATERIAL GAP: participant recruitment and inclusion/exclusion]`; `[MATERIAL GAP: recording dates and session protocol]`; `[MATERIAL GAP: repetition, replacement, re-recording, and rejection rules]` |
| Data source location | Sriwijaya State Polytechnic, Palembang, Indonesia (provisional source-manuscript value) | Verified collection location and public-safe geographic granularity remain required |
| Data accessibility | Private Hugging Face staging at revision `830a2069416707e3f38c06c507255889513cdf4b`; licence recorded as `other`; persistent dataset DOI unavailable | `[MATERIAL GAP: repository, exact version, persistent DOI, direct URL, checksums, and access date]`; `[MATERIAL GAP: exact dataset licence or component-specific licences]`; `[MATERIAL GAP: approved controlled-access mechanism, if applicable]` |
| Related research article | R. Atika, S. Dwijayanti, B. Y. Suprapto, *Improving speech-to-text for the Indonesian language using a modified transformer*, 2026; DOI `10.15587/1729-4061.2026.350949` | Bibliographic record verified; `[MATERIAL GAP: related 2026 article citation and data/result overlap assessment]` remains open for eligibility determination |

Self-contained captions, source/scope notes, conditional-use notes, and the split-hour rounding note for all editable tables are provided in [`05_TABLE_CAPTIONS_AND_NOTES.md`](05_TABLE_CAPTIONS_AND_NOTES.md). The machine-readable table values remain in `tables/*.csv`.

# 1. Value of the Data

- The current NSS-ID release target provides 104,500 category-organized Indonesian read-speech recordings with machine-readable human/synthetic provenance.
- Recording-level metadata and fixed manifests enable reproducible filtering and scoped, seen-script held-out-human-speaker ASR experiments without presenting the partition as an unseen-text benchmark.
- Explicit `speaker_type`, `is_synthetic`, source-voice, repair-target, and split fields allow users to identify, retain, or exclude the current 132 synthetic repair recordings.
- Eleven prompted communicative categories and repeated utterances support controlled category-, speaker-, duration-, transcript-, and model-recipe analyses, subject to the population, prompt, split, acoustic, privacy, and access limitations stated below.

# 2. Background

Prior work has evaluated end-to-end automatic speech recognition architectures for Indonesian [1]. Multilingual initiatives such as Common Voice [2] and FLEURS [3] illustrate how recorded speech, transcripts, language coverage, and benchmark design can be packaged for broad research use. They are contextual comparators rather than evidence that NSS-ID has the same population, collection process, consent basis, licence, or generalization scope.

Reusable data require more than file deposition. The FAIR principles emphasize persistent identification, retrievable metadata, provenance, and clear reuse conditions [4], while Datasheets for Datasets provides a structured approach to documenting dataset motivation, composition, collection, preprocessing, uses, and limitations [5]. NSS-ID is organized around these documentation goals, but the current private staging state is not yet FAIR-complete or journal-compliant: the access route, persistent identifier, licence, rights, and ethical releasability remain unresolved.

A published model article used NSS-ID to evaluate a modified Transformer architecture [6]. The publisher record and article are verified, and the earlier paper reports an approximately 80,000-file, 120-h corpus state, a different 80:10:10 split, dataset-derived displays, and a two-model comparison. The current release target and frozen benchmark have different counts and manifests. Nevertheless, exact row-level intersection, figure/result overlap, and *Data in Brief* eligibility remain open. The internal assessment is recorded in [`Draft_Paper/02_Evidence/PRIOR_PUBLICATION_OVERLAP_ASSESSMENT.md`](../02_Evidence/PRIOR_PUBLICATION_OVERLAP_ASSESSMENT.md); the model architecture and its novelty are not contributions of this data article.

The objective of this article is therefore bounded: to document the current data construction and package, distinguish the release target from the frozen benchmark, expose human/synthetic provenance, describe the metadata and split design, report limited quality evidence and technical validation, and state the conditions under which the corpus may or may not be reused. It does not claim that NSS-ID is the first, largest, nationally representative, dialect-validated, conversational, or field-validated Indonesian speech corpus.

# 3. Data description

## 3.1. Package organization and file inventory

The release package is designed around 11 English-category TAR shards rather than 104,500 independent repository uploads. In the pinned private Hugging Face listing, the 11 shards total 15,623,106,560 bytes. Each archive corresponds to one public category and preserves relative WAV paths. The staging repository also contains recording-level metadata, 11 category transcript lists, a sentence-ID inventory, public identifier documentation, split summaries, a synthetic repair manifest, descriptive source values, and public-safe figures. Table 1 distinguishes artifacts already present in private staging from components still required for a final deposit, including immutable row manifests, environment locks, direct audit outputs, and package-wide SHA-256 checksums.

The planned package flow is shown conceptually in Figure 1. The diagram must retain recruitment and consent as an unresolved gate, not as a verified input. Audio collection, segmentation, transcript assignment, quality control, synthetic repair, metadata generation, and packaging are separate provenance steps. A branch from the pre-transcript-repair metadata state leads to the frozen 102,544-file benchmark; it must not be drawn as if that benchmark were regenerated from the repaired release metadata.

**[FIGURE 1 PLACEHOLDER — NOT FOR SUBMISSION]** Construction and package flow. The first node must read “recruitment/consent evidence — material gate,” and the final node must read “private staging — release not authorized.”

## 3.2. Release-target scope and scope bridge

The current release target contains 104,500 files and 134.1762 h of audio. It comprises 104,368 human recordings and 132 synthetic repairs. Twenty human public speaker labels occur in the metadata. Corrected metadata labels comprise 12 male and 8 female labels, but the meaning and source of that field remain unresolved: `[MATERIAL GAP: sex/gender label definition and provenance]`. These counts must not be restated as self-identified demographic characteristics until primary evidence and privacy approval are available.

Table 2 is the mandatory bridge between corpus description and technical validation. The frozen benchmark contains 102,544 files and 130.6548 h, with 71,792 training, 15,376 development, and 15,376 test items. By contrast, the release target uses 73,150, 15,675, and 15,675 files. The release target contains 213 distinct `(category, sentence_id)` pairs, while the benchmark contains 209. Pair counts are stable metadata keys, not claims about global text uniqueness.

The 1,956-row difference arose because those metadata rows had blank transcript fields when the benchmark was frozen. They were excluded from `metadata/dataset_metadata_clean.csv` and the benchmark manifests. The pinned repaired private metadata has zero blank transcript fields and retains all 104,500 rows. The metadata repair did not alter the audio shards, and the benchmark was not regenerated. Accordingly, release-target descriptive values must use 104,500 rows, whereas all nine-model scores must use the 102,544-file frozen scope.

## 3.3. Sentence categories and transcript inventory

The public English category names are Clarification, Conditional, Confirmation, Declarative, Exclamatory, Imperative, Interrogative, Negation, Persuasive, Rhetorical, and Scheduling. Each category contains 9,500 release-target files. Category durations range from 7.8119 h for Imperative to 17.2061 h for Persuasive; their release-target mean durations range from 2.9603 to 6.5202 s. These values are descriptive and do not establish inherent linguistic complexity or real-world frequency. Figure 2 and Table 3 use the same Tier-A source file, `per_category_public.csv`.

**[FIGURE 2 PLACEHOLDER — NOT FOR SUBMISSION]** Release-target hours and mean duration by category, generated only from `per_category_public.csv`. The source-value table must accompany the final artwork.

Original collection identifiers in the range `01`–`20` are retained. Seven categories have 19 available IDs with one documented intentional gap; users must not renumber them. Four categories contain paired partial replacements: Conditional IDs 19/20 have 490/10 rows, Confirmation IDs 05/20 have 483/17 rows, Persuasive IDs 17/20 have 489/11 rows, and Interrogative IDs 17/20 have 494/6 rows. These eight pair counts explain why a universal statement that every speaker read every prompt exactly 25 times is not valid for the current metadata.

The release-target lexical summary records 714 normalized word types. The interpretation of that number depends on `[MATERIAL GAP: transcript source and normalization specification]`. It describes a narrow repeated prompt inventory; it must not be used with Zipf-, Heaps-, or sentence-length plots to claim representative everyday Indonesian.

## 3.4. Split and source composition

The release-target training, development, and test partitions contain 73,150, 15,675, and 15,675 files and 94.9437, 20.2969, and 18.9357 h, respectively. The authoritative total remains 134.1762 h rather than the sum of independently rounded table cells. Human speaker counts are 14, 3, and 3. Synthetic counts are 122, 8, and 2.

Table 4 separates retained public human-label counts from acoustic-source file counts. Training contains six male-label and eight female-label natural recording sources. Development and test each contain three male-label natural recording sources and no natural female-label recording source. Development contains zero female-source files. Test contains two female-source recordings, but both are synthetic files associated with the unresolved female-source/male-target repair pair. The partition is therefore unsuitable for gender-balanced evaluation or claims of gender robustness.

Human public speaker IDs occur in only one partition. This limited sense of speaker separation does not make the benchmark text-disjoint: scripts recur across partitions. It also does not guarantee TTS acoustic-voice separation, because the same provider voices may recur in different partitions.

**[FIGURE 3 PLACEHOLDER — NOT FOR SUBMISSION]** Release-target split/source composition. If Table 4 is sufficient, this figure should be omitted rather than duplicated.

## 3.5. Metadata schema and identifiers

Recording-level metadata is intended to expose the fields needed to locate, filter, and interpret each row: relative audio path, public speaker ID, speaker type, public source-label field, category, original sentence ID, split, transcript, duration, metadata-reported sample rate/channel/bit depth, synthetic flag, synthetic public ID, repair-target public ID, target-label field, and source/target match flag. The final data dictionary must describe field type, allowed values, nullability, units, generation rule, and privacy status.

Human rows use pseudonymous `M1..M12` and `F1..F8` labels. Synthetic rows use `Ms1..Ms9` and `Fs1..Fs9`, with separate repair-target fields. These labels do not remove voice identifiability: voice remains a potentially identifying biometric signal. The private respondent crosswalk is excluded from Git, Hugging Face, and the manuscript package and is not needed for ordinary reuse.

Public-schema decisions remain blocked by `[MATERIAL GAP: demographic minimization and public-schema decision]`. Lifecycle controls remain blocked by `[MATERIAL GAP: data controller/contact, crosswalk retention, withdrawal, takedown, breach, versioning, and maintenance policy]`. Before any release, the entire package—not only CSV text—requires `[MATERIAL GAP: final whole-package identity/leakage audit]`, covering archive paths, document properties, images/OCR, PDF internals, logs, notebooks, audio tags, and embedded local paths.

## 3.6. Synthetic repair subset

The current snapshot contains 132 synthetic repairs, 632.52 s (0.1757 h), or 0.1263% of the 104,500-file release target. The public manifest records 73 male-source and 59 female-source files, with 122/8/2 files in training/development/test. Every category contains at least two synthetic rows; the largest current category count is 29 in Confirmation. Table 5 records the complete aggregate breakdown and the fields by which users can exclude these rows.

Project provenance records the provider voice identifiers `id-ID-ArdiNeural` and `id-ID-GadisNeural` and states that the documented process did not use speaker cloning. Submission wording still requires `[MATERIAL GAP: Edge-TTS version/date/configuration and redistribution-rights review]` and broader `[MATERIAL GAP: prompt-text, audio, metadata, code, and synthetic-output rights clearance]`. Provider terms, output rights, text ownership, processing settings, selection rules, and quality checks must be frozen before release.

Two female-source synthetic test recordings target the male public repair label M8. They are not hidden: `voice_gender_matches_target=False` identifies them. Current values are provisional pending `[MATERIAL GAP: disposition of two female-source/male-target synthetic rows]`. Regeneration, exclusion, or explicit retained-mismatch treatment would require new manifests, statistics, displays, checksums, and any affected benchmark sensitivity analysis.

## 3.7. Reuse guidance and diagnostic artifacts

Users should join data by stable public speaker, category, sentence, take, split, and provenance fields rather than reconstructing identity from filenames. Human-only analyses should filter `is_synthetic=False`; synthetic sensitivity analyses should retain the source-voice, repair-target, and source/target-match fields. Release-target descriptive work must use the 104,500-row metadata state, whereas reproduction of the frozen benchmark must use its 102,544-row manifests. Public examples must use relative paths and approved public IDs only.

The planned package lists a 297-row acoustic-diagnostic table as a deposited derivative, but the procedure and results belong in Sections 4.6, 4.12, and 5.1 rather than in Data Description. The table contains dynamic range, silence ratio, and spectral centroid values and currently includes 27 rows from each category. Its frame and selection process require `[MATERIAL GAP: 297-file sampling frame, allocation, seed, and inclusion criteria]`. It must therefore be described only as covering **297 sampled files**, without a sampling-design adjective.

Spectrogram examples remain supplementary unless their selection rule, public-safe relative paths, permissions, and source values are documented. A main-text sampled-diagnostic figure remains blocked because these metrics do not establish corpus-wide signal-to-noise ratio, clipping, reverberation, parsability, perceptual quality, or audio–transcript correctness.

**[FIGURE 4 BLOCKED — NOT FOR SUBMISSION]** Acoustic diagnostics for 297 sampled files. Move to the supplement if the full sampling provenance is not attached.

# 4. Experimental design, materials and methods

This internal Methods section distinguishes a reconstructable data-production step from a plausible retrospective description. During the targeted audit, each proposed fact was classified as **OBSERVED, INFERRED, CONFLICTED, or MISSING**. `OBSERVED` means that a local artifact directly records a value, operation, or assertion; for acquisition details, an author-draft assertion is not proof that the reported event occurred. `INFERRED` means that code, file structure, or inventories strongly support a reconstruction but no contemporaneous protocol was located. `CONFLICTED` means that local records disagree or refer to different dataset states. `MISSING` means that no adequate evidence was found. The line-cited decisions are retained in [`Draft_Paper/02_Evidence/METHODS_EVIDENCE_MATRIX.csv`](../02_Evidence/METHODS_EVIDENCE_MATRIX.csv), and unresolved author/institution questions are in [`Draft_Paper/02_Evidence/AUTHOR_METHODS_EVIDENCE_QUESTIONNAIRE.md`](../02_Evidence/AUTHOR_METHODS_EVIDENCE_QUESTIONNAIRE.md).

The construction account also separates two scopes. The release target is the repaired 104,500-row inventory used for corpus description and packaging. The frozen benchmark is a pre-repair 102,544-row subset used for existing model predictions and uniform rescoring. Methods and results below identify the applicable scope rather than treating these states as interchangeable.

## 4.1. Ethics, recruitment, participant records, and consent

Artifact-level evidence establishes 20 retained human speaker labels, each contributing 5,225 files in the current release-target metadata. It does not independently establish how people were recruited, whether every label represents a distinct eligible person, what language criterion was used, whether compensation was provided, or why any candidate was excluded. These procedures require `[MATERIAL GAP: participant recruitment and inclusion/exclusion]`.

The source draft contains incompatible age ranges of 25–38 and 22–38 years and lists localities and regional accents without a participant questionnaire, self-report method, dialect assessment, or public-release basis. Age therefore remains `[MATERIAL GAP: participant age or approved omission]`; locality is not used as a proxy for dialect. A later internal correction produces 12 male and 8 female metadata labels, whereas stale frozen/split artifacts report 11/9. The draft consequently reports only corrected metadata-label counts and retains `[MATERIAL GAP: sex/gender label definition and provenance]` rather than claiming self-described demographic characteristics.

Collection and public release of voice require a competent determination and a retained legal/ethical basis. No primary record currently supports approval, exemption, waiver, informed consent, or another lawful basis. Submission and repository activation remain blocked by `[MATERIAL GAP: ethics committee/determination, reference number, and date]` and `[MATERIAL GAP: informed-consent procedure and exact public voice-release/reuse scope]`. The latter must be checked against repository access, redistribution, model training, derivatives, publication, future use, and withdrawal limits. Sensitive source records must remain under institutional control and outside the public package.

## 4.2. Prompt inventory, category organization, and balanced-build transformation

Eleven UTF-8 prompt inventories organize items under Clarification, Conditional, Confirmation, Declarative, Exclamatory, Imperative, Interrogative, Negation, Persuasive, Rhetorical, and Scheduling. The local parser reads only entries matching the `NN|text` convention, retains the numeric identifier and text, treats later `Note` material separately, and derives absent IDs against the original `01`–`20` range. The labels are used as functional organizational categories; no evidence was found for a formally validated discourse-act annotation scheme.

The clearest executable construction record is `process_paper_dataset_sota.py`. Its source audit expects 11 category directories, 20 source speaker labels, 25 take directories per label, and 20 numbered WAV items per take. The corresponding build report records **110,000 source WAV files** across **5,500 take directories**. For balanced V3, one prompt ID per category was absent from the retained `NN|text` inventory. The copy step retained the other 19 IDs, skipped **5,500 omitted files**, normalized output to **two-digit sentence filenames**, and verified exact expected names and counts. The resulting arithmetic was 11 categories × 20 labels × 25 takes × 19 retained IDs = 104,500 files. The report records zero structurally problematic take directories for this operation.

This evidence supports the deterministic file-tree transformation; it does not prove how prompts were authored, presented, spoken, or accepted during collection. Inventory notes attribute removals to duplicate/balancing intent, but the decision owner, date, linguistic criteria, and rights remain unverified. The current repaired release metadata also contains 213 category-ID pairs rather than the balanced inventory's 209 because Conditional, Confirmation, Persuasive, and Interrogative contain partial ID-20 replacement groups. Exact authorship, rights, ordering, intended repetitions, and replacement logic remain linked to `[MATERIAL GAP: repetition, replacement, re-recording, and rejection rules]` and `[MATERIAL GAP: prompt-text, audio, metadata, code, and synthetic-output rights clearance]`.

## 4.3. Recording setting, equipment, and final audio properties

The source author draft reports collection in a dedicated room in the Electrical Engineering Laboratory building at Sriwijaya State Polytechnic. It describes glasswool, egg-crate acoustic foam, carpet, and placement away from external noise. An embedded, undated montage shows a participant position, chair, laptop, microphone, and foam-lined surfaces. This image is near-primary visual evidence for the depicted setup only; it cannot establish which sessions used that setup, hidden wall materials, collection dates, attenuation, reverberation time, or background-noise performance.

Exact dimensions are conflicted. The prose reports 1 × 1 m floor area and 2.5 m height, whereas embedded diagrams show **approximately 1.5037 m × 2.5027 m** and a height near 2.5027 m. The draft does not select one value. Resolution requires `[MATERIAL GAP: verified room dimensions and treatment]`.

The same source draft names a BOYA BY-MM1+ supercardioid microphone, Audacity 3.7.4, Windows 10, and a 5–10 cm mouth-to-microphone distance. The photograph cannot verify the model, polar pattern, software, operating system, gain, interface, or distance. No purchase/asset record, device enumeration, session screenshot, calibration record, or operator checklist was located. A submission account therefore requires `[MATERIAL GAP: verified microphone, interface, operating system, and recording software/version]` and `[MATERIAL GAP: microphone distance, gain/calibration, monitoring, and prompt presentation]`.

Release-target metadata records every row as 16,000 Hz, mono, and 16-bit PCM WAV. These are evidence-backed final-file metadata values, not yet verified acquisition-native settings. No statement is made that the room was certified, soundproof, echo-free, or noise-free. A direct full-corpus decoder/header audit with hashes is required before upgrading the metadata statement to a file-level attestation.

## 4.4. Elicitation sessions, take structure, segmentation, and file naming

The audited source tree strongly implies an acquisition organization of 11 categories × 20 source labels × 25 take directories × 20 numeric items. It does not define a “take,” show whether a take was a session, repetition block, or directory created after collection, or establish that every person successfully read every prompt 25 times. No primary record was found for fixed versus randomized order, screen or paper presentation, operator cues, reading pace, deliberate intonation/rate/volume conditions, fatigue controls, interruptions, session length, breaks, or maximum attempts. These elements remain `[MATERIAL GAP: recording dates and session protocol]` and part of the repetition/re-recording gap.

Likewise, the repository does not establish whether audio was captured one utterance at a time or segmented from longer sessions. Later processing is observable: retained numeric filenames were zero-padded to two digits, category/speaker/take hierarchy was preserved, and the build verifier checked the expected filename set. Capture-time boundaries, silence padding, segmentation software, manual edits, resampling, and the relationship between source names and final relative paths are still author-owned method details. The final procedure must separate original acquisition from later normalization and must report observed re-recording, rejection, replacement, and exclusion counts rather than infer them from balanced output.

## 4.5. Transcript construction, identifier preservation, and normalization

The prompt inventories are the apparent source for reference text because the balanced-build parser associates each retained numeric ID with its `NN|text` entry. This relationship is strongly supported by code and inventory structure but lacks a contemporaneous transcription protocol. Original `01`–`20` identifiers are retained across audio paths, inventories, repair records, and metadata, including intentional gaps; they are not compacted or renumbered. Stable identifiers permit later versions to explain removals and partial replacement pairs without silently changing joins.

A statistics-preparation script lowercases text and extracts tokens using an `[A-Za-zÀ-ÿ0-9]+`-style expression for descriptive vocabulary counts. That implementation supports the reported 714 normalized word types only; it is not a complete reference-transcript policy. The package still requires `[MATERIAL GAP: transcript source and normalization specification]` covering Unicode form, case, punctuation, numerals, abbreviations, whitespace, apostrophes, disfluencies, noise/non-speech events, spelling decisions, and versioning.

No full listening census, double review, adjudication workflow, annotator qualification record, or measured transcript error rate was located. The release therefore supplies *reference transcript fields* but does not claim that all transcripts have been acoustically validated. Any stronger statement depends on an item-level audio–text audit with sampling/census design, criteria, assessors, disagreement handling, and observed errors.

## 4.6. Structural quality control, exclusions, and acoustic checks

The balanced-build script performs useful structural quality control. It audits expected category, source-label, take-directory, and numbered-WAV structure; separates retained from omitted IDs; detects unexpected or missing names; checks zero-padding; and verifies the exact expected output total. The build report records 104,500 copied files, 5,500 skipped by design, and no structurally bad takes. These checks document corpus assembly but do not establish pronunciation correctness, transcript alignment, waveform readability, clipping, signal-to-noise ratio, reverberation, or perceptual quality.

Current release checks reconcile metadata row totals, category totals, human/synthetic counts, split membership, public-ID ranges, transcript presence at the pinned repaired revision, and selected format fields. Publication-grade integrity still requires direct decoding and header checks over the frozen package, duplicate/content-hash analysis, required-field/schema assertions, archive-manifest reconciliation, and immutable checksums. Human quality evidence must state the eligible frame, whether a census or sample was used, assessor training, acceptance criteria, and observed rejection/error counts. The absence of a recorded rejection ledger must not be converted into a claim that no recordings failed.

A derivative table contains dynamic range, silence ratio, and spectral centroid for **297 sampled files**, currently 27 rows per category. No executable selection procedure, eligible frame, seed, or inclusion rule was found. It therefore remains conditional on `[MATERIAL GAP: 297-file sampling frame, allocation, seed, and inclusion criteria]`. These three metrics do not establish corpus-wide SNR, clipping, reverberation, intelligibility, or transcript correctness.

## 4.7. Post-freeze transcript repair and version bridge

At benchmark freeze, 1,956 release-target rows had blank transcript fields and were excluded from `metadata/dataset_metadata_clean.csv` and the clean split manifests. The counts were Conditional 490, Confirmation 483, Persuasive 489, and Interrogative 494. A later metadata-only update populated all **1,956** fields in private Hugging Face staging and reduced the pinned remote blank count to zero. The execution report states that no audio shard was changed; the frozen benchmark was not regenerated.

Available analysis indicates that the repair combined numbered source inventories with current metadata identifiers and metadata-only ID-20 replacement text. However, the executable repair implementation, source-precedence rule, exact join keys, ambiguity handling, immutable repaired-row manifest, and input/output hashes were not found in the audited package. The final method therefore retains `[MATERIAL GAP: transcript-repair algorithm, join keys, manifest hashes, and audio-text audit result]`. Required closure evidence includes the script, environment, source revisions, row-level before/after values, automated assertions, and a designed listening audit. Zero blanks establish field completeness, not audio–text correctness.

## 4.8. Synthetic gap filling and source/target provenance

The release-target metadata marks 132 rows as synthetic and stores engine, provider voice, public synthetic ID, target public ID, generation round, quality field, and source/target-label relationship. Aggregate artifacts record 73 files from `id-ID-ArdiNeural`, 59 from `id-ID-GadisNeural`, and split counts of 122/8/2. Human target labels and synthetic acoustic voices are separate concepts, and provider voices may recur across partitions even when human public IDs do not.

Metadata identifies Microsoft Edge-TTS and the two provider voice IDs. Separately, the source author draft states that speaker cloning was not used, but no immutable generation command or technical log confirms that assertion. Exact package/version/date, account or region if relevant, text input, rate/pitch/volume, output encoding, resampling, post-processing, retry/selection rules, generated-versus-retained counts, and listening/file QC require `[MATERIAL GAP: Edge-TTS version/date/configuration and redistribution-rights review]`. Rights must be evaluated for prompt input, provider output, redistribution, and derivative model training rather than inferred from article or software availability.

Two synthetic test rows use a female provider voice while targeting male public repair label M8. They remain explicitly flagged and require `[MATERIAL GAP: disposition of two female-source/male-target synthetic rows]`. Regeneration, exclusion, or retained-mismatch treatment must occur before the final data freeze and must trigger regeneration of manifests, statistics, displays, checksums, and synthetic-excluded benchmark sensitivity results.

## 4.9. Metadata generation, public identifiers, and privacy controls

The internal recording-level CSV includes relative and absolute paths, category, source speaker label, take and sentence identifiers, transcript, duration, sample rate, channel count, bit depth, sample count, file size, synthetic flag, engine/voice fields, and dataset version. Absolute paths and private source labels are internal evidence only. The public preparation layer maps human rows to `M1..M12` and `F1..F8` and synthetic rows to `Ms1..Ms9` and `Fs1..Fs9`, while retaining separate repair-target and mismatch fields. One internal source-label correction changes the derived male/female composition; its definition and provenance remain unresolved as stated in Section 4.1.

Public identifiers are pseudonymous, not identity-removing. Voice is a potentially identifying biometric signal, and the private crosswalk is not part of Git, Hugging Face, or manuscript artifacts. Public-field retention, aggregation, and suppression require `[MATERIAL GAP: demographic minimization and public-schema decision]`. Crosswalk custody, retention, withdrawal, takedown, breach response, version correction, and maintenance require `[MATERIAL GAP: data controller/contact, crosswalk retention, withdrawal, takedown, breach, versioning, and maintenance policy]`.

The field schema is observable, but the executable builder that measured duration, sample count, and file size for the current metadata state was not located in the targeted audit. The final package should publish the builder, environment, field types, allowed values, units, nullability, source precedence, input hashes, and validation assertions. After freezing, archives, paths, metadata, audio tags, embedded media/OCR, document properties, logs, notebooks, and generated outputs must undergo `[MATERIAL GAP: final whole-package identity/leakage audit]`.

## 4.10. Split construction and leakage characterization

The release-target manifests assign 14 human public speaker labels to training, three to development, and three to test, producing 73,150/15,675/15,675 rows. Exact current assignments and **seed 42** are recorded. Human labels are partition-disjoint. This is an observed property of the manifests, not proof that the split can be regenerated: the executed generator, eligible input ordering, random-number implementation, constraints, and library version are absent. Closure requires `[MATERIAL GAP: split-generation algorithm, candidate order, library/version, and exact assignments]` with source revision, sorted candidates, code/environment, row-level outputs, hashes, and assertions.

Disjointness applies only to human public labels. Prompt scripts recur across partitions, and the two provider TTS voices may recur. A stale split summary also predates the internal sex/gender-label correction; corrected source composition must be regenerated after field provenance is resolved. For the frozen benchmark, exact normalized template intersections and hashes remain `[MATERIAL GAP: exact benchmark template-overlap audit]`. Until that attachment exists, the defensible interpretation is seen-script, held-out-human-speaker recognition rather than unseen-text evaluation.

## 4.11. Descriptive statistics, figures, and release packaging

Release-target tables and Figures 1–3 are generated from the 104,500-row release-target artifacts. Benchmark counts and model scores use the 102,544-row clean metadata/manifests. The 297-row diagnostic is a third, sampled scope. Scripts and captions must name their input scope, revision/hash, aggregation unit, normalizer, and rounding rule. Category and split durations are calculated from unrounded seconds; independently rounded split values sum to 134.1763 h, while the authoritative release-target total is 134.1762 h.

Private staging uses 11 English-category TAR shards to avoid 104,500 independent uploads. Deterministic figure builders emit editable SVG plus 600-dpi PNG and source-value CSV files. Existing Elsevier artwork derived from the frozen clean metadata remains benchmark-scoped and cannot be relabelled as release-target artwork. A final deposit must add environment locks, direct integrity results, source-value mappings, complete relative-path/SHA-256 manifests, component licences, version, persistent identifier, and clean-session access verification. These tasks do not authorize release before ethics, consent, rights, and privacy gates close.

## 4.12. Technical-validation design and scoring

The validation design has three levels: structural assembly checks, the conditional 297-file acoustic diagnostic, and ASR scoring on the frozen benchmark. Procedures are described here; observed outcomes are reported in Section 5. The frozen benchmark contains 71,792/15,376/15,376 train/development/test items. Its test set has 15,374 human recordings and two synthetic repairs. Only three human public labels occur in test, participant uniqueness is unverified, scripts are represented in training, and no natural female-label recording source occurs in development or test. These constraints define technical validation rather than broad generalization.

SentencePiece [7] is used by relevant local recipes, but vocabularies are not interchangeable. The nine complete recipes comprise Whisper-small fine-tuning based on Whisper [8]; Conformer-CTC [9]; Bi-LSTM CTC using CTC and LSTM methods [10,11]; a vanilla Transformer [12]; a ViT-modified encoder using CTC/attention and ViT components [10,13]; a Wav2Letter-style CNN-CTC [14]; classical HMM-GMM [15]; and two DNN/HMM hybrids informed by neural acoustic modeling [16]. These are heterogeneous complete recipes, not a controlled architecture or efficiency experiment.

Per-recipe features, preprocessing, tokenizer/vocabulary, initialization or pretraining, augmentation, optimization, batches/epochs/seeds, checkpoint selection, software/hardware, decoder, language model, inference settings, and checkpoint/tokenizer/prediction hashes belong in **Supplementary Table S6** and its method cards. Each checkpoint and tokenizer must be treated as one atomic, hash-verified pair. The full nine-row result table remains supplementary by default until those cards are complete; if retained in the main article, all nine rows must appear together without rank, timing, or superiority wording.

Historical run-native metrics used non-identical reference normalization and denominators. Publication-facing values therefore come from a corrective rescore of existing prediction CSVs, not an inference rerun. Predictions are matched to `splits/test_clean.tsv`; references and hypotheses are normalized by `nssid_project_uniform_v1` using Unicode NFKC, lowercase conversion, replacement of non-ASCII-letter/non-whitespace/non-apostrophe characters by spaces, and whitespace collapse. Corpus WER and CER sum substitution, deletion, and insertion errors across utterances and divide by 135,911 reference words and 942,599 reference characters, respectively. Canonical-manifest and prediction SHA-256 hashes are retained with the rescore outputs.

Uniform scoring fixes the denominator defect but does not equalize pretraining, features, optimization, decoding, software, or hardware. Training and inference times remain provenance only. Synthetic-test-excluded sensitivity, dependence-aware uncertainty, and systematic error analysis are not yet results. The 297-file diagnostic design remains conditional on its sampling token, and direct whole-package header/listening checks remain pending. Section 5 therefore reports only checks actually supported by current artifacts.

# 5. Technical validation

## 5.1. Integrity and sampled acoustic checks

Current checks verify scope totals, category and split sums, human/synthetic counts, public-ID ranges, the 1,956-row bridge, and zero blank transcript fields at the pinned repaired private revision. Metadata records a uniform 16-kHz, mono, PCM16 configuration. These are metadata and manifest checks; the final article must not call them a full audio-header or listening audit until direct evidence and hashes are attached.

The 297 sampled-file table provides dynamic range, silence ratio, and spectral centroid. It is useful for inspecting a bounded cross-category set but cannot support a whole-corpus quality conclusion. Transcript-repair correctness, direct file integrity, and sampling provenance remain separate open validations.

## 5.2. Frozen nine-model benchmark

Technical validation uses the 102,544-file, 130.6548-h frozen benchmark, not the 104,500-file release target. Its train/development/test counts are 71,792/15,376/15,376, with 209 distinct `(category, sentence_id)` pairs. The 15,376-item test set contains 15,374 human recordings and two synthetic repairs. Only three human public labels occur in test, participant uniqueness is unverified, and no natural female-label recording source occurs in development or test.

Human public IDs are separated across partitions, but scripts are seen across splits. The registry records that development/test references occur in training and that 206 test templates are represented in training; exact final wording depends on the pinned overlap attachment. Results therefore measure seen-script held-out-human-speaker recognition under controlled conditions, not unseen-text or open-domain generalization.

Supplementary Table S6 records uniformly rescored WER and CER for all nine recipes as percentages rounded to three decimals and contains no performance-rank column. Across the complete set, WER ranges from 0.186% to 95.966% and CER from 0.140% to 85.117%. These ranges describe heterogeneous complete-recipe outcomes under one scorer; they are not evidence of model-family superiority or hardware-normalized efficiency. Parameter counts remain in the supplementary method cards because the HMM-GMM template-bank count is not directly comparable with neural trainable parameters. Publication disposition is Supplementary Table S6 by default. If editors require a main-text utility table after every method card is complete, all nine rows must be promoted together rather than selectively reported.

# 6. Limitations and responsible use

NSS-ID is closed-prompt/read speech, not conversational or spontaneous speech. It contains only 20 retained human public speaker labels and a narrow repeated prompt inventory with 714 normalized word types under a normalization specification that is not yet publication-complete. Participant uniqueness, age, population, region, dialect, and public sex/gender-label provenance are limited or unverified. The release split has only three human public labels in test, no natural female-label development/test recording source, and scripts represented across partitions. Human-label separation therefore does not imply demographic, text, or TTS-voice separation.

The current release target includes 132 synthetic repairs, including eight development and two test items. Two test repairs have an unresolved female-source/male-target mapping. Synthetic provider voices may recur across partitions. The 297-file acoustic table is a sample, not a whole-corpus acoustic audit. A post-freeze repair restored transcript values for 1,956 release-target rows, but the benchmark was not regenerated and does not validate those rows.

The nine benchmark recipes differ in pretraining, features, tokenizers, optimization, decoders, software, and hardware. Dependence-aware uncertainty, human-only/synthetic-excluded sensitivity, and systematic error analyses are absent. The benchmark provides no evidence of unseen-text, open-vocabulary, conversational, demographic, dialect, population, open-microphone, field, service-robot, or open-domain performance. Deployment recordings and Whisper-derived labels are not corpus ground truth.

Pseudonymous labels reduce direct name exposure but do not anonymize voice. Residual recognition and linkage risk remains. Subject to final consent, governance, and licence wording, the dataset is not intended for re-identification, biometric enrollment or authentication, surveillance, voice cloning or impersonation, demographic or origin inference, harassment, or decisions about individuals. Users should retain provenance fields and document whether synthetic rows were included.

## Ethics Statement — blocked

`[MATERIAL GAP: ethics committee/determination, reference number, and date]`

`[MATERIAL GAP: informed-consent procedure and exact public voice-release/reuse scope]`

`[MATERIAL GAP: demographic minimization and public-schema decision]`

`[MATERIAL GAP: data controller/contact, crosswalk retention, withdrawal, takedown, breach, versioning, and maintenance policy]`

No submission-facing ethics statement may replace these tokens until competent primary evidence and institutional approval are recorded.

## Data Availability — blocked

The working data are staged in a private Hugging Face repository at revision `830a2069416707e3f38c06c507255889513cdf4b`. The repository is not publicly accessible, the card licence is `other`, and no persistent dataset DOI is available. This state is not presented as journal-compliant availability.

`[MATERIAL GAP: prompt-text, audio, metadata, code, and synthetic-output rights clearance]`

`[MATERIAL GAP: exact dataset licence or component-specific licences]`

`[MATERIAL GAP: repository, exact version, persistent DOI, direct URL, checksums, and access date]`

`[MATERIAL GAP: approved controlled-access mechanism, if applicable]`

`[MATERIAL GAP: final whole-package identity/leakage audit]`

## CRediT author statement — blocked

`[MATERIAL GAP: CRediT roles approved by every author]`

## Funding — blocked

`[MATERIAL GAP: funding and sponsor role]`

## Declaration of Competing Interest — blocked

`[MATERIAL GAP: competing-interest declaration approved by every author]`

## Acknowledgements — blocked

`[MATERIAL GAP: acknowledgements]`

## Declaration of generative AI and AI-assisted technologies in manuscript preparation — blocked

`[MATERIAL GAP: GenAI manuscript-preparation determination and declaration]`

Edge-TTS use in data generation belongs in Methods and does not determine whether a separate manuscript-preparation declaration is required.

## Internal author-authorization gate

`[MATERIAL GAP: all-author approval, exclusivity, and explicit submission authorization]`

This internal draft must not be submitted, made public as a manuscript of record, or used to activate the audio repository until the scientific, ethical, rights, privacy, access, and author-approval gates are closed.

# Figure captions for planned artwork

**Figure 1. NSS-ID construction and package flow.** Internal schematic separating recruitment/consent evidence (unresolved gate), 11-category prompt design, the prompted read-speech source tree with 20 retained human labels, segmentation/transcript/QC, 132 labelled synthetic repairs, a common pre-transcript-repair metadata state, the repaired 104,500-row release target, manifests/schema/checksums, private staging, and the separately frozen 102,544-row benchmark. Counts affected by the synthetic mismatch remain provisional. Source values and drawing script must be deposited.

**Figure 2. Release-target duration by category.** Total hours and mean recording duration for each of 11 public English categories in the 104,500-file release target; each category contains 9,500 files. Values are descriptive and do not establish linguistic complexity or real-world frequency. Source: [`tables/Table_3_release_target_category_composition.csv`](tables/Table_3_release_target_category_composition.csv) and its Tier-A input.

**Figure 3. Release-target split and acoustic-source composition.** Files, hours, human public speaker-label counts, and synthetic counts for training, development, and test. Development has zero female-source files; the two female-source test files are synthetic and target M8. There is no natural female-label development/test recording source; participant uniqueness and label provenance are unverified, so the display must not be interpreted as evidence of gender balance or robustness. Omit this figure if Table 4 is sufficient.

**Figure 4. Acoustic diagnostics for 297 sampled files (conditional).** Per-file dynamic range, silence ratio, and spectral centroid for a bounded sample. The figure does not establish corpus-wide SNR, clipping, reverberation, integrity, or transcript correctness and remains blocked until sampling provenance is attached.

# References

1. Suyanto, A. Arifianto, A. Sirwan, A.P. Rizaendra, End-to-End Speech Recognition Models for a Low-Resourced Indonesian Language, in: 2020 8th International Conference on Information and Communication Technology (ICoICT), 2020, pp. 1–6. https://doi.org/10.1109/ICoICT49345.2020.9166346.
2. R. Ardila, M. Branson, K. Davis, M. Kohler, J. Meyer, M. Henretty, R. Morais, L. Saunders, F. Tyers, G. Weber, Common Voice: A Massively-Multilingual Speech Corpus, in: Proceedings of the Twelfth Language Resources and Evaluation Conference, 2020, pp. 4218–4222. https://aclanthology.org/2020.lrec-1.520/.
3. A. Conneau, M. Ma, S. Khanuja, Y. Zhang, V. Axelrod, S. Dalmia, J. Riesa, C. Rivera, A. Bapna, FLEURS: FEW-Shot Learning Evaluation of Universal Representations of Speech, in: 2022 IEEE Spoken Language Technology Workshop (SLT), 2023, pp. 798–805. https://doi.org/10.1109/SLT54892.2023.10023141.
4. M.D. Wilkinson, M. Dumontier, I.J. Aalbersberg, et al., The FAIR Guiding Principles for scientific data management and stewardship, Sci. Data 3 (2016) 160018. https://doi.org/10.1038/sdata.2016.18.
5. T. Gebru, J. Morgenstern, B. Vecchione, J. Wortman Vaughan, H. Wallach, H. Daumé III, K. Crawford, Datasheets for datasets, Commun. ACM 64 (12) (2021) 86–92. https://doi.org/10.1145/3458723.
6. R. Atika, S. Dwijayanti, B.Y. Suprapto, Improving speech-to-text for the Indonesian language using a modified transformer, Eastern-European Journal of Enterprise Technologies 1 (9 (139)) (2026) 78–90. https://doi.org/10.15587/1729-4061.2026.350949.
7. T. Kudo, J. Richardson, SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing, in: Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing: System Demonstrations, 2018, pp. 66–71. https://doi.org/10.18653/v1/D18-2012.
8. A. Radford, J.W. Kim, T. Xu, G. Brockman, C. McLeavey, I. Sutskever, Robust Speech Recognition via Large-Scale Weak Supervision, Proc. Mach. Learn. Res. 202 (2023) 28492–28518. https://proceedings.mlr.press/v202/radford23a.html.
9. A. Gulati, J. Qin, C.-C. Chiu, et al., Conformer: Convolution-augmented Transformer for Speech Recognition, in: Interspeech 2020, 2020, pp. 5036–5040. https://doi.org/10.21437/Interspeech.2020-3015.
10. A. Graves, S. Fernández, F. Gomez, J. Schmidhuber, Connectionist temporal classification: Labelling unsegmented sequence data with recurrent neural networks, in: Proceedings of the 23rd International Conference on Machine Learning, 2006, pp. 369–376. https://doi.org/10.1145/1143844.1143891.
11. S. Hochreiter, J. Schmidhuber, Long Short-Term Memory, Neural Comput. 9 (8) (1997) 1735–1780. https://doi.org/10.1162/neco.1997.9.8.1735.
12. A. Vaswani, N. Shazeer, N. Parmar, et al., Attention Is All You Need, in: Advances in Neural Information Processing Systems 30, 2017. https://papers.nips.cc/paper/7181-attention-is-all-you-need.
13. A. Dosovitskiy, L. Beyer, A. Kolesnikov, et al., An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale, in: International Conference on Learning Representations, 2021. https://openreview.net/forum?id=YicbFdNTTy.
14. R. Collobert, C. Puhrsch, G. Synnaeve, Wav2Letter: an End-to-End ConvNet-based Speech Recognition System, arXiv:1609.03193 (2016). https://arxiv.org/abs/1609.03193.
15. L.R. Rabiner, A tutorial on hidden Markov models and selected applications in speech recognition, Proc. IEEE 77 (2) (1989) 257–286. https://doi.org/10.1109/5.18626.
16. G. Hinton, L. Deng, D. Yu, et al., Deep Neural Networks for Acoustic Modeling in Speech Recognition: The Shared Views of Four Research Groups, IEEE Signal Process. Mag. 29 (6) (2012) 82–97. https://doi.org/10.1109/MSP.2012.2205597.

**Required final dataset reference:** `[dataset]` entry blocked until the approved repository, version, persistent DOI, licence, and access date exist.
