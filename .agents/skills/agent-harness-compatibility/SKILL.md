---
name: agent-harness-compatibility
description: Make every grand-skill discoverable and usable across multiple agent harnesses — Codex CLI, Pi, Cursor, Claude Code, Aider, OpenCode, Continue, Cline, Roo, and any custom runner that reads SKILL.md files. Documents per-harness install paths, manifest formats, and how to keep one source of truth without forking the skill content.
provides: agent-harness-compatibility
version: 1.0.0
---

# Agent Harness Compatibility

Each agent harness has its own way of "discovering" skills. The skill
content does not need to fork — only the install location and manifest do.
This skill maps each common harness to the path/manifest it expects, so
`scripts/configure.sh` can drop the right adapter without copying files.

## When to use

- First time setting up grand-skills in a new harness.
- Adding a second harness to an existing project.
- A harness sees the files but ignores them — the manifest is wrong.
- The user wants a single source of truth that every agent reads.

## Harness map

| Harness | Skills directory | Manifest / loader | Reads our SKILL.md? | Notes |
| --- | --- | --- | --- | --- |
| **Codex CLI (OpenAI)** | `~/.codex/skills/<skill>/` (global) or `<project>/.agents/skills/<skill>/` | `SKILL.md` frontmatter (`name`, `description`) + optional `agents/openai.yaml` | yes | install via `$skill-installer` or our `scripts/install.sh` |
| **Pi** | `<project>/.pi/agent/git/...` and `<user>/.agents/skills/<skill>/` | `SKILL.md` frontmatter | yes | accepts the same SKILL.md format |
| **Cursor** | `<project>/.cursor/rules/` (project) or `~/.cursor/rules/` (global) | `*.mdc` files; rule body is markdown | needs `.mdc` adapter (auto-generated) | one `.mdc` per skill |
| **Claude Code** | `<project>/.claude/skills/<skill>/` | `SKILL.md` frontmatter | yes | identical to Codex layout |
| **Aider** | `<project>/.aider.conf.yml` + repo `CONVENTIONS.md` | preloaded text files via `read:` | needs concat adapter | aggregates into one `CONVENTIONS.md` |
| **OpenCode** | `<project>/.opencode/skills/<skill>/` | `SKILL.md` | yes | new but follows the agent-skills.io standard |
| **Continue** (VS Code) | `<project>/.continue/rules/` | `*.md` rule files | needs flat-md adapter | one md per skill |
| **Cline / Roo** | `<project>/.clinerules/` or `<project>/.roo/` | flat markdown | needs flat-md adapter | one md per skill |
| **Generic / custom** | `<project>/.agents/skills/<skill>/` | SKILL.md | yes | recommend this layout for new harnesses |

The official open standard the layout follows is **agentskills.io**.
Anything that conforms reads `SKILL.md` directly.

## Single-source-of-truth strategy

We keep canonical content under `<project>/.agents/skills/<skill>/SKILL.md`.
Adapters for each harness are **symlinks or generated wrappers**, not copies.
The matrix:

| Harness | Adapter shape |
| --- | --- |
| Codex / Pi / Claude Code / OpenCode | symlink the directory |
| Cursor | per-skill `*.mdc` that `@include`s the SKILL.md |
| Continue / Cline / Roo | per-skill `*.md` that includes the SKILL.md |
| Aider | one concatenated `CONVENTIONS.md` (regenerated on change) |

`scripts/configure.sh` writes the adapter that matches the harness it
detected. If multiple harnesses are present, all adapters are generated.

## Detection signals (what `configure.sh` looks at)

- `$CODEX_HOME` set or `~/.codex/` exists → Codex
- `~/.pi/` or `pi-coding-agent` on PATH → Pi
- `<project>/.cursor/` → Cursor
- `<project>/.claude/` → Claude Code
- `<project>/.aider.conf.yml` → Aider
- `<project>/.opencode/` → OpenCode
- `<project>/.continue/` → Continue
- `<project>/.clinerules/` or `<project>/.roo/` → Cline / Roo
- otherwise: write the generic adapter at `<project>/.agents/skills/`

## Hard rules

- One canonical content tree. Adapters are symlinks or generated, not
  hand-copied.
- Never embed harness-specific instructions inside SKILL.md. Keep the
  difference in the adapter, not the content.
- Never auto-overwrite an existing `*.mdc`, `*.md`, or `CONVENTIONS.md`
  the user wrote by hand. Smart-sync rules apply (skip identical, keep
  diverged, upgrade older).
- Never assume a harness loads frontmatter. If unsure, the adapter must
  duplicate the description as plain text near the top.

## Per-harness usage notes

### Codex CLI

- Pre-installed system skills live at `skills/.system/*` upstream.
- Custom skills live at `~/.codex/skills/<skill>/SKILL.md`.
- Restart Codex after install.
- The `$skill-installer` shell function ships with Codex; we provide
  `scripts/install.sh` as a portable equivalent.

### Pi

- Skills under `<user>/.agents/skills/<skill>/`.
- Per-project skills under `<project>/.agents/skills/<skill>/`.
- Pi reads SKILL.md frontmatter without modification.
- For long-context Pi runs, set `model-provider-config` first so all
  skills can be preloaded.

### Cursor

- Adapter creates `<project>/.cursor/rules/<skill>.mdc` containing:

  ```mdc
  ---
  description: <skill description from SKILL.md>
  globs: ["**/*"]
  alwaysApply: false
  ---

  @include ../../.agents/skills/<skill>/SKILL.md
  ```

- Rules with `alwaysApply: true` are preloaded; we leave most at false
  to keep context budget healthy.

### Claude Code

- Skills under `<project>/.claude/skills/<skill>/`.
- Symlink works; or copy on Windows where symlinks are restricted.

### Aider

- Aider does not load multi-file skill folders natively.
- Adapter generates `<project>/.aider/grand-skills.md` (one file).
- Add `read: [.aider/grand-skills.md]` to `.aider.conf.yml`.

### OpenCode

- New, follows agent-skills.io. Same layout as Codex.

### Continue / Cline / Roo

- Each gets a flat `<skill>.md` under their rules dir, with a 1-line
  pointer to the canonical SKILL.md in `.agents/skills/`.

## Verification before sign-off

- [ ] One canonical SKILL.md per skill, under `.agents/skills/<skill>/`.
- [ ] At least one harness adapter present and pointing at the canonical.
- [ ] `scripts/configure.sh` shows `harness.detected` is non-empty.
- [ ] The harness picks up at least one skill (smoke test: ask the agent
      to run `grand-saas-orchestrator` and see if it loads).
