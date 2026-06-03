#!/usr/bin/env bash
set -Eeuo pipefail
DRIVE_PROJECT_ROOT="${DRIVE_PROJECT_ROOT:-/content/drive/MyDrive/ASR_Colab_A100}"
DRIVE_COLAB_ROOT="${DRIVE_COLAB_ROOT:-$DRIVE_PROJECT_ROOT/Colab_ASR_A100_Training}"
DRIVE_DATA_ROOT="${DRIVE_DATA_ROOT:-$DRIVE_PROJECT_ROOT/Data/Processed_Balanced19_v7_natural_synth/Dataset_Balanced19}"
DRIVE_DATA_FINAL="${DRIVE_DATA_FINAL:-$DRIVE_PROJECT_ROOT/Data/training/data_final}"
DRIVE_RESULTS_ROOT="${DRIVE_RESULTS_ROOT:-$DRIVE_PROJECT_ROOT/Results}"
DRIVE_ARCHIVE_ROOT="${DRIVE_ARCHIVE_ROOT:-$DRIVE_PROJECT_ROOT/Data/_archives}"
DRIVE_DATA_ARCHIVE="${DRIVE_DATA_ARCHIVE:-$DRIVE_ARCHIVE_ROOT/dataset_balanced19_v7.tar}"
DRIVE_DATA_FINAL_ARCHIVE="${DRIVE_DATA_FINAL_ARCHIVE:-$DRIVE_ARCHIVE_ROOT/data_final.tar}"
COLAB_WORK_ROOT="${COLAB_WORK_ROOT:-/content/asr_work}"
COLAB_REPO="${COLAB_REPO:-$COLAB_WORK_ROOT/Paper_Datatset_SOTA}"
USE_LOCAL_SSD="${USE_LOCAL_SSD:-1}"
USE_DATA_ARCHIVE="${USE_DATA_ARCHIVE:-1}"
LOCAL_DATA_ROOT="${LOCAL_DATA_ROOT:-/content/asr_data/Processed_Balanced19_v7_natural_synth/Dataset_Balanced19}"
LOCAL_DATA_FINAL="${LOCAL_DATA_FINAL:-/content/asr_data/training/data_final}"
MIN_LOCAL_FREE_GB="${MIN_LOCAL_FREE_GB:-40}"
# Support flat Drive layout: MyDrive/Colab_ASR_A100/{scripts,Data,...}
if [[ ! -f "$DRIVE_COLAB_ROOT/scripts/colab_bootstrap_a100.sh" && -f "$DRIVE_PROJECT_ROOT/scripts/colab_bootstrap_a100.sh" ]]; then
  DRIVE_COLAB_ROOT="$DRIVE_PROJECT_ROOT"
fi
if [[ ! -d "$DRIVE_PROJECT_ROOT/Data" && -d "$DRIVE_COLAB_ROOT/Data" ]]; then
  DRIVE_PROJECT_ROOT="$DRIVE_COLAB_ROOT"
  DRIVE_DATA_ROOT="${DRIVE_DATA_ROOT:-$DRIVE_PROJECT_ROOT/Data/Processed_Balanced19_v7_natural_synth/Dataset_Balanced19}"
  DRIVE_DATA_FINAL="${DRIVE_DATA_FINAL:-$DRIVE_PROJECT_ROOT/Data/training/data_final}"
  DRIVE_RESULTS_ROOT="${DRIVE_RESULTS_ROOT:-$DRIVE_PROJECT_ROOT/Results}"
  DRIVE_ARCHIVE_ROOT="${DRIVE_ARCHIVE_ROOT:-$DRIVE_PROJECT_ROOT/Data/_archives}"
  DRIVE_DATA_ARCHIVE="${DRIVE_DATA_ARCHIVE:-$DRIVE_ARCHIVE_ROOT/dataset_balanced19_v7.tar}"
  DRIVE_DATA_FINAL_ARCHIVE="${DRIVE_DATA_FINAL_ARCHIVE:-$DRIVE_ARCHIVE_ROOT/data_final.tar}"
fi
nvidia-smi || true
python3 - <<PY
import shutil, sys
free = shutil.disk_usage('/content').free / (1024**3)
print(f'[colab-bootstrap] /content free space: {free:.1f} GiB')
if free < float('$MIN_LOCAL_FREE_GB'):
    raise SystemExit(f'ERROR: /content free space {free:.1f} GiB < MIN_LOCAL_FREE_GB=$MIN_LOCAL_FREE_GB')
PY
mkdir -p "$COLAB_WORK_ROOT" "$DRIVE_RESULTS_ROOT"
python3 -m pip install -q --upgrade pip
python3 -m pip install -q -r "$DRIVE_COLAB_ROOT/requirements_colab_a100.txt"
rm -rf "$COLAB_REPO"
mkdir -p "$COLAB_REPO"
rsync -aH --delete "$DRIVE_COLAB_ROOT/repo_code/" "$COLAB_REPO/"
echo "[colab-bootstrap] DRIVE_DATA_ROOT=$DRIVE_DATA_ROOT"
echo "[colab-bootstrap] DRIVE_DATA_FINAL=$DRIVE_DATA_FINAL"
echo "[colab-bootstrap] DRIVE_DATA_ARCHIVE=$DRIVE_DATA_ARCHIVE"
echo "[colab-bootstrap] DRIVE_DATA_FINAL_ARCHIVE=$DRIVE_DATA_FINAL_ARCHIVE"
if [[ "$USE_LOCAL_SSD" == "1" && "$USE_DATA_ARCHIVE" == "1" && -f "$DRIVE_DATA_ARCHIVE" ]]; then
  echo "[colab-bootstrap] dataset source OK: archive exists. Raw Drive dataset folder is not required."
elif [[ -d "$DRIVE_DATA_ROOT" ]]; then
  echo "[colab-bootstrap] dataset source OK: raw Drive dataset folder exists."
else
  echo "ERROR: missing dataset source. Need either archive or raw folder:"
  echo "  archive: $DRIVE_DATA_ARCHIVE"
  echo "  raw dir:  $DRIVE_DATA_ROOT"
  exit 3
fi
if [[ "$USE_LOCAL_SSD" == "1" && "$USE_DATA_ARCHIVE" == "1" && -f "$DRIVE_DATA_FINAL_ARCHIVE" ]]; then
  echo "[colab-bootstrap] split source OK: archive exists. Raw Drive data_final folder is not required."
elif [[ -d "$DRIVE_DATA_FINAL" ]]; then
  echo "[colab-bootstrap] split source OK: raw Drive data_final folder exists."
else
  echo "ERROR: missing split source. Need either archive or raw folder:"
  echo "  archive: $DRIVE_DATA_FINAL_ARCHIVE"
  echo "  raw dir:  $DRIVE_DATA_FINAL"
  exit 3
fi
if [[ "$USE_LOCAL_SSD" == "1" ]]; then
  echo "Using Colab local SSD (/content) for A100 training/testing."
  echo "This is a temporary runtime copy, not a permanent Drive duplicate."
  mkdir -p "$(dirname "$LOCAL_DATA_ROOT")" "$(dirname "$LOCAL_DATA_FINAL")" /content/asr_archives

  if [[ -f "$LOCAL_DATA_ROOT/.colab_copy_complete" && -f "$LOCAL_DATA_FINAL/train.tsv" ]]; then
    echo "Local SSD dataset already present in this runtime; skipping copy."
  elif [[ "$USE_DATA_ARCHIVE" == "1" && -f "$DRIVE_DATA_ARCHIVE" ]]; then
    echo "FAST PATH: found dataset archive: $DRIVE_DATA_ARCHIVE"
    echo "Copying one large archive to /content, then extracting locally (much faster than 104k small Drive reads)."
    rsync -aH --info=progress2 "$DRIVE_DATA_ARCHIVE" /content/asr_archives/dataset_balanced19_v7.tar
    rm -rf "$LOCAL_DATA_ROOT"
    mkdir -p "$(dirname "$LOCAL_DATA_ROOT")"
    tar -xf /content/asr_archives/dataset_balanced19_v7.tar -C "$(dirname "$LOCAL_DATA_ROOT")"
    touch "$LOCAL_DATA_ROOT/.colab_copy_complete"
  else
    echo "SLOW FALLBACK: dataset archive not found; copying many WAV files from Drive."
    echo "For faster bootstrap, create/upload: $DRIVE_DATA_ARCHIVE"
    mkdir -p "$(dirname "$LOCAL_DATA_ROOT")"
    rsync -aH --info=progress2 "$DRIVE_DATA_ROOT/" "$LOCAL_DATA_ROOT/"
    touch "$LOCAL_DATA_ROOT/.colab_copy_complete"
  fi

  if [[ -f "$LOCAL_DATA_FINAL/.colab_copy_complete" && -f "$LOCAL_DATA_FINAL/train.tsv" ]]; then
    echo "Local SSD split TSVs already present; skipping TSV copy."
  elif [[ "$USE_DATA_ARCHIVE" == "1" && -f "$DRIVE_DATA_FINAL_ARCHIVE" ]]; then
    echo "FAST PATH: found split archive: $DRIVE_DATA_FINAL_ARCHIVE"
    rsync -aH --info=progress2 "$DRIVE_DATA_FINAL_ARCHIVE" /content/asr_archives/data_final.tar
    rm -rf "$LOCAL_DATA_FINAL"
    mkdir -p "$(dirname "$LOCAL_DATA_FINAL")"
    tar -xf /content/asr_archives/data_final.tar -C "$(dirname "$LOCAL_DATA_FINAL")"
    touch "$LOCAL_DATA_FINAL/.colab_copy_complete"
  else
    echo "Copying split TSVs to local SSD as well (avoid Drive I/O during training/test)."
    mkdir -p "$LOCAL_DATA_FINAL"
    rsync -aH --delete --info=progress2 "$DRIVE_DATA_FINAL/" "$LOCAL_DATA_FINAL/"
    touch "$LOCAL_DATA_FINAL/.colab_copy_complete"
  fi

  DATA_ROOT="$LOCAL_DATA_ROOT"
  DATA_FINAL="$LOCAL_DATA_FINAL"
else
  echo "WARNING: Using dataset directly from Google Drive mount. This can make runtime extremely slow."
  echo "Recommended: set USE_LOCAL_SSD=1 unless /content free space is insufficient."
  DATA_ROOT="$DRIVE_DATA_ROOT"
  DATA_FINAL="$DRIVE_DATA_FINAL"
fi

echo "[colab-bootstrap] DATA_ROOT=$DATA_ROOT"
echo "[colab-bootstrap] DATA_FINAL=$DATA_FINAL"
du -sh "$DATA_ROOT" "$DATA_FINAL" || true
cat > "$COLAB_WORK_ROOT/colab_env.sh" <<ENV
export DRIVE_PROJECT_ROOT="$DRIVE_PROJECT_ROOT"
export DRIVE_COLAB_ROOT="$DRIVE_COLAB_ROOT"
export DRIVE_DATA_ROOT="$DRIVE_DATA_ROOT"
export DRIVE_DATA_FINAL="$DRIVE_DATA_FINAL"
export DRIVE_RESULTS_ROOT="$DRIVE_RESULTS_ROOT"
export DRIVE_ARCHIVE_ROOT="$DRIVE_ARCHIVE_ROOT"
export DRIVE_DATA_ARCHIVE="$DRIVE_DATA_ARCHIVE"
export DRIVE_DATA_FINAL_ARCHIVE="$DRIVE_DATA_FINAL_ARCHIVE"
export COLAB_WORK_ROOT="$COLAB_WORK_ROOT"
export REPO="$COLAB_REPO"
export DATA_ROOT="$DATA_ROOT"
export DATA_FINAL="$DATA_FINAL"
export MIN_LOCAL_FREE_GB="${MIN_LOCAL_FREE_GB:-40}"
export USE_DATA_ARCHIVE="${USE_DATA_ARCHIVE:-1}"
export A100_SYNC_INTERVAL_SEC="${A100_SYNC_INTERVAL_SEC:-600}"
export A100_AUTO_DISCONNECT="${A100_AUTO_DISCONNECT:-0}"
ENV
cat "$COLAB_WORK_ROOT/colab_env.sh"
cd "$COLAB_REPO"
python3 "$DRIVE_COLAB_ROOT/scripts/colab_verify_dataset.py" --data-root "$DATA_ROOT" --data-final "$DATA_FINAL" --quick 200
echo "Bootstrap complete. Source env with: source $COLAB_WORK_ROOT/colab_env.sh"
