#!/usr/bin/env bash
# install-deps.sh — fetch Master-cai/Research-Paper-Writing-Skills into
# $SKILLS_DEST. Called only by scripts/bootstrap.sh.
set -euo pipefail

log() { printf '[research-paper-writing] %s\n' "$*"; }

DEST="${SKILLS_DEST:-}"
if [[ -z "$DEST" ]]; then
  log "SKILLS_DEST not set by bootstrap; skipping."
  exit 0
fi

if ! command -v git >/dev/null 2>&1; then
  log "git not found; skipping."
  exit 0
fi

FORCE="${SKILLS_FORCE:-0}"
UPSTREAM="https://github.com/Master-cai/Research-Paper-Writing-Skills.git"
SKILL_NAME="research-paper-writing"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if ! git clone --depth 1 "$UPSTREAM" "$tmp/src" 2>/dev/null; then
  log "Upstream clone failed; skipping."
  exit 0
fi

# Upstream lays the skill out as a top-level directory "research-paper-writing/".
src_dir=""
for cand in "$tmp/src/$SKILL_NAME" "$tmp/src/skills/$SKILL_NAME"; do
  if [[ -d "$cand" ]]; then
    src_dir="$cand"
    break
  fi
done

if [[ -z "$src_dir" ]]; then
  log "Upstream layout unexpected; skipping."
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
