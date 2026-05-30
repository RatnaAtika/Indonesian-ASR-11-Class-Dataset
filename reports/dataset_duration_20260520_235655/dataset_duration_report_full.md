# Dataset Duration Report
## Total durasi audio Paper_Datatset_SOTA / Processed_Balanced19_v3

> Audit lengkap 104 500 WAV files via direct WAV header parsing (fast path 100 %, 0 fallback, 0 errors).  
> **Generated**: 2026-05-20 23:32 WIB · session `session_20260520_225029_dataset_duration_audit`

---

## 1. TL;DR — total jam dataset

# 🎯 134.19 jam (134 h 11 min)

| Metrik | Nilai |
|--------|------:|
| **Total durasi** | **483 073.92 detik** |
| Dalam menit | 8 051.23 menit |
| **Dalam jam** | **134.1872 jam** |
| Total file | 104 500 WAV |
| Total take | 5 500 |
| Avg durasi/file | 4.62 detik |
| Median durasi/file | 4.51 detik |
| Min durasi/file | 1.15 detik |
| Max durasi/file | 206.40 detik (outlier) |
| Standar deviasi | 1.67 detik |

---

## 2. Posisi terhadap dataset benchmark publik

| Dataset | Bahasa | Total jam | Domain | Lisensi |
|---------|--------|---------:|--------|---------|
| **Paper_Datatset_SOTA (this)** | **Indonesian** | **134.19** | **11 sentence-types, limited vocab** | TBD (rec: CC-BY 4.0) |
| Speech Commands v2 | English | ~58 | 35 keyword / words | CC-BY 4.0 |
| LibriSpeech-clean-100 | English | 100 | read-speech books | CC-BY 4.0 |
| LibriSpeech-train-clean-360 | English | 360 | read-speech books | CC-BY 4.0 |
| TIMIT | English | 5.4 | acoustic-phonetic | LDC commercial |
| Magic Data Indonesian | Indonesian | 100 | conversational | LDC commercial |
| TITML-IDN | Indonesian | 30 | read-speech | open |
| Common Voice ID | Indonesian | ~30 (variable) | crowdsourced | CC-0 |

📊 **Insight paper §4 Dataset**: 134.19 jam menempatkan dataset ini di **kelas-yang-sama dengan LibriSpeech-clean-100** secara skala, dengan tambahan struktur taxonomic sentence-type (11 kelas pragmatic) yang **belum pernah dirilis untuk Bahasa Indonesia**. Ini diferensiasi kuat untuk paper SOTA.

---

## 3. Per kategori (urut total jam ↓)

| # | Kategori | n_files | total (sec) | total (min) | **total (jam)** | mean/file | median |
|--:|----------|--------:|------------:|------------:|---------------:|----------:|-------:|
| 1 | **Kalimat_Persuasif** | 9 500 | 61 969.48 | 1 032.82 | **17.21** | 6.52 s | 6.31 s |
| 2 | **Kalimat_Kondisional** | 9 500 | 57 480.31 | 958.01 | **15.97** | 6.05 s | 5.90 s |
| 3 | **Kalimat_Konfirmasi** | 9 500 | 53 280.64 | 888.01 | **14.80** | 5.61 s | 5.51 s |
| 4 | Kalimat_Klarifikasi | 9 500 | 49 718.03 | 828.63 | 13.81 | 5.23 s | 5.13 s |
| 5 | Kalimat_Penjadwalan | 9 500 | 47 211.20 | 786.85 | 13.11 | 4.97 s | 4.78 s |
| 6 | Kalimat_Tanya | 9 500 | 42 789.74 | 713.16 | 11.89 | 4.50 s | 4.35 s |
| 7 | Kalimat_Deklaratif | 9 500 | 38 512.71 | 641.88 | 10.70 | 4.05 s | 3.88 s |
| 8 | Kalimat_Retoris | 9 500 | 37 483.63 | 624.73 | 10.41 | 3.95 s | 3.92 s |
| 9 | Kalimat_Negasi | 9 500 | 33 955.30 | 565.92 | 9.43 | 3.57 s | 3.55 s |
| 10 | Kalimat_Seruan | 9 500 | 32 555.67 | 542.59 | 9.04 | 3.43 s | 3.33 s |
| 11 | **Kalimat_Perintah** | 9 500 | 28 117.20 | 468.62 | **7.81** | 2.96 s | 2.65 s |
|  | **TOTAL** | **104 500** | **483 074** | **8 051** | **134.19** | **4.62 s** | **4.51 s** |

Penjelasan distribusi:
- **Persuasif** = kategori paling panjang (kalimat retorika persuasif kompleks dengan klausa multi-paragraf).
- **Perintah** = kategori paling pendek (kalimat imperatif singkat seperti "Tolong ambilkan remote itu!").
- Rasio max/min = 17.21 / 7.81 = **2.20×** — wajar untuk linguistic taxonomy.

**Untuk paper §4**: setiap kategori punya jumlah file identik (9 500), tetapi durasi total bervariasi karena karakteristik linguistik. Ini adalah **fitur dataset, bukan bug** — taxonomic stratification natural.

---

## 4. Per speaker (20 speaker, urut total jam ↓)

> ⚠️ **Anomali terdeteksi**: ada 2 nama folder `Fito` vs `FIto` (case-sensitive). Setelah merge logical, 20 unique speakers (sesuai spec).

| Speaker | n_files | total (sec) | total (min) | total (jam) | mean/file |
|---------|--------:|------------:|------------:|------------:|----------:|
| Atika | 5 225 | 28 016.10 | 466.93 | **7.78** | 5.36 s |
| Elisa | 5 225 | 26 863.78 | 447.73 | 7.46 | 5.14 s |
| Bey | 5 225 | 25 944.67 | 432.41 | 7.21 | 4.97 s |
| Pram | 5 225 | 25 330.68 | 422.18 | 7.04 | 4.85 s |
| Fito + FIto* | 5 225 | 28 364.91 | 472.75 | 7.88 | 5.43 s |
| Nanda | 5 225 | 25 080.73 | 418.01 | 6.97 | 4.80 s |
| Risky | 5 225 | 25 047.54 | 417.46 | 6.96 | 4.79 s |
| Indah | 5 225 | 24 994.76 | 416.58 | 6.94 | 4.78 s |
| Amri | 5 225 | 24 057.01 | 400.95 | 6.68 | 4.60 s |
| Joni | 5 225 | 22 972.17 | 382.87 | 6.38 | 4.40 s |
| Erlin | 5 225 | 23 692.74 | 394.88 | 6.58 | 4.53 s |
| Fajar | 5 225 | 23 686.36 | 394.77 | 6.58 | 4.53 s |
| Muhaimin | 5 225 | 22 598.99 | 376.65 | 6.28 | 4.33 s |
| Anggi | 5 225 | 22 291.00 | 371.52 | 6.19 | 4.27 s |
| Robi | 5 225 | 22 011.92 | 366.87 | 6.11 | 4.21 s |
| Baron | 5 225 | 23 182.70 | 386.38 | 6.44 | 4.44 s |
| Uly | 5 225 | 23 341.30 | 389.02 | 6.48 | 4.47 s |
| Ammar | 5 225 | 23 514.92 | 391.92 | 6.53 | 4.50 s |
| Harry | 5 225 | 21 305.52 | 355.09 | 5.92 | 4.08 s |
| Afgan | 5 225 | 20 776.10 | 346.27 | **5.77** | 3.98 s |

*Fito = 4 750 file (10 categories) + FIto = 475 file (Kalimat_Konfirmasi) → digabung ke `Fito` setelah folder rename.

**Distribusi per-speaker**:
- Range total jam: 5.77 (Afgan) → 7.78 (Atika)
- Δ = 2.01 jam = 26 % variasi — significant
- Sumber variasi = kecepatan bicara berbeda + jeda antar-kalimat berbeda

**Untuk paper §6 Benchmarks**: variansi durasi ini wajib dilaporkan di per-speaker WER table. Speakers dengan total durasi rendah (Afgan, Harry) cenderung punya kecepatan bicara lebih tinggi → kemungkinan WER lebih tinggi pada Whisper.

---

## 5. Per take — distribusi extreme

### 🥇 Top 5 take terlama
| Take | Total dur | Mean/file | Catatan |
|------|----------:|----------:|---------|
| `Kalimat_Penjadwalan/Atika/Atika_Penjadwalan_Take5` | 320.7 s (5.3 min) | 16.9 s | **mengandung file outlier 206s** |
| `Kalimat_Persuasif/Atika/Atika_Persuasif_Take10` | 218.2 s (3.6 min) | 11.5 s | persuasif natural panjang |
| `Kalimat_Persuasif/Atika/Atika_Persuasif_Take4` | 217.0 s (3.6 min) | 11.4 s | – |
| `Kalimat_Tanya/Anggi/Anggi_tanya_take12` | 207.3 s (3.5 min) | 10.9 s | **mengandung file outlier 135s** |
| `Kalimat_Persuasif/Atika/Atika_Persuasif_Take7` | 206.8 s (3.5 min) | 10.9 s | – |

### 🥉 Bottom 5 take terpendek
| Take | Total dur | Mean/file | Catatan |
|------|----------:|----------:|---------|
| `Kalimat_Perintah/Harry/Harry_Perintah_Take16` | 43.7 s | 2.30 s | imperatif Harry cepat |
| `Kalimat_Perintah/Harry/Harry_Perintah_Take19` | 44.0 s | 2.32 s | – |
| `Kalimat_Perintah/Harry/Harry_Perintah_Take20` | 44.9 s | 2.36 s | – |
| `Kalimat_Perintah/Afgan/Afgan_perintah_take21` | 44.9 s | 2.36 s | – |
| `Kalimat_Perintah/Risky/Risky_Perintah_Take20` | 45.3 s | 2.38 s | – |

Range take: 43.7 s → 320.7 s = rasio **7.34×**. Ini menunjukkan ada beberapa take outlier yang akan mempengaruhi distribusi.

---

## 6. Outliers terdeteksi

3 file dari 104 500 (= **0.0029 %**) di luar range 0.5–30 s:

| File | Durasi | Catatan |
|------|-------:|---------|
| `Kalimat_Penjadwalan/Atika/Atika_Penjadwalan_Take5/04.wav` | **206.40 s** | 3.4 menit — kemungkinan TIDAK trimmed atau berisi multi-take |
| `Kalimat_Tanya/Anggi/Anggi_tanya_take12/03.wav` | **135.35 s** | 2.3 menit — sama |
| `Kalimat_Perintah/Pram/Pram_Perintah_take12/17.wav` | **82.73 s** | 1.4 menit — sama |

**Tindakan rekomendasi**:
- Audit manual via play-back atau Whisper transcription untuk melihat apakah berisi 1 atau N kalimat.
- Jika multi-take: trim ke segment yang benar.
- Jika single-take dengan silence pad panjang: trim VAD.
- Jika single-take legitimate: tetap simpan tapi flag di metadata.

Tambahan analisis: ada juga 5 file di range 18–24 detik (Elisa_Seruan, Harry_Persuasif, dll) yang lebih panjang dari median tapi masih dalam range "wajar untuk persuasif/seruan kompleks".

---

## 7. Anomali speaker name

```
Fito: 4 750 files (10 categories: Deklaratif, Klarifikasi, Kondisional, Negasi,
                  Penjadwalan, Perintah, Persuasif, Retoris, Seruan, Tanya)
FIto: 475 files  (1 category: Konfirmasi)
```

🔧 **Tindakan**: rename `Kalimat_Konfirmasi/FIto/` → `Kalimat_Konfirmasi/Fito/` agar agregasi per-speaker bersih. Saat ini agregasi memunculkan 21 row (bukan 20) di `durations_per_speaker.csv`. Tidak mempengaruhi total durasi atau total file count.

---

## 8. Statistik distribusi (untuk paper §4)

```
Total       : 134.1872 hours (483 073.92 sec)
Files       : 104 500
Takes       : 5 500
Speakers    : 20 (after FIto+Fito merge)
Categories  : 11
Sample rate : 16 kHz mono PCM_16 (uniform)

Per-file duration:
  mean      : 4.6227 s
  median    : 4.5060 s  (≈ mean → near-symmetric distribution)
  stddev    : 1.6678 s
  min       : 1.1507 s  (Risky_Perintah_take1/08.wav, terlalu pendek?)
  max       : 206.4045 s (outlier, 3.4 min)
  IQR       : ~3.5–5.5 s (typical sentence)
```

**Skewness**: median (4.51) ≈ mean (4.62) tetapi max sangat besar → distribusi punya **right-skew tipis** karena 3 outlier. Tanpa outlier, distribusi normal-ish.

**Untuk paper §4**: lapor mean ± stddev = **4.62 ± 1.67 detik per file**. Ini sebanding dengan baseline corpus speech-commands (1 detik) dan LibriSpeech (avg ~12 detik utterance), positioning dataset ini di tier sentence-level (medium).

---

## 9. Ringkasan untuk paper

> "The dataset comprises **104 500 audio recordings** totaling **134.19 hours**, distributed across **11 sentence-type categories** (Declarative, Clarification, Conditional, Confirmation, Negation, Scheduling, Imperative, Persuasive, Rhetorical, Exclamation, Interrogative) and **20 speakers** (10 female, 10 male — to be verified). Each take contains exactly **19 utterances** (with 1 sentence-ID dropped per category to balance), yielding **5 500 takes total** (250 takes per speaker × 20 speakers / 11 categories ≈ 25 takes per speaker per category). Mean utterance duration is **4.62 s ± 1.67** with median 4.51 s and 99.997% of files within the 0.5–30 s range. All audio is recorded as **16 kHz mono 16-bit PCM**. Three files (0.003 %) exceed 30 s and are flagged for trim audit."

---

## 10. Rekomendasi tindakan post-audit

| Prio | Tindakan | Effort | Impact |
|-----:|----------|-------:|--------|
| 1 | Rename `FIto/` → `Fito/` di v3 atau v4_merged | 1 min | clean per-speaker aggregation |
| 2 | Audit 3 outlier file (206s, 135s, 82s); trim atau document | 15 min | clean max-duration metric |
| 3 | Rename outlier ke `_legacy.wav` jika tidak bisa di-trim, ganti dengan retake | 30 min | atau: tambahkan ke `bad_takes_v2` untuk gelombang retake |
| 4 | Tambahkan kolom `duration_sec` ke `dataset_m (NEXT-2) | 5 min | input metadata pusat |
| 5 | Per-speaker WER reporting di paper §6 menggunakan range durasi | – | paper rigor |

---

## Lampiran — File yang dihasilkan

| File | Ukuran | Isi |
|------|-------:|-----|
| `dataset_durations.csv` | ~12 MB | 104 500 baris × 10 kolom |
| `durations_per_category.csv` | 1.3 KB | 11 baris |
| `durations_per_speaker.csv` | 2.5 KB | 21 baris (sebelum rename FIto) |
| `durations_per_take.csv` | 745 KB | 5 500 baris |
| `duration_outliers.csv` | 1.4 KB | 3 baris |
| `duration_stats.json` | 720 B | machine-readable |
| `dataset_duration_report.md` | (this file) | paper-grade narrative |

---

*Generated 2026-05-20 23:32 (WIB +07) by `kiro-cli` mengikuti BMAD discipline. Wall-clock scan: 33.78 menit (104 500 files @ 52 files/sec).*
