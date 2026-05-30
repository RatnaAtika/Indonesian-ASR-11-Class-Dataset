# TRANSFER PROMPT PAPER DATASET SOTA

## Tujuan File

File ini adalah handoff komprehensif untuk agent model lain yang akan melanjutkan atau meninjau pekerjaan pada proyek `Paper_Datatset_SOTA`.

Isi file ini merangkum:

- tujuan proyek
- prompt/permintaan USER yang sudah dikerjakan
- respons/tindakan yang sudah dilakukan
- file yang dibuat atau diubah
- hasil final yang sudah tervalidasi
- debugging penting yang pernah terjadi
- analisis mismatch Whisper terbaru
- konteks teknis dan aturan kerja yang harus dipertahankan

Catatan cakupan:

- File ini disusun sebagai transfer prompt/handoff menyeluruh, bukan dump log chat mentah baris-per-baris.
- Semua bagian penting yang dapat ditindaklanjuti oleh agent lain sudah disalin dalam bentuk resume teknis: objektif USER, respons/tindakan, artefak, hasil validasi, masalah yang pernah terjadi, dan status lanjutan.
- Angka hasil final diambil dari artefak proyek yang sudah dibuat, terutama `Processed_Balanced19_v3/FINAL_RESUME.md`, `Whisper_Verification/run_20260403_221557/whisper_summary.json`, dan laporan analisis mismatch.

## Identitas Workspace dan Aturan Penting

- Nama folder kerja yang benar adalah `Paper_Datatset_SOTA`
- Perhatikan bahwa nama folder memang mengandung typo `Datatset`, bukan `Dataset`
- Seluruh pekerjaan untuk task ini harus tetap terisolasi di:
  - `c:\Users\ratnaatika\AI\Dataset ASR\Paper_Datatset_SOTA`
- Runtime yang dipakai selama pengerjaan:
  - `WSL2`
  - conda env `torch-gpu`
  - GPU aktif `RTX 4060 8GB`
- Prinsip kerja yang diikuti selama proyek:
  - tidak mengubah source dataset secara destruktif
  - hasil baru selalu dibuat di folder output terpisah
  - run/report bersifat versioned, tidak overwrite sembarangan
  - audit dan verifikasi harus menghasilkan artefak yang bisa ditelusuri

## Ringkasan Tujuan Proyek

Secara garis besar, proyek `Paper_Datatset_SOTA` memiliki dua fase utama yang sudah dikerjakan:

- **Fase A: Audit dan rebuild dataset balanced 19**
  - audit struktur dataset asli
  - parse aturan transkrip aktif per kategori
  - filter 20 WAV source menjadi 19 WAV output per take sesuai transkrip
  - normalkan penamaan output menjadi `01.wav` s.d. `19/20.wav` sesuai ID aktif
  - verifikasi hasil akhir

- **Fase B: Verifikasi isi audio vs transkrip menggunakan Whisper**
  - bangun skrip verifikasi berbasis `openai/whisper-large-v3`
  - jalankan smoke test dan full run
  - debug kegagalan runtime terkait audio decoding
  - sederhanakan progress bar
  - analisis mendalam terhadap `likely_mismatch`

## Struktur Dataset dan Aturan Dasar yang Sudah Terkonfirmasi

- Jumlah kategori transkrip: `11`
- Jumlah respondent per kategori: `20`
- Jumlah take per respondent: `25`
- Jumlah WAV source per take: `20`
- Total take source: `5500`
- Total WAV source: `110000`

Kategori yang digunakan:

- `Kalimat_Deklaratif`
- `Kalimat_Klarifikasi`
- `Kalimat_Kondisional`
- `Kalimat_Konfirmasi`
- `Kalimat_Negasi`
- `Kalimat_Penjadwalan`
- `Kalimat_Perintah`
- `Kalimat_Persuasif`
- `Kalimat_Retoris`
- `Kalimat_Seruan`
- `Kalimat_Tanya`

Aturan balancing hasil parse transkrip aktif:

- `Kalimat_Deklaratif`: drop `[6]`
- `Kalimat_Klarifikasi`: drop `[9]`
- `Kalimat_Kondisional`: drop `[20]`
- `Kalimat_Konfirmasi`: drop `[20]`
- `Kalimat_Negasi`: drop `[8]`
- `Kalimat_Penjadwalan`: drop `[20]`
- `Kalimat_Perintah`: drop `[20]`
- `Kalimat_Persuasif`: drop `[20]`
- `Kalimat_Retoris`: drop `[15]`
- `Kalimat_Seruan`: drop `[20]`
- `Kalimat_Tanya`: drop `[20]`

## Ringkasan Prompt USER dan Respons/Tindakan yang Sudah Dikerjakan

Bagian ini bukan transkrip verbatim penuh percakapan, tetapi resume menyeluruh dari intent USER dan respons kerja yang sudah dilakukan.

### 1. Audit struktur dan aturan dataset

- **Prompt/intent USER**
  - audit struktur `Paper_Dataset_SOTA`
  - identifikasi folder dataset dan transkrip
  - daftar kategori transkrip
  - cek pola file WAV dan konsistensi take

- **Respons/tindakan yang dilakukan**
  - membaca struktur folder `Dataset_Ori` dan `Transkrip_ASR_Jurnal_Dataset`
  - memeriksa format file transkrip kategori
  - memetakan bahwa sumber memiliki struktur kategori -> respondent -> take -> WAV
  - memverifikasi bahwa target balancing adalah 19 kalimat aktif per kategori

- **Hasil**
  - baseline struktur proyek dipahami
  - kategori dan aturan transkrip berhasil dipetakan

### 2. Memetakan aturan balancing dari transkrip

- **Prompt/intent USER**
  - petakan aturan 19 kalimat per kategori dari transkrip
  - tentukan item mana yang harus dibuang berdasarkan transkrip aktif

- **Respons/tindakan yang dilakukan**
  - membaca file `.txt` transkrip per kategori
  - memisahkan entry aktif dari section `note`
  - menghindari salah interpretasi note sebagai daftar keep/drop mentah
  - menetapkan drop ID berdasarkan selisih dari rentang `01-20` terhadap entry aktif

- **Hasil**
  - aturan keep/drop per kategori berhasil ditetapkan dengan aman
  - ini menjadi dasar builder dataset balanced

### 3. Membangun pipeline terisolasi untuk audit dan rebuild dataset

- **Prompt/intent USER**
  - buat pipeline terisolasi untuk audit, filtering, copy hasil ke folder output baru, dan generate report

- **Respons/tindakan yang dilakukan**
  - membuat skrip `process_paper_dataset_sota.py`
  - menambahkan audit transcript
  - menambahkan audit dataset source
  - menambahkan build balanced dataset
  - menambahkan verifikasi output dataset
  - menambahkan export laporan CSV/JSON/TXT/MD

- **File utama**
  - `Paper_Datatset_SOTA/process_paper_dataset_sota.py`

- **Fungsi penting di skrip ini**
  - `parse_transcript_file`
  - `load_transcripts`
  - `inspect_wav_inventory`
  - `audit_dataset`
  - `build_dataset`
  - `verify_output_dataset`
  - `make_report_text`
  - `make_report_md`
  - `make_final_resume_md`

### 4. Menormalkan penamaan output dan memperketat audit

- **Prompt/intent USER**
  - pastikan output memakai penomoran eksplisit dan konsisten `01-20`
  - perbaiki audit agar source dan output tervalidasi ketat

- **Respons/tindakan yang dilakukan**
  - memperketat logika audit source
  - membuat normalisasi output filename ke `zero_padded_2_digit`
  - memastikan file output mengikuti ID aktif transkrip
  - memastikan verifikasi output mendeteksi file hilang/tambahan dan nama non-zero-padded

- **Hasil**
  - output akhir dibakukan ke format `01.wav`, `02.wav`, dan seterusnya
  - verifikasi output menjadi lebih tegas dan mudah diaudit

### 5. Rebuild final ke `Processed_Balanced19_v3`

- **Prompt/intent USER**
  - lakukan rebuild bersih ke folder target final `Processed_Balanced19_v3`
  - verifikasi bahwa seluruh target akhir tercapai

- **Respons/tindakan yang dilakukan**
  - menjalankan pipeline build final ke `Processed_Balanced19_v3`
  - melakukan verifikasi hasil output
  - menyimpan laporan final build dan verifikasi

- **Hasil final yang tervalidasi**
  - kategori: `11`
  - total take: `5500`
  - total WAV source: `110000`
  - total WAV output: `104500`
  - setiap take output berisi `19` WAV
  - take source bermasalah: `0`
  - take build bermasalah: `0`
  - take output bermasalah: `0`
  - semua output zero-padded: `5500` take

### 6. Membuat resume dan report final untuk dataset build

- **Prompt/intent USER**
  - buat resume final yang mendalam untuk hasil build v3

- **Respons/tindakan yang dilakukan**
  - menyusun ringkasan final dan report multi-format
  - memastikan ada file yang mudah dibaca manual maupun mesin

- **Artefak utama**
  - `Processed_Balanced19_v3/FINAL_RESUME.md`
  - `Processed_Balanced19_v3/reports/PROCESS_SUMMARY.txt`
  - `Processed_Balanced19_v3/reports/PROCESS_REPORT.md`
  - `Processed_Balanced19_v3/reports/dataset_audit_before.json`
  - `Processed_Balanced19_v3/reports/build_summary.json`
  - `Processed_Balanced19_v3/reports/output_verify.json`
  - CSV audit/detail lainnya di subfolder `reports/`

### 7. Merancang verifikasi isi audio vs transkrip dengan Whisper

- **Prompt/intent USER**
  - rancang verifikasi kecocokan WAV vs transkrip menggunakan Whisper
  - targetkan dataset output `Processed_Balanced19_v3/Dataset_Balanced19`
  - hasilkan report ringkas dan detail

- **Respons/tindakan yang dilakukan**
  - membuat skrip `verify_paper_dataset_sota_whisper.py`
  - memuat transkrip kategori
  - mengumpulkan file WAV target
  - menjalankan Whisper untuk transkripsi
  - membandingkan hasil prediksi dengan kalimat expected dan kandidat terbaik di kategori yang sama
  - menyimpan report CSV/JSON/TXT/MD

- **File utama**
  - `Paper_Datatset_SOTA/verify_paper_dataset_sota_whisper.py`

### 8. Menyusun panduan penggunaan Whisper verifier

- **Prompt/intent USER**
  - simpan panduan penggunaan skrip verifikasi Whisper ke README terpisah

- **Respons/tindakan yang dilakukan**
  - membuat file `README_RUN_WHISPER.md`
  - menjelaskan parameter, contoh command, default aman, dan rekomendasi smoke test

- **File utama**
  - `Paper_Datatset_SOTA/README_RUN_WHISPER.md`

### 9. Menyederhanakan output progress

- **Prompt/intent USER**
  - ubah output progress agar tidak verbose per-file
  - tampilkan progress bar satu baris dengan ETA

- **Respons/tindakan yang dilakukan**
  - memodifikasi `ProgressPrinter` di skrip Whisper verifier
  - mengganti log panjang per-file dengan progress bar satu baris yang lebih ringkas

- **Hasil**
  - terminal output lebih bersih dan cocok untuk run besar

### 10. Debug kegagalan run Whisper terbaru

- **Prompt/intent USER**
  - debug run Whisper yang gagal total
  - bandingkan run bagus vs run gagal
  - cek error per-file, model/cache, dan pemakaian GPU

- **Respons/tindakan yang dilakukan**
  - membandingkan report run baik dan run gagal
  - menemukan akar masalah pada audio decoding internal yang bergantung pada `torchcodec`
  - mengonfirmasi error `Could not load libtorchcodec`
  - menghindari decoder internal pipeline
  - memuat audio manual memakai `soundfile`
  - menjalankan inferensi langsung via `model.generate` dan `processor.batch_decode`
  - menjaga eksekusi tetap memakai GPU
  - menyesuaikan pemakaian `dtype` agar kompatibel dengan API transformers yang aktif

- **Akar masalah**
  - library `torchcodec` tidak kompatibel dengan kombinasi runtime saat itu
  - akibatnya pipeline audio decode gagal walaupun model Whisper sendiri sebenarnya bisa berjalan

- **Perbaikan yang diterapkan**
  - bypass pipeline decoder
  - audio dibaca manual dari file WAV
  - feature extraction dan generate dilakukan langsung

### 11. Menjalankan full verification seluruh dataset output

- **Prompt/intent USER**
  - setelah debugging selesai, jalankan verifikasi penuh dan analisis hasilnya

- **Respons/tindakan yang dilakukan**
  - menjalankan full run di dataset output final
  - menghasilkan report lengkap di folder run terpisah

- **Run penting**
  - run baseline sukses kecil: `run_20260331_185035`
  - run gagal karena `torchcodec`: `run_20260403_215729`
  - run full sukses: `run_20260403_221557`

### 12. Menganalisis `likely_mismatch` Whisper

- **Prompt/intent USER**
  - analisis mendalam `465 likely_mismatch` dari full run Whisper
  - pahami penyebab utamanya, khususnya apakah hanya shift urutan atau error transkripsi yang lebih kompleks

- **Respons/tindakan yang dilakukan**
  - membaca `whisper_mismatch_only.csv`
  - mengamati bahwa banyak `predicted_text` sangat dekat atau identik dengan `best_match_text`, tetapi `best_match_id` berbeda dari `expected_id`
  - menyimpulkan bahwa banyak mismatch disebabkan pergeseran urutan isi audio per take
  - kemudian dibuat analyzer khusus agar klasifikasi mismatch dapat dipakai ulang

- **File analyzer baru**
  - `Paper_Datatset_SOTA/analyze_whisper_likely_mismatches.py`

- **Artefak analisis mismatch**
  - `Whisper_Verification/run_20260403_221557/whisper_mismatch_only.csv`
  - `Whisper_Verification/run_20260403_221557/whisper_match_details.csv`
  - `Whisper_Verification/run_20260403_221557/likely_mismatch_analysis/likely_mismatch_rows_enriched.csv`
  - `Whisper_Verification/run_20260403_221557/likely_mismatch_analysis/likely_mismatch_take_patterns.csv`
  - `Whisper_Verification/run_20260403_221557/likely_mismatch_analysis/likely_mismatch_summary.json`
  - `Whisper_Verification/run_20260403_221557/likely_mismatch_analysis/likely_mismatch_report.txt`
  - `Whisper_Verification/run_20260403_221557/likely_mismatch_analysis/likely_mismatch_report.md`

## File yang Dibuat atau Diubah dalam Proyek Ini

### File kode utama

- `process_paper_dataset_sota.py`
  - pipeline audit source
  - parse transkrip aktif
  - build dataset balanced 19
  - verifikasi output
  - generate laporan multi-format

- `verify_paper_dataset_sota_whisper.py`
  - verifier berbasis Whisper
  - load transcript dan WAV
  - compute similarity terhadap expected sentence dan best candidate sentence
  - generate report multi-format
  - progress bar satu baris
  - perbaikan runtime untuk bypass `torchcodec`

- `analyze_whisper_likely_mismatches.py`
  - analyzer khusus untuk `likely_mismatch`
  - klasifikasi offset dan pola mismatch per take
  - generate laporan analisis tambahan

### File dokumentasi utama

- `README_RUN_WHISPER.md`
- `Processed_Balanced19_v3/FINAL_RESUME.md`
- `Processed_Balanced19_v3/reports/PROCESS_SUMMARY.txt`
- `Processed_Balanced19_v3/reports/PROCESS_REPORT.md`

## Ringkasan Hasil Final Dataset Build

Berdasarkan `Processed_Balanced19_v3/FINAL_RESUME.md`, hasil final yang tervalidasi adalah:

- Output root: `/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/Processed_Balanced19_v3`
- Status target akhir tercapai: `True`
- Kategori: `11`
- Total take: `5500`
- Total WAV source: `110000`
- Take source valid 1-20: `5500`
- Take source bermasalah: `0`
- Distribusi gaya penomoran source:
  - `mixed_numeric`: `2501`
  - `zero_padded_2_digit`: `2999`
- Total take diproses: `5500`
- Total WAV dicopy: `104500`
- Total WAV diskip: `5500`
- Target WAV output: `104500`
- Take build bermasalah: `0`
- Format nama output: `zero_padded_2_digit`
- Total WAV output aktual: `104500`
- Total WAV output ekspektasi: `104500`
- Take output valid penuh: `5500`
- Take output zero-padded: `5500`
- Take output bermasalah: `0`

## Ringkasan Hasil Full Run Whisper

Berdasarkan `Whisper_Verification/run_20260403_221557/whisper_summary.json`, hasil run penuh yang sukses adalah:

- Model: `openai/whisper-large-v3`
- Language: `indonesian`
- Task: `transcribe`
- Similarity threshold: `0.75`
- Dataset root: `Processed_Balanced19_v3/Dataset_Balanced19`
- Total files: `104500`
- OK files: `104500`
- Error files: `0`
- Exact normalized match count: `76546`
- Best match expected ID count: `103857`
- Pass threshold count: `103261`
- Likely mismatch count: `465`
- Average expected similarity: `0.974362`
- Average best similarity: `0.977337`
- Runtime device: `cuda:0`
- Runtime dtype: `float16`

Distribusi `likely_mismatch` per kategori:

- `Kalimat_Konfirmasi`: `78`
- `Kalimat_Kondisional`: `66`
- `Kalimat_Retoris`: `58`
- `Kalimat_Perintah`: `51`
- `Kalimat_Tanya`: `45`
- `Kalimat_Negasi`: `40`
- `Kalimat_Persuasif`: `40`
- `Kalimat_Penjadwalan`: `37`
- `Kalimat_Klarifikasi`: `31`
- `Kalimat_Seruan`: `12`
- `Kalimat_Deklaratif`: `7`

## Ringkasan Analisis `Likely Mismatch`

Analyzer khusus menemukan bahwa mismatch mayoritas **bukan** error ASR acak.

Ringkasan utama:

- `mismatch_rows`: `465`
- `mismatch_takes`: `99`
- `avg_expected_similarity`: `0.352769`
- `avg_best_similarity`: `0.974768`
- `avg_similarity_margin`: `0.621999`
- `predicted_matches_best_count`: `334`
- `repeat_cue_count`: `51`
- `systematic_or_dominant_shift_rows`: `382`
- `systematic_or_dominant_shift_takes`: `51`
- `adjacent_sentence_confusion_rows`: `30`
- `speaker_said_other_known_sentence_rows`: `3`
- `speech_restart_or_repeat_rows`: `29`

Distribusi offset `best_match_id - expected_id`:

- `-1`: `234`
- `+1`: `200`
- `+2`: `15`
- offset lain: kecil dan sporadis

Kesimpulan analisis mismatch:

- mayoritas mismatch adalah **pergeseran isi audio terhadap nomor file** dalam satu take
- offset yang paling dominan adalah `-1` dan `+1`
- banyak prediksi justru sangat yakin terhadap kalimat valid lain dalam kategori yang sama
- artinya, pada banyak kasus, **audio kemungkinan memang berisi kalimat lain yang valid**, bukan hasil Whisper yang ngawur
- ada subset kecil yang tampak mengandung restart/pengulangan ucapan
- ada subset kecil yang tampak seperti swap isi file antar kalimat tetangga

Contoh take yang sangat representatif untuk audit manual:

- `Kalimat_Kondisional/Elisa/Elisa_Kondisional_Take3`
- `Kalimat_Penjadwalan/Anggi/Anggi_penjadwalan_take8`
- `Kalimat_Tanya/Afgan/Afgan_tanya_take24`
- `Kalimat_Persuasif/Erlin/Erlin_Persuasif_Take1`
- `Kalimat_Kondisional/Anggi/Anggi_kondisional_take5`
- `Kalimat_Konfirmasi/Elisa/Elisa_Konfirmasi_Take18`
- `Kalimat_Retoris/Nanda/Nanda_retoris_take6`
- `Kalimat_Deklaratif/Atika/Atika_Deklaratif_Take23`

## Temuan Debugging Penting yang Harus Diingat Agent Baru

### 1. Masalah `torchcodec`

Masalah terbesar saat verifikasi Whisper bukan pada model, melainkan pada mekanisme decoding audio internal.

Gejala:

- run gagal total
- `ok_files: 0`
- seluruh file error
- error message konsisten berkaitan dengan `Could not load libtorchcodec`

Akar masalah:

- dependency audio decode internal tidak cocok dengan runtime PyTorch / FFmpeg yang tersedia saat itu

Solusi yang sudah diterapkan:

- jangan bergantung pada decoder internal pipeline untuk file lokal
- baca audio manual via `soundfile`
- lakukan feature extraction dan `model.generate()` secara langsung
- decode output token dengan `processor.batch_decode()`

### 2. GPU dan runtime final sudah benar

Run final yang sukses mencatat:

- `device = cuda:0`
- `torch_dtype = float16`
- `error_files = 0`

Jadi, jika muncul mismatch pada run final, **itu bukan karena GPU tidak aktif** dan **bukan karena verifier sedang rusak**.

### 3. Default penggunaan aman

Skrip verifier disetel dengan pendekatan aman untuk debugging:

- default aman hanya `20` file bila tidak memakai `--full-run`
- gunakan `--list-only` untuk cek target tanpa memuat model
- gunakan subset kecil dulu saat debugging agent baru

## Artefak Paling Penting untuk Dibaca Agent Baru

Jika agent baru ingin cepat memahami status proyek, baca urutan berikut:

### Untuk build dataset

- `Processed_Balanced19_v3/FINAL_RESUME.md`
- `Processed_Balanced19_v3/reports/PROCESS_SUMMARY.txt`
- `Processed_Balanced19_v3/reports/PROCESS_REPORT.md`
- `process_paper_dataset_sota.py`

### Untuk verifikasi Whisper

- `README_RUN_WHISPER.md`
- `verify_paper_dataset_sota_whisper.py`
- `Whisper_Verification/run_20260403_221557/whisper_summary.json`
- `Whisper_Verification/run_20260403_221557/whisper_match_details.csv`
- `Whisper_Verification/run_20260403_221557/whisper_mismatch_only.csv`
- `Whisper_Verification/run_20260403_221557/whisper_report.txt`
- `Whisper_Verification/run_20260403_221557/whisper_report.md`

### Untuk analisis mismatch

- `analyze_whisper_likely_mismatches.py`
- `Whisper_Verification/run_20260403_221557/likely_mismatch_analysis/likely_mismatch_report.md`
- `Whisper_Verification/run_20260403_221557/likely_mismatch_analysis/likely_mismatch_take_patterns.csv`
- `Whisper_Verification/run_20260403_221557/likely_mismatch_analysis/likely_mismatch_rows_enriched.csv`

## Command dan Pola Eksekusi yang Sudah Dipakai

### Build dataset balanced

Contoh pola command:

```bash
python3 "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/process_paper_dataset_sota.py" --output-root "Processed_Balanced19_v3"
```

### Whisper verifier: list only

```bash
python3 "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/verify_paper_dataset_sota_whisper.py" --list-only
```

### Whisper verifier: smoke test

```bash
python3 "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/verify_paper_dataset_sota_whisper.py" --max-files 20
```

### Whisper verifier: full run

```bash
python3 "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/verify_paper_dataset_sota_whisper.py" --full-run
```

### Analyzer mismatch

```bash
python3 "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/analyze_whisper_likely_mismatches.py" --run-dir "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/Whisper_Verification/run_20260403_221557"
```

## Status Terkini Proyek `Paper_Datatset_SOTA`

Yang sudah selesai:

- audit source dataset
- mapping aturan transkrip 19 kalimat
- implementasi pipeline build dataset balanced
- normalisasi output filename
- rebuild final ke `Processed_Balanced19_v3`
- verifikasi output final
- pembuatan laporan final build
- implementasi verifier Whisper
- pembuatan README penggunaan Whisper verifier
- penyederhanaan progress output
- debugging kegagalan runtime `torchcodec`
- full verification seluruh dataset output
- analisis mendalam `465 likely_mismatch`
- implementasi analyzer khusus mismatch

Yang belum ada tindakan lanjutan otomatis terhadap data:

- belum ada auto-relabel/auto-repair terhadap take mismatch
- belum ada keputusan final apakah mismatch sistematis akan dipakai untuk koreksi metadata, audit manual, atau dibiarkan sebagai temuan penelitian

Pending work dari daftar kerja penelitian yang masih relevan tetapi belum termasuk scope selesai `Paper_Datatset_SOTA`:

- menentukan pipeline persiapan lanjutan untuk training/evaluasi model ASR, termasuk ekstraksi bila masih arsip, normalisasi audio, cleaning transcript, split train/valid/test, format manifest/Kaldi-style, dan feature extraction sesuai baseline ViT
- merancang tokenisasi subword `SentencePiece` untuk memungkinkan kata baru, termasuk strategi vocab, dampak ke model ViT lama, dan opsi fine-tune/adapter/CTC head reset

## Saran Kerja untuk Agent Baru

- jangan menyentuh source `Dataset_Ori` secara destruktif
- jangan overwrite artefak final yang sudah valid tanpa instruksi eksplisit
- kalau perlu eksperimen lanjutan, buat folder run/output baru
- bila ingin melanjutkan analisis mismatch, mulai dari `likely_mismatch_take_patterns.csv`
- bila ingin membuktikan hipotesis shift urutan, fokus ke take dengan `row_count` besar dan offset seragam
- bila ingin menjalankan ulang Whisper, gunakan subset kecil dulu sebelum full run

## Prompt Transfer Siap Pakai untuk Agent Model Lain

Salin blok di bawah ini jika ingin memberikan konteks penuh ke agent lain:

```text
Kamu sedang melanjutkan proyek di workspace:
C:\Users\ratnaatika\AI\Dataset ASR\Paper_Datatset_SOTA

Catatan penting:
- Nama folder memang "Paper_Datatset_SOTA" (ada typo Datatset)
- Semua pekerjaan harus tetap terisolasi di folder ini
- Runtime yang dipakai selama proyek adalah WSL2 + conda env torch-gpu + GPU RTX 4060
- Jangan ubah source dataset secara destruktif
- Jangan overwrite artefak final tanpa instruksi eksplisit

Status proyek yang sudah selesai:
1. Dataset source dan transkrip sudah diaudit.
2. Aturan balancing 19 kalimat per kategori sudah dipetakan dari transkrip aktif.
3. Pipeline build final ada di process_paper_dataset_sota.py.
4. Output final tervalidasi di Processed_Balanced19_v3 dengan hasil:
   - 11 kategori
   - 5500 take
   - 104500 WAV output
   - 19 WAV per take
   - 0 source bad takes
   - 0 build problem takes
   - 0 bad output takes
5. Whisper verifier ada di verify_paper_dataset_sota_whisper.py.
6. README penggunaan ada di README_RUN_WHISPER.md.
7. Bug audio decoding torchcodec sudah diperbaiki dengan bypass decoder internal dan memakai soundfile + model.generate langsung.
8. Full run Whisper sukses di Whisper_Verification/run_20260403_221557 dengan:
   - total_files 104500
   - ok_files 104500
   - error_files 0
   - likely_mismatch_count 465
9. Analyzer mismatch ada di analyze_whisper_likely_mismatches.py.
10. Analisis mismatch menunjukkan mayoritas kasus adalah systematic/dominant shift isi audio terhadap nomor file, terutama offset -1 dan +1, bukan error ASR acak.

File yang wajib dibaca dulu:
- Processed_Balanced19_v3/FINAL_RESUME.md
- Processed_Balanced19_v3/reports/PROCESS_SUMMARY.txt
- Processed_Balanced19_v3/reports/PROCESS_REPORT.md
- process_paper_dataset_sota.py
- README_RUN_WHISPER.md
- verify_paper_dataset_sota_whisper.py
- analyze_whisper_likely_mismatches.py
- Whisper_Verification/run_20260403_221557/likely_mismatch_analysis/likely_mismatch_report.md

Jika diminta lanjut kerja, anggap hasil final dataset build sudah valid. Fokus pekerjaan berikutnya kemungkinan akan berada pada:
- audit manual mismatch sistematis
- eksperimen auto-relabel berbasis shift per take
- analisis penelitian atas mismatch dan kualitas dataset
```

## Penutup

File ini dimaksudkan sebagai sumber transfer konteks tunggal untuk proyek `Paper_Datatset_SOTA` agar agent lain tidak perlu memulai dari nol.

## Checklist Audit Ulang Kelengkapan File Ini

- Lokasi file sudah benar: `Paper_Datatset_SOTA/transfer_prompt_paper_dataset.md`
- Workspace otoritatif sudah disebut: `c:\Users\ratnaatika\AI\Dataset ASR\Paper_Datatset_SOTA`
- Tujuan proyek dan aturan isolasi sudah disebut
- Prompt/intent USER dan respons/tindakan utama sudah diringkas dari awal audit dataset sampai analisis mismatch
- File kode utama sudah disebut: `process_paper_dataset_sota.py`, `verify_paper_dataset_sota_whisper.py`, `analyze_whisper_likely_mismatches.py`
- Artefak final dataset build sudah disebut
- Artefak full run Whisper sudah disebut
- File sumber mismatch `whisper_mismatch_only.csv` dan `whisper_match_details.csv` sudah disebut
- Hasil final `Processed_Balanced19_v3` sudah dicatat dengan angka validasi
- Hasil run `run_20260403_221557` sudah dicatat dengan angka validasi
- Temuan debugging `torchcodec` sudah dicatat
- Analisis penyebab `465 likely_mismatch` sudah dicatat
- Status pekerjaan yang belum diputuskan sudah dicatat
- Blok prompt siap pakai untuk agent lain sudah tersedia
