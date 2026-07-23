# Data in Brief v.19 Template Conformance Report

> **NOT FOR SUBMISSION OR PUBLIC RELEASE**

**Template:** [`Draft_Paper/data-in-brief-article-template.docx`](../data-in-brief-article-template.docx)  
**Version:** v.19 (December 2024)  
**Template SHA-256:** `5c02d5f9e0762e05f69c06d1d042ea800b6214427c82a78166863dfd17264190`  
**Generated DOCX SHA-256:** `17a07e5567793bf68566a35689738ab41c8b864b08f332ff6ec25c3d1253e704`

## Implementation decision

The canonical internal DOCX is now built by loading the supplied official template rather than creating a blank Word document. The build removes the author-instruction page, blue instructional text, comment boxes, editable-region protection, external hyperlinks, and custom sensitivity properties while preserving the official theme, A4 page geometry, 1-inch margins, line numbering, Heading 1 style, and Data in Brief header artwork.

The comprehensive evidence master remains at `04_INTERNAL_WORKING_MANUSCRIPT.md`; the template-facing canonical source is `06_DATA_IN_BRIEF_TEMPLATE_MANUSCRIPT.md`.

## Official structure check

The generated DOCX contains exactly these 12 Heading 1 sections, without numbering:

1. ARTICLE INFORMATION
2. SPECIFICATIONS TABLE
3. VALUE OF THE DATA
4. BACKGROUND
5. DATA DESCRIPTION
6. EXPERIMENTAL DESIGN, MATERIALS AND METHODS
7. LIMITATIONS
8. ETHICS STATEMENT
9. CRediT AUTHOR STATEMENT
10. ACKNOWLEDGEMENTS
11. DECLARATION OF COMPETING INTERESTS
12. REFERENCES

No separate Heading 1 section is used for Technical Validation, Data Availability, Funding, or GenAI. Technical validation is integrated into Methods; access appears in the Specifications Table; funding appears under Acknowledgements; the unresolved GenAI determination remains a paragraph-level internal control.

## Template limits and content checks

| Requirement | Result | Status |
|---|---:|---|
| Title includes “data” or “dataset” | Includes “dataset” | PASS |
| Keywords | 6; no title-word repetition | PASS |
| Abstract | 195 words; required range 100–500 | PASS |
| Specifications Table | Exactly 7 fixed rows | PASS |
| Specific subject area | 61 characters excluding spaces; maximum 150 | PASS |
| Data collection cell | 362 characters excluding whitespace in the complete rendered cell; maximum 600 | PASS |
| Value of the Data | 4 bullets; required range 3–6 | PASS |
| Background | 130 words using the regression-test regex; maximum 200 | PASS |
| Limitations | 126 words; maximum 200 | PASS |
| References | 16 numbered entries; maximum 20 | PASS |
| Related article | Citation [1] and one Specifications Table entry | PASS |
| Dataset citation | Explicitly blocked pending repository/version/DOI | CONTROLLED GAP |
| Canonical material gaps | All 33 exact tokens retained | PASS_INTERNAL_ONLY |

## Repository/file-description check

Data Description individually names:

- `README.md` and `CITATION.cff`;
- all 11 category TAR archives;
- all 11 category transcript files;
- `metadata/dataset_metadata_public.csv`;
- `metadata/transcript_sentence_inventory_public.csv`;
- `metadata/speaker_labels/hf_public_metadata_schema.md`;
- `splits/speaker_split_assignment_public.csv`;
- `splits/split_summary_public.json`;
- `paper/dataset_information/synthetic_repair_rows_public.csv`;
- planned minimal scripts, environment locks, and `checksums/SHA256SUMS`.

Tables 1–5 and Figures 1–3 are embedded. Supplementary Table S6 remains in editable CSV/XLSX and is not presented as a main DOCX table.

## Structural extraction

The generated DOCX was re-opened and deterministically extracted:

- 119 paragraphs; 116 non-empty;
- approximately 5,035 extracted words including tables/references;
- 6 tables: the seven-row Specifications Table plus Tables 1–5;
- 3 body figures;
- 4 media parts: the official header artwork plus the 3 figures;
- 1 A4 section with 1-inch margins;
- 12 Heading 1 sections in the official order;
- no comments, tracked insertions/deletions, external hyperlinks, or document protection;
- blank author and last-modified-by core properties.

Extraction artifacts are under [`Draft_Paper/01_Extraction/template_aligned_internal/`](../01_Extraction/template_aligned_internal).

## Microsoft Word rendering and visual audit

The canonical DOCX was opened locally in Microsoft Word through a non-interactive COM render and exported to:

- [`Draft_Paper/01_Extraction/template_aligned_internal/rendered_preview.pdf`](../01_Extraction/template_aligned_internal/rendered_preview.pdf)
- SHA-256 `828794f76643ce2390f0fe39c21fc8b483b5e0d64af2fcf45d90709a896c2e74`
- 14 A4 pages
- contact sheet: `rendered_preview_contact_sheet.jpg`

Page-by-page inspection found:

- the official Data in Brief header artwork and line numbering are retained;
- the internal-only banner/footer remain visible;
- all required sections are present in order;
- tables and figures remain within page boundaries;
- table headers repeat when a table continues;
- no visible clipping, overlapping objects, or orphaned figure was observed;
- Table 4 was compacted in the DOCX display while its complete editable source remains in CSV/XLSX;
- detailed Specifications evidence-status fields remain in the editable CSV/evidence registry rather than being appended to constrained rendered cells;
- the full rendered Specific subject area and Data collection cells are regression-tested at 61/150 and 362/600 non-whitespace characters, respectively;
- red material-gap text is intentionally prominent because this is an internal evidence-control draft.

## Package checks

- DOCX generation is byte-deterministic across two independent builds.
- XLSX generation remains deterministic and includes Specifications, Tables 1–5, and Supplementary Table S6.
- `PACKAGE_MANIFEST.json` lists 42 hashed files and records the official template version/hash, canonical source hash, template-builder hash, and package-builder hash.
- The internal verifier reports `PASS_INTERNAL_ONLY` across 8/8 mechanical groups.

## Submission decision

Template conformance does not close ethics, consent, rights, privacy, data freeze, reproducibility, public/controlled access, DOI, prior-publication eligibility, declarations, or author-authorization gates. The DOCX remains **NOT FOR SUBMISSION OR PUBLIC RELEASE** until G0–G6 are closed and the material-gap text is replaced only with verified, author-approved content.
