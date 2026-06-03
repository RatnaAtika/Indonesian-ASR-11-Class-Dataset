#!/usr/bin/env bash
set -Eeuo pipefail
REMOTE="${GDRIVE_REMOTE:-gdrive:}"
DRIVE_ROOT="${DRIVE_ROOT:-ASR_Colab_A100}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$REMOTE$DRIVE_ROOT/Colab_ASR_A100_Training"
command -v rclone >/dev/null || { echo "ERROR: rclone not installed/configured"; exit 2; }
echo "Upload Colab code package -> $DEST"
rclone sync "$HERE" "$DEST" --progress --transfers 8 --checkers 16 --fast-list \
  --exclude '.ipynb_checkpoints/**' \
  --exclude '__pycache__/**'
