# Extracted manuscript — NSS-ID_INTERNAL_NOT_FOR_SUBMISSION.docx

INTERNAL WORKING DRAFT — NOT FOR SUBMISSION OR PUBLIC RELEASE

## ARTICLE INFORMATION

Article title: NSS-ID: An Indonesian read-speech dataset spanning 11 communicative sentence categories

Authors: Ratna Atika; Suci Dwijayanti; Bhakti Yudho Suprapto. [MATERIAL GAP: final author order and affiliations]

Affiliations: [MATERIAL GAP: final author order and affiliations]

Corresponding author's email address and Twitter handle: [MATERIAL GAP: corresponding author name and current email]

Keywords: ASR; speaker-independent recognition; acoustic modelling; prompted utterances; synthetic augmentation; metadata provenance

Abstract: NSS-ID is a collection of prompted Indonesian voice recordings organized under 11 communicative category labels. The current release-target inventory contains 104,500 PCM WAV files totaling 134.1762 h, including 104,368 human recordings and 132 explicitly flagged synthetic repairs. Repository artifacts organize the human recordings under 20 retained public speaker labels. The final-file metadata records 16-kHz sampling, mono channels, and 16-bit pulse-code modulation. An executable balancing pipeline audited 110,000 source WAV files arranged across 5,500 take directories, omitted one numbered prompt item per category, normalized sentence filenames to two digits, and produced 104,500 structurally verified outputs. The release-target metadata contains 213 distinct (category, sentence_id) pairs and preserves original sentence identifiers, including intentional gaps and partial replacement groups. The planned repository package contains 11 category TAR archives, category transcript files, recording-level metadata, public identifier documentation, split manifests, synthetic-source and repair-target fields, descriptive source values, and reproducibility scripts. A separate pre-repair subset of 102,544 files is retained for seen-script, held-out-human-label ASR technical validation. The package supports filtering by category, public speaker label, partition, sentence identifier, duration, and human or synthetic source while preserving explicit provenance between the release target and frozen benchmark.

[MATERIAL GAP: all-author approval, exclusivity, and explicit submission authorization]

## SPECIFICATIONS TABLE

### Extracted table 1

| Subject | Computer Science |
| --- | --- |
| Specific subject area | Automatic speech recognition and curated Indonesian read-speech data |
| Type of data | Raw PCM WAV audio; processed TAR archives; UTF-8 CSV/TSV/JSON metadata and manifests; analyzed CSV source values; PNG/SVG figures; Python scripts |
| Data collection | Repository artifacts organize prompted recordings under 20 retained human public speaker labels and 11 functional categories. The audited build inspected 110,000 source WAVs, retained 19 numbered items per category, zero-padded filenames, and produced 104,500 files; 132 rows are flagged Edge-TTS repairs. Metadata records final audio as 16-kHz mono PCM16. Recruitment, equipment, session, and QC evidence remain open. |
| Data source location | Sriwijaya State Polytechnic, Palembang, Indonesia (provisional source-draft assertion) |
| Data accessibility | Private Hugging Face staging at revision 830a2069416707e3f38c06c507255889513cdf4b; not publicly accessible; licence recorded as other; persistent dataset DOI unavailable |
| Related research article | R. Atika, S. Dwijayanti, B.Y. Suprapto, Improving speech-to-text for the Indonesian language using a modified transformer, Eastern-European Journal of Enterprise Technologies 1(9 (139)) (2026) 78–90. https://doi.org/10.15587/1729-4061.2026.350949 |

Editable source: tables/Specifications_Table.csv

## VALUE OF THE DATA

• NSS-ID provides 104,500 category-organized prompted recordings with recording-level metadata, stable sentence identifiers, and explicit human/synthetic source fields.

• Eleven TAR archives and corresponding transcript inventories allow users to retrieve data by communicative category without transferring 104,500 individual repository objects.

• Public speaker labels, fixed split fields, sentence identifiers, duration fields, and synthetic repair provenance support reproducible filtering and construction of user-defined analysis subsets.

• Separate release-target and frozen-benchmark manifests allow users to distinguish the repaired 104,500-row corpus state from the 102,544-row state used by the stored nine-recipe ASR validation outputs.

## BACKGROUND

The related research article evaluated a modified Transformer using what appears to be a smaller earlier NSS-ID-derived corpus state [1]. This data article documents the 104,500-file release target, its package hierarchy, stable prompt identifiers, public label scheme, human/synthetic provenance, metadata repair, split manifests, and bounded technical-validation artifacts. Indonesian ASR resources and multilingual corpora provide relevant context for reusable recorded-voice collections [2–4]. FAIR data principles and Datasheets for Datasets motivate explicit identifiers, provenance, access conditions, construction records, and limitations [5,6]. The current article is restricted to data description and acquisition/curation methods; model architecture novelty remains outside its contribution. Exact row, figure, and result overlap with the related article requires [MATERIAL GAP: related 2026 article citation and data/result overlap assessment] before journal eligibility can be determined.

## DATA DESCRIPTION

Repository organization and file inventory

The release package is designed around the directory structure summarized in Table 1 and Figure 1. The pinned private staging revision is 830a2069416707e3f38c06c507255889513cdf4b. It is not presented as publicly available or journal-compliant access.

Table 1. Current and planned components of the NSS-ID data package. The pinned private staging listing contains 11 English-category TAR shards representing 104,500 WAV files; the shard listing totals 15,623,106,560 bytes. Package rows distinguish the 104,500-file release target, the 102,544-file frozen benchmark, sampled diagnostics, and final-deposit components that remain pending. A revision identifier is not a substitute for final package checksums or a persistent dataset DOI.

### Extracted table 2

| Component | Path / member | Format | Rows / files | Package state |
| --- | --- | --- | --- | --- |
| Category audio shards | data/audio_shards/by_category/*.tar | 11 TAR archives containing PCM WAV files | 11 shards / 104500 WAV files | Present in private staging; release not authorized |
| Recording-level metadata | metadata/dataset_metadata_public.csv | CSV | 104500 | Present in private staging; repaired metadata has zero blank transcripts |
| Category transcript lists | data/transcripts/*.txt | UTF-8 text | 11 files / 213 distinct (category, sentence_id) pairs | Present in private staging; numbering gaps are intentional |
| Sentence-ID inventory | metadata/transcript_sentence_inventory_public.csv | CSV | 11 category rows | Present in private staging |
| Public identifier schema | metadata/speaker_labels/hf_public_metadata_schema.md | Markdown | Field dictionary | Present; private identity crosswalk excluded |
| Split manifests | splits/speaker_split_assignment_public.csv; splits/split_summary_public.json; final row manifests [pending] | CSV/JSON/TSV | 20 human public IDs; 104500 row assignments in final manifest [pending] | Summary present; publication-grade generator and immutable row manifests pending |
| Synthetic repair manifest | paper/dataset_information/synthetic_repair_rows_public.csv | CSV | 132 rows | Present; disposition of two source/target mismatches pending |
| Descriptive source values | paper/dataset_information/*.csv; paper/dataset_information/*.json | CSV/JSON | Category, split, speaker, synthetic, lexical, and 297-file sampled diagnostic values | Partly present; regenerated main-figure source package pending |
| Frozen benchmark artifacts | Draft_Paper/02_Evidence/unified_benchmark_rescore/; Report_paper_9model/benchmark/benchmark.json; model cards | CSV/JSON/Markdown/model artifacts | 9 uniformly rescored prediction records / 102544-audio-row benchmark | Uniform rescore present; per-recipe method cards and final supplement/checksum package pending |
| Validation and reproduction scripts | scripts/ and manuscript-facing audit scripts [final paths pending] | Python/shell | Multiple scripts | Local scripts exist; final minimal release bundle pending |
| Package checksum manifest | checksums/SHA256SUMS [planned] | Text/CSV | One record per deposited artifact | Not yet generated because the release package is not frozen |

Editable full source: tables/Table_1_package_inventory.csv

Figure 1. NSS-ID construction and package flow. Internal schematic separating recruitment/consent evidence (unresolved gate), 11-category prompt design, the prompted read-speech source tree with 20 retained human labels, segmentation/transcript/QC, 132 labelled synthetic repairs, a common pre-transcript-repair metadata state, the repaired 104,500-row release target, manifests/schema/checksums, private staging, and the separately frozen 102,544-row benchmark. Counts affected by the synthetic mismatch remain provisional. Source values and drawing script must be deposited.

The root contains README.md and CITATION.cff. The folder data/audio_shards/by_category/ contains the 11 archives Clarification.tar, Conditional.tar, Confirmation.tar, Declarative.tar, Exclamatory.tar, Imperative.tar, Interrogative.tar, Negation.tar, Persuasive.tar, Rhetorical.tar, and Scheduling.tar. Together, the pinned listing reports 15,623,106,560 bytes and 104,500 WAV members.

The folder data/transcripts/ contains Clarification.txt, Conditional.txt, Confirmation.txt, Declarative.txt, Exclamatory.txt, Imperative.txt, Interrogative.txt, Negation.txt, Persuasive.txt, Rhetorical.txt, and Scheduling.txt. These files preserve original 01–20 sentence identifiers and documented numbering gaps.

The metadata/ folder contains dataset_metadata_public.csv with 104,500 rows and transcript_sentence_inventory_public.csv. The file metadata/speaker_labels/hf_public_metadata_schema.md defines public human labels M1..M12 and F1..F8, synthetic labels Ms1..Ms9 and Fs1..Fs9, repair-target fields, and source/target-match fields. The private respondent crosswalk is not part of the package.

The splits/ folder contains speaker_split_assignment_public.csv and split_summary_public.json; immutable release-target row manifests and a complete generator remain pending. The paper/dataset_information/ folder contains synthetic_repair_rows_public.csv and descriptive CSV/JSON source values. Final minimal validation scripts, environment locks, and checksums/SHA256SUMS remain planned components.

Dataset scopes

Table 2 distinguishes the release target from the frozen benchmark. The release target contains 104,500 files and 134.1762 h. The frozen benchmark contains 102,544 files and 130.6548 h because 1,956 rows with blank transcript fields were excluded when its clean manifests were created. A later metadata-only repair populated those fields without changing the audio TAR archives.

Table 2. Mandatory bridge between the current 104,500-file, 134.1762-h release target and the distinct 102,544-file, 130.6548-h frozen benchmark used for nine-model technical validation. The 1,956-row difference reflects transcript fields that were blank when the benchmark was frozen before transcript repair and were later repaired in private staging. The repair did not change audio shards, and the benchmark was not regenerated. Counts of 213 and 209 denote distinct (category, sentence_id) pairs, not necessarily globally unique transcript texts.

### Extracted table 3

| Field | Release target | Frozen benchmark | Evidence control |
| --- | --- | --- | --- |
| Files | 104500 | 102544 | Distinct current release-target and frozen-benchmark scopes |
| Duration (h) | 134.1762 | 130.6548 | Computed within each scope |
| Train / development / test files | 73150 / 15675 / 15675 | 71792 / 15376 / 15376 | Do not substitute one split definition for the other |
| Human recordings | 104368 | 102412 | Frozen scope contains the same 132 synthetic rows |
| Synthetic repairs | 132 | 132 | Synthetic provenance must remain explicit |
| Human speakers | 20 | 20 | Human public IDs are partition-disjoint; TTS voice identity is not guaranteed disjoint |
| Distinct (category, sentence_id) pairs | 213 | 209 | Pairs are not asserted to be globally unique transcript texts |
| Transcript state | Repaired private HF metadata: 0 blank transcript fields | Frozen before transcript repair; excludes rows blank at freeze time | Audio shards did not change during metadata repair |
| Rows present only in release target | 1956 | 0 (excluded) | 1956-row repair bridge requires an immutable publication attachment |
| Test composition | 15675 items = 15673 human + 2 synthetic | 15376 items = 15374 human + 2 synthetic | Do not call every test item human |
| Intended role in article | Corpus description, package, provenance, and reuse | Nine-model technical validation only | Benchmark does not validate every release-target row |
| Availability | Private HF staging; licence other; persistent DOI unavailable | Local frozen evidence package; deposit mapping pending | Neither scope is presently submission-compliant public data |

Editable full source: tables/Table_2_scope_bridge.csv

Categories and prompt identifiers

Each of the 11 public English categories contains 9,500 files. Table 3 and Figure 2 report category-level file count, duration, mean duration, synthetic count, and distinct category–sentence-ID pair count. Seven categories retain 19 identifiers with one intentional gap. Conditional, Confirmation, Persuasive, and Interrogative contain partial replacement pairs involving ID 20. The release target contains 213 distinct (category, sentence_id) pairs; this is not a claim of 213 globally unique transcript texts.

Table 3. File count, duration, mean duration, synthetic count, and sentence-ID inventory for the 11 public English categories in the 104,500-file release target. Each category contains 9,500 files. Values are descriptive and do not establish inherent linguistic complexity or real-world category frequency. Original sentence identifiers and documented gaps/replacement pairs are preserved without renumbering.

### Extracted table 4

| Category | Files | Duration (h) | Mean duration (s) | Synthetic | Category–ID pairs | ID note |
| --- | --- | --- | --- | --- | --- | --- |
| Clarification | 9500 | 13.8089 | 5.2328 | 9 | 19 | Intentional original-ID gap: 09; do not renumber |
| Conditional | 9500 | 15.9704 | 6.0519 | 16 | 20 | Partial replacement pair: 19=490 rows, 20=10 rows; stable original IDs retained |
| Confirmation | 9500 | 14.7951 | 5.6065 | 29 | 20 | Partial replacement pair: 05=483 rows, 20=17 rows; stable original IDs retained |
| Declarative | 9500 | 10.6981 | 4.054 | 2 | 19 | Intentional original-ID gap: 06; do not renumber |
| Exclamatory | 9500 | 9.0423 | 3.4265 | 3 | 19 | Intentional original-ID gap: 20; do not renumber |
| Imperative | 9500 | 7.8119 | 2.9603 | 15 | 19 | Intentional original-ID gap: 20; do not renumber |
| Interrogative | 9500 | 11.8858 | 4.5041 | 10 | 20 | Partial replacement pair: 17=494 rows, 20=6 rows; stable original IDs retained |
| Negation | 9500 | 9.4318 | 3.5742 | 11 | 19 | Intentional original-ID gap: 08; do not renumber |
| Persuasive | 9500 | 17.2061 | 6.5202 | 16 | 20 | Partial replacement pair: 17=489 rows, 20=11 rows; stable original IDs retained |
| Rhetorical | 9500 | 10.4137 | 3.9463 | 17 | 19 | Intentional original-ID gap: 15; do not renumber |
| Scheduling | 9500 | 13.1122 | 4.9688 | 4 | 19 | Intentional original-ID gap: 20; do not renumber |

Editable full source: tables/Table_3_release_target_category_composition.csv

Figure 2. Release-target duration by category. Total hours and mean recording duration for each of 11 public English categories in the 104,500-file release target; each category contains 9,500 files. Values are descriptive and do not establish linguistic complexity or real-world frequency. Source: tables/Table_3_release_target_category_composition.csv and its Tier-A input.

Split and source composition

The release-target train, development, and test partitions contain 73,150, 15,675, and 15,675 files. Their rounded durations are 94.9437, 20.2969, and 18.9357 h; the total calculated from unrounded seconds is 134.1762 h. Retained human public speaker-label counts are 14/3/3, and synthetic counts are 122/8/2. Table 4 and Figure 3 describe the observed source composition without treating labels as independently verified participant identities.

Table 4. Training, development, and test composition for the 104,500-file release target. Retained human public speaker-label counts are 14/3/3 and synthetic counts are 122/8/2. Development has zero female-source files; the two female-source test files are synthetic repairs targeting M8. No natural female-label recording source occurs in development or test. Participant uniqueness and public label provenance remain material gaps. Public-label separation does not imply participant, script, or TTS-voice separation. Split hours are displayed to four decimals and therefore sum to 134.1763 h; the authoritative total calculated from unrounded seconds is 134.1762 h.

### Extracted table 5

| Split | Human public labels | Files | Human recordings | Synthetic | Duration (h) | Male-source files | Female-source files |
| --- | --- | --- | --- | --- | --- | --- | --- |
| train | 14 | 73150 | 73028 | 122 | 94.9437 | 31350 | 41800 |
| dev | 3 | 15675 | 15667 | 8 | 20.2969 | 15675 | 0 |
| test | 3 | 15675 | 15673 | 2 | 18.9357 | 15673 | 2 |
| Total | 20 | 104500 | 104368 | 132 | 134.1762 | 62698 | 41802 |

Editable full source: tables/Table_4_release_target_split_source_composition.csv

Figure 3. Release-target split and acoustic-source composition. Files, hours, human public speaker-label counts, and synthetic counts for training, development, and test. Development has zero female-source files; the two female-source test files are synthetic and target M8. There is no natural female-label development/test recording source; participant uniqueness and label provenance are unverified, so the display must not be interpreted as evidence of gender balance or robustness. Omit this figure if Table 4 is sufficient.

Synthetic repair subset

The release target contains 132 flagged synthetic repairs totaling 632.52 s. Metadata records 73 male-provider-voice files, 59 female-provider-voice files, two provider voice IDs, target public labels, partitions, categories, and source/target-match flags. Two female-provider-voice test rows target male public label M8 and remain unresolved. Table 5 treats the no-cloning statement as a source-author assertion rather than a measured generation result.

Table 5. Current snapshot of 132 explicitly labelled synthetic repairs in the 104,500-file release target, including source-voice, split, category, filtering, and mismatch summaries. Counts are provisional until the authors decide whether to regenerate, exclude, or explicitly retain the two female-source/male-target test rows. Provider configuration, rights, and redistribution review remain open.

### Extracted table 6

| Dimension | Value | Files | Duration (s) | % of release target | Note | Source / scope |
| --- | --- | --- | --- | --- | --- | --- |
| Total | Synthetic repairs | 132 | 632.5200 | 0.1263 | All rows must remain explicitly filterable; totals may change after mismatch disposition. | Release target |
| Generation | Edge-TTS neural voices | 132 |  |  | Documented voice IDs: id-ID-ArdiNeural and id-ID-GadisNeural; [MATERIAL GAP: Edge-TTS version/date/configuration and redistribution-rights review]. | Release target |
| Generation assertion | No-cloning statement |  |  |  | The source author draft states that speaker cloning was not used; an immutable generation log and technical confirmation remain pending. | Source-draft assertion; not a measured release-target count |
| Voice source | Male-source | 73 |  |  | Acoustic TTS voice source, not the sex/gender of a human participant. | Release target |
| Voice source | Female-source | 59 |  |  | Acoustic TTS voice source, not the sex/gender of a human participant. | Release target |
| Split | train | 122 |  |  | Synthetic rows occur in this partition. | Release target |
| Split | dev | 8 |  |  | Synthetic rows occur in this partition. | Release target |
| Split | test | 2 |  |  | Synthetic rows occur in this partition. | Release target |
| Category | Clarification | 9 |  |  | English public category name. | Release target |
| Category | Conditional | 16 |  |  | English public category name. | Release target |
| Category | Confirmation | 29 |  |  | English public category name. | Release target |
| Category | Declarative | 2 |  |  | English public category name. | Release target |
| Category | Exclamatory | 3 |  |  | English public category name. | Release target |
| Category | Imperative | 15 |  |  | English public category name. | Release target |
| Category | Interrogative | 10 |  |  | English public category name. | Release target |
| Category | Negation | 11 |  |  | English public category name. | Release target |
| Category | Persuasive | 16 |  |  | English public category name. | Release target |
| Category | Rhetorical | 17 |  |  | English public category name. | Release target |
| Category | Scheduling | 4 |  |  | English public category name. | Release target |
| Mismatch | Female-source / male-target | 2 | 11.7120 |  | Targets public label M8; [MATERIAL GAP: disposition of two female-source/male-target synthetic rows]. | Release target / unresolved |
| Filtering | is_synthetic and provenance fields | 132 |  |  | Users can exclude synthetic rows with is_synthetic and inspect source/target fields. | Release target |

Editable full source: tables/Table_5_synthetic_repair_provenance.csv

Diagnostic and benchmark derivatives

A derivative CSV contains dynamic range, silence ratio, and spectral centroid for 297 sampled files. Its selection frame and manifest are not yet attached. The frozen benchmark stores nine prediction sets rescored against one 15,376-item canonical test manifest. Supplementary Table S6 contains the complete nine-row WER/CER display and remains outside the main manuscript table sequence pending full method-card and sensitivity attachments.

## EXPERIMENTAL DESIGN, MATERIALS AND METHODS

Evidence classification and scope control

Method statements were classified as OBSERVED, INFERRED, CONFLICTED, or MISSING. OBSERVED denotes an artifact, executable operation, manifest value, or source-author assertion; a source-author assertion is not independent verification that an acquisition event occurred. INFERRED denotes a reconstruction from code or file structure. CONFLICTED denotes disagreeing local records or mixed data states. MISSING denotes absent primary or executable evidence. Release-target and frozen-benchmark procedures are identified separately.

Ethics, recruitment, and participant records

Artifacts establish 20 retained human public speaker labels but do not independently establish recruitment route, eligibility, compensation, participant uniqueness, or exclusions. These require [MATERIAL GAP: participant recruitment and inclusion/exclusion]. The source draft gives both 25–38 and 22–38 years; publication of age requires [MATERIAL GAP: participant age or approved omission]. A later metadata correction yields 12 male and 8 female labels, but field definition and provenance require [MATERIAL GAP: sex/gender label definition and provenance].

No primary artifact currently supports an ethics approval, exemption, waiver, informed consent, or another lawful basis for repository release. Required closure evidence is [MATERIAL GAP: ethics committee/determination, reference number, and date] and [MATERIAL GAP: informed-consent procedure and exact public voice-release/reuse scope].

Prompt inventory and balanced-build transformation

Eleven UTF-8 prompt inventories use an NN|text convention. The parser retains numbered entries, handles later notes separately, and derives absent identifiers against the original 01–20 range. The labels are treated as functional organizational categories; no formal discourse-act validation artifact was found.

process_paper_dataset_sota.py expects 11 category directories, 20 source labels, 25 take directories per label, and 20 numeric WAV items per take. Its build report records 110,000 source WAV files across 5,500 take directories. Balanced V3 retained 19 IDs per category, skipped 5,500 files, zero-padded sentence filenames, and verified 104,500 output files. Prompt authorship, rights, presentation order, intended repetitions, replacement decisions, and retake/rejection procedures require [MATERIAL GAP: repetition, replacement, re-recording, and rejection rules] and [MATERIAL GAP: prompt-text, audio, metadata, code, and synthetic-output rights clearance].

Recording setting and equipment

The source author draft reports collection in a dedicated room in the Electrical Engineering Laboratory building at Sriwijaya State Polytechnic. An undated embedded photograph shows a microphone, laptop, participant position, and foam-lined surfaces. It does not establish which sessions used the setup or measured acoustic performance.

The prose reports a 1 × 1 m floor area and 2.5 m height, whereas embedded diagrams show approximately 1.5037 m × 2.5027 m and approximately 2.5027 m height. The manuscript does not select a value; closure requires [MATERIAL GAP: verified room dimensions and treatment].

The source draft names a BOYA BY-MM1+ microphone, Audacity 3.7.4, Windows 10, and 5–10 cm placement. No asset record, interface record, session screenshot, gain setting, calibration record, or distance-control protocol was located. Required evidence is [MATERIAL GAP: recording dates and session protocol], [MATERIAL GAP: verified microphone, interface, operating system, and recording software/version], and [MATERIAL GAP: microphone distance, gain/calibration, monitoring, and prompt presentation]. Metadata records the final files as 16-kHz, mono, 16-bit PCM WAV; acquisition-native format remains unverified.

Elicitation, segmentation, naming, and transcripts

The source tree implies 11 categories × 20 source labels × 25 take directories × 20 numbered items. It does not define a take or prove universal completion, deliberate variation conditions, prompt randomization, session length, or break structure. Capture-time segmentation and silence-padding procedures are missing. Later processing preserves category/source-label/take hierarchy and normalizes numeric filenames to two digits.

Prompt inventories are the apparent reference-text source, but a contemporaneous transcription protocol was not found. Original sentence identifiers and gaps remain stable. A lowercase regex tokenizer supports the 714-word-type descriptive statistic; it is not a normative reference-transcript policy. The final specification requires [MATERIAL GAP: transcript source and normalization specification] covering Unicode form, case, punctuation, numerals, abbreviations, whitespace, disfluencies, and non-speech events.

Structural quality control and sampled diagnostics

The balanced-build script checks expected directories, retained/omitted IDs, exact filenames, zero-padding, missing/unexpected items, and output totals. These are structural assembly checks, not waveform, pronunciation, or transcript-alignment validation. Direct package-wide decoding, header, duplicate/hash, clipping, and listening evidence remains under sub-gate SG-AUDIO-QC and the parent [MATERIAL GAP: repetition, replacement, re-recording, and rejection rules].

The 297-row derivative contains 27 rows per category, but its selection procedure requires [MATERIAL GAP: 297-file sampling frame, allocation, seed, and inclusion criteria]. Its three metrics are not used as corpus-wide SNR, reverberation, clipping, intelligibility, or transcript-accuracy measurements.

Transcript repair and version bridge

At benchmark freeze, 1,956 rows had blank transcript fields: Conditional 490, Confirmation 483, Persuasive 489, and Interrogative 494. A later private-staging update populated all fields and left audio archives unchanged. The benchmark was not regenerated. Reproducible closure requires [MATERIAL GAP: transcript-repair algorithm, join keys, manifest hashes, and audio-text audit result], including source precedence, ambiguity handling, immutable before/after rows, hashes, assertions, and a listening audit.

Synthetic gap filling

Metadata identifies Microsoft Edge-TTS, id-ID-ArdiNeural, id-ID-GadisNeural, source/target fields, and 132 retained rows. The source author draft states that speaker cloning was not used; an immutable generation log does not currently confirm that statement. Exact package/version/date, commands, output settings, post-processing, generated/rejected counts, QC, and redistribution review require [MATERIAL GAP: Edge-TTS version/date/configuration and redistribution-rights review].

The two female-provider-voice/male-target rows require [MATERIAL GAP: disposition of two female-source/male-target synthetic rows]. Any regeneration or exclusion requires rebuilding manifests, statistics, figures, checksums, and affected sensitivity results.

Metadata, public identifiers, and privacy

Internal metadata includes private source labels and absolute paths; these are not public fields. Public preparation uses M1..M12, F1..F8, Ms1..Ms9, and Fs1..Fs9 with separate repair-target and mismatch fields. The private crosswalk is excluded. Public labels are pseudonymous; recorded voice remains potentially identifying.

The executable metadata builder and complete field provenance remain under SG-METADATA-BUILD and [MATERIAL GAP: transcript source and normalization specification]. Public-field retention requires [MATERIAL GAP: demographic minimization and public-schema decision]. Crosswalk custody and data lifecycle require [MATERIAL GAP: data controller/contact, crosswalk retention, withdrawal, takedown, breach, versioning, and maintenance policy]. Final package inspection requires [MATERIAL GAP: final whole-package identity/leakage audit].

Split construction

Current manifests record 14/3/3 retained human public labels and seed 42. The executed generator, sorted candidate order, RNG/library version, constraints, row-level outputs, hashes, and assertions require [MATERIAL GAP: split-generation algorithm, candidate order, library/version, and exact assignments]. Human public labels are partition-disjoint; prompt texts are not, and provider voices may recur. Exact normalized template intersections and complete benchmark method attachments remain under SG-BENCHMARK-METHODS and [MATERIAL GAP: exact benchmark template-overlap audit].

Statistics, figures, packaging, and technical validation

Release-target tables and Figures 1–3 use 104,500-row source artifacts. Frozen benchmark statistics use 102,544 clean rows. The 297-row derivative is a third scope. Scripts must record input hashes, environments, normalizers, aggregation units, and rounding. Final deposit evidence requires [MATERIAL GAP: repository, exact version, persistent DOI, direct URL, checksums, and access date], [MATERIAL GAP: exact dataset licence or component-specific licences], and [MATERIAL GAP: approved controlled-access mechanism, if applicable].

The nine stored prediction files are matched to splits/test_clean.tsv; publication-facing values are a uniform diagnostic rescore by nssid_project_uniform_v1, not an inference rerun. The normalizer applies Unicode NFKC, lowercase conversion, character replacement, and whitespace collapse. WER and CER use summed exact Levenshtein errors over 135,911 words and 942,599 characters. SentencePiece [7] is used by relevant local recipes, while tokenizer vocabularies remain recipe-specific. The nine recipes use Whisper [8], Conformer [9], CTC/LSTM [10,11], Transformer [12], ViT components [13], Wav2Letter-style CNN-CTC [14], HMM-GMM [15], and DNN/HMM methods [16]. Supplementary Table S6 remains conditional on complete per-recipe method cards, atomic checkpoint/tokenizer/prediction hashes, synthetic-excluded sensitivity, uncertainty, and error analysis.

## LIMITATIONS

NSS-ID contains prompted read speech under 20 retained human public speaker labels; participant uniqueness, recruitment, age, region, dialect, and sex/gender-label provenance are incomplete or unverified. The prompt inventory is narrow and repeatedly represented across partitions. Natural female-label recording sources occur only in training. The release target includes 132 synthetic repairs, including two unresolved female-provider-voice/male-target test rows, and provider voices may recur across partitions. The 1,956 repaired transcript rows lack an attached executable repair manifest and audio–text audit. Acoustic diagnostics cover 297 sampled files without an attached selection frame. Direct package-wide header, readability, clipping, listening, and identity-leakage audits are pending. Voice remains potentially identifying despite pseudonymous labels. Public access, component rights, licence, DOI, data-freeze checksums, collection protocol, and participant consent scope remain unresolved.

## ETHICS STATEMENT

[MATERIAL GAP: ethics committee/determination, reference number, and date]

[MATERIAL GAP: informed-consent procedure and exact public voice-release/reuse scope]

[MATERIAL GAP: demographic minimization and public-schema decision]

[MATERIAL GAP: data controller/contact, crosswalk retention, withdrawal, takedown, breach, versioning, and maintenance policy]

No submission-facing ethics statement is asserted without competent primary evidence and institutional approval.

## CRediT AUTHOR STATEMENT

[MATERIAL GAP: CRediT roles approved by every author]

## ACKNOWLEDGEMENTS

[MATERIAL GAP: acknowledgements]

Funding: [MATERIAL GAP: funding and sponsor role]

## DECLARATION OF COMPETING INTERESTS

[MATERIAL GAP: competing-interest declaration approved by every author]

Internal GenAI manuscript-preparation control: [MATERIAL GAP: GenAI manuscript-preparation determination and declaration]

Internal release/licensing controls: [MATERIAL GAP: prompt-text, audio, metadata, code, and synthetic-output rights clearance]; [MATERIAL GAP: exact dataset licence or component-specific licences]; [MATERIAL GAP: repository, exact version, persistent DOI, direct URL, checksums, and access date]; [MATERIAL GAP: approved controlled-access mechanism, if applicable]; [MATERIAL GAP: related 2026 article citation and data/result overlap assessment]; [MATERIAL GAP: final whole-package identity/leakage audit].

Internal author-authorization control: [MATERIAL GAP: all-author approval, exclusivity, and explicit submission authorization]

## REFERENCES

[1] R. Atika, S. Dwijayanti, B.Y. Suprapto, Improving speech-to-text for the Indonesian language using a modified transformer, Eastern-European Journal of Enterprise Technologies 1 (9 (139)) (2026) 78–90. https://doi.org/10.15587/1729-4061.2026.350949.

[2] Suyanto, A. Arifianto, A. Sirwan, A.P. Rizaendra, End-to-End Speech Recognition Models for a Low-Resourced Indonesian Language, in: 2020 8th International Conference on Information and Communication Technology (ICoICT), 2020, pp. 1–6. https://doi.org/10.1109/ICoICT49345.2020.9166346.

[3] R. Ardila, M. Branson, K. Davis, M. Kohler, J. Meyer, M. Henretty, R. Morais, L. Saunders, F. Tyers, G. Weber, Common Voice: A Massively-Multilingual Speech Corpus, in: Proceedings of the Twelfth Language Resources and Evaluation Conference, 2020, pp. 4218–4222. https://aclanthology.org/2020.lrec-1.520/.

[4] A. Conneau, M. Ma, S. Khanuja, Y. Zhang, V. Axelrod, S. Dalmia, J. Riesa, C. Rivera, A. Bapna, FLEURS: FEW-Shot Learning Evaluation of Universal Representations of Speech, in: 2022 IEEE Spoken Language Technology Workshop (SLT), 2023, pp. 798–805. https://doi.org/10.1109/SLT54892.2023.10023141.

[5] M.D. Wilkinson, M. Dumontier, I.J. Aalbersberg, et al., The FAIR Guiding Principles for scientific data management and stewardship, Sci. Data 3 (2016) 160018. https://doi.org/10.1038/sdata.2016.18.

[6] T. Gebru, J. Morgenstern, B. Vecchione, J. Wortman Vaughan, H. Wallach, H. Daumé III, K. Crawford, Datasheets for datasets, Commun. ACM 64 (12) (2021) 86–92. https://doi.org/10.1145/3458723.

[7] T. Kudo, J. Richardson, SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing, in: Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing: System Demonstrations, 2018, pp. 66–71. https://doi.org/10.18653/v1/D18-2012.

[8] A. Radford, J.W. Kim, T. Xu, G. Brockman, C. McLeavey, I. Sutskever, Robust Speech Recognition via Large-Scale Weak Supervision, Proc. Mach. Learn. Res. 202 (2023) 28492–28518. https://proceedings.mlr.press/v202/radford23a.html.

[9] A. Gulati, J. Qin, C.-C. Chiu, et al., Conformer: Convolution-augmented Transformer for Speech Recognition, in: Interspeech 2020, 2020, pp. 5036–5040. https://doi.org/10.21437/Interspeech.2020-3015.

[10] A. Graves, S. Fernández, F. Gomez, J. Schmidhuber, Connectionist temporal classification: Labelling unsegmented sequence data with recurrent neural networks, in: Proceedings of the 23rd International Conference on Machine Learning, 2006, pp. 369–376. https://doi.org/10.1145/1143844.1143891.

[11] S. Hochreiter, J. Schmidhuber, Long Short-Term Memory, Neural Comput. 9 (8) (1997) 1735–1780. https://doi.org/10.1162/neco.1997.9.8.1735.

[12] A. Vaswani, N. Shazeer, N. Parmar, et al., Attention Is All You Need, in: Advances in Neural Information Processing Systems 30, 2017. https://papers.nips.cc/paper/7181-attention-is-all-you-need.

[13] A. Dosovitskiy, L. Beyer, A. Kolesnikov, et al., An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale, in: International Conference on Learning Representations, 2021. https://openreview.net/forum?id=YicbFdNTTy.

[14] R. Collobert, C. Puhrsch, G. Synnaeve, Wav2Letter: an End-to-End ConvNet-based Speech Recognition System, arXiv:1609.03193 (2016). https://arxiv.org/abs/1609.03193.

[15] L.R. Rabiner, A tutorial on hidden Markov models and selected applications in speech recognition, Proc. IEEE 77 (2) (1989) 257–286. https://doi.org/10.1109/5.18626.

[16] G. Hinton, L. Deng, D. Yu, et al., Deep Neural Networks for Acoustic Modeling in Speech Recognition: The Shared Views of Four Research Groups, IEEE Signal Process. Mag. 29 (6) (2012) 82–97. https://doi.org/10.1109/MSP.2012.2205597.

[dataset] Dataset citation blocked pending [MATERIAL GAP: repository, exact version, persistent DOI, direct URL, checksums, and access date].
