---
name: portable-project-adapter
description: Adapt reusable skill packs to the current repository by reading local context, selecting a profile, and stripping source-project assumptions.
---

# Portable Project Adapter

Use this skill first when moving reusable skills into a new repository.

## Workflow

1. Read local context: `README.md`, `AGENTS.md`, package manifests, deployment files, and domain docs.
2. Classify the repository into a profile: `design-heavy`, `workflow-heavy`, `docs-site`, or `default`.
3. Load only the smallest useful skill set from this repo.
4. Rewrite instructions in project-native terms.
5. Keep local security, deployment, and data rules intact.

## Rules

- Do not carry source-project names or data shapes into a new codebase by default.
- Treat upstream references as guidance, not as hard requirements.
- Prefer explicit local config files over assumptions.
- If a project-specific contract is missing, create a local placeholder in the target repo instead of inventing one globally.
