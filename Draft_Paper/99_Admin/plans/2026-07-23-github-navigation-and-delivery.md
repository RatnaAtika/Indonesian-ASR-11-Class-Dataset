# Draft Paper GitHub Navigation and Delivery Implementation Plan

> **REQUIRED SUB-SKILL:** Use secure-commit-guard and verification-before-completion before commit/push.

**Goal:** Publish every repository-safe, non-ephemeral artifact under [`Draft_Paper/`](../..) to a dedicated GitHub branch and make the latest manuscript package easy to navigate through verified clickable links.

**Architecture:** Keep [`Draft_Paper/`](../..) as the dedicated repository folder. Add a bilingual root README and deterministic exhaustive file index. Convert resolvable repository-path references in human-authored Markdown to relative GitHub-compatible links, while preserving extraction snapshots as immutable evidence and refusing to create dead links to local-only/ignored files. Keep package generation deterministic and validate every internal Markdown link before delivery.

**Tech Stack:** Python 3 standard library, Markdown relative links, existing DOCX/XLSX/package builders, Git/GitHub CLI.

---

## Task 1: GitHub navigation sources and tests

**Files:**
- Create: [`Draft_Paper/README.md`](../../README.md)
- Create: [`Draft_Paper/GITHUB_FILE_INDEX.md`](../../GITHUB_FILE_INDEX.md)
- Create: [`Draft_Paper/GITHUB_LINK_AUDIT.json`](../../GITHUB_LINK_AUDIT.json)
- Create: [`Draft_Paper/99_Admin/github_navigation.py`](../github_navigation.py)
- Create: [`Draft_Paper/99_Admin/test_github_navigation.py`](../test_github_navigation.py)

**Steps:**
1. Add tests for primary README links, exhaustive file-index coverage, relative-link resolution, cache exclusion, and absence of unresolved links produced by the generator.
2. Run the test and confirm it fails before implementation.
3. Implement deterministic path resolution, URL encoding, Markdown linkification, file indexing, and link auditing.
4. Generate the README/index/audit and rerun the focused test.

## Task 2: Preserve document generation while linking Markdown

**Files:**
- Modify: [`Draft_Paper/99_Admin/build_data_in_brief_template_docx.py`](../build_data_in_brief_template_docx.py)
- Modify: [`Draft_Paper/99_Admin/build_internal_docx_package.py`](../build_internal_docx_package.py)
- Modify: relevant tests under [`Draft_Paper/99_Admin/`](..)

**Steps:**
1. Ensure internal Markdown links render as readable labels rather than raw Markdown syntax in DOCX.
2. Generate clickable package README entries.
3. Run navigation generation after package copies are created and before package hashes are written.
4. Verify byte-deterministic DOCX/XLSX/package behavior remains intact.

## Task 3: GitHub-safe artifact scope

**Files:**
- Modify: `.gitignore`
- Modify: [`Draft_Paper/99_Admin/extract_docx.py`](../extract_docx.py)
- Modify: extraction inventory JSON files containing machine-local source paths.

**Steps:**
1. Permit DOCX/PDF files only under [`Draft_Paper/`](../..) despite repository-wide binary ignores.
2. Permit the public HF metadata snapshot under [`Draft_Paper/02_Evidence/`](../../02_Evidence).
3. Continue excluding `.cache/`, `__pycache__/`, private audio, credentials, checkpoints, crosswalks, and the three source-only artifacts containing respondent imagery.
4. Preserve the original source hash and add a repository-safe custody note while keeping the original DOCX local.
5. Replace machine-local paths in generated inventories with repository-relative paths.
6. Run targeted privacy, secret, file-size, and public-ID scans.

## Task 4: Rebuild and verify

**Steps:**
1. Rebuild the internal manuscript package.
2. Regenerate GitHub navigation artifacts.
3. Run the complete [`Draft_Paper/99_Admin`](..) regression suite and package verifier.
4. Verify every Markdown link and all manifest hashes.
5. Recheck the Word-rendered PDF and canonical DOCX hashes.

## Task 5: Commit and push

**Target:** `origin`, branch `docs/draft-paper-github-navigation`.

**Steps:**
1. Stage only `.gitignore` and [`Draft_Paper/`](../..); do not stage unrelated working-tree changes.
2. Review staged names/statistics, binary sizes, secrets, private paths, and package scope.
3. Commit with a Conventional Commit message.
4. Re-run pre-push tests and scan the outgoing commit range.
5. Push without force.
6. Verify the remote branch and clickable GitHub README/file links through the GitHub API/CLI.
