---
name: skill-authoring
description: Write portable agent skills that follow the agentskills.io open standard. Covers frontmatter, content style, helper scripts, examples, version discipline, and harness adapters. Use when creating a new skill for grand-skills, openai/skills, claude-skills, or any agent harness.
provides: skill-authoring
version: 1.0.0
---

# Skill Authoring

A skill is a folder a discoverable agent can read and act on. The format
is simple, but small choices make the difference between a skill that an
agent picks up reliably and one it ignores.

## When to use

- Creating a new portable skill in grand-skills or any sibling pack.
- Refactoring an existing skill so it works across more harnesses.
- Reviewing a contributor's skill PR.

## Required layout

```text
my-skill/
├── SKILL.md                  # required
├── agents/
│   └── openai.yaml           # optional UI metadata
├── scripts/                  # optional helper bash/python scripts
│   └── *.sh
├── examples/                 # optional concrete examples
│   └── *.md
└── install-deps.sh           # optional one-shot dep install for the skill
```

`SKILL.md` is the only required file. Everything else is optional. Keep
the layout flat — nested skills are not supported in most harnesses.

## Frontmatter contract

```yaml
---
name: my-skill                # lowercase-hyphenated, unique
description: One sentence that tells the agent when to use this skill.
provides: capability-tag      # used by conflict resolver
version: 1.0.0                # semver; required for smart-sync
---
```

Optional fields supported by harnesses:

```yaml
license: MIT
categories: [security, data]
maintainers: ["@you"]
keywords: ["pdf", "extraction"]
```

Hard rules for frontmatter:

- `name` must match the directory name.
- `description` must answer "when should I (the agent) load this?" in one
  sentence. Avoid "this skill is about ...".
- `version` follows SemVer 2 — bump per the rules in `release-management`.
- `provides` should be a stable capability tag that conflict resolvers
  can use; do not change it across versions.

## Content structure

A skill is a procedure, not a reference book. Use this skeleton:

```md
# <Display name>

One paragraph framing the problem the skill solves.

## When to use

Bulleted list. Match each bullet to a likely user request.

## Workflow

Numbered steps the agent can follow. Concrete commands welcome.

## Hard rules

Things the agent must not do.

## Adaptation rules

How to fit the workflow to the project at hand.

## Verification

Checklist the agent should walk before declaring done.
```

Style:

- Direct voice. "Run X." not "It is recommended to run X."
- Show the command. Don't paraphrase the man page.
- Cite sources for non-trivial claims (URLs welcome).
- Keep one screen per section. Long skills lose attention.

## Helper scripts

- Write portable `bash` (POSIX-leaning) by default.
- Set `set -euo pipefail`.
- Accept `--root`, `--dry-run`, `--verbose` for portability.
- Never assume a project layout the user did not declare.
- Never modify outside the project root.

## Versioning

- `1.0.0` for the first stable release.
- Patch bump for typo / link / source refresh.
- Minor bump for a new section or new capability that does not break
  callers.
- Major bump when a "Hard rule" changes or content layout shifts in a
  way that breaks downstream skills consuming this one.

`skill-evolution-engine` reads `version:` for the smart-sync UPGRADE
path. Keep it monotonically increasing.

## Per-harness portability

- The canonical SKILL.md works for Codex, Pi, Claude Code, OpenCode.
- For Cursor / Continue / Cline / Roo, write `.mdc` / `.md` adapters via
  `agent-harness-compatibility`.
- For Aider, the concat adapter handles it.
- Do **not** embed harness-specific instructions inside the SKILL.md
  body — keep that in the adapter.

## Cross-skill linking

- Refer to other skills by name in backticks: `` `auth-identity` ``.
- Do not hardcode paths; another harness lays them out differently.
- For "must run before this", say so in plain language and let the
  orchestrator route.

## Examples folder

When the workflow is non-obvious, ship an `examples/` folder with one
or two end-to-end runs the agent can read for grounding.

## Hard rules

- Never write a skill that asks for credentials in plaintext.
- Never write a skill that exfiltrates project content to a third party
  without explicit user opt-in.
- Never claim a skill works on a harness you did not test on.
- Never copy upstream skills without preserving their license + a
  pointer in `catalog/registry.yaml`.

## Adaptation rules

- For org-internal skills, add an `internal: true` flag and keep them
  out of public profiles.
- For OSS distribution, dual-license under MIT or Apache-2.0 to match
  the rest of the pack.
- For research / academic skills, cite the paper(s) the workflow comes
  from.

## Cross-skill integration

- `skill-evolution-engine` audits and upgrades skills.
- `adaptive-master-architect` decides which skills the project needs.
- `agent-harness-compatibility` writes the adapter per harness.
- `model-provider-config` declares which capabilities the model can
  honor.

## Verification before sign-off

- [ ] Frontmatter valid (`name`, `description`, `provides`, `version`)
- [ ] Workflow has concrete, testable steps
- [ ] Hard rules listed
- [ ] Verification checklist present
- [ ] Helper scripts pass `bash -n` and `shellcheck`
- [ ] Examples (if any) actually run
- [ ] Cross-references to other skills are by name, not path
