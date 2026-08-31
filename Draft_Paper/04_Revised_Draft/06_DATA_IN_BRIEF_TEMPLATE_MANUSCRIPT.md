# INTERNAL WORKING DRAFT — NOT FOR SUBMISSION OR PUBLIC RELEASE

## ARTICLE INFORMATION

**Article title:** NSS-ID: An Indonesian read-speech dataset spanning 11 communicative sentence categories

**Authors:** Ratna Atika; Suci Dwijayanti; Bhakti Yudho Suprapto. `[MATERIAL GAP: final author order and affiliations]`

**Affiliations:** `[MATERIAL GAP: final author order and affiliations]`

**Corresponding author's email address and Twitter handle:** `[MATERIAL GAP: corresponding author name and current email]`

**Keywords:** ASR; speaker-independent recognition; acoustic modelling; prompted utterances; synthetic augmentation; metadata provenance

**Abstract:** NSS-ID is a collection of prompted Indonesian voice recordings organized under 11 communicative category labels. The current release-target inventory contains 104,500 PCM WAV files totaling 134.1762 h, including 104,368 human recordings and 132 explicitly flagged synthetic repairs. Repository artifacts organize the human recordings under 20 retained public speaker labels. The final-file metadata records 16-kHz sampling, mono channels, and 16-bit pulse-code modulation. An executable balancing pipeline audited 110,000 source WAV files arranged across 5,500 take directories, omitted one numbered prompt item per category, normalized sentence filenames to two digits, and produced 104,500 structurally verified outputs. The release design contains 209 canonical balanced sentence slots (11 categories × 19 retained slots) and preserves original sentence identifiers, including intentional gaps and replacement provenance. The planned repository package contains 11 category TAR archives, category transcript files, recording-level metadata, public identifier documentation, split manifests, synthetic-source and repair-target fields, descriptive source values, and reproducibility scripts. A separate pre-repair subset of 102,544 files is retained for seen-script, held-out-human-label ASR technical validation. The package supports filtering by category, public speaker label, partition, sentence identifier, duration, and human or synthetic source while preserving explicit provenance between the release target and frozen benchmark.

`[MATERIAL GAP: all-author approval, exclusivity, and explicit submission authorization]`

## SPECIFICATIONS TABLE

[SPECIFICATIONS_TABLE]

## VALUE OF THE DATA

- NSS-ID provides 104,500 category-organized prompted recordings with recording-level metadata, stable sentence identifiers, and explicit human/synthetic source fields.
- Eleven TAR archives and corresponding transcript inventories allow users to retrieve data by communicative category without transferring 104,500 individual repository objects.
- Public speaker labels, fixed split fields, sentence identifiers, duration fields, and synthetic repair provenance support reproducible filtering and construction of user-defined analysis subsets.
- Separate release-target and frozen-benchmark manifests allow users to distinguish the repaired 104,500-row corpus state from the 102,544-row state used by the stored nine-recipe ASR validation outputs.

## BACKGROUND

The related research article evaluated a modified Transformer using what appears to be a smaller earlier NSS-ID-derived corpus state [1]. This data article documents the 104,500-file release target, its package hierarchy, stable prompt identifiers, public label scheme, human/synthetic provenance, metadata repair, split manifests, and bounded technical-validation artifacts. Indonesian ASR resources and multilingual corpora provide relevant context for reusable recorded-voice collections [2–4]. FAIR data principles and Datasheets for Datasets motivate explicit identifiers, provenance, access conditions, construction records, and limitations [5,6]. The current article is restricted to data description and acquisition/curation methods; model architecture novelty remains outside its contribution. Exact row, figure, and result overlap with the related article requires `[MATERIAL GAP: related 2026 article citation and data/result overlap assessment]` before journal eligibility can be determined.

## DATA DESCRIPTION

### Repository organization and file inventory

The release package is designed around the directory structure summarized in Table 1 and Figure 1. The pinned private staging revision is `830a2069416707e3f38c06c507255889513cdf4b`. It is not presented as publicly available or journal-compliant access.

[TABLE 1]

[FIGURE 1]

The root contains `README.md` and `CITATION.cff`. The folder `data/audio_shards/by_category/` contains the 11 archives `Clarification.tar`, `Conditional.tar`, `Confirmation.tar`, `Declarative.tar`, `Exclamatory.tar`, `Imperative.tar`, `Interrogative.tar`, `Negation.tar`, `Persuasive.tar`, `Rhetorical.tar`, and `Scheduling.tar`. Together, the pinned listing reports 15,623,106,560 bytes and 104,500 WAV members.

The folder `data/transcripts/` contains `Clarification.txt`, `Conditional.txt`, `Confirmation.txt`, `Declarative.txt`, `Exclamatory.txt`, `Imperative.txt`, `Interrogative.txt`, `Negation.txt`, `Persuasive.txt`, `Rhetorical.txt`, and `Scheduling.txt`. These files preserve original `01`–`20` sentence identifiers and documented numbering gaps.

The `metadata/` folder contains `dataset_metadata_public.csv` with 104,500 rows and `transcript_sentence_inventory_public.csv`. The file `metadata/speaker_labels/hf_public_metadata_schema.md` defines public human labels `M1..M12` and `F1..F8`, synthetic labels `Ms1..Ms9` and `Fs1..Fs9`, repair-target fields, and source/target-match fields. The private respondent crosswalk is not part of the package.

The `splits/` folder contains `speaker_split_assignment_public.csv` and `split_summary_public.json`; immutable release-target row manifests and a complete generator remain pending. The `paper/dataset_information/` folder contains `synthetic_repair_rows_public.csv` and descriptive CSV/JSON source values. Final minimal validation scripts, environment locks, and `checksums/SHA256SUMS` remain planned components.

### Dataset scopes

Table 2 distinguishes the release target from the frozen benchmark. The release target contains 104,500 files and 134.1762 h. The frozen benchmark contains 102,544 files and 130.6548 h because 1,956 rows with blank transcript fields were excluded when its clean manifests were created. A later metadata-only repair populated those fields without changing the audio TAR archives.

[TABLE 2]

### Categories and prompt identifiers

Each of the 11 public English categories contains 9,500 files. Table 3 and Figure 2 report category-level file count, duration, mean duration, synthetic count, and canonical slot design. The release uses 209 canonical balanced sentence slots: 19 retained slots in each of 11 categories. Original sentence IDs, intentional gaps, and replacement provenance remain documented separately.

[TABLE 3]

[FIGURE 2]

### Split and source composition

The release-target train, development, and test partitions contain 73,150, 15,675, and 15,675 files. Their rounded durations are 94.9437, 20.2969, and 18.9357 h; the total calculated from unrounded seconds is 134.1762 h. Retained human public speaker-label counts are 14/3/3, and synthetic counts are 122/8/2. Table 4 and Figure 3 describe the observed source composition without treating labels as independently verified participant identities.

[TABLE 4]

[FIGURE 3]

### Synthetic repair subset

The release target contains 132 flagged synthetic repairs totaling 632.52 s. Metadata records 73 male-provider-voice files, 59 female-provider-voice files, two provider voice IDs, target public labels, partitions, categories, and source/target-match flags. Two female-provider-voice test rows target male public label M8 and remain unresolved. Table 5 treats the no-cloning statement as a source-author assertion rather than a measured generation result.

[TABLE 5]

### Diagnostic and benchmark derivatives

A derivative CSV contains dynamic range, silence ratio, and spectral centroid for 297 sampled files. Its selection frame and manifest are not yet attached. The frozen benchmark stores nine prediction sets rescored against one 15,376-item canonical test manifest. Supplementary Table S6 contains the complete nine-row WER/CER display and remains outside the main manuscript table sequence pending full method-card and sensitivity attachments.

## EXPERIMENTAL DESIGN, MATERIALS AND METHODS

### Evidence classification and scope control

Method statements were classified as OBSERVED, INFERRED, CONFLICTED, or MISSING. OBSERVED denotes an artifact, executable operation, manifest value, or source-author assertion; a source-author assertion is not independent verification that an acquisition event occurred. INFERRED denotes a reconstruction from code or file structure. CONFLICTED denotes disagreeing local records or mixed data states. MISSING denotes absent primary or executable evidence. Release-target and frozen-benchmark procedures are identified separately.

### Ethics, recruitment, and participant records

Artifacts establish 20 retained human public speaker labels but do not independently establish recruitment route, eligibility, compensation, participant uniqueness, or exclusions. These require `[MATERIAL GAP: participant recruitment and inclusion/exclusion]`. The source draft gives both 25–38 and 22–38 years; publication of age requires `[MATERIAL GAP: participant age or approved omission]`. A later metadata correction yields 12 male and 8 female labels, but field definition and provenance require `[MATERIAL GAP: sex/gender label definition and provenance]`.

No primary artifact currently supports an ethics approval, exemption, waiver, informed consent, or another lawful basis for repository release. Required closure evidence is `[MATERIAL GAP: ethics committee/determination, reference number, and date]` and `[MATERIAL GAP: informed-consent procedure and exact public voice-release/reuse scope]`.

### Prompt inventory and balanced-build transformation

Eleven UTF-8 prompt inventories use an `NN|text` convention. The parser retains numbered entries, handles later notes separately, and derives absent identifiers against the original `01`–`20` range. The labels are treated as functional organizational categories; no formal discourse-act validation artifact was found.

`process_paper_dataset_sota.py` expects 11 category directories, 20 source labels, 25 take directories per label, and 20 numeric WAV items per take. Its build report records 110,000 source WAV files across 5,500 take directories. Balanced V3 retained 19 IDs per category, skipped 5,500 files, zero-padded sentence filenames, and verified 104,500 output files. Prompt authorship, rights, presentation order, intended repetitions, replacement decisions, and retake/rejection procedures require `[MATERIAL GAP: repetition, replacement, re-recording, and rejection rules]` and `[MATERIAL GAP: prompt-text, audio, metadata, code, and synthetic-output rights clearance]`.

### Recording setting and equipment

The source author draft reports collection in a dedicated room in the Electrical Engineering Laboratory building at Sriwijaya State Polytechnic. An undated embedded photograph shows a microphone, laptop, participant position, and foam-lined surfaces. It does not establish which sessions used the setup or measured acoustic performance.

The prose reports a 1 × 1 m floor area and 2.5 m height, whereas embedded diagrams show approximately 1.5037 m × 2.5027 m and approximately 2.5027 m height. The manuscript does not select a value; closure requires `[MATERIAL GAP: verified room dimensions and treatment]`.

The source draft names a BOYA BY-MM1+ microphone, Audacity 3.7.4, Windows 10, and 5–10 cm placement. No asset record, interface record, session screenshot, gain setting, calibration record, or distance-control protocol was located. Required evidence is `[MATERIAL GAP: recording dates and session protocol]`, `[MATERIAL GAP: verified microphone, interface, operating system, and recording software/version]`, and `[MATERIAL GAP: microphone distance, gain/calibration, monitoring, and prompt presentation]`. Metadata records the final files as 16-kHz, mono, 16-bit PCM WAV; acquisition-native format remains unverified.

### Elicitation, segmentation, naming, and transcripts

The source tree implies 11 categories × 20 source labels × 25 take directories × 20 numbered items. It does not define a take or prove universal completion, deliberate variation conditions, prompt randomization, session length, or break structure. Capture-time segmentation and silence-padding procedures are missing. Later processing preserves category/source-label/take hierarchy and normalizes numeric filenames to two digits.

Prompt inventories are the apparent reference-text source, but a contemporaneous transcription protocol was not found. Original sentence identifiers and gaps remain stable. A lowercase regex tokenizer supports the 714-word-type descriptive statistic; it is not a normative reference-transcript policy. The final specification requires `[MATERIAL GAP: transcript source and normalization specification]` covering Unicode form, case, punctuation, numerals, abbreviations, whitespace, disfluencies, and non-speech events.

### Structural quality control and sampled diagnostics

The balanced-build script checks expected directories, retained/omitted IDs, exact filenames, zero-padding, missing/unexpected items, and output totals. These are structural assembly checks, not waveform, pronunciation, or transcript-alignment validation. Direct package-wide decoding, header, duplicate/hash, clipping, and listening evidence remains under sub-gate `SG-AUDIO-QC` and the parent `[MATERIAL GAP: repetition, replacement, re-recording, and rejection rules]`.

The 297-row derivative contains 27 rows per category, but its selection procedure requires `[MATERIAL GAP: 297-file sampling frame, allocation, seed, and inclusion criteria]`. Its three metrics are not used as corpus-wide SNR, reverberation, clipping, intelligibility, or transcript-accuracy measurements.

### Transcript repair and version bridge

At benchmark freeze, 1,956 rows had blank transcript fields: Conditional 490, Confirmation 483, Persuasive 489, and Interrogative 494. A later private-staging update populated all fields and left audio archives unchanged. The benchmark was not regenerated. Reproducible closure requires `[MATERIAL GAP: transcript-repair algorithm, join keys, manifest hashes, and audio-text audit result]`, including source precedence, ambiguity handling, immutable before/after rows, hashes, assertions, and a listening audit.

### Synthetic gap filling

Metadata identifies Microsoft Edge-TTS, `id-ID-ArdiNeural`, `id-ID-GadisNeural`, source/target fields, and 132 retained rows. The source author draft states that speaker cloning was not used; an immutable generation log does not currently confirm that statement. Exact package/version/date, commands, output settings, post-processing, generated/rejected counts, QC, and redistribution review require `[MATERIAL GAP: Edge-TTS version/date/configuration and redistribution-rights review]`.

The two female-provider-voice/male-target rows require `[MATERIAL GAP: disposition of two female-source/male-target synthetic rows]`. Any regeneration or exclusion requires rebuilding manifests, statistics, figures, checksums, and affected sensitivity results.

### Metadata, public identifiers, and privacy

Internal metadata includes private source labels and absolute paths; these are not public fields. Public preparation uses `M1..M12`, `F1..F8`, `Ms1..Ms9`, and `Fs1..Fs9` with separate repair-target and mismatch fields. The private crosswalk is excluded. Public labels are pseudonymous; recorded voice remains potentially identifying.

The executable metadata builder and complete field provenance remain under `SG-METADATA-BUILD` and `[MATERIAL GAP: transcript source and normalization specification]`. Public-field retention requires `[MATERIAL GAP: demographic minimization and public-schema decision]`. Crosswalk custody and data lifecycle require `[MATERIAL GAP: data controller/contact, crosswalk retention, withdrawal, takedown, breach, versioning, and maintenance policy]`. Final package inspection requires `[MATERIAL GAP: final whole-package identity/leakage audit]`.

### Split construction

Current manifests record 14/3/3 retained human public labels and seed 42. The executed generator, sorted candidate order, RNG/library version, constraints, row-level outputs, hashes, and assertions require `[MATERIAL GAP: split-generation algorithm, candidate order, library/version, and exact assignments]`. Human public labels are partition-disjoint; prompt texts are not, and provider voices may recur. Exact normalized template intersections and complete benchmark method attachments remain under `SG-BENCHMARK-METHODS` and `[MATERIAL GAP: exact benchmark template-overlap audit]`.

### Statistics, figures, packaging, and technical validation

Release-target tables and Figures 1–3 use 104,500-row source artifacts. Frozen benchmark statistics use 102,544 clean rows. The 297-row derivative is a third scope. Scripts must record input hashes, environments, normalizers, aggregation units, and rounding. Final deposit evidence requires `[MATERIAL GAP: repository, exact version, persistent DOI, direct URL, checksums, and access date]`, `[MATERIAL GAP: exact dataset licence or component-specific licences]`, and `[MATERIAL GAP: approved controlled-access mechanism, if applicable]`.

The nine stored prediction files are matched to `splits/test_clean.tsv`; publication-facing values are a uniform diagnostic rescore by `nssid_project_uniform_v1`, not an inference rerun. The normalizer applies Unicode NFKC, lowercase conversion, character replacement, and whitespace collapse. WER and CER use summed exact Levenshtein errors over 135,911 words and 942,599 characters. SentencePiece [7] is used by relevant local recipes, while tokenizer vocabularies remain recipe-specific. The nine recipes use Whisper [8], Conformer [9], CTC/LSTM [10,11], Transformer [12], ViT components [13], Wav2Letter-style CNN-CTC [14], HMM-GMM [15], and DNN/HMM methods [16]. Supplementary Table S6 remains conditional on complete per-recipe method cards, atomic checkpoint/tokenizer/prediction hashes, synthetic-excluded sensitivity, uncertainty, and error analysis.

## LIMITATIONS

NSS-ID contains prompted read speech under 20 retained human public speaker labels; participant uniqueness, recruitment, age, region, dialect, and sex/gender-label provenance are incomplete or unverified. The prompt inventory is narrow and repeatedly represented across partitions. Natural female-label recording sources occur only in training. The release target includes 132 synthetic repairs, including two unresolved female-provider-voice/male-target test rows, and provider voices may recur across partitions. The 1,956 repaired transcript rows lack an attached executable repair manifest and audio–text audit. Acoustic diagnostics cover 297 sampled files without an attached selection frame. Direct package-wide header, readability, clipping, listening, and identity-leakage audits are pending. Voice remains potentially identifying despite pseudonymous labels. Public access, component rights, licence, DOI, data-freeze checksums, collection protocol, and participant consent scope remain unresolved.

## ETHICS STATEMENT

`[MATERIAL GAP: ethics committee/determination, reference number, and date]`

`[MATERIAL GAP: informed-consent procedure and exact public voice-release/reuse scope]`

`[MATERIAL GAP: demographic minimization and public-schema decision]`

`[MATERIAL GAP: data controller/contact, crosswalk retention, withdrawal, takedown, breach, versioning, and maintenance policy]`

No submission-facing ethics statement is asserted without competent primary evidence and institutional approval.

## CRediT AUTHOR STATEMENT

`[MATERIAL GAP: CRediT roles approved by every author]`

## ACKNOWLEDGEMENTS

`[MATERIAL GAP: acknowledgements]`

**Funding:** `[MATERIAL GAP: funding and sponsor role]`

## DECLARATION OF COMPETING INTERESTS

`[MATERIAL GAP: competing-interest declaration approved by every author]`

**Internal GenAI manuscript-preparation control:** `[MATERIAL GAP: GenAI manuscript-preparation determination and declaration]`

**Internal release/licensing controls:** `[MATERIAL GAP: prompt-text, audio, metadata, code, and synthetic-output rights clearance]`; `[MATERIAL GAP: exact dataset licence or component-specific licences]`; `[MATERIAL GAP: repository, exact version, persistent DOI, direct URL, checksums, and access date]`; `[MATERIAL GAP: approved controlled-access mechanism, if applicable]`; `[MATERIAL GAP: related 2026 article citation and data/result overlap assessment]`; `[MATERIAL GAP: final whole-package identity/leakage audit]`.

**Internal author-authorization control:** `[MATERIAL GAP: all-author approval, exclusivity, and explicit submission authorization]`

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

[dataset] Dataset citation blocked pending `[MATERIAL GAP: repository, exact version, persistent DOI, direct URL, checksums, and access date]`.
