---
name: superpowers-suite
description: Apply the reusable Superpowers workflow stack to the current repository: brainstorming, planning, debugging, TDD, verification, and agent orchestration.
---

# Superpowers Suite

Use this when a project needs structured execution instead of ad-hoc prompting.

## Workflow

1. Read the current repository and classify the task.
2. Pick the smallest useful process skill:
   - `brainstorming` for feature or behavior changes
   - `writing-plans` for multi-step implementation
   - `systematic-debugging` for bugs, regressions, or confusing failures
   - `test-driven-development` for risky new behavior
   - `verification-before-completion` before commit, push, or handoff
   - `executing-plans` or `subagent-driven-development` when a task should be executed step by step
   - `dispatching-parallel-agents` when work can be split cleanly
   - `using-git-worktrees` when isolation will reduce collision risk
3. Keep local project rules ahead of generic workflow guidance.
4. Prefer small, reviewable changes with explicit verification.

## Guardrails

- Do not force process overhead onto tiny, self-evident fixes.
- Do not skip verification when the change touches behavior, data flow, or publish steps.
- Use the current repository's conventions first, then apply Superpowers only where it adds discipline.
