#!/usr/bin/env bash
set -Eeuo pipefail
DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then DRY_RUN=1; fi
REMOTE="${GDRIVE_REMOTE:-gdrive:}"
DRIVE_ROOT="${DRIVE_ROOT:-ASR_Colab_A100}"
SRC_REPO="${SRC_REPO:-$HOME/AI/Dataset_ASR_Train_Linux}"
DATA_SRC="$SRC_REPO/Processed_Balanced19_v7_natural_synth/Dataset_Balanced19"
SPLIT_SRC="$SRC_REPO/training/data_final"
DATA_DEST="$REMOTE$DRIVE_ROOT/Data/Processed_Balanced19_v7_natural_synth/Dataset_Balanced19"
SPLIT_DEST="$REMOTE$DRIVE_ROOT/Data/training/data_final"
command -v rclone >/dev/null || { echo "ERROR: rclone not installed/configured"; exit 2; }
test -d "$DATA_SRC" || { echo "ERROR: missing DATA_SRC=$DATA_SRC"; exit 3; }
test -d "$SPLIT_SRC" || { echo "ERROR: missing SPLIT_SRC=$SPLIT_SRC"; exit 3; }
args=(--progress --transfers 8 --checkers 16 --fast-list)
if [[ "$DRY_RUN" == 1 ]]; then args+=(--dry-run); fi
echo "Upload dataset existing source -> Google Drive (no local staging duplicate)"
rclone copy "$DATA_SRC" "$DATA_DEST" "${args[@]}"
echo "Upload split TSV"
rclone copy "$SPLIT_SRC" "$SPLIT_DEST" "${args[@]}"
