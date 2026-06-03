# Transfer Prompt — Linux to Windows / WSL2 / Google Colab A100

Gunakan prompt ini untuk agent di sisi Windows/WSL2 setelah pekerjaan persiapan di Ubuntu/Linux selesai. Tujuannya adalah melanjutkan workflow ASR dari Windows, menjaga sinkronisasi hasil Linux, dan menjalankan Colab A100 untuk training Whisper yang terlalu lama di laptop lokal.

## 0. Peran agent Windows

Kamu adalah agent yang berjalan dari sisi Windows/WSL2 untuk repository ASR ini. Tugas utama:

1. Verifikasi hasil sinkronisasi dari Linux sudah ada di repository Windows.
2. Jangan menggandakan dataset besar jika data sudah ada.
3. Gunakan file panduan yang sudah disinkronkan dari Linux.
4. Siapkan/lanjutkan training lokal Windows/WSL2 jika diperlukan.
5. Buka dan jalankan workflow Google Colab A100 dari Chrome/Drive untuk Whisper.
6. Setelah Colab selesai, sinkronkan hasil Colab kembali ke repository Windows dan, jika perlu, ke Linux.

Jangan meminta atau menyimpan password/token Google/ExpressVPN/API di chat. Jika perlu login, minta user melakukan login manual di browser/CLI.

---

## 1. Path penting

### Windows repository utama

Di Windows Explorer:

```text
C:\Users\wayandadang\AI\Dataset ASR\Paper_Datatset_SOTA
```

Dari WSL2/Linux mount:

```bash
cd "/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
```

Jika path mount di Ubuntu native:

```bash
cd "/media/wayan/Windows-SSD/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
```

### Linux native repository hasil training

```bash
/home/wayan/AI/Dataset_ASR_Train_Linux
```

### Google Drive folder yang sudah diberikan user

```text
https://drive.google.com/drive/folders/1A8TniSYZ4R4j2K1qJsToioM9xpWZW-gO?usp=sharing
```

Gunakan link ini untuk membuka folder Drive dari Chrome di Windows dan menjalankan notebook Colab.

---

## 2. Ringkasan pekerjaan yang sudah selesai di Linux

### 2.1 Repo dan dataset dipindahkan ke ext4 Linux

Folder Linux:

```text
/home/wayan/AI/Dataset_ASR_Train_Linux
```

Dataset v7 valid:

```text
train rows = 71,792
 dev rows = 15,376
test rows = 15,376
total rows = 102,544
WAV files = 104,500
audio hours = 130.6548
missing audio = 0
```

Dataset berada di:

```text
Processed_Balanced19_v7_natural_synth/Dataset_Balanced19
training/data_final/
```

### 2.2 Skills dan workflow

Project skills tersedia termasuk:

```text
.agents/skills/bmad-suite
.agents/skills/superpowers-suite
.agents/skills/github-delivery
.agents/skills/portable-project-adapter
.agents/skills/research-paper-writing
.agents/skills/agent-harness-compatibility
```

Gunakan BMAD dan Superpowers sebagai workflow discipline, tetapi jangan menambah overhead berlebihan untuk tugas kecil.

### 2.3 RUN_GUIDE.md sudah sinkron Linux dan Windows

File ini sudah disinkronkan di Linux dan Windows:

```text
RUN_GUIDE.md
```

Isi penting yang ditambahkan:

- Command utama tetap valid untuk Windows/WSL2.
- Ada blok tambahan **Run via Ubuntu/Linux native/ext4**.
- Run hasil Linux/Colab diberi label khusus seperti `_linux` dan `_colab_a100`.

### 2.4 Hasil training Linux m06 dan m07 sudah selesai dan dicopy ke Windows

#### m06 Conformer — hasil Linux di Windows

```text
training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux
```

Ukuran saat copy:

```text
4.7G
100 files
```

Metrics test final setelah audit/fix metric helper jiwer:

```text
model_id = m06-conformer-ctc
WER = 0.011941638277990744
CER = 0.004322092427426721
MER = 0.011934174534545134
WIL = 0.020544206605723203
SER = 0.059833506763787736
```

Catatan: nilai lama `WER=1.0` adalah fallback artifact akibat `jiwer.compute_measures()` tidak tersedia di jiwer versi baru, bukan perilaku model.

#### m07 Bi-LSTM — hasil Linux di Windows

```text
training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux
```

Ukuran saat copy:

```text
14G
97 files
```

Metrics test final setelah audit/fix metric helper jiwer:

```text
model_id = m07-bilstm-ctc
WER = 0.04012184444231887
CER = 0.013216648861286718
MER = 0.04002642492751496
WIL = 0.0721196371666768
SER = 0.1515998959417274
```

Catatan audit: anomali lama `WER=1.0` sudah dikritisi dan diperbaiki. Penyebabnya sama: fallback metric helper akibat perubahan API jiwer.

### 2.5 Manifest transfer Linux ke Windows

Folder manifest transfer di Windows:

```text
Linux_Train_Results_Transfer_20260602_222537
```

Setiap run Linux yang dicopy memiliki:

```text
LINUX_SOURCE_MANIFEST.txt
```

---

## 3. Persiapan Colab A100 sudah dibuat dan sinkron Linux/Windows

Folder Colab di Windows:

```text
Colab_ASR_A100_Training
```

Folder yang sama di Linux:

```text
/home/wayan/AI/Dataset_ASR_Train_Linux/Colab_ASR_A100_Training
```

Verifikasi terakhir:

```text
linux files = 353
windows files = 353
size = 279M
WAV inside Colab folder = 0
checkpoint/model weight inside Colab folder = 0
repo_code run dirs = 0
```

Artinya folder Colab aman untuk upload karena tidak membawa dataset/checkpoint besar.

### File penting Colab

```text
COLAB_A100_WHISPER_START_GUIDE.md
Colab_ASR_A100_Training/START_HERE_COLAB_A100_WHISPER.md
Colab_ASR_A100_Training/COLAB_A100_README.md
Colab_ASR_A100_Training/DATASET_UPLOAD_MANIFEST.md
Colab_ASR_A100_Training/requirements_colab_a100.txt
Colab_ASR_A100_Training/notebooks/ASR_Whisper_A100_Colab.ipynb
Colab_ASR_A100_Training/scripts/colab_bootstrap_a100.sh
Colab_ASR_A100_Training/scripts/colab_train_m02b_whisper_small_a100_fast.sh
Colab_ASR_A100_Training/scripts/colab_train_m02b_whisper_small_paper_exact.sh
Colab_ASR_A100_Training/scripts/colab_train_m02b_whisper_medium_a100.sh
Colab_ASR_A100_Training/repo_code/
```

---

## 4. Google Drive / Colab target

User memberikan link Drive:

```text
https://drive.google.com/drive/folders/1A8TniSYZ4R4j2K1qJsToioM9xpWZW-gO?usp=sharing
```

Struktur Drive yang diharapkan:

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

Jika file sudah diupload ke Drive, jangan upload ulang dataset. Verifikasi saja bahwa folder dataset dan TSV ada.

Dataset yang perlu ada di Drive:

```text
Data/Processed_Balanced19_v7_natural_synth/Dataset_Balanced19
Data/training/data_final
```

Ukuran referensi:

```text
Dataset WAV folder = 15.46 GB / 104,500 files
Split TSV folder = 79.9 MiB
Colab code package = 279M
```

Karena dataset berisi banyak file kecil, upload via browser bisa lebih lama daripada estimasi bandwidth murni.

---

## 5. Instruksi untuk agent Windows: verifikasi lokal dulu

Dari WSL2:

```bash
cd "/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
```

Cek file/folder penting:

```bash
ls RUN_GUIDE.md transfer_prompt_Linux_to_Win.md
ls Colab_ASR_A100_Training
ls training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/test_results/test_paper.json
ls training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/test_results/test_paper.json
```

Cek ukuran:

```bash
du -sh Colab_ASR_A100_Training \
  training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux \
  training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux
```

Cek dataset lokal Windows tidak perlu diduplikasi:

```bash
ls "Processed_Balanced19_v7_natural_synth/Dataset_Balanced19" | head
wc -l training/data_final/train.tsv training/data_final/dev.tsv training/data_final/test.tsv
```

Expected TSV line counts termasuk header:

```text
71793 train.tsv
15377 dev.tsv
15377 test.tsv
```

---

## 6. Instruksi membuka Google Drive dan Colab dari Windows Chrome

Di Windows Chrome, buka:

```text
https://drive.google.com/drive/folders/1A8TniSYZ4R4j2K1qJsToioM9xpWZW-gO?usp=sharing
```

Cari/buka notebook:

```text
Colab_ASR_A100_Training/notebooks/ASR_Whisper_A100_Colab.ipynb
```

Di Colab:

1. Runtime → Change runtime type.
2. Pilih GPU A100 40 GB jika tersedia.
3. Jalankan cell mount Google Drive.
4. Jalankan cell `nvidia-smi` untuk memastikan A100.
5. Jalankan bootstrap.
6. Jalankan training Whisper-small A100.

Jika Drive folder bukan berada di `MyDrive/ASR_Colab_A100`, sesuaikan env di notebook:

```python
os.environ['DRIVE_PROJECT_ROOT'] = '/content/drive/MyDrive/ASR_Colab_A100'
```

ubah ke lokasi sebenarnya.

---

## 7. Run Colab yang disarankan

### 7.1 Whisper-small A100 fast — recommended untuk masalah training lama

Di notebook sudah ada cell:

```bash
!bash /content/drive/MyDrive/ASR_Colab_A100/Colab_ASR_A100_Training/scripts/colab_train_m02b_whisper_small_a100_fast.sh
```

Profile:

```text
batch-size = 32
grad-accum = 1
effective batch = 32
run label = _colab_a100
```

### 7.2 Whisper-small paper-exact — jika butuh sama persis RUN_GUIDE

```bash
!bash /content/drive/MyDrive/ASR_Colab_A100/Colab_ASR_A100_Training/scripts/colab_train_m02b_whisper_small_paper_exact.sh
```

Profile:

```text
batch-size = 8
grad-accum = 4
effective batch = 32
gradient-checkpointing = on
run label = _colab_a100_paper_exact
```

### 7.3 Whisper-medium A100 — optional secondary/appendix

```bash
!bash /content/drive/MyDrive/ASR_Colab_A100/Colab_ASR_A100_Training/scripts/colab_train_m02b_whisper_medium_a100.sh
```

Catatan:

- Ini bukan target utama paper 9-model jika protokol tidak diubah.
- Gunakan sebagai secondary/appendix.
- Jangan jalankan di RTX 4060 8 GB lokal.

---

## 8. Hasil Colab

Script Colab otomatis:

1. Menjalankan training.
2. Menjalankan `test.py`.
3. Menyalin hasil ke Drive:

```text
MyDrive/ASR_Colab_A100/Results/m02b_whisper_small_ft/<run_name>/
MyDrive/ASR_Colab_A100/Results/m02b_whisper_medium_ft/<run_name>/
```

Run name akan berlabel:

```text
run_paper_<YYYYMMDD_HHMMSS>_colab_a100
```

Setelah Colab selesai, agent Windows harus menyalin hasil dari Google Drive ke repository Windows, misalnya ke:

```text
training/m02b_whisper_small_ft/runs/<run_name>_from_colab_a100
```

atau langsung mempertahankan nama run asli jika sudah mengandung `_colab_a100`.

Jangan overwrite run lama.

---

## 9. Sinkronisasi hasil Colab kembali ke Windows

Jika Google Drive Desktop tersedia di Windows, copy dari folder Drive ke:

```text
C:\Users\wayandadang\AI\Dataset ASR\Paper_Datatset_SOTA\training\m02b_whisper_small_ft\runs\
```

Jika memakai WSL2 path Google Drive Desktop, sesuaikan mount path yang tersedia.

Jika memakai rclone dari WSL2:

```bash
cd "/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
mkdir -p training/m02b_whisper_small_ft/runs
rclone copy "gdrive:ASR_Colab_A100/Results/m02b_whisper_small_ft" \
  "training/m02b_whisper_small_ft/runs" \
  --progress --transfers 4 --checkers 8
```

Lalu verifikasi:

```bash
find training/m02b_whisper_small_ft/runs -path '*/test_results/test_paper.json' | sort
```

---

## 10. Setelah hasil Colab ada di Windows

Jalankan agregasi bila semua model paper sudah ada:

```bash
cd "/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
python3 aggregate_paper_test_results.py
python3 -m json.tool reports/paper_benchmark/benchmark.json | grep -E 'n_paper_models_present|missing_paper_models'
```

Jika aggregator belum lengkap, jangan paksa kesimpulan. Laporkan model mana yang masih missing.

---

## 11. Hal yang perlu diaudit sebelum final paper

1. **WER m06/m07 = 1.0 tetapi CER rendah.**
   - Jangan abaikan.
   - Audit normalisasi WER, CTC decoding, spasi/token word segmentation, dan isi `predictions`.

2. **Whisper Colab harus mengikuti `COLAB_A100_WHISPER_START_GUIDE.md` / `START_HERE_COLAB_A100_WHISPER.md`:**
   - Untuk paper utama, jalankan `colab_train_m02b_whisper_small_paper_exact.sh`.
   - Pastikan Colab benar-benar A100 40GB.
   - Pastikan periodic sync ke Drive aktif agar checkpoint tidak hilang jika runtime disconnect.

3. **Whisper Colab result harus memiliki artefak lengkap:**

```text
config.json
meta.json
history.json
log.txt
report.md
best_model/
checkpoints/
test_results/test_paper.json
```

4. **Label asal run harus jelas:**

```text
_linux
_colab_a100
_from_colab_a100
```

5. **Dataset jangan digandakan di repo atau Colab package.**

6. **Jangan commit/upload token, auth, checkpoint besar ke git.**

---

## 12. Checklist cepat untuk agent Windows

- [ ] Buka repo Windows/WSL2.
- [ ] Baca `RUN_GUIDE.md` terbaru.
- [ ] Baca file ini: `transfer_prompt_Linux_to_Win.md`.
- [ ] Verifikasi m06/m07 Linux result sudah ada di Windows.
- [ ] Verifikasi `Colab_ASR_A100_Training` ada di Windows.
- [ ] Buka link Drive dari Chrome.
- [ ] Verifikasi folder Drive berisi Colab package dan dataset.
- [ ] Buka notebook `ASR_Whisper_A100_Colab.ipynb`.
- [ ] Pilih A100.
- [ ] Jalankan Whisper-small A100 fast atau paper-exact sesuai keputusan user.
- [ ] Setelah selesai, copy hasil Colab kembali ke Windows runs folder.
- [ ] Jalankan test/aggregator hanya setelah artifact lengkap.
- [ ] Laporkan status dan temuan, terutama WER/CER anomaly.

---

## 13. Prompt singkat untuk agent Windows

Copy-paste bagian ini ke agent Windows jika ingin instruksi ringkas:

```text
Kita berada di Windows/WSL2 untuk repo Paper_Datatset_SOTA. Baca transfer_prompt_Linux_to_Win.md, RUN_GUIDE.md, dan Colab_ASR_A100_Training/COLAB_A100_README.md. Verifikasi hasil Linux m06/m07 sudah ada di runs dengan label _linux. Jangan duplikasi dataset. Buka link Google Drive: https://drive.google.com/drive/folders/1A8TniSYZ4R4j2K1qJsToioM9xpWZW-gO?usp=sharing. Jalankan notebook Colab_ASR_A100_Training/notebooks/ASR_Whisper_A100_Colab.ipynb di Chrome/Colab dengan GPU A100. Prioritas: training m02b Whisper-small karena lokal lambat. Gunakan run label _colab_a100, pastikan test.py selesai dan test_results/test_paper.json ada. Setelah Colab selesai, sinkronkan hasil ke training/m02b_whisper_small_ft/runs/ di Windows tanpa overwrite, lalu laporkan status dan audit anomali WER/CER m06/m07.
```
