#!/usr/bin/env bash
# install-deps.sh — fetch upstream uditgoenka/autoresearch and copy its
# Codex-ready skill directory into $SKILLS_DEST. Called only by bootstrap.sh.
set -euo pipefail

log() { printf '[autoresearch-suite] %s\n' "$*"; }

DEST="${SKILLS_DEST:-}"
if [[ -z "$DEST" ]]; then
  log "SKILLS_DEST not set; skipping."
  exit 0
fi

if ! command -v git >/dev/null 2>&1; then
  log "git not found; skipping."
  exit 0
fi

FORCE="${SKILLS_FORCE:-0}"
UPSTREAM="https://github.com/uditgoenka/autoresearch.git"
SKILL_NAME="autoresearch"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if ! git clone --depth 1 "$UPSTREAM" "$tmp/src" 2>/dev/null; then
  log "Upstream clone failed; skipping."
  exit 0
fi

# Upstream Codex layout: .agents/skills/autoresearch/
src_dir=""
for cand in "$tmp/src/.agents/skills/autoresearch" \
            "$tmp/src/.codex/skills/autoresearch" \
            "$tmp/src/claude-plugin/skills/autoresearch"; do
  if [[ -d "$cand" ]]; then
    src_dir="$cand"
    break
  fi
done

if [[ -z "$src_dir" ]]; then
  log "Upstream skill directory not found; skipping."
  exit 0
fi

mkdir -p "$DEST"
dst="$DEST/$SKILL_NAME"
if [[ -e "$dst" ]]; then
  if [[ "$FORCE" != "1" ]]; then
    log "Skipping existing '$dst'."
    exit 0
  fi
  rm -rf "$dst"
fi

cp -a "$src_dir" "$dst"
log "Installed $SKILL_NAME → $dst"
