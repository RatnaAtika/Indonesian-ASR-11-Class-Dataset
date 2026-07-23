# Final Internal Delivery Summary

> **STATUS: NOT FOR SUBMISSION OR PUBLIC RELEASE**

## Decision

| Decision area | Status |
|---|---|
| Evidence-led internal rebuild | **COMPLETE / GO for controlled author–institution review** |
| Internal artifact verification | **PASS_INTERNAL_ONLY** |
| Journal submission | **NO-GO** |
| Public dataset release | **NO-GO** |
| G0–G5 | **NO-GO** |
| G6 author authorization | **UNASSESSED** |

`PASS_INTERNAL_ONLY` means that the generated working artifacts pass the recorded mechanical and semantic checks. It does not establish ethical releasability, legal rights, privacy acceptability, journal eligibility, reproducibility completeness, or permission to submit.

## Delivered working artifacts

| Artifact | Path | SHA-256 |
|---|---|---|
| Comprehensive evidence master | [`Draft_Paper/04_Revised_Draft/04_INTERNAL_WORKING_MANUSCRIPT.md`](../04_Revised_Draft/04_INTERNAL_WORKING_MANUSCRIPT.md) | `a6ae332ea90ec7c3b267306aec058538de5a05e3108d68998c5512b66315c820` |
| Canonical Data in Brief v.19 manuscript source | [`Draft_Paper/04_Revised_Draft/06_DATA_IN_BRIEF_TEMPLATE_MANUSCRIPT.md`](../04_Revised_Draft/06_DATA_IN_BRIEF_TEMPLATE_MANUSCRIPT.md) | `2d0b2aa17bdc72574f62a32d709548cc12dcc25f42ad854a85e7c740893dd304` |
| Official-template-based internal DOCX | [`Draft_Paper/05_Submission_Package/NSS-ID_INTERNAL_NOT_FOR_SUBMISSION.docx`](../05_Submission_Package/NSS-ID_INTERNAL_NOT_FOR_SUBMISSION.docx) | `17a07e5567793bf68566a35689738ab41c8b864b08f332ff6ec25c3d1253e704` |
| Consolidated editable XLSX | [`Draft_Paper/05_Submission_Package/NSS-ID_EDITABLE_TABLES_INTERNAL_NOT_FOR_SUBMISSION.xlsx`](../05_Submission_Package/NSS-ID_EDITABLE_TABLES_INTERNAL_NOT_FOR_SUBMISSION.xlsx) | `feb3d967fc8a40307376220c8ff7065dab685b3bbc232a27a11376c62e2f68bd` |
| Internal package manifest | [`Draft_Paper/05_Submission_Package/PACKAGE_MANIFEST.json`](../05_Submission_Package/PACKAGE_MANIFEST.json) | `a25861e8900f0a35a032de3a13931ca070930ae10612673afbe2dca71cd23d2f` |
| Verification report | [`Draft_Paper/03_Review/11_INTERNAL_PACKAGE_VERIFICATION_REPORT.md`](11_INTERNAL_PACKAGE_VERIFICATION_REPORT.md) and `.json` | JSON: `0b7a902f79b98301e34319dd49ce091c72387c6b46daa4d1cfe8f3b3f206e3dd` |
| Template conformance reports | [`Draft_Paper/03_Review/15_DATA_IN_BRIEF_TEMPLATE_CONFORMANCE_REPORT.md`](15_DATA_IN_BRIEF_TEMPLATE_CONFORMANCE_REPORT.md) and [`16_FINAL_DATA_IN_BRIEF_TEMPLATE_REVIEW.md`](16_FINAL_DATA_IN_BRIEF_TEMPLATE_REVIEW.md) | Final verdict: `PASS_INTERNAL_ONLY` |
| Full readiness résumé | [`Draft_Paper/03_Review/10_PROJECT_RESUME_AND_READINESS.md`](10_PROJECT_RESUME_AND_READINESS.md) | Rebuild status, G0–G6 table, and expanded action list |

Supporting artifacts include the Specifications Table, five numbered main data tables, Supplementary Table S6, three release-target PNG/SVG figure pairs, the 16-item verified-reference register, prior-publication assessment, scope-safe evidence registry, 60-row methods evidence matrix, bilingual author questionnaire, current snippet-qualified journal/example brief, structurally valid claim–evidence flow, uniform benchmark-rescore CSV/JSON/audit, reviewer-risk matrix, revision roadmap, and all 33 canonical material-gap controls plus three closure sub-gates.

## Material corrections completed

1. Audited all three post-draft reviews and applied evidence-backed editorial, quantitative, citation, privacy, and gate corrections.
2. Found that historical nine-model metrics used nonidentical reference normalization and denominators; removed their publication-facing rank interpretation.
3. Uniformly rescored all nine stored prediction files against the same 15,376-item canonical manifest using 135,911 reference words and 942,599 reference characters, without rerunning inference.
4. Rebuilt the complete nine-row benchmark display as **Supplementary Table S6** without rank or timing. Historical run-native values remain provenance only.
5. Corrected citation first-use order and retained only source-supported adjacent claims.
6. Regenerated Figures 1–3 from release-target Tier-A values using deterministic Pillow/SVG code. Figure 4 remains blocked pending the exact 297-file sampling design and manifest.
7. Rebuilt the deterministic DOCX directly from the supplied official Data in Brief v.19 template, preserving its header artwork, theme, A4 geometry, 1-inch margins, line numbering, and Heading 1 style while removing author instructions, comments, protection, external links, and sensitivity properties.
8. Mapped the manuscript to the exact 12-section v.19 order, the seven-row Specifications Table, Tables 1–5, Figures 1–3, and separate Supplementary Table S6; the DOCX has six embedded tables and three body figures.
9. Generated a deterministic editable workbook with seven visibly marked sheets and copied all supporting source tables, figures, and evidence controls into the internal package.
10. Re-audited the source Word Methods against code, manifests, inventories, images, and reports; expanded the evidence master Methods using OBSERVED/INFERRED/CONFLICTED/MISSING discipline and compressed it into the official template without upgrading claims.
11. Rebuilt Figure 1 around a common pre-transcript-repair state; bounded participant claims to retained public labels; separated the source-draft no-cloning assertion from metadata evidence; and fixed all claim-flow CSV/token defects.
12. Completed independent methods and post-fix template reviews with verdict **PASS_INTERNAL_ONLY** ([`14_FINAL_METHODS_CLOSURE_REVIEW.md`](14_FINAL_METHODS_CLOSURE_REVIEW.md) and [`16_FINAL_DATA_IN_BRIEF_TEMPLATE_REVIEW.md`](16_FINAL_DATA_IN_BRIEF_TEMPLATE_REVIEW.md)).

## Verification evidence

- **43 regression tests passed** across evidence/methods semantics, claim-flow structure and canonical tokens, official-template structure and cell limits, GitHub navigation/link and line-anchor resolution, clean-checkout source custody, privacy exclusions, uniform rescoring, editable tables, manuscript semantics/citation order, release-target figures, deterministic DOCX/XLSX generation, and end-to-end package audit.
- **8/8 package-audit groups passed**: manifest hashes; canonical material gaps; quantitative reconciliation; benchmark comparability; citations; privacy/secrets/file scope; DOCX/XLSX integrity; and figure integrity.
- Python compilation passed for [`Draft_Paper/99_Admin/`](../99_Admin).
- All 33 canonical material-gap tokens occur in both Markdown and DOCX; no noncanonical material-gap token is present.
- Release-target totals, rounded split/category hours, 213 distinct `(category, sentence_id)` pairs, frozen 102,544-file/209-pair scope, and all nine unified benchmark rows reconcile.
- All 16 selected references have verified or verified-with-primary-metadata status and are first cited in numerical order.
- Targeted scans found no machine-specific path, credential pattern, prohibited anonymity formulation, out-of-range public speaker ID, private audio, checkpoint, runtime log, or forbidden package file type.
- DOCX re-parsing found 6 tables, 3 body images plus official header artwork, 12 required Heading 1 sections, 119 paragraphs, clean core properties, and no tracked insertions/deletions, comments, protection, or external relationships.
- Microsoft Word rendered the canonical DOCX to 14 A4 pages; page-by-page contact-sheet inspection found no evident clipping, overlap, or orphaned figure.
- The package contains 42 manifest-listed artifacts plus `PACKAGE_MANIFEST.json`; every listed byte count and SHA-256 matches.

## Stop-ship actions for authors and institution

### P0 — must close before any release or submission

1. Supply the competent ethics approval/exemption/waiver determination, reference number, and date.
2. Supply retained consent or another institutionally approved lawful basis covering public voice access, redistribution, model training, derivative research, withdrawal, and the intended access model.
3. Clear component-specific rights for audio, prompt text, transcripts/metadata, code, and synthetic outputs; approve exact licences consistent with consent and third-party terms.
4. Approve privacy minimization and lifecycle governance, including controller/contact, crosswalk retention, withdrawal, takedown, breach, versioning, maintenance, and whole-package leakage review.
5. Complete the exact row/result/figure overlap map for the related 2026 article and obtain a documented *Data in Brief* eligibility/editor decision.
6. Decide whether the two female-source/male-target synthetic files are regenerated, excluded, or explicitly retained; then regenerate every affected manifest, statistic, table, figure, and benchmark result.

### P1 — publication-grade data and method freeze

7. Attach immutable release, repair, split/template-overlap, prior-row-intersection, audio-header/audio–text, 297-file sample, and whole-package checksum manifests.
8. Supply authoritative acquisition and QC evidence: recruitment, age or approved omission, recording dates, room, microphone/interface, distance/gain, software, prompt presentation, repetition/replacement/rejection rules, transcript source, and normalization specification.
9. Complete per-recipe method cards, atomic checkpoint/tokenizer/prediction hashes, synthetic-test-excluded sensitivity, dependence-aware uncertainty, and error analysis before considering any promotion of Supplementary Table S6.
10. Resolve journal-compliant public or approved controlled access, exact version, persistent DOI, direct URL, checksums, access date, and a clean-session access test.

### P2 — declarations and human authority

11. Approve corresponding-author details, final author order and affiliations, CRediT roles, funding/sponsor role, competing interests, acknowledgements, and the GenAI manuscript-preparation determination.
12. Obtain written all-author approval, exclusivity confirmation, and explicit submission authorization only after G0–G5 pass and the regenerated package passes the final audit.

## Residual technical limitation

The current canonical DOCX was rendered with Microsoft Word and inspected page by page through a 14-page PDF/contact sheet. This establishes internal visual integrity only; before any future submission candidate is approved, responsible authors must repeat the review after all gap text is replaced and check final pagination, table accessibility, figure legibility, captions, alt text, accessibility, and journal production requirements in the exact file authorized for submission.

## Final instruction

Do not upload, mint a DOI, make the Hugging Face repository public, send the manuscript to a journal, or remove any **NOT FOR SUBMISSION** marking until G0–G6 are documented as passed by the responsible humans and the entire package is regenerated and re-audited.
