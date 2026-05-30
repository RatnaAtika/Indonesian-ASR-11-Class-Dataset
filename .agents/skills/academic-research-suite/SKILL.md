---
name: academic-research-suite
description: Portable academic research pipeline wrapper covering research → write → review → revise → finalize. Use this skill when the project is a paper, thesis, dissertation, systematic review, or any research manuscript.
provides:
  - academic-pipeline
  - academic-paper
  - academic-paper-reviewer
  - deep-research
aliases:
  - ars
  - academic-research
  - research-pipeline
upstream:
  repo: https://github.com/Imbad0202/academic-research-skills
  codex_sibling: https://github.com/Imbad0202/academic-research-skills-codex
  license: CC-BY-NC-4.0
relevance:
  project_types:
    - academic
    - research
    - thesis
    - paper
  signals:
    - "*.tex exists"
    - "main.tex, paper.tex, manuscript.tex exists"
    - "references.bib, bibliography.bib, library.bib exists"
    - "manuscript/, paper/, chapters/, drafts/ directories"
    - "apa7, ieeetran, elsarticle, llncs class in .tex"
    - "README mentions arXiv, DOI, ICLR, NeurIPS, ACL, EMNLP"
---

# Academic Research Suite (portable wrapper)

Full academic pipeline adapted from
[Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills)
and its Codex sibling
[academic-research-skills-codex](https://github.com/Imbad0202/academic-research-skills-codex).

This pack is a wrapper. It tells the agent how to load the upstream suite into
the current project, and it captures the portability rules so the pipeline does
not carry upstream-specific assumptions into the target repository.

## Scope

Covers the 4 upstream skills:

- `deep-research` — 13-agent research team (full / quick / systematic-review /
  socratic / fact-check / lit-review / review modes).
- `academic-paper` — 12-agent paper writing pipeline (full / plan /
  outline-only / revision / revision-coach / abstract-only / lit-review /
  format-convert / citation-check / disclosure modes).
- `academic-paper-reviewer` — 7-agent multi-perspective review (EIC + 3
  Reviewers + Devil's Advocate + 0-100 rubric) with full / re-review / quick /
  methodology-focus / guided / calibration modes.
- `academic-pipeline` — 10-stage orchestrator with integrity verification
  (Stage 2.5 + 4.5), R&R traceability, and cross-model hooks.

## When to use

- Drafting, revising, or reviewing an academic paper.
- Running a structured literature review (incl. PRISMA systematic review).
- Writing responses to reviewers.
- Producing IMRaD or theoretical structures (Thematic Review, Case Study,
  Policy Brief, Conference Paper).

## When NOT to use

- Non-academic prose (blog, marketing, fiction).
- Simple summaries where a full pipeline is overkill.
- Projects that already have a different research skill stack installed;
  defer to `scripts/resolve-conflicts.sh` to pick one suite.

## Install (auto via bootstrap)

The pack's `install-deps.sh` fetches the upstream Codex suite and stages the
four skills into the same `skills/` folder this repo installs into.

```bash
# manual equivalent:
mkdir -p "$CODEX_HOME/skills"
git clone --depth 1 https://github.com/Imbad0202/academic-research-skills-codex \
  "$(mktemp -d)/ars-codex"
# copy the four upstream skills; DO NOT rename them
cp -R "$(mktemp -d)/ars-codex/skills/"{deep-research,academic-paper,academic-paper-reviewer,academic-pipeline} \
  "$CODEX_HOME/skills/"
```

If the Codex sibling is unavailable, fall back to the Claude Code source repo
and strip Claude-only bindings:

```bash
git clone --depth 1 https://github.com/Imbad0202/academic-research-skills \
  "$(mktemp -d)/ars-claude"
# copy the same four subdirectories
```

## Supported citation formats

- APA 7.0 (default, incl. Chinese rules)
- Chicago (Notes + Author-Date)
- MLA
- IEEE
- Vancouver

## Rules

- **Human-in-the-loop.** The pipeline is advisory. Never finalize or submit
  without user confirmation. Stage 2.5 and Stage 4.5 integrity gates are
  mandatory.
- **No fabrication.** If a reference, datum, or figure is missing, emit
  `[MATERIAL GAP]` and ask; do not fill from parametric memory.
- **Reviewer skill is read-only.** It must not modify the manuscript.
- **Citation verification.** Prefer Semantic Scholar API + WebSearch audit
  trails; the suite's anti-hallucination mandate overrides any convenience
  shortcut.
- **Attribution.** Upstream license is CC-BY-NC-4.0. Distribution and
  modification must carry attribution to Cheng-I Wu and the Imbad0202 repo.
- **No Claude-isms.** Strip `$CLAUDE_PLUGIN_ROOT`, `/plugin` commands, and
  Claude Code specific hooks when adapting for Codex. The Codex sibling repo
  already does this; prefer it.

## Related

Pair with `research-paper-writing` (Master-cai) for ML/CV/NLP paper-specific
section templates, and with `autoresearch-suite` for iterative-experiment
grunt work inside Stage 1 RESEARCH.

## Upstream references

- Source (Claude Code): https://github.com/Imbad0202/academic-research-skills
- Source (Codex sibling): https://github.com/Imbad0202/academic-research-skills-codex
- Architecture doc: https://github.com/Imbad0202/academic-research-skills/blob/main/docs/ARCHITECTURE.md
- License: https://creativecommons.org/licenses/by-nc/4.0/
