# RUN_GUIDE — All-Model Per-Terminal Execution + Hyperparameter Tuning

> **Workflow**: launch satu model per terminal, di terminal manapun, paralel atau sequential.
> Setelah semua **14 fine-tuned + 3 zero-shot = 17 systems** selesai, agent akan
> menjalankan aggregator untuk produce final 17-arch paper comparison.

## Index

- [Pre-flight](#pre-flight)
- [⭐ Hyperparameter Tuning — penting!](#hyper)
  - [Konsep "epoch" per family](#epoch-concept)
  - [Tabel lengkap hyperparameter](#hp-table)
  - [Recipe tuning (akurasi, kecepatan, ukuran)](#recipes)
- [Modern models — `training/`](#modern)
- [Zero-shot baselines](#zs)
- [Conventional models — `training_conventional/`](#conv)
- [Post-run aggregation](#aggregate)

---

<a id="pre-flight"></a>
## Pre-flight (one-time setup)

```bash
# Setiap terminal butuh ini di awal
source ~/miniconda3/etc/profile.d/conda.sh
conda activate torch-gpu
cd "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA"

# Build conventional features SEKALI (~12 menit pada /mnt/c)
python3 training_conventional/common/spm_builder.py
python3 training_conventional/common/feature_builder.py
```

> **Convention**: setiap full run masuk `runs/run_full_$(date +%Y%m%d)/`. Jangan
> hapus folder smoke (`runs/run_smoke_*/`) — itu evidence bahwa pipeline OK.

## 💾 Best-model saving + manual cleanup

Setiap trainer sekarang **otomatis** menyimpan best model (lowest WER) selama
training. Naming convention dijaga konsisten supaya user mudah membandingkan
antar-run dan menghapus checkpoint yang tidak dipakai.

### Struktur checkpoint folder

Untuk modern + from-scratch + CNN-CTC trainer:
```
runs/run_full_20260525/
└── checkpoints/
    ├── epoch_001.pt              ← per-epoch (selalu disimpan)
    ├── epoch_002.pt
    ├── ...
    ├── epoch_030.pt
    ├── best_wer0p2345_e018.pt    ← frozen historical best
    └── best.pt                   ← pointer ke current best (rewritten tiap update)
```

Untuk HMM family (m08, m09, m10) — single-shot training (no per-epoch):
```
runs/run_full_20260525/
└── checkpoints/
    ├── best_wer0p3500_final.pkl  ← frozen final model
    └── best.pkl                  ← pointer
```

### Naming convention detail

- `best_wer<value>_e<N>.pt` — **frozen** historical best (never overwritten;
  jadi user bisa compare multiple bests dari berbagai run / tuning iteration)
- `best.pt` — **current best pointer**, di-rewrite setiap kali ada best baru
- WER value di-encode dengan `.` → `p` (so `0.2345` jadi `0p2345`) supaya filename
  filesystem-safe
- `_e<N>` zero-padded 3 digit untuk sortabilitas alphanumerik

### Console log saat best update

```
Epoch 12: Train Loss=0.831 | Val Loss=0.612 | Train Acc=0.879 | Val Acc=0.872 | Val WER=0.234 | Val CER=0.092 | Time=00:23:01 | GPU=4900MB
  ★ New best WER=0.234 @ epoch 12 → best_wer0p2345_e012.pt
```

Kalau epoch berikutnya WER tidak improve, **tidak ada save baru** — yang lama
tetap.

### Multi-run scenario (yang user khawatirkan: "bingung kalau ada 2 best")

Dengan `unique_run_dir()` auto-timestamp + best naming dengan WER value,
user bisa lihat run mana yang terbaik dengan `ls`:
```bash
$ ls training/m02_whisper_small/runs/
run_full_20260524/                  ← first attempt
run_full_20260524_171532/           ← second attempt (different hyperparam)
run_full_20260525_092103/           ← third attempt

$ ls training/m02_whisper_small/runs/run_full_20260524/checkpoints/
best_wer0p1234_e002.pt              ← best dari run pertama
best.pt

$ ls training/m02_whisper_small/runs/run_full_20260524_171532/checkpoints/
best_wer0p0892_e003.pt              ← best dari run kedua
best.pt
```
WER langsung kelihatan dari nama file — tidak perlu buka history.json untuk
tahu run mana lebih bagus.

### Manual cleanup (hapus run yang tidak dipakai)

```bash
# Lihat dulu best WER tiap run
for d in training/m02_whisper_small/runs/run_full_*/checkpoints; do
  best=$(ls "$d" 2>/dev/null | grep '^best_wer' | head -1)
  echo "$(dirname $d | xargs basename): $best"
done

# Hapus run yang tidak dipakai
rm -rf training/m02_whisper_small/runs/run_full_20260524

# Atau lebih granular — cuma hapus per-epoch, simpan best.pt + best_wer*_e*.pt:
for d in training/m02_whisper_small/runs/run_full_*/checkpoints; do
  rm -f "$d"/epoch_*.pt   # hapus semua per-epoch
  # best.pt + best_wer*_e*.pt tetap
done
```

### Restore kembali (load best model untuk inference)

```python
import torch
ckpt = torch.load("training/m02_whisper_small/runs/run_full_20260524_171532/checkpoints/best.pt")
print("WER:", ckpt["best_wer"])         # 0.0892
print("epoch:", ckpt["epoch"])           # 3
print("prev_best:", ckpt["prev_best"])   # 0.1234 (dari epoch sebelumnya kalau ada)
# Apply ke model:
model.load_state_dict(ckpt["model_state"])
```

## ⚠️ VRAM budgeting (RTX 4060 Laptop 8 GB)

### m06 Conformer-CTC + m07 Bi-LSTM CTC: jangan over-batch

Bi-LSTM bidirectional menyimpan ALL hidden states untuk backprop. VRAM scales
linear dengan `batch_size × sequence_length × num_layers × hidden_size`. Untuk
full data (~700 frames per utterance, 5 layers × 512 hidden):

| `--batch-size` | `--grad-accum` | Effective batch | Peak VRAM | Status |
|---:|---:|---:|---:|---|
| 8 | 4 | 32 | ~3 GB | safe |
| 16 | 2 | 32 | ~5 GB | recommended |
| 16 | 4 | 64 | ~5 GB | larger effective batch, recommended |
| 32 | 1 | 32 | ~7 GB | tight, mungkin OOM saat val |
| 64 | 1 | 64 | ~12 GB | **OOM pada 8 GB** → user error sebelumnya |

**Rule of thumb**: `effective_batch = --batch-size × --grad-accum` — ini yang
menentukan kualitas training (gradient signal). Yang menentukan VRAM adalah
hanya `--batch-size`. Jadi prefer `--batch-size 16 --grad-accum 4` daripada
`--batch-size 64 --grad-accum 1`.

### Recovery dari OOM

Kalau dapat error `CUDA out of memory`, trainer sekarang otomatis print hint:
```
[OOM] CUDA out of memory at first batch.
  Suggested fix: reduce --batch-size and use --grad-accum to keep effective batch.
  Current: batch_size=64 grad_accum=1
  Try:     --batch-size 32 --grad-accum 2
  Or:      --batch-size 16 --grad-accum 4
  Also try: PYTORCH_ALLOC_CONF=expandable_segments:True python3 ...
```

Ikuti saran tersebut.

### Per-trainer VRAM ceiling (verified)

| Slot | Aman pada 8 GB? | Saran |
|------|:---:|-------|
| m01 Whisper-tiny | ✓ | `--batch-size 16` OK |
| m02 Whisper-small | ✓ (tight) | `--batch-size 4 --grad-accum 4` (default) |
| m03 wav2vec2-XLS-R-300M | ✓ | `--batch-size 8 --grad-accum 2` (default) |
| m04 cahya-w2v2-id | ✓ | `--batch-size 8 --grad-accum 2` (default) |
| m05 MMS-1B-adapter | ✓ (tight) | `--batch-size 4 --grad-accum 4` (default) |
| m06 Conformer-CTC | ✓ | `--batch-size 16 --grad-accum 2` (NEW) |
| m07 Bi-LSTM CTC | ✓ | `--batch-size 16 --grad-accum 2` (NEW; jangan 64!) |
| m08–m10 HMM | ✓ (CPU only or <500MB) | tidak ada batch concept |
| m11 Vanilla TF | ✓ | default OK |
| m12 ViT-modified-ID | ✓ | default OK |
| m13 Wav2Letter | ✓ | `--batch-size 16` OK |
| m14 Jasper-mini | ✓ (tight) | `--batch-size 8` (default) |

## 📊 Progress visibility & I/O bottleneck (PENTING untuk full data)

### Apakah ini stuck atau lambat?

Dataset di `/mnt/c` (Windows mount via WSL2) **I/O bound**. Untuk model from-scratch
(m06 Conformer-CTC, m07 Bi-LSTM CTC, m13 Wav2Letter, m14 Jasper), tiap epoch butuh:
- **22–40 menit per epoch** untuk full 71,792 train samples (just I/O)
- **30 epoch × 30 menit ≈ 15 jam total** — ini normal!

Trainer sekarang menampilkan estimasi setelah batch pertama:
```
[from-scratch] train batches/epoch: 2244, val batches/epoch: 481
[from-scratch] data on /mnt/c (Windows mount); first batch may take ~5–10s for warmup
[from-scratch] first batch OK in 1.5s; estimated epoch time: 56.0 min
                (28.0 h total for 30 epochs)
Epoch 1/30 [Train]: 12%|█▊    | 268/2244 [06:52<50:35,  0.65it/s, loss=2.341, lr=3.00e-04]
```

Progress bar (tqdm) menunjukkan:
- Step saat ini / total step
- Persen progress
- Wall time elapsed / ETA
- Loss saat ini + LR saat ini

### Cara cek apakah benar-benar stuck atau lambat

```bash
# Jika tqdm progress berhenti update > 5 menit, baru concern
# Cara cek dari terminal lain:
nvidia-smi --query-gpu=utilization.gpu --format=csv -l 5
# Jika GPU util > 0% → LAGI compute, BUKAN stuck
# Jika GPU util = 0% lama → mungkin stuck di I/O

# Cek log file (di-tulis tiap epoch)
tail -f training/m07_bilstm_ctc/runs/run_full_*/log.txt
```

### Speed-up I/O (opsional)

1. **Pindah dataset ke disk Linux native** (NTFS → ext4):
   ```bash
   cp -r /mnt/c/.../Dataset_Balanced19 ~/asr_data/
   # Lalu pakai --data-root ~/asr_data/Dataset_Balanced19
   ```
   Speedup: 3–5× (NTFS via DrvFs sangat lambat).

2. **Pre-compute features** ke `.pkl` (sudah dilakukan di `training_conventional/`):
   `pkl_cnn_ctc_trainer.py` (m13, m14) baca dari `data_pkl/train.pkl` — jauh lebih cepat
   karena audio + mel sudah di-pre-compute.

3. **Naikkan `num_workers`** (opsi advance, butuh edit kode):
   - Default `num_workers=0` aman tapi slow
   - Set `num_workers=2` di DataLoader bisa 2× lebih cepat tapi kadang hang di /mnt/c

## 🔒 Safety nets (otomatis aktif di semua 14 trainer)

### 1. Auto-timestamp run folder (anti-overwrite)
Jika `--run-dir <X>` sudah berisi run sebelumnya (mis. `history.json`,
`meta.json`, `config.json`, `log.txt` ada), trainer akan **otomatis** men-suffix
dengan `_HHMMSS` supaya hasil lama tidak ditimpa.

Contoh:
```bash
# Pertama kali — folder dibuat
python3 training_conventional/m08_hmm_gmm/train.py \
  --run-dir training_conventional/m08_hmm_gmm/runs/run_full_20260524 \
  --hmm-iters 30 --hmm-states 5 --hmm-mixtures 3 --seed 42  # [FAIRNESS-C] budget kanonik
# → menulis ke runs/run_full_20260524/

# Re-run dengan flag yang sama — trainer auto-timestamp
python3 training_conventional/m08_hmm_gmm/train.py \
  --run-dir training_conventional/m08_hmm_gmm/runs/run_full_20260524 \
  --hmm-iters 30 --hmm-states 5 --hmm-mixtures 3 --seed 42  # JANGAN ubah budget (anti-asimetri)
# → menulis ke runs/run_full_20260524_163027/
# → hasil run pertama TETAP utuh di runs/run_full_20260524/
```

Setiap log akan menampilkan path final yang dipakai:
```
[hmm-trainer] resolved run_dir: training_conventional/m08_hmm_gmm/runs/run_full_20260524_163027
```

**Konsekuensi praktis**: kamu bisa **eksperimen tuning bebas** dengan command
yang sama, tiap run masuk folder berbeda. Untuk melihat semua run yang pernah
dilakukan:
```bash
ls -la training_conventional/m08_hmm_gmm/runs/
# run_full_20260524/
# run_full_20260524_163027/
# run_full_20260524_171532/
# ...
```

Kalau kamu ingin OVERWRITE secara eksplisit, hapus folder lama dulu manually:
```bash
rm -rf training_conventional/m08_hmm_gmm/runs/run_full_20260524
# lalu re-run
```

### 2. HMM transmat fixed (no degeneracy)
Untuk HMM family (m08/m09/m10), strict left-right transmat di-pinned dan
TIDAK di-update selama EM. Ini menghindari warning `transmat_ zero rows`.
Flag yang efektif (**[FAIRNESS-C] budget kanonik dikunci** — jangan diubah untuk run paper):
- `--hmm-iters 30` (Baum-Welch EM iterations; sudah konvergen, jangan dinaikkan)
- `--hmm-states 5`
- `--hmm-mixtures 3`
- `--cov-type diag` (default; `full` hanya untuk eksperimen RAM, bukan run paper)


---

<a id="hyper"></a>
## ⭐ Hyperparameter Tuning — Cara Mudah Tweak Tiap Model

**Semua hyperparameter di-set lewat CLI flag, bukan editing kode.** Tinggal
tambah flag di belakang command.

<a id="epoch-concept"></a>
### Konsep "Epoch" per Family Model

| Family | Konsep "epoch" | Flag yang relevan |
|--------|----------------|-------------------|
| **Whisper / wav2vec2 / MMS** (m01–m05) | Iterasi standar gradient descent atas dataset | `--epochs N` |
| **From-scratch CNN/Transformer** (m06, m07, m13, m14) | Iterasi gradient descent | `--epochs N` |
| **Vanilla TF + ViT-modified-ID** (m11, m12) | Iterasi gradient descent | `--epochs N` (di wrapper) |
| **m08 HMM-GMM** | **TIDAK ADA "epoch" konvensional** — pakai Baum-Welch EM (1× run, N iterations internal) | `--hmm-iters N` |
| **m09 DNN-HMM** | DNN (CTC loss) punya epoch; CTC belajar alignment sendiri | `--dnn-epochs N` |
| **m10 GMM-HMM-DNN** | Stage 1 (HMM): `--hmm-iters`. Stage 3 (DNN, CTC): `--dnn-epochs` | `--hmm-iters N --dnn-epochs M` |

**Kenapa HMM-GMM cuma "Epoch 1/1" di log?** Karena HMM bukan model neural —
training Baum-Welch EM bukan iterasi atas dataset, melainkan algoritma maximum-
likelihood yang konvergen dalam beberapa iterasi internal. **[FAIRNESS-C]** Untuk run
paper, budget dikunci dan TIDAK dinaikkan (anti-asimetri — jangan menganakemaskan baseline):
- `--hmm-iters 30` (EM sudah konvergen ~10–25 iter; 30 = buffer aman)
- `--hmm-states 5`
- `--hmm-mixtures 3`

Hasil tetap "1 epoch" di log = "1 round of Baum-Welch", tapi parameter HMM lebih bagus.

<a id="hp-table"></a>
### Tabel Hyperparameter Lengkap (semua 14 trainer)

#### Modern models (`training/`)

##### m01–m02 Whisper (`whisper_trainer.py`)
| Flag | Default | Recommended (full) | Effect |
|------|---------|---------------------|--------|
| `--epochs` | 2 | **3** (small), 5 (tiny) | Iterasi gradient descent |
| `--batch-size` | 8 | **4** (small) / 16 (tiny) | Per-GPU batch size |
| `--grad-accum` | 2 | **4** (small) / 1 (tiny) | Effective batch = batch_size × grad_accum |
| `--lr` | 1e-5 | **1e-5** (small) / 5e-6 (tiny) | Learning rate |
| `--warmup-steps` | 100 | **500** | LR warmup steps |
| `--gradient-checkpointing` | False | True if OOM | Trade speed for VRAM |
| `--max-train-samples` | 0 (full) | 0 | Subsample for smoke |
| `--max-val-samples` | 0 (full) | 0 | Subsample dev for smoke |
| `--language` | `indonesian` | `indonesian` | Forced language tag |
| `--task` | `transcribe` | `transcribe` | Whisper task |
| `--seed` | 42 | 42 | Reproducibility |

##### m03–m05 wav2vec2/MMS (`wav2vec2_trainer.py`)
| Flag | Default | Recommended (full) | Effect |
|------|---------|---------------------|--------|
| `--epochs` | 2 | **5** | Gradient-descent epochs |
| `--batch-size` | 8 | **8** (m03/m04) / 4 (m05) | Per-GPU batch |
| `--grad-accum` | 2 | **2** (m03/m04) / 4 (m05) | |
| `--lr` | 1e-4 | **1e-4** (m03) / 5e-5 (m04) / 1e-3 (m05 adapter) | |
| `--warmup-steps` | 100 | **500–1000** | |
| `--target-lang` | None | `ind` (m05 only) | MMS adapter target language |
| `--adapter-only` | False | **True** (m05 only) | Train only adapter, freeze base |
| `--gradient-checkpointing` | False | True if OOM | |

##### m06 Conformer-CTC + m07 Bi-LSTM (`from_scratch_trainer.py`)
| Flag | Default | Recommended (full) | Effect |
|------|---------|---------------------|--------|
| `--arch` | required | `conformer` (m06) / `bilstm` (m07) | Pilih arsitektur |
| `--epochs` | 2 | **30** | Banyak epoch karena from-scratch |
| `--batch-size` | 16 | **32** | |
| `--lr` | 3e-4 | **3e-4** | |
| `--hidden-size` | 512 | **256** (m06) / 512 (m07) | Hidden dimension |
| `--num-layers` | 4 | **6** (m06) / 5 (m07) | Transformer/LSTM layers |
| `--dropout` | 0.1 | **0.1** | |
| `--n-mels` | 80 | 80 | Mel filter banks |

#### Conventional models (`training_conventional/`)

##### m08 HMM-GMM, m09 DNN-HMM, m10 GMM-HMM-DNN (`pkl_hmm_trainer.py`)

**Common flags (semua mode):**
| Flag | Default | Recommended (full) | Effect |
|------|---------|---------------------|--------|
| `--mode` | required | `hmm_gmm` / `dnn_hmm` / `gmm_hmm_dnn` | Pilih varian HMM |
| `--max-train-samples` | 0 (full) | 0 | |
| `--max-val-samples` | 0 (full) | 0 | |
| `--seed` | 42 | 42 | |

**HMM-specific (m08, m10 stage 1):**
| Flag | Default | Recommended (full) | Effect |
|------|---------|---------------------|--------|
| `--hmm-iters` | 10 | **30 (kanonik)** | EM iterations; ★ [FAIRNESS-C] kunci 30, JANGAN naikkan |
| `--hmm-states` | 5 | **5 (kanonik)** | States per HMM (left-right); kunci 5 |
| `--hmm-mixtures` | 2 | **3 (kanonik)** | Gaussian mixtures per state; kunci 3 |
| `--cov-type` | `diag` | `diag` (8GB) / `full` (lebih banyak RAM) | Covariance matrix structure |

**DNN-specific (m09, m10 stage 3) — dilatih dengan CTC loss (blank=`<pad>`):**
| Flag | Default | Recommended (full) | Effect |
|------|---------|---------------------|--------|
| `--dnn-epochs` | 3 | **30 (kanonik)** | DNN training epochs; ★ [FAIRNESS-C] sama dgn m11/m12 from-scratch |
| `--dnn-batch-size` | 256 | **12000** | ★ Budget **FRAME** (bukan utterance) untuk CTC. 256 terlalu kecil. |
| `--dnn-lr` | 1e-3 | **1e-3** | Learning rate |
| `--dnn-hidden` | 512 | **512–1024** | DNN hidden width |
| `--dnn-layers` | 4 | **4–6** | DNN depth |
| `--dnn-context` | 5 | **5–7** | ±N frame context window |

##### m11 Vanilla Transformer + m12 ViT-modified-ID ★ (wrappers)
Semua flag yang diteruskan ke root script `train_model_vanilla.py` /
`train_model_vit.py`. Wrapper di `m11_*/train.py` dan `m12_*/train.py`
menambahkan flag default; user bisa **override** dengan menambahkan flag di
belakang command.

| Flag | Default (wrapper) | Recommended (full) | Effect |
|------|-------------------|---------------------|--------|
| `--epochs` | 80 (m11) / 200 (m12) | **80–200** | |
| `--batch-size` | 16 | **16** | |
| `--lr` | 5e-4 | **5e-4** | |
| `--d-model` | 192 | **192** | Transformer width |
| `--nhead` | 4 | **4** | Attention heads |
| `--num-layers` | 6 (m11) / 2 (m12) | **6 (m11) / 2 (m12)** | Encoder layers |
| `--ff` | 256 | **256** | FFN dimension |
| `--dropout` | 0.1 | **0.1** | |
| `--lambda-ctc` | 0.1 (m12 only) | **0.1** | CTC auxiliary weight |
| `--scheduler` | `plateau` (m12) | `plateau` | LR schedule |
| `--specaug` | True (m12) | enable | SpecAugment data aug |
| `--amp` | True | enable | FP16 autocast |
| `--seed` | 2026 (m11) / 42 (m12) | sesuai default | Reproducibility |

##### m13 Wav2Letter + m14 Jasper-mini (`pkl_cnn_ctc_trainer.py`)
| Flag | Default | Recommended (full) | Effect |
|------|---------|---------------------|--------|
| `--arch` | required | `wav2letter` (m13) / `jasper` (m14) | Arsitektur |
| `--epochs` | 2 | **50 (m13) / 40 (m14)** | |
| `--batch-size` | 16 | **16 (m13) / 8 (m14)** | |
| `--lr` | 3e-4 | **3e-4 (m13) / 2e-4 (m14)** | |
| `--warmup-pct` | 0.1 | **0.1** | OneCycle warmup % |
| `--dropout` | 0.1 | **0.1 (m13) / 0.2 (m14)** | |
| `--grad-clip` | 5.0 | **5.0** | Gradient clipping |
| `--input-dim` | 80 | 80 | Mel features |

<a id="recipes"></a>
### 3 Recipe Tuning

#### Recipe A — Lebih akurat (paper-grade)
Naikkan epoch + model size. Trade-off: lebih lama, lebih banyak VRAM.
```bash
# m02 Whisper-small
python3 training/m02_whisper_small/train.py \
  --run-dir training/m02_whisper_small/runs/run_full_$(date +%Y%m%d) \
  --epochs 5 --batch-size 4 --grad-accum 8 --lr 5e-6 --warmup-steps 1000

# m08 HMM-GMM  [FAIRNESS-C] budget kanonik (jangan naikkan states/mixtures/iters)
python3 training_conventional/m08_hmm_gmm/train.py \
  --run-dir training_conventional/m08_hmm_gmm/runs/run_full_$(date +%Y%m%d) \
  --hmm-iters 30 --hmm-states 5 --hmm-mixtures 3 --seed 42

# m09 DNN-HMM (CTC loss, batch = budget frame)
python3 training_conventional/m09_dnn_hmm/train.py \
  --run-dir training_conventional/m09_dnn_hmm/runs/run_full_$(date +%Y%m%d_%H%M%S) \
  --dnn-epochs 30 --dnn-hidden 512 --dnn-layers 4 --dnn-context 5 \
  --dnn-batch-size 12000 --dnn-lr 1e-3 --seed 42

# m13 Wav2Letter
python3 training_conventional/m13_wav2letter_cnn/train.py \
  --run-dir training_conventional/m13_wav2letter_cnn/runs/run_full_$(date +%Y%m%d) \
  --epochs 80 --batch-size 16 --lr 3e-4 --dropout 0.15
```

#### Recipe B — Lebih cepat (smoke / debug)
Subsample data + epoch sedikit. Trade-off: WER tinggi tapi pipeline OK.
```bash
# Smoke 200 samples / 1 epoch — semua model under 1 menit
python3 training/m02_whisper_small/train.py \
  --run-dir training/m02_whisper_small/runs/run_smoke_$(date +%H%M) \
  --max-train-samples 200 --max-val-samples 50 \
  --epochs 1 --batch-size 4

python3 training_conventional/m08_hmm_gmm/train.py \
  --run-dir training_conventional/m08_hmm_gmm/runs/run_smoke_$(date +%H%M) \
  --max-train-samples 200 --max-val-samples 50 \
  --hmm-iters 5 --hmm-states 4 --hmm-mixtures 2
```

#### Recipe C — VRAM-constrained (RTX 4060 8 GB)
Pakai gradient checkpointing + grad accumulation. Trade-off: lebih lambat ~30 %.
```bash
# m02 di laptop 8GB
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

### Cek hyperparameter mana yang tersedia
Selalu bisa dilakukan dengan `--help`:
```bash
python3 training/common/whisper_trainer.py --help
python3 training_conventional/common/pkl_hmm_trainer.py --help
# dst.
```

---

<a id="modern"></a>
## Modern models (`training/`)

Setiap command di bawah asumsi terminal sudah `conda activate torch-gpu` dan
`cd <project_root>`. **Run satu per terminal**.

### Terminal 1 — m01 Whisper-tiny FT (~3 jam)
```bash
python3 training/m01_whisper_tiny/train.py \
  --run-dir training/m01_whisper_tiny/runs/run_full_$(date +%Y%m%d) \
  --epochs 5 --batch-size 16 --grad-accum 1 --lr 5e-6 --warmup-steps 500
```

### Terminal 2 — m02 Whisper-small FT ★ PRIMARY (~14 jam RTX 4060)
```bash
python3 training/m02_whisper_small/train.py \
  --run-dir training/m02_whisper_small/runs/run_full_$(date +%Y%m%d) \
  --epochs 3 --batch-size 4 --grad-accum 4 --lr 1e-5 --warmup-steps 500
```
> Di Colab Pro+ A100 ~2 jam — lihat `training/SCALING.md`.

### Terminal 3 — m03 wav2vec2-XLS-R-300M FT (~10–12 jam)
```bash
python3 training/m03_wav2vec2_xlsr_300m/train.py \
  --run-dir training/m03_wav2vec2_xlsr_300m/runs/run_full_$(date +%Y%m%d) \
  --epochs 5 --batch-size 8 --grad-accum 2 --lr 1e-4 --warmup-steps 1000
```

### Terminal 4 — m04 cahya/wav2vec2-large-xlsr-indonesian FT (~10 jam)
```bash
python3 training/m04_cahya_wav2vec2_id/train.py \
  --run-dir training/m04_cahya_wav2vec2_id/runs/run_full_$(date +%Y%m%d) \
  --epochs 5 --batch-size 8 --grad-accum 2 --lr 5e-5 --warmup-steps 500
```

### Terminal 5 — m05 MMS-1B adapter FT (~14 jam)
```bash
python3 training/m05_mms_1b_adapter/train.py \
  --run-dir training/m05_mms_1b_adapter/runs/run_full_$(date +%Y%m%d) \
  --epochs 5 --batch-size 4 --grad-accum 4 --lr 1e-3 --warmup-steps 500
```

### Terminal 6 — m06 Conformer-CTC small (~6–8 jam)
```bash
python3 training/m06_conformer_ctc/train.py \
  --run-dir training/m06_conformer_ctc/runs/run_full_$(date +%Y%m%d) \
  --epochs 30 --batch-size 16 --grad-accum 2 \
  --hidden-size 256 --num-layers 6 --lr 3e-4
```
> Effective batch = 16 × 2 = 32. Aman pada RTX 4060 8 GB.

### Terminal 7 — m07 Bi-LSTM CTC (~5 jam)
```bash
python3 training/m07_bilstm_ctc/train.py \
  --run-dir training/m07_bilstm_ctc/runs/run_full_$(date +%Y%m%d) \
  --epochs 30 --batch-size 16 --grad-accum 2 \
  --hidden-size 512 --num-layers 5 --lr 3e-4
```
> Bi-LSTM 5-layer 512-hidden butuh memory besar. **Jangan pakai `--batch-size 64`** — OOM pada 8 GB. Pakai `--batch-size 16 --grad-accum 4` untuk effective batch 64.

---

<a id="zs"></a>
## Zero-shot baselines (~30 menit each, no training)

> Default smoke pakai `--max-samples 30`; full evaluation pakai `--max-samples 0`.

### Terminal 8 — zs1 Whisper-large-v3 zero-shot (~25 menit RTX 4060 fp16)
```bash
python3 training/zero_shot_baselines/run_inference.py \
  --model-id openai/whisper-large-v3 \
  --run-dir training/zero_shot_baselines/runs/whisper_large_v3_full_$(date +%Y%m%d) \
  --max-samples 0
```

### Terminal 9 — zs2 Whisper-medium zero-shot (~16 menit)
```bash
python3 training/zero_shot_baselines/run_inference.py \
  --model-id openai/whisper-medium \
  --run-dir training/zero_shot_baselines/runs/whisper_medium_full_$(date +%Y%m%d) \
  --max-samples 0
```

### Terminal 10 — zs3 MMS-1B-all zero-shot (~5 menit)
```bash
python3 training/zero_shot_baselines/run_inference.py \
  --model-id facebook/mms-1b-all --target-lang ind \
  --run-dir training/zero_shot_baselines/runs/mms_1b_all_full_$(date +%Y%m%d) \
  --max-samples 0
```

---

<a id="conv"></a>
## Conventional models (`training_conventional/`)

### Terminal 11 — m08 HMM-GMM template classifier (~30 menit, CPU only)
```bash
python3 training_conventional/m08_hmm_gmm/train.py \
  --run-dir training_conventional/m08_hmm_gmm/runs/run_full_$(date +%Y%m%d) \
  --hmm-iters 30 --hmm-states 5 --hmm-mixtures 3 --seed 42
```
> ★ HMM-GMM TIDAK pakai `--epochs`; `--hmm-iters` = jumlah Baum-Welch EM iteration.
> **[FAIRNESS-C 2026-05-29]** Budget kanonik = `--hmm-iters 30 --hmm-states 5 --hmm-mixtures 3`.
> JANGAN menaikkan states/mixtures/iters untuk "akurasi lebih tinggi": itu melanggar
> pagar anti-asimetri (menganakemaskan baseline lemah) dan EM sudah konvergen ~10–25 iter.
> Lihat `training_conventional/reports/fairness_protocol_C_FINAL.md`.

### Terminal 12 — m09 DNN-HMM hybrid (~1 jam)
```bash
python3 training_conventional/m09_dnn_hmm/train.py \
  --run-dir training_conventional/m09_dnn_hmm/runs/run_full_$(date +%Y%m%d_%H%M%S) \
  --dnn-hidden 512 --dnn-layers 4 --dnn-context 5 \
  --dnn-epochs 30 --dnn-batch-size 12000 --dnn-lr 1e-3 --seed 42
```
> Gunakan `--dnn-epochs` (bukan `--epochs`) untuk DNN training.
> DNN dilatih dengan **CTC loss** (blank=`<pad>`); `--dnn-batch-size` = budget
> **frame**, jadi pakai 12000 (256 terlalu kecil). Ekspektasi WER tinggi
> (≈0.85–0.95) dan turun pelan — baseline terlemah. **WER>1 = bug, bukan kapasitas.**

### Terminal 13 — m10 GMM-HMM-DNN 3-stage (~2 jam)
```bash
python3 training_conventional/m10_gmm_hmm_dnn/train.py \
  --run-dir training_conventional/m10_gmm_hmm_dnn/runs/run_full_$(date +%Y%m%d_%H%M%S) \
  --hmm-iters 30 --hmm-states 5 --hmm-mixtures 3 \
  --dnn-hidden 512 --dnn-layers 4 --dnn-context 5 --dnn-epochs 30 \
  --dnn-batch-size 12000 --dnn-lr 1e-3 --seed 42
```
> Stage 1 (HMM-GMM): `--hmm-iters/states/mixtures`. Stage 3 (DNN, **CTC loss**):
> `--dnn-epochs/...`. `--dnn-batch-size` = budget **frame** (pakai 12000).

### Terminal 14 — m11 Vanilla Transformer (~14–40 jam)

> **Note**: Wrapper default sekarang `--epochs 30` (paper-grade fair).
> Command di bawah ini reproduksi **extended training** (80 epoch) yang
> akan dilaporkan di Appendix B paper. Untuk paper Table 1 (fair comparison),
> pakai Terminal P-4 di section "PAPER-GRADE" paling bawah.

Train (extended training reproduction):
```bash
python3 training_conventional/m11_vanilla_transformer/train.py \
  --epochs 80 --batch-size 16 --lr 5e-4 \
  --d-model 192 --nhead 4 --num-layers 6 --ff 256 --dropout 0.1 \
  --input-dim 80 --amp --seed 2026
```
Test (setelah train):
```bash
python3 training_conventional/m11_vanilla_transformer/test.py \
  --max-decode-len 64
```

### Terminal 15 — m12 ★ ViT-modified-ID (USER'S NOVEL ARCH) (~14–38 jam)

> **Note**: Wrapper default sekarang `--epochs 30 --num-layers 6` (paper-grade fair).
> Command di bawah ini reproduksi **extended training** (200 epoch / 2-layer) yang
> akan dilaporkan di Appendix B paper. Untuk paper Table 1 (fair comparison),
> pakai Terminal P-5 di section "PAPER-GRADE" paling bawah.

Train (extended training reproduction):
```bash
python3 training_conventional/m12_vit_modified/train.py \
  --epochs 200 --batch-size 16 --lr 5e-4 \
  --d-model 192 --nhead 4 --num-layers 2 --ff 256 --dropout 0.1 \
  --input-dim 80 --amp --specaug \
  --lambda-ctc 0.1 --scheduler plateau --seed 42
```
Test (setelah train):
```bash
python3 training_conventional/m12_vit_modified/test.py --max-decode-len 64
```

### Terminal 16 — m13 Wav2Letter CNN-CTC (~5 jam)
```bash
python3 training_conventional/m13_wav2letter_cnn/train.py \
  --run-dir training_conventional/m13_wav2letter_cnn/runs/run_full_$(date +%Y%m%d) \
  --epochs 50 --batch-size 16 --lr 3e-4
```

### Terminal 17 — m14 Jasper-mini CNN-CTC (~6 jam)
```bash
python3 training_conventional/m14_jasper_cnn/train.py \
  --run-dir training_conventional/m14_jasper_cnn/runs/run_full_$(date +%Y%m%d) \
  --epochs 40 --batch-size 8 --lr 2e-4
```

---

<a id="aggregate"></a>
## Post-run aggregation (agent jalankan setelah ALL 17 terminal selesai)

```bash
python3 aggregate_all_models.py
```
Output `reports/all_models_full/`:
- `comparison.md`, `comparison_table.csv` — paper Table 1
- `paper_table.tex` — LaTeX `\input{...}` siap pakai
- `wer_bar_all17.png` — paper Figure 3 (1 bar per arsitektur)
- `wer_vs_params.png` — Figure 4 (WER vs params, log scale)
- `era_timeline.png` — Figure 5 (1990s → 2026 timeline)
- `family_summary.png` — grouped bar by family
- `summary.json` — machine-readable supplement

Lalu re-plot paper figures dalam style jurnal target — lihat `REPLAY_GUIDE.md`:
```bash
# Single style, semua model
python3 replot_all.py --style ieee --pattern "run_full*" \
  --out-root reports/paper_figures_ieee --formats pdf png

# Multi-model overlay (Figure 2)
python3 replot_compare.py --auto-discover \
  --metrics wer cer train_loss val_loss --style ieee \
  --out reports/paper_figures_ieee/figure2_overlay.pdf
```

---

## Tracking terminal yang sudah selesai

```bash
echo "m02 done: $(date)" >> training/STATUS.txt
echo "m12 done: $(date)" >> training_conventional/STATUS.txt
```
Aggregator akan membaca STATUS.txt untuk konfirmasi kelengkapan.

## GPU sharing tips

RTX 4060 8 GB — beberapa kombo aman, beberapa OOM:

| Kombo | OK? | Reason |
|-------|:---:|--------|
| m08 + m09 | ✓ | m08 CPU-only |
| m13 + m08 | ✓ | m13 ≤500 MB, m08 CPU |
| m02 + apapun | ✗ | m02 ≈6 GB peak |
| m05 + apapun | ✗ | m05 ≈7 GB peak |
| m14 + GPU model lain | ✗ | m14 ≈2 GB + spike risk |
| m11 + m12 | ✗ | attention spike |

**Rekomendasi**: 1 GPU model per terminal kecuali yakin headroom cukup.

## Resume / restart

Jika terminal mati di tengah run:
- Modern m01–m07 (HF Trainer): re-run dengan `--run-dir` sama → auto-resume
- Conventional m13/m14: simpan `epoch_NNN.pt` per epoch; manual load
- m11/m12 wrappers: forward `--checkpoint <path>` ke root script

## Smoke vs full

Smoke runs (`runs/run_smoke_*`) sudah pernah jalan dan **tidak boleh dihapus** —
itu evidence pipeline OK. Full runs masuk `runs/run_full_<YYYYMMDD>/` terpisah.

## Tuning tip akhir

1. Mulai dengan **default** (yang sudah di-tune di README-RUN.md masing-masing folder)
2. Cek log per epoch — jika WER plateau, tambah epoch atau LR warmup
3. Jika OOM, kurangi `--batch-size` dan tambah `--grad-accum`
4. HMM family: tambah `--hmm-iters`, `--hmm-states`, `--hmm-mixtures` untuk akurasi lebih
5. Re-train tidak perlu re-plot — cukup `python3 replot_all.py --style <jurnal>` setelah training

---

# 📖 SECTION KHUSUS — PAPER-GRADE FAIR COMPARISON (Data in Brief submission)

> **Section ini terpisah dari konfigurasi smoke / tuning di atas.** Yang di atas
> tetap berlaku untuk eksplorasi internal. Section di bawah ini adalah
> **protokol final yang harus dipakai untuk run yang masuk paper Data in
> Brief.** Hyperparameter di sini sudah di-harmonize untuk **fairness**
> antar arsitektur — reviewer paper akan menerima hasilnya.

## P1. 9 Model Paper (target submission)

| Slot | Model | Epoch budget | Justifikasi |
|------|-------|:-:|---|
| m08 | HMM-GMM ⭐ | 30 EM iter | Baum-Welch convergence buffer |
| m09 | DNN-HMM ⭐ | 30 ep DNN | CTC acoustic model convergence (WER≈0.85–0.95, baseline terlemah) |
| m10 | GMM-HMM-DNN ⭐ | 30+30 | 3-stage hybrid (Stage 3 DNN = CTC) |
| m11 | Vanilla Transformer ⭐ | 30 ep | from-scratch enc-dec |
| m12 | ViT-modified-ID ⭐ ☆ | 30 ep | from-scratch (user's novel; extended 200-ep run di Appendix) |
| m07 | Bi-LSTM CTC ⭐ | 30 ep | from-scratch RNN-CTC |
| m06 | Conformer-CTC ⭐ | 30 ep | from-scratch conv+attn-CTC |
| m13 | Wav2Letter ⭐ | 30 ep | from-scratch CNN-CTC |
| m02b | Whisper-medium FT ⭐ | 5 ep | pretrained FT (Radford 2022 convention) |

☆ = user's novel architecture (Ratna 2026, this paper's first public report)

**Total wall time** (RTX 4060 Laptop 8 GB, sequential): ~80 jam.
**Pada Colab Pro+ A100-40GB**: ~16 jam.

## P2. Setup Pre-flight (sekali saja)

```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate torch-gpu
cd "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA"

# Build feature pickles untuk conventional models (~12 menit, sekali saja)
python3 training_conventional/common/spm_builder.py
python3 training_conventional/common/feature_builder.py
```

## P3. 9 Paper Commands (run di terminal terpisah)

Semua command di-set untuk **30 epoch (atau setara) dengan effective batch 32**
untuk fairness. Output otomatis di-save ke `runs/run_paper_<YYYYMMDD>/`
yang tidak bentrok dengan run sebelumnya (auto-timestamp via `unique_run_dir`).

### Terminal P-1 — m08 HMM-GMM (CPU, ~30 menit)
```bash
python3 training_conventional/m08_hmm_gmm/train.py \
  --run-dir training_conventional/m08_hmm_gmm/runs/run_paper_$(date +%Y%m%d) \
  --hmm-iters 30 --hmm-states 5 --hmm-mixtures 3 --seed 42
```

### Terminal P-2 — m09 DNN-HMM (~1 jam)
```bash
python3 training_conventional/m09_dnn_hmm/train.py \
  --run-dir training_conventional/m09_dnn_hmm/runs/run_paper_$(date +%Y%m%d_%H%M%S) \
  --dnn-epochs 30 --dnn-hidden 512 --dnn-layers 4 --dnn-context 5 \
  --dnn-batch-size 12000 --dnn-lr 1e-3 --seed 42
```
> DNN dilatih dengan **CTC loss** (blank=`<pad>`); decode = greedy collapse.
> `--dnn-batch-size` = budget **frame** (256 terlalu kecil). Ekspektasi WER
> ≈0.85–0.95 (baseline terlemah, hasil ilmiah yang benar). **WER>1 = bug.**

### Terminal P-3 — m10 GMM-HMM-DNN (~2 jam)
```bash
python3 training_conventional/m10_gmm_hmm_dnn/train.py \
  --run-dir training_conventional/m10_gmm_hmm_dnn/runs/run_paper_$(date +%Y%m%d_%H%M%S) \
  --hmm-iters 30 --hmm-states 5 --hmm-mixtures 3 \
  --dnn-epochs 30 --dnn-hidden 512 --dnn-layers 4 --dnn-context 5 \
  --dnn-batch-size 12000 --dnn-lr 1e-3 --seed 42
```

### Terminal P-4 — m11 Vanilla Transformer (~14 jam laptop / 2 jam A100)
```bash
python3 training_conventional/m11_vanilla_transformer/train.py \
  --epochs 30 --batch-size 16 --lr 5e-4 \
  --d-model 192 --nhead 4 --num-layers 6 --ff 256 --dropout 0.1 \
  --input-dim 80 --amp --seed 42
```
> Note: epoch turun dari 80 → 30 untuk fairness. Run 80-epoch validated
> milik supervisor akan tetap dilaporkan sebagai "extended training" di
> Appendix B paper.

### Terminal P-5 — m12 ViT-modified-ID ⭐ ☆ USER NOVEL (~14 jam laptop)
```bash
python3 training_conventional/m12_vit_modified/train.py \
  --epochs 30 --batch-size 16 --lr 5e-4 \
  --d-model 192 --nhead 4 --num-layers 6 --ff 256 --dropout 0.1 \
  --input-dim 80 --amp --specaug \
  --lambda-ctc 0.1 --scheduler plateau --seed 42
```
> Default wrapper sudah set `epoch=30 --num-layers 6 --batch-size 16 --grad-accum 2`,
> jadi cukup `python3 training_conventional/m12_vit_modified/train.py` tanpa flag.
>
> User's original 200-epoch / 2-layer run dilaporkan di Appendix B (extended training).
> Main paper Table 1 menggunakan 30-epoch / 6-layer fair comparison (matches m11).
>
> **Versioned run-dir**: tiap invocation menulis ke `runs/run_full_<YYYYMMDD>_<HHMMSS>/`
> baru — hasil run sebelumnya tidak terhapus.

### Terminal P-6 — m13 Wav2Letter CNN-CTC (~5 jam)
```bash
python3 training_conventional/m13_wav2letter_cnn/train.py \
  --run-dir training_conventional/m13_wav2letter_cnn/runs/run_paper_$(date +%Y%m%d) \
  --epochs 30 --batch-size 16 --lr 3e-4 --seed 42
```
> **[FIX 2026-05-31]** CTC greedy decode kini truncate tiap sample ke panjang
> output valid (`new_lens`) sebelum collapse. Sebelumnya men-decode seluruh
> sumbu waktu ter-pad → ekor token sampah → prediksi lebih panjang dari label,
> Train/Val Acc=0 & WER/CER>1 di epoch awal. Fix di `common/pkl_cnn_ctc_trainer.py`
> (`ctc_greedy_decode(..., lengths=new_lens)`) + `common/pkl_cnn_ctc_test.py`
> (berlaku juga untuk m14 Jasper). Diuji: smoke 2-ep → CER 1.03→0.60, tanpa ekor.
> **[+2026-05-31]** `model_summary.txt` (params + arsitektur) kini ditulis di awal
> training (seragam dgn 8 model lain), jadi tetap ada walau run terinterupsi.

### Terminal P-7 — m07 Bi-LSTM CTC (~12 jam, recipe C VRAM-safe)
```bash
python3 training/m07_bilstm_ctc/train.py \
  --run-dir training/m07_bilstm_ctc/runs/run_paper_$(date +%Y%m%d) \
  --epochs 30 --batch-size 16 --grad-accum 2 \
  --hidden-size 512 --num-layers 5 --lr 3e-4 --seed 42
```

### Terminal P-8 — m06 Conformer-CTC (~8 jam)
```bash
python3 training/m06_conformer_ctc/train.py \
  --run-dir training/m06_conformer_ctc/runs/run_paper_$(date +%Y%m%d) \
  --epochs 30 --batch-size 16 --grad-accum 2 \
  --hidden-size 256 --num-layers 6 --lr 3e-4 --seed 42
```

### Terminal P-9 — m02b Whisper-medium FT (~10 jam laptop / 1.5 jam A100)
```bash
python3 training/m02b_whisper_medium_ft/train.py \
  --epochs 5 --batch-size 2 --grad-accum 16 \
  --lr 1e-5 --warmup-steps 500 \
  --gradient-checkpointing --seed 42
```
> 5 epoch (bukan 30) karena pretrained Whisper-medium akan over-fit dengan
> training panjang. Sangat disarankan run di Colab Pro+ A100 (~1.5 jam).

## P3-T. Testing per-model (jalankan SETELAH training selesai)

> **NEW**: setelah training selesai, jalankan test untuk SETIAP model. Output
> JSON `test_paper.json` di `<run_dir>/test_results/` adalah single source of
> truth untuk **AI agent menulis paper**.

> **[PIPELINE UPDATE 2026-05-30]** Perbaikan integritas test (commit `adfa7fd`):
> - **m10 GMM-HMM-DNN**: artifact `.pkl` kini menyimpan `model_state` (dulu hilang →
>   test jalan DNN random-init / WER≈1). **m09 & m10 WAJIB di-run ulang** dgn trainer
>   terbaru agar artifact valid.
> - **m09/m10**: artifact memuat bobot **best-on-val** (dari `checkpoints/best.pt`),
>   bukan epoch terakhir — konsisten dgn protokol fairness.
> - **`find_best_checkpoint`**: bila hanya ada `epoch_*.pt`, kini pilih epoch ber-WER
>   terendah dari `history.json` (bukan epoch terakhir).
> - **Aggregator**: label `family`+`model_id` otoritatif dari tabel kanonik
>   `PAPER_MODELS` (cegah drift label, mis. "unpublished" bocor ke Table 1).
> Detail: `training_conventional/reports/pipeline_audit_test_aggregate.md`.

Tiap test.py auto-pick best checkpoint terbaru (run_paper_*) di slot folder,
jalankan greedy decode pada full test split (15,376 utterances), dan save JSON
+ CSV + sample preds.

### Per-model test commands

```bash
# Conventional models (8 dari 9 paper)
python3 training_conventional/m08_hmm_gmm/test.py
python3 training_conventional/m09_dnn_hmm/test.py
python3 training_conventional/m10_gmm_hmm_dnn/test.py
python3 training_conventional/m11_vanilla_transformer/test.py
python3 training_conventional/m12_vit_modified/test.py    # ☆ USER NOVEL
python3 training_conventional/m13_wav2letter_cnn/test.py

# Modern models (m07 + m06 di training/, m02b di training/)
python3 training/m07_bilstm_ctc/test.py
python3 training/m06_conformer_ctc/test.py
python3 training/m02b_whisper_medium_ft/test.py
```

Setiap test.py akan:
1. Auto-detect run_dir terbaru dari `runs/run_paper_*` (override dengan `--run-dir`)
2. Auto-detect best checkpoint dari `checkpoints/best.pt` atau `best_wer*_e*.pt`
3. Run greedy decoding pada full test split
4. Save:
   - `<run_dir>/test_results/test_paper.json` — master JSON (AI-readable)
   - `<run_dir>/test_results/predictions.csv` — full per-utterance predictions
   - `<run_dir>/test_results/test_summary.md` — human-readable summary

### Override default

```bash
# Test specific run_dir
python3 training_conventional/m12_vit_modified/test.py \
  --run-dir training_conventional/m12_vit_modified/runs/run_paper_20260601_140523

# Test only first 100 samples (debugging)
python3 training/m07_bilstm_ctc/test.py --max-test-samples 100
```

### Output JSON schema (untuk AI agent)

```json
{
  "model_id": "m12-vit-modified-ID",
  "family": "ViT-modified-ID (Ratna 2026, unpublished)",
  "is_paper_model": true,
  "is_user_novel": true,
  "checkpoint": "...",
  "checkpoint_filename": "best_wer0p1234_e012.pt",
  "best_train_wer": 0.1234,
  "best_train_epoch": 12,
  "n_epochs_trained": 30,
  "test_set": {"split": "test", "n_samples": 15376, ...},
  "metrics": {"wer": 0.1456, "cer": 0.0345, "mer": 0.1450, "wil": 0.2678, "ser": 0.5234},
  "decoding": {"method": "greedy_ar_with_ctc_aux", "beam_size": 1, "lm": null},
  "wall_time_sec": 312.5,
  "throughput_samples_per_sec": 49.2,
  "peak_gpu_mb": 2400.0,
  "predictions_csv": "<run_dir>/test_results/predictions.csv",
  "sample_predictions": [{"idx": 0, "audio": "...", "pred": "...", "label": "...",
                          "per_sample_wer": 0.0, "per_sample_cer": 0.0}, ...10 items],
  "config": {...},
  "training_meta": {...},
  "timestamp": "ISO",
  "test_environment": {...}
}
```

## P3-A. Aggregator: 9 test JSONs → paper benchmark

Setelah semua 9 model di-test, jalankan aggregator:

```bash
python3 aggregate_paper_test_results.py
# Output: reports/paper_benchmark/
#   - benchmark.json         (master, AI-readable)
#   - benchmark.md           (human-readable)
#   - benchmark_table.csv    (paper Table 1 raw data)
#   - paper_table.tex        (LaTeX \input{} ready)
#   - sample_predictions.md  (per-model 10 samples for Appendix A)
#   - training_summary.md    (hyperparameters + env per-model)
```

### `benchmark.json` schema (AI agent entry point)

```json
{
  "generated": "ISO",
  "target_journal": "Data in Brief (Elsevier, ISSN 2352-3409)",
  "n_paper_models": 9,
  "n_paper_models_present": <int>,
  "missing_paper_models": [...],
  "best_paper_model": {"model_id": ..., "wer": ..., "cer": ..., "is_user_novel": bool},
  "paper_models_ranked_by_wer": [
    {"rank": 1, "model_id": ..., "family": ..., "wer": ..., "cer": ..., "is_user_novel": bool},
    ...
  ],
  "paper_models": [<TestResult>, ...9],
  "secondary_models": [<TestResult>, ...]
}
```

## P3-AI. Cara AI Agent Membaca + Menulis Paper

Agent yang akan menulis paper Section 5 (Results) cukup baca **SATU FILE**:
`reports/paper_benchmark/benchmark.json`. Dari situ bisa derive:

1. **Section 5 prose** — dari `best_paper_model` + `paper_models_ranked_by_wer`
2. **Paper Table 1** — langsung `\input{reports/paper_benchmark/paper_table.tex}`
3. **Section 4.2 (Experimental Setup)** — dari `paper_models[*].config`
4. **Appendix A (sample predictions)** — dari `sample_predictions.md`
5. **Section 4.3 (Reproducibility)** — dari `paper_models[*].training_meta.environment`
6. **Best-model checkpoint refs** — dari `paper_models[*].checkpoint`
7. **Compute budget per model** — dari `paper_models[*].wall_time_sec` + `peak_gpu_mb`

```python
# Quick AI-agent recipe
import json
with open("reports/paper_benchmark/benchmark.json") as f:
    bench = json.load(f)

best = bench["best_paper_model"]
print(f"Best WER: {best['wer']:.4f} — {best['family']}")
for row in bench["paper_models_ranked_by_wer"]:
    print(f"#{row['rank']}: {row['model_id']:30s}  WER={row['wer']:.4f}")
```

## P4. Post-run: aggregate + replot ke Data in Brief style

Setelah semua 9 terminal training + 9 testing + aggregator selesai:

```bash
# 1. Aggregate semua hasil ke paper Table 1
python3 aggregate_all_models.py
# Output: reports/all_models_full/{paper_table.tex, comparison.md, plots, summary.json}

# 2. Re-plot semua run_paper_* ke style Data in Brief
python3 replot_all.py --style data_in_brief --pattern "run_paper_*" \
  --formats pdf png \
  --out-root reports/paper_figures_data_in_brief
# Output: reports/paper_figures_data_in_brief/<slot>/<run_name>/<plot>.{pdf,png}
# DiB-compliant: Times serif font, 600 DPI raster, vector PDF, color-blind-spalette, line+marker patterns (BW-print friendly)

# 3. Multi-model overlay untuk paper Figure 2
python3 replot_compare.py --auto-discover --pattern "run_paper_*" \
  --metrics wer cer train_loss val_loss \
  --style data_in_brief --formats pdf \
  --out reports/paper_figures_data_in_brief/figure2_overlay_9models.pdf
```

## P5. Data in Brief Compliance Checklist

- [x] **Vector format**: semua plot `.pdf` (DiB requires vector for line plots)
- [x] **Raster fallback**: `.png` @ 600 DPI (DiB minimum 300 dpi for halftone)
- [x] **Single-column figsize**: 90 mm = 3.54 in (DiB single-col width)
- [x] **Double-column figsize**: 190 mm = 7.48 in
- [x] **Font**: Times-like serif (DiB body font)
- [x] **Font size**: 8-10 pt (DiB legible at single-column)
- [x] **Colormap**: viridis (DiB bans `jet`)
- [x] **Color-blind safe palette**: Okabe-Ito (no red-green only differentiation)
- [x] **Line patterns + markers**: solid/dashed/dotted + circle/square/diamond
      (DiB requires patterns *in addition to* color)
- [x] **No AI-generated images**: all plots from matplotlib (algorithmic)
- [x] **PDF font embed**: `pdf.fonttype=42` (TrueType, Elsevier-required)
- [x] **Captions in manuscript**: not baked into image (user task; figures are
      caption-less by design — add caption in paper TeX)
- [x] **Editable tables**: `paper_table.tex` is `\input{}`-able LaTeX, never image

## P6. Reproducibility Bundle (untuk submission supplementary)

Setelah training selesai, setiap `runs/run_paper_<date>/` berisi:
- `meta.json` — environment snapshot (Python, torch, CUDA, libraries)
- `model_summary.txt` — arsitektur + jumlah parameter (ditulis di awal training; seragam m06–m14)
- `config.json` — exact CLI args
- `history.json` — per-epoch WER/CER/loss/acc/lr/gpu/throughput
- `log.txt` — human-readable training log dengan PRED/LABEL samples
- `predictions/sample_preds_e*.txt` — sample predictions per epoch
- `checkpoints/best_wer*_e*.pt` — frozen best model (with WER + epoch in filename)
- `checkpoints/best.pt` — pointer to current best
- `checkpoints/epoch_NNN.pt` — per-epoch checkpoints (untuk replay/inspection)
- `plots_data_in_brief/` — DiB-compliant figures (after `replot_all.py`)

Untuk supplementary material zip:
```bash
tar -czf paper_supplementary.tar.gz \
  reports/all_models_full/ \
  reports/paper_figures_data_in_brief/ \
  reports/hyperparameter_reference/ \
  Whisper_Verification_Sessions/session_20260524_125144_dataset_statistics_viz/ \
  RUN_GUIDE.md REPLAY_GUIDE.md \
  training/*/runs/run_paper_*/{config,history,meta}.json \
  training_conventional/*/runs/run_paper_*/{config,history,meta}.json
```

## P7. Justifikasi yang masuk paper §4.2 (siap-pakai)

```
All neural models were trained with AdamW (β₁=0.9, β₂=0.98 for Transformer
variants; β₂=0.999 for CNN and RNN architectures) using mixed-precision FP16
with gradient clipping at max-norm 5. We adopted a 5% linear warmup followed
by cosine annealing to zero learning rate. The effective batch size was held
constant at 32 across all from-scratch and HMM-DNN trainers via gradient
accumulation when single-batch GPU memory was insufficient. From-scratch
models (Bi-LSTM, Conformer, Wav2Letter, Vanilla Transformer, ViT-modified-ID)
were trained for 30 epochs and the best checkpoint was selected on validation
WER (best-on-validation); the encoder-decoder models additionally used early
stopping with patience 12. Pretrained Whisper-medium was fine-tuned for 5
epochs following Radford et al. (2022) to avoid catastrophic forgetting of
the original multilingual capability, with the best checkpoint chosen by
validation WER (load_best_model_at_end). HMM-GMM was trained via Baum-Welch EM
for 30 iterations. SpecAugment (Park et al. 2019) was applied to all neural
models with T=20, F=10, mT=2, mF=2 except HMM (incompatible). Greedy decoding
was used at evaluation time across all systems for head-to-head comparison;
language-model rescoring was deliberately omitted to avoid favoring systems
that pair more naturally with KenLM. Word and character error rates were
computed via the *jiwer* package (v3.0).
```

## P8. Sanity Checks (sebelum submit paper)

```bash
# 1. Verify semua 9 model punya run_paper_*/ dengan history.json
for slot in m02b_whisper_medium_ft m06_conformer_ctc m07_bilstm_ctc; do
  ls training/$slot/runs/run_paper_*/history.json 2>/dev/null \
    || echo "  ⚠ missing: $slot"
done
for slot in m08_hmm_gmm m09_dnn_hmm m10_gmm_hmm_dnn \
            m11_vanilla_transformer m12_vit_modified m13_wav2letter_cnn; do
  ls training_conventional/$slot/runs/run_paper_*/history.json 2>/dev/null \
    || echo "  ⚠ missing: $slot"
done

# 2. Verify best model tersimpan untuk semua
find training -name "best_wer*" -path "*/run_paper_*/*" | wc -l   # harus 8
find training_conventional -name "best_wer*" -path "*/run_paper_*/*" | wc -l

# 3. Verify plot DiB-style sudah dibuild
ls reports/paper_figures_data_in_brief/ 2>&1 | head -5

# 4. Check meta.json env snapshots match (same Python/torch versions)
find training -name meta.json -path "*/run_paper_*" -exec \
  python3 -c "import json,sys; d=json.load(open(sys.argv[1])); \
  print(d['environment']['python'], d['environment'].get('torch_version'))" {} \;
```

## P9. Reference dokumen

- `reports/hyperparameter_reference/FAIR_COMPARISON_PROTOCOL.md` — complete fairness rationale (paper-ready prose)
- `reports/hyperparameter_reference/HYPERPARAMETER_REFERENCE.md` — master hyperparameter reference
- `REPLAY_GUIDE.md` — cara re-plot ke style apapun tanpa retrain
- `reports/all_models_full/paper_table.tex` — paper Table 1 (akan terisi setelah aggregate_all_models.py)

