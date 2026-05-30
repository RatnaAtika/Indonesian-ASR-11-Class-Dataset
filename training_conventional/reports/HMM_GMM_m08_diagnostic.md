# Laporan Diagnostik — HMM-GMM (m08) vs DNN-HMM (m09)

**Tanggal:** 2026-05-29
**Pertanyaan:** Apakah HMM-GMM (m08) sudah diperbaiki seperti DNN-HMM (m09), atau memang seperti itu batasannya?

---

## TL;DR

- **DNN-HMM (m09) SUDAH diperbaiki** hari ini: bug "frame-CE + uniform alignment + collapse" yang membuat WER ~3 diganti menjadi **training CTC** (blank = `<pad>`=0). Lihat docstring `run_dnn_hmm` ("fixed 2026-05-29").
- **HMM-GMM (m08) BELUM diperbaiki.** Tapi WER>1 di m08 **bukan batasan desain yang tak terhindarkan** seperti yang ditulis di docstring. Itu **kegagalan diskriminasi model akustik** yang sebenarnya bisa diperbaiki.
- Catatan di kode (`Predictions cap at the closed sentence set, so WER >= floor of test-template coverage`) **tidak berlaku** untuk dataset ini, karena **100% template val ada di train**. Jadi alasan "memang batasannya" yang tertulis itu **keliru** untuk korpus v7.

---

## 1. Hasil aktual m08 (run_paper_20260529)

| Metrik | Nilai |
|---|---|
| WER | **1.0255** (>1.0) |
| CER | 0.7695 |
| MER | 0.9010 |
| WIL | 0.9875 |
| Train acc (proxy) | 0.197 |
| Val acc (proxy) | 0.230 |
| N templates | 209 |
| Train / Val utts | 71792 / 15376 |
| Waktu train | 03:01:19 |
| Waktu eval | 00:57:48 |
| Config | states=5, mixtures=3, iters=30, cov=diag |

Contoh prediksi: PRED selalu kalimat utuh & gramatikal (template asli) tapi **template yang salah** — mis. LABEL "saya membutuhkan rekomendasi tempat wisata di kota palembang" → PRED "saya ingin berkontribusi untuk kemajuan kota palembang melalui pendidikan".

---

## 2. Apa yang dilakukan m08 (desain)

m08 adalah **template classifier closed-vocabulary**:
1. Kelompokkan utterance train per transkrip → 209 template.
2. Latih 1 GMM-HMM per template (left-right, transmat fixed, Baum-Welch hanya update emisi `mcw`).
3. Saat test: skor utterance `x` ke semua 209 HMM, ambil `argmax log-likelihood` → keluarkan teks template tsebagai prediksi.

Karena keluaran selalu template utuh, akurasi per-token (CER 0.77) bisa terlihat "tidak terlalu buruk" walau template-nya salah, tapi WER tetap > 1.

---

## 3. Mengapa WER > 1 — analisis akar masalah

WER bisa > 1 karena setiap kesalahan = ganti seluruh kalimat: jika hipotesis lebih panjang dari referensi, jumlah edit (sub+ins) bisa melebihi jumlah kata referensi.

**Yang penting: WER>1 di sini BUKAN floor coverage.**

Pemeriksaan korpus (train.pkl / valid.pkl):

```
unique train templates : 209
unique val templates    : 206
val templates ⊂ train   : 206 / 206  (100%)
val utts dengan template terlihat di train : 15376 / 15376 (100.0%)
```

Artinya secara teori classifier **bisa mencapai WER≈0** kalau ranking likelihood-nya benar. Kenyataannya val_acc hanya 0.23 → ranking GMM-HMM **mendekati acak** (chance ≈ 1/209 = 0.005, jadi 0.23 sedikit di atas acak tapi sangat jauh dari benar).

Jadi catatan docstring berikut **menyesatkan untuk dataset ini**:
> "Predictions cap at the closed sentence set, so WER >= floor of test-template coverage; we report the gap as part of the baseline limitations"

Coverage = 100%, floor = 0. Masalahnya bukan vocabulary, tapi **model akustik tidak diskriminatif**.

---

## 4. Penyebab teknis ranking lemah

Kombinasi pada `run_hmm_gmm` yang menekan diskriminasi:

1. **Kapasitas model sangat kecil**: states=5, mixtures=3 untuk merepresentasikan kalimat penuh berdurasi ~215 frame (fitur 80-dim). 5 state untuk satu kalimat → tiap state harus memodelkan ~43 frame fonem berbeda. Terlalu kasar untuk membedakan 209 kalimat yang banyak berbagi kata.
2. **Transisi di-fix (params="mcw")**: transmat left-right tidak di-update; durasi/timing tidak ikut membedakan template.
3. **Skor likelihood mentah tanpa normalisasi struktural**: semua template diskor pada `x` yang sama, jadi panjang tidak bias, tapi 5-state GMM-HMM cenderung memberi likelihood tinggi ke template yang fonetiknya "umum" → bias ke kalimat tertentu (terlihat dari PRED yang berulang-ulang sama).
4. **Fitur**: 80-dim (kemungkinan fbank/mel) tanpa delta; GMM-HMM klasik biasanya pakai MFCC+Δ+ΔΔ dan jumlah state proporsional panjang.

---

## 5. Status "diperbaiki" per model

| Model | Mode | Status fix 2026-05-29 | WER terbaru |
|---|---|---|---|
| m08 HMM-GMM | `hmm_gmm` | **BELUM** diperbaiki | 1.0255 |
| m09 DNN-HMM | `dnn_hmm` | **SUDAH** (CE→CTC) | 0.988 (epoch 1, run baru) |
| m10 GMM-HMM-DNN | `gmm_hmm_dnn` | Stage-3 ikut perbaikan m09 (CTC); Stage-1 = m08 (belum) | — |

Catatan m10: karena Stage-1 m10 memanggil `run_hmm_gmm` yang sama, kelemahan m08 ikut terbawa ke metrik Stage-1 m10 (tapi metrik final m10 = Stage-3 CTC).

---

## 6. Apakah perlu diperbaiki? — Rekomendasi

Ada **dua jalur sah**, tergantung peran m08 di paper:

### Jalur A — Biarkan apa adanya, tapi koreksi narasi (paling cepat)
Jika m08 memang dimaksudkan sebagai **baseline 1990-an yang lemah** untuk menunjukkan progres ke model modern, maka angka WER~1 itu **wajar sebagai baseline**. Tapi WAJIB:
- Perbaiki docstring/laporan: jangan klaim "WER ≥ floor of test-template coverage" — coverage 100%, floor 0. Sebut jujur: "ranking GMM-HMM mendekati acak karena kapasitas model rendah pada kalimat penuh."
- Laporkan sebagai *limitation of low-capacity generative template scoring*, bukan limitation of closed vocabulary.

### Jalur B — Perbaiki agar diskriminatif (kalau ingin baseline yang adil)
Perubahan berdampak besar, dari yang termurah:
1. **Naikkan kapasitas**: states proporsional ke jumlah token/durasi (mis. `states ≈ 3×jumlah_kata` atau berbasis fonem), mixtures 8–16.
2. **Aktifkan update transmat** (`params="tmcw"`, biarkan startprob left-right) agar durasi ikut membedakan.
3. **Tambah fitur dinamis** (Δ+ΔΔ) — sangat standar untuk GMM-HMM.
4. **Normalisasi skor** per-frame (`score(x)/T`) jika nanti membandingkan antar-panjang (saat ini tidak perlu karena x sama).
5. Opsi paling benar secara metodologi: **monophone GMM-HMM + bigram/loop grammar** alih-alih per-kalimat template, lalu Viterbi decode — ini baseline HMM-GMM "betulan" dan bisa generalisasi ke kalimat tak terlihat.

> ⚠️ Eksperimen ulang m08 = full run ~4 jam (train 3 jam + eval 1 jam, CPU-only, 6.6 utt/s). Jalankan di **terminal terpisah**, bukan dari pi-cli.

---

## 7. Verifikasi yang sudah & belum dilakukan

**Sudah diverifikasi (dibaca/dijalankan):**
- Kode `pkl_hmm_trainer.py` (mode hmm_gmm, dnn_hmm, gmm_hmm_dnn).
- Hasil run m08 `run_paper_20260529` (report.md, history.json, log.txt).
- Overlap template train/val dari pickle aktual (100% coverage).
- Distribusi utts/template (min 6, median/max 350), fitur 80-dim, ~215 frame/utt.

**Belum diverifikasi:**
- Apakah Jalur B benar-benar menurunkan WER (belum dijalankan eksperimen).
- Isi pasti fitur 80-dim (fbank vs MFCC) — diasumsikan dari dim.
- Run m09 baru hanya sampai epoch 1 (WER 0.988) — proses sudah dimatikan; angka final 30-epoch belum ada.

---

## Kesimpulan

HMM-GMM (m08) **belum diperbaiki**. WER>1 yang terlihat **bukan batasan closed-vocabulary** (coverage val 100%, floor seharusnya 0), melainkan **GMM-HMM 5-state/3-mix terlalu lemah** untuk membedakan 209 kalimat penuh, sehingga ranking likelihood mendekati acak. Pilih Jalur A (terima sebagai baseline lemah + koreksi narasi yang salah) atau Jalur B (perkuat model agar adil). DNN-HMM (m09) sudah benar lewat migrasi ke CTC.
