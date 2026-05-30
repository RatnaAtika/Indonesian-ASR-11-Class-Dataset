---
name: research-paper-writing
description: Section-by-section writing guide for ML/CV/NLP papers (Abstract, Introduction, Method, Experiments, Conclusion, Related Work) curated from Prof. Peng Sida's open study notes. Use this skill to draft, rewrite, or review paper sections.
provides:
  - paper-section-writer
  - claim-evidence-checker
aliases:
  - paper-writing
  - pengsida-notes
upstream:
  repo: https://github.com/Master-cai/Research-Paper-Writing-Skills
  credit: Prof. Peng Sida (彭思达) — https://github.com/pengsida/learning_research
  license: MIT
relevance:
  project_types:
    - ml-research
    - cv-research
    - nlp-research
    - paper
  signals:
    - main.tex, paper.tex, manuscript.tex
    - ieeetran.cls, llncs.cls, neurips_2024.sty, iclr*.sty, acl*.sty
    - experiments/, results/, figures/, tables/
    - pyproject.toml + notebooks/ + README mentions benchmark / SOTA
---

# Research Paper Writing (ML/CV/NLP)

Portable wrapper around
[Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills),
itself curated from Prof. Peng Sida's open notes at
https://pengsida.notion.site/c1a22465a0fa4b15a12985223916048e .

The upstream pack ships a single skill directory `research-paper-writing/`
containing:

- `SKILL.md` — core workflow and usage rules
- `references/` — section-specific writing guides and templates
- `agents/openai.yaml` — agent metadata for Codex

This wrapper fetches that directory into the current project's skills path.

## Use for

- Drafting or rewriting Abstract / Introduction / Method / Experiments /
  Conclusion / Related Work.
- Improving paragraph flow and section logic.
- Checking claim–evidence alignment in results discussion.
- Running pre-submission self-review from a reviewer mindset.

## Do NOT use for

- Humanities / social science papers (different norms; use
  `academic-research-suite` instead).
- General English copy-editing without claim structure.
- Code-heavy README files (paper narrative, not engineering notes).

## Install (auto via bootstrap)

The pack's `install-deps.sh` runs:

```bash
git clone --depth 1 https://github.com/Master-cai/Research-Paper-Writing-Skills "$tmp"
cp -R "$tmp/research-paper-writing" "$SKILLS_DEST/"
```

Codex picks it up on next session under the skill name `research-paper-writing`.

## Rules

- Treat Prof. Peng's methodology as a starting point, not a hard contract.
  If the target venue (e.g., CHI, HCI) prefers a different narrative
  structure, adapt.
- Never invent references or experimental numbers. Flag missing content.
- Coordinate with `academic-research-suite` when both are installed: defer
  orchestration and citation integrity to `academic-pipeline`; this pack
  only handles section-level writing.
- Preserve MIT attribution to Master-cai when redistributing the upstream
  content.

## Related

- `academic-research-suite` — full pipeline (research → review → revise).
- `autoresearch-suite` — for experiment-running loops that feed the
  Experiments section.

## Upstream references

- Source: https://github.com/Master-cai/Research-Paper-Writing-Skills
- Original notes: https://github.com/pengsida/learning_research
- License: MIT
