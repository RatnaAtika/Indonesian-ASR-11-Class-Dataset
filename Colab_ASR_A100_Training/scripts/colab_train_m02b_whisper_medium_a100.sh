#!/usr/bin/env bash
set -Eeuo pipefail
source /content/asr_work/colab_env.sh
cd "$REPO"
mkdir -p ubuntu_logs
RUN_ID="run_paper_$(date +%Y%m%d_%H%M%S)_colab_a100"
RUN_DIR="training/m02b_whisper_medium_ft/runs/$RUN_ID"
DEST="$DRIVE_RESULTS_ROOT/m02b_whisper_medium_ft/$RUN_ID"
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
    echo "[medium-a100] periodic sync -> $DEST"
    sync_once
  done
}
SYNC_PID=""
trap 'status=$?; echo "[medium-a100] final sync on exit -> $DEST"; sync_once; if [ -n "${SYNC_PID:-}" ]; then kill "$SYNC_PID" 2>/dev/null || true; fi; exit $status' EXIT
periodic_sync & SYNC_PID=$!
BATCH="${A100_MEDIUM_BATCH_SIZE:-8}"
ACCUM="${A100_MEDIUM_GRAD_ACCUM:-4}"
NUM_WORKERS="${A100_NUM_WORKERS:-2}"
echo "[medium-a100] RUN_DIR=$RUN_DIR batch=$BATCH grad_accum=$ACCUM effective=$((BATCH*ACCUM)) workers=$NUM_WORKERS sync_interval=${SYNC_INTERVAL_SEC}s"
TRAIN_LOG="ubuntu_logs/train_m02b_medium_${RUN_ID}.log"
TEST_LOG="ubuntu_logs/test_m02b_medium_${RUN_ID}.log"
echo "[medium-a100] quiet Colab output mode. Full train log: $TRAIN_LOG"
echo "[medium-a100] To inspect without lag: tail -n 80 $REPO/$TRAIN_LOG"
if [[ "${A100_CONSOLE_LOG:-0}" == "1" ]]; then
  time python3 training/m02b_whisper_medium_ft/train.py \
    --run-dir "$RUN_DIR" --data-root "$DATA_ROOT" --data-final "$DATA_FINAL" \
    --epochs 5 --batch-size "$BATCH" --grad-accum "$ACCUM" \
    --lr 1e-5 --warmup-steps 500 --num-workers "$NUM_WORKERS" --seed 42 --disable-tqdm \
    2>&1 | tee "$TRAIN_LOG"
else
  time python3 training/m02b_whisper_medium_ft/train.py \
    --run-dir "$RUN_DIR" --data-root "$DATA_ROOT" --data-final "$DATA_FINAL" \
    --epochs 5 --batch-size "$BATCH" --grad-accum "$ACCUM" \
    --lr 1e-5 --warmup-steps 500 --num-workers "$NUM_WORKERS" --seed 42 --disable-tqdm \
    > "$TRAIN_LOG" 2>&1 || { status=$?; echo "[medium-a100] TRAIN FAILED; last log lines:"; tail -n 120 "$TRAIN_LOG"; exit $status; }
fi
echo "[medium-a100] train complete. Last train log lines:"
tail -n 40 "$TRAIN_LOG"
echo "[medium-a100] running test. Full test log: $TEST_LOG"
if [[ "${A100_CONSOLE_LOG:-0}" == "1" ]]; then
  python3 training/m02b_whisper_medium_ft/test.py --run-dir "$RUN_DIR" --data-root "$DATA_ROOT" --data-final "$DATA_FINAL" \
    2>&1 | tee "$TEST_LOG"
else
  python3 training/m02b_whisper_medium_ft/test.py --run-dir "$RUN_DIR" --data-root "$DATA_ROOT" --data-final "$DATA_FINAL" \
    > "$TEST_LOG" 2>&1 || { status=$?; echo "[medium-a100] TEST FAILED; last log lines:"; tail -n 120 "$TEST_LOG"; exit $status; }
fi
echo "[medium-a100] test complete. Last test log lines:"
tail -n 40 "$TEST_LOG"
rsync -aH --info=progress2 "$RUN_DIR/" "$DEST/"
rsync -aH ubuntu_logs/ "$DRIVE_RESULTS_ROOT/ubuntu_logs/" || true
python3 "$DRIVE_COLAB_ROOT/scripts/colab_write_results_summary.py" --results-root "$DRIVE_RESULTS_ROOT" || true
echo "Saved complete run results to $DEST"
echo "Paper summary: $DRIVE_RESULTS_ROOT/paper_training_time_summary.md"
python3 "$DRIVE_COLAB_ROOT/scripts/colab_auto_disconnect.py" || true
