# Current Data in Brief expectations for speech-dataset Methods

**Retrieval date:** 22 July 2026  
**Scope:** Elsevier *Data in Brief* (DiB) requirements and peer-reviewed speech/audio data-article examples, with implications for NSS-ID.

## Summary

A DiB speech data article should use the journal template, link the described data to a repository, and give enough dataset-specific detail to understand how every released object was generated. For human speech, the current Guide for Authors also calls for dated, numbered ethics approval, informed consent, and protection of participant privacy. Strong speech examples document the full chain from recruitment and prompts through recording, segmentation, transcription/labels, quality control, dataset organization, and validation; however, calibration, checksums, and leakage-safe split manifests are weakly represented in the examples reviewed.

## Evidence labels

- **Official / snippet-only:** authoritative Elsevier source, but evidence was read through the `web_search` indexed extract because direct full-page retrieval tools were unavailable.
- **Primary article / indexed full-text extract:** peer-reviewed DiB article exposed through the PMC result returned by `web_search`; stronger as an example than as a journal-wide rule.
- **Dataset record / indexed extract:** repository metadata returned by search; useful for deposited-file details.

## 1. Current official requirements

1. **Purpose and article type — Official / snippet-only.** DiB publishes short, peer-reviewed articles that describe and provide access to research data, supports FAIR, and expects data collected by a scientific method with community reuse value. Data articles are templated and must describe data produced and owned by the author or institution. The current guide says all data articles must link to a repository and that datasets with insufficient variables or samples are not accepted. [Guide for Authors](https://www.sciencedirect.com/journal/data-in-brief/publish/guide-for-authors)

2. **Expected structure — Official / snippet-only.** The guide requires clearly defined sections covering essential elements and use of the data-article template. The editor-authored June 2024 quick guide highlights the Specifications table, Value of the Data, Data Description, and Experimental Design, Materials and Methods. It advises moving detailed experimental factors/features from the Specifications table into Methods and avoiding a mini research paper, Discussion, or Conclusion. [Quick guide, June 2024](https://researcheracademy.elsevier.com/uploads/2024-07/Quick_guide_Data_in_brief.pdf)

3. **Methods content — Official / snippet-only.** “Experimental Design, Materials and Methods” should give the essential information needed to understand how the shared data were created, include only material directly relevant to those data, and add enough detail, equations, or statistics to explain generation or derivation. Authors should not paste a parent paper's entire Methods section. [Quick guide, June 2024](https://researcheracademy.elsevier.com/uploads/2024-07/Quick_guide_Data_in_brief.pdf)

4. **Data access and citation — Official / snippet-only.** Under Elsevier research-data policy Option D, authors are required to deposit research data in a relevant repository and cite/link the dataset in the article. The guide requests dataset author(s), title, repository, version where available, year, and persistent identifier. The quick guide says links should not be behind a firewall and describes depositing to a public repository or Mendeley Data. [Guide for Authors](https://www.sciencedirect.com/journal/data-in-brief/publish/guide-for-authors) [Quick guide](https://researcheracademy.elsevier.com/uploads/2024-07/Quick_guide_Data_in_brief.pdf)

5. **Human participants — Official / snippet-only.** For work involving humans, the current guide says procedures must comply with relevant laws and institutional guidelines and be approved by the appropriate committee. The manuscript statement must contain the approval date and reference number, state that privacy rights were observed, and state that informed consent was obtained. It also says identifiable personal details should not be used and written consents must be retained rather than routinely submitted. [Guide: Studies in humans; Informed consent and patient details](https://www.sciencedirect.com/journal/data-in-brief/publish/guide-for-authors)

6. **Sex/gender reporting — Official / snippet-only.** Where relevant, the guide asks authors to define how sex and gender are used, address those dimensions or identify limits to generalizability, and aim for representative human populations. [Guide for Authors](https://www.sciencedirect.com/journal/data-in-brief/publish/guide-for-authors)

**Implication for NSS-ID:** follow the current policy rather than copying older examples that state “no ethical approval was required.” NSS-ID should report the responsible committee, approval date/ID, consent scope for recording and public voice release, withdrawal terms, de-identification, and residual re-identification/voice-cloning risk.

## 2. Relevant speech/audio examples

1. **IndoWaveSentiment (published 16 November 2024) — Primary article / indexed full-text extract.** Ten Indonesian voice professionals, balanced 5/5 by reported sex, recorded one sentence across five emotions, two intensities, and three repetitions (300 files). Methods report a studio, cardioid dynamic microphone, mono capture, ≤10 cm placement, 32-bit depth, Audacity segmentation to 3–5 s, volume normalization/noise reduction, a four-field filename scheme, and validation by 104 questionnaire respondents. It reports voluntary consent, anonymization, and post-recording sample approval. Concrete strength: protocol, repetition arithmetic, naming, processing, and perceptual QC are connected. [Article; DOI 10.1016/j.dib.2024.111138](https://pmc.ncbi.nlm.nih.gov/articles/PMC11647155/)

2. **LUMINA Indonesian audio-visual speech (published 1 March 2024) — Primary article / indexed full-text extract.** Fourteen native speakers each read at least 1,000 algorithm-selected sentences. It documents sentence construction and syllable-coverage selection, a 4 × 4 m soundproof room, microphone/camera/light/prompter models and geometry, 20-minute sessions to limit fatigue, backup prompts, manual rejection rules, 3.3 s clips, resampling to 16 kHz, audio/video pairing, and `P<speaker>_S<sentence>` naming. Ethics text reports consent, voluntariness, anonymization, and participant approval of samples. [Article; DOI 10.1016/j.dib.2024.110279](https://pmc.ncbi.nlm.nih.gov/articles/PMC11220857/)

3. **BanglaSER (published 22 March 2022) — Primary article / indexed full-text extract.** Thirty-four nonprofessional actors produced three sentences, three repetitions, and five acted emotions. Methods document recruitment and training, quiet-room versus smartphone collection, BOYA BY-M1 microphone at 6 cm through a USB interface, 44.1 kHz capture, Audacity 2.3.2, trimming to 3–4 s, WAV conversion, a seven-field filename convention, erroneous-recording removal, and independent perceptual evaluation by 15 listeners (reported 80.5% recognition). The dataset has a versioned Mendeley DOI. [Article; DOI 10.1016/j.dib.2022.108091](https://pmc.ncbi.nlm.nih.gov/articles/PMC8980634/)

4. **Curated Luganda/Kiswahili TTS data (article accepted 16 July 2025; repository published 8 May 2025) — Primary article and dataset record / indexed extracts.** The corpus derives from specified Mozilla Common Voice versions. Six female speakers per language were selected manually and checked with pitch/MFCC clustering; WebRTC VAD trimmed silence, causal DEMUCS denoised audio, and WV-MOS filtering retained clips scoring ≥3.5. The final release pairs WAV files with `metadata.csv` filename/transcript rows and reports more than 19 h Luganda and 15 h Kiswahili. This is a strong provenance and reproducible-curation example, but not a new recruitment/recording protocol. [Article; DOI 10.1016/j.dib.2025.111915](https://doi.org/10.1016/j.dib.2025.111915) [Mendeley Data v1](https://data.mendeley.com/datasets/nb8b25h9nj/1)

5. **H-Voice synthetic/fake voice histograms (published 26 February 2020) — Primary article / indexed full-text extract.** This example distinguishes machine-generated “fake” speech sources, identifies Deep Voice and wavelet-based imitation provenance, supplies generation/pseudocode details, requantizes source audio to 16 bit, specifies 65,536-bin histogram derivation, and enumerates training, validation, and two external-test directories. Version 4 records correction of corrupted images. It demonstrates how NSS-ID should isolate synthetic/augmented derivatives and document algorithms, inputs, parameters, counts, and split purpose. [Article; DOI 10.1016/j.dib.2020.105331](https://pmc.ncbi.nlm.nih.gov/articles/PMC7058910/)

## 3. Minimum-evidence checklist for NSS-ID

### Participants and governance

- State target population, inclusion/exclusion criteria, recruitment and sampling route, location/date range, compensation, speaker count, and relevant demographic distribution.
- Give ethics committee name, approval date and reference number; describe informed consent for recording, public redistribution, computational use, and synthetic/voice-cloning uses; state withdrawal and privacy procedures.
- Use pseudonymous speaker IDs; keep contact/consent records outside the release; discuss voice re-identification risk and license restrictions without claiming that voice is anonymized merely by renaming files.

### Recording and elicitation

- Report room/environment, background-noise policy, device chain (microphone, interface/recorder, app/software and versions), channel count, sample rate, bit depth, format, microphone placement, gain settings, and any level checks.
- Report calibration method and reference level if performed; otherwise explicitly state that no formal acoustic calibration was performed and describe consistency controls.
- Publish the prompt inventory and its provenance/licensing, assignment/randomization, instructions, pace, repetitions, retake policy, session duration/breaks, and expected-versus-retained count arithmetic.

### Processing, transcripts, and QC

- Describe continuous-recording boundaries and utterance segmentation, silence padding, resampling, normalization, denoising, clipping policy, and every tool/model/version/threshold. Preserve raw versus processed status and provenance links.
- Define the filename grammar and directory hierarchy; provide stable speaker, prompt, repetition, condition, and derivative identifiers without personal data.
- Document transcription source, orthography, Unicode and punctuation/case/number rules, disfluency/noise tags, non-speech handling, annotator qualifications, double review/adjudication, and audio–text alignment checks.
- State automated and manual QC tests and rejection counts/reasons: readability/decoding, duration, sample rate/channel consistency, clipping, silence, SNR/noise where used, duplicate detection, prompt/transcript match, pronunciation, and spot-audit sampling. Report agreement or error statistics where labels require judgment.

### Synthetic data, splits, and release integrity

- Keep original, augmented, and synthetic audio separable. For each derivative, record source IDs, algorithm/model and version, parameters/seed, generation date, filtering, license, and counts; do not mix synthetic clips into human totals.
- Explain split generation, ratios/counts, random seed/code, stratification, exclusions, and leakage controls. For speaker recognition/ASR, state whether speakers, prompts, sessions, and source recordings are disjoint as appropriate.
- Deposit audio, transcripts, prompt list, machine-readable metadata/data dictionary, explicit split manifests, QC/rejection summary, license/README, and generation scripts in a versioned repository with DOI.
- Provide a complete file manifest with relative path, bytes, media properties, duration, speaker/prompt/split IDs, and SHA-256 checksum; report totals that reconcile across manuscript, metadata, archive, and repository version.

### Technical validation

- Validate archive integrity and manifest checksums; report corpus totals and distributions by speaker, split, condition, prompt/category, duration, and recording chain.
- Report transcription/label audit results and inter-annotator agreement where applicable. Add a modest reproducible baseline only if useful for demonstrating fitness (for example, ASR WER/CER), with speaker-safe splits and no claims beyond validation.

## 4. Limitations of this research

- Direct full-page retrieval/fetch tools were unavailable. Official requirements above are therefore explicitly **search-snippet-only**, even where the search index returned long extracts. Requirements should be rechecked against the live Guide and current DiB template immediately before submission.
- The article evidence was obtained from indexed PMC/search extracts, not independently downloaded PDFs. Examples show accepted reporting practice, not mandatory fields.
- The reviewed examples rarely report formal microphone calibration, cryptographic checksums, complete file manifests, normalization specifications, or leakage-safe split-generation code. Their absence is not evidence that DiB discourages these items; NSS-ID should include them to strengthen reproducibility.
- Older examples' ethics wording may not satisfy the current Guide. No determination was made about NSS-ID's local ethics status or consent language.

## Sources retained

- Elsevier, *Data in Brief* Guide for Authors — current official policy and requirements: https://www.sciencedirect.com/journal/data-in-brief/publish/guide-for-authors
- Wang, “How to write a good Data in Brief article,” June 2024 — editor-authored structure/methods guidance: https://researcheracademy.elsevier.com/uploads/2024-07/Quick_guide_Data_in_brief.pdf
- IndoWaveSentiment (2024): https://pmc.ncbi.nlm.nih.gov/articles/PMC11647155/
- LUMINA (2024): https://pmc.ncbi.nlm.nih.gov/articles/PMC11220857/
- BanglaSER (2022): https://pmc.ncbi.nlm.nih.gov/articles/PMC8980634/
- Luganda/Kiswahili TTS article and repository (2025): https://doi.org/10.1016/j.dib.2025.111915 and https://data.mendeley.com/datasets/nb8b25h9nj/1
- H-Voice (2020): https://pmc.ncbi.nlm.nih.gov/articles/PMC7058910/
