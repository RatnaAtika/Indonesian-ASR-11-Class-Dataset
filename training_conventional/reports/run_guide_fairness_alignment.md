# Verifikasi Konsistensi Run HMM-Family vs Protokol Fairness-C

**Tanggal:** 2026-05-29 | **Tag:** `[FAIRNESS-C 2026-05-29]`
**Pertanyaan:** Apakah kode/command lama di RUN_GUIDE ikut berubah atau sama saja? Pastikan tidak ada perbedaan saat run ulang m08/m09/m10.

---

## Temuan: RUN_GUIDE.md SEBELUMNYA TIDAK KONSISTEN (sumber bug fairness)

Ditemukan **3 varian command m08 berbeda** di RUN_GUIDE lama → hasil run berbeda tergantung blok yang disalin:

| Lokasi | Command lama (TIDAK fair) |
|---|---|
| Contoh re-run (l.253) | `--hmm-iters 25` lalu `--hmm-iters 50` |
| Recipe A (l.447) | `--hmm-iters 50 --hmm-states 7 --hmm-mixtures 6` ← **boost baseline lemah** |
| Terminal 11 (l.602) | `--hmm-states 5 --hmm-mixtures 3 --hmm-iters 25` |
| Tabel param (l.386) | "naikkan ke 25–50 / 5–9 / 3–8 ★ TINGKATKAN INI" ← **melanggar anti-asimetri** |

Saran lama "naikkan states/mixtures/iters untuk akurasi lebih tinggi" persis kasus **menganakemaskan baseline lemah** yang dilarang pagar anti-asimetri.

---

## Yang DIUBAH agar semua run identik & fair

### 1. RUN_GUIDE.md — semua command HMM disamakan ke budget kanonik
- m08: `--hmm-iters 30 --hmm-states 5 --hmm-mixtures 3 --seed 42` (di SEMUA blok)
- m09: `--dnn-epochs 30 --dnn-hidden 512 --dnn-layers 4 --dnn-context 5 --dnn-batch-size 12000 --dnn-lr 1e-3 --seed 42`
- m10: `--hmm-iters 30 --hmm-states 5 --hmm-mixtures 3` + DNN identik m09
- Saran "TINGKATKAN INI / naikkan ke 7–9, 4–8" → diganti "**kunci, JANGAN naikkan (anti-asimetri)**".

### 2. Wrapper `train.py` — default disamakan ke budget kanonik
Sebelumnya default wrapper ≠ protokol (mis. m08 `--hmm-mixtures 2`, m09/m10 `--dnn-epochs 5`).
Sekarang **bare call pun fair**:

| File | Default lama | Default baru `[FAIRNESS-C]` |
|---|---|---|
| `m08_hmm_gmm/train.py` | states5 mix2 | **states5 mix3 iters30 seed42** |
| `m09_dnn_hmm/train.py` | dnn-epochs5 | **dnn-epochs30 batch12000 lr1e-3 seed42** |
| `m10_gmm_hmm_dnn/train.py` | mix2 dnn-epochs5 | **mix3 iters30 + dnn-epochs30 batch12000 lr1e-3 seed42** |

> Catatan teknis: wrapper memakai `+ sys.argv[1:]`, jadi flag eksplisit di command **menimpa** default (argparse pakai nilai terakhir). Artinya command RUN_GUIDE kanonik sudah benar bahkan sebelum default diperbaiki; perbaikan default menghapus satu-satunya footgun bila dijalankan tanpa flag.

---

## Verifikasi (bukti, bukan asumsi)
- `py_compile` ketiga wrapper + `pkl_hmm_trainer.py` → **COMPILE OK**.
- Dump cmd ketiga wrapper → semua emit budget kanonik identik (lihat dump di sesi).
- `rg` non-canonical command tersisa di RUN_GUIDE → **NONE**.

## Yang TIDAK diubah (sengaja, demi fairness)
- Logika trainer (`pkl_hmm_trainer.py`): tidak disentuh — hanya budget yang diseragamkan, bukan algoritma.
- m06/m07/m11/m12/Whisper: command sudah sesuai protokol, tidak diubah.
- Topologi HMM (left-right transmat fixed): tetap.

## Untuk run ulang m08/m09/m10 (fair, tinggal salin)
```bash
# m08 HMM-GMM
python3 training_conventional/m08_hmm_gmm/train.py \
  --run-dir training_conventional/m08_hmm_gmm/runs/run_paper_$(date +%Y%m%d_%H%M%S) \
  --hmm-iters 30 --hmm-states 5 --hmm-mixtures 3 --seed 42

# m09 DNN-HMM
python3 training_conventional/m09_dnn_hmm/train.py \
  --run-dir training_conventional/m09_dnn_hmm/runs/run_paper_$(date +%Y%m%d_%H%M%S) \
  --dnn-epochs 30 --dnn-hidden 512 --dnn-layers 4 --dnn-context 5 \
  --dnn-batch-size 12000 --dnn-lr 1e-3 --seed 42

# m10 GMM-HMM-DNN
python3 training_conventional/m10_gmm_hmm_dnn/train.py \
  --run-dir training_conventional/m10_gmm_hmm_dnn/runs/run_paper_$(date +%Y%m%d_%H%M%S) \
  --hmm-iters 30 --hmm-states 5 --hmm-mixtures 3 \
  --dnn-hidden 512 --dnn-layers 4 --dnn-context 5 --dnn-epochs 30 \
  --dnn-batch-size 12000 --dnn-lr 1e-3 --seed 42
```
> Jalankan di **terminal terpisah** (bukan pi-cli). Budget ini sama untuk model kuat & lemah → fairness terjaga.
