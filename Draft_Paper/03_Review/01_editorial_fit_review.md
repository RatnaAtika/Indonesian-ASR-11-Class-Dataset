# Editorial-fit review: NSS-ID source manuscript

## Verdict

**REJECT in its current form (major rebuild and new editorial review required).** The subject is suitable for an Elsevier *Data in Brief* data article, and the corpus could become publishable, but this draft is not submission-ready. Public data access/reuse terms and human-participant governance are unresolved; the article is structurally incomplete; and several prominent claims conflict with the authoritative registry. These are desk-rejection risks, not copyediting issues.

## Review

### Correct

- **Journal concept/fit:** A reusable Indonesian read-speech corpus with audio, transcripts, metadata, split manifests, and validation scripts is within the scope of a data journal. The manuscript correctly foregrounds the dataset rather than making the modified model its primary title claim ([`Draft_Paper/01_Extraction/manuscript_text.md:3,13-15`](../01_Extraction/manuscript_text.md#L3)).
- **Core full-corpus facts:** The stated 104,500 files, about 134.18 h, 20 retained human public speaker labels (corrected label counts 12 male/8 female; participant uniqueness/provenance unverified), 16-kHz/16-bit/mono format, and 132 synthetic files broadly agree with the registry (`manuscript_text.md:15,52`; [`Draft_Paper/02_Evidence/evidence_registry.json:83-99`](../02_Evidence/evidence_registry.json#L83-L99)).
- **Synthetic-data disclosure:** The draft identifies TTS gap fills, lack of speaker cloning, split/category counts, and the synthetic flag (`manuscript_text.md:52,60-62`). This is appropriate for a data article, subject to the corrections below.
- **Core Data in Brief headings:** Specifications Table, Value of the Data, Background, Data Description, and Experimental Design/Materials and Methods are at least represented (`manuscript_text.md:19-34,46,50,72`).

### Fixed

- None. This was a read-only editorial review; the source manuscript and evidence files were not changed. Only this required review artifact was written.

### Blockers — critical / likely desk rejection

1. **No accessible, citable dataset and no defined reuse licence.** The Specifications Table contains literal placeholders for repository, DOI, and URL (`manuscript_text.md:31`). The authoritative repository is private and its licence is only `other` (`EVIDENCE_REGISTRY.md:15,34-36`; `evidence_registry.json:448-455,724-727`). A data article cannot substantiate reuse or peer review while its data are inaccessible and reuse rights are unknown.
   - **Required fix (Specifications Table; Data Availability):** Deposit the final 104,500-row release in a durable public repository, mint a persistent DOI, provide a direct record URL and version/revision, and select an explicit licence approved by the authors/institution. Add a formal Data Availability statement that identifies exactly what is public and links every directory/file named in the text. Do not submit with placeholders or a private-only Hugging Face record.

2. **Human-participant ethics and voice-release consent are absent and unverified.** This is identifiable voice-biometric data, yet the manuscript has no Ethics Statement or consent statement. The registry confirms that committee details and written-consent scope for public voice release are unresolved (`EVIDENCE_REGISTRY.md:37-38`). Regional-origin attributes add privacy sensitivity (`EVIDENCE_REGISTRY.md:41`).
   - **Required fix (new Ethics Statement; Methods; Data Description):** Obtain and state the verified committee/approval or a justified exemption, approval/reference/date, recruitment and consent procedure, and explicit consent basis for publishing reusable voice recordings and demographic metadata. Remove regional-origin/dialect details unless covered by consent and supported by a public-safe verified table. This cannot be repaired editorially by generic wording.

3. **The manuscript is visibly incomplete.** Keywords are blank (`manuscript_text.md:17`); Methods switches to Indonesian and ends after one fragment (`manuscript_text.md:74-82`); Figure 1 and its underlying-data sentence are incomplete (`manuscript_text.md:64`); no reference list supports citations [1] and [2] (`manuscript_text.md:48`); and there are no complete Ethics, CRediT author-contribution, funding, competing-interest, or acknowledgment/declaration sections. Corresponding-author information is also unresolved in the registry (`EVIDENCE_REGISTRY.md:44`).
   - **Required fix (whole manuscript):** Rebuild in complete English using the current journal template. Supply keywords, references, corresponding author, Ethics Statement, CRediT roles, funding, competing-interest declaration, Data Availability, and any acknowledgments. Resolve author-owned facts rather than inserting boilerplate.

4. **The public-corpus inventory is materially misstated.** The draft says the corpus has 209 sentences and every speaker read every sentence 25 times, yielding 5,225 files each (`manuscript_text.md:48,56`). Authoritative full-public scope is **213 category–sentence templates**; 209 applies only to the frozen 102,544-row benchmark, and four categories have partial replacement ID pairs, so the universal 25-repeat claim is false (`EVIDENCE_REGISTRY.md:5-7,14,40`; `evidence_registry.json:99-140,678-681`).
   - **Required fix (Abstract/Background/Data Description/Methods):** State that the release has 104,500 files and 213 public category–sentence templates, preserve documented numbering gaps/replacement IDs, and explain the partial replacements. Introduce a clearly labelled scope bridge: full public corpus = 104,500/134.1762 h/213 templates; frozen benchmark = 102,544/130.6548 h/209 templates.

### Major findings

5. **Full-corpus and benchmark statistics are mixed without labels.** Figure discussion gives category means of 6.43/5.96/5.58 s and 711 word types (`manuscript_text.md:66,70`), whereas authoritative full-public statistics are 6.5202/6.0519/5.6065 s and 714 normalized word types (`evidence_registry.json:142,191-203,231-234`). The benchmark table (`manuscript_text.md:84-96`) is not identified as results on the frozen 102,544-row subset.
   - **Required fix (Data Description; figures; Technical Validation):** Regenerate all descriptive figures from Tier-A 104,500-row artifacts and label their scope in captions. If the nine-model table remains, place it under a concise “Technical validation” subsection and state its 102,544-row training corpus, 15,376-item test set, and speaker-disjoint design. State that it is **not text-template-disjoint** and that all dev/test rows use transcripts represented in training (`evidence_registry.json:533-543`). Do not present model ranking as the data article’s novelty.

6. **Acquisition and demographic claims exceed verified evidence.** The microphone model/Audacity version (`manuscript_text.md:29`), 5–10 cm distance (`manuscript_text.md:42`), room dimensions/protocol (`manuscript_text.md:76`), ages (25–38 at line 54 versus 22–38 at line 78), and regional/dialect claims (`manuscript_text.md:36-38,48,54,78`) are unverified or internally conflicting. The registry explicitly records these as gaps (`EVIDENCE_REGISTRY.md:39,41-43`).
   - **Required fix (Specifications Table; Value; Methods):** Confirm each acquisition parameter from primary records, reconcile room dimensions and age range, and cite the resulting protocol. Until confirmed, use `[MATERIAL GAP]` internally rather than factual prose. Remove “dialectal variations” and regional representativeness claims unless collection, annotation, consent, and coverage support them.

7. **Methods are not reproducible enough for a data article.** Beyond a room description, the draft does not explain participant selection, prompt design, recording workflow, file naming, transcription creation/validation, normalization, QC/rejection criteria, blank-transcript repair, TTS gap-selection/generation, split algorithm, or descriptive-statistic generation (`manuscript_text.md:72-82`). “Validated transcription” in the abstract is therefore unsupported by described procedures (`manuscript_text.md:15`).
   - **Required fix (Experimental Design, Materials and Methods):** Add ordered subsections for recruitment/consent; prompt/category construction; verified hardware/software/environment; recording and repetitions; transcription and normalization; QC and exclusions; public metadata repair; synthetic replacements and provenance; speaker split generation; and validation/statistical scripts. Identify software versions and repository paths only after confirming they exist in the published package.

8. **Split limitations are hidden.** The abstract promotes speaker-disjoint independent-speaker evaluation (`manuscript_text.md:15`), but the full-public split has no female-source files in dev and only two female-source files in test, while 132 synthetic files include 8 dev and 2 test items (`evidence_registry.json:143-170`). Two female synthetic voices also target a male public label (`evidence_registry.json:717-722`).
   - **Required fix (Data Description; Limitations):** Publish a split table with files, hours, speakers, gender/source composition, and synthetic counts. Explicitly warn that the released split is unsuitable for gender-balanced evaluation and that synthetic items occur in evaluation partitions. Resolve the two voice/target-gender mismatches by regenerating, excluding, or retaining them with a machine-readable mismatch flag and explicit disclosure.

9. **The narrative overclaims naturalness, representativeness, and generalization.** Statements that a repeated, prompted corpus has “realistic linguistic characteristics,” is “representative of everyday language use,” supports “real-world” structures, reduces bias, or supports reliable generalization are not demonstrated (`manuscript_text.md:66,68,70`). A Zipf-like curve does not establish representativeness, especially with only 213 prompted templates repeated many times.
   - **Required fix (Value/Data Description/Limitations):** Describe this precisely as controlled **read/prompted speech**. Replace causal and representativeness language with descriptive observations. Limit reuse claims to tasks the structure supports, and state the constrained vocabulary/template coverage, controlled room, small speaker count, repeated prompts, geographic uncertainty, synthetic repairs, and non-template-disjoint benchmark.

10. **Table and figure architecture is broken.** Text says Table 1 describes repository directories and Table 2 contains split counts (`manuscript_text.md:52,58`), but extracted Table 1 is the Specifications Table and Table 2 is the model ranking (`manuscript_text.md:21-32,84-96`). Figure numbering alternates between “Figure 1” and “F1–F5,” captions are embedded as a long paragraph, and the Figure 1 source-data reference is unfinished (`manuscript_text.md:64-70`).
    - **Required fix (Data Description; displays):** Renumber displays sequentially and align every callout. Add (a) repository tree/file-inventory table, (b) full-corpus category table, (c) full-public split/composition table, and (d) metadata data dictionary. Give each figure a standalone self-contained caption with population/scope, units, sample size, and underlying-data path. Move secondary descriptive plots to supplement if they do not aid reuse. Avoid a model-ranking table in the main narrative unless fully contextualized as technical validation.

### Moderate editorial findings

11. **Title is understandable but weak and inconsistently styled.** “NSS-ID : Nusantara Speech Sample Indonesian Dataset” has faulty colon spacing, expands the acronym awkwardly, and does not identify controlled read speech or the principal reusable structure (`manuscript_text.md:3`).
    - **Concrete replacement:** **“NSS-ID: An Indonesian read-speech dataset spanning 11 communicative sentence categories.”** Do not add “dialectal,” “representative,” or performance language without evidence.

12. **Abstract needs factual tightening.** It is a useful inventory-style abstract, but the synthetic percentage is wrong (0.129% at `manuscript_text.md:15`; authoritative 0.1263% at `evidence_registry.json:83-87`), it does not disclose prompted/repeated speech, and it overextends reuse to text normalization and resource-constrained NLP without explaining the supporting content. “Speaker’s identity” should be “anonymized speaker ID.”
    - **Required fix (Abstract):** Use one scope throughout; state 104,500 files/134.1762 h, 104,368 human + 132 synthetic (0.1263%), 20 speakers, controlled read speech, 213 public templates/11 categories, audio format, package contents, and restrained reuse. Add the persistent repository/DOI only once public. Avoid model-performance claims.

13. **Value of the Data does not follow a strong value proposition.** It is five prose paragraphs, two of which are acquisition/count facts rather than value (`manuscript_text.md:34-44`), and it repeats unsupported dialect/real-time robot claims.
    - **Required fix (Value of the Data):** Convert to 3–5 concise bullets that answer: what is distinctive; who benefits; how it can be reused; what annotations/splits enable; and what comparisons/augmentation are possible. A defensible core is category-balanced prompted Indonesian speech with explicit human/synthetic provenance and reproducible manifests—not dialect coverage or field robustness.

14. **Specifications Table is incomplete and partly misclassified.** It omits the journal-style data location details needed for reuse, mixes “Data collection” with “How acquired,” and gives unverified equipment facts (`manuscript_text.md:23-32`). Keywords are empty (`manuscript_text.md:17`).
    - **Required fix:** Populate all current template fields exactly, add 4–6 searchable keywords (e.g., Indonesian; read speech; automatic speech recognition; speech corpus; communicative sentence categories; synthetic speech), and make location/acquisition/access entries consistent with Methods and the public archive.

15. **A dedicated Limitations section is needed.** Current text reads as promotion and does not consolidate limitations. This makes the extremely low benchmark WER especially easy to misinterpret.
    - **Required fix:** State controlled acoustics, 20 speakers, prompted/repeated templates, limited lexical coverage, unresolved demographic representativeness, split gender imbalance, synthetic gap fills (including test), template overlap across benchmark splits, sampled-only acoustic diagnostics (n=297, not all files; `evidence_registry.json:437-438,696-704`), and the distinction between corpus utility and out-of-domain performance.

## Recommended section-level rebuild order

1. Resolve **public DOI/access/licence** and **ethics/voice-release consent** before prose polishing.
2. Freeze the scope bridge and regenerate all full-public descriptive statistics/figures from Tier A.
3. Rewrite title, abstract, keywords, Specifications Table, and Value bullets around controlled read-speech reuse.
4. Rebuild Data Description with repository inventory, schemas/data dictionary, category/split composition, synthetic provenance, replacement IDs, and figure/table captions.
5. Write complete reproducible Methods and a frank Limitations section.
6. Retain the nine-model results only as bounded technical validation of the frozen benchmark; disclose transcript-template overlap and hardware differences, and avoid speed comparisons or model-novelty framing.
7. Complete references and all declarations; then perform a final cross-reference, language, privacy-label, and evidence audit.

## Residual risks

- Publication remains blocked until authors/institution resolve DOI/access/licence and ethics/consent facts.
- Acquisition details, age range, regional metadata, room geometry, author roles, funding, and competing interests require primary-source confirmation; editorial inference is unsafe.
- The existing benchmark’s transcript-template overlap and evaluation split composition limit generalization claims even after accurate disclosure.
- The two synthetic voice/target-gender mismatches require a documented data decision.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Severity-ranked findings cite Draft_Paper/01_Extraction/manuscript_text.md and both evidence-registry representations with line-level evidence, concrete section-level fixes, a reject verdict, and residual risks."
    }
  ],
  "changedFiles": [
    "Draft_Paper/03_Review/01_editorial_fit_review.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "nl -ba Draft_Paper/01_Extraction/manuscript_text.md | sed -n '1,260p'",
      "result": "passed",
      "summary": "Inspected the complete extracted manuscript with stable line numbers."
    },
    {
      "command": "nl -ba Draft_Paper/02_Evidence/EVIDENCE_REGISTRY.md",
      "result": "passed",
      "summary": "Verified authoritative scope and material-gap statements with line numbers."
    },
    {
      "command": "nl -ba Draft_Paper/02_Evidence/evidence_registry.json | sed -n '78,170p;430,475p;525,550p;674,735p'",
      "result": "passed",
      "summary": "Verified corpus, split, repository, benchmark, scope-bridge, privacy, and material-gap evidence."
    },
    {
      "command": "git status --short -- Draft_Paper",
      "result": "passed",
      "summary": "No staged files were shown; Draft_Paper is untracked in the working tree."
    }
  ],
  "validationOutput": [
    "Observed full public scope: 104,500 files, 134.1762 h, 213 templates; benchmark scope: 102,544 files, 130.6548 h, 209 templates.",
    "Observed public-access blockers: private HF repository, licence recorded as 'other', no persistent dataset DOI.",
    "Observed manuscript blockers: placeholder data URL/DOI, absent ethics/consent declarations, blank keywords, incomplete methods, broken display references, and evidence-conflicting claims."
  ],
  "residualRisks": [
    "Dataset DOI/access/licence and ethics/voice-release consent are unresolved author-owned blockers.",
    "Several acquisition, demographic, regional, room, and declaration facts remain unverified.",
    "Benchmark template overlap and split composition constrain generalization claims.",
    "Two synthetic female-voice files target a male public label and require a documented resolution."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added only the requested editorial review artifact; no manuscript or evidence source was modified.",
  "reviewFindings": [
    "blocker: Draft_Paper/01_Extraction/manuscript_text.md:31 - repository, DOI, and URL are placeholders while authoritative evidence says the repository is private and the licence unresolved.",
    "blocker: Draft_Paper/01_Extraction/manuscript_text.md - no verified ethics/voice-release consent statement for identifiable speech data.",
    "blocker: Draft_Paper/01_Extraction/manuscript_text.md:48,56 - 209-sentence and universal 25-repeat claims conflict with the 213-template public inventory and documented partial replacements.",
    "major: Draft_Paper/01_Extraction/manuscript_text.md:66,70,84-96 - full-corpus descriptions and frozen-benchmark evidence are mixed without scope labels.",
    "major: Draft_Paper/01_Extraction/manuscript_text.md:72-82 - methods are incomplete and partly Indonesian.",
    "major: Draft_Paper/01_Extraction/manuscript_text.md:52,58,64-70,84-96 - tables, figures, captions, and cross-references are inconsistent or incomplete."
  ],
  "manualNotes": "Verdict: reject in current form; the dataset topic fits Data in Brief, but a major evidence-led rebuild is required before submission."
}
```
