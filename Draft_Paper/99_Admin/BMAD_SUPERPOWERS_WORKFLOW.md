# BMAD + Superpowers Manuscript Revision Workflow

## Project

- **Working title:** NSS-ID Data in Brief revision
- **Source manuscript:** `Draft_Paper/00_Source/Draft Jurnal Data In Brief NSS-ID_ver3.docx`
- **Target venue:** Elsevier *Data in Brief*
- **Workflow track:** BMAD Method adapted to an existing research manuscript (brownfield)
- **Communication language:** Indonesian
- **Manuscript language:** English

## Core problem

The source draft must be rebuilt into a reviewer-defensible data article using the newest verified project evidence without mixing incompatible scopes or turning a dataset paper into a model-development paper.

## Success criteria

1. Every quantitative claim is linked to an authoritative project artifact.
2. The full public dataset (104,500 files) is separated from the paper benchmark subset (102,544 files).
3. Public artifacts use only `M*`, `F*`, `Ms*`, and `Fs*` labels.
4. Synthetic data, transcript repairs, numbering gaps, sampling limitations, and split composition are disclosed.
5. Benchmark results are framed as technical validation/data utility, not as the dataset's primary novelty.
6. Unknown ethics, consent, licence, DOI, funding, and author-contribution details remain explicit `[MATERIAL GAP]` fields rather than fabricated prose.
7. The package includes an editable English manuscript, DOCX, evidence map, reviewer critique, and revision roadmap.

## BMAD phases

### Phase 1 — Analysis

- Extract DOCX text, tables, images, styles, references, and metadata.
- Build a source hierarchy and evidence registry.
- Identify factual conflicts and unsupported claims.
- Conduct journal-guideline and comparable-resource research.

### Phase 2 — Planning

- Define one manuscript take-home message.
- Design the Data in Brief section sequence.
- Decide what enters the main text, tables, figures, supplement, or is excluded.
- Build a claim–evidence matrix and material-gap register.

### Phase 3 — Solutioning/readiness

Readiness gate requires:

- no scope mixing;
- no private speaker names;
- no invented ethics/licence/DOI facts;
- benchmark caveats are explicit;
- full-scope and benchmark-scope figures are labelled;
- all mandatory Data in Brief declarations are represented.

### Phase 4 — Implementation and review

- Draft in English from verified evidence.
- Generate DOCX and editable supporting artifacts.
- Run independent reviewer, methodology, data-integrity, privacy, and editorial critiques.
- Revise until no unresolved Critical/Important issue remains except author-owned material gaps.

## Superpowers controls

- **Brainstorming:** compare conservative patching, evidence-led rewrite, and split-publication approaches; use evidence-led rewrite.
- **Writing plan:** this file and the tracked plan serve as the execution specification.
- **Parallel agents:** use independent read-only reviewers for manuscript, data, methods, and editor-fit assessments.
- **Systematic debugging:** treat contradictory counts/scopes as evidence bugs; trace to primary artifacts.
- **Verification before completion:** regenerate and re-extract the final DOCX, scan public identifiers, and validate all numbers against the evidence registry.

## Evidence hierarchy

1. **Tier A — primary/full public dataset:** full 104,500-row public metadata and HF publication artifacts.
2. **Tier B — frozen benchmark subset:** 102,544-row clean subset and 15,376-item speaker-disjoint test results.
3. **Tier C — sampled diagnostics:** n=297 audio-quality sample and selected spectrogram/accent analyses.
4. **Tier D — deployment diagnostics:** local/live OOD and robot-web results; use only as limitations/future validation, never as corpus accuracy evidence.
5. **Tier E — old narrative reports:** usable only after cross-check; never authoritative when they conflict with Tiers A–D.

## Hard exclusions

- Private speaker-name crosswalks.
- Original respondent names in manuscript-facing tables, figures, paths, or captions.
- Field-accuracy claims derived from development recordings or Whisper pseudo-labels.
- Placeholder institutional, ethics, consent, licence, funding, DOI, or author-role assertions presented as facts.
- Claims that sampled acoustic quality covers all 104,500 recordings.
- Direct comparison of test wall-clock times across unequal hardware as a fair speed ranking.
