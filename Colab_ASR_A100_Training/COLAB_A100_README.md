# Colab ASR A100 Training Prep

Tujuan: menjalankan training Whisper di Google Colab GPU A100 40 GB tanpa menggandakan dataset di repo lokal.

**Mulai dari sini:** baca `START_HERE_COLAB_A100_WHISPER.md` untuk instruksi lengkap end-to-end (verifikasi A100, bootstrap, paper-exact run, resume dari Drive, copy hasil ke Windows, dan checklist kritik/fix). File README ini hanya ringkasan.

## Struktur Google Drive yang disarankan

```text
MyDrive/ASR_Colab_A100/
  Colab_ASR_A100_Training/        # folder ini: notebook + scripts + repo_code
  Data/
    Processed_Balanced19_v7_natural_synth/
      Dataset_Balanced19/         # upload dataset v7 yang sudah ada, satu kali saja
    training/
      data_final/                 # train/dev/test TSV
  Results/                        # output training Colab disalin ke sini
```

## Prinsip anti-duplikasi dataset

- Jangan membuat copy dataset baru di Linux/Windows untuk staging.
- Upload dataset v7 yang sudah ada langsung ke Google Drive satu kali.
- Folder `repo_code/` di paket ini sengaja **tidak berisi WAV/checkpoint/model weight**.
- **Best practice wajib untuk A100:** set `USE_LOCAL_SSD=1`. Ini menyalin WAV dataset **dan split TSV** dari Drive ke SSD runtime Colab `/content` (umumnya ratusan GB, cukup untuk dataset ~15GB) agar training/test tidak membaca ribuan file kecil langsung dari Google Drive.
- Copy `/content` ini sementara, hilang saat runtime Colab mati, dan bukan duplikasi permanen di Drive.
- Gunakan Drive hanya sebagai sumber upload awal dan tujuan sinkronisasi hasil akhir.

## Upload ke Google Drive

Sebelum upload/sync, regenerasi snapshot code agar Drive memakai versi terbaru:

```bash
cd "/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA"
bash Colab_ASR_A100_Training/scripts/prepare_repo_code_snapshot.sh
```

`repo_code/` adalah snapshot lokal untuk Drive dan sengaja di-ignore dari git.

Jangan training langsung dari Drive kecuali darurat. Jika `USE_LOCAL_SSD=1`, bootstrap akan mengecek free space `/content` (default minimal 40 GiB), lalu copy dataset + TSV ke local SSD sebelum training.

**Cara tercepat:** buat/upload archive satu kali:

```bash
bash Colab_ASR_A100_Training/scripts/build_colab_data_archives.sh
rclone copy Colab_ASR_A100_Training/archives gdrive:ASR_Colab_A100/Data/_archives --progress --transfers 2 --checkers 4
```

Jika Drive berisi `Data/_archives/dataset_balanced19_v7.tar` dan `Data/_archives/data_final.tar`, bootstrap akan memakai archive itu (1 file besar) lalu extract ke `/content`; ini jauh lebih cepat daripada copy 104 ribu WAV kecil dari Drive.

### Opsi A — Web UI Google Drive

Upload folder ini ke:

```text
MyDrive/ASR_Colab_A100/Colab_ASR_A100_Training
```

Upload dataset existing dari Linux atau Windows ke:

```text
MyDrive/ASR_Colab_A100/Data/Processed_Balanced19_v7_natural_synth/Dataset_Balanced19
```

Upload split TSV ke:

```text
MyDrive/ASR_Colab_A100/Data/training/data_final
```

### Opsi B — rclone

Dari Linux:

```bash
cd ~/AI/Dataset_ASR_Train_Linux/Colab_ASR_A100_Training
scripts/upload_dataset_to_gdrive_rclone.sh --dry-run
scripts/upload_dataset_to_gdrive_rclone.sh
scripts/upload_colab_code_to_gdrive_rclone.sh
```

Syarat: remote rclone Google Drive sudah dikonfigurasi, default `gdrive:`.

## Jalankan di Colab

1. Buka `notebooks/ASR_Whisper_A100_Colab.ipynb` dari Google Drive.
2. Runtime → Change runtime type → pilih GPU A100.
3. Jalankan cell dari atas. Notebook sudah auto-detect lokasi package, baik layout flat `MyDrive/Colab_ASR_A100/{scripts,Data,...}` seperti screenshot maupun layout nested `MyDrive/ASR_Colab_A100/Colab_ASR_A100_Training/{scripts,...}`. Jika masih muncul `No such file or directory`, berarti folder package belum terupload lengkap atau `MANUAL_COLAB_ROOT` perlu diisi dengan path Drive yang tepat, misalnya `/content/drive/MyDrive/Colab_ASR_A100`.
4. Untuk paper model #9, jalankan Whisper-small **paper-exact** kecuali user eksplisit memilih A100-fast.
5. Whisper-medium tersedia sebagai secondary/appendix dan butuh A100.
6. Script training kini melakukan periodic sync run-dir/checkpoint ke Drive (default tiap 10 menit) dan final sync saat exit, agar runtime disconnect tidak menghapus semua progress.

## Profile training

### Paper-exact

Mengikuti RUN_GUIDE: `batch-size 8`, `grad-accum 4`, effective batch 32, gradient checkpointing aktif.

### A100-fast

Default script A100 memakai effective batch tetap 32, tetapi menaikkan per-device batch agar A100 lebih penuh:

- Whisper-small: `batch-size 32`, `grad-accum 1`, effective batch 32.
- Whisper-medium: `batch-size 8`, `grad-accum 4`, effective batch 32.

Jika OOM, turunkan `A100_BATCH_SIZE` dan naikkan `A100_GRAD_ACCUM` agar effective batch tetap 32.

## Hasil

Script training otomatis menjalankan `test.py`, melakukan periodic sync selama training, menulis **total akumulasi waktu training** ke `log.txt` dan `report.md`, lalu menyalin **seluruh run-dir lengkap** ke Google Drive, termasuk `best_model/`, `checkpoints/`, `model_summary.png/.pdf`, `report.md`, `history.json`, `log.txt`, dan `test_results/`.

```text
MyDrive/ASR_Colab_A100/Results/<model>/<run_name>/
```

Run Colab diberi label:

```text
run_paper_<YYYYMMDD_HHMMSS>_colab_a100
```

Setelah final sync, script training otomatis membuat summary paper-ready. Notebook juga punya cell **Paper-ready training time and metric summary** untuk re-check manual. Keduanya membaca `log.txt`, `report.md`, dan `test_results/test_paper.json`, lalu menulis:

```text
MyDrive/ASR_Colab_A100/Results/paper_training_time_summary.md
MyDrive/ASR_Colab_A100/Results/paper_training_time_summary.json
```

Auto-disconnect runtime Colab setelah semua proses selesai bersifat opsional. Set di notebook sebelum bootstrap:

```python
os.environ['A100_AUTO_DISCONNECT'] = '1'
```

Jika `A100_AUTO_DISCONNECT=1`, runtime baru di-unassign setelah training, testing, final sync, dan summary selesai.
