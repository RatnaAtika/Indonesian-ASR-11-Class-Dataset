#!/usr/bin/env bash
# install-deps.sh — fetch the upstream academic-research skills into the same
# destination this repo installs into. Called only by scripts/bootstrap.sh.
set -euo pipefail

log() { printf '[academic-research-suite] %s\n' "$*"; }

DEST="${SKILLS_DEST:-}"
if [[ -z "$DEST" ]]; then
  log "SKILLS_DEST not set by bootstrap; skipping."
  exit 0
fi

if ! command -v git >/dev/null 2>&1; then
  log "git not found; cannot fetch upstream suite."
  exit 0
fi

FORCE="${SKILLS_FORCE:-0}"

UPSTREAM_CODEX="https://github.com/Imbad0202/academic-research-skills-codex.git"
UPSTREAM_CLAUDE="https://github.com/Imbad0202/academic-research-skills.git"
SUB_SKILLS=(deep-research academic-paper academic-paper-reviewer academic-pipeline)

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

clone_ok=0
if git clone --depth 1 "$UPSTREAM_CODEX" "$tmp/src" 2>/dev/null; then
  clone_ok=1
  log "Cloned Codex sibling."
elif git clone --depth 1 "$UPSTREAM_CLAUDE" "$tmp/src" 2>/dev/null; then
  clone_ok=1
  log "Cloned Claude Code source as fallback."
fi

if [[ "$clone_ok" -ne 1 ]]; then
  log "Upstream clone failed; skipping. Run bootstrap again with network access."
  exit 0
fi

# Upstream layouts we know about: skills/<name>, <name>/, or top-level <name>/.
src_root=""
for cand in "$tmp/src/skills" "$tmp/src"; do
  if [[ -d "$cand/deep-research" || -d "$cand/academic-pipeline" ]]; then
    src_root="$cand"
    break
  fi
done

if [[ -z "$src_root" ]]; then
  log "Could not locate upstream skills directory; skipping."
  exit 0
fi

mkdir -p "$DEST"
for s in "${SUB_SKILLS[@]}"; do
  src="$src_root/$s"
  dst="$DEST/$s"
  if [[ ! -d "$src" ]]; then
    log "Upstream skill '$s' not found; skipping."
    continue
  fi
  if [[ -e "$dst" ]]; then
    if [[ "$FORCE" != "1" ]]; then
      log "Skipping existing '$dst' (re-run bootstrap with --force to overwrite)."
      continue
    fi
    rm -rf "$dst"
  fi
  cp -a "$src" "$dst"
  log "Installed $s → $dst"
done
