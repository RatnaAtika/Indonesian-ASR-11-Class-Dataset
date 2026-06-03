#!/usr/bin/env bash
set -Eeuo pipefail
# Build single-file tar archives for fast Colab bootstrap.
# Upload resulting archives to Drive: ASR_Colab_A100/Data/_archives/

SRC_REPO="${SRC_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
OUT_DIR="${OUT_DIR:-$SRC_REPO/Colab_ASR_A100_Training/archives}"
DATA_PARENT="$SRC_REPO/Processed_Balanced19_v7_natural_synth"
DATA_DIR="$DATA_PARENT/Dataset_Balanced19"
SPLIT_PARENT="$SRC_REPO/training"
SPLIT_DIR="$SPLIT_PARENT/data_final"

mkdir -p "$OUT_DIR"
test -d "$DATA_DIR" || { echo "ERROR missing DATA_DIR=$DATA_DIR"; exit 3; }
test -d "$SPLIT_DIR" || { echo "ERROR missing SPLIT_DIR=$SPLIT_DIR"; exit 3; }

echo "Building dataset archive (uncompressed tar; fastest extract, one Drive file):"
echo "  source: $DATA_DIR"
echo "  output: $OUT_DIR/dataset_balanced19_v7.tar"
tar -cf "$OUT_DIR/dataset_balanced19_v7.tar" -C "$DATA_PARENT" Dataset_Balanced19

echo "Building split TSV archive:"
echo "  source: $SPLIT_DIR"
echo "  output: $OUT_DIR/data_final.tar"
tar -cf "$OUT_DIR/data_final.tar" -C "$SPLIT_PARENT" data_final

sha256sum "$OUT_DIR/dataset_balanced19_v7.tar" "$OUT_DIR/data_final.tar" > "$OUT_DIR/SHA256SUMS.txt"
ls -lh "$OUT_DIR/dataset_balanced19_v7.tar" "$OUT_DIR/data_final.tar" "$OUT_DIR/SHA256SUMS.txt"
cat <<EOF

Next upload to Drive:
  MyDrive/ASR_Colab_A100/Data/_archives/dataset_balanced19_v7.tar
  MyDrive/ASR_Colab_A100/Data/_archives/data_final.tar

If using rclone:
  rclone copy "$OUT_DIR" gdrive:ASR_Colab_A100/Data/_archives --progress --transfers 2 --checkers 4
EOF
