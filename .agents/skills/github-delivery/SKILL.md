---
name: github-delivery
description: Use when committing, pushing, opening PRs, handling review comments, triaging issues, or debugging GitHub Actions for the current repository.
---

# GitHub Delivery

Use this when the work is about shipping changes through GitHub.

## Workflow

1. Resolve the current local branch and remote first.
2. Use `github` for repo, PR, or issue triage.
3. Use `yeet` for commit, push, and PR publication flows.
4. Use `gh-fix-ci` for failing checks and Actions logs.
5. Use `gh-address-comments` for review feedback on an existing PR.
6. Keep local checkout state and remote state aligned.

## Guardrails

- Do not skip security or diff review before publishing.
- Do not assume a PR exists just because the branch is pushed.
- Keep the workflow narrow: triage, fix CI, address review, or publish.
