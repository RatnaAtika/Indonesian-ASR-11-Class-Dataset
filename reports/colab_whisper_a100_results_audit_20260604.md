# Audit Hasil Colab A100 Whisper-small

Generated: 2026-06-04T20:31:30

## Ringkasan keputusan

- **Status ekstraksi**: 11 file ZIP sudah diekstrak dan ZIP sumber sudah dihapus; tidak ada `.zip` tersisa di `Colab_ASR_A100_Training/results/`.
- **Run final yang dipakai**: `run_paper_20260604_005100_colab_a100_paper_exact`.
- **Run lama/incomplete**: `run_paper_20260603_160446_colab_a100_paper_exact` ada tetapi **jangan dipakai** karena summary menunjukkan `MISSING` untuk total/WER/CER.
- **Kesimpulan**: data final **lengkap dan bisa dipakai** untuk tahap paper benchmark/analisis lanjutan.

## Lokasi hasil lokal

- Root hasil ekstraksi: `Colab_ASR_A100_Training/results/Results`
- Run final: `Colab_ASR_A100_Training/results/Results/m02b_whisper_small_ft/run_paper_20260604_005100_colab_a100_paper_exact`
- Ukuran run final: 19.84 GiB (88 file)
- Sisa ZIP: 0

## Metrik utama

- Model: `m02b-whisper-small-ft` — Whisper-small FT (Radford 2022)
- Full test set: 15376 samples
- Predictions CSV rows: 15376
- WER: **0.008523540683**
- CER: **0.001857029544**
- MER: 0.008521288542
- WIL: 0.012964770865
- SER: 0.038956815817
- Test wall time: 4363.1 s (72.7 min)
- Test throughput: 3.52 samples/s

## Training

- Epochs: 5
- Batch/grad accumulation: 8 × 4 = effective 32
- LR/warmup: 1e-05 / 500
- Gradient checkpointing: True
- FP16: True
- Device: NVIDIA A100-SXM4-40GB
- Total training time: **04:48:29 / 4 jam, 48 menit, 29 detik**
- Best validation WER: 0.001458445356 at epoch 5
- Best validation CER: 0.001067459260

## Kelengkapan artefak

| Item | Path | Status | Size |
|---|---|---:|---:|
| HF best model | `best_model/model.safetensors` | OK | 966,995,080 bytes |
| HF config | `best_model/config.json` | OK | 1,302 bytes |
| HF generation config | `best_model/generation_config.json` | OK | 4,592 bytes |
| HF tokenizer | `best_model/tokenizer.json` | OK | 3,931,230 bytes |
| HF tokenizer config | `best_model/tokenizer_config.json` | OK | 2,100 bytes |
| HF processor config | `best_model/processor_config.json` | OK | 409 bytes |
| Best model info | `best_model/BEST_INFO.txt` | OK | 259 bytes |
| Test JSON | `test_results/test_paper.json` | OK | 8,333 bytes |
| Predictions CSV | `test_results/predictions.csv` | OK | 2,996,816 bytes |
| Test summary | `test_results/test_summary.md` | OK | 2,846 bytes |
| Training history | `history.json` | OK | 2,718 bytes |
| Training log | `log.txt` | OK | 6,984 bytes |
| Training report | `report.md` | OK | 1,222 bytes |
| Model summary PNG | `model_summary.png` | OK | 119,964 bytes |
| Model summary PDF | `model_summary.pdf` | OK | 22,135 bytes |
| Metadata | `meta.json` | OK | 2,466 bytes |
| Training config | `config.json` | OK | 586 bytes |
| Loss plot | `plots/loss.png` | OK | 63,347 bytes |
| WER/CER plot | `plots/wer_cer.png` | OK | 59,518 bytes |

## Checkpoint dan model

- `best_model/model.safetensors`: 922.2 MiB
- HF-loadable path: `Colab_ASR_A100_Training/results/Results/m02b_whisper_small_ft/run_paper_20260604_005100_colab_a100_paper_exact/best_model`
- Epoch checkpoint dirs: checkpoint-11220, checkpoint-2244, checkpoint-4488, checkpoint-6732, checkpoint-8976
- Best `.pt` files: best.pt, best_wer0p0015_e004.pt, best_wer0p0015_e005.pt, best_wer0p0016_e003.pt, best_wer0p0022_e002.pt, best_wer0p0028_e001.pt

## Kecocokan untuk tahap selanjutnya

### Bisa langsung dipakai

1. **Paper Table / benchmark**: `test_results/test_paper.json` sudah lengkap dengan WER/CER/MER/WIL/SER, n=15,376, sample predictions, path predictions CSV, dan metadata checkpoint.
2. **Testing ulang / inference**: `best_model/` sudah berisi model HF (`model.safetensors`, tokenizer, processor, config).
3. **Bukti training**: `history.json`, `log.txt`, `report.md`, `plots/`, dan `model_summary.*` lengkap.
4. **Paper narrative**: hasil valid untuk slot paper #9 `m02b-whisper-small-ft` karena memakai Whisper-small, 5 epoch, effective batch 32, seed 42, full v7 test split.

### Belum otomatis terbaca aggregator lokal

Aggregator `aggregate_paper_test_results.py` mencari run di:

`training/m02b_whisper_small_ft/runs/`

Sedangkan hasil ini sekarang ada di:

`Colab_ASR_A100_Training/results/Results/m02b_whisper_small_ft/...`

Jadi untuk tahap aggregate 9-model, pilih salah satu:

**Opsi hemat disk (disarankan): buat symlink run final ke lokasi canonical.**

```bash
mkdir -p training/m02b_whisper_small_ft/runs
ln -s "../../../Colab_ASR_A100_Training/results/Results/m02b_whisper_small_ft/run_paper_20260604_005100_colab_a100_paper_exact" \
  "training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact"
python3 aggregate_paper_test_results.py
```

**Opsi tanpa symlink: copy folder run final.** Ini memakan sekitar 20 GiB tambahan, jadi kurang disarankan.

## Rekomendasi

- Pakai `run_paper_20260604_005100_colab_a100_paper_exact` sebagai hasil resmi Whisper-small paper #9.
- Jangan pakai run `20260603_160446` karena incomplete.
- Untuk menghemat disk, jangan duplikasi folder 20 GiB; gunakan symlink ke lokasi canonical saat ingin menjalankan aggregator.
- Jika hanya butuh model untuk inference/test ulang, cukup gunakan folder `best_model/`.
