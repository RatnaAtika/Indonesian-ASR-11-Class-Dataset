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
ARCHIVE_SRC="${ARCHIVE_SRC:-$SRC_REPO/Colab_ASR_A100_Training/archives}"
ARCHIVE_DEST="$REMOTE$DRIVE_ROOT/Data/_archives"
command -v rclone >/dev/null || { echo "ERROR: rclone not installed/configured"; exit 2; }
test -d "$DATA_SRC" || { echo "ERROR: missing DATA_SRC=$DATA_SRC"; exit 3; }
test -d "$SPLIT_SRC" || { echo "ERROR: missing SPLIT_SRC=$SPLIT_SRC"; exit 3; }
args=(--progress --transfers 8 --checkers 16 --fast-list)
if [[ "$DRY_RUN" == 1 ]]; then args+=(--dry-run); fi
echo "Upload dataset existing source -> Google Drive (no local staging duplicate)"
rclone copy "$DATA_SRC" "$DATA_DEST" "${args[@]}"
echo "Upload split TSV"
rclone copy "$SPLIT_SRC" "$SPLIT_DEST" "${args[@]}"
if [[ -d "$ARCHIVE_SRC" ]]; then
  if [[ -f "$ARCHIVE_SRC/dataset_balanced19_v7.tar" && -f "$ARCHIVE_SRC/data_final.tar" ]]; then
    echo "Upload fast-bootstrap tar archives"
    rclone copy "$ARCHIVE_SRC" "$ARCHIVE_DEST" "${args[@]}" --include 'dataset_balanced19_v7.tar' --include 'data_final.tar' --include 'SHA256SUMS.txt' --exclude '*'
  else
    echo "Archive dir exists but expected tar files are missing: $ARCHIVE_SRC"
  fi
else
  echo "No archive dir found ($ARCHIVE_SRC). Optional: run scripts/build_colab_data_archives.sh for faster Colab bootstrap."
fi
