# README RUN WHISPER PAPER DATASET SOTA

## Tujuan

File ini menjelaskan cara menjalankan skrip `verify_paper_dataset_sota_whisper.py` untuk mengecek apakah file WAV pada dataset hasil build sesuai dengan kalimat transkrip kategori.

Skrip ini menggunakan model Whisper melalui `transformers` dengan pola berikut:

```python
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
```

Default model yang dipakai di skrip adalah:

```python
openai/whisper-large-v3
```

## Lokasi File

- Skrip verifikasi:
  - `Paper_Datatset_SOTA/verify_paper_dataset_sota_whisper.py`

- Dataset output default yang dicek:
  - `Paper_Datatset_SOTA/Processed_Balanced19_v3/Dataset_Balanced19`

- Folder transkrip default:
  - `Paper_Datatset_SOTA/Transkrip_ASR_Jurnal_Dataset`

- Folder report hasil run:
  - `Paper_Datatset_SOTA/Whisper_Verification/run_YYYYMMDD_HHMMSS`

## Cara Kerja Singkat

Skrip akan:

- Memuat seluruh kalimat transkrip per kategori dari file `.txt`
- Membaca file WAV dari dataset output
- Mengambil `expected_id` dari nama file WAV, misalnya `01.wav`, `02.wav`, dan seterusnya
- Menjalankan Whisper untuk menghasilkan teks prediksi
- Membandingkan hasil prediksi dengan:
  - kalimat expected sesuai ID file
  - seluruh kandidat kalimat dalam kategori yang sama
- Menentukan apakah file kemungkinan cocok atau mismatch

## Prasyarat

Jalankan dari WSL2 dengan environment yang sudah dipakai sebelumnya:

- WSL2
- conda env: `torch-gpu`
- GPU aktif bila tersedia

Contoh aktivasi environment:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate torch-gpu
```

## Perintah Dasar

Contoh umum:

```bash
python3 "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/verify_paper_dataset_sota_whisper.py" --list-only
```

Default aman skrip sekarang hanya mengambil 20 WAV pertama. Gunakan `--list-only` untuk mengecek target tanpa memuat model Whisper.

## Rekomendasi Run Pertama

Disarankan mulai dari smoke test kecil dulu karena `whisper-large-v3` sangat berat jika langsung dijalankan ke seluruh file. Jangan memakai full run untuk debugging agent.

Contoh:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate torch-gpu
python3 "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/verify_paper_dataset_sota_whisper.py" --max-files 5
```

## Contoh Penggunaan

### 1. Smoke test kecil

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate torch-gpu
python3 "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/verify_paper_dataset_sota_whisper.py" --max-files 20
```

### 2. Cek satu kategori

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate torch-gpu
python3 "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/verify_paper_dataset_sota_whisper.py" --category "Kalimat_Negasi" --max-files 100
```

### 3. Cek respondent tertentu

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate torch-gpu
python3 "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/verify_paper_dataset_sota_whisper.py" --category "Kalimat_Negasi" --respondent "Afgan" --max-files 50
```

### 4. Cek take tertentu

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate torch-gpu
python3 "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/verify_paper_dataset_sota_whisper.py" --category "Kalimat_Negasi" --respondent "Afgan" --take "Afgan_negasi_take1"
```

### 5. Full run seluruh dataset output

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate torch-gpu
python3 "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/verify_paper_dataset_sota_whisper.py" --full-run
```

`--full-run` berarti semua file yang lolos filter akan diproses. Ini bisa sangat lama karena dataset berisi puluhan/ratusan ribu WAV; gunakan hanya untuk run terencana, bukan debugging agent.

## Parameter Penting

- `--dataset-root`
  - Path dataset WAV yang ingin dicek
  - Default: `Processed_Balanced19_v3/Dataset_Balanced19`

- `--transcript-dir`
  - Path folder transkrip `.txt`
  - Default: `Transkrip_ASR_Jurnal_Dataset`

- `--report-base`
  - Folder dasar untuk menyimpan hasil run
  - Default: `Whisper_Verification`

- `--model-id`
  - Model Whisper Hugging Face
  - Default: `openai/whisper-large-v3`

- `--language`
  - Bahasa yang dipass ke Whisper
  - Default: `indonesian`

- `--task`
  - Task Whisper
  - Default: `transcribe`

- `--similarity-threshold`
  - Ambang similarity untuk menandai kecocokan
  - Default: `0.75`

- `--max-files`
  - Membatasi jumlah file yang diproses
  - Default aman: `20`
  - Nilai `0` hanya dipakai lewat `--full-run`

- `--full-run`
  - Memproses semua file yang lolos filter
  - Wajib untuk run seluruh dataset agar tidak terjadi full scan tanpa sengaja

- `--category`
  - Filter kategori, bisa diisi satu atau lebih dipisah koma

- `--respondent`
  - Filter respondent, bisa diisi satu atau lebih dipisah koma

- `--take`
  - Filter take, bisa diisi satu atau lebih dipisah koma

## Hasil Output per Run

Setiap run akan membuat folder baru seperti:

```text
Paper_Datatset_SOTA/Whisper_Verification/run_YYYYMMDD_HHMMSS
```

Isi report:

- `whisper_match_details.csv`
  - Seluruh file yang diproses
  - Menyimpan expected ID, expected text, predicted text, best match, similarity, dan status

- `whisper_mismatch_only.csv`
  - Hanya kandidat mismatch

- `whisper_summary.json`
  - Ringkasan terstruktur untuk dibaca ulang atau diproses lanjutan

- `whisper_report.txt`
  - Ringkasan teks cepat

- `whisper_report.md`
  - Ringkasan markdown yang lebih enak dibaca

## Interpretasi Kolom Penting

- `expected_id`
  - ID kalimat yang seharusnya cocok dengan nama WAV

- `expected_text`
  - Kalimat transkrip yang seharusnya diucapkan

- `predicted_text`
  - Hasil transkripsi Whisper

- `best_match_id`
  - ID kalimat kategori yang paling mirip dengan hasil Whisper

- `matches_expected_id`
  - `True` bila kandidat terbaik sesuai dengan ID file

- `expected_similarity`
  - Similarity antara hasil Whisper dan kalimat expected

- `best_similarity`
  - Similarity terhadap kandidat transkrip terbaik dalam kategori itu

- `passes_threshold`
  - `True` bila hasil memenuhi threshold dan best match sama dengan expected ID

- `likely_mismatch`
  - `True` bila kandidat terbaik justru mengarah ke ID lain dengan similarity tinggi

## Catatan Penting

- Dataset `Processed_Balanced19_v3` sebelumnya sudah tervalidasi struktur file-nya:
  - `11` kategori
  - `5500` take
  - `104500` WAV
  - `19 WAV/take`
  - `0 bad take`

- Skrip Whisper ini dipakai untuk audit **isi ucapan vs transkrip**, bukan audit struktur folder.

- `whisper-large-v3` sangat berat untuk full run semua `104500` file.

- Sangat disarankan mulai dari:
  - smoke test `10-20` file
  - lalu `1` kategori
  - lalu subset respondent tertentu
  - baru full run jika memang dibutuhkan

- Contoh dari `whisper-test.py` yang memakai `load_dataset("distil-whisper/librispeech_long", ...)` tidak dipakai di sini karena target verifikasi adalah file WAV lokal.

## Validasi yang Sudah Dilakukan

Skrip `verify_paper_dataset_sota_whisper.py` sudah lolos validasi sintaks:

```bash
python3 -m py_compile "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/verify_paper_dataset_sota_whisper.py"
```

## Saran Penggunaan Praktis

Urutan yang aman:

1. Jalankan smoke test `--max-files 20`
2. Jalankan satu kategori, misalnya `Kalimat_Negasi`
3. Lihat `whisper_mismatch_only.csv`
4. Audit manual beberapa baris mismatch
5. Jika pola hasilnya bagus, lanjutkan ke subset lebih besar atau full run

## Ringkasan

- Skrip Whisper verifikasi sudah terisolasi di dalam `Paper_Datatset_SOTA`
- README ini menyimpan cara pakainya untuk akses di kemudian hari
- Belum dilakukan inferensi penuh secara otomatis dari sesi ini
