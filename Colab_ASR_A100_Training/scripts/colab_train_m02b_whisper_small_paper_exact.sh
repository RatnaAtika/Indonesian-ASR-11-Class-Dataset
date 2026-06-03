#!/usr/bin/env bash
set -Eeuo pipefail
source /content/asr_work/colab_env.sh
cd "$REPO"
mkdir -p ubuntu_logs
RUN_ID="run_paper_$(date +%Y%m%d_%H%M%S)_colab_a100_paper_exact"
RUN_DIR="training/m02b_whisper_small_ft/runs/$RUN_ID"
DEST="$DRIVE_RESULTS_ROOT/m02b_whisper_small_ft/$RUN_ID"
mkdir -p "$(dirname "$DEST")"
SYNC_INTERVAL_SEC="${A100_SYNC_INTERVAL_SEC:-600}"
sync_once() {
  if [ -d "$RUN_DIR" ]; then
    mkdir -p "$DEST"
    rsync -aH "$RUN_DIR/" "$DEST/" || true
    rsync -aH ubuntu_logs/ "$DRIVE_RESULTS_ROOT/ubuntu_logs/" || true
  fi
}
periodic_sync() {
  while true; do
    sleep "$SYNC_INTERVAL_SEC"
    echo "[small-paper-exact] periodic sync -> $DEST"
    sync_once
  done
}
SYNC_PID=""
trap 'status=$?; echo "[small-paper-exact] final sync on exit -> $DEST"; sync_once; if [ -n "${SYNC_PID:-}" ]; then kill "$SYNC_PID" 2>/dev/null || true; fi; exit $status' EXIT
periodic_sync & SYNC_PID=$!
echo "[small-paper-exact] RUN_DIR=$RUN_DIR batch=8 grad_accum=4 effective=32 sync_interval=${SYNC_INTERVAL_SEC}s"
time python3 training/m02b_whisper_small_ft/train.py \
  --run-dir "$RUN_DIR" --data-root "$DATA_ROOT" --data-final "$DATA_FINAL" \
  --epochs 5 --batch-size 8 --grad-accum 4 \
  --lr 1e-5 --warmup-steps 500 --gradient-checkpointing --seed 42 \
  2>&1 | tee "ubuntu_logs/train_m02b_small_${RUN_ID}.log"
python3 training/m02b_whisper_small_ft/test.py --run-dir "$RUN_DIR" --data-root "$DATA_ROOT" --data-final "$DATA_FINAL" \
  2>&1 | tee "ubuntu_logs/test_m02b_small_${RUN_ID}.log"
rsync -aH --info=progress2 "$RUN_DIR/" "$DEST/"
rsync -aH ubuntu_logs/ "$DRIVE_RESULTS_ROOT/ubuntu_logs/" || true
python3 "$DRIVE_COLAB_ROOT/scripts/colab_write_results_summary.py" --results-root "$DRIVE_RESULTS_ROOT" || true
echo "Saved complete run results to $DEST"
echo "Paper summary: $DRIVE_RESULTS_ROOT/paper_training_time_summary.md"
python3 "$DRIVE_COLAB_ROOT/scripts/colab_auto_disconnect.py" || true
