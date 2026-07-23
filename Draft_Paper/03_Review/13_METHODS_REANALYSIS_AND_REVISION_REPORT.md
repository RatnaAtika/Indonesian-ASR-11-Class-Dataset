# Methods Re-analysis and Revision Report

> **NOT FOR SUBMISSION OR PUBLIC RELEASE**

**Revision date:** 2026-07-22  
**Decision:** internal methods rebuild complete; journal submission and public release remain **NO-GO**

## Scope

The source Word draft and current package were re-audited with emphasis on how NSS-ID was recruited, elicited, recorded, segmented, named, transcribed, normalized, checked, repaired, partitioned, packaged, and technically validated. Source-DOCX statements were treated as author assertions rather than automatic proof of collection events.

The audit used four evidence classes:

- **OBSERVED:** directly recorded in an artifact, executable script, manifest, or source assertion;
- **INFERRED:** strongly reconstructable from code/file structure but not backed by a contemporaneous protocol;
- **CONFLICTED:** local records disagree or refer to different data states;
- **MISSING:** no adequate evidence was located.

## Durable evidence products

- [`Draft_Paper/02_Evidence/METHODS_EVIDENCE_MATRIX.csv`](../02_Evidence/METHODS_EVIDENCE_MATRIX.csv) — 60 line-cited method/validation decisions.
- [`Draft_Paper/02_Evidence/AUTHOR_METHODS_EVIDENCE_QUESTIONNAIRE.md`](../02_Evidence/AUTHOR_METHODS_EVIDENCE_QUESTIONNAIRE.md) — bilingual English/Indonesian secure-response questionnaire covering all 33 canonical material gaps.
- [`Draft_Paper/02_Evidence/CURRENT_DIB_SPEECH_METHODS_EXPECTATIONS.md`](../02_Evidence/CURRENT_DIB_SPEECH_METHODS_EXPECTATIONS.md) — current journal/example brief, explicitly labelled **Official / snippet-only** where direct full-page retrieval was unavailable.
- [`Draft_Paper/02_Evidence/JOURNAL_REQUIREMENTS_SNAPSHOT.md`](../02_Evidence/JOURNAL_REQUIREMENTS_SNAPSHOT.md) — now carries the same retrieval limitation and mandatory live pre-submission recheck.
- [`Draft_Paper/04_Revised_Draft/03_MATERIAL_GAP_PLACEHOLDERS.md`](../04_Revised_Draft/03_MATERIAL_GAP_PLACEHOLDERS.md) — fixed 33-token ledger plus `SG-METADATA-BUILD`, `SG-AUDIO-QC`, and `SG-BENCHMARK-METHODS` closure sub-gates.

## Key evidence findings

1. **Executable balanced-build evidence:** 110,000 source WAV files across 5,500 take directories were audited; one prompt ID per category was omitted; 5,500 files were skipped; two-digit sentence filenames were enforced; 104,500 output files were structurally verified.
2. **Acquisition facts remain partly author-owned:** the source draft reports a laboratory room, treatment, BOYA microphone, Audacity/Windows, and 5–10 cm placement, but contemporaneous equipment/session evidence is absent.
3. **Room dimensions conflict:** prose reports 1 × 1 × 2.5 m; embedded diagrams show approximately 1.5037 m × 2.5027 m and approximately 2.5027 m height.
4. **Age conflicts:** the source draft reports both 25–38 and 22–38 years; age is omitted pending primary evidence and privacy approval.
5. **Participant authority is bounded:** artifacts establish 20 retained human public speaker labels, not independently verified participant uniqueness or recruitment eligibility.
6. **Transcript repair is operation-level evidence only:** 1,956 blank fields were filled and audio shards were unchanged, but the executable repair implementation, immutable repaired-row manifest, and audio–text audit remain open.
7. **Synthetic provenance remains conditional:** 132 rows are flagged, but exact Edge-TTS generation records/rights and the two female-source/male-target rows remain unresolved. The no-cloning statement is attributed only to the source author draft pending technical logs.
8. **Split evidence is incomplete:** exact assignments and seed 42 are observed; the executed generator, candidate order, RNG/library version, and validation attachment are missing.
9. **The 297-row acoustic derivative remains sample-bounded:** selection provenance is missing, so no corpus-wide acoustic conclusion is allowed.
10. **Benchmark scoring is reproducible but subordinate:** M053–M060 now cover the nine-recipe inventory, SentencePiece boundary, normalizer, canonical matching, WER/CER denominators, hashes, historical comparability defect, and open method-card/sensitivity/uncertainty/error-analysis work.

## Manuscript and display changes

- Restored Data in Brief-style numbering:
  1. Value of the Data
  2. Background
  3. Data Description
  4. Experimental Design, Materials and Methods
  5. Technical Validation
  6. Limitations and Responsible Use
- Expanded Section 4 to a detailed dataset-production account while preserving every unresolved material-gap token.
- Separated Data Description (what users receive), Methods (how data were made), and Technical Validation (what checks showed).
- Made the nine-model display **Supplementary Table S6** everywhere; no conflicting Table 6 identity remains.
- Rebuilt Figure 1 so a common pre-transcript-repair metadata state forks into transcript repair → release target and blank-row exclusion → frozen benchmark.
- Replaced person-level language with retained public speaker-label wording where participant uniqueness is not independently verified.
- Corrected the claim-evidence CSV schema and removed every bare/noncanonical material-gap alias.

## Independent review sequence

Initial methodology/editorial reviews identified speaker-label authority upgrades, mixed no-cloning attribution, incomplete Section 4.12 matrix coverage, missing closure paths, Table 6/S6 collision, Figure 1 topology, snippet-only provenance disclosure, and malformed/noncanonical claim-flow entries. Each was corrected and regression-tested.

The final independent closure review is stored at:

- [`Draft_Paper/03_Review/14_FINAL_METHODS_CLOSURE_REVIEW.md`](14_FINAL_METHODS_CLOSURE_REVIEW.md)

Its verdict is **PASS_INTERNAL_ONLY**, with no residual defect in the requested post-fix mechanics. This pass is not scientific, ethical, legal, release, or submission authorization.

## Remaining stop-ship gates

- **G0:** ethics/consent/lawful basis — NO-GO.
- **G1:** rights, licence, privacy governance, synthetic-output terms, and leakage audit — NO-GO.
- **G2:** mismatch-row disposition and immutable release freeze — NO-GO.
- **G3:** acquisition/QC, transcript repair, split generation, overlap/sample/audio audits, and method cards — NO-GO.
- **G4:** compliant repository access, licence, DOI/version/checksums/URL, and clean-session test — NO-GO.
- **G5:** final submission-package integrity after G0–G4 closure — NO-GO.
- **G6:** all-author approval, exclusivity, and explicit submission authority — UNASSESSED.

The related-article overlap/eligibility question also remains stop-ship pending exact row/result/figure intersection and editor determination.
