# Audit Mendalam Pipeline PAPER-GRADE (training → test → aggregate → paper artifacts)

**Tanggal:** 2026-05-30 | **Tag:** `[FAIRNESS-C/PIPELINE 2026-05-30]`
**Peran:** ASR researcher + reviewer paper expert. **Target:** Data in Brief, 9 model.
**Metode:** scout recon (kontrak schema), verifikasi langsung, **2 run end-to-end nyata** (m08 test→aggregate), debugging mendalam, fix minimal.

---

## Ringkasan eksekutif

Rantai `test.py → test_paper.json → aggregate_paper_test_results.py → benchmark.{json,md,csv,tex}` **konsisten & terverifikasi jalan end-to-end**. Schema seragam (satu `write_test_results` dipakai semua writer). Ditemukan & diperbaiki **2 bug nyata yang akan merusak paper** dan **2 perbaikan integritas**, semua minimal.

---

## A. Yang terverifikasi BENAR (bukti)

1. **9 test.py + 9 train.py ada & compile OK**; semua flag PAPER-GRADE diterima trainer di belakangnya (argparse diverifikasi sesi sebelumnya).
2. **Schema JSON seragam**: 21 key top-level + `metrics{wer,cer,mer,wil,ser}`; semua key yang dibaca aggregator diproduksi writer. Tidak ada key mismatch. (diverifikasi pada `test_paper.json` m08 nyata)
3. **E2E nyata**: `m08 test.py` → auto-detect `best.pkl` → inference → tulis JSON lengkap (config/training_meta/test_environment ada) → `aggregate_paper_test_results.py` → benchmark.{json,md,csv,tex}+sample_predictions+training_summary. Aggregator exit 1 bila <9 model (completeness gate, reviewer-detectable). ✓
4. **HMM family checkpoint** (`pkl_hmm_test.py`) sengaja pakai locate `.pkl` sendiri (bukan `find_best_checkpoint`) — benar, karena `best.pt` (torch) tak boleh di-pickle-load.
5. **Root CSV m11/m12**: `test_model_vit.py`→`results_vit.csv` kolom `hyp,ref,cer,wer,text`; `test_model_vanilla.py`→`results_vanilla.csv` kolom sama. m11/m12 test.py auto-detect `hyp`/`ref` → **match** (TIDAK ada risiko WER=1.0 senyap). `audio` kosong (tak ada kolom fname) — non-breaking.
6. **Trainer→test wiring DNN**: `pkl_hmm_trainer` menyimpan `best.pkl`+`best_wer*_final.pkl` untuk m08/m09/m10; `test_dnn_hmm` rekonstruksi `FrameDNN` dari `artifact["model_state"]`+`args`. Routing `gmm_hmm_dnn→test_dnn_hmm` benar.

---

## B. BUG NYATA yang diperbaiki (akan merusak paper bila dibiarkan)

### B1. m10 GMM-HMM-DNN: artifact `.pkl` TIDAK menyimpan `model_state` → test pakai DNN random-init → WER≈1 (CRITICAL)
- Akar: builder artifact `gmm_hmm_dnn` di `pkl_hmm_trainer.main()` hanya simpan metrik, tanpa `model_state`. `test_dnn_hmm` punya guard `if artifact.get("model_state")` → DNN tetap acak → m10 di paper terlihat rusak/terburuk palsu.
- **Fix:** tambah `"model_state": _best_dnn_state()` ke artifact m10.

### B2. m09/m10: artifact menyimpan bobot DNN **epoch terakhir**, bukan **best-on-val** → understate (FAIRNESS)
- Akar: artifact pakai `result["model"].state_dict()` = model di akhir training, padahal `BestCheckpointTracker` menyimpan best-epoch ke `checkpoints/best.pt`. Melanggar prinsip "best-on-val untuk semua".
- **Fix:** helper `_best_dnn_state()` memuat `model_state` dari `best.pt` (best-epoch) lebih dulu, fallback ke last-epoch. Dipakai m09 & m10.

> Konsekuensi: **m09/m10 WAJIB di-run ulang** dengan trainer terbaru agar artifact testable & best-on-val. Run lama m09/m10 artifact-nya cacat (m10 random-init).

---

## C. Perbaikan integritas (proteksi reviewer)

### C1. `find_best_checkpoint` Strategy-4 sekarang history-aware
- Akar: bila hanya ada `epoch_*.pt` (tanpa `best.pt`, mis. run lama/terinterupsi), dulu memilih epoch **TERAKHIR**, bukan **best-WER**. Bukti: run lama m06 punya 30 epoch ckpt tapi tanpa `best.pt`; best WER di epoch 16 (0.0381), bukan epoch 30 (0.064).
- **Fix:** Strategy-4 baca `history.json`, pilih `epoch_NNN.pt` dengan val-WER terendah. **Diuji:** m06 kini pilih `epoch_016.pt` (benar), m07 pilih `epoch_020.pt` (satu-satunya yang tersimpan).
- Catatan: run paper baru selalu punya `best.pt` (tracker aktif di `from_scratch_trainer`), jadi ini jaring pengaman untuk legacy/interupsi.

### C2. Aggregator otoritatif untuk label `family` + `model_id`
- Akar: writer m12 set `family="ViT-modified-ID (Ratna 2026, unpublished)"` ≠ tabel kanonik "ViT-modified-ID (Ratna 2026)". Aggregator dulu memakai string writer → label Table 1 tidak konsisten ("unpublished" bocor ke paper).
- **Fix:** aggregator meng-override `r["family"]` & `r["model_id"]` dengan nilai kanonik `PAPER_MODELS`. **Diuji:** benchmark m08 kini "HMM-GMM (classical)" (kanonik).

---

## D. Catatan kelengkapan log untuk paper
- Tiap run penuh punya: `config.json, meta.json (env snapshot), history.json (per-epoch WER/CER/loss/acc/lr/gpu/throughput), log.txt (PRED/LABEL), predictions/, checkpoints/`. Diverifikasi pada m08/m06/m07. → cukup untuk §4.2/§4.3 + Appendix + matriks 9-model.
- **Run lama m06/m07** = `run_full_*` (bukan `run_paper_*`), tidak punya `best.pt`. Aggregator hanya scan `run_paper_*`, jadi run lama tak mencemari paper; **run ulang sebagai `run_paper_*`** akan menulis `best.pt` benar.

---

## E. Tindakan WAJIB sebelum submit (untuk user)
1. **Run ulang m08/m09/m10** sebagai `run_paper_*` (trainer terbaru) — terutama m10 (artifact lama cacat). Command kanonik di RUN_GUIDE P-1/P-2/P-3.
2. Run ulang m06/m07/m11/m12/m13/m02b sebagai `run_paper_*` bila belum (best.pt akan tersimpan).
3. `test.py` tiap model → `aggregate_paper_test_results.py` → cek `n_paper_models_present == 9` di benchmark.json.
4. `replot_all.py --style data_in_brief` untuk figur.

## F. Yang TIDAK diubah (sengaja)
- 9 command PAPER-GRADE, hyperparameter, algoritma decoding, schema JSON, topologi HMM. Hanya bug artifact + integritas checkpoint/label yang disentuh.

> Verifikasi: 16 file compile OK; 2 run E2E nyata (m08 test+aggregate) sukses; fix Strategy-4 & family diuji pada data nyata; benchmark asli dipulihkan (WER m08 1.1687) & artifact smoke dibersihkan. Belum diverifikasi (butuh GPU + run penuh ~jam): m09/m10/m06/m07/m11/m12/m02b end-to-end test nyata — hanya kontrak + smoke yang divalidasi di sini.
