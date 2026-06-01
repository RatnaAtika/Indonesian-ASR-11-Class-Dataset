# Note Prompt Linux - Best Practice Training 3 Model Berat dari Ubuntu Native

Tujuan file ini: menjadi instruksi/prompt siap pakai saat laptop direstart ke Ubuntu native (dual OS) untuk menjalankan 3 model berat paper:

1. `m07_bilstm_ctc` - BiLSTM CTC, 30 epoch, estimasi lokal lama sekitar 1.5 jam/epoch.
2. `m06_conformer_ctc` - Conformer CTC, 30 epoch, estimasi lokal sekitar 30 jam total.
3. `m02b_whisper_small_ft` - Whisper-small fine-tuning, 5 epoch; jika yang berat adalah Whisper-medium, gunakan catatan medium di bawah.

Prinsip utama: **jangan training dari filesystem Windows/NTFS jika bisa dihindari**. Copy repo + dataset ke filesystem Ubuntu/ext4/NVMe supaya audio I/O lebih cepat dan lebih stabil. Opsi run langsung dari data Windows tetap disediakan sebagai fallback.

---

## 0. Prompt untuk AI agent di Ubuntu

Jika nanti membuka Codex/GPT agent dari Ubuntu, paste prompt ini:

```text
Kita sedang di Ubuntu native dual-boot, bukan WSL. Tugas: jalankan training 3 model berat paper Indonesian ASR dari repo Indonesian-ASR-11-Class-Dataset. Ikuti file note_prompt_linux.md. Prioritas: jangan overwrite hasil lama, pakai run_dir timestamp, data sebaiknya di ext4/NVMe lokal, verifikasi CUDA, verifikasi split count, jalankan probe kecil dulu, lalu final run m07 BiLSTM, m06 Conformer, dan m02b Whisper-small sesuai RUN_GUIDE.md. Semua output harus punya log.txt dengan Total waktu training, history.json, report.md, checkpoint/best_model, dan test_results/test_paper.json. Jangan ubah hyperparameter fairness kecuali untuk OOM; jika berubah, dokumentasikan. Setelah training tiap model, jalankan test.py dengan --run-dir yang benar.
```

---

## 1. Kenapa Ubuntu native lebih baik daripada Windows/WSL untuk training ini

- Native Ubuntu membaca file dari ext4 lebih cepat daripada WSL membaca banyak WAV kecil dari `/mnt/c`.
- Risiko Windows Update/sleep/Defender scanning lebih kecil.
- CUDA/PyTorch biasanya lebih stabil untuk long run Linux.
- Log, checkpoint, dan `runs/` lebih aman ditulis ke filesystem Linux.
- Untuk ASR, bottleneck sering audio loading + CPU + disk, bukan hanya GPU. Memindahkan dataset ke ext4 bisa memberi speedup besar tanpa mengubah model.

---

## 2. Best practice storage

### Opsi A - recommended: repo dan data di Ubuntu ext4/NVMe

Gunakan ini jika Ubuntu punya ruang disk minimal 150-200 GB. Rekomendasi aman: 250-300 GB.

Layout target:

```text
/home/$USER/asr/
  Paper_Datatset_SOTA/                         # repo clean
    Processed_Balanced19_v7_natural_synth/
      Dataset_Balanced19/                      # raw wav dataset
    training/data_final/                       # split TSV
    training/m07_bilstm_ctc/runs/              # hasil run Ubuntu
    training/m06_conformer_ctc/runs/
    training/m02b_whisper_small_ft/runs/
```

Keuntungan:

- Paling cepat dan stabil.
- Semua run ditulis ke ext4.
- Tidak bergantung pada mount NTFS Windows saat training berhari-hari.

### Opsi B - fallback: repo di Ubuntu, data tetap dibaca dari Windows C

Gunakan jika ruang Ubuntu kurang. Repo dan `runs/` tetap di ext4, tetapi `--data-root` diarahkan ke dataset di partisi Windows.

Konsekuensi:

- Lebih lambat karena banyak file WAV dibaca dari NTFS.
- Jangan mount Windows dalam kondisi hibernate/Fast Startup.
- Lebih baik mount read-only untuk data jika hanya membaca.

### Opsi C - tidak direkomendasikan: run langsung dari folder Windows/NTFS

Contoh `cd /media/$USER/Windows/Users/.../Paper_Datatset_SOTA` lalu training langsung. Ini bisa jalan, tetapi tidak disarankan karena:

- Write checkpoint/log ke NTFS lebih lambat.
- Banyak file kecil membuat I/O berat.
- Risiko permission/path/hibernation Windows lebih tinggi.

---

## 3. Sebelum boot ke Ubuntu: lakukan dari Windows

1. Matikan Windows Fast Startup:
   - Control Panel -> Power Options -> Choose what the power buttons do -> disable `Turn on fast startup`.
2. Jangan hibernate Windows sebelum masuk Ubuntu. Lakukan shutdown penuh.
3. Pastikan charger laptop terpasang.
4. Jika BIOS punya pilihan GPU mode/performance, pilih mode yang membuat NVIDIA GPU aktif.

---

## 4. Cek GPU dan driver di Ubuntu

Setelah masuk Ubuntu:

```bash
nvidia-smi
```

Harus terlihat GPU NVIDIA laptop (RTX 4060 atau GPU lain). Jika tidak:

```bash
ubuntu-drivers devices
sudo ubuntu-drivers autoinstall
sudo reboot
```

Opsional cek power/performance:

```bash
nvidia-smi -q | grep -E "Product Name|Driver Version|CUDA Version|Power"
```

Jangan ubah power limit jika tidak yakin. Untuk laptop, yang paling penting adalah charger terpasang dan mode performance aktif.

---

## 5. Setup environment Python/PyTorch

Jika sudah punya conda/mamba:

```bash
conda create -n torch-gpu python=3.10 -y
conda activate torch-gpu
python -m pip install --upgrade pip wheel setuptools
```

Install PyTorch CUDA. Pilih salah satu yang cocok dengan driver. Untuk banyak sistem Ubuntu modern, CUDA 12.1 wheel aman:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Install package ASR/research yang dibutuhkan:

```bash
pip install transformers datasets accelerate evaluate jiwer soundfile librosa sentencepiece torchinfo matplotlib pandas scikit-learn seaborn reportlab pillow tqdm
```

Verifikasi:

```bash
python3 - <<'PY'
import torch, torchaudio, transformers, soundfile, jiwer
print('torch:', torch.__version__)
print('cuda:', torch.version.cuda)
print('cuda_available:', torch.cuda.is_available())
print('gpu:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')
print('torchaudio:', torchaudio.__version__)
print('transformers:', transformers.__version__)
PY
```

Jika `torch.cuda.is_available()` False, jangan mulai training. Perbaiki driver/PyTorch dulu.

---

## 6. Temukan mount Windows C dari Ubuntu

Cari partisi Windows:

```bash
lsblk -f
```

Biasanya akan otomatis termount di salah satu path:

```bash
ls /media/$USER
ls /mnt
```

Contoh path umum:

```text
/media/$USER/Windows
/media/$USER/OS
/mnt/windows
```

Set variabel sesuai kondisi nyata:

```bash
export WIN_MOUNT="/media/$USER/Windows"
export WIN_REPO="$WIN_MOUNT/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
ls "$WIN_REPO"
```

Jika path tidak ada, cari:

```bash
find /media/$USER /mnt -maxdepth 5 -type d -name 'Paper_Datatset_SOTA' 2>/dev/null | head
```

---

## 7. Opsi A recommended: clone/copy ke ext4 Ubuntu

### 7.1 Buat folder kerja Ubuntu

```bash
mkdir -p "$HOME/asr"
cd "$HOME/asr"
```

### 7.2 Ambil repo clean dari GitHub

Jika internet tersedia:

```bash
git clone https://github.com/RatnaAtika/Indonesian-ASR-11-Class-Dataset.git Paper_Datatset_SOTA
cd Paper_Datatset_SOTA
git status --short
git rev-parse HEAD
```

Jika tidak ingin clone, copy kode dari Windows tapi exclude run lama:

```bash
mkdir -p "$HOME/asr/Paper_Datatset_SOTA"
rsync -aH --info=progress2 \
  --exclude '.git/' \
  --exclude '__pycache__/' \
  --exclude '*/runs/' \
  "$WIN_REPO/" "$HOME/asr/Paper_Datatset_SOTA/"
cd "$HOME/asr/Paper_Datatset_SOTA"
```

### 7.3 Copy raw dataset dan split TSV ke ext4

Jika repo hasil clone belum punya dataset lokal, copy dari Windows:

```bash
cd "$HOME/asr/Paper_Datatset_SOTA"

rsync -aH --info=progress2 \
  "$WIN_REPO/Processed_Balanced19_v7_natural_synth/" \
  "Processed_Balanced19_v7_natural_synth/"

rsync -aH --info=progress2 \
  "$WIN_REPO/training/data_final/" \
  "training/data_final/"
```

Opsional untuk nanti semua 9 model conventional:

```bash
rsync -aH --info=progress2 \
  "$WIN_REPO/training_conventional/data_pkl/" \
  "training_conventional/data_pkl/"

rsync -aH --info=progress2 \
  "$WIN_REPO/training_conventional/spm/" \
  "training_conventional/spm/"
```

### 7.4 Verifikasi dataset

```bash
cd "$HOME/asr/Paper_Datatset_SOTA"

wc -l training/data_final/train.tsv training/data_final/dev.tsv training/data_final/test.tsv
# expected termasuk header:
# 71793 train.tsv
# 15377 dev.tsv
# 15377 test.tsv

python3 - <<'PY'
import csv, pathlib
for split in ['train','dev','test']:
    p=pathlib.Path('training/data_final')/f'{split}.tsv'
    n=0; dur=0.0; missing=0
    with p.open(encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            n += 1
            dur += float(row.get('duration_sec') or 0)
            ap = pathlib.Path('Processed_Balanced19_v7_natural_synth/Dataset_Balanced19') / row['audio_path']
            if not ap.exists():
                missing += 1
    print(split, 'rows=', n, 'hours=', round(dur/3600,4), 'missing=', missing)
PY
```

Expected:

```text
train rows=71792 hours=92.4882 missing=0
dev   rows=15376 hours=19.7412 missing=0
test  rows=15376 hours=18.4254 missing=0
```

---

## 8. Opsi B fallback: repo ext4, data langsung dari Windows C

Jika tidak copy raw dataset ke Ubuntu, tetap jalankan repo dari ext4, tetapi arahkan `--data-root` ke Windows dataset.

Set variabel:

```bash
export REPO="$HOME/asr/Paper_Datatset_SOTA"
export WIN_MOUNT="/media/$USER/Windows"
export WIN_REPO="$WIN_MOUNT/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
export WIN_DATA="$WIN_REPO/Processed_Balanced19_v7_natural_synth/Dataset_Balanced19"
cd "$REPO"
ls "$WIN_DATA" | head
```

Verifikasi split terhadap data Windows:

```bash
python3 - <<'PY'
import csv, os, pathlib
root=pathlib.Path(os.environ['WIN_DATA'])
for split in ['train','dev','test']:
    p=pathlib.Path('training/data_final')/f'{split}.tsv'
    n=0; missing=0
    with p.open(encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            n += 1
            if not (root / row['audio_path']).exists():
                missing += 1
    print(split, n, 'missing=', missing)
PY
```

Saat training, tambahkan:

```bash
--data-root "$WIN_DATA" --data-final "$REPO/training/data_final"
```

---

## 9. Long-run safety: tmux, no sleep, logging

Install tmux jika belum ada:

```bash
sudo apt update
sudo apt install -y tmux nvtop htop rsync git
```

Cegah sleep selama training:

```bash
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

Setelah semua training selesai, bisa restore:

```bash
sudo systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

Buat folder log monitor:

```bash
cd "$HOME/asr/Paper_Datatset_SOTA"
mkdir -p ubuntu_logs
```

Monitor GPU di tmux session terpisah:

```bash
tmux new -s gpu_monitor
```

Di dalam tmux:

```bash
cd "$HOME/asr/Paper_Datatset_SOTA"
nvidia-smi --query-gpu=timestamp,name,utilization.gpu,utilization.memory,memory.used,memory.total,power.draw,temperature.gpu --format=csv -l 60 | tee ubuntu_logs/nvidia_smi_$(date +%Y%m%d_%H%M%S).csv
```

Detach tmux: tekan `Ctrl-b` lalu `d`.

Cek session:

```bash
tmux ls
tmux attach -t gpu_monitor
```

---

## 10. Environment variables recommended

```bash
export REPO="$HOME/asr/Paper_Datatset_SOTA"
cd "$REPO"

export CUDA_VISIBLE_DEVICES=0
export HF_HOME="$HOME/.cache/huggingface"
export TRANSFORMERS_CACHE="$HF_HOME/transformers"
export OMP_NUM_THREADS=$(nproc)
export MKL_NUM_THREADS=$(nproc)

mkdir -p "$HF_HOME" ubuntu_logs
```

Catat environment:

```bash
nvidia-smi | tee ubuntu_logs/nvidia_smi_start.txt
python3 - <<'PY' | tee ubuntu_logs/env_check.txt
import torch, torchaudio, transformers
print('torch', torch.__version__)
print('cuda', torch.version.cuda)
print('gpu', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')
print('torchaudio', torchaudio.__version__)
print('transformers', transformers.__version__)
PY
pip freeze > ubuntu_logs/pip_freeze_$(date +%Y%m%d_%H%M%S).txt
```

---

## 11. Probe kecil sebelum final run

Probe bertujuan cek CUDA, data path, VRAM, dan estimasi speed. Jangan pakai hasil probe untuk paper.

### 11.1 Probe BiLSTM

Opsi A data ext4:

```bash
cd "$REPO"
python3 training/m07_bilstm_ctc/train.py \
  --run-dir training/m07_bilstm_ctc/runs/run_ubuntu_probe_$(date +%Y%m%d_%H%M%S) \
  --epochs 1 --batch-size 16 --grad-accum 2 \
  --hidden-size 512 --num-layers 5 --lr 3e-4 --seed 42 \
  --max-train-samples 512 --max-val-samples 128 2>&1 | tee ubuntu_logs/probe_m07_$(date +%Y%m%d_%H%M%S).log
```

Opsi B data Windows C tambahkan:

```bash
  --data-root "$WIN_DATA" --data-final "$REPO/training/data_final"
```

### 11.2 Probe Conformer

```bash
cd "$REPO"
python3 training/m06_conformer_ctc/train.py \
  --run-dir training/m06_conformer_ctc/runs/run_ubuntu_probe_$(date +%Y%m%d_%H%M%S) \
  --epochs 1 --batch-size 16 --grad-accum 2 \
  --hidden-size 256 --num-layers 6 --lr 3e-4 --seed 42 \
  --max-train-samples 512 --max-val-samples 128 2>&1 | tee ubuntu_logs/probe_m06_$(date +%Y%m%d_%H%M%S).log
```

### 11.3 Probe Whisper-small

```bash
cd "$REPO"
python3 training/m02b_whisper_small_ft/train.py \
  --epochs 1 --batch-size 8 --grad-accum 4 \
  --lr 1e-5 --warmup-steps 10 \
  --gradient-checkpointing --seed 42 \
  --max-train-samples 512 --max-val-samples 128 2>&1 | tee ubuntu_logs/probe_m02b_small_$(date +%Y%m%d_%H%M%S).log
```

Jika OOM:

```bash
python3 training/m02b_whisper_small_ft/train.py \
  --epochs 1 --batch-size 4 --grad-accum 8 \
  --lr 1e-5 --warmup-steps 10 \
  --gradient-checkpointing --seed 42 \
  --max-train-samples 512 --max-val-samples 128 2>&1 | tee ubuntu_logs/probe_m02b_small_bs4_$(date +%Y%m%d_%H%M%S).log
```

Catatan fairness: batch-size boleh turun jika OOM, tetapi `batch_size * grad_accum` tetap efektif 32.

---

## 12. Final run 3 model berat - recommended sequential order

Laptop hanya punya satu GPU, jadi jangan jalankan tiga training berat paralel. Jalankan satu per satu.

Urutan recommended:

1. `m07` BiLSTM - panjang dan belum punya resume CLI nyaman.
2. `m06` Conformer - panjang dan belum punya resume CLI nyaman.
3. `m02b` Whisper-small - sudah punya `--resume`, jadi paling aman jika harus dilanjutkan.

Jika target utama mengejar Whisper dulu, boleh ubah urutan, tetapi catat alasannya.

---

## 13. Final run m07 BiLSTM CTC

Buka tmux:

```bash
tmux new -s train_m07
```

Opsi A data ext4:

```bash
conda activate torch-gpu
export REPO="$HOME/asr/Paper_Datatset_SOTA"
cd "$REPO"
mkdir -p ubuntu_logs

RUN_ID="run_paper_$(date +%Y%m%d_%H%M%S)_ubuntu"
RUN_DIR="training/m07_bilstm_ctc/runs/$RUN_ID"

time python3 training/m07_bilstm_ctc/train.py \
  --run-dir "$RUN_DIR" \
  --epochs 30 --batch-size 16 --grad-accum 2 \
  --hidden-size 512 --num-layers 5 --lr 3e-4 --seed 42 \
  2>&1 | tee "ubuntu_logs/train_m07_${RUN_ID}.log"

echo "$RUN_DIR" | tee ubuntu_logs/LAST_M07_RUN_DIR.txt
python3 training/m07_bilstm_ctc/test.py --run-dir "$RUN_DIR" 2>&1 | tee "ubuntu_logs/test_m07_${RUN_ID}.log"
```

Opsi B data Windows C: tambahkan sebelum `2>&1`:

```bash
  --data-root "$WIN_DATA" --data-final "$REPO/training/data_final" \
```

Verifikasi hasil:

```bash
grep -i "Total waktu training" "$RUN_DIR/log.txt"
ls "$RUN_DIR/test_results/test_paper.json"
```

---

## 14. Final run m06 Conformer CTC

```bash
tmux new -s train_m06
```

Di dalam tmux:

```bash
conda activate torch-gpu
export REPO="$HOME/asr/Paper_Datatset_SOTA"
cd "$REPO"
mkdir -p ubuntu_logs

RUN_ID="run_paper_$(date +%Y%m%d_%H%M%S)_ubuntu"
RUN_DIR="training/m06_conformer_ctc/runs/$RUN_ID"

time python3 training/m06_conformer_ctc/train.py \
  --run-dir "$RUN_DIR" \
  --epochs 30 --batch-size 16 --grad-accum 2 \
  --hidden-size 256 --num-layers 6 --lr 3e-4 --seed 42 \
  2>&1 | tee "ubuntu_logs/train_m06_${RUN_ID}.log"

echo "$RUN_DIR" | tee ubuntu_logs/LAST_M06_RUN_DIR.txt
python3 training/m06_conformer_ctc/test.py --run-dir "$RUN_DIR" 2>&1 | tee "ubuntu_logs/test_m06_${RUN_ID}.log"
```

Opsi B data Windows C: tambahkan sebelum `2>&1`:

```bash
  --data-root "$WIN_DATA" --data-final "$REPO/training/data_final" \
```

Verifikasi:

```bash
grep -i "Total waktu training" "$RUN_DIR/log.txt"
ls "$RUN_DIR/test_results/test_paper.json"
```

---

## 15. Final run m02b Whisper-small FT

Whisper wrapper sekarang otomatis membuat folder baru `runs/run_paper_<YYYYMMDD_HHMMSS>/` dan menyimpan best model ke `<run_dir>/best_model/`.

```bash
tmux new -s train_m02b
```

Di dalam tmux:

```bash
conda activate torch-gpu
export REPO="$HOME/asr/Paper_Datatset_SOTA"
cd "$REPO"
mkdir -p ubuntu_logs

RUN_TAG="$(date +%Y%m%d_%H%M%S)_ubuntu"

time python3 training/m02b_whisper_small_ft/train.py \
  --epochs 5 --batch-size 8 --grad-accum 4 \
  --lr 1e-5 --warmup-steps 500 \
  --gradient-checkpointing --seed 42 \
  2>&1 | tee "ubuntu_logs/train_m02b_small_${RUN_TAG}.log"

RUN_DIR=$(ls -dt training/m02b_whisper_small_ft/runs/run_paper_* | head -1)
echo "$RUN_DIR" | tee ubuntu_logs/LAST_M02B_SMALL_RUN_DIR.txt

python3 training/m02b_whisper_small_ft/test.py --run-dir "$RUN_DIR" 2>&1 | tee "ubuntu_logs/test_m02b_small_${RUN_TAG}.log"
```

Opsi B data Windows C: tambahkan ke train dan test command:

```bash
  --data-root "$WIN_DATA" --data-final "$REPO/training/data_final" \
```

Verifikasi:

```bash
grep -i "Total waktu training" "$RUN_DIR/log.txt"
ls "$RUN_DIR/best_model"
ls "$RUN_DIR/test_results/test_paper.json"
```

### Resume Whisper jika terputus

Jika training Whisper terputus:

```bash
cd "$REPO"
RUN_DIR=$(cat ubuntu_logs/LAST_M02B_SMALL_RUN_DIR.txt)
python3 training/m02b_whisper_small_ft/train.py \
  --run-dir "$RUN_DIR" --resume \
  --epochs 5 --batch-size 8 --grad-accum 4 \
  --lr 1e-5 --warmup-steps 500 \
  --gradient-checkpointing --seed 42 \
  2>&1 | tee "ubuntu_logs/resume_m02b_small_$(date +%Y%m%d_%H%M%S).log"
```

Jika OOM, gunakan effective batch tetap 32:

```bash
python3 training/m02b_whisper_small_ft/train.py \
  --run-dir "$RUN_DIR" --resume \
  --epochs 5 --batch-size 4 --grad-accum 8 \
  --lr 1e-5 --warmup-steps 500 \
  --gradient-checkpointing --seed 42
```

---

## 16. Jika yang ingin dilatih adalah Whisper-medium secondary

Whisper-medium bukan paper primary slot saat ini, tetapi bisa dilatih untuk appendix/secondary jika VRAM cukup.

Di RTX 4060 8GB kemungkinan besar OOM atau sangat lambat. Coba hanya jika siap risiko:

```bash
cd "$REPO"
time python3 training/m02b_whisper_medium_ft/train.py \
  --epochs 5 --batch-size 1 --grad-accum 32 \
  --lr 1e-5 --warmup-steps 500 \
  --gradient-checkpointing --seed 42 \
  2>&1 | tee "ubuntu_logs/train_m02b_medium_$(date +%Y%m%d_%H%M%S).log"
```

Kritik:

- Di laptop 8GB, medium tidak direkomendasikan untuk final karena OOM/time risk.
- Jika medium wajib, lebih baik L40S/A100 cloud seperti di `GPU_Cloud.md`.
- Jangan masukkan medium ke 9-model paper utama kecuali protokol paper diubah.

---

## 17. Setelah 3 model selesai

Cek semua test JSON:

```bash
cd "$REPO"
cat ubuntu_logs/LAST_M07_RUN_DIR.txt
cat ubuntu_logs/LAST_M06_RUN_DIR.txt
cat ubuntu_logs/LAST_M02B_SMALL_RUN_DIR.txt

for f in \
  "$(cat ubuntu_logs/LAST_M07_RUN_DIR.txt)/test_results/test_paper.json" \
  "$(cat ubuntu_logs/LAST_M06_RUN_DIR.txt)/test_results/test_paper.json" \
  "$(cat ubuntu_logs/LAST_M02B_SMALL_RUN_DIR.txt)/test_results/test_paper.json"; do
  echo "=== $f ==="
  test -f "$f" && python3 -m json.tool "$f" | head -40 || echo "MISSING"
done
```

Jika semua 9 model paper sudah ada, jalankan aggregator:

```bash
python3 aggregate_paper_test_results.py
python3 -m json.tool reports/paper_benchmark/benchmark.json | grep -E 'n_paper_models_present|missing_paper_models'
```

Expected:

```text
n_paper_models_present = 9
missing_paper_models = []
```

---

## 18. Copy hasil dari Ubuntu ke Windows setelah selesai

Jika ingin hasil tersedia di Windows:

```bash
export REPO="$HOME/asr/Paper_Datatset_SOTA"
export WIN_REPO="$WIN_MOUNT/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"

rsync -aH --info=progress2 \
  "$REPO/training/m07_bilstm_ctc/runs/" \
  "$WIN_REPO/training/m07_bilstm_ctc/runs/"

rsync -aH --info=progress2 \
  "$REPO/training/m06_conformer_ctc/runs/" \
  "$WIN_REPO/training/m06_conformer_ctc/runs/"

rsync -aH --info=progress2 \
  "$REPO/training/m02b_whisper_small_ft/runs/" \
  "$WIN_REPO/training/m02b_whisper_small_ft/runs/"

rsync -aH --info=progress2 \
  "$REPO/reports/paper_benchmark/" \
  "$WIN_REPO/reports/paper_benchmark/"
```

Jika Windows Fast Startup/hibernation belum dimatikan, jangan write ke NTFS. Copy ke external drive atau upload ke remote Git/GDrive/HF instead.

---

## 19. Git handling dari Ubuntu

Jangan commit checkpoint/model besar. `.gitignore` sudah dirancang agar checkpoint/runs berat tidak masuk git.

Cek sebelum commit:

```bash
cd "$REPO"
git status --short
```

Yang boleh dicommit:

- Markdown report kecil.
- Config/report kecil jika memang ingin disimpan.
- Aggregated benchmark reports.

Yang jangan dicommit:

- `best_model/`
- `checkpoints/`
- `.pt`, `.pth`, `.pkl` besar
- seluruh raw dataset

---

## 20. Troubleshooting cepat

### CUDA OOM

- Whisper-small: turunkan `--batch-size 8 --grad-accum 4` menjadi `--batch-size 4 --grad-accum 8`.
- Conformer/BiLSTM: turunkan `--batch-size 16 --grad-accum 2` menjadi `--batch-size 8 --grad-accum 4`.
- Effective batch tetap 32 agar fairness terjaga.

### Training lambat walau GPU ada

Cek:

```bash
nvidia-smi dmon -s pucm
htop
iostat -xz 5
```

Jika GPU util rendah:

- Pastikan data di ext4, bukan NTFS.
- Tutup aplikasi berat.
- Pastikan laptop tidak thermal throttle.
- Pastikan charger terpasang dan mode performance aktif.

### File missing

Cek path dataset:

```bash
ls "$REPO/Processed_Balanced19_v7_natural_synth/Dataset_Balanced19" | head
```

Jika pakai Windows data:

```bash
ls "$WIN_DATA" | head
```

### tmux terputus

Reconnect:

```bash
tmux ls
tmux attach -t train_m07
# atau
# tmux attach -t train_m06
# tmux attach -t train_m02b
```

---

## 21. Ringkasan perintah final paling aman

Jika data sudah dicopy ke Ubuntu ext4:

```bash
export REPO="$HOME/asr/Paper_Datatset_SOTA"
cd "$REPO"
conda activate torch-gpu
mkdir -p ubuntu_logs

# m07 BiLSTM
RUN_ID="run_paper_$(date +%Y%m%d_%H%M%S)_ubuntu"
RUN_DIR="training/m07_bilstm_ctc/runs/$RUN_ID"
time python3 training/m07_bilstm_ctc/train.py --run-dir "$RUN_DIR" --epochs 30 --batch-size 16 --grad-accum 2 --hidden-size 512 --num-layers 5 --lr 3e-4 --seed 42 2>&1 | tee "ubuntu_logs/train_m07_${RUN_ID}.log"
python3 training/m07_bilstm_ctc/test.py --run-dir "$RUN_DIR"

# m06 Conformer
RUN_ID="run_paper_$(date +%Y%m%d_%H%M%S)_ubuntu"
RUN_DIR="training/m06_conformer_ctc/runs/$RUN_ID"
time python3 training/m06_conformer_ctc/train.py --run-dir "$RUN_DIR" --epochs 30 --batch-size 16 --grad-accum 2 --hidden-size 256 --num-layers 6 --lr 3e-4 --seed 42 2>&1 | tee "ubuntu_logs/train_m06_${RUN_ID}.log"
python3 training/m06_conformer_ctc/test.py --run-dir "$RUN_DIR"

# m02b Whisper-small
RUN_TAG="$(date +%Y%m%d_%H%M%S)_ubuntu"
time python3 training/m02b_whisper_small_ft/train.py --epochs 5 --batch-size 8 --grad-accum 4 --lr 1e-5 --warmup-steps 500 --gradient-checkpointing --seed 42 2>&1 | tee "ubuntu_logs/train_m02b_small_${RUN_TAG}.log"
RUN_DIR=$(ls -dt training/m02b_whisper_small_ft/runs/run_paper_* | head -1)
python3 training/m02b_whisper_small_ft/test.py --run-dir "$RUN_DIR"
```

Jika data tetap di Windows C, tambahkan ke semua train/test command yang mendukung:

```bash
--data-root "$WIN_DATA" --data-final "$REPO/training/data_final"
```

Best practice final: **copy data ke Ubuntu ext4 dulu**, lalu training dari sana.
