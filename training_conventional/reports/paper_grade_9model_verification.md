# Verifikasi PAPER-GRADE 9-Model — Akurasi & Kesiapan Run

**Tanggal:** 2026-05-30 | **Tag:** `[FAIRNESS-C 2026-05-29]`
**Scope:** Section "📖 SECTION KHUSUS — PAPER-GRADE FAIR COMPARISON (Data in Brief submission)" di RUN_GUIDE.md (baris 766–dst), berisi 9 model paper (P-1…P-9).

---

## 1. Temuan utama: SECTION PAPER-GRADE SUDAH BENAR sejak awal

Edit-edit fairness saya sebelumnya menyentuh **blok eksplorasi/smoke** (Terminal 11–13, Recipe A) yang TIDAK konsisten. **Section PAPER-GRADE (P-1…P-9) sudah memakai budget kanonik** dan tidak perlu diubah. Diverifikasi command-per-command terhadap protokol:

| Slot | Command PAPER-GRADE | Protokol | ✓ |
|---|---|---|:-:|
| m08 | `--hmm-iters 30 --hmm-states 5 --hmm-mixtures 3 --seed 42` | 30 EM/5/3 | ✓ |
| m09 | `--dnn-epochs 30 --dnn-hidden 512 --dnn-layers 4 --dnn-context 5 --dnn-batch-size 12000 --dnn-lr 1e-3 --seed 42` | 30 ep CTC | ✓ |
| m10 | iters 30/5/3 + dnn-epochs 30 … seed 42 | 30+30 | ✓ |
| m11 | `--epochs 30 --lr 5e-4 --num-layers 6 … --seed 42` | 30 ep, L6 | ✓ |
| m12 ★ | `--epochs 30 --lr 5e-4 --num-layers 6 --specaug --lambda-ctc 0.1 --scheduler plateau --seed 42` | **identik m11** | ✓ |
| m13 | `--epochs 30 --lr 3e-4 --seed 42` | 30 ep | ✓ |
| m07 | `--epochs 30 --hidden-size 512 --num-layers 5 --lr 3e-4 --seed 42` | 30 ep | ✓ |
| m06 | `--epochs 30 --hidden-size 256 --num-layers 6 --lr 3e-4 --seed 42` | 30 ep | ✓ |
| m02b | `--epochs 5 --lr 1e-5 --warmup-steps 500 --seed 42` | 5 ep FT | ✓ |

**Prinsip atribusi-arsitektur terpenuhi** (m11 ≡ m12 kecuali arsitektur). **Pagar anti-asimetri terpenuhi** (tak ada model lemah dapat lebih banyak / model kuat ditahan).

## 2. Verifikasi kesiapan run (9 entry point)

- Semua 9 `train.py` **ada** dan **compile OK** (`py_compile`).
- Flag tiap command **diterima** trainer di belakangnya (diverifikasi argparse):
  - m08/m09/m10 → `pkl_hmm_trainer.py` ✓
  - m13 → `pkl_cnn_ctc_trainer.py` (epochs/batch-size/lr/seed) ✓
  - m06/m07 → `from_scratch_trainer.py` (epochs/batch-size/grad-accum/hidden-size/num-layers/lr/seed) ✓
  - m02b → `whisper_trainer.py` (wrapper inject `--model-id openai/whisper-medium`) ✓
  - m11/m12 → root `train_model_vanilla.py` / `train_model_vit.py` di `ASR_ROOT` (epochs/lr/d-model/nhead/num-layers/ff/dropout/input-dim/specaug/amp/seed; m12 +`--lambda-ctc`+`--scheduler{plateau}`) ✓
- **Smoke test nyata m08** (canonical flags, env `torch-gpu`, 1500 train/10 val): pipeline jalan end-to-end → `config.json`+`history.json`+`log.txt`+`report.md` terbuat; perilaku sesuai diagnosis (template classifier → WER>1). Full run pakai `--max-train-samples 0` (71.792 utt / 209 template).

## 3. Perbaikan yang dilakukan (ciri khas `[FAIRNESS-C]` / `[VERIFIED]`)

### 3a. Koreksi akurasi dokumentasi: "patience 10" → mekanisme sebenarnya
Klaim lama "early-stopping patience 10 untuk semua" **TIDAK sesuai kode**. Mekanisme aktual (diverifikasi):
- m06/m07 (`from_scratch_trainer`) & m13 (`pkl_cnn_ctc_trainer`): latih penuh 30 epoch, simpan **best-on-val** via `BestCheckpointTracker(metric="wer", lower_is_better=True)` — **tanpa early-stop**.
- m11/m12 (root scripts): early-stop **patience 12**.
- m02b (HF): `load_best_model_at_end=True, metric_for_best_model="wer"`.
- **Penyetara keadilan sebenarnya = best-on-validation untuk SEMUA model**, bukan patience seragam.

Dikoreksi di: `RUN_GUIDE.md` (P7 §4.2), `fairness_protocol_C_FINAL.md`, `hyperparameter_fairness_decision.md`, `FAIR_COMPARISON_PROTOCOL.md`. Residual "patience 10" → **0** (diverifikasi `grep`).

### 3b. Guard defensif m08 (robustness)
Trainer dulu crash `IndexError` bila 0 template lolos pruning (hanya pada subsample mini). Ditambah guard `SystemExit` pesan jelas di `run_hmm_gmm` setelah pruning. Tidak memengaruhi run paper (full data selalu >threshold), hanya mencegah crash membingungkan saat debug.

## 4. Yang TIDAK diubah (sengaja)
- 9 command PAPER-GRADE: sudah benar, tidak disentuh.
- Hyperparameter m06/m07/m11/m12/m02b: sudah sesuai protokol & sudah konvergen baik.
- Algoritma trainer, topologi HMM, decoding greedy no-LM.

## 5. Kesimpulan
Section PAPER-GRADE 9-model **akurat & siap run**, sesuai prinsip atribusi-arsitektur dan pagar anti-asimetri. Yang diperbaiki: (a) koreksi klaim early-stopping agar dokumen cocok dengan kode (penting untuk reviewer yang cek code-vs-paper), (b) guard defensif m08. Semua diverifikasi via compile + argparse + smoke run nyata.
