# Canonical Dev-to-Val Migration Implementation Plan

> **REQUIRED SUB-SKILL:** Use the executing-plans skill to implement this plan task-by-task.

**Goal:** Migrate every active dataset/training/public surface from `train/dev/test` to `train/val/test` while preserving historical artifacts and exact data membership.

**Architecture:** Active inputs, metadata, documentation, generators, and public package artifacts use the machine token `val` and human label `Validation`. Small compatibility resolvers prefer `val.tsv` and fall back to historical `dev.tsv` with an explicit warning; archived run bundles, packaged historical source, old snapshots, and old verification sessions remain immutable. Hugging Face is migrated from a downloaded exact revision, verified privately, and uploaded as a bounded small-file commit without touching the eleven audio TAR shards.

**Tech Stack:** Python 3, unittest, CSV/JSON/Markdown, Git/GitHub CLI, Hugging Face Hub CLI.

---

### Task 1: Define migration policy and failing acceptance tests

**Files:**
- Create: `tests/test_validation_split_migration.py`
- Create: `docs/operations/VALIDATION_SPLIT_MIGRATION.md`

**Steps:**
1. Add tests requiring `val.tsv`, resolver preference/fallback behavior, exact active-surface terminology, and unchanged split counts.
2. Run the tests and verify they fail because the repository still uses `dev`.
3. Record the active-versus-historical boundary and compatibility period.

### Task 2: Implement compatibility resolvers and canonical training inputs

**Files:**
- Create: `training/common/split_compat.py`
- Create: `training_conventional/common/split_compat.py`
- Rename: `training/data_final/dev.tsv` to `training/data_final/val.tsv`
- Modify: `training/common/from_scratch_trainer.py`
- Modify: `training/common/wav2vec2_trainer.py`
- Modify: `training/common/whisper_trainer.py`
- Modify: `training_conventional/common/feature_builder.py`
- Modify: `training_conventional/common/spm_builder.py`
- Modify: `training/zero_shot_baselines/run_inference.py`
- Modify: `Colab_ASR_A100_Training/scripts/colab_verify_dataset.py`

**Steps:**
1. Implement resolvers that prefer `val.tsv`, accept legacy `dev.tsv`, warn on fallback, and fail if neither exists.
2. Update active loaders/builders to request the validation split through the resolver.
3. Keep `valid.pkl` compatibility because it is a cache artifact name, not the legacy split token.
4. Run migration tests until green.

### Task 3: Update active GitHub documentation and generation sources

**Files:**
- Modify: `README.md`
- Modify: `RUN_GUIDE.md`
- Modify: `RESEARCH_FLOW.md`
- Modify: active Colab/GPU guides containing `training/data_final/dev.tsv`
- Modify: `tools_prepare_hf_anonymization.py`
- Modify: `tools_prepare_hf_dataset_information.py`
- Modify: `Draft_Paper/99_Admin/build_release_target_figures.py`
- Modify: `Draft_Paper/99_Admin/build_revised_manuscript_tables.py`
- Modify: active public HF staging/data-information files under `Report_paper_9model/`
- Modify: current canonical draft/table sources under `Draft_Paper/04_Revised_Draft/`

**Steps:**
1. Replace machine values `dev` with `val` in active artifacts only.
2. Use `Validation` in human-facing labels.
3. Keep release-target and frozen-benchmark counts distinct.
4. Regenerate bounded current tables/figures where supported.
5. Verify archived paths still retain historical terminology.

### Task 4: Prepare and validate the Hugging Face organization migration

**Files:**
- Create temporary staging outside Git from HF revision `788b195ff9f38900fcc810db369d3a2f8b9fb9c5`.
- Modify only non-TAR text/data artifacts in the temporary staging.

**Steps:**
1. Download the exact live HF organization revision excluding TAR files.
2. Rewrite exact standalone `dev` tokens to `val` in active text/data artifacts.
3. Update old personal-namespace URLs to organization URLs.
4. Align README visibility wording with actual repository settings.
5. Verify 104,500 metadata rows remain present with counts 73,150/15,675/15,675.
6. Verify eleven TAR sibling objects remain untouched.
7. Upload the bounded staging as one HF commit and verify the resulting revision live.

### Task 5: Repeated critique and closure gates

**Files:**
- Update: `docs/operations/VALIDATION_SPLIT_MIGRATION.md` with verification evidence.

**Steps:**
1. Run migration unit tests, Python compilation, current administrative tests, link checks, and secret scans.
2. Audit the diff for unintended historical changes and restore any archived artifact changes.
3. Audit active GitHub surfaces for residual standalone `dev`, allowing only compatibility modules and migration documentation.
4. Audit live HF for residual standalone `dev` and require zero.
5. Compare pre/post row counts, speaker assignments, synthetic counts, audio-shard inventory, and non-split metadata.
6. Repeat audit/fix cycles until every gate passes.

### Task 6: Commit and push

**Steps:**
1. Stage only reviewed migration files.
2. Run `git diff --cached --check`, targeted secret scan, tests, and changed-file inventory.
3. Commit with `refactor(data): standardize validation split as val`.
4. Push without force to GitHub organization `main` as explicitly authorized.
5. Verify GitHub main commit and live files.
6. Report GitHub commit, HF revision, tests, residual historical exceptions, and any remaining risks.
