# Submission-readiness audit: NSS-ID data article

**Target:** Elsevier *Data in Brief* (data article)  
**Decision:** **FAIL — not ready for submission; do not submit in the present state.**  
**Audit type:** Read-only review of the three specified project sources. Only this audit artifact was created; the manuscript, evidence registry, and workflow were not modified.

## Basis and limits of review

Reviewed:

- [`Draft_Paper/01_Extraction/manuscript_text.md`](../01_Extraction/manuscript_text.md)
- [`Draft_Paper/02_Evidence/EVIDENCE_REGISTRY.md`](../02_Evidence/EVIDENCE_REGISTRY.md)
- [`Draft_Paper/99_Admin/BMAD_SUPERPOWERS_WORKFLOW.md`](../99_Admin/BMAD_SUPERPOWERS_WORKFLOW.md)

The current *Data in Brief* Guide for Authors and data-suitability policy were also checked on **2026-07-22**:

- <https://www.sciencedirect.com/journal/data-in-brief/publish/guide-for-authors>
- <https://www.sciencedirect.com/journal/data-in-brief/about/policies-and-guidelines/what-data-are-suitable-for-data-in-brief>

Those policies say that a data article must describe data deposited in a repository and link/cite the data; raw data must be freely available for acceptance, subject to the journal's controlled-access provisions for genuinely sensitive data. The guide also requires human-study ethics and informed-consent statements, funding disclosure, competing-interest completion, and a declaration when generative AI was used in manuscript preparation. This audit did **not** inspect the DOCX, repository files, consent forms, ethics documents, figures, references, cover letter, submission portal, or primary acquisition records. Their existence must not be inferred from manuscript claims.

## Gate verdicts

| Gate | Verdict | Evidence and rationale |
|---|---|---|
| **1. Research worth / data utility** | **CONDITIONAL PASS** | A 134.1762-hour Indonesian speech resource with 104,500 files, recording-level metadata, labeled synthetic repairs, and intended speaker-disjoint splits could be useful for ASR and speech-resource research (`EVIDENCE_REGISTRY.md:5-16`; `manuscript_text.md:15,52-60`). *Data in Brief* evaluates data utility and reusability rather than conventional hypothesis novelty. However, utility cannot be established fully while the data are private, reuse rights are undefined, methods/QC are incomplete, and representativeness is overstated. |
| **2. Design, ethics, validity, and reproducibility** | **FAIL** | Ethics approval and public-release consent for identifiable voice data are unverified; acquisition details conflict; transcript validation is asserted but not described; 209 versus 213 sentence-template scopes conflict; the exact-25-repetitions claim is known to be false as written; synthetic files occur in train/dev/test and two have a voice/target-sex mismatch (`EVIDENCE_REGISTRY.md:34-45`; `manuscript_text.md:15,42,48,54-60,74-82`). |
| **3. Manuscript story and internal coherence** | **FAIL** | A defensible central message is possible—an openly reusable, controlled Indonesian read-speech corpus with explicit synthetic repairs—but the current text mixes full-dataset and benchmark narratives, overstates dialect/everyday-language representativeness, contains contradictory demographics and counts, and ends in an incomplete Indonesian-language methods section plus an unexplained model ranking table (`manuscript_text.md:36-48,54-56,66-96`; `BMAD_SUPERPOWERS_WORKFLOW.md:14-24`). |
| **4. Editor-facing submission package** | **FAIL** | The data-access field contains placeholders, the only evidenced HF repository is private with licence `other`, keywords are blank, tables/figures are missing or misnumbered, references are incomplete, the corresponding author is not properly designated, and ethics/consent, CRediT, funding, competing interests, and GenAI determination are absent (`manuscript_text.md:3-17,21-32,52-64`; `EVIDENCE_REGISTRY.md:15,34-44`). No cover letter or final submission checklist was among the reviewed files. |

**Overall journal fit:** **potentially suitable only after remediation.** The subject and data-article format fit *Data in Brief* in principle, but public/reviewer-accessible deposition, lawful reuse, human-participant safeguards, scientific-method documentation, and template completeness are threshold conditions, not cosmetic revisions. A backup-journal cascade is premature because the public-access, consent, licence, and factual-integrity problems would follow the manuscript to another venue.

## Desk-rejection and administrative blockers

### Critical — resolve before submission

1. **No compliant repository link or persistent dataset citation.**  
   `manuscript_text.md:31` still says `[Mendeley Data/Zenodo]`, `[dataset DOI]`, and `[URL]`. The registry confirms that no final DOI exists and the HF repository is private (`EVIDENCE_REGISTRY.md:15,34-35`). A private HF revision is not evidence of the openly accessible, citable dataset described in the manuscript. Deposit the complete article data in a suitable repository, provide editor/reviewer access as required, establish the compliant public-release path, test all links without privileged credentials, and cite the versioned dataset with its persistent identifier. Include raw/source data underlying every article figure and table.

2. **Human-subject ethics and consent are not documented.**  
   The article describes recordings from adult volunteers and releases voices plus demographic/regional metadata (`manuscript_text.md:15,36-44,54,76-78`), yet it contains no ethics or consent section. Committee name, approval/reference number, and approval date are unverified; the scope of written consent for public release and reuse of voice biometrics is also unverified (`EVIDENCE_REGISTRY.md:37-38`). Obtain and accurately report the actual approval or documented exemption/waiver from the competent body, including date/reference, applicable law/institutional compliance, privacy safeguards, and informed consent. Confirm that consent explicitly covers repository publication and the intended reuse terms. If it does not, stop public release and seek institutional/journal guidance; do not invent or retrospectively imply approval.

3. **The data are not demonstrably reusable under a defined licence.**  
   The repository licence is only `other` (`EVIDENCE_REGISTRY.md:15,36`). Confirm data ownership and select explicit, legally compatible terms for audio, transcripts/metadata, and code. Confirm that participant consent, sentence-text rights, and Microsoft Edge-TTS terms permit the planned redistribution and licence. The eventual open-access article licence does not substitute for a dataset licence.

4. **The manuscript is structurally incomplete and not in submission language throughout.**  
   Methods are largely in Indonesian, section 4.2 is only a heading and fragment, a figure reference is blank, and sentences at lines 60 and 64 are unfinished (`manuscript_text.md:60-64,72-82`). The text at line 52 promises a repository-organization Table 1, but the displayed Table 1 is the Specifications Table (`manuscript_text.md:21-32`); line 58 promises a split-count Table 2, but the displayed Table 2 is a model ranking (`manuscript_text.md:84-96`). This is not a complete editable English data article and is likely to be returned before scientific review.

5. **Known factual conflicts remain in core dataset claims.**  
   The manuscript says 209 sentences and exactly 25 readings per speaker (`manuscript_text.md:48,56`), whereas the authoritative registry says the public inventory has 213 category-sentence templates and four categories contain paired low-count replacement IDs (`EVIDENCE_REGISTRY.md:14,40`). The age range is 25–38 at line 54 but 22–38 at line 78, with neither range verified (`EVIDENCE_REGISTRY.md:39`). The abstract reports 132/104,500 as 0.129%, whereas it is 0.1263% (`manuscript_text.md:15`; `EVIDENCE_REGISTRY.md:12`). These are editor-visible integrity failures.

6. **Prior-publication overlap has not been cleared.**  
   The Specifications Table cites a related 2026 research article (`manuscript_text.md:32`), and the background says an earlier eight-category corpus was used in that work (`manuscript_text.md:48`). *Data in Brief* does not accept data already published in full or substantial part as supplementary material. Verify the cited article/DOI, document exactly which data were previously described or released, confirm that the present raw dataset was not already published in a disqualifying form, and explain any legitimate relationship without duplicate-publication claims.

### High — likely rejection or major revision if the submission passes intake

7. **Full-dataset and benchmark scopes are not bridged.**  
   The registry distinguishes 104,500 files/134.1762 h from a frozen benchmark of 102,544 files/130.6548 h, a difference of 1,956 rows (`EVIDENCE_REGISTRY.md:5-8`). The workflow explicitly prohibits scope mixing (`BMAD_SUPERPOWERS_WORKFLOW.md:14,19,45-51`), but the manuscript presents a nine-model table without identifying the benchmark scope or evaluation population (`manuscript_text.md:80-96`). Add an auditable scope-bridge table and label every count, figure, manifest, and benchmark result by scope.

8. **Synthetic repair design threatens interpretation of the split and benchmark.**  
   The manuscript places 122 synthetic files in training, 8 in development, and 2 in test (`manuscript_text.md:60`). The registry records two female-voice recordings targeting a male public speaker label (`EVIDENCE_REGISTRY.md:45`). Decide, document, and regenerate analyses after choosing whether to regenerate, exclude, or retain those files with explicit mismatch flags. Verify whether reuse of TTS voice identities across partitions affects acoustic speaker-disjointness; do not equate disjoint public target IDs with proven disjoint acoustic voices. Report a human-only sensitivity result or remove synthetic items from evaluation if scientifically appropriate.

9. **Collection, transcription, QC, and split methods are not reproducible.**  
   “Validated transcription” is asserted without a validation protocol (`manuscript_text.md:15`). Recruitment/sampling, inclusion/exclusion, prompts, repetition/replacement logic, recording session structure, normalization, segmentation, annotators, adjudication, error checks, and missing/corrupt-file handling are absent. Microphone model, 5–10 cm distance, Audacity version, room dimensions, and room protocol require confirmation against primary records (`manuscript_text.md:29,42,76`; `EVIDENCE_REGISTRY.md:42-43`). Seed 42 alone is insufficient: give the splitting algorithm, input speaker list, library/version, resulting manifests, and validation that public IDs do not cross splits.

10. **Privacy language and demographic/dialect claims are unsafe or unsupported.**  
    Calling participants “anonymous” (`manuscript_text.md:54`) is inappropriate for released voice recordings; coded records are at most pseudonymized, and voices retain re-identification risk. Regional-origin/dialect claims require a consent/privacy decision and verified public-safe table (`EVIDENCE_REGISTRY.md:41`). State how sex/gender was defined and collected, following relevant SAGER principles, and report sampling limitations. Do not infer dialect competence from origin or release granular locations unless justified, consented, and necessary.

11. **The value narrative overclaims representativeness.**  
    A controlled, scripted corpus from only 20 adults with repeated prompts cannot support an unqualified claim of realistic everyday-language representativeness merely because word frequencies resemble Zipf's law (`manuscript_text.md:36-40,48,66-70`). Limit claims to the observed population, scripted read-speech protocol, vocabulary/domain, recording environment, and regional-background coverage. Explain that balance by file count does not establish population representativeness or equal acoustic diversity.

12. **Technical validation is not defensible as presented.**  
    The nine-model table has no evaluation protocol, uncertainty, test size/scope, reference linkage, preprocessing controls, or leakage analysis (`manuscript_text.md:80-96`). Reframe benchmarking as data utility/technical validation, not primary novelty, as required by `BMAD_SUPERPOWERS_WORKFLOW.md:21-23`. Tie results only to the 102,544-file frozen scope, disclose the exact test manifest and synthetic-item handling, and avoid fair-speed claims across unequal hardware (`BMAD_SUPERPOWERS_WORKFLOW.md:70-83`). If these details cannot be supported, remove the ranking table rather than turning the data article into an underdocumented model paper.

### Important — package and presentation defects

13. **Title/abstract/keywords are not final.**  
    The title is concise but its expansion is awkward and does not clearly identify controlled read speech (`manuscript_text.md:3`). The extracted abstract is approximately 226 whitespace-delimited tokens, provisionally below the current 250-word maximum, but it contains the wrong synthetic percentage, treats the complete corpus as human-recorded, and states unproven transcript validation (`manuscript_text.md:15`). Keywords are blank although the guide requires 1–7 English keywords (`manuscript_text.md:17`). Recount in the final DOCX.

14. **Data-description inventory and figure/table source data are incomplete.**  
    No actual repository directory table or split-count table appears. Figure F1–F5 descriptions are compressed into long paragraphs, Figure 1's source-data sentence is unfinished, and the figures/captions themselves were not available for audit (`manuscript_text.md:52,58,64-70`). Provide a file-level inventory, formats/schema/data dictionary, checksums or integrity mechanism, split counts/hours, captions, editable tables, separate artwork, and openly deposited source values.

15. **References are incomplete or unverifiable in the reviewed extraction.**  
    Citations `[1]` and `[2]` appear without a reference list (`manuscript_text.md:48`), while model citations are absent from Table 2. Verify every citation and DOI; cite the dataset itself using the journal's dataset-reference format.

## Mandatory and author-owned declarations

| Item | Current status | Required action |
|---|---|---|
| **Data accessibility / dataset citation** | **FAIL** — placeholders; private HF; no persistent DOI | Deposit/link/cite the versioned dataset; ensure editor/reviewer access and compliant public availability; test access and include raw figure/table data. |
| **Ethics approval** | **FAIL** — committee/date/reference unverified | Insert only the actual committee/institution, decision, approval or exemption reference, date, and compliance statement. If none exists, seek formal institutional and journal guidance. |
| **Informed consent and privacy** | **FAIL** — public voice-release scope unverified | Verify retained written consent for participation, publication, repository distribution, and reuse of identifiable voice recordings and metadata; describe pseudonymization and residual risk. |
| **Dataset licence** | **FAIL** — `other` | Apply explicit terms consistent with consent, ownership, third-party rights, and repository requirements; distinguish data, code, and article licences. |
| **Corresponding author** | **FAIL** — malformed marker and no email | Designate one author and provide current email and required contact details; verify names, order, affiliations, and country names. |
| **CRediT author roles** | **MISSING** | Obtain all authors' approval for a role-by-role CRediT statement; do not infer roles. |
| **Funding and sponsor role** | **MISSING** | Provide funder and grant identifiers plus sponsor role, or the journal's no-specific-funding statement, only after author confirmation. |
| **Competing interests** | **MISSING** | Every author must complete the journal declarations process and approve the manuscript statement; do not assume “none.” |
| **Generative AI declaration** | **UNRESOLVED, conditional** | Authors must determine whether generative AI/AI-assisted tools were used in manuscript preparation. If used, add the journal-prescribed section before the references naming the tool/service, purpose, human review/editing, and author responsibility. If nothing qualifying was used, the current guide says no manuscript statement is needed, but record the author-attested decision. Basic spelling/grammar/reference tools are excluded. Edge-TTS used to create research data is a separate methods/reproducibility disclosure, not a substitute for the manuscript-preparation declaration. |
| **Acknowledgements** | **UNVERIFIED** | Name non-author assistance, including qualifying language/writing help, if applicable and permitted. |
| **Exclusive submission / all-author approval** | **UNVERIFIED** | Obtain explicit human confirmation that the manuscript is not under consideration elsewhere, that all authors approved the final version/order/declarations, and that only one journal will receive it. Submission remains a human action. |

## Prioritized author checklist

### P0 — stop-ship items

- [ ] **Ethics/consent dossier:** locate the primary ethics decision and written consent; verify public voice/data release, demographic fields, reuse, and withdrawal provisions. Record committee, date, and reference exactly. Escalate any absence to the institution and journal rather than drafting around it.
- [ ] **Repository release:** choose a suitable recognized repository, upload the complete dataset plus metadata, schema, manifests, scripts, and raw figure/table data; establish compliant reviewer access/public release; obtain and test the versioned persistent identifier from a clean browser session.
- [ ] **Rights/licence:** confirm author/institution ownership, participant permissions, sentence-text rights, and Edge-TTS redistribution terms; apply explicit compatible licences.
- [ ] **Single source of truth:** reconcile 104,500 full versus 102,544 benchmark files, 213 public versus 209 benchmark templates, natural versus synthetic counts, duration/storage, sex/gender labels, and the age range. Generate and cite a scope bridge; replace the false blanket “all sentences × 25” statement.
- [ ] **Synthetic repair decision:** resolve the two female-voice/male-target mismatches; assess test contamination and acoustic voice overlap; freeze new manifests and rerun all affected statistics/results.
- [ ] **Prior-publication check:** verify the 2026 related article and DOI, map overlap, and confirm that the raw data were not already published in full or substantial part as supplementary material.

### P1 — scientific and narrative rebuild

- [ ] Rewrite the complete manuscript in English using the latest *Data in Brief* data-article template; preserve explicit `[MATERIAL GAP]` fields until authors resolve them.
- [ ] Expand methods from primary records: recruitment/sampling, inclusion/exclusion, consent process, prompts/categories, recording sessions, equipment/settings, room, segmentation/normalization, transcript validation, QC sampling and its **n**, repair logic, Edge-TTS version/configuration/voices, and split algorithm/software/version.
- [ ] Replace “anonymous” with accurate pseudonymization language and add privacy/re-identification limitations. Remove granular regional metadata unless consented, verified, and scientifically necessary.
- [ ] Narrow the take-home message to a controlled Indonesian read-speech resource; remove unsupported “dialect,” “real-world,” and “representative of everyday language” conclusions.
- [ ] Add a repository inventory and data dictionary; restore the actual split-count table and correctly numbered figures/tables with captions and deposited source values.
- [ ] Either recast the nine-model benchmark as bounded technical validation of the frozen subset, with protocol and caveats, or remove it. Never mix deployment/OOD diagnostics with corpus accuracy.

### P2 — submission package

- [ ] Finalize a precise title, a fact-checked abstract under 250 words, and 1–7 English keywords.
- [ ] Complete the Data Accessibility, Ethics, Informed Consent, CRediT, Funding, Competing Interests, GenAI (if applicable), and Acknowledgements sections using author-attested facts.
- [ ] Designate the corresponding author; verify author spelling/order, affiliations, email/contact details, and all-author approval.
- [ ] Complete and cross-check the reference list, including the dataset citation, related article, methods/software, and model references actually retained.
- [ ] Inspect the final editable DOCX, separate artwork, captions, tables, supplementary files, permissions, disclosures, repository links, and current journal checklist. Re-extract the DOCX and rerun identifier/count checks before sign-off.
- [ ] Prepare a journal-specific cover letter only after the science/access/ethics gates pass; include truthful novelty/utility and fit, exclusivity, and all-author-approval statements. Confirm APC responsibility. Do not submit without explicit human authorization and never submit simultaneously elsewhere.

### P3 — editorial cleanup

- [ ] Standardize English, decimal separators (`104,500`, not `104.500`), units, capitalization, author punctuation, and terminology.
- [ ] Correct extraction-visible defects such as `mintnumber`, unfinished “provided in” sentences, the blank figure callout, and inconsistent `Figure`/`F` numbering.
- [ ] Split long interpretive paragraphs into self-contained data-description paragraphs and 3–5 concise *Value of the Data* bullets.

## Residual risks after the present audit

- The actual repository may differ from the registry; public accessibility, download integrity, file schemas, and licence text were not tested.
- The ethics/consent defect may be non-remediable if original consent did not authorize public distribution of voice biometrics; repository or licence changes alone cannot cure that problem.
- The extracted Markdown may omit content present in the source DOCX, but absent evidence cannot be credited. The final DOCX and generated PDF require separate inspection.
- Dataset ownership and third-party rights (sentence text and Edge-TTS output redistribution) remain unverified.
- Prior-publication overlap with the cited 2026 article remains unknown and could make the article out of scope.
- Split leakage, transcript correctness, audio QC, and all benchmark metrics remain unverified against primary artifacts.
- Journal instructions and templates can change; recheck them immediately before human-confirmed submission.

## Sign-off

The project has a plausible *Data in Brief* article after an evidence-led rebuild, but it **must not be represented as submission-ready** while public deposition/linking, ethics and voice-release consent, licence, scope reconciliation, synthetic-test handling, and mandatory author declarations remain unresolved. Formatting work should begin only alongside—not instead of—these threshold fixes.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "The audit records severity-ranked, line-addressable findings for Draft_Paper/01_Extraction/manuscript_text.md, Draft_Paper/02_Evidence/EVIDENCE_REGISTRY.md, and Draft_Paper/99_Admin/BMAD_SUPERPOWERS_WORKFLOW.md; it includes gate verdicts, desk-rejection blockers, an author checklist, and residual risks."
    }
  ],
  "changedFiles": [
    "Draft_Paper/03_Review/04_submission_readiness_review.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "Read the three specified Markdown sources with the file reader",
      "result": "passed",
      "summary": "Inspected the complete 96-line manuscript extraction, 45-line evidence registry, and 83-line workflow."
    },
    {
      "command": "rg -n targeted submission, ethics, access, licence, scope, synthetic-data, declaration, and manuscript-structure terms",
      "result": "passed",
      "summary": "Located concrete source lines for all material findings without scanning excluded dataset trees."
    },
    {
      "command": "wc and Python read-only checks for headings, abstract token estimate, placeholders, and percentages",
      "result": "passed",
      "summary": "Found an approximately 226-token abstract, blank keywords/placeholders, and confirmed 132/104,500 = 0.1263%."
    },
    {
      "command": "Web policy check of the current Elsevier Data in Brief Guide for Authors and data-suitability policy",
      "result": "passed",
      "summary": "Confirmed repository/data-linking, human-study ethics/consent, disclosure, abstract, keyword, and submission requirements on 2026-07-22."
    }
  ],
  "validationOutput": [
    "Overall decision: FAIL — not ready for submission.",
    "Critical blockers identified: repository/DOI access, ethics and public voice-release consent, licence, structural completeness, factual conflicts, and unresolved prior-publication overlap.",
    "Source manuscript, evidence registry, and workflow were not modified."
  ],
  "residualRisks": [
    "Repository contents, accessibility, integrity, and licence were not directly inspected.",
    "Ethics approval and consent for public release of identifiable voice recordings remain unverified and may be non-remediable.",
    "The source DOCX, primary records, figures, references, data files, and benchmark artifacts were outside this audit.",
    "Prior-publication overlap and third-party redistribution rights remain unresolved."
  ],
  "noStagedFiles": true,
  "diffSummary": "Created only the requested submission-readiness review artifact; no project source file was edited.",
  "reviewFindings": [
    "critical: Draft_Paper/01_Extraction/manuscript_text.md:31 and Draft_Paper/02_Evidence/EVIDENCE_REGISTRY.md:34-35 - dataset DOI/URL are placeholders and the evidenced HF repository is private.",
    "critical: Draft_Paper/02_Evidence/EVIDENCE_REGISTRY.md:37-38 - ethics approval and consent for public voice-biometric release are unverified.",
    "critical: Draft_Paper/02_Evidence/EVIDENCE_REGISTRY.md:15,36 - dataset licence is only 'other', so reuse rights are undefined.",
    "critical: Draft_Paper/01_Extraction/manuscript_text.md:60-96 - the manuscript is incomplete, partly Indonesian, and has missing/misnumbered tables and figures.",
    "critical: Draft_Paper/01_Extraction/manuscript_text.md:15,48,54-56,78 and Draft_Paper/02_Evidence/EVIDENCE_REGISTRY.md:39-40 - percentage, age, sentence-inventory, and repetition claims conflict.",
    "high: Draft_Paper/01_Extraction/manuscript_text.md:80-96 and Draft_Paper/02_Evidence/EVIDENCE_REGISTRY.md:5-8 - full-dataset and frozen-benchmark scopes are not separated in the benchmark presentation.",
    "high: Draft_Paper/01_Extraction/manuscript_text.md:60 and Draft_Paper/02_Evidence/EVIDENCE_REGISTRY.md:45 - synthetic files occur in evaluation splits and two voice/target labels mismatch.",
    "important: Draft_Paper/02_Evidence/EVIDENCE_REGISTRY.md:44 - corresponding-author email, CRediT roles, funding, and competing-interest confirmation are missing; GenAI use determination is also absent from the manuscript."
  ],
  "manualNotes": "Submission/resubmission was not attempted. All author-owned declarations must be confirmed by humans; no missing fact was inferred or fabricated."
}
```
