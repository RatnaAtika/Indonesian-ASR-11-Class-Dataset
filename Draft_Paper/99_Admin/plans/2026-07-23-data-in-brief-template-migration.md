# Official Data in Brief Template Migration Implementation Plan

> **REQUIRED SUB-SKILL:** Use the executing-plans skill to implement this plan task-by-task.

**Goal:** Generate a deterministic, internal-only NSS-ID manuscript from the supplied Data in Brief v.19 DOCX template and make it the canonical packaged DOCX.

**Architecture:** Keep `04_INTERNAL_WORKING_MANUSCRIPT.md` as the evidence master. Add a concise template-aligned Markdown source and a builder that loads the official DOCX, clears instructional content, preserves official style/header/page geometry, inserts the NSS-ID content/tables/figures, removes comments/protection, sanitizes properties, and normalizes the ZIP. Integrate the builder into the existing package generator.

**Tech stack:** Python 3, `python-docx`, `lxml`, `openpyxl`, `zipfile`, `unittest`, existing deterministic table/figure builders.

---

### Task 1: Template-conformance tests

**Files:**
- Create: [`Draft_Paper/99_Admin/test_data_in_brief_template_docx.py`](../test_data_in_brief_template_docx.py)
- Test input: [`Draft_Paper/data-in-brief-article-template.docx`](../../data-in-brief-article-template.docx)

1. Assert the official template hash/version.
2. Assert a generated file exists and inherits A4/1-inch geometry, heading style, and header image.
3. Assert exact official Heading 1 sequence and absence of non-template Heading 1 sections.
4. Assert seven-row Specifications Table, 4–8 keywords, 100–500-word abstract, Background ≤200 words, Limitations ≤200 words, 3–6 Value bullets, ≤20 references, and related article [1].
5. Assert all 33 canonical material gaps, NOT-FOR-SUBMISSION marking, no instruction page/comments/protection/external relationships.
6. Run the test and confirm RED because the builder/source do not yet exist.

### Task 2: Template-aligned manuscript source

**Files:**
- Create: [`Draft_Paper/04_Revised_Draft/06_DATA_IN_BRIEF_TEMPLATE_MANUSCRIPT.md`](../../04_Revised_Draft/06_DATA_IN_BRIEF_TEMPLATE_MANUSCRIPT.md)
- Modify: [`Draft_Paper/04_Revised_Draft/05_TABLE_CAPTIONS_AND_NOTES.md`](../../04_Revised_Draft/05_TABLE_CAPTIONS_AND_NOTES.md) only if template naming requires it.

1. Draft Article Information and a template-compliant abstract.
2. Build the exact seven-row Specifications Table content.
3. Rewrite Value of the Data, Background, Data Description, Methods, and Limitations to v.19 limits and non-interpretive style.
4. Integrate technical validation under Methods and retain Supplementary Table S6 outside the main DOCX body.
5. Reorder citations so the related article is [1] and keep ≤20 references.
6. Preserve all 33 canonical material-gap tokens.

### Task 3: Deterministic official-template builder

**Files:**
- Create: [`Draft_Paper/99_Admin/build_data_in_brief_template_docx.py`](../build_data_in_brief_template_docx.py)
- Test: [`Draft_Paper/99_Admin/test_data_in_brief_template_docx.py`](../test_data_in_brief_template_docx.py)

1. Load the official DOCX and clear body elements while preserving section properties.
2. Populate exact template headings and content blocks.
3. Insert the seven-row Specifications Table, Tables 1–5, and Figures 1–3.
4. Preserve official styles/header artwork; add internal footer.
5. Strip comments/protection/external links and sanitize properties.
6. Normalize ZIP timestamps and verify deterministic hash across two builds.
7. Run the test and confirm GREEN.

### Task 4: Package integration

**Files:**
- Modify: [`Draft_Paper/99_Admin/build_internal_docx_package.py`](../build_internal_docx_package.py)
- Modify: [`Draft_Paper/99_Admin/test_internal_docx_package.py`](../test_internal_docx_package.py)
- Modify: [`Draft_Paper/99_Admin/verify_internal_manuscript_package.py`](../verify_internal_manuscript_package.py)

1. Make the template builder produce `NSS-ID_INTERNAL_NOT_FOR_SUBMISSION.docx`.
2. Copy the template-aligned Markdown and template conformance record into the package.
3. Update expected DOCX table/heading/section counts and official-template hash in the manifest.
4. Keep XLSX and Supplementary Table S6 unchanged.
5. Run package tests and verifier.

### Task 5: Structural and visual audit

**Files:**
- Create: [`Draft_Paper/03_Review/15_DATA_IN_BRIEF_TEMPLATE_CONFORMANCE_REPORT.md`](../../03_Review/15_DATA_IN_BRIEF_TEMPLATE_CONFORMANCE_REPORT.md)

1. Re-extract the generated DOCX to a temporary/durable audit directory.
2. Verify exact headings, word limits, tables, figures, comments/protection, relationships, properties, and hashes.
3. Inspect each embedded figure and generate a DOCX contact/preview artifact if a renderer is available; otherwise document structural inspection limitation.
4. Run targeted privacy, secret, path, and material-gap scans.

### Task 6: Independent review and final verification

**Files:**
- Create: `Draft_Paper/03_Review/16_FINAL_TEMPLATE_BASED_MANUSCRIPT_REVIEW.md`
- Update: [`Draft_Paper/03_Review/12_FINAL_DELIVERY_SUMMARY.md`](../../03_Review/12_FINAL_DELIVERY_SUMMARY.md)

1. Obtain a read-only independent template-conformance/editorial review.
2. Fix any concrete internal consistency defects.
3. Run all admin tests, compileall, deterministic rebuild, 8/8 package checks, and manifest verification.
4. Record new DOCX/XLSX/manifest hashes and retain G0–G6 stop-ship status.

**No commit or submission step is authorized by this plan.**
