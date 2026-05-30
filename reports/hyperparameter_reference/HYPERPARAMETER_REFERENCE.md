# Hyperparameter Reference & Tuning Recipes — 14 ASR Models on Indonesian v7

**Generated**: 2026-05-24
**Scope**: paper Section 4.2 (Training Setup) + Appendix B (Reproducibility & Tuning Notes)
**Owner role**: Senior ML Engineer / Paper Author
**Source files**:
- `training/common/whisper_trainer.py`, `wav2vec2_trainer.py`, `from_scratch_trainer.py`
- `training_conventional/common/pkl_cnn_ctc_trainer.py`, `pkl_hmm_trainer.py`
- Project root: `train_model_vanilla.py`, `train_model_vit.py` (m11/m12)
- Companion docs: `RUN_GUIDE.md`, `REPLAY_GUIDE.md`

> **Tujuan dokumen ini**: ringkasan single-source-of-truth untuk seluruh
> hyperparameter dan recipe tuning, supaya update laporan paper / re-tuning
> di kemudian hari tinggal baca file ini tanpa scroll dokumentasi panjang.

---

## 1. Hyperparameter Concept per Family

Setiap arsitektur ASR punya konsep "training" yang berbeda. Tabel ini meringkas
**flag mana yang menambah training duration** vs **flag mana yang ubah model
capacity**.

| Family | Flag yang menambah training | Flag yang ubah model size |
|--------|------------------------------|----------------------------|
| **Whisper / wav2vec2 / MMS** (m01–m05) | `--epochs N` | `--batch-size`, `--lr`, `--gradient-checkpointing` |
| **Conformer / Bi-LSTM / CNN** (m06, m07, m13, m14) | `--epochs N` | `--hidden-size`, `--num-layers`, `--dropout` |
| **Vanilla TF + ViT-modified-ID** (m11, m12) | `--epochs N` | `--d-model`, `--num-layers`, `--ff`, `--nhead` |
| **m08 HMM-GMM** | `--hmm-iters N` ⭐ | `--hmm-states`, `--hmm-mixtures`, `--cov-type` |
| **m09 DNN-HMM** | `--dnn-epochs N` | `--dnn-hidden`, `--dnn-layers`, `--dnn-context` |
| **m10 GMM-HMM-DNN** | `--hmm-iters` + `--dnn-epochs` | semua flag HMM + DNN |

### Catatan penting
1. **m08 HMM-GMM tidak punya konsep "epoch" konvensional.** Algoritma training
   adalah Baum-Welch EM (Expectation-Maximization) — satu round training dengan
   N iterasi internal. Log selalu menampilkan "Epoch 1/1"; yang sebenarnya
   bekerja adalah `--hmm-iters` (default 10).
2. **m11 (Vanilla TF) dan m12 (ViT-modified-ID ★)** adalah wrapper ke skrip root
   (`train_model_vanilla.py`, `train_model_vit.py`). Flag yang tidak diberikan
   user akan diisi default oleh wrapper; flag yang diberikan akan **override**
   default.
3. **HF Trainer-based (m01–m05)** auto-resume dari checkpoint terakhir jika
   `--run-dir` sama digunakan ulang. From-scratch (m06, m07, m13, m14) save
   `epoch_NNN.pt` per epoch dan butuh manual load untuk resume.
4. **Sub-sampling** (`--max-train-samples`, `--max-val-samples`) tersedia di
   semua trainer — set ke 0 untuk full data (default behavior pada flag
   tidak di-pass).

---

## 2. Tiga Recipe Tuning yang Sudah Disiapkan

Tabel high-level — detail command per-model di `RUN_GUIDE.md` § "3 Recipe Tuning":

| Recipe | Tujuan | Trade-off |
|--------|--------|-----------|
| **A: Lebih akurat** | Akurasi paper-grade (full data + epoch besar + model besar) | Lebih lambat, RAM/VRAM lebih |
| **B: Lebih cepat** | Smoke / debug (200 sample / 1 ep) | WER tinggi, tapi pipeline OK |
| **C: VRAM-constrained** | RTX 4060 8 GB (`--batch-size 2 --grad-accum 8 --gradient-checkpointing`) | ~30% lebih lambat |

### 2.1 Kapan pakai mana

- **Recipe A**: untuk run final yang masuk paper. Gunakan setelah hyperparameter
  sudah dipilih + dataset full sudah build.
- **Recipe B**: untuk verifikasi pipeline OK setelah edit kode atau mengganti
  trainer. Smoke run cuma 1–2 menit per model.
- **Recipe C**: jika OOM di laptop. Kurangi `--batch-size` ke 2, kompensasi
  dengan `--grad-accum 8` (effective batch tetap 16). Tambah
  `--gradient-checkpointing` untuk Whisper / wav2vec2 / MMS.

### 2.2 Recipe A copy-paste lengkap (semua 14 model — paper-grade)

#### Modern (`training/`)
```bash
# m01 Whisper-tiny FT
python3 training/m01_whisper_tiny/train.py \
  --run-dir training/m01_whisper_tiny/runs/run_full_$(date +%Y%m%d) \
  --epochs 5 --batch-size 16 --grad-accum 1 --lr 5e-6 --warmup-steps 500

# m02 Whisper-small FT ★ PRIMARY
python3 training/m02_whisper_small/train.py \
  --run-dir training/m02_whisper_small/runs/run_full_$(date +%Y%m%d) \
  --epochs 3 --batch-size 4 --grad-accum 4 --lr 1e-5 --warmup-steps 500

# m03 wav2vec2-XLS-R-300M FT
python3 training/m03_wav2vec2_xlsr_300m/train.py \
  --run-dir training/m03_wav2vec2_xlsr_300m/runs/run_full_$(date +%Y%m%d) \
  --epochs 5 --batch-size 8 --grad-accum 2 --lr 1e-4 --warmup-steps 1000

# m04 cahya/wav2vec2-large-xlsr-indonesian FT
python3 training/m04_cahya_wav2vec2_id/train.py \
  --run-dir training/m04_cahya_wav2vec2_id/runs/run_full_$(date +%Y%m%d) \
  --epochs 5 --batch-size 8 --grad-accum 2 --lr 5e-5 --warmup-steps 500

# m05 MMS-1B adapter FT
python3 training/m05_mms_1b_adapter/train.py \
  --run-dir training/m05_mms_1b_adapter/runs/run_full_$(date +%Y%m%d) \
  --epochs 5 --batch-size 4 --grad-accum 4 --lr 1e-3 --warmup-steps 500

# m06 Conformer-CTC small (from-scratch)
python3 training/m06_conformer_ctc/train.py \
  --run-dir training/m06_conformer_ctc/runs/run_full_$(date +%Y%m%d) \
  --epochs 30 --batch-size 32 --hidden-size 256 --num-layers 6 --lr 3e-4

# m07 Bi-LSTM CTC (from-scratch)
python3 training/m07_bilstm_ctc/train.py \
  --run-dir training/m07_bilstm_ctc/runs/run_full_$(date +%Y%m%d) \
  --epochs 30 --batch-size 32 --hidden-size 512 --num-layers 5 --lr 3e-4
```

#### Conventional (`training_conventional/`)
```bash
# m08 HMM-GMM template classifier (Baum-Welch EM)
python3 training_conventional/m08_hmm_gmm/train.py \
  --run-dir training_conventional/m08_hmm_gmm/runs/run_full_$(date +%Y%m%d) \
  --hmm-iters 25 --hmm-states 5 --hmm-mixtures 3

# m09 DNN-HMM hybrid (CTC loss, batch = budget frame)
python3 training_conventional/m09_dnn_hmm/train.py \
  --run-dir training_conventional/m09_dnn_hmm/runs/run_full_$(date +%Y%m%d) \
  --dnn-hidden 512 --dnn-layers 4 --dnn-context 5 \
  --dnn-epochs 30 --dnn-batch-size 12000 --dnn-lr 1e-3

# m10 GMM-HMM-DNN 3-stage (Stage 3 DNN = CTC, sama seperti m09)
python3 training_conventional/m10_gmm_hmm_dnn/train.py \
  --run-dir training_conventional/m10_gmm_hmm_dnn/runs/run_full_$(date +%Y%m%d) \
  --hmm-states 5 --hmm-mixtures 3 --hmm-iters 25 \
  --dnn-hidden 512 --dnn-layers 4 --dnn-context 5 --dnn-epochs 30 --dnn-batch-size 12000

# m11 Vanilla Transformer (Vaswani 2017 baseline)
python3 training_conventional/m11_vanilla_transformer/train.py \
  --epochs 80 --batch-size 16 --lr 5e-4 \
  --d-model 192 --nhead 4 --num-layers 6 --ff 256 --dropout 0.1 \
  --input-dim 80 --amp --seed 2026

# m12 ★ ViT-modified-ID (USER'S NOVEL ARCH, unpublished)
python3 training_conventional/m12_vit_modified/train.py \
  --epochs 200 --batch-size 16 --lr 5e-4 \
  --d-model 192 --nhead 4 --num-layers 2 --ff 256 --dropout 0.1 \
  --input-dim 80 --amp --specaug \
  --lambda-ctc 0.1 --scheduler plateau --seed 42

# m13 Wav2Letter CNN-CTC
python3 training_conventional/m13_wav2letter_cnn/train.py \
  --run-dir training_conventional/m13_wav2letter_cnn/runs/run_full_$(date +%Y%m%d) \
  --epochs 50 --batch-size 16 --lr 3e-4

# m14 Jasper-mini CNN-CTC
python3 training_conventional/m14_jasper_cnn/train.py \
  --run-dir training_conventional/m14_jasper_cnn/runs/run_full_$(date +%Y%m%d) \
  --epochs 40 --batch-size 8 --lr 2e-4
```

### 2.3 Recipe B (smoke) — verifikasi pipeline cepat
Subsample 200 train / 50 val / 1 epoch. Total ~1–2 menit per model.
```bash
# Contoh — Whisper-small smoke
python3 training/m02_whisper_small/train.py \
  --run-dir training/m02_whisper_small/runs/run_smoke_$(date +%H%M) \
  --max-train-samples 200 --max-val-samples 50 \
  --epochs 1 --batch-size 4

# Contoh — HMM-GMM smoke
python3 training_conventional/m08_hmm_gmm/train.py \
  --run-dir training_conventional/m08_hmm_gmm/runs/run_smoke_$(date +%H%M) \
  --max-train-samples 200 --max-val-samples 50 \
  --hmm-iters 5 --hmm-states 4 --hmm-mixtures 2
```

### 2.4 Recipe C (VRAM-constrained, RTX 4060 8 GB)
```bash
# m02 Whisper-small di laptop 8 GB
python3 training/m02_whisper_small/train.py \
  --run-dir training/m02_whisper_small/runs/run_full_$(date +%Y%m%d) \
  --epochs 3 --batch-size 2 --grad-accum 8 \
  --gradient-checkpointing --lr 1e-5

# m05 MMS-1B-adapter di laptop
python3 training/m05_mms_1b_adapter/train.py \
  --run-dir training/m05_mms_1b_adapter/runs/run_full_$(date +%Y%m%d) \
  --epochs 5 --batch-size 2 --grad-accum 8 \
  --gradient-checkpointing --lr 1e-3
```

---

## 3. Lookup Cepat — Default vs Recommended Hyperparameter

Disusun per family untuk traceability paper:

### 3.1 Whisper FT (m01, m02)
| Flag | Default | Smoke (Recipe B) | Full Recipe A | Justifikasi |
|------|---------|------------------|---------------|-------------|
| `--epochs` | 2 | 1 | 3 (small) / 5 (tiny) | Whisper sudah pretrained besar, 3 epoch cukup |
| `--batch-size` | 8 | 2 | 4 (small) / 16 (tiny) | small model = 244 M params membatasi BS di 8 GB |
| `--grad-accum` | 2 | 1 | 4 (small) / 1 (tiny) | effective batch_size = 16 di laptop |
| `--lr` | 1e-5 | 1e-5 | 1e-5 (small) / 5e-6 (tiny) | Whisper FT umumnya pakai LR rendah |
| `--warmup-steps` | 100 | 5 | 500 | linear warmup ~3% total steps |

### 3.2 wav2vec2 / MMS (m03, m04, m05)
| Flag | Default | Recommended Full | Catatan |
|------|---------|-------------------|---------|
| `--epochs` | 2 | 5 | CTC head fresh di m03 → butuh epochs |
| `--batch-size` | 8 | 8 (m03/m04) / 4 (m05) | MMS-1B ≈ 7 GB peak |
| `--grad-accum` | 2 | 2 (m03/m04) / 4 (m05) | |
| `--lr` | 1e-4 | 1e-4 (m03) / 5e-5 (m04) / 1e-3 (m05 adapter) | adapter LR jauh lebih tinggi |
| `--target-lang` | None | `ind` (m05 only) | wajib untuk MMS ind adapter |
| `--adapter-only` | False | True (m05 only) | freeze base 1 B params, train ~3 M adapter |
| `--gradient-checkpointing` | False | enable jika OOM | trade ~30% speed for 30% VRAM |

### 3.3 From-scratch encoder (m06, m07)
| Flag | Default | Recommended Full |
|------|---------|-------------------|
| `--arch` | required | `conformer` (m06) / `bilstm` (m07) |
| `--epochs` | 2 | 30 |
| `--batch-size` | 16 | 32 |
| `--lr` | 3e-4 | 3e-4 |
| `--hidden-size` | 512 | 256 (m06) / 512 (m07) |
| `--num-layers` | 4 | 6 (m06) / 5 (m07) |

### 3.4 HMM family (m08, m09, m10)
| Flag | Default | Recipe A |
|------|---------|----------|
| `--mode` | required | `hmm_gmm` / `dnn_hmm` / `gmm_hmm_dnn` |
| `--hmm-iters` ⭐ | 10 | **25–50** |
| `--hmm-states` | 5 | 5–9 |
| `--hmm-mixtures` | 2 | 3–8 |
| `--cov-type` | `diag` | `diag` (8GB) / `full` (lebih banyak RAM) |
| `--dnn-epochs` | 3 | 20–40 |
| `--dnn-hidden` | 512 | 512–1024 |
| `--dnn-layers` | 4 | 4–6 |
| `--dnn-context` | 5 | 5–7 |
| `--dnn-batch-size` | 256 | **8000–16000** (CTC = frame-count budget, naikkan utk konvergensi) |

> **Penting (m09/m10 sejak 2026-05-29):** DNN dilatih dengan **CTC loss**
> (blank = `<pad>`=0), bukan lagi frame cross-entropy pada linear-alignment.
> Decode = argmax per-frame → collapse repeat → buang blank. `--dnn-batch-size`
> kini dihitung dalam **jumlah frame** (bukan utterance), jadi nilai 256 terlalu
> kecil — pakai 8000+ supaya tiap step CTC melihat banyak utterance.
>
> **Ekspektasi realistis:** m09/m10 adalah baseline akustik monophone-style
> tanpa LM eksternal. WER-nya akan **tinggi (≈0.85–0.97 di subset, turun pelan
> dengan full data + 30 epoch)** dan akan tetap menjadi model terlemah — ini
> hasil yang **benar secara ilmiah** (baseline konvensional memang harus kalah
> dari Conformer/Whisper). Kalau WER > 1.0 (prediksi jauh lebih panjang dari
> label) itu **bug**, bukan kapasitas — lihat Update Log 2026-05-29.

### 3.5 Vanilla TF + ViT-modified-ID (m11, m12 — wrapper)
| Flag | Default Wrapper | Recommended Full |
|------|------------------|-------------------|
| `--epochs` | 80 (m11) / 200 (m12) | 80–200 |
| `--batch-size` | 16 | 16 |
| `--lr` | 5e-4 | 5e-4 |
| `--d-model` | 192 | 192 |
| `--nhead` | 4 | 4 |
| `--num-layers` | 6 (m11) / 2 (m12) | 6 / 2 |
| `--ff` | 256 | 256 |
| `--lambda-ctc` | 0.1 (m12 only) | 0.1 |
| `--scheduler` | `plateau` (m12) | `plateau` |
| `--specaug` | enabled (m12) | enable |

### 3.6 CNN-CTC (m13, m14)
| Flag | Default | Recommended Full |
|------|---------|-------------------|
| `--arch` | required | `wav2letter` (m13) / `jasper` (m14) |
| `--epochs` | 2 | 50 (m13) / 40 (m14) |
| `--batch-size` | 16 | 16 (m13) / 8 (m14) |
| `--lr` | 3e-4 | 3e-4 (m13) / 2e-4 (m14) |
| `--dropout` | 0.1 | 0.1 (m13) / 0.2 (m14) |

---

## 4. Cara Standar Cek Hyperparameter Tiap Trainer

```bash
# Setiap trainer support --help dengan deskripsi default + range
python3 training/common/whisper_trainer.py --help
python3 training/common/wav2vec2_trainer.py --help
python3 training/common/from_scratch_trainer.py --help
python3 training_conventional/common/pkl_cnn_ctc_trainer.py --help
python3 training_conventional/common/pkl_hmm_trainer.py --help
```

Tidak perlu edit kode untuk tuning — selalu pakai CLI flag.

---

## 5. Catatan untuk Paper Section 4.2 (Training Setup)

### Justifikasi pemilihan default
1. **Whisper FT lr = 1e-5**: konsisten dengan rekomendasi original paper
   (Radford et al. 2022) untuk fine-tuning, jauh di bawah pretraining LR.
2. **wav2vec2 lr = 1e-4**: rekomendasi Baevski et al. (2020) untuk
   downstream FT.
3. **MMS adapter lr = 1e-3**: 10× lebih tinggi karena adapter starts dari
   random init (Pratap et al. 2023).
4. **HMM-GMM hmm-iters = 25**: standard untuk Baum-Welch convergence pada
   Indonesian speech corpus berdasarkan Indonesian Phoneme Lexicon literature.
5. **Conformer/Bi-LSTM epochs = 30**: dari-scratch CTC butuh banyak epoch
   untuk align (Gulati et al. 2020 melaporkan 50–100 untuk LibriSpeech).
6. **CNN-CTC epochs = 50 (m13) / 40 (m14)**: Wav2Letter (Collobert 2016) dan
   Jasper (Li 2019) original paper merekomendasikan 50–200 epoch. Kita kompromi
   karena RTX 4060 throughput.

### Reproducibility
- Random seed default: 42 (semua trainer kecuali m11=2026, m12=42)
- Deterministic mode: tambah `--deterministic` jika tersedia
- Library versions: tersimpan di `meta.json` setiap run folder
- Re-plot tanpa retrain: lihat `REPLAY_GUIDE.md` (6 journal style preset)

---

## 6. Acuan & Cross-References

- **Workflow per-terminal**: `RUN_GUIDE.md`
- **Re-plotting & journal style**: `REPLAY_GUIDE.md`
- **Hasil aggregator final**: `reports/all_models_full/comparison.md`,
  `paper_table.tex`
- **Per-folder docs**:
  - `training/README.md`, `training/README-RUN.md`, `training/SCALING.md`
  - `training_conventional/README.md`, `README-RUN.md`, `SCALING.md`
- **Model research report**: `Whisper_Verification_Sessions/session_20260521_233637_grand_master_model_research/`
- **Dataset statistics**: `Whisper_Verification_Sessions/session_20260524_125144_dataset_statistics_viz/`

---

## 7. Update Log

| Tanggal | Perubahan |
|---------|-----------|
| 2026-05-24 | Dokumen awal: 6 family + 3 recipe + lookup hyperparameter lengkap untuk 14 model |
| 2026-05-24 | **Bug fix HMM**: `params="cmt"` → `params="mc"`/`"mcw"`. Strict left-right transmat fixed during EM — tidak ada lagi warning `transmat_ zero rows`. |
| 2026-05-24 | **Safety net**: `unique_run_dir()` auto-timestamp jika `--run-dir` collide dengan run sebelumnya. Format: `<base>_HHMMSS`. Aktif di semua 14 trainer + 2 wrapper (m11, m12). |
| 2026-05-24 | **m11/m12 add Val WER**: `train_model_vanilla.py` + `train_model_vit.py` sekarang menampilkan **Val WER + Val CER** per epoch. Plot `cer.png`/`cer_vit.png` punya 4 kurva: Train/Val CER (solid) + Train/Val WER (dashed). |
| 2026-05-25 | **Progress visibility fix**: tambah tqdm progress bar + first-batch timing diagnostic + ETA log every 100 batches di `from_scratch_trainer.py` (m06/m07) dan `pkl_cnn_ctc_trainer.py` (m13/m14). Fix `lr_scheduler.step()` ordering: hanya advance scheduler setelah `scaler.step()` benar-benar berhasil (tidak skip karena inf/nan FP16). User tidak akan lihat "stuck" lagi tanpa update. |
| 2026-05-25 | **`--grad-accum` flag** ditambahkan ke `from_scratch_trainer.py`. Effective batch = `batch_size × grad_accum` (sama gradient signal, lebih kecil VRAM). Trainer sekarang catch CUDA OOM dengan hint langsung berisi command yang harus dicoba. Default Bi-LSTM (m07) di RUN_GUIDE.md diturunkan dari `--batch-size 32` ke `--batch-size 16 --grad-accum 2` (effective batch tetap 32, peak VRAM ~5 GB instead of 7 GB). User bisa pakai `--batch-size 16 --grad-accum 4` untuk effective batch 64. |
| 2026-05-28 | **Best-model saving**: semua 14 trainer otomatis save best model dengan naming konsisten `best_wer<value>_e<N>.pt` (frozen historical) + `best.pt` (pointer). Per-epoch checkpoints `epoch_NNN.pt` tetap disimpan supaya user bisa cleanup manual nanti. HF Trainer (m01–m05) plus integrasi `metric_for_best_model="wer"` + `load_best_model_at_end=True`. HMM family (m08–m10) save sebagai `best_wer<value>_final.pkl`. Fix juga torch 2.10 OneCycleLR zero-division bug dengan `pct_start=0.3`. |
| 2026-05-28 | **Data in Brief compliance + Fair Comparison Protocol**: tambah `data_in_brief` style preset (PDF vector + 600 DPI raster + Times serif + Okabe-Ito + line+marker patterns + viridis colormap, semua DiB-compliant). Tambah `FAIR_COMPARISON_PROTOCOL.md` dengan justifikasi epoch budget per family (30 ep from-scratch, 5 ep pretrained-FT, 30 EM HMM). Tambah m02b_whisper_medium_ft/ folder untuk paper model #9. Append "SECTION KHUSUS PAPER-GRADE" ke RUN_GUIDE.md di paling bawah (terpisah dari section tuning). |
| 2026-05-29 | **m11/m12 versioned run-dir + m12 num-layers fairness fix**: (1) Wrapper default run_dir sekarang `runs/run_full_<YYYYMMDD>_<HHMMSS>` (timestamped per-second) supaya re-run TIDAK menimpa hasil sebelumnya. (2) `unique_run_dir()` sentinel list di-extend untuk include root-script artifacts (`transformer_asr_last.pth`, `cer.png`, `cer_vit.png`, `model_summary.{png,pdf}`, dll) untuk collision detection lebih akurat. (3) m12 default `--num-layers` 2 → 6 (matches m11 vanilla untuk fairness alignment). (4) m12 default `--epochs` 200 → 30 (paper-grade fair). User's original 200-epoch / 2-layer run reproducible di Appendix B via `--epochs 200 --num-layers 2` flag explicit. |
| 2026-05-29 | **Test pipeline + AI-agent benchmark report**: tambah test scripts untuk semua 9 paper models. Output JSON `test_paper.json` per-model adalah single source of truth untuk AI agent menulis paper. (a) `test_helper.py` di common/ define schema + helpers (find_best_checkpoint, write_test_results). (b) Per-family test scripts: `from_scratch_test.py` (m06/m07), `pkl_cnn_ctc_test.py` (m13/m14), `pkl_hmm_test.py` (m08-m10), `m02b_whisper_medium_ft/test.py` (HF generate). (c) m11/m12 wrappers upgraded: pasca-call root script, parse predictions CSV → write our JSON schema. (d) NEW `aggregate_paper_test_results.py` di project root: reads 9 test_paper.json → produces `reports/paper_benchmark/{benchmark.json, benchmark.md, benchmark_table.csv, paper_table.tex, sample_predictions.md, training_summary.md}`. AI agent cukup baca `benchmark.json` untuk tulis paper Section 5 + Table 1 + Appendix A + Section 4.2/4.3. |
| 2026-05-29 | **Vanilla/ViT model fixes**: (1) PositionalEncoding `max_len` default `1000 → 8192` di `transformer_model_vanilla.py` + `transformer_model_vit.py`. Sebelumnya: outlier sample dengan max=12901 frames → RuntimeError di pos_enc. Sekarang: aman untuk seluruh dataset (after Conv1d 4× downsample, 3225 frames < 8192). (2) m11/m12 wrapper sekarang dedup args: user-provided flags override wrapper defaults; cmd line tidak ada lagi duplicate `--epochs 30 --epochs 30`. Logic: `extract_user_flags()` parse `extra` argv, skip wrapper default untuk flag yang user pass. Verified: 0 duplicate untuk semua flag. |
| 2026-05-29 | **m09 DNN-HMM + m10 GMM-HMM-DNN critical fix**: (1) ROOT CAUSE error "stuck di building frame labels": kode lama build `X_train_arr = np.concatenate(...)` = **68 GB float32 array** untuk full 71792 utterances → OOM/hang. FIX: streaming — `stack_context` dihitung per-utterance di dalam batch loop, tidak ada giant array. (2) Per-epoch logging: m09/m10 sekarang decode val SETIAP epoch → `history.json` + `log.txt` punya WER/CER **per epoch** (bukan 1-shot Epoch 1/1), konsisten dengan vanilla/vit/from-scratch. Tiap epoch save best checkpoint (`best_wer*_e*.pt`). (3) m10 stage-3 per-epoch history ditulis ke MAIN run_dir (bukan subfolder). (4) Fix `BestCheckpointTracker` import yang hilang di pkl_hmm_trainer.py. Verified: schema history.json m07/m09/m10/m13 semua IDENTIK. |
| 2026-05-29 | **m09/m10 WER>1 root-cause + CTC decoding fix**: User lapor m09 latih 7-9 epoch tapi WER ~3.0-3.6, val_acc=0, prediksi gibberish ~10× lebih panjang dari label. DIAGNOSA (terbukti empiris): vocab adalah SPM **subword** (`an`,`ng`,`kan`), adjacent-token repeat rate = **0.0000**, dan tidak ada blank token. Trainer lama latih frame-DNN dgn **cross-entropy pada linear-alignment** (244 frame → 244 token argmax), lalu decode collapse-repeat. Karena subword tidak pernah repeat berturut, collapse hampir tidak menghapus apa-apa → output ~10× kepanjangan → WER>1. Ini **bug desain, bukan kapasitas**. FIX (berbasis Zeyer et al. Interspeech 2017 "CTC = special case of full-sum HMM training"): latih FrameDNN dgn **`nn.CTCLoss(blank=0)`** (blank = `<pad>`). Network belajar emit blank antar subword → collapse+remove-blank → hipotesis panjang benar. Decode train/test sudah CTC-compatible (collapse + skip id 0,1,2,3). `--dnn-batch-size` kini = budget frame (pakai 8000+). HASIL smoke: WER **3.45 → 0.92-0.98**, train loss turun 7.6→0.16, prediksi mengandung kata benar ("Palembang","Mahasiswa"). JAWABAN pertanyaan user: setelah bug fix, WER sisa yang tinggi = kombinasi (a) butuh full data + 30 epoch, (b) ceiling arsitektur baseline DNN-HMM monophone tanpa LM — m09/m10 memang harus jadi model terlemah (hasil ilmiah yang benar). Docstring header pkl_hmm_trainer.py + §3.4 + FAIR_COMPARISON_PROTOCOL diupdate. |

> **Catatan untuk update kemudian**: jika ada hyperparameter baru ditambahkan
> ke trainer, atau recipe tuning baru ditemukan optimal, append ke dokumen ini
> dengan tanggal di Update Log. Hal ini memudahkan reviewer paper untuk
> mereproduksi hasil eksperimen apapun versi-nya.

---

## 8. Safety Nets (otomatis aktif)

### 8.1 Anti-overwrite via `unique_run_dir()`

Semua trainer (modern + conventional) sekarang memanggil `unique_run_dir()`
di awal `main()`. Logic:

1. Jika `--run-dir <X>` BELUM ADA → dipakai apa adanya.
2. Jika `--run-dir <X>` ADA tapi KOSONG (atau cuma ada empty subdirs) → dipakai
   apa adanya.
3. Jika `--run-dir <X>` ADA dan berisi sentinel file (`history.json`,
   `meta.json`, `config.json`, `log.txt`) → **otomatis** suffix `_HHMMSS`.
4. Jika `_HHMMSS` juga sudah ada (sub-second re-run) → tambahkan counter
   `_HHMMSS_2`, `_HHMMSS_3`, ...

Contoh log saat aktif:
```
[hmm-trainer] resolved run_dir: training_conventional/m08_hmm_gmm/runs/run_full_20260524_163027
```

Konsekuensi: re-run command yang sama persis tetap aman — hasil lama tidak
hilang. Cocok untuk eksperimen tuning iteratif.

### 8.2 HMM transmat fix

Untuk m08 / m09 stage 1 / m10 stage 1: strict left-right transmat di-PIN dan
tidak di-update selama EM. Hyperparameter:
- `--hmm-iters N` controls EM iterations (emission update)
- `--hmm-states N` controls topology (5–9)
- `--hmm-mixtures K` controls Gaussian mixture per state (2–8)
- `--cov-type {diag, full, tied, spherical}` controls covariance structure

Transmat sendiri TIDAK lagi sebagai hyperparameter — selalu strict left-right
uniform per skip-no-skip.

