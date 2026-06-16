# Test Results — m11-vanilla-transformer

**Family**: Vanilla Transformer (Vaswani 2017)
**Paper model**: yes
**User novel**: no

## Metrics (test set, n=15376, greedy decoding, no LM)

- **WER**: 0.0439
- **CER**: 0.0327
- **MER**: 0.0438
- **WIL**: 0.0774
- **SER**: 0.0454

## Performance

- Wall time: 1293.3 s (21.6 min)
- Throughput: 11.89 samples/sec
- Peak GPU: 0 MB

## Checkpoint

- Path: `/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA/training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328/checkpoints/best.pth`
- Best train WER (during training): None
- Best epoch: None
- Total epochs trained: 0

## Sample predictions (10 evenly-spaced)

- `[0]`
  - PRED: `Saya membutuhkan rekomendasi tempat wisata di kota Palembang`
  - LABEL: `Saya membutuhkan rekomendasi tempat wisata di kota Palembang`
  - WER: 0.000 | CER: 0.000

- `[1708]`
  - PRED: `Bisakah kamu memastikan apakah ruang kelas yang saya tuju tersedia?`
  - LABEL: `Bisakah kamu memastikan apakah ruang kelas yang saya tuju tersedia?`
  - WER: 0.000 | CER: 0.000

- `[3416]`
  - PRED: `Jika mereka menerapkan metode pengajaran yang interaktif, siswa akan lebih tertarik.`
  - LABEL: `Jika mereka menerapkan metode pengajaran yang interaktif, siswa akan lebih tertarik.`
  - WER: 0.000 | CER: 0.000

- `[5125]`
  - PRED: `Apakah kamu sudah memeriksa apakah semua dokumen yang diperlukan sudah saya serahkan?"`
  - LABEL: `Apakah kamu sudah memeriksa apakah semua dokumen yang diperlukan sudah saya serahkan?"`
  - WER: 0.000 | CER: 0.000

- `[6833]`
  - PRED: `Mahasiswa baru tidak diwajibkan mengenakan jas almamater setiap hari`
  - LABEL: `Mahasiswa baru tidak diwajibkan mengenakan jas almamater setiap hari`
  - WER: 0.000 | CER: 0.000

- `[8541]`
  - PRED: `Robot, tolong jelaskan panduan keselamatan sebelum memulai praktikum di lab ini`
  - LABEL: `Robot, tolong jelaskan panduan keselamatan sebelum memulai praktikum di lab ini`
  - WER: 0.000 | CER: 0.000

- `[10250]`
  - PRED: `Jangan ragu untuk bertanya pada guru jika ada yang tidak kamu mengerti, itu adalah langkah menuju pemahaman yang lebih baik`
  - LABEL: `Jangan ragu untuk bertanya pada guru jika ada yang tidak kamu mengerti, itu adalah langkah menuju pemahaman yang lebih baik`
  - WER: 0.000 | CER: 0.000

- `[11958]`
  - PRED: `Siapa yang akan menegakkan hukum jika aparat sendiri tidak memberikan contoh?`
  - LABEL: `Siapa yang akan menegakkan hukum jika aparat sendiri tidak memberikan contoh?`
  - WER: 0.000 | CER: 0.000

- `[13666]`
  - PRED: `Hebat, kamu berhasil lulus dengan predikat cumlaude!`
  - LABEL: `Hebat, kamu berhasil lulus dengan predikat cumlaude!`
  - WER: 0.000 | CER: 0.000

- `[15375]`
  - PRED: `Bagaimana cara mengakses Wi-Fi kampus?`
  - LABEL: `Bagaimana cara mengakses Wi-Fi kampus?`
  - WER: 0.000 | CER: 0.000


Full predictions in `predictions.csv`. Full JSON in `test_paper.json`.
