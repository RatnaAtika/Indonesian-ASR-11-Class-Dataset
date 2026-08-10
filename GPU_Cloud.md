# GPU Cloud Plan untuk 9 Model Paper Indonesian ASR

Tanggal audit: 2026-06-01  
Repo target: `Indonesian-ASR-11-Class-Dataset` / `Paper_Datatset_SOTA`  
Sumber command final: `RUN_GUIDE.md` bagian `P1` sampai `P3-T`  
Metode analisis: BMAD Analyst + Superpowers planning + audit repository + riset harga GPU cloud.

> Dokumen ini tidak mengganti `RUN_GUIDE.md`. Semua training final untuk paper tetap memakai command canonical di `RUN_GUIDE.md`. Dokumen ini hanya menentukan cloud GPU, storage, biaya, risiko, dan rencana eksekusi.

---

## 1. Executive decision

Rekomendasi praktis untuk menyelesaikan 9 model paper dengan murah dan cepat:

1. **Default cheapest-fast:** sewa **1x RTX 4090 24GB on-demand** di Vast.ai atau RunPod Community, disk NVMe minimal 200 GB.
2. **Jika ingin lebih cepat tanpa menaikkan total biaya banyak:** sewa **2x RTX 4090** selama 1-2 hari.
   - GPU-1: Whisper final.
   - GPU-2: BiLSTM, Conformer, m11, m12, m13, m09, m10.
   - m08 HMM-GMM jalan di CPU/local sambil GPU training.
3. **Jika Whisper-medium atau Conformer OOM/terlalu lambat di 4090:** naik ke **L40S 48GB** dulu, bukan langsung A100.
4. **A100 40GB** dipakai untuk run final yang butuh stabilitas/reproducibility tinggi, atau jika 4090/L40S gagal. A100 biasanya lebih mahal per hasil, kecuali workload benar-benar compute-bound dan speedup >2.2x dari 4090.
5. **RTX 5090** menarik kalau harga dekat 4090, tetapi wajib smoke test CUDA/PyTorch/torchaudio dulu. Risiko kompatibilitas 50-series masih lebih tinggi daripada 4090/L40S/A100.
6. **RTX 3090** paling murah untuk BiLSTM dan job kecil, tetapi untuk deadline biasanya kalah wall-clock dari 4090.

Kesimpulan biaya planning untuk 3 model berat (berdasarkan timing terbaru user):

| Skenario | Estimasi wall-clock 3 heavy | Estimasi biaya GPU | Catatan |
|---|---:|---:|---|
| Local RTX 4060 Laptop 8GB | ~175 jam | listrik lokal | Terlalu lama untuk deadline paper |
| Vast 1x RTX 4090 | ~60 jam | ~$24 GPU compute | Best value; run 2.5 hari sequential |
| Vast 2x RTX 4090 | ~30-40 jam wall-clock | ~$25-35 GPU compute + idle/setup | Lebih cepat; total GPU-hour mirip |
| Vast/RunPod RTX 5090 | ~50 jam | ~$28-40 | Pakai hanya jika stack stabil |
| L40S 48GB | ~53 jam | ~$37-48 | Aman untuk VRAM, lebih reliable |
| A100 40GB | ~46 jam | ~$42-65 | Paling defensible, bukan termurah |

Untuk **semua 9 model paper**, planning baseline terbaru adalah sekitar **210-215 jam local sequential** jika Whisper memang 20 jam/epoch. Di 1x RTX 4090 cloud, target realistis menjadi **70-85 GPU-hour termasuk buffer**, biaya sekitar **$30-50** di marketplace murah, atau **$55-90** di RunPod Secure/Lambda-style yang lebih reliable.

---

## 2. BMAD analysis

### B - Business / paper goal

Tujuan utama bukan GPU tercepat absolut, tetapi **paper-grade completion**:

- Semua 9 model di `RUN_GUIDE.md` selesai dengan budget fair.
- Waktu training, config, logs, checkpoint, test JSON, dan aggregator evidence lengkap.
- Biaya cloud masuk akal, tidak boros pada A100/H100 kalau 4090 cukup.
- Tidak ada hasil lama tertimpa; semua run final punya folder unik dan bukti reproducibility.

### M - Market / provider context

Harga GPU cloud sangat berubah per jam, terutama Vast.ai. Planning price yang dipakai di dokumen ini adalah rentang konservatif dari riset 2026:

| GPU | VRAM | Vast.ai planning | RunPod Community planning | RunPod Secure / reliable planning | Komentar |
|---|---:|---:|---:|---|
| RTX 3090 | 24GB | ~$0.20-0.30/h | ~$0.22/h | ~$0.46/h | Murah, cukup untuk BiLSTM/job kecil |
| RTX 4090 | 24GB | ~$0.35-0.45/h | ~$0.34/h | ~$0.69/h | Best default cheap-fast |
| RTX 5090 | 32GB | ~$0.44-0.70/h | ~$0.69/h | ~$0.99/h | Cepat + 32GB, tapi stack risk |
| L40S | 48GB | ~$0.60-0.90/h | ~$0.79/h | ~$0.86/h | VRAM aman, datacenter-class |
| A100 40GB | 40GB | ~$0.65-1.20/h | ~$1.19/h | ~$1.39/h | Stabil dan defensible |
| A100 80GB | 80GB | ~$0.90-1.60/h | ~$1.39-1.64/h | ~$1.49+ | Overkill untuk paper slot kecil/medium |

Sumber riset harga yang dipakai sebagai rujukan:

- ComputePrices Vast.ai pricing, update Mei 2026.
- GPUFinder Vast.ai pricing, update Mei 2026.
- RunPod pricing summaries, 2026.
- Northflank/RunPod pricing article, Desember 2025.
- Cloud GPU rental comparison, 2026.

**Catatan penting:** sebelum beli, cek live price langsung di dashboard provider dan simpan screenshot/receipt untuk evidence paper.

### A - Architecture / workload fit

Semua model paper saat ini single-GPU atau CPU; belum ada distributed training/DDP. Karena itu:

- Multi-GPU dalam satu mesin **tidak otomatis mempercepat satu model**.
- Cara mempercepat adalah menjalankan **beberapa model paralel** di GPU berbeda.
- VRAM besar membantu OOM dan batch stabil, tetapi tidak boleh mengubah effective batch/fairness tanpa dokumentasi.
- Untuk ASR, bottleneck bisa audio I/O/CPU, bukan GPU. Copy dataset ke local NVMe.

### D - Decision

Keputusan final yang paling rasional:

- **Mulai dari RTX 4090 on-demand** untuk probe dan sebagian besar final run.
- **Naik ke L40S** jika model butuh >24GB VRAM atau 4090 gagal/host buruk.
- **Gunakan A100 40GB** hanya untuk final defensible run atau jika L40S/4090 tidak stabil.
- **Gunakan 5090 opportunistic** jika harga <=1.4x 4090 dan smoke test stack lolos.
- Hindari H100/H200 untuk batch paper ini; terlalu mahal dan tidak perlu.

---

## 3. Superpowers planning lens

### Critical assumptions

1. Paper slot ke-9 saat ini adalah **m02b Whisper-small FT**. Whisper-medium tetap secondary/opsional.
2. User menyebut Whisper berat butuh **20 jam/epoch** di RTX 4060 laptop. Karena paper Whisper FT memakai 5 epoch, planning worst-case = **100 jam local**.
3. Conformer (`m06`) butuh sekitar **30 jam / 30 epoch** local.
4. BiLSTM (`m07`) butuh sekitar **1.5 jam/epoch**, jadi **45 jam / 30 epoch** local.
5. Semua command final tetap mengikuti `RUN_GUIDE.md`; cloud VRAM tidak digunakan untuk menaikkan batch/epoch tanpa alasan ilmiah.
6. Untuk model tanpa resume CLI eksplisit (m06/m07), hindari spot/preemptible.

### Verification rule before full spend

Jangan langsung bayar 2 hari A100. Lakukan probe 15-60 menit:

1. Jalankan 1 subset epoch untuk Whisper, Conformer, BiLSTM.
2. Catat `Total waktu training`, GPU util, peak VRAM, dan samples/s.
3. Hitung `cost_per_epoch = measured_epoch_hours * gpu_hour_price`.
4. Upgrade GPU hanya jika cost-per-epoch turun atau OOM teratasi.

### Stop / switch rules

- Jika RTX 4090 GPU util <40%, masalah kemungkinan I/O/CPU. Jangan langsung pindah A100; pindahkan data ke NVMe dan cek dataloader.
- Jika RTX 4090 OOM untuk Whisper-medium, pindah ke L40S/A100.
- Jika 5090 error CUDA/torchaudio/AMP, jangan debugging lama untuk final paper; pindah 4090/L40S.
- Jika Vast host throttling/unstable, pindah RunPod Community/Secure daripada kehilangan 20+ jam.

---

## 4. Audit data dan storage repository

### Dataset/split aktual

Dihitung dari `training/data_final/{train,val,test}.tsv`:

| Split | Rows | Durasi audio | Estimasi WAV bytes |
|---|---:|---:|---:|
| train | 71,792 | 92.4882 jam | 9.93 GiB |
| val | 15,376 | 19.7412 jam | 2.12 GiB |
| test | 15,376 | 18.4254 jam | 1.98 GiB |
| total unik | 102,544 file | 130.6548 jam | 14.02 GiB / 15.06 GB |

Feature cache conventional:

| Komponen | Ukuran aktual |
|---|---:|
| `training_conventional/data_pkl/train.pkl` | 6.24 GiB |
| `training_conventional/data_pkl/valid.pkl` | 1.33 GiB |
| `training_conventional/data_pkl/test.pkl` | 1.24 GiB |
| Total `training_conventional/data_pkl/` | ~8.9G |
| `training_conventional/spm/` | ~5.3 MB |
| Local Hugging Face cache saat audit | ~18G |

### Estimasi artefak final per model

Berdasarkan run yang sudah ada dan pola checkpoint saat ini:

| Model | Estimasi final run dir | Catatan storage |
|---|---:|---|
| m08 HMM-GMM | <0.1 GB | pkl kecil |
| m09 DNN-HMM | ~0.05-0.2 GB | DNN kecil |
| m10 GMM-HMM-DNN | ~0.05-0.3 GB | hybrid kecil |
| m11 Transformer | ~0.05-0.2 GB | root script artefak kecil |
| m12 ViT-modified | ~0.05-0.2 GB | artefak kecil, model_summary PDF/PNG |
| m13 Wav2Letter | ~10-15 GB | run lama teramati 10.65-13.89 GiB |
| m07 BiLSTM | ~0.5-2 GB | tergantung checkpoint terbaik yang tersimpan |
| m06 Conformer | ~4-6 GB | run lama teramati 3.71 GiB |
| m02b Whisper-small | ~3-4 GB | HF checkpoint + `best_model/` |
| m02b Whisper-medium optional | ~9-12 GB | HF model lebih besar |

### Rekomendasi disk cloud

| Disk | Bisa? | Kapan dipakai |
|---|---|---|
| 100 GB | Bisa tapi ketat | Hanya final 9 model small, tanpa old runs, cleanup disiplin |
| 200 GB | **Rekomendasi minimum** | Dataset + pkl + HF cache + final runs + probe terbatas |
| 300 GB | Rekomendasi aman | Ada Whisper-medium atau beberapa retry/probe |
| 500 GB | Aman sekali | Banyak eksperimen, simpan old runs, zip evidence sebelum download |

Perhitungan 200 GB:

```text
Raw WAV unik              ~15 GB
PKL conventional          ~9 GB
HF cache/model weights    ~10-25 GB
Final run dirs 9 model    ~25-35 GB (small) / ~35-50 GB (medium)
Temp/build/log/probe      ~20-40 GB
Safety margin             ~50 GB
Total recommended         ~150-200 GB
```

Storage cost kecil dibanding GPU. Contoh RunPod volume $0.10/GB/month: 200 GB selama 7 hari sekitar $4.7; 500 GB sekitar $11.7. Tetapi jangan lupa stop/delete storage setelah evidence diunduh.

### Upload strategy

Jangan upload seluruh folder lokal yang sudah berisi banyak old runs. Lebih bersih:

1. `git clone` repo dari GitHub.
2. Upload/copy raw dataset saja:
   - `Processed_Balanced19_v7_natural_synth/Dataset_Balanced19/`
   - `training/data_final/`
3. Upload `training_conventional/data_pkl/` dan `training_conventional/spm/`, atau rebuild di cloud:
   - `python3 training_conventional/common/spm_builder.py`
   - `python3 training_conventional/common/feature_builder.py`
4. Pastikan parent scripts untuk m11/m12 ikut tersedia:
   - `train_model_vanilla.py`
   - `train_model_vit.py`
   - `test_model_vanilla.py`
   - `test_model_vit.py`

**Risiko penting:** wrapper m11/m12 memanggil script di parent layout. Jika cloud hanya berisi folder `Paper_Datatset_SOTA/` tanpa parent scripts, m11/m12 bisa gagal.

---

## 5. 9 model paper yang dihitung

Dari `RUN_GUIDE.md` bagian P1/P3:

| Slot | Model | Budget paper | Local baseline untuk planning |
|---|---|---:|---:|
| m08 | HMM-GMM | 30 EM iter | ~0.5 jam CPU |
| m09 | DNN-HMM | 30 ep DNN | ~1 jam |
| m10 | GMM-HMM-DNN | 30+30 | ~2 jam |
| m11 | Vanilla Transformer | 30 ep | ~14 jam |
| m12 | ViT-modified-ID | 30 ep | ~14 jam |
| m07 | BiLSTM CTC | 30 ep | **45 jam** (1.5 jam/epoch) |
| m06 | Conformer CTC | 30 ep | **30 jam** |
| m13 | Wav2Letter CNN-CTC | 30 ep | ~5 jam |
| m02b | Whisper FT | 5 ep | **100 jam worst-case** (20 jam/epoch) |

Baseline total sequential local dengan angka terbaru user:

```text
m08 0.5 + m09 1 + m10 2 + m11 14 + m12 14 + m13 5 + m07 45 + m06 30 + m02b 100
= 211.5 jam sequential local planning baseline
```

Catatan: angka `RUN_GUIDE.md` lama menulis total ~80 jam RTX 4060, tetapi timing terbaru user untuk tiga model berat saja sudah ~175 jam. Jadi dokumen cloud ini memakai angka terbaru user sebagai baseline konservatif.

---

## 6. Asumsi speedup GPU untuk planning

Ini bukan benchmark final. Ini hanya model hitung awal sebelum paid probe.

| GPU | Faktor speedup terhadap RTX 4060 Laptop 8GB | Alasan |
|---|---:|---|
| RTX 3090 24GB | 1.6-2.0x | Murah, 24GB, lebih tua |
| RTX 4090 24GB | 2.5-3.5x | Best value, tensor core kuat |
| RTX 5090 32GB | 3.2-4.2x | Potensial cepat, VRAM 32GB, stack risk |
| L40S 48GB | 3.0-3.8x | VRAM besar, datacenter, tidak selalu lebih cepat per dolar |
| A100 40GB | 3.5-4.5x | Stabil, HBM, BF16 bagus, lebih mahal |

Break-even sederhana terhadap 4090 Vast ~$0.40/h:

| Upgrade | Harga planning | Harus lebih cepat dari 4090 sebesar | Kritik |
|---|---:|---:|---|
| 3090 $0.25/h | 0.625x harga 4090 | 4090 harus >1.6x lebih cepat agar lebih murah | 4090 biasanya menang untuk Transformer/Whisper; 3090 menarik untuk BiLSTM |
| 5090 $0.55/h | 1.375x harga 4090 | 5090 harus >1.4x lebih cepat | Mungkin, jika stack stabil |
| L40S $0.70/h | 1.75x harga 4090 | L40S harus >1.75x lebih cepat | Biasanya tidak; bayar untuk VRAM/reliability |
| A100 $0.90/h | 2.25x harga 4090 | A100 harus >2.25x lebih cepat | Biasanya tidak; bayar untuk stability/final defensibility |

---

## 7. Perhitungan 3 model berat

### 7.1 Runtime dan biaya planning

Harga planning yang dipakai untuk tabel ini:

- RTX 3090: $0.25/h
- RTX 4090: $0.40/h
- RTX 5090: $0.55/h
- L40S: $0.70/h
- A100 40GB: $0.90/h

| Model berat | Local RTX 4060 baseline | RTX 3090 | RTX 4090 | RTX 5090 | L40S | A100 40GB |
|---|---:|---:|---:|---:|---:|---:|
| Whisper FT 5 ep | 100.0h | 52.6h / $13.2 | **30.3h / $12.1** | 25.0h / $13.8 | 25.6h / $17.9 | 22.2h / $20.0 |
| m06 Conformer 30 ep | 30.0h | 16.7h / $4.2 | **10.0h / $4.0** | 7.9h / $4.3 | 8.6h / $6.0 | 7.5h / $6.8 |
| m07 BiLSTM 30 ep | 45.0h | **28.1h / $7.0** | 19.6h / $7.8 | 17.3h / $9.5 | 18.8h / $13.1 | 16.7h / $15.0 |
| **Total 3 heavy** | **175.0h** | **97.4h / $24.4** | **59.9h / $24.0** | **50.2h / $27.6** | **53.0h / $37.1** | **46.4h / $41.8** |

Interpretasi:

- **RTX 4090 adalah pilihan paling seimbang**: hampir semurah 3090 tetapi jauh lebih cepat.
- **RTX 3090 bisa lebih murah untuk BiLSTM**, tetapi wall-clock lama.
- **RTX 5090 hanya menarik jika driver/PyTorch stabil** dan harga <=$0.55-0.60/h.
- **L40S/A100 tidak menang biaya**, tetapi menang VRAM/stability.
- Untuk deadline, 2x RTX 4090 biasanya lebih masuk akal daripada 1x A100, karena total cost mirip/rendah dan wall-clock paralel lebih pendek.

### 7.2 Jika Whisper yang dimaksud adalah Whisper-medium

Whisper-medium OOM di RTX 4060 8GB dan bukan paper primary slot. Jika user ingin medium sebagai appendix/secondary:

- Minimum aman: **RTX 4090 24GB** dengan batch kecil + gradient checkpointing.
- Lebih aman: **L40S 48GB** atau **A100 40GB**.
- Storage tambahan: `best_model/` + checkpoint HF medium sekitar 9-12 GB per final run.
- Jangan campur hasil medium ke 9-model paper utama kecuali protokol paper diubah dan aggregator dimutakhirkan.

---

## 8. Perhitungan semua 9 model paper

### 8.1 Sequential 1 GPU

| Model | Local baseline | RTX 4090 target | Cost @ $0.40/h | A100 target | Cost @ $0.90/h |
|---|---:|---:|---:|---:|---:|
| m08 HMM-GMM | 0.5h CPU | 0.5h CPU | ~$0 | 0.5h CPU | ~$0 |
| m09 DNN-HMM | 1.0h | 0.5h | $0.2 | 0.3h | $0.3 |
| m10 GMM-HMM-DNN | 2.0h | 1.0h | $0.4 | 0.7h | $0.6 |
| m11 Vanilla Transformer | 14.0h | 4.7h | $1.9 | 3.5h | $3.2 |
| m12 ViT-modified-ID | 14.0h | 4.7h | $1.9 | 3.5h | $3.2 |
| m13 Wav2Letter | 5.0h | 2.0h | $0.8 | 1.5h | $1.4 |
| m07 BiLSTM | 45.0h | 19.6h | $7.8 | 16.7h | $15.0 |
| m06 Conformer | 30.0h | 10.0h | $4.0 | 7.5h | $6.8 |
| m02b Whisper FT | 100.0h | 30.3h | $12.1 | 22.2h | $20.0 |
| **Total** | **211.5h** | **73.3h** | **~$29.1** | **55.9h** | **~$50.3** |

Tambahkan buffer 15-30% untuk setup, pip/conda, upload/download, failed smoke, idle time:

| Skenario | GPU-hour + buffer | Biaya planning |
|---|---:|---:|
| 1x RTX 4090 Vast/RunPod Community | 85-95h | ~$35-45 |
| 1x RTX 4090 RunPod Secure | 85-95h | ~$59-66 |
| 1x L40S | 65-80h | ~$45-70 |
| 1x A100 40GB | 65-75h | ~$60-100 |

### 8.2 Parallel 2 GPU

Best practical schedule:

| Lane | GPU | Jobs | Estimasi wall-clock |
|---|---|---|---:|
| GPU-1 | RTX 4090 / L40S | Whisper FT final | ~30h on 4090, ~22-26h on L40S/A100 |
| GPU-2 | RTX 4090 | m07, m06, m11, m12, m13, m09, m10 | ~42-45h |
| CPU/local | CPU | m08 + aggregation/test prep | <1h CPU |

Dengan 2x RTX 4090:

- Total GPU-hour mirip 1 GPU (~75-90 GPU-hour + overhead).
- Wall-clock turun dari ~3-4 hari menjadi ~2 hari.
- Biaya tidak naik banyak jika tidak ada idle lama.
- Risiko lebih rendah karena satu job gagal tidak menghentikan semua model.

### 8.3 Schedule prioritas jika hanya bisa satu GPU

Urutan terbaik:

1. Jalankan probe singkat semua heavy model.
2. Jalankan **m07 BiLSTM** dulu (paling lama dan resume belum nyaman).
3. Jalankan **m06 Conformer**.
4. Jalankan **Whisper** (resume sudah ada, jadi lebih aman belakangan).
5. Jalankan m11, m12, m13, m09, m10.
6. Jalankan m08 di CPU kapan saja.
7. Jalankan semua P3-T test dan aggregator sebelum stop instance.

---

## 9. Provider recommendation

### Vast.ai

Gunakan jika prioritas biaya paling murah.

Checklist host Vast:

- On-demand, bukan interruptible, untuk m06/m07 final.
- Reliability score >95%.
- Disk NVMe >=200 GB.
- RAM >=32 GB, lebih baik 64 GB.
- vCPU >=8, lebih baik 16-32.
- Upload/download bandwidth bagus.
- Simpan screenshot listing: GPU, harga, host reliability, disk, start UTC.

Kritik:

- Host variance besar: thermal throttling, disk lambat, network lambat.
- Data berada di community host; jangan gunakan jika dataset sensitif.
- Cocok untuk public/non-sensitive dataset dan checkpointed workflow.

### RunPod Community

Best default kalau ingin murah tetapi UI/template lebih nyaman daripada Vast.

- RTX 4090 community sekitar $0.34/h.
- L40S sekitar $0.79/h.
- A100 40GB sekitar $1.19/h.
- Persistent volume dan template PyTorch mudah.

Kritik:

- Community cloud tetap bukan enterprise SLA.
- Secure cloud lebih aman tapi 4090 bisa sekitar $0.69/h.

### RunPod Secure / Lambda / Paperspace

Gunakan jika:

- Dataset tidak boleh berada di host marketplace.
- Butuh reliability lebih tinggi.
- A100 final run untuk paper evidence lebih penting daripada biaya.

Kritik:

- Biaya lebih tinggi.
- Lambda umumnya tidak menyediakan 4090; fokus datacenter GPU.
- Paperspace/Colab lebih cocok notebook/prototyping, bukan 30-epoch final benchmark karena quota/session variance.

### RTX 5090 cloud

Use case:

- Harga dekat 4090.
- Butuh 32GB VRAM.
- Stack CUDA terbaru tersedia.

Wajib smoke test:

```bash
nvidia-smi
python3 - <<'PY'
import torch, torchaudio
print(torch.__version__, torch.version.cuda)
print(torch.cuda.get_device_name(0))
x=torch.randn(2048,2048,device='cuda')
print((x@x).mean().item())
PY
```

Jika error driver/CUDA/torchaudio muncul, jangan habiskan waktu; pindah 4090/L40S.

---

## 10. Cloud setup checklist

### 10.1 Instance spec

Minimum:

- 1 GPU: RTX 4090 24GB, atau L40S/A100 jika perlu.
- Disk: 200 GB NVMe.
- RAM: 32 GB minimum, 64 GB recommended.
- CPU: 8 vCPU minimum, 16+ recommended.
- Image: PyTorch CUDA image dengan Python 3.10/3.11.

### 10.2 Folder layout recommended

Agar default path trainer tetap bekerja:

```text
/workspace/
  Paper_Datatset_SOTA/                       # repo
  Processed_Balanced19_v7_natural_synth/
    Dataset_Balanced19/                      # raw wav dataset
  train_model_vanilla.py                     # parent script m11
  train_model_vit.py                         # parent script m12
  test_model_vanilla.py
  test_model_vit.py
```

Jika dataset ditempatkan di path lain, gunakan `--data-root` untuk trainer yang mendukungnya (Whisper, Conformer, BiLSTM). Untuk conventional feature builder, gunakan `--audio-root`.

### 10.3 Preflight commands

```bash
cd /workspace/Paper_Datatset_SOTA

git rev-parse HEAD
git status --short
nvidia-smi
python3 - <<'PY'
import torch, torchaudio, transformers
print('torch', torch.__version__, 'cuda', torch.version.cuda)
print('gpu', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu')
print('torchaudio', torchaudio.__version__)
print('transformers', transformers.__version__)
PY

wc -l training/data_final/train.tsv training/data_final/val.tsv training/data_final/test.tsv
# expected including header: 71793, 15377, 15377
```

Jika `training_conventional/data_pkl/` belum ada:

```bash
python3 training_conventional/common/spm_builder.py
python3 training_conventional/common/feature_builder.py
```

### 10.4 Monitoring

Jalankan di terminal terpisah:

```bash
mkdir -p cloud_logs
nvidia-smi --query-gpu=timestamp,name,utilization.gpu,utilization.memory,memory.used,memory.total,power.draw,temperature.gpu --format=csv -l 60 | tee cloud_logs/nvidia_smi_$(date +%Y%m%d_%H%M%S).csv
```

Catat juga:

```bash
df -h | tee cloud_logs/disk_start.txt
free -h | tee cloud_logs/ram_start.txt
pip freeze > cloud_logs/pip_freeze.txt
```

---

## 11. Probe plan sebelum final run

Probe harus diberi nama `run_cloud_probe_*` agar tidak tertukar dengan paper final.

### Whisper probe

```bash
python3 training/m02b_whisper_small_ft/train.py \
  --epochs 1 --batch-size 8 --grad-accum 4 \
  --lr 1e-5 --warmup-steps 10 \
  --gradient-checkpointing --seed 42 \
  --max-train-samples 2048 --max-val-samples 256
```

Untuk medium secondary:

```bash
python3 training/m02b_whisper_medium_ft/train.py \
  --epochs 1 --batch-size 2 --grad-accum 16 \
  --lr 1e-5 --warmup-steps 10 \
  --gradient-checkpointing --seed 42 \
  --max-train-samples 1024 --max-val-samples 128
```

### Conformer probe

```bash
python3 training/m06_conformer_ctc/train.py \
  --run-dir training/m06_conformer_ctc/runs/run_cloud_probe_$(date +%Y%m%d_%H%M%S) \
  --epochs 1 --batch-size 16 --grad-accum 2 \
  --hidden-size 256 --num-layers 6 --lr 3e-4 --seed 42 \
  --max-train-samples 2048 --max-val-samples 256
```

### BiLSTM probe

```bash
python3 training/m07_bilstm_ctc/train.py \
  --run-dir training/m07_bilstm_ctc/runs/run_cloud_probe_$(date +%Y%m%d_%H%M%S) \
  --epochs 1 --batch-size 16 --grad-accum 2 \
  --hidden-size 512 --num-layers 5 --lr 3e-4 --seed 42 \
  --max-train-samples 2048 --max-val-samples 256
```

Projection formula:

```text
projected_full_epoch_hours = measured_subset_epoch_hours * (71792 / subset_train_rows)
projected_full_run_cost = projected_full_epoch_hours * epoch_budget * gpu_hour_price
```

Kritik formula: subset tidak selalu linear karena validation overhead, dataloader warmup, dan sequence-length distribution. Gunakan probe hanya untuk OOM/utilization; untuk estimasi final yang lebih akurat, pakai waktu epoch pertama full run.

---

## 12. Final execution plan

### Option A - cheapest acceptable (1x RTX 4090)

1. Sewa 1x RTX 4090 on-demand, 200-300 GB NVMe.
2. Copy dataset ke local NVMe.
3. Jalankan probe heavy.
4. Jalankan m07 final.
5. Jalankan m06 final.
6. Jalankan Whisper final.
7. Jalankan m11/m12/m13/m09/m10.
8. Jalankan m08 di CPU.
9. Jalankan semua P3-T tests.
10. Jalankan `python3 aggregate_paper_test_results.py`.
11. Download final run dirs dan reports.

Estimasi: ~3-4 hari wall-clock termasuk setup/buffer, ~$35-50 pada marketplace murah.

### Option B - recommended fast-cheap (2x RTX 4090)

- GPU-1: Whisper final.
- GPU-2: m07 -> m06 -> m11 -> m12 -> m13 -> m09 -> m10.
- CPU/local: m08.

Estimasi: ~2 hari wall-clock, ~$40-70 tergantung idle/setup/provider.

### Option C - safer memory/reliability (4090 + L40S)

- L40S: Whisper-medium/Whisper-heavy atau Conformer jika 4090 OOM.
- 4090: BiLSTM dan model lain.

Estimasi: lebih mahal, tetapi risiko OOM lebih kecil.

### Option D - final defensible A100 run

Gunakan A100 40GB jika reviewer-grade reproducibility dan stability lebih penting daripada biaya.

- Pilih RunPod Secure/Lambda/Vast verified datacenter host.
- Simpan environment + billing + nvidia-smi evidence.
- Jangan gunakan H100 kecuali deadline ekstrem.

---

## 13. Evidence checklist untuk reviewer/paper

Global evidence:

- [ ] Provider, region, GPU, VRAM, CPU/RAM, disk type.
- [ ] Start UTC, stop UTC, billed GPU-hours, total cost screenshot.
- [ ] `git rev-parse HEAD`.
- [ ] `git status --short`.
- [ ] `nvidia-smi` output.
- [ ] PyTorch, CUDA, torchaudio, transformers versions.
- [ ] `pip freeze` / conda export.
- [ ] Dataset root path.
- [ ] Split counts: train/val/test = 71,792 / 15,376 / 15,376 rows excluding header.
- [ ] Hash TSV split files.
- [ ] Whether `data_pkl/` was transferred or rebuilt.

Per-model evidence:

- [ ] Exact command.
- [ ] Final resolved run directory.
- [ ] `config.json`, `meta.json`, `history.json`, `log.txt`.
- [ ] `Total waktu training: X jam, Y menit, Z detik` in log.
- [ ] `model_summary.png` / `.pdf` when generated.
- [ ] Best checkpoint path: `best.pt`, `best.pkl`, or Whisper `best_model/`.
- [ ] Best validation WER/CER and best epoch.
- [ ] Test output: `<run_dir>/test_results/test_paper.json`.
- [ ] Predictions CSV / summary markdown.
- [ ] Any interruption/resume notes.

Aggregator evidence:

- [ ] `reports/paper_benchmark/benchmark.json`.
- [ ] `reports/paper_benchmark/benchmark.md`.
- [ ] `reports/paper_benchmark/benchmark_table.csv`.
- [ ] `reports/paper_benchmark/paper_table.tex`.
- [ ] `n_paper_models_present == 9`.
- [ ] `missing_paper_models == []`.

---

## 14. Risiko dan kritik hasil analisis

### Risiko 1 - timing local tidak sepenuhnya GPU-bound

Whisper 20 jam/epoch di laptop RTX 4060 bisa disebabkan oleh:

- WSL `/mnt/c` I/O lambat.
- Audio decode CPU-bound.
- Dataloader worker kurang.
- Thermal throttling laptop.
- VRAM 8GB memaksa gradient checkpointing dan batch kecil.

Karena itu, speedup cloud bisa lebih besar dari estimasi jika data dipindah ke NVMe, tetapi bisa juga lebih kecil jika pipeline tetap CPU/I/O-bound.

### Risiko 2 - A100 belum tentu lebih murah

A100 40GB sering terlihat paling aman, tetapi pada harga $0.90-1.39/h harus >2.2-3.5x lebih cepat dari 4090 agar lebih murah. Untuk model ASR ukuran sedang, itu belum tentu terjadi. A100 dipilih untuk reliability, bukan default cost saving.

### Risiko 3 - BiLSTM tidak mendapat speedup besar dari GPU mahal

RNN sequential sering kurang memanfaatkan tensor cores dibanding Transformer/Conformer. BiLSTM mungkin tidak jauh lebih cepat di A100 dibanding 4090/3090. Untuk BiLSTM, RTX 3090/4090 adalah pilihan biaya terbaik.

### Risiko 4 - 5090 compatibility

5090 punya VRAM 32GB dan potensi speedup bagus, tetapi stack training ASR (PyTorch, torchaudio, CUDA, cuDNN) harus cocok. Jangan jadikan 5090 satu-satunya rencana final tanpa smoke test.

### Risiko 5 - marketplace host quality

Vast/Community host bisa punya:

- Disk lambat.
- CPU kecil.
- Thermal throttling.
- Network lambat.
- Interruption/reclaim.

Mitigasi: pilih host verified, on-demand, score tinggi, dan lakukan 10-15 menit utilization test.

### Risiko 6 - fairness paper

GPU besar tidak boleh digunakan untuk diam-diam menaikkan batch/epoch atau mengubah recipe. Jika batch berubah karena OOM, jaga effective batch via grad accumulation dan dokumentasikan.

---

## 15. Final recommendation

Untuk kebutuhan saat ini, rekomendasi paling kuat:

1. **Jalankan 2x RTX 4090 on-demand di RunPod Community atau Vast verified** selama 1-2 hari.
2. Pakai disk **300 GB NVMe** agar aman untuk raw audio, pkl, HF cache, final runs, dan probe.
3. Jika dataset dianggap sensitif, jangan pakai community marketplace; gunakan **RunPod Secure L40S/A100**.
4. Jika hanya satu GPU, pakai **1x RTX 4090** dan siapkan 3-4 hari wall-clock.
5. Jika Whisper-medium wajib masuk appendix dan 4090 OOM, gunakan **L40S 48GB** terlebih dahulu; A100 40GB hanya jika perlu stability/reproducibility final.
6. Jangan delete cloud instance sebelum semua P3-T test dan `aggregate_paper_test_results.py` selesai serta evidence diunduh.

Ringkas:

```text
Best cost/performance:  RTX 4090 24GB
Best cheap fallback:    RTX 3090 24GB (terutama BiLSTM, jika waktu longgar)
Best opportunistic:     RTX 5090 32GB (hanya setelah smoke test)
Best VRAM-safe:         L40S 48GB
Best reviewer-safe:     A100 40GB
Recommended disk:       300 GB NVMe
Minimum disk:           200 GB NVMe
Safe disk:              500 GB NVMe
```

---

## 16. Catatan Skills / GPT-5.5 compatibility

Analisis ini sengaja ditulis sebagai artifact Markdown mandiri agar dapat dibaca oleh agent/model generasi berikutnya (termasuk GPT-5.5/Codex-style agents) tanpa bergantung pada state percakapan. Struktur BMAD, Superpowers checklist, decision tables, dan evidence checklist dibuat eksplisit supaya skill/agent lain dapat melanjutkan eksekusi cloud training, review, atau paper-writing secara reproducible.
