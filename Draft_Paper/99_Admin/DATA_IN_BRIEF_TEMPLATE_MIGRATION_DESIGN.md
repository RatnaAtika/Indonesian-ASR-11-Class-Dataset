# Data in Brief Template Migration Design

> **INTERNAL — NOT FOR SUBMISSION OR PUBLIC RELEASE**

**Template:** [`Draft_Paper/data-in-brief-article-template.docx`](../data-in-brief-article-template.docx)  
**Template version:** data article template v.19 (December 2024)  
**Template SHA-256:** `5c02d5f9e0762e05f69c06d1d042ea800b6214427c82a78166863dfd17264190`

## Decision

Use the supplied official DOCX as the structural and style base for the canonical internal paper. Preserve the current long evidence manuscript as the master source, and create a separate template-aligned manuscript whose section order, limits, table schema, reference order, and DOCX styles follow v.19.

This is preferred over:

1. **Cosmetic reformatting of the existing DOCX:** fast, but retains non-template sections, numbered headings, a nine-row Specifications Table, and a separate Technical Validation section.
2. **Manual Word editing:** visually direct, but nondeterministic and difficult to regression-test.
3. **Official-template base plus deterministic population (selected):** preserves the supplied styles, banner, A4 geometry, and required section order while allowing repeatable tests and sanitization.

## Template requirements mapped to NSS-ID

| Official element | NSS-ID implementation |
|---|---|
| Article title contains “data” or “dataset” | Keep “NSS-ID: An Indonesian read-speech dataset spanning 11 communicative sentence categories.” |
| Article Information | Title, provisional authors, affiliation/correspondence material gaps, 4–8 non-title-repeating keywords, 100–500-word abstract. |
| Specifications Table | Exactly seven fixed left-column rows from v.19; merge format/acquisition/collection into `Data collection`. |
| Value of the Data | Four evidence-safe bullets; no conclusions or unsupported generalization. |
| Background | Maximum 200 words; related article is citation [1]. |
| Data Description | Describe repository/package folders, 11 TAR files, 11 transcript files, metadata, split, synthetic, source-value, benchmark, script, and checksum components; use Tables 1–5 and Figures 1–3. |
| Experimental Design, Materials and Methods | Comprehensive evidence-qualified acquisition/curation account; integrate validation procedure and point to Supplementary Table S6 rather than creating a separate main heading. |
| Limitations | Maximum 200 words; data collection/curation limitations only. |
| Ethics Statement | Retain primary ethics/consent/privacy material gaps; do not fabricate boilerplate. |
| CRediT | Retain author-approved-role material gap. |
| Acknowledgements | Include acknowledgements and funding material gaps, as required by the template. |
| Competing Interests | Retain author-approved declaration gap. |
| References | Maximum 20; related research article becomes [1]; dataset citation remains visibly blocked pending final repository/DOI. |

## DOCX construction

1. Load the official template with `python-docx`.
2. Remove all body content except the final section properties.
3. Preserve the official theme, styles, A4 page geometry, 1-inch margins, and Data in Brief header artwork.
4. Populate only manuscript content; omit the author-instruction page and blue instructional text.
5. Remove comments, comment relationships, editing protection, permission ranges, tracked changes, and external relationships.
6. Add an internal footer stating `NOT FOR SUBMISSION OR PUBLIC RELEASE` without replacing the official header.
7. Sanitize core properties and normalize ZIP timestamps for deterministic output.

## Internal evidence controls

The template-aligned source and DOCX must retain all 33 canonical material-gap tokens. This requirement is internal only: before a future submission candidate, each token must be closed with primary evidence or the affected field must be omitted/approved, then the package must be regenerated.

The file remains private and must not be submitted or used to activate repository access while G0–G6 are open.
