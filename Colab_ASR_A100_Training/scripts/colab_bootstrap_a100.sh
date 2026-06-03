#!/usr/bin/env bash
set -Eeuo pipefail
DRIVE_PROJECT_ROOT="${DRIVE_PROJECT_ROOT:-/content/drive/MyDrive/ASR_Colab_A100}"
DRIVE_COLAB_ROOT="${DRIVE_COLAB_ROOT:-$DRIVE_PROJECT_ROOT/Colab_ASR_A100_Training}"
DRIVE_DATA_ROOT="${DRIVE_DATA_ROOT:-$DRIVE_PROJECT_ROOT/Data/Processed_Balanced19_v7_natural_synth/Dataset_Balanced19}"
DRIVE_DATA_FINAL="${DRIVE_DATA_FINAL:-$DRIVE_PROJECT_ROOT/Data/training/data_final}"
DRIVE_RESULTS_ROOT="${DRIVE_RESULTS_ROOT:-$DRIVE_PROJECT_ROOT/Results}"
COLAB_WORK_ROOT="${COLAB_WORK_ROOT:-/content/asr_work}"
COLAB_REPO="${COLAB_REPO:-$COLAB_WORK_ROOT/Paper_Datatset_SOTA}"
USE_LOCAL_SSD="${USE_LOCAL_SSD:-1}"
LOCAL_DATA_ROOT="${LOCAL_DATA_ROOT:-/content/asr_data/Processed_Balanced19_v7_natural_synth/Dataset_Balanced19}"
LOCAL_DATA_FINAL="${LOCAL_DATA_FINAL:-$COLAB_REPO/training/data_final}"
nvidia-smi || true
mkdir -p "$COLAB_WORK_ROOT" "$DRIVE_RESULTS_ROOT"
python3 -m pip install -q --upgrade pip
python3 -m pip install -q -r "$DRIVE_COLAB_ROOT/requirements_colab_a100.txt"
rm -rf "$COLAB_REPO"
mkdir -p "$COLAB_REPO"
rsync -aH --delete "$DRIVE_COLAB_ROOT/repo_code/" "$COLAB_REPO/"
test -d "$DRIVE_DATA_ROOT" || { echo "ERROR: missing DRIVE_DATA_ROOT=$DRIVE_DATA_ROOT"; exit 3; }
test -d "$DRIVE_DATA_FINAL" || { echo "ERROR: missing DRIVE_DATA_FINAL=$DRIVE_DATA_FINAL"; exit 3; }
if [[ "$USE_LOCAL_SSD" == "1" ]]; then
  echo "Copying dataset from Drive to Colab local SSD for faster A100 training (temporary runtime copy)."
  mkdir -p "$(dirname "$LOCAL_DATA_ROOT")"
  rsync -aH --info=progress2 "$DRIVE_DATA_ROOT/" "$LOCAL_DATA_ROOT/"
  DATA_ROOT="$LOCAL_DATA_ROOT"
else
  echo "Using dataset directly from Google Drive mount. This may be slower."
  DATA_ROOT="$DRIVE_DATA_ROOT"
fi
if [[ -d "$LOCAL_DATA_FINAL" ]]; then DATA_FINAL="$LOCAL_DATA_FINAL"; else DATA_FINAL="$DRIVE_DATA_FINAL"; fi
cat > "$COLAB_WORK_ROOT/colab_env.sh" <<ENV
export DRIVE_PROJECT_ROOT="$DRIVE_PROJECT_ROOT"
export DRIVE_COLAB_ROOT="$DRIVE_COLAB_ROOT"
export DRIVE_DATA_ROOT="$DRIVE_DATA_ROOT"
export DRIVE_DATA_FINAL="$DRIVE_DATA_FINAL"
export DRIVE_RESULTS_ROOT="$DRIVE_RESULTS_ROOT"
export COLAB_WORK_ROOT="$COLAB_WORK_ROOT"
export REPO="$COLAB_REPO"
export DATA_ROOT="$DATA_ROOT"
export DATA_FINAL="$DATA_FINAL"
ENV
cat "$COLAB_WORK_ROOT/colab_env.sh"
cd "$COLAB_REPO"
python3 "$DRIVE_COLAB_ROOT/scripts/colab_verify_dataset.py" --data-root "$DATA_ROOT" --data-final "$DATA_FINAL" --quick 200
echo "Bootstrap complete. Source env with: source $COLAB_WORK_ROOT/colab_env.sh"
