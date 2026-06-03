#!/usr/bin/env bash
set -Eeuo pipefail
source /content/asr_work/colab_env.sh
cd "$REPO"
mkdir -p "$DRIVE_RESULTS_ROOT/manual_collect"
for slot in training/m02b_whisper_small_ft/runs training/m02b_whisper_medium_ft/runs; do
  if [ -d "$slot" ]; then
    rsync -aH --include='*/' --include='run_paper_*_colab_a100*/***' --exclude='*' "$slot/" "$DRIVE_RESULTS_ROOT/manual_collect/$slot/"
  fi
done
rsync -aH ubuntu_logs/ "$DRIVE_RESULTS_ROOT/ubuntu_logs/" || true
echo "Collected to $DRIVE_RESULTS_ROOT/manual_collect"
