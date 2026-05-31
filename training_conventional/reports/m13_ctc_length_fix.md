# Fix m13 Wav2Letter CTC — Prediksi Terlalu Panjang (Acc=0, WER/CER>1)

**Tanggal:** 2026-05-31 | **Tag:** `[FIX-CTC-LEN 2026-05-31]`
**Model terdampak:** m13 Wav2Letter (utama), m14 Jasper, dan konsisten juga m06 Conformer & m07 Bi-LSTM (semua keluarga CTC). Fokus 9-model paper.

---

## Gejala (dari log user)
- Epoch 1–2: **Train/Val Accuracy 0.000000**, **WER 1.04 / CER 1.03** (di atas 100%).
- Prediksi **lebih panjang dari label** dengan ekor sampah, mis:
  `PRED: Saya membutuhkan rekomendasi tempat wisata di kota Palembang|ankanudi d t m r h merianhiduptantuku mer labnya?`
  padahal model sebenarnya **sudah benar di awal** (prefix tepat).

## Akar masalah (root cause)
`ctc_greedy_decode()` men-decode **seluruh sumbu waktu yang ter-pad** (B, T, V), bukan hanya frame valid per-sample. Frame padding (nol) tetap melewati Conv/BatchNorm dan **memunculkan token non-blank palsu** di ekor → hipotesis over-panjang → edit distance > panjang referensi → CER/WER > 1 dan `acc = max(0, 1-CER) = 0`.

`new_lens` (jumlah frame output valid) **dihitung tapi tidak dipakai** saat decode — padahal CTC loss sudah memakainya. Jadi loss benar, tapi decode tidak konsisten.

## Fix (minimal)
`ctc_greedy_decode(logits, blank, lengths=new_lens)` → truncate tiap sequence ke `lengths[i]` **sebelum** collapse. Diterapkan di:
- `training_conventional/common/pkl_cnn_ctc_trainer.py` (eval + train-acc proxy) — m13/m14
- `training_conventional/common/pkl_cnn_ctc_test.py` — m13/m14 test
- `training/common/from_scratch_trainer.py` (`ctc_decode`, eval + train-acc) — m06/m07 (konsistensi)
- `training/common/from_scratch_test.py` — m06/m07 test

`new_lens` terverifikasi akurat (≤ frame output aktual, undercount ≤1 → harmless): T=215→new_lens=108=out_frames.

## Bukti (smoke 2-epoch, 3000 train / 300 val, di torch-gpu)
| | Train Acc (ep1) | CER (ep1) | WER (ep1) | CER (ep2) | ekor sampah? |
|---|---|---|---|---|---|
| **Sebelum** (log user) | 0.000 | 1.025 | 1.039 | — | YA |
| **Sesudah** (fix) | **0.300** | **0.709** | 0.956 | **0.597** | TIDAK |

- Prediksi bersih: `PRED: Saya membutuhkanan tempat wrensata dii Palembang.` (len_ratio 0.77–0.89, tidak lagi >1).
- **Test runner E2E** pada checkpoint smoke: WER 0.8536 / CER 0.5993, JSON `test_paper.json` lengkap & valid (5 metrik, model_id `m13-wav2letter`).
- Sisa ketidaksempurnaan = underfitting 2-epoch saja; mekanisme decode sudah benar. Run penuh 30-epoch/71k akan konvergen rendah seperti m06/m07.

## Catatan untuk run paper
- **Command P-6 RUN_GUIDE TIDAK berubah** (hanya internal decode yang diperbaiki). Catatan fix ditambahkan di RUN_GUIDE P-6.
- Run m13 `run_paper_20260531` yang ter-log (terinterupsi) dibuat **SEBELUM** fix → history-nya masih cacat. **Run ulang m13** dengan kode terbaru untuk hasil paper.
- m06/m07 yang sudah baik (WER 0.038/0.026) tidak terdampak negatif — fix hanya membuang frame pad, konsisten dengan CTC loss.

## Verifikasi
4 file compile OK; smoke train + test E2E nyata membuktikan ekor hilang & metrik turun normal; tidak ada perubahan algoritma/command, hanya decode length-aware.
