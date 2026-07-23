# Material-Gap Placeholders for the Internal Manuscript

**Status:** author/institution input form; **NOT FOR SUBMISSION**

**Evidence companions:** [`Draft_Paper/02_Evidence/METHODS_EVIDENCE_MATRIX.csv`](../02_Evidence/METHODS_EVIDENCE_MATRIX.csv) classifies current claims as OBSERVED, INFERRED, CONFLICTED, or MISSING; [`Draft_Paper/02_Evidence/AUTHOR_METHODS_EVIDENCE_QUESTIONNAIRE.md`](../02_Evidence/AUTHOR_METHODS_EVIDENCE_QUESTIONNAIRE.md) provides bilingual closure questions and secure-response fields.

The manuscript builder must insert the following tokens verbatim until documentary evidence and author approval are available. Empty or generic boilerplate must not be substituted.

| Token | Required evidence/decision | Submission impact |
|---|---|---|
| `[MATERIAL GAP: corresponding author name and current email]` | Author-approved corresponding author and current contact details | Mandatory title-page field |
| `[MATERIAL GAP: final author order and affiliations]` | All-author approval and verified institutional names/addresses | Mandatory title-page field |
| `[MATERIAL GAP: participant recruitment and inclusion/exclusion]` | Primary protocol or author-attested contemporaneous record | Methods reproducibility |
| `[MATERIAL GAP: participant age or approved omission]` | Authoritative public-safe source and consent/privacy approval | Remove age if unverifiable/unnecessary |
| `[MATERIAL GAP: sex/gender label definition and provenance]` | Whether labels were self-described, administratively recorded, or inferred; author/privacy approval | Required for precise demographic reporting |
| `[MATERIAL GAP: recording dates and session protocol]` | Primary collection log/protocol | Methods reproducibility |
| `[MATERIAL GAP: verified room dimensions and treatment]` | Primary record resolving text/diagram conflict | Omit if unresolved |
| `[MATERIAL GAP: verified microphone, interface, operating system, and recording software/version]` | Primary equipment/software record | Omit exact values if unresolved |
| `[MATERIAL GAP: microphone distance, gain/calibration, monitoring, and prompt presentation]` | Primary collection protocol | Omit exact values if unresolved |
| `[MATERIAL GAP: repetition, replacement, re-recording, and rejection rules]` | Collection/QC record explaining partial replacement pairs, observed rejection/re-record counts, direct decoder/header integrity checks, and any listening/alignment audit design/results (closure sub-gate `SG-AUDIO-QC`) | Core corpus-construction and direct quality-control method |
| `[MATERIAL GAP: transcript source and normalization specification]` | Published transcript rules plus executable transcript/metadata builder, schema, field provenance, units/nullability, software environment, input hashes, and validation assertions (closure sub-gate `SG-METADATA-BUILD`) | Required before transcripts and technical metadata are fully reproducible |
| `[MATERIAL GAP: transcript-repair algorithm, join keys, manifest hashes, and audio-text audit result]` | Script, source inventory, immutable manifest, automated checks, listening-audit design/result | Do not use “validated transcripts” without it |
| `[MATERIAL GAP: split-generation algorithm, candidate order, library/version, and exact assignments]` | Generator and fixed manifests | Seed 42 alone is insufficient |
| `[MATERIAL GAP: exact benchmark template-overlap audit]` | Pinned frozen-manifest overlap report plus complete per-recipe method cards, atomic checkpoint/tokenizer/prediction hashes, scorer/normalizer implementation and environment, synthetic-excluded sensitivity, uncertainty, and error-analysis attachments (closure sub-gate `SG-BENCHMARK-METHODS`) | Required before exact overlap wording or main-text promotion of the nine-model display |
| `[MATERIAL GAP: 297-file sampling frame, allocation, seed, and inclusion criteria]` | Sampling code/manifest | Use “sampled,” not “stratified,” until supplied |
| `[MATERIAL GAP: disposition of two female-source/male-target synthetic rows]` | Author decision: regenerate, exclude, or retain with explicit flags | May change data/manifests/results |
| `[MATERIAL GAP: Edge-TTS version/date/configuration and redistribution-rights review]` | Generation record and legal/terms review | Required for reproducibility and licence compatibility |
| `[MATERIAL GAP: ethics committee/determination, reference number, and date]` | Primary approval, exemption, or waiver record | Fatal submission/release blocker |
| `[MATERIAL GAP: informed-consent procedure and exact public voice-release/reuse scope]` | Retained consent or documented lawful basis approved by the institution | Fatal submission/release blocker |
| `[MATERIAL GAP: demographic minimization and public-schema decision]` | Institutionally approved fields, aggregation/suppression, and provenance | Fatal privacy/release blocker |
| `[MATERIAL GAP: data controller/contact, crosswalk retention, withdrawal, takedown, breach, versioning, and maintenance policy]` | Approved lifecycle governance document | Release blocker |
| `[MATERIAL GAP: final whole-package identity/leakage audit]` | Audit covering archive paths, metadata, images/OCR, document properties, PDF internals, logs/notebooks, audio tags, and embedded paths | Release blocker |
| `[MATERIAL GAP: prompt-text, audio, metadata, code, and synthetic-output rights clearance]` | Ownership and third-party rights review | Release/licence blocker |
| `[MATERIAL GAP: exact dataset licence or component-specific licences]` | Author/institution/legal approval consistent with consent and third-party rights | Fatal reuse/submission blocker |
| `[MATERIAL GAP: repository, exact version, persistent DOI, direct URL, checksums, and access date]` | Final frozen deposit, complete relative-path/SHA-256 manifest, direct package-wide decode/header/readability result, environment locks, and clean-session access test | Fatal Data Availability and final-package reproducibility blocker |
| `[MATERIAL GAP: approved controlled-access mechanism, if applicable]` | Institution/journal-approved sensitive-data route and editor/reviewer access | Do not assume eligibility |
| `[MATERIAL GAP: related 2026 article citation and data/result overlap assessment]` | Verified DOI/citation, release chronology, itemized overlap, eligibility conclusion | Potential fatal prior-publication blocker |
| `[MATERIAL GAP: CRediT roles approved by every author]` | Role-by-role author approval | Mandatory declaration |
| `[MATERIAL GAP: funding and sponsor role]` | Funder/grant and sponsor-role confirmation, or author-approved no-specific-funding statement | Mandatory declaration |
| `[MATERIAL GAP: competing-interest declaration approved by every author]` | Completed author declarations | Mandatory declaration |
| `[MATERIAL GAP: acknowledgements]` | Author-approved non-author assistance and permissions | End matter |
| `[MATERIAL GAP: GenAI manuscript-preparation determination and declaration]` | Author attestation and current Elsevier-compliant wording if applicable | Mandatory when applicable |
| `[MATERIAL GAP: all-author approval, exclusivity, and explicit submission authorization]` | Written human confirmation | Submission must not proceed without it |

## Fixed-token closure sub-gates

The project intentionally retains the fixed set of 33 canonical tokens. Scientific gaps that need finer tracking are mandatory closure sub-gates under those tokens, not new aliases:

- `SG-METADATA-BUILD` → transcript-source/normalization token;
- `SG-AUDIO-QC` → repetition/re-recording/rejection token and final repository/checksum evidence;
- `SG-BENCHMARK-METHODS` → exact benchmark template-overlap token.

A parent token cannot close while any of its sub-gates is open. The questionnaire and evidence matrix must name the parent token and sub-gate explicitly.

## Prohibited substitutions

Do not replace any token with:

- “Ethical approval was not required” without a competent, documented determination;
- “informed consent was obtained” without retained evidence and verified release scope;
- “the authors declare no conflict” without every author’s approval;
- “no funding” without author confirmation;
- a guessed licence or DOI;
- a guessed age range, room dimension, microphone, distance, software version, or protocol;
- “anonymous” or “fully anonymized” for raw voice;
- regional/dialect claims inferred from unverified locality fields;
- a private HF URL presented as compliant public availability.

## Closure notation

When evidence is supplied, record:

```text
Token:
Decision/evidence owner:
Primary artifact:
Artifact date:
SHA-256:
Approved wording:
Approved by:
Approval date:
Downstream files regenerated:
```

A token is closed only after the primary artifact and approval are recorded and all affected counts, displays, manuscript text, and package files are regenerated and re-audited.
