# Analisis Baseline m08 (HMM-GMM): Mengapa Model Generatif Template Tidak Cocok untuk Korpus v7

**Slot paper:** Section 5.1 (Baseline Analysis) / Appendix — *Why the classical generative baseline fails*
**Model:** `m08-hmm-gmm` — HMM-GMM template classifier (family HMM, era 1990-an)
**Test set:** 15.376 utterance (full v7 test split)
**Keputusan editorial:** Jalur A — model dipertahankan apa adanya sebagai baseline klasik; laporan ini memberikan analisis tersendiri yang jujur dan memotivasi progresi ke arsitektur yang lebih canggih hingga model novel ViT-modified-ID (Ratna 2026).

---

## 5.1.1 Ringkasan hasil

| Metrik | Nilai (test split, n=15.376) |
|---|---|
| WER | 1.1687 |
| CER | 0.8980 |
| MER | 0.9272 |
| WIL | 0.9932 |
| SER | 0.9400 |
| Parameter | n/a (model generatif non-parametrik-neural) |
| Wall time (eval) | sangat rendah; train CPU-only ~3 jam |

HMM-GMM menempati posisi terbawah dari sembilan sistem yang dibandingkan dan merupakan satu-satunya sistem dengan **WER > 1.0**. Angka ini bukan artefak pelaporan: ia adalah konsekuensi langsung dari ketidakcocokan struktural antara asumsi model dan karakteristik korpus v7. Bagian ini menjelaskan ketidakcocokan tersebut dan menunjukkan mengapa ia secara alami mengarahkan paper menuju keluarga model diskriminatif dan akhirnya ke arsitektur attention berbasis ViT.

---

## 5.1.2 Apa yang sebenarnya dilakukan model

m08 adalah pendekatan **klasifikasi template generatif closed-vocabulary**, representatif untuk paradigma ASR era 1990-an pada kosakata terbatas:

1. Seluruh utterance pelatihan dikelompokkan berdasarkan transkrip identik, menghasilkan 209 *template* kalimat unik.
2. Untuk setiap template dilatih satu GMM-HMM left-right (5 state, 3 campuran Gaussian per state, kovarians diagonal) menggunakan Baum-Welch.
3. Pada inferensi, setiap utterance uji `x` diskor terhadap seluruh 209 HMM, dan kalimat dari model dengan log-likelihood tertinggi dikeluarkan sebagai hipotesis (`argmax_t log p(x | HMM_t)`).

Sifat keluaran ini penting untuk menafsirkan metrik: **hipotesis selalu berupa kalimat penuh yang gramatikal** (karena ia adalah template asli), tetapi sering kali merupakan **kalimat yang salah**. Akibatnya CER tampak "tidak ekstrem" (0.898) padahal pada tingkat kalimat model hampir selalu keliru (SER 0.94), dan WER melampaui 1.0 karena setiap kesalahan menggantikan seluruh kalimat sekaligus.

---

## 5.1.3 Diagnosis: ini bukan keterbatasan kosakata, melainkan keterbatasan daya pisah model

Penjelasan paling mudah — "model dibatasi kosakata tertutup, jadi wajar gagal pada kalimat tak terlihat" — **tidak berlaku** untuk korpus ini. Pemeriksaan langsung terhadap split pelatihan dan pengujian menunjukkan:

> Seluruh 206 template unik pada test split (100%) juga muncul pada train split (209 template), sehingga **100% utterance uji memiliki template yang seharusnya dapat dikenali**.

Dengan kata lain, batas bawah teoretis WER untuk classifier ini adalah **nol**: setiap kalimat uji memiliki template yang benar di antara 209 kandidat. Kegagalan terjadi karena **peringkat likelihood GMM-HMM hampir tidak diskriminatif** — akurasi pemilihan template hanya ~0.20–0.23, hanya sedikit di atas tebakan acak (1/209 ≈ 0.005 untuk acak murni, namun jauh dari akurasi yang dibutuhkan). Model secara sistematis memberi likelihood tinggi pada beberapa template berfonem "umum", terlihat dari hipotesis yang berulang-ulang sama untuk masukan yang berbeda.

Maka temuan inti paper untuk baseline ini adalah:

**HMM-GMM gagal pada v7 bukan karena keterbatasan closed-vocabulary, melainkan karena model akustik generatif berkapasitas rendah tidak mampu membedakan kalimat-kalimat panjang yang berbagi banyak kata.**

---

## 5.1.4 Mengapa model ini tidak cocok untuk korpus v7 — empat ketidakcocokan struktural

**(1) Granularitas state terlalu kasar untuk kalimat penuh.**
Korpus v7 berisi kalimat lengkap berbahasa Indonesia dengan durasi rata-rata ~215 frame (fitur 80 dimensi). Memodelkan satu kalimat utuh hanya dengan 5 state HMM memaksa setiap state merepresentasikan ~40 frame yang mencakup banyak fonem berbeda. Topologi ini dirancang untuk unit pendek (kata terisolasi/digit) pada paradigma 1990-an, bukan untuk kalimat naratif. Konsekuensinya, model kehilangan kemampuan membedakan urutan fonem yang menjadi pembeda antar-kalimat.

**(2) Asumsi independensi frame dari GMM mengabaikan konteks jangka panjang.**
GMM mengemisikan tiap frame secara independen bersyarat pada state. Bahasa Indonesia pada korpus ini memiliki banyak kalimat dengan leksikon dan struktur yang tumpang tindih ("...di kota palembang", "...mahasiswa..."), sehingga pembeda sesungguhnya terletak pada konteks panjang dan koartikulasi — justru aspek yang tidak ditangkap oleh emisi per-frame.

**(3) Pelatihan generatif memaksimalkan likelihood, bukan daya pisah antar-kelas.**
Setiap HMM dilatih terpisah untuk memaksimalkan p(x|template) pada datanya sendiri, tanpa kriteria diskriminatif antar-template. Tidak ada mekanisme yang secara eksplisit mendorong template benar mengungguli template pesaing. Pada ruang 209 kelas yang fonetiknya saling tumpang tindih, pelatihan generatif murni ini menghasilkan keputusan yang rapuh.

**(4) Skalabilitas yang buruk sebagai paradigma pengenalan.**
Pendekatan template tidak dapat menggeneralisasi ke kalimat di luar set tertutup, dan biaya inferensi tumbuh linear terhadap jumlah template (209 evaluasi likelihood per utterance, ~3 jam pelatihan CPU). Ini menutup jalan menuju pengenalan kosakata terbuka yang merupakan tujuan akhir paper.

---

## 5.1.5 Implikasi: motivasi menuju model yang lebih canggih

Kegagalan m08 bukan sekadar angka buruk — ia adalah **argumen metodologis** yang menstrukturkan keseluruhan progresi model dalam paper ini. Setiap kelemahan di atas memetakan langsung ke perbaikan arsitektur pada generasi model berikutnya:

| Kelemahan m08 (HMM-GMM) | Perbaikan yang dituntut | Diwujudkan oleh |
|---|---|---|
| Emisi per-frame generatif, tidak diskriminatif | Posterior akustik diskriminatif per frame | m09 DNN-HMM (hybrid, CTC) |
| Penyelarasan kaku, alignment eksternal | Penyelarasan ditangani kriteria CTC tanpa alignment manual | m09 / m10 |
| State kasar, tak menangkap konteks panjang | Pemodelan urutan & dependensi jarak jauh | m11 Vanilla Transformer (self-attention) |
| Representasi akustik tetap & dangkal | Representasi spektro-temporal kaya berbasis patch attention | **m12 ViT-modified-ID (Ratna 2026)** |
| Closed-vocabulary, tak menggeneralisasi | Dekoding kosakata terbuka tingkat sub-kata/karakter | m11–m14 (CTC/attention) |

Urutan ini mengikuti garis evolusi historis ASR — dari model generatif HMM-GMM (1990-an), ke hybrid neural-HMM (2010-an), lalu ke model berbasis attention murni — dan memuncak pada **arsitektur novel ViT-modified-ID** yang diajukan dalam paper ini. ViT-modified-ID mengatasi keempat ketidakcocokan sekaligus: ia memperlakukan representasi spektral sebagai urutan patch dan menggunakan self-attention untuk menangkap konteks global, dilatih secara diskriminatif terhadap target sub-kata, dan mendekode kosakata terbuka. Dengan demikian m08 berfungsi sebagai **titik referensi terendah (lower anchor)** yang membuat keunggulan model novel dapat diukur secara bermakna pada korpus yang sama.

---

## 5.1.6 Pernyataan keterbatasan untuk paper (versi jujur, menggantikan klaim lama)

> Sistem HMM-GMM dilaporkan sebagai baseline generatif klasik. WER-nya yang melampaui 1.0 **bukan** disebabkan oleh tutupnya kosakata — seluruh template uji terdapat dalam set pelatihan (cakupan 100%, batas bawah WER teoretis = 0) — melainkan oleh rendahnya daya pisah model akustik generatif berkapasitas rendah (5 state, 3 campuran) pada kalimat-kalimat panjang dengan leksikon yang tumpang tindih. Baseline ini sengaja dipertahankan tanpa penyetelan ulang untuk merepresentasikan paradigma era 1990-an secara setia dan untuk menyediakan titik referensi terendah yang memotivasi keluarga model diskriminatif dan berbasis attention pada paper ini.

---

## 5.1.7 Catatan reproduksibilitas

- Angka pada bagian ini diambil dari benchmark resmi test split (`reports/paper_benchmark/benchmark.md`, WER 1.1687 / CER 0.8980). Run pelatihan internal pada split validasi memberikan angka yang konsisten (WER 1.0255 / CER 0.7695), keduanya menegaskan kesimpulan yang sama.
- Cakupan template train/val/test diverifikasi langsung dari pickle korpus: 206/206 template uji ⊂ 209 template latih.
- Config: states=5, mixtures=3, iters=30, kovarians diagonal, seed=42; pelatihan CPU-only (hmmlearn 0.3.3), throughput ~6,6 utt/s.
- Model dipertahankan apa adanya (Jalur A); tidak ada perubahan kode pada `run_hmm_gmm`. Analisis bersifat naratif dan diagnostik, bukan modifikasi model.
