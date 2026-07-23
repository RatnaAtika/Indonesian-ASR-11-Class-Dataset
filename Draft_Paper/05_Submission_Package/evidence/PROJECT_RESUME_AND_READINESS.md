# Project Résumé and Readiness Status

## Project

**NSS-ID: Indonesian controlled read-speech data article rebuild**  
**Target venue:** Elsevier *Data in Brief*  
**Current phase:** Internal package generation, verification, and stop-ship gate closure

## One-paragraph résumé

NSS-ID is a release-target Indonesian closed-prompt read-speech corpus organized into 11 communicative sentence categories. The authoritative metadata snapshot contains 104,500 audio files (134.1762 h), comprising 104,368 human recordings and 132 explicitly identified synthetic gap-fill recordings (0.1263%) under 20 retained human public speaker labels with corrected label counts (12 male and 8 female). Primary recruitment records are still required to verify participant uniqueness and label provenance. A separate frozen 102,544-file benchmark subset (130.6548 h) was used for nine-model technical validation. The project has completed private-first Hugging Face staging, transcript repair, public-label pseudonymization, evidence extraction, scope reconciliation, independent reviews, a complete English internal manuscript mapped to the official Data in Brief v.19 template, the Specifications Table plus Tables 1–5 and Supplementary Table S6, three release-target PNG/SVG figure pairs, verified references, prior-publication assessment, a uniform diagnostic rescore correcting historical benchmark denominator drift, and deterministic DOCX/XLSX package generation. Forty-three regression tests and eight package-verification groups pass. Those passes establish only internal artifact consistency: public release and journal submission remain NO-GO because ethics/consent, component rights and licence, privacy governance, DOI/access, prior-publication eligibility, acquisition evidence, frozen release manifests, and human authorization remain unresolved.

## Verified dataset snapshot

| Item | Release target | Frozen benchmark |
|---|---:|---:|
| Audio files | 104,500 | 102,544 |
| Duration | 134.1762 h | 130.6548 h |
| Human recordings | 104,368 | 102,412 |
| Synthetic recordings | 132 | 132 |
| Train/dev/test | 73,150 / 15,675 / 15,675 | 71,792 / 15,376 / 15,376 |
| Category–sentence pairs | 213 | 209 |
| Purpose | Intended dataset release and full-corpus description | Nine-model technical validation |

The 1,956-row difference reflects rows excluded from the benchmark because transcript fields were blank in the local metadata snapshot at benchmark freeze time. The repaired HF metadata retains those rows; audio shards were not changed.

## Technical-validation snapshot

- Nine systems produced predictions for the same frozen 15,376-item test manifest.
- The test set contains 15,374 human recordings and 2 synthetic repair recordings.
- A post-draft audit found that historical run-native metrics used two reference normalization/denominator sets, so the old ranking and old cross-recipe score comparison are not publication-valid.
- A corrective uniform diagnostic rescore now uses `splits/test_clean.tsv`, `nssid_project_uniform_v1`, 135,911 reference words, and 942,599 reference characters for all nine prediction files; no inference was rerun.
- Under that uniform rescore, Whisper-small FT is 0.186% WER / 0.140% CER, and ViT-modified-ID is 1.761% WER / 1.298% CER with 4,353,248 reported parameters. The main table contains no performance-rank column.
- Human public speaker labels are separated across partitions, but participant uniqueness is unverified, scripts are represented in training, and only three human public labels occur in test.
- Development/test contain no natural female evaluation speaker; gender-generalization conclusions are unsupported.
- Hardware and training recipes differ, so timing is provenance, not a controlled efficiency comparison.

## Work completed

- Private HF dataset staging with 11 category tar shards.
- Repair of 1,956 blank public transcript fields to zero remaining at the pinned HF revision.
- Preservation and documentation of intentional sentence-number gaps.
- Public-label pseudonymization and correction to 12 male/8 female human labels.
- English public category names and public-safe figure regeneration.
- Reproducibility checks for the nine-model benchmark and an L4 execution smoke test.
- Deterministic extraction of the source DOCX, including text, tables, styles, images, metadata, and source hash.
- Authoritative evidence registry and claim–evidence matrix.
- Six independent editorial, data-integrity, methodology, submission, privacy/ethics, and adversarial reviews.
- Consolidated gap analysis, reviewer-risk matrix, and dependency-gated roadmap.
- Post-draft editorial, quantitative/citation, and privacy/gate reviews, followed by an independent benchmark-fix re-review with no blocker/high/medium findings in the corrected scoring scope.
- Uniform rescoring of all nine stored prediction files against one canonical reference manifest and normalizer; historical run-native ranking retained only as provenance.
- Three deterministic release-target figure pairs (PNG at 600 dpi plus editable SVG), each visibly marked **NOT FOR SUBMISSION**; Figure 4 remains blocked pending 297-file sampling provenance.
- Deterministic internal DOCX built from the official v.19 template with 6 embedded tables, 3 body figures, 12 required Heading 1 sections, retained official header artwork/A4 geometry/line numbering, sanitized properties, no macros/comments/protection/external relationships/tracked changes, and reproducible ZIP timestamps.
- Consolidated editable XLSX workbook with 7 marked sheets, plus CSV tables, figures, evidence controls, and a SHA-256 package manifest.
- Microsoft Word rendering and 14-page visual audit found no evident clipping, overlap, or orphaned figure.
- Final mechanical verification: 43 regression tests pass and 8/8 package-audit groups return `PASS_INTERNAL_ONLY`; GitHub navigation adds 200 repository-safe indexed files with zero broken links and validates line-anchor ranges, while independent post-fix template review also returns `PASS_INTERNAL_ONLY`.

## Current readiness dashboard

| Area | Status | Reason |
|---|---|---|
| Dataset utility | **Conditional green** | Scale, category structure, explicit synthetic provenance, and fixed manifests can support ASR reuse if release and documentation gates close. |
| Scope integrity | **Amber/green** | Registry, manuscript, tables, and figures separate release target, frozen benchmark, and sampled diagnostics. Internal package hashes now verify; publication-attached release/repair/overlap/sample manifests remain open. |
| Ethics and consent | **Red** | Oversight record and public voice-release consent scope are unverified. |
| Public accessibility and licence | **Red** | HF is private, DOI absent, and licence `other`. |
| Privacy governance | **Red** | Voice remains identifiable; demographic minimization, lifecycle policy, and whole-package leakage audit are incomplete. |
| Data integrity | **Amber** | Main totals reconcile; synthetic disposition, repair validation, overlap/format/sample audit packaging, and stale-source blacklisting remain open. |
| Benchmark interpretation | **Amber/red** | Uniform rescoring corrected the historical reference-denominator defect, but seen scripts, only three human public labels in test, no natural female-label development/test recording source, two synthetic test files, incomplete method cards, and heterogeneous protocols sharply limit claims. |
| Manuscript | **Amber/red** | A complete English internal manuscript mapped to the official v.19 structure, 7 editable tables, 3 scope-safe figures, sanitized template-based DOCX, editable XLSX, verified-reference register, and all 33 canonical material-gap tokens now exist. Missing primary evidence, final declarations/access wording, Figure 4 provenance, and author approvals still block submission. |
| Public release | **NO-GO** | Ethics, consent, licence, rights, privacy, and release-governance gates are not closed. |
| Journal submission | **NO-GO** | Template/mechanical reviews pass only for internal use; evidence, ethics, rights, access, prior-publication, reproducibility, declaration, and authorization blockers remain. |

## Gate status after internal-package verification

| Gate | Status | Closure requirement |
|---|---|---|
| G0 — ethical releasability | **NO-GO** | Competent ethics determination and retained consent/lawful-basis evidence covering the intended raw-voice release and reuse. |
| G1 — rights and privacy | **NO-GO** | Component-specific rights/licences, synthetic-output review, approved privacy minimization, lifecycle governance, and whole-package leakage audit. |
| G2 — data freeze | **NO-GO** | Author decision on two mismatch rows plus immutable release, repair, checksum, and prior-row-intersection manifests. |
| G3 — reproducibility | **NO-GO** | Acquisition/QC records, transcript-repair and split algorithms, exact overlap report, 297-file sampling design, audio–text/header audits, and adequate per-recipe method cards. |
| G4 — access and citation | **NO-GO** | Journal-compliant public or approved controlled access, exact licence, persistent DOI, version, checksums, direct URL, and clean-session test. |
| G5 — package integrity | **NO-GO for submission** | The internal package passes its mechanical audit, but a final submission/release package cannot exist until G0–G4 close and all affected artifacts are regenerated. |
| G6 — human authorization | **UNASSESSED** | Final author order/declarations, all-author approval, exclusivity confirmation, and explicit submission authorization. |

Mechanical audit evidence is recorded in [`Draft_Paper/03_Review/11_INTERNAL_PACKAGE_VERIFICATION_REPORT.md`](../../03_Review/11_INTERNAL_PACKAGE_VERIFICATION_REPORT.md) and `.json`. `PASS_INTERNAL_ONLY` must not be interpreted as permission to submit or release.

## Current defensible take-home message

> NSS-ID is a controlled, closed-prompt Indonesian read-speech resource with explicit human and synthetic provenance, category-balanced file counts, pseudonymous public speaker labels, and fixed manifests that can support seen-script, held-out-human-speaker ASR experiments once ethical release, rights, access, and reproducibility requirements are resolved.

This message does **not** claim conversational, national, dialect, gender, unseen-text, open-domain, or field generalization.

## Stop-ship author actions

1. Supply the actual ethics approval/exemption/waiver record and consent language.
2. Confirm whether consent and rights permit the planned raw-voice access and reuse model.
3. Approve exact data, code, transcript/text, and synthetic-output licences.
4. Decide whether the two female-source/male-target synthetic files are regenerated, excluded, or retained with explicit flags.
5. Complete the exact row/figure/result overlap map for the verified related 2026 article and obtain an author/editor eligibility decision.
6. Confirm primary acquisition facts: participants/age, room, microphone, distance, software, and collection protocol—or approve their omission.
7. Approve demographic minimization, responsible-use, withdrawal, retention, takedown, and maintenance policies.
8. Attach immutable release, repair, split/template-overlap, prior-row-intersection, audio-header/audio–text, 297-file sample, and whole-package checksum manifests.
9. Complete per-recipe method cards or move the full nine-model table to the supplement; add synthetic-test-excluded and uncertainty/sensitivity analyses if the comparison is retained.
10. Provide corresponding-author details, final author order/affiliations, CRediT roles, funding, competing interests, acknowledgements, and GenAI-use determination.
11. Authorize a repository/DOI plan only after ethics, consent, rights, and privacy gates pass.
12. Obtain written all-author approval, exclusivity confirmation, and explicit submission authorization only after regenerated artifacts pass the final audit.

## Readiness statement

The evidence-led internal rebuild and mechanically verified working package are complete. The project is ready only for **controlled author/institution review and gate closure**, not for public release or journal submission. Every manuscript, figure, table, DOCX, XLSX, and package artifact must remain marked **NOT FOR SUBMISSION** until G0–G6 pass and the entire package is regenerated and re-audited.
