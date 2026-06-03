#!/usr/bin/env bash
set -Eeuo pipefail
COLAB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$COLAB_ROOT/.." && pwd)"
SNAP="$COLAB_ROOT/repo_code"
mkdir -p "$SNAP"
rsync -aH --delete \
  --exclude='.git/' \
  --exclude='__pycache__/' \
  --exclude='*/__pycache__/' \
  --exclude='*.pyc' \
  --exclude='Colab_ASR_A100_Training/' \
  --exclude='Dataset_Ori/' \
  --exclude='Processed_Balanced19/' \
  --exclude='Processed_Balanced19_v2/' \
  --exclude='Processed_Balanced19_v3/' \
  --exclude='Processed_Balanced19_v4_merged/' \
  --exclude='Processed_Balanced19_v5_uniform/' \
  --exclude='Processed_Balanced19_v6_relabeled/' \
  --exclude='Processed_Balanced19_v7_natural_synth/' \
  --exclude='Whisper_Verification/' \
  --exclude='Whisper_Verification_Sessions/' \
  --exclude='*/runs/' \
  --exclude='*/checkpoints/' \
  --exclude='*/best_model/' \
  --exclude='*.wav' \
  --exclude='*.pt' \
  --exclude='*.pth' \
  --exclude='*.pkl' \
  --exclude='*.safetensors' \
  "$REPO_ROOT/" "$SNAP/"
if find "$SNAP" -type f \( -name '*.wav' -o -name '*.pt' -o -name '*.pth' -o -name '*.pkl' -o -name '*.safetensors' \) | grep -q .; then
  echo "ERROR: heavy files found in repo_code snapshot"; exit 4
fi
echo "Snapshot ready: $SNAP"
du -sh "$SNAP"
