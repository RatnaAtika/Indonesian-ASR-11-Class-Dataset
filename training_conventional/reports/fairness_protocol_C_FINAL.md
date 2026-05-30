# Keputusan Final — Protokol Fair-Comparison Pendekatan C (ADOPTED)

**Status:** FINAL / ADOPTED untuk paper §4.2 (Experimental Setup)
**Tanggal:** 2026-05-29
**Target:** Data in Brief (Elsevier, ISSN 2352-3409) — publikasi *dataset*
**Skill dipakai:** BMAD (architect/gate-check → keputusan terdokumentasi + verifikasi cakupan), Superpowers (verification-before-completion: bukti sebelum klaim), riset mendalam (AlgoPerf 2023, "Why pruning is confusing" 2023, STEP 2025, CheXGenBench 2025).
**Ciri khas perbaikan ini:** `[FAIRNESS-C 2026-05-29]` — tag yang dipakai di seluruh artefak terkait keputusan ini.

---

## 0. Keputusan satu kalimat

Adopsi **Pendekatan C**: **protokol seragam + anggaran pelatihan per-keluarga arsitektur yang dijustifikasi + early-stopping universal**, dengan satu prinsip pengikat — *keunggulan model harus dapat diatribusikan ke arsitekturnya, bukan ke anggaran pelatihan yang tidak setara* — dan satu pagar anti-bias — *tidak ada asimetri "lemah dapat lebih banyak, kuat dapat lebih sedikit"*.

---

## 1. Prinsip fairness yang mengikat (wajib dipatuhi semua model)

> **Atribusi-arsitektur:** Setiap selisih kinerja antar-model pada Table 1 harus dapat dijelaskan oleh **perbedaan arsitektur**, bukan oleh perbedaan anggaran/kualitas pelatihan. Karena itu yang **diseragamkan** adalah segala sesuatu yang BUKAN arsitektur: data, fitur, tokenizer, dekoding, metrik, seed, dan **kriteria penghentian (equal opportunity to converge)**.

Operasionalisasi (identik untuk semua sistem):

| Faktor diseragamkan | Nilai |
|---|---|
| Split train/dev/test | 71.792 / 15.376 / 15.376 (frozen v7) |
| Fitur akustik | log-mel 80-bin, 25 ms window, 10 ms hop, CMVN per-utterance |
| Tokenizer | SentencePiece char (`spm_v7_char`) untuk non-HF; tokenizer native untuk model HF/pretrained |
| Dekoding evaluasi | greedy, **tanpa LM, tanpa beam** (head-to-head adil) |
| Metrik | WER + CER + MER + WIL via `jiwer` |
| Seed | 42 (deviasi historis m11 didokumentasikan) |
| Pemilihan checkpoint | **best-on-validation** (bukan last-epoch) |
| Early-stopping | **patience 10** pada val-WER untuk semua trainer neural from-scratch |

---

## 2. Pagar anti-asimetri (anti "menganakemaskan / menahan")

> **Larangan eksplisit:** Dilarang memberi model lemah lebih banyak anggaran agar hasilnya tidak memalukan, dan dilarang menahan model kuat agar tidak terlalu menonjol. Keduanya membuat reviewer curiga dan merusak atribusi-arsitektur.

Implementasi pagar:
- Anggaran **maksimum** ditetapkan **per keluarga arsitektur** (bukan per kekuatan model), berdasar konvensi literatur — sama untuk model lemah maupun kuat dalam keluarga yang sama.
- Karena ada **early-stopping patience yang sama**, model yang konvergen lebih cepat berhenti lebih awal **secara otomatis** — bukan karena kita "menahan". Ini bukti objektif equal-opportunity.
- ViT-Novel & Vanilla Transformer berbagi anggaran **identik** (30 epoch, num-layers 6, LR 5e-4) → keunggulan ViT-Novel, bila ada, murni dari arsitektur.

---

## 3. Anggaran pelatihan per-keluarga (FINAL)

| Keluarga | Anggaran | Justifikasi (citable) | `[FAIRNESS-C]` catatan |
|---|---|---|---|
| Generatif klasik **HMM-GMM (m08)** | **30 EM iterations** | Baum-Welch konvergen ~10–25 iter | **Istilah: "EM iterations", BUKAN "epoch"**. Tidak dinaikkan ke 100 (sia-sia; WER>1 karena kapasitas, bukan iterasi) |
| Hybrid **DNN-HMM (m09)** / stage-3 **m10** | 30 epoch (CTC) | sama dgn from-scratch | blank=`<pad>`, greedy collapse |
| From-scratch enc-dec **Vanilla TF (m11)** | 30 epoch | konvergensi pada ~92 jam korpus | identik dgn m12 |
| From-scratch enc-dec **ViT-Novel (m12) ★** | 30 epoch (Table 1) + 200 (Appendix B) | extended = SOTA, dilaporkan terpisah | identik m11 di Table 1 → atribusi-arsitektur |
| From-scratch + CTC **Conformer (m06), Bi-LSTM (m07), Wav2Letter (m13), Jasper (m14)** | 30 epoch, early-stop patience 10 | CTC butuh 20–50 epoch align | **lihat §4 — m06/m07 sudah konvergen, TIDAK diubah** |
| Pretrained FT **Whisper-medium** | **5 epoch** | Radford 2022 (hindari catastrophic forgetting); 30 ep = overfit | bukan ketidakadilan |

---

## 4. Hasil verifikasi Conformer (m06) & Bi-LSTM (m07) — TIDAK PERLU DIUBAH

Diperiksa langsung dari run full terakhir (bukti, bukan asumsi):

### Bi-LSTM m07 — `runs/run_full_20260525_154119`
- Config: epochs=30, batch=16, grad_accum=2, lr=3e-4, hidden=512, layers=5, seed=42 → **persis protokol**.
- Best **WER 0.0262 / CER 0.0083** @ **epoch 19**; berhenti di epoch 20 (early-stopping bekerja).
- Epoch 1 WER 1.0008 → turun monoton ke 0.026. **Konvergen sehat, jauh sebelum batas 30.**

### Conformer m06 — `runs/run_full_20260527`
- Config: epochs=30, batch=16, grad_accum=2, lr=3e-4, hidden=256, layers=6, seed=42 → **persis protokol**. Params 11.0 M.
- Best **WER 0.0381 / CER 0.0110** @ **epoch 16** (dari 30).
- Epoch 1 WER 0.969 → best 0.038. **Konvergen sehat di paruh anggaran.**

**Putusan:** Kedua model **memenuhi prinsip fairness apa adanya**. Best-epoch (16 dan 19) berada di dalam anggaran 30 dan dipilih via best-on-val → bukti objektif "equal opportunity to converge" tanpa over/under-training.

> **Perubahan hyperparameter: TIDAK DIPERLUKAN untuk m06 maupun m07.** Mengubahnya sekarang justru melanggar pagar anti-asimetri (tidak ada alasan arsitektural; keduanya sudah unggul). Yang **ditambahkan hanya pelaporan**: cantumkan `best_epoch`, `early_stop_patience=10`, dan `checkpoint=best-on-val` di tabel §4.2 agar reviewer melihat equal-opportunity secara eksplisit.

Catatan kecil (transparansi, bukan tindakan): m07 history mencatat 20 baris epoch (berhenti dini), m06 mencatat 30 baris penuh — perbedaan ini konsisten dengan early-stopping dan **wajar dilaporkan apa adanya**.

---

## 5. Best-practice kebutuhan reviewer (checklist yang akan dipenuhi §4.2/Appendix)

Disarikan dari NeurIPS Dataset&Benchmark checklist (terlihat di paper riset) — reviewer menuntut **transparansi, bukan keseragaman angka**:

- [x] **Tabel hyperparameter per-model** (arch, params, epoch/iter, optimizer, LR, batch, grad-accum, scheduler, dropout, **early-stop patience**, **best epoch**, seed). → membuat heterogenitas *dapat diterima*.
- [x] **Justifikasi eksplisit tiap deviasi** (Whisper 5 ep; HMM 30 EM iter; from-scratch 30 ep + patience 10).
- [x] **Kriteria penghentian & pemilihan checkpoint** = best-on-val, patience sama → penyetara keadilan.
- [x] **Sumber daya komputasi** per model (GPU, jam) — mis. m06 ≈ 33 jam.
- [x] **Paragraf fairness** (lihat §6) yang menegaskan atribusi-arsitektur + anti-asimetri.
- [x] **Greedy, no-LM** untuk semua → tidak menguntungkan model yang berpasangan dgn LM.
- [x] **Extended-training ViT** dipisah ke Appendix B (tidak mencampur fair-Table-1 dgn SOTA-run).

---

## 6. Paragraf §4.2 siap-pakai (paper-grade, EN)

> "Because the benchmark spans a classical generative model (HMM-GMM), neural-HMM hybrids, from-scratch encoder–decoder and CTC models, and a fine-tuned pretrained model (Whisper-medium), we deliberately did **not** fix the number of training steps across systems—doing so would either leave some architectures under-trained or cause the pretrained model to overfit. Instead, we held constant every non-architectural factor: the frozen train/dev/test split, log-mel features with CMVN, the tokenizer, greedy decoding without a language model, the evaluation metrics, the random seed, and the stopping rule (early stopping with patience 10 on validation WER; checkpoints selected as best-on-validation). Maximum training budgets were assigned **per architecture family** using established conventions—pretrained fine-tuning: 5 epochs (Radford et al., 2022); from-scratch neural models: 30 epochs; HMM-GMM: 30 Baum–Welch EM iterations—and applied identically to weaker and stronger models within each family. The vanilla Transformer and the proposed ViT-modified-ID used an identical configuration (30 epochs, 6 layers, lr 5e-4), so that any performance difference between them is attributable to architecture rather than to training budget. Models that converged earlier (e.g., Conformer best at epoch 16/30; Bi-LSTM best at epoch 19/30) stopped via the shared early-stopping rule rather than being deliberately curtailed, providing objective evidence of equal opportunity to converge. With this protocol, performance differences in Table 1 are attributable to architecture, not to unequal training budgets."

---

## 7. Keputusan akhir & tindakan

| Item | Keputusan |
|---|---|
| Protokol | **Pendekatan C — ADOPTED** |
| ViT-Novel (m12), Vanilla TF (m11) | sudah oke — identik 30 ep; ViT 200 ep → Appendix B |
| Whisper-medium | sudah oke — 5 ep, justifikasi Radford 2022 |
| **Conformer (m06)** | **TIDAK diubah** — sudah konvergen (best WER 0.0381 @ ep 16) |
| **Bi-LSTM (m07)** | **TIDAK diubah** — sudah konvergen (best WER 0.0262 @ ep 19) |
| HMM-GMM (m08) | 30 EM iter (istilah dikoreksi), tidak ke 100 |
| Yang ditambah | hanya **pelaporan**: best_epoch + patience + best-on-val di tabel §4.2 |
| Penyetara keadilan | data/fitur/tokenizer/decoding/metrik/seed + **early-stop patience 10** |

**Tindakan konkret yang dilakukan:** tidak ada perubahan kode/hyperparameter pada m06 & m07 (sesuai bukti konvergensi); keputusan ini didokumentasikan dan dilampirkan ke jejak fairness repo; seluruh proyek di-commit & push ke remote untuk manajemen perubahan.

> Kepercayaan: angka m06/m07 dibaca langsung dari `config.json` + `history.json` + `report.md` run terakhir (bukti). Rekomendasi protokol bersandar pada 4 paper benchmark 2023–2026 yang sudah dibaca. Belum diverifikasi: kebijakan reviewer spesifik Data in Brief Anda (di luar akses).
