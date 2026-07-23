# Privacy, Ethics, and Responsible-Release Audit

## Review

- **Correct:** The staging repository remains private and explicitly says release must wait for consent and licensing checks ([`Draft_Paper/02_Evidence/hf_remote_snapshot/README.md:10-18`](../02_Evidence/hf_remote_snapshot/README.md#L10-L18)).
- **Correct:** Public human labels are bounded to `M1..M12` and `F1..F8`; the current synthetic inventory is `Ms1..Ms9` and `Fs1..Fs9`, and the private crosswalk is excluded from the manuscript package ([`Draft_Paper/02_Evidence/evidence_registry.json:717-722`](../02_Evidence/evidence_registry.json#L717-L722)). The README states the same human-label policy and uses only `Ms*`/`Fs*` for synthetic sources ([`Draft_Paper/02_Evidence/hf_remote_snapshot/README.md:22-31`](../02_Evidence/hf_remote_snapshot/README.md#L22-L31)).
- **Correct:** The public schema distinguishes acoustic source, source gender, synthetic status, and repair target rather than silently attributing synthetic audio to a human ([`Report_paper_9model/hf_anonymization/hf_public_metadata_schema.md:3-14`](../../Report_paper_9model/hf_anonymization/hf_public_metadata_schema.md#L3-L14)). The manuscript also discloses the synthesis provider, voice types, count, splits, and that cloning was not used ([`Draft_Paper/01_Extraction/manuscript_text.md:52-62`](../01_Extraction/manuscript_text.md#L52-L62)).
- **Correct, with scope limit:** The supplied cleanup report records zero errors across 92 filenames, 36 text files, and 23 extractable PDFs ([`reports/public_artifact_anonymization_cleanup_20260619.md:82-102`](../../reports/public_artifact_anonymization_cleanup_20260619.md#L82-L102)). It does not establish that all release artifacts are clean: PNG pixel text was not OCR-scanned ([`reports/public_artifact_anonymization_cleanup_20260619.md:104-108`](../../reports/public_artifact_anonymization_cleanup_20260619.md#L104-L108)).
- **Blocker — Critical:** Public-release consent for identifiable voice biometrics is unverified ([`Draft_Paper/02_Evidence/evidence_registry.json:728-729`](../02_Evidence/evidence_registry.json#L728-L729)). Pseudonymous labels do not anonymize a voice. Each human contributes roughly 5,225 recordings and several hours of repeated speech ([`Draft_Paper/01_Extraction/manuscript_text.md:54-66`](../01_Extraction/manuscript_text.md#L54-L66)), enabling speaker embeddings, cross-dataset linkage, recognition, and possible voice-cloning misuse. Do not make the repository public until written consent or another valid, documented legal/ethical basis explicitly covers public audio release and foreseeable reuse.
- **Blocker — Critical:** Ethics oversight is unverified: committee name, decision/reference, and date are missing ([`Draft_Paper/02_Evidence/evidence_registry.json:724-729`](../02_Evidence/evidence_registry.json#L724-L729)), and the manuscript has no ethics/consent section in its collection methods ([`Draft_Paper/01_Extraction/manuscript_text.md:72-82`](../01_Extraction/manuscript_text.md#L72-L82)). Obtain and accurately report prospective approval/exemption/waiver evidence; do not imply approval or seek a retrospective number merely for publication.
- **Blocker — High:** The release license is unresolved (`license: other`) ([`Draft_Paper/02_Evidence/hf_remote_snapshot/README.md:1-18,100-104`](../02_Evidence/hf_remote_snapshot/README.md#L1-L18); [`Draft_Paper/02_Evidence/evidence_registry.json:448-452,727`](../02_Evidence/evidence_registry.json#L448-L452)). License terms must be compatible with participant consent, synthetic-voice provider terms, and intended downstream use. Broad reuse claims cannot precede that determination.
- **Blocker — High:** The manuscript calls speakers and metadata “anonymous/anonymized” and describes “speaker identity” ([`Draft_Paper/01_Extraction/manuscript_text.md:15,48,52-56`](../01_Extraction/manuscript_text.md#L15)). This is materially misleading because the audio is inherently linkable and IDs are stable. Replace with “pseudonymous public speaker ID” and state that re-identification risk remains.
- **Blocker — High:** Fine-grained regional-origin metadata creates a strong quasi-identifier when combined with age, gender, accent, split, duration, and raw voice. The manuscript lists many specific localities and says the per-speaker table maps demographics and regional background ([`Draft_Paper/01_Extraction/manuscript_text.md:54`](../01_Extraction/manuscript_text.md#L54)). The evidence registry says these claims still require a consent/privacy decision and verified public-safe table ([`Draft_Paper/02_Evidence/evidence_registry.json:730-732`](../02_Evidence/evidence_registry.json#L730-L732)). Remove per-speaker region unless explicitly consented and necessary; otherwise aggregate to a defensible coarse level and suppress rare cells.
- **Blocker — High:** No withdrawal, retention, deletion, breach/takedown, versioning, or maintenance policy is evidenced in the manuscript or dataset card. Before release, designate a data controller/contact, define crosswalk access and retention, document how participants may request withdrawal, and explain the practical limit that already-downloaded copies and trained models may not be retractable.
- **Blocker — High:** The public-release package still requires a final whole-package leakage audit. Existing audit coverage is limited and explicitly excludes OCR of PNG pixels ([`reports/public_artifact_anonymization_cleanup_20260619.md:104-107`](../../reports/public_artifact_anonymization_cleanup_20260619.md#L104-L107)). Audit metadata values, filenames, archive member paths, embedded document properties, PDF layers/attachments, images with OCR/manual inspection, notebooks/logs, audio tags, and path strings. Keep the crosswalk outside version control and public archives as required by `evidence_registry.json:720`.
- **Blocker — High:** Two synthetic female-source files target a male public label ([`Draft_Paper/02_Evidence/evidence_registry.json:722,736`](../02_Evidence/evidence_registry.json#L722)). Both schema and README say mismatches require review ([`Report_paper_9model/hf_anonymization/hf_public_metadata_schema.md:14`](../../Report_paper_9model/hf_anonymization/hf_public_metadata_schema.md#L14); [`Draft_Paper/02_Evidence/hf_remote_snapshot/README.md:100-102`](../02_Evidence/hf_remote_snapshot/README.md#L100-L102)). Regenerate or exclude them, or retain only with explicit row-level flags and a manuscript limitation; verify that no synthetic row is presented as the human target’s voice.
- **Blocker — High (release readiness):** The repository is private and no persistent dataset DOI is available ([`Draft_Paper/02_Evidence/evidence_registry.json:724-727`](../02_Evidence/evidence_registry.json#L724-L727); [`Draft_Paper/01_Extraction/manuscript_text.md:31`](../01_Extraction/manuscript_text.md#L31)). Resolve accessibility only after the privacy/ethics gates above; do not publish merely to satisfy the placeholder.
- **Note — Medium:** Age is inconsistent: 25–38 in the data description versus 22–38 in the methods ([`Draft_Paper/01_Extraction/manuscript_text.md:54,78`](../01_Extraction/manuscript_text.md#L54)), and no authoritative public-safe source exists ([`Draft_Paper/02_Evidence/evidence_registry.json:730`](../02_Evidence/evidence_registry.json#L730)). Verify before any demographic disclosure; use a coarser range if adequate.
- **Note — Medium:** The phrase “independent speaker evaluation” is ambiguous and can sound like speaker-identification reuse ([`Draft_Paper/01_Extraction/manuscript_text.md:15`](../01_Extraction/manuscript_text.md#L15)). If the intent is ASR generalization, use “speaker-independent ASR evaluation.”
- **Note — Medium:** Reuse claims span “various speech processing applications,” voice interfaces, and real-time service robots without responsible-use limits ([`Draft_Paper/01_Extraction/manuscript_text.md:15,36-40`](../01_Extraction/manuscript_text.md#L15)). Add explicit exclusions for re-identification, biometric enrollment/authentication, surveillance, voice cloning/impersonation, demographic or origin inference, harassment, and decisions about individuals. Do not claim that a license alone prevents misuse.
- **Note — Medium:** Synthetic disclosure is strong but internally inconsistent: 0.129% in the abstract versus 0.126% in the body; registry evidence supports 0.1263% ([`Draft_Paper/01_Extraction/manuscript_text.md:15,52-60`](../01_Extraction/manuscript_text.md#L15); [`Draft_Paper/02_Evidence/evidence_registry.json:268-289`](../02_Evidence/evidence_registry.json#L268-L289)). Use one denominator and value, explain that synthetic test rows can affect evaluation, and document provider/version/date and redistribution rights.
- **Note — Medium:** Sex/gender labels are presented as “corrected/inferred” without provenance in the schema ([`Report_paper_9model/hf_anonymization/hf_public_metadata_schema.md:5-12`](../../Report_paper_9model/hf_anonymization/hf_public_metadata_schema.md#L5-L12)). State whether labels are self-described, administratively recorded, or inferred; avoid treating perceived vocal characteristics as gender identity.

## Red-team risk register

| ID | Severity | Threat / affected parties | Evidence and plausible harm | Required control | Release status |
|---|---|---|---|---|---|
| R1 | Critical | Voice re-identification, linkage, cloning; participants | Stable labels plus hours of raw speech per person (`manuscript_text.md:54-66`) permit biometric matching even without names. | Verify explicit public voice-release consent; call data pseudonymous; document residual risk and prohibited uses. | **Blocker** |
| R2 | Critical | Non-consensual secondary use; participants | Consent scope is explicitly unverified (`evidence_registry.json:729`). | Confirm consent covers public worldwide access, raw audio, transcripts/metadata, research/commercial scope as applicable, derivatives, model training, and foreseeable biometric risk; otherwise restrict access or do not release affected audio. | **Blocker** |
| R3 | High | Ethical/legal noncompliance | Oversight details are unverified (`evidence_registry.json:728`); manuscript lacks a statement. | Verify and report approval/exemption/waiver and collection dates; align release with institutional requirements. | **Blocker** |
| R4 | High | Demographic/regional triangulation and stereotyping | Fine localities, age, gender, accent, and public speaker mapping are proposed (`manuscript_text.md:54`). | Data-minimization review; remove per-speaker region or aggregate/suppress; disclose non-representativeness. | **Blocker** |
| R5 | High | Identity leakage from release artifacts | Prior audit is clean for tested surfaces but did not OCR PNGs (`cleanup_20260619.md:82-107`). | Run a final archive-wide public-safe audit including images, metadata, archive paths, tags, and document internals. | **Blocker** |
| R6 | High | Unauthorized/unclear reuse | License remains `other` (`README.md:10,104`). | Approve exact terms after consent/provider-rights review; add citation and acceptable-use guidance. | **Blocker** |
| R7 | High | Irreversible dissemination after withdrawal | No lifecycle/takedown policy is documented. | Publish controller/contact, retention and crosswalk controls, withdrawal process, version/tombstone policy, and limits after redistribution/model training. | **Blocker** |
| R8 | High | Synthetic/human attribution error and gender-label harm | Two source/target mismatches exist (`evidence_registry.json:722,736`). | Regenerate/exclude or explicitly flag and explain; preserve distinct `speaker_type` and synthetic source IDs. | **Blocker** |
| R9 | Medium | Unsafe downstream biometric or surveillance use | Manuscript advertises broad speech/robotics reuse (`manuscript_text.md:15,36-40`). | Bound intended uses; add misuse warnings and no-endorsement language; consider gated access if consent is narrower than open release. | Open |
| R10 | Medium | Misleading privacy representation | “Anonymous/anonymized” conflicts with stable IDs and raw biometrics (`manuscript_text.md:48-56`). | Use “pseudonymized/pseudonymous”; explain that IDs protect direct names but not voice identifiability. | Open |
| R11 | Medium | Synthetic provenance/licensing and evaluation ambiguity | Provider voices are disclosed, but rights/version are not; synthetic rows occur in dev/test (`manuscript_text.md:60`). | Confirm redistribution terms, pin provenance, label every row, provide filtering instructions, and report human-only sensitivity metrics where feasible. | Open |
| R12 | Medium | Demographic misclassification | Public source-gender is described as corrected/inferred (`hf_public_metadata_schema.md:7`). | Document provenance and limitations; avoid identity claims from acoustic perception. | Open |

## Required manuscript caveats

1. **Privacy/identifiability:** “Speaker IDs are pseudonymous, not anonymous. Speech is a biometric signal and may permit recognition or linkage to recordings outside this dataset. Direct identifiers and the private crosswalk are not released, but residual re-identification risk remains.”
2. **Consent and oversight:** State the verified committee/determination, reference/date, collection consent procedure, and exact consent scope for public audio, metadata, derivative models, and applicable reuse. If any item is unavailable, say so and restrict release rather than infer permission.
3. **Data minimization:** Explain which demographic fields are released and why. Do not publish per-speaker fine-grained region/age combinations without explicit scope and a documented re-identification assessment.
4. **Responsible use:** Limit endorsed use to consent- and license-compatible speech/ASR research. State that the dataset is not intended for identity recognition, biometric enrollment/authentication, surveillance, impersonation/voice cloning, demographic profiling, or decisions about individuals.
5. **Synthetic audio:** State the exact count/fraction (132/104,500; 0.1263%), provider voices, absence of speaker cloning, row-level source labels, split counts including two test rows, and treatment of the two gender-mismatched repair targets. Explain how users can exclude synthetic rows.
6. **Withdrawal and lifecycle:** Give a contact and process, crosswalk-retention/access policy, dataset versioning/takedown plan, expected maintenance period, and the limitation that external copies and models may be impossible to retract.
7. **Demographic limitations:** Resolve the age conflict and explain that 20 controlled-recording speakers do not support population-level conclusions about Indonesian regions, dialects, sex/gender, or real-world deployment fairness.
8. **Terminology:** Replace “speaker identity” with “public speaker ID,” “anonymous/anonymized” with “pseudonymous/pseudonymized,” and “independent speaker evaluation” with “speaker-independent ASR evaluation.”

## Public-safe identifier check

A targeted check of only the five authorized inputs found no explicit speaker-label token outside the permitted human ranges or current synthetic inventory. Apparent tokens such as `F11` in the cleanup report are figure identifiers, not speaker IDs ([`reports/public_artifact_anonymization_cleanup_20260619.md:55-60`](../../reports/public_artifact_anonymization_cleanup_20260619.md#L55-L60)). No private crosswalk was searched and no respondent name is reproduced here. This is **not** an attestation for uninspected release files; the final release-package audit remains a blocker.

## Release decision

**DO NOT RELEASE publicly.** Critical consent and ethics evidence is absent, licensing is unresolved, the manuscript overstates anonymity, detailed demographics need minimization, lifecycle governance is missing, synthetic mismatches remain unresolved, and the prior leakage audit has known coverage limits. Keeping the HF staging repository private is the correct current control.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Concrete privacy/ethics findings and residual risks are severity-ranked with line-specific citations across the manuscript, evidence registry, HF snapshot README, public metadata schema, and anonymization cleanup report."
    }
  ],
  "changedFiles": [
    "Draft_Paper/03_Review/05_privacy_ethics_review.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "Read the five user-authorized source/evidence files with targeted line ranges",
      "result": "passed",
      "summary": "Reviewed manuscript, evidence registry, staged dataset card, public metadata schema, and cleanup audit without searching private crosswalks."
    },
    {
      "command": "Targeted explicit public-label token validation over the five authorized inputs",
      "result": "passed",
      "summary": "No speaker-label token outside M1..M12, F1..F8, Ms1..Ms9, or Fs1..Fs9; F11 was verified contextually as a figure identifier."
    },
    {
      "command": "Targeted consent/ethics/privacy/retention/license keyword review of manuscript and HF README",
      "result": "passed",
      "summary": "Confirmed that release gating is acknowledged in the README but substantive consent, ethics, withdrawal, retention, and maintenance disclosures are absent from the manuscript."
    },
    {
      "command": "git diff --cached --name-only",
      "result": "passed",
      "summary": "No staged files were reported before writing the required review artifact."
    }
  ],
  "validationOutput": [
    "Current evidence explicitly marks the HF repository private and license as other.",
    "Evidence registry marks ethics approval details and written consent for public voice-biometric release as unverified.",
    "Existing anonymization audit reports zero errors on tested text/PDF/filename surfaces but explicitly did not OCR PNG pixels.",
    "Final decision: public release blocked."
  ],
  "residualRisks": [
    "Raw voice remains biometrically linkable despite pseudonymous labels.",
    "Consent scope and ethics determination are unverified.",
    "Fine-grained region, age, gender, accent, and stable speaker IDs may enable triangulation.",
    "Whole-package leakage audit, including OCR and embedded metadata/archive paths, is not evidenced.",
    "License, provider redistribution rights, withdrawal, retention, takedown, and maintenance governance remain unresolved.",
    "Two synthetic voice/repair-target gender mismatches remain unresolved."
  ],
  "noStagedFiles": true,
  "diffSummary": "Created only the required review artifact; no project source or evidence file was modified.",
  "reviewFindings": [
    "critical blocker: Draft_Paper/02_Evidence/evidence_registry.json:728-729 - ethics details and written consent for public identifiable voice-biometric release are unverified.",
    "high blocker: Draft_Paper/01_Extraction/manuscript_text.md:48-56 - raw voice with stable IDs and detailed demographics is incorrectly called anonymous/anonymized.",
    "high blocker: Draft_Paper/02_Evidence/hf_remote_snapshot/README.md:10-18,104 - release license is unresolved and the repository correctly remains private.",
    "high blocker: reports/public_artifact_anonymization_cleanup_20260619.md:104-107 - prior leak audit did not OCR PNG pixel text.",
    "high blocker: Draft_Paper/02_Evidence/evidence_registry.json:722,736 - two synthetic source/repair-target gender mismatches require resolution.",
    "no prohibited respondent label was found in the five authorized inputs; no private crosswalk was searched."
  ],
  "manualNotes": "The identifier validation is scoped only to the five authorized inputs and must not be treated as a complete public-package audit."
}
```
