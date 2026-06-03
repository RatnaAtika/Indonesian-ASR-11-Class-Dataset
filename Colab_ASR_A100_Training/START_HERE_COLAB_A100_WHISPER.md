# Colab A100 Whisper Start Guide - Paper ASR m02b

Tanggal: 2026-06-03  
Target: training `m02b_whisper_small_ft` di Google Colab A100 40GB  
Repo lokal Windows/WSL: `/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA`  
Google Drive target: `MyDrive/ASR_Colab_A100/`

Dokumen ini adalah instruksi lengkap untuk memulai, menjalankan, mengkritisi, memperbaiki, dan mengambil hasil training Whisper dari Colab A100. Gunakan bersama:

- `transfer_prompt_Linux_to_Win.md`
- `RUN_GUIDE.md`
- `Colab_ASR_A100_Training/COLAB_A100_README.md`
- `Colab_ASR_A100_Training/notebooks/ASR_Whisper_A100_Colab.ipynb`

---

## 1. Status sebelum mulai Whisper Colab

### 1.1 m06/m07 Linux sudah selesai

Hasil Linux yang sudah ada di Windows:

```text
m06 Conformer:
training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux
Total waktu training: 6 jam, 31 menit, 49 detik

m07 BiLSTM:
training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux
Total waktu training: 7 jam, 6 menit, 23 detik
```

### 1.2 Kritik dan fix metric m06/m07

Audit menemukan bug metric helper:

- `training/common/test_helper.py` memakai `jiwer.compute_measures()`.
- Pada jiwer versi baru, API ini tidak ada.
- Exception disilent, sehingga WER/MER/WIL fallback menjadi `1.0`.
- Ini menyebabkan anomali: sample prediction benar dan CER rendah, tetapi WER global 1.0.

Fix yang dilakukan:

- Ganti ke `jiwer.process_words()` dengan fallback ke `jiwer.wer/mer/wil`.
- Patch juga snapshot Colab di `Colab_ASR_A100_Training/repo_code/...`.
- Recompute m06/m07 dari `predictions.csv` full test.

Metric valid setelah fix:

| Model | WER | CER | MER | WIL | SER |
|---|---:|---:|---:|---:|---:|
| m06 Conformer | 0.0119416 | 0.0043221 | 0.0119342 | 0.0205442 | 0.0598335 |
| m07 BiLSTM | 0.0401218 | 0.0132166 | 0.0400264 | 0.0721196 | 0.1515999 |

Kritik: hasil ini jauh lebih masuk akal daripada WER=1.0. Sebelum paper final, aggregator harus memakai JSON yang sudah fix, bukan JSON lama.

---

## 2. Keputusan profile training Whisper

Ada tiga script Colab:

```text
Colab_ASR_A100_Training/scripts/colab_train_m02b_whisper_small_paper_exact.sh
Colab_ASR_A100_Training/scripts/colab_train_m02b_whisper_small_a100_fast.sh
Colab_ASR_A100_Training/scripts/colab_train_m02b_whisper_medium_a100.sh
```

### Rekomendasi utama untuk paper

Gunakan:

```text
colab_train_m02b_whisper_small_paper_exact.sh
```

Alasan:

- Ini paling sesuai `RUN_GUIDE.md` dan fairness paper.
- Hyperparameter sama dengan paper command:
  - `epochs=5`
  - `batch-size=8`
  - `grad-accum=4`
  - effective batch = 32
  - `lr=1e-5`
  - `warmup-steps=500`
  - `gradient-checkpointing=on`
  - `seed=42`
- Reviewer lebih mudah menerima karena tidak ada perubahan microbatch.

### Kapan pakai A100-fast

Gunakan:

```text
colab_train_m02b_whisper_small_a100_fast.sh
```

hanya jika user eksplisit memilih speed. Profil default:

- `batch-size=32`
- `grad-accum=1`
- effective batch tetap 32
- gradient checkpointing off untuk speed

Kritik: effective batch sama, tetapi microbatch dan checkpointing berubah. Ini kemungkinan valid secara praktis, tetapi untuk paper utama lebih defensible memakai paper-exact.

### Whisper-medium

`colab_train_m02b_whisper_medium_a100.sh` hanya secondary/appendix. Jangan mengganti slot paper #9 dengan medium tanpa mengubah protokol paper dan aggregator.

---

## 3. Fix tambahan di script Colab

Kritik terhadap script lama: hasil baru disalin ke Drive **setelah training selesai**. Jika Colab disconnect sebelum selesai, checkpoint lokal `/content` bisa hilang.

Fix yang sudah dilakukan pada tiga script training:

- Periodic sync run-dir ke Drive setiap `A100_SYNC_INTERVAL_SEC` detik (default 600 detik / 10 menit).
- Final sync otomatis saat script exit.
- Log juga disync ke `Results/ubuntu_logs/`.

Artinya saat training, Drive akan berisi partial checkpoint/run-dir yang bisa dipakai untuk resume manual jika runtime putus.

---

## 4. Verifikasi lokal Windows/WSL sebelum membuka Colab

Dari WSL:

```bash
cd "/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"

ls transfer_prompt_Linux_to_Win.md RUN_GUIDE.md COLAB_A100_WHISPER_START_GUIDE.md
ls Colab_ASR_A100_Training/COLAB_A100_README.md
ls Colab_ASR_A100_Training/notebooks/ASR_Whisper_A100_Colab.ipynb
ls Colab_ASR_A100_Training/scripts/colab_bootstrap_a100.sh
ls Colab_ASR_A100_Training/scripts/colab_train_m02b_whisper_small_paper_exact.sh
```

Cek code package tidak membawa WAV/checkpoint:

```bash
find Colab_ASR_A100_Training -type f \( -name '*.wav' -o -name '*.pt' -o -name '*.pth' -o -name '*.pkl' -o -name '*.safetensors' \) | head
```

Expected: kosong atau tidak ada file berat.

Cek dataset lokal Windows jika perlu upload/verifikasi:

```bash
wc -l training/data_final/train.tsv training/data_final/dev.tsv training/data_final/test.tsv
# expected dengan header:
# 71793 train.tsv
# 15377 dev.tsv
# 15377 test.tsv
```

---

## 5. Struktur Google Drive yang harus ada

Target recommended:

```text
MyDrive/ASR_Colab_A100/
  Colab_ASR_A100_Training/
  Data/
    Processed_Balanced19_v7_natural_synth/
      Dataset_Balanced19/
    training/
      data_final/
  Results/
```

Dataset Drive harus berisi:

```text
Data/Processed_Balanced19_v7_natural_synth/Dataset_Balanced19
Data/training/data_final
```

Referensi ukuran:

```text
Dataset WAV folder: sekitar 15.46 GB / 104,500 files
Split TSV folder: sekitar 79.9 MiB
Colab code package: sekitar 279 MB
```

Kritik: upload dataset via browser bisa lambat karena banyak file kecil. Jika dataset sudah ada di Drive, jangan upload ulang. Verifikasi saja.

---

## 6. Upload/sinkron paket Colab jika belum ada di Drive

Sebelum upload, regenerasi snapshot `repo_code/` agar Colab memakai fix terbaru (termasuk fix jiwer metric helper dan periodic sync scripts):

```bash
cd "/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
bash Colab_ASR_A100_Training/scripts/prepare_repo_code_snapshot.sh
```

Catatan git: `Colab_ASR_A100_Training/repo_code/` adalah snapshot lokal untuk upload Drive dan sengaja di-ignore dari git. Source canonical tetap repo root.

### Opsi A - lewat browser Google Drive

Upload folder lokal:

```text
Colab_ASR_A100_Training/
```

ke:

```text
MyDrive/ASR_Colab_A100/Colab_ASR_A100_Training/
```

### Opsi B - rclone dari WSL

Jika rclone sudah konfigurasi remote `gdrive:`:

```bash
cd "/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
export GDRIVE_REMOTE="gdrive:"
export DRIVE_ROOT="ASR_Colab_A100"
bash Colab_ASR_A100_Training/scripts/upload_colab_code_to_gdrive_rclone.sh
```

Upload dataset jika belum ada:

```bash
export SRC_REPO="/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
bash Colab_ASR_A100_Training/scripts/upload_dataset_to_gdrive_rclone.sh --dry-run
bash Colab_ASR_A100_Training/scripts/upload_dataset_to_gdrive_rclone.sh
```

Kritik: jangan upload dataset kalau sudah ada; ini membuang waktu dan quota.

---

## 7. Buka Colab dan pilih A100

1. Buka Chrome Windows.
2. Buka Drive link user:

```text
https://drive.google.com/drive/folders/1A8TniSYZ4R4j2K1qJsToioM9xpWZW-gO?usp=sharing
```

3. Buka notebook:

```text
Colab_ASR_A100_Training/notebooks/ASR_Whisper_A100_Colab.ipynb
```

4. Di Colab:
   - Runtime -> Change runtime type.
   - Hardware accelerator: GPU.
   - Pilih A100 40GB jika tersedia.
   - Jika tidak dapat A100, disconnect dan coba ulang atau tunggu.

Validasi A100:

```bash
!nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
```

Expected:

```text
NVIDIA A100..., 40960 MiB, ...
```

Jika bukan A100, jangan mulai final paper run.

---

## 8. Cell Colab bootstrap lengkap

Notebook `ASR_Whisper_A100_Colab.ipynb` sekarang sudah auto-detect lokasi folder `Colab_ASR_A100_Training` di Google Drive. Jika error `No such file or directory` tetap muncul, penyebabnya hampir pasti folder package belum terupload lengkap, berada di luar batas pencarian, atau perlu mengisi `MANUAL_COLAB_ROOT` di cell bootstrap dengan path Drive yang tepat.

Jalankan cell ini di Colab:

```python
from google.colab import drive
import os, pathlib

drive.mount('/content/drive')

# Sesuaikan jika Drive folder berbeda.
os.environ['DRIVE_PROJECT_ROOT'] = '/content/drive/MyDrive/ASR_Colab_A100'
os.environ['USE_LOCAL_SSD'] = '1'                 # recommended: copy dataset Drive -> /content local SSD
os.environ['A100_SYNC_INTERVAL_SEC'] = '600'      # sync checkpoint ke Drive tiap 10 menit

print('DRIVE_PROJECT_ROOT =', os.environ['DRIVE_PROJECT_ROOT'])
```

Lalu bootstrap:

```bash
!bash /content/drive/MyDrive/ASR_Colab_A100/Colab_ASR_A100_Training/scripts/colab_bootstrap_a100.sh
```

Bootstrap akan:

1. Install requirements.
2. Copy `repo_code/` ke `/content/asr_work/Paper_Datatset_SOTA`.
3. Verifikasi dataset Drive.
4. Copy dataset ke local SSD `/content/asr_data/...` jika `USE_LOCAL_SSD=1`.
5. Membuat `/content/asr_work/colab_env.sh`.
6. Menjalankan quick dataset verification.

Kritik: jangan training langsung dari Drive kecuali terpaksa. Banyak WAV kecil -> Drive mount lambat. `USE_LOCAL_SSD=1` adalah best practice.

---

## 9. Verifikasi setelah bootstrap

Di Colab:

```bash
!source /content/asr_work/colab_env.sh && echo $REPO && echo $DATA_ROOT && echo $DATA_FINAL
!source /content/asr_work/colab_env.sh && cd "$REPO" && wc -l "$DATA_FINAL/train.tsv" "$DATA_FINAL/dev.tsv" "$DATA_FINAL/test.tsv"
!du -sh /content/asr_data || true
!source /content/asr_work/colab_env.sh && cd "$REPO" && python3 Colab_ASR_A100_Training/scripts/colab_verify_dataset.py --data-root "$DATA_ROOT" --data-final "$DATA_FINAL" --quick 1000
```

Jika path script verify tidak ada di `$REPO`, gunakan script dari Drive:

```bash
!source /content/asr_work/colab_env.sh && python3 "$DRIVE_COLAB_ROOT/scripts/colab_verify_dataset.py" --data-root "$DATA_ROOT" --data-final "$DATA_FINAL" --quick 1000
```

Expected line counts:

```text
71793 train.tsv
15377 dev.tsv
15377 test.tsv
```

Jika missing audio >0, stop. Jangan training.

---

## 10. Run final paper: Whisper-small paper-exact

Jalankan ini untuk paper utama:

```bash
!bash /content/drive/MyDrive/ASR_Colab_A100/Colab_ASR_A100_Training/scripts/colab_train_m02b_whisper_small_paper_exact.sh
```

Output run:

```text
/content/asr_work/Paper_Datatset_SOTA/training/m02b_whisper_small_ft/runs/run_paper_<timestamp>_colab_a100_paper_exact/
```

Drive result:

```text
MyDrive/ASR_Colab_A100/Results/m02b_whisper_small_ft/run_paper_<timestamp>_colab_a100_paper_exact/
```

Script otomatis menjalankan:

1. training 5 epoch,
2. test.py,
3. periodic sync ke Drive,
4. final sync ke Drive.

---

## 11. Monitoring saat training

Cek GPU:

```bash
!nvidia-smi
```

Cek log training terbaru:

```bash
!source /content/asr_work/colab_env.sh && cd "$REPO" && ls -dt ubuntu_logs/train_m02b_small_* | head
!source /content/asr_work/colab_env.sh && cd "$REPO" && tail -n 80 $(ls -t ubuntu_logs/train_m02b_small_* | head -1)
```

Cek periodic sync Drive:

```bash
!find /content/drive/MyDrive/ASR_Colab_A100/Results/m02b_whisper_small_ft -maxdepth 2 -type d | tail -20
```

Kritik:

- Jika GPU util rendah, kemungkinan bottleneck data copy/Drive/dataloader.
- Jika training dari Drive langsung, ulang bootstrap dengan `USE_LOCAL_SSD=1`.
- Jika Colab idle timeout, periodic sync minimal menyelamatkan checkpoint terakhir yang sudah tersync.

---

## 12. Jika runtime Colab putus: resume dari Drive checkpoint

Jika training belum selesai tetapi Drive sudah punya partial run:

1. Reconnect Colab A100.
2. Mount Drive dan bootstrap ulang.
3. Tentukan run name partial di Drive:

```bash
!find /content/drive/MyDrive/ASR_Colab_A100/Results/m02b_whisper_small_ft -maxdepth 1 -type d | sort | tail -10
```

4. Copy partial run ke local repo:

```bash
!source /content/asr_work/colab_env.sh && \
  RUN_NAME="run_paper_YYYYMMDD_HHMMSS_colab_a100_paper_exact" && \
  SRC="$DRIVE_RESULTS_ROOT/m02b_whisper_small_ft/$RUN_NAME" && \
  DST="$REPO/training/m02b_whisper_small_ft/runs/$RUN_NAME" && \
  mkdir -p "$DST" && rsync -aH --info=progress2 "$SRC/" "$DST/"
```

5. Resume training:

```bash
!source /content/asr_work/colab_env.sh && \
  RUN_NAME="run_paper_YYYYMMDD_HHMMSS_colab_a100_paper_exact" && \
  cd "$REPO" && \
  python3 training/m02b_whisper_small_ft/train.py \
    --run-dir "training/m02b_whisper_small_ft/runs/$RUN_NAME" --resume \
    --data-root "$DATA_ROOT" --data-final "$DATA_FINAL" \
    --epochs 5 --batch-size 8 --grad-accum 4 \
    --lr 1e-5 --warmup-steps 500 \
    --gradient-checkpointing --seed 42
```

6. Setelah selesai, jalankan test dan sync manual:

```bash
!source /content/asr_work/colab_env.sh && \
  RUN_NAME="run_paper_YYYYMMDD_HHMMSS_colab_a100_paper_exact" && \
  cd "$REPO" && \
  python3 training/m02b_whisper_small_ft/test.py \
    --run-dir "training/m02b_whisper_small_ft/runs/$RUN_NAME" \
    --data-root "$DATA_ROOT" --data-final "$DATA_FINAL" && \
  rsync -aH --info=progress2 "training/m02b_whisper_small_ft/runs/$RUN_NAME/" \
    "$DRIVE_RESULTS_ROOT/m02b_whisper_small_ft/$RUN_NAME/"
```

---

## 13. Optional: A100-fast run

Jika user memilih speed:

```bash
!bash /content/drive/MyDrive/ASR_Colab_A100/Colab_ASR_A100_Training/scripts/colab_train_m02b_whisper_small_a100_fast.sh
```

Opsional override:

```python
import os
os.environ['A100_BATCH_SIZE'] = '24'
os.environ['A100_GRAD_ACCUM'] = '1'
os.environ['A100_SYNC_INTERVAL_SEC'] = '600'
```

Kritik:

- Jika batch 32 OOM karena Colab memory fragmentation, coba 24 atau 16 dengan grad accumulation agar effective batch mendekati/menjadi 32.
- Untuk paper utama tetap lebih baik paper-exact.

---

## 14. Optional: Whisper-medium A100 secondary

Jalankan hanya setelah Whisper-small paper selesai:

```bash
!bash /content/drive/MyDrive/ASR_Colab_A100/Colab_ASR_A100_Training/scripts/colab_train_m02b_whisper_medium_a100.sh
```

Default:

```text
batch-size=8
grad-accum=4
effective batch=32
```

Jika OOM:

```python
import os
os.environ['A100_MEDIUM_BATCH_SIZE'] = '4'
os.environ['A100_MEDIUM_GRAD_ACCUM'] = '8'
```

Kritik:

- Medium bukan paper slot utama.
- Jangan campur medium ke aggregator 9-model kecuali protokol paper diubah.
- Medium memerlukan Drive storage lebih besar (`best_model/` + checkpoints bisa ~9-12GB per run).

---

## 15. Verifikasi hasil di Colab setelah selesai

Ganti `RUN_DIR` sesuai run terbaru:

```bash
!source /content/asr_work/colab_env.sh && cd "$REPO" && \
  RUN_DIR=$(ls -dt training/m02b_whisper_small_ft/runs/run_paper_*_colab_a100* | head -1) && \
  echo "$RUN_DIR" && \
  ls "$RUN_DIR" && \
  grep -i "Total waktu training" "$RUN_DIR/log.txt" && \
  ls "$RUN_DIR/best_model" && \
  ls "$RUN_DIR/test_results/test_paper.json" && \
  python3 -m json.tool "$RUN_DIR/test_results/test_paper.json" | grep -E '"wer"|"cer"|"model_id"|"family"' | head -20
```

Artifact wajib:

```text
config.json
meta.json
history.json
log.txt
report.md
model_summary.png
model_summary.pdf
best_model/
checkpoints/
test_results/test_paper.json
test_results/predictions.csv
test_results/test_summary.md
```

Jika salah satu artifact wajib hilang, jangan hapus runtime. Jalankan manual sync/test ulang.

---

## 16. Copy hasil Colab ke Windows/WSL

Jika Google Drive Desktop tersedia di Windows, copy folder result ke:

```text
C:\Users\wayandadang\AI\Dataset ASR\Paper_Datatset_SOTA\training\m02b_whisper_small_ft\runs\
```

Dari WSL dengan rclone:

```bash
cd "/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
mkdir -p training/m02b_whisper_small_ft/runs
rclone copy "gdrive:ASR_Colab_A100/Results/m02b_whisper_small_ft" \
  "training/m02b_whisper_small_ft/runs" \
  --progress --transfers 4 --checkers 8
```

Verifikasi:

```bash
find training/m02b_whisper_small_ft/runs -path '*/test_results/test_paper.json' | sort
python3 - <<'PY'
import json, pathlib
for p in sorted(pathlib.Path('training/m02b_whisper_small_ft/runs').glob('run_paper_*colab*/test_results/test_paper.json')):
    d=json.loads(p.read_text())
    print(p)
    print(d.get('model_id'), d.get('family'), d.get('metrics'))
PY
```

---

## 17. Setelah Whisper ada di Windows: aggregator

Jalankan dari WSL:

```bash
cd "/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
python3 aggregate_paper_test_results.py
python3 -m json.tool reports/paper_benchmark/benchmark.json | grep -E 'n_paper_models_present|missing_paper_models'
```

Expected final:

```text
n_paper_models_present = 9
missing_paper_models = []
```

Jika belum 9, jangan paksa paper table. Laporkan model yang missing.

---

## 18. Review loop wajib sampai fix

### Loop 1 - Before training

- [ ] Colab benar-benar A100 40GB.
- [ ] Drive path benar.
- [ ] Dataset counts benar.
- [ ] Missing audio = 0.
- [ ] `USE_LOCAL_SSD=1` aktif.
- [ ] Script yang dipilih adalah `paper_exact` untuk paper utama.

### Loop 2 - During training

- [ ] Log menunjukkan epoch berjalan.
- [ ] `Total waktu training` akan ditulis di akhir.
- [ ] Periodic sync muncul di log setiap 10 menit.
- [ ] Drive `Results/` mulai terisi partial run.
- [ ] Tidak ada OOM atau runtime fallback ke CPU.

### Loop 3 - After training/test

- [ ] `best_model/` ada.
- [ ] `test_results/test_paper.json` ada.
- [ ] Metric WER/CER tidak fallback 1.0 tanpa alasan.
- [ ] Jika WER=1.0 tetapi CER rendah, ulang audit metric dari predictions.csv seperti m06/m07.
- [ ] `log.txt` berisi `Total waktu training`.
- [ ] `report.md` sesuai.

### Loop 4 - After copy to Windows

- [ ] Path run tidak overwrite run lama.
- [ ] JSON bisa dibaca di WSL.
- [ ] Aggregator melihat m02b.
- [ ] `n_paper_models_present == 9` jika semua model lain lengkap.
- [ ] Checkpoint besar tidak masuk git.

---

## 19. Jangan commit file besar

Boleh commit:

- Panduan Markdown.
- Script Colab kecil.
- Notebook kecil.
- JSON/report agregat kecil.

Jangan commit:

- `training/*/runs/*/checkpoints/`
- `best_model/`
- `*.pt`, `*.pth`, `*.safetensors`, `*.pkl`
- dataset WAV
- Google token/auth/rclone config

Cek sebelum commit:

```bash
git status --short
git status --short --ignored | grep -E 'best_model|checkpoints|safetensors|\.pt|\.pth|\.wav|auth|token' || true
```

---

## 20. Prompt singkat untuk operator Colab

```text
Buka Colab_ASR_A100_Training/notebooks/ASR_Whisper_A100_Colab.ipynb dari Drive. Pilih Runtime GPU A100 40GB. Mount Drive. Set DRIVE_PROJECT_ROOT=/content/drive/MyDrive/ASR_Colab_A100, USE_LOCAL_SSD=1, A100_SYNC_INTERVAL_SEC=600. Jalankan colab_bootstrap_a100.sh dan pastikan dataset train/dev/test count benar serta missing audio=0. Untuk paper utama jalankan colab_train_m02b_whisper_small_paper_exact.sh. Jangan pakai fast profile untuk paper utama kecuali user menyetujui. Tunggu training + test selesai. Pastikan best_model/, log.txt dengan Total waktu training, dan test_results/test_paper.json ada. Hasil tersimpan otomatis di Drive Results/m02b_whisper_small_ft/<run>. Setelah selesai copy result ke Windows runs folder dan jalankan aggregate_paper_test_results.py.
```
