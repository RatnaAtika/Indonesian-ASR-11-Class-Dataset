# NSS-ID Data in Brief v.19 Manuscript Architecture

**Artifact status:** internal planning document; **NOT FOR SUBMISSION OR PUBLIC RELEASE**  
**Official template:** [`Draft_Paper/data-in-brief-article-template.docx`](../data-in-brief-article-template.docx)  
**Template version/hash:** v.19 (December 2024), SHA-256 `5c02d5f9e0762e05f69c06d1d042ea800b6214427c82a78166863dfd17264190`  
**Canonical template source:** [`Draft_Paper/04_Revised_Draft/06_DATA_IN_BRIEF_TEMPLATE_MANUSCRIPT.md`](06_DATA_IN_BRIEF_TEMPLATE_MANUSCRIPT.md)  
**Evidence master:** [`Draft_Paper/04_Revised_Draft/04_INTERNAL_WORKING_MANUSCRIPT.md`](04_INTERNAL_WORKING_MANUSCRIPT.md)

## Editorial take-home message

NSS-ID is a closed-prompt Indonesian read-speech resource organized into 11 functional category labels. The paper documents package structure, stable identifiers, human/synthetic provenance, the release-target/frozen-benchmark bridge, construction methods, open evidence gaps, and bounded reuse without claiming conversational, demographic, dialect, unseen-text, field, or robot generalization.

## Required official Heading 1 sequence

The template-aligned DOCX uses only these Heading 1 sections and does not number them:

1. `ARTICLE INFORMATION`
2. `SPECIFICATIONS TABLE`
3. `VALUE OF THE DATA`
4. `BACKGROUND`
5. `DATA DESCRIPTION`
6. `EXPERIMENTAL DESIGN, MATERIALS AND METHODS`
7. `LIMITATIONS`
8. `ETHICS STATEMENT`
9. `CRediT AUTHOR STATEMENT`
10. `ACKNOWLEDGEMENTS`
11. `DECLARATION OF COMPETING INTERESTS`
12. `REFERENCES`

Technical validation is a Methods subsection and its complete model display remains Supplementary Table S6. Data accessibility is reported in the fixed Specifications Table. Funding is reported under Acknowledgements. The unresolved GenAI determination is retained as an internal paragraph-level control rather than a non-template Heading 1 section.

## Article Information

- **Title:** `NSS-ID: An Indonesian read-speech dataset spanning 11 communicative sentence categories`; contains “dataset” as required.
- **Authors/affiliations/correspondence:** retain exact material gaps until all-author approval.
- **Keywords:** 4–8 semicolon-separated terms that do not repeat title words.
- **Abstract:** 100–500 words; describe collection, data objects, and reuse potential without conclusions or interpretive performance claims.

## Specifications Table

Use exactly seven fixed left-column labels from v.19:

1. Subject
2. Specific subject area — maximum 150 characters excluding spaces
3. Type of data
4. Data collection — maximum 600 characters excluding spaces
5. Data source location
6. Data accessibility
7. Related research article — exactly one related article

All access, DOI, licence, collection-hardware, recruitment, and related-article eligibility gaps remain explicit in the right-hand cells.

## Value of the Data

Use four bullets, each under 150 words, restricted to deposited objects and concrete reuse operations:

- recording-level metadata and stable identifiers;
- 11 TAR archives plus transcript inventories;
- filtering by public label, category, split, sentence ID, duration, and source type;
- explicit separation of release target and frozen benchmark.

Do not advertise dialect coverage, population representativeness, field accuracy, robot performance, model superiority, or gender robustness.

## Background

Maximum 200 words. Cite the related 2026 article first as [1], then Indonesian/multilingual resource context and documentation principles [2–6]. State how this data article adds package/provenance detail without reclaiming model novelty. Keep the prior-publication overlap decision as a material gap.

## Data Description

Describe what readers receive, not how it was produced or what model results mean.

### Repository organization

Name `README.md`, `CITATION.cff`, all 11 category TAR files, all 11 transcript files, public metadata/schema files, split files, synthetic repair manifest, descriptive source-value files, validation scripts, and planned checksum/environment artifacts. Cite Table 1 and Figure 1.

### Scope bridge

State 104,500 files / 134.1762 h for the release target and 102,544 files / 130.6548 h for the frozen benchmark, plus the 1,956-row transcript-state difference and unchanged audio archives. Cite Table 2.

### Categories and identifiers

Report 11 categories, 9,500 files/category, 213 distinct `(category, sentence_id)` pairs, stable `01`–`20` IDs, intentional gaps, and partial replacements. Cite Table 3 and Figure 2.

### Split/source composition

Report 73,150/15,675/15,675 files, 14/3/3 retained human public labels, 122/8/2 synthetic rows, rounded hours, and source-label composition. Cite Table 4 and Figure 3.

### Synthetic and derivative artifacts

Report 132 flagged synthetic rows, source/target fields, the source-draft no-cloning assertion with technical confirmation pending, two mismatches, the 297-row diagnostic derivative, and frozen prediction artifacts. Cite Table 5 and Supplementary Table S6 without interpreting comparative performance.

## Experimental Design, Materials and Methods

This section has no template word limit and remains the most detailed section. Use bold paragraph-level subsections rather than additional Heading 1 sections.

Required sequence:

1. evidence classification and scope control;
2. ethics/recruitment/participant records;
3. prompt inventory and balanced-build transformation;
4. recording setting/equipment and conflicts;
5. elicitation, segmentation, naming, and transcripts;
6. structural QC and sampled diagnostics;
7. transcript repair/version bridge;
8. synthetic generation/provenance;
9. metadata/public identifiers/privacy;
10. split construction/leakage characterization;
11. statistics, figures, packaging, and technical-validation scoring.

The section must retain OBSERVED/INFERRED/CONFLICTED/MISSING discipline, identify source-author assertions, separate 104,500/102,544/297-row scopes, and keep all acquisition/QC/rights/access gaps visible.

## Limitations

Maximum 200 words and limited to properties or gaps of the data: retained label count and unverified participant provenance, narrow repeated prompts, split/source imbalance, synthetic rows/mismatches, missing repair/sample/direct-audio audits, residual voice identifiability, and unresolved access/rights/freeze records. Do not discuss model-performance interpretation here.

## Ethics, declarations, and references

- **Ethics:** no boilerplate approval/consent claim; retain committee, consent, demographic minimization, and lifecycle gaps.
- **CRediT:** author-approved assignments only.
- **Acknowledgements:** acknowledgements and funding/sponsor-role gaps.
- **Competing interests:** all-author-approved declaration only.
- **GenAI:** paragraph-level internal control pending current policy and author determination.
- **References:** maximum 20; related article [1]; remaining verified sources [2–16]; dataset citation visibly blocked until repository/version/DOI exists.

## DOCX construction controls

- Build from the supplied template, not a blank document.
- Preserve official A4 geometry, 1-inch margins, line numbering, theme, Heading 1 style, and header artwork.
- Delete the instruction page, blue instructions, comments, and locked-editing protection.
- Insert the seven-row Specifications Table, Tables 1–5, and Figures 1–3.
- Keep Supplementary Table S6 in XLSX/CSV rather than embedding it as a main DOCX table.
- Add visible internal-only marking, sanitize core/custom properties, remove external relationships, and normalize ZIP timestamps.
- Preserve all 33 canonical material gaps until documented closure and regeneration.
