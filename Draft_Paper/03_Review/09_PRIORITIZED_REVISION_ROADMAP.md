# Prioritized Revision Roadmap

## Objective

Rebuild the source DOCX into an internally auditable English *Data in Brief* working manuscript while preventing unresolved author-owned facts from becoming claims. Public release and submission remain gated.

## Gate model

| Gate | Pass condition | Current state |
|---|---|---|
| G0 — Ethical releasability | Verified ethics determination and consent/lawful basis covering the intended voice and metadata release | **NO-GO** |
| G1 — Rights and privacy | Compatible data/code/text/TTS rights; approved demographic minimization; lifecycle and leakage controls | **NO-GO** |
| G2 — Data freeze | Synthetic decision complete; both manifests and hashes frozen; scope bridge and repair provenance audited | **NO-GO** |
| G3 — Reproducibility | Collection, transcript, QC, split, sampled diagnostics, and retained benchmark methods supported by primary evidence | **NO-GO** |
| G4 — Access and citation | Exact frozen package, explicit licence, persistent identifier, and tested reviewer/public access | **NO-GO** |
| G5 — Manuscript and package | Complete English data article, bounded claims, declarations, references, figures/tables, and final integrity audit | **NO-GO** |
| G6 — Submission authority | All-author approval, exclusivity, and explicit human authorization | **UNASSESSED** |

**Submission may be declared GO only after G0–G6 all pass.** Internal drafting may proceed with visible `[MATERIAL GAP]` markers.

## Dependency graph

```text
Ethics/consent ─┐
Rights/licence ─┼─> release model and permitted public schema ─┐
Privacy policy ─┘                                              │
Prior-publication review ───────────────────────────────────────┤
Synthetic-row decision ─────────────────────────────────────────┤
                                                               v
         authoritative release-target + benchmark data freeze
                               |
                               v
      direct audits, regenerated statistics, tables, and figures
                               |
Primary acquisition records ──┼──> reproducible Methods
Repair/normalization evidence ─┤
Benchmark protocol evidence ───┘
                               |
                               v
               complete English working manuscript
                               |
                               v
whole-package privacy audit -> exact repository deposit -> DOI/access test
                               |
                               v
author declarations -> final DOCX/package QA -> explicit human submission approval
```

## Stage 0 — Hold and terminology correction

**May start immediately.**

### Actions

- Keep HF private and freeze submission activity.
- Use “104,500-row release-target corpus/HF metadata snapshot,” not “public corpus.”
- Use “102,544-row frozen benchmark” for all nine-model results.
- Mark all internal draft outputs **NOT FOR SUBMISSION**.
- Keep the private crosswalk outside Git, HF, and manuscript artifacts.

### Exit evidence

- Working documents distinguish data scope, accessibility state, and benchmark scope.
- No internal artifact claims public availability, DOI, approved licence, ethics, or consent.

## Stage 1 — Resolve fatal author/institution facts

**Parallel owner work; highest priority.**

### Workstreams

1. **Ethics and consent:** locate approval/exemption/waiver and retained consent; verify exact public voice, metadata, derivative, redistribution, training, and withdrawal scope.
2. **Rights and licence:** review ownership, prompt-text rights, Edge-TTS redistribution terms, and component-specific licences.
3. **Privacy governance:** decide public demographic fields, controller/contact, crosswalk retention/access, withdrawal, takedown, breach, versioning, and maintenance.
4. **Prior publication:** verify the related article/DOI and map data, methods, and benchmark overlap.
5. **Author facts:** collect author order/affiliations, corresponding author, CRediT, funding, competing interests, acknowledgements, and GenAI-use determination; these may be finalized later but should be requested now.

### Stop rule

If consent or rights do not support the access required by *Data in Brief*, stop the open-audio article route and seek institutional/journal guidance. Do not publish simply to fill the manuscript placeholder.

### Exit gate

**G0 and the release-basis portion of G1 pass.**

## Stage 2 — Make data decisions and freeze evidence

### Actions

- Decide whether the two female-source/male-target synthetic rows will be regenerated, excluded, or retained with explicit flags.
- Freeze the release-target and benchmark row manifests separately.
- Create the authoritative 1,956-row scope/repair bridge.
- Archive the 213 distinct `(category, sentence_id)` inventory; preserve original numbering gaps and replacement IDs.
- Build a source-priority table that blacklists stale gender fields and the stale Whisper-medium label.
- Generate SHA-256 values for all manuscript evidence inputs.
- Update the claim–evidence matrix with publication-safe wording and access status.

### Exit gate

**G2 passes:** row counts, duration, split counts, templates/pairs, repairs, synthetic status, and provenance reconcile under immutable manifests and hashes.

## Stage 3 — Run direct audits and refresh analyses

**These tasks may run in parallel after Stage 2.**

### Required audits

1. Full release-target audio-header/integrity audit for 16-kHz, mono, PCM16 and file readability.
2. Transcript-repair reconstruction and sampled audio–text validation.
3. Split-generation and template-overlap audit.
4. Corrected source-gender and synthetic composition by split.
5. The 297-file sample frame, allocation, seed, manifest, and metric-generation audit.
6. Whole-release clipping/integrity scan and a documented listening audit if feasible.
7. Human-only and synthetic-test-excluded benchmark sensitivity calculations.
8. Regeneration of all affected statistics, editable tables, and public-safe figures.

### Exit evidence

- Each manuscript claim has a scope-matched, hashed source artifact.
- No sampled result is generalized to the whole corpus.
- No benchmark result is presented without its exact manifest and synthetic treatment.

## Stage 4 — Reconstruct Methods and bound technical validation

### Dataset Methods

Document, from primary records:

- recruitment, inclusion/exclusion, and consent procedure;
- prompt/category design and original numbering;
- verified equipment, software, room, distance, and settings;
- session organization, prompt order, repetition/replacement logic, and speaker instructions;
- segmentation, naming, re-record/rejection criteria, and missing-file handling;
- transcript source, normalization, validation, and the post-freeze repair;
- Edge-TTS generation, voices, configuration, provenance, filtering, and QC;
- split generation and validation;
- data-quality diagnostics and their sampling limitations;
- packaging, checksums, schema, and versioning.

Unverified fields remain `[MATERIAL GAP]` or are removed.

### Technical validation

- Keep the benchmark subordinate to data utility.
- State 102,544 files and the 15,376-item test split explicitly.
- State 15,374 human + 2 synthetic test items.
- Describe human speaker separation and seen-script overlap separately.
- Use the corrective uniform diagnostic rescore in [`Draft_Paper/02_Evidence/unified_benchmark_rescore/`](../02_Evidence/unified_benchmark_rescore); do not use the historical run-native ranking because its reference normalizations and denominators differed.
- Provide complete retained model/evaluation details and scoring rules, including the canonical manifest, normalizer, shared denominators, and prediction hashes.
- Report uniform-rescore WER/CER as percentages with declared rounding and state that existing predictions were rescored without rerunning inference.
- Do not include a performance-rank column or compare heterogeneous hardware times as controlled efficiency.
- Label the one-epoch L4 run as an execution smoke test only.
- Move the full nine-model protocol/results to the supplement or retain a smaller utility demonstration if method-card evidence remains inadequate.

### Exit gate

**G3 passes** for every method and result retained in the article.

## Stage 5 — Rebuild the English manuscript

### Proposed order

1. Title and abstract.
2. Keywords.
3. Specifications Table.
4. Value of the Data bullets.
5. Background.
6. Data Description.
7. Experimental Design, Materials and Methods.
8. Technical Validation.
9. Limitations and Responsible Use.
10. Ethics and Consent.
11. Data Availability.
12. CRediT, Funding, Competing Interests, Acknowledgements, and GenAI declaration as applicable.
13. References.

### Mandatory narrative controls

- Central story: controlled Indonesian closed-prompt read speech with explicit human/synthetic provenance and reproducible manifests.
- One scope bridge appears before technical validation.
- No claim of national/dialect representativeness, natural conversation, everyday-language representativeness, gender robustness, unseen-text performance, or field accuracy.
- “Pseudonymous,” never “anonymous,” for public IDs.
- Deployment appears, if at all, only as a bounded reuse example or future-validation need.

### Main text / supplement / exclusion rule

- **Main text:** release-target inventory, scope bridge, schema, split composition, synthetic disclosure, limited data-quality evidence, concise benchmark validation, and limitations.
- **Supplement:** full per-category/per-speaker tables, 213-pair inventory, detailed repair manifest/method, all nine model cards/results, direct audit reports, and additional figures.
- **Exclude:** private crosswalk, names, unsupported demographics/acquisition facts, cross-hardware efficiency rankings, OOD/Whisper pseudo-label accuracy, and deployment claims presented as validation.

### Exit gate

Stage 4.5 integrity review: every quantitative, ethical, access, and generalization statement is checked against the evidence registry and material-gap ledger.

## Stage 6 — Build and validate the release/submission package

### Actions

- Complete the whole-package leakage audit, including OCR/manual image checks and DOCX properties.
- Deposit the exact ethics/rights-approved data version and mint the persistent identifier.
- Verify data, licence, revision, citation, checksums, and manuscript references agree.
- Test repository access from a non-privileged clean session.
- Generate the editable DOCX and, in an environment with a renderer, inspect the page-level PDF.
- Re-extract the final DOCX and compare text, tables, figures, references, properties, and identifiers.
- Obtain all author-approved declarations and the current journal checklist.

### Exit gate

**G4 and G5 pass.** No `[MATERIAL GAP]` remains in a submission-facing file.

## Stage 7 — Human sign-off

### Required confirmations

- all authors approve content, order, roles, declarations, and submission;
- the manuscript is not under consideration elsewhere;
- the current journal instructions and data-access policy were rechecked;
- the cover letter is truthful and venue-specific;
- the corresponding author explicitly authorizes submission.

### Exit gate

**G6 passes.** Submission remains a human action and must not be automated by this workflow.

## Immediate next actions for the manuscript team

1. Send the P0 author/institution evidence request.
2. Correct evidence-registry terminology and the claim matrix.
3. Create the hashed source-priority and scope-bridge artifacts.
4. Design the complete English outline and claim–evidence flow using only verified evidence.
5. Draft the internal working manuscript with `[MATERIAL GAP]` fields intact.
6. Prepare a `python-docx` build pipeline, but label its output **NOT FOR SUBMISSION** until G0–G5 pass.
