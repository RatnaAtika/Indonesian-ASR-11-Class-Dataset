---
name: autoresearch-suite
description: Autonomous goal-directed iteration skill. Takes a mechanical metric and a verify command and runs a modify → verify → keep/discard loop until the metric converges or an iteration cap is hit. Use this skill when the project has a measurable target (coverage, bundle size, benchmark score, error count, latency).
provides:
  - autonomous-iteration-loop
  - security-audit-loop
  - debug-loop
  - fix-loop
  - ship-workflow
aliases:
  - autoresearch
  - karpathy-loop
upstream:
  repo: https://github.com/uditgoenka/autoresearch
  codex_source: .agents/skills/autoresearch
  license: MIT
  based_on: https://github.com/karpathy/autoresearch
relevance:
  project_types:
    - software
    - ml
    - data-pipeline
    - backend
    - frontend
    - research
  signals:
    - tests/, __tests__/, spec/
    - package.json has "test" script
    - pyproject.toml + pytest / hatch / tox
    - benchmark/, bench/, benchmarks/
    - .github/workflows/ has CI job
    - README mentions coverage, p95, SOTA, latency, bundle size
---

# Autoresearch Suite (portable wrapper)

Portable wrapper for
[uditgoenka/autoresearch](https://github.com/uditgoenka/autoresearch). The
upstream repo already ships a Codex-ready layout at
`.agents/skills/autoresearch/`; this wrapper fetches that directory and
documents the 11 commands so the agent knows when to route what.

Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch):
> "Set the GOAL → The agent runs the LOOP → You wake up to results."

## The loop

```
1. Review current state + git history + results log
2. Pick the next change (what worked, what failed, what's untried)
3. Make ONE focused change
4. Git commit (before verification)
5. Run mechanical verification (tests, benchmarks, scores)
6. Improved → keep. Worse → git revert. Crashed → fix or skip.
7. Log the result
8. Repeat until interrupt or N iterations.
```

## Commands (Codex invocation)

In Codex the skill is invoked via `$autoresearch` mention syntax. Subcommands
are keywords.

| Command | Use for |
| --- | --- |
| `$autoresearch` | Run the iteration loop (unbounded unless `Iterations: N`) |
| `$autoresearch plan` | Interactive wizard to define Goal / Scope / Metric / Verify |
| `$autoresearch security` | STRIDE + OWASP + red-team audit (read-only by default) |
| `$autoresearch ship` | Universal shipping checklist (9 output types) |
| `$autoresearch debug` | Autonomous bug-hunting loop |
| `$autoresearch fix` | Iteratively repair until tests / types / lint clean |
| `$autoresearch scenario` | Scenario / edge-case generator across 12 dimensions |
| `$autoresearch predict` | 5-expert pre-analysis panel |
| `$autoresearch learn` | Autonomous documentation engine |
| `$autoresearch reason` | Adversarial refinement with blind-judge panel |
| `$autoresearch probe` | Requirement interrogation with 8 personas |

## When to use

- The user has a measurable target: "coverage 72 → 90", "p95 under 200 ms",
  "zero ESLint errors", "bundle < 300 kB".
- The project has `git` history and at least one verify command that outputs
  a comparable number or pass/fail.
- A security audit or large-scale bug hunt is needed and the user accepts
  autonomous investigation.

## When NOT to use

- No mechanical verification exists and none can be defined.
- Subjective work (copy tone, brand voice, designs without metrics) — use
  `$autoresearch reason` instead of the plain loop.
- Repos without git history.

## Install (auto via bootstrap)

The pack's `install-deps.sh` fetches the upstream `.agents/skills/autoresearch`
directory into `$SKILLS_DEST/autoresearch`:

```bash
git clone --depth 1 https://github.com/uditgoenka/autoresearch "$tmp"
cp -R "$tmp/.agents/skills/autoresearch" "$SKILLS_DEST/"
```

Or manually:

```bash
# project-local
cp -R path/to/autoresearch/.agents/skills/autoresearch .agents/skills/
# global
cp -R path/to/autoresearch/.agents/skills/autoresearch "$HOME/.codex/skills/"
```

## Rules

- **Mechanical verification only.** "Looks good" does not count. Every
  iteration must produce a pass/fail or a comparable number.
- **One change per iteration.** Atomic. If it breaks, you know why.
- **Commit before verify.** `git revert` preserves failed experiments; the
  agent MUST read `git log` + `git diff` before each iteration.
- **Guard command.** When provided, must pass for the change to be kept,
  even if the metric improves.
- **Never auto-run `$autoresearch security --fix`** without explicit user
  confirmation. The default security mode is read-only.
- **Respect the safety guardrails** of the outer environment. Do not push
  to main, run mass deletes, or hit production infra from inside the loop.
- **Stop condition.** Honour `Iterations: N` strictly. Infinite loops are
  only allowed when the user explicitly opts in and can interrupt.
- **Attribution.** MIT; keep attribution to Udit Goenka and Karpathy when
  redistributing.

## Related

- Pair with `academic-research-suite` → Experiment Agent role: autoresearch
  runs the experiment loop between Stage 1 RESEARCH and Stage 2 WRITE.
- Pair with `superpowers-suite` → `systematic-debugging`, `writing-plans`,
  `verification-before-completion` set the discipline autoresearch enforces.
- Pair with `github-delivery` → `$autoresearch ship` output plugs into the
  PR / release flow.

## Upstream references

- Source: https://github.com/uditgoenka/autoresearch
- Karpathy's autoresearch: https://github.com/karpathy/autoresearch
- License: MIT
