# Test Results — m13-wav2letter

**Family**: Wav2Letter CNN-CTC
**Paper model**: yes
**User novel**: no

## Metrics (test set, n=15376, greedy decoding, no LM)

- **WER**: 0.0929
- **CER**: 0.0520
- **MER**: 0.0920
- **WIL**: 0.1524
- **SER**: 0.2822

## Performance

- Wall time: 22.9 s (0.4 min)
- Throughput: 672.19 samples/sec
- Peak GPU: 194 MB

## Checkpoint

- Path: `/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA/training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/checkpoints/best.pt`
- Best train WER (during training): 0.07194719956538018
- Best epoch: 27
- Total epochs trained: 30

## Sample predictions (10 evenly-spaced)

- `[0]`
  - PRED: `Saya membutuhkan rekomendasi tempat wisata di kota Palembang`
  - LABEL: `Saya membutuhkan rekomendasi tempat wisata di kota Palembang`
  - WER: 0.000 | CER: 0.000

- `[1708]`
  - PRED: `Bisakah kamu memperjelas apa ruang kelas yang saya cari tersedia?`
  - LABEL: `Bisakah kamu memastikan apakah ruang kelas yang saya tuju tersedia?`
  - WER: 0.300 | CER: 0.209

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
  - PRED: `Siapa yaung bertanggugakkan hukum jika aparat sendiri tidak memberikan contoh?`
  - LABEL: `Siapa yang akan menegakkan hukum jika aparat sendiri tidak memberikan contoh?`
  - WER: 0.273 | CER: 0.130

- `[13666]`
  - PRED: `Hebat, kamu berhasil lulus dengan predikat cumlaude!`
  - LABEL: `Hebat, kamu berhasil lulus dengan predikat cumlaude!`
  - WER: 0.000 | CER: 0.000

- `[15375]`
  - PRED: `Bagaimana cara mengakses Wi-Fi kampus?`
  - LABEL: `Bagaimana cara mengakses Wi-Fi kampus?`
  - WER: 0.000 | CER: 0.000


Full predictions in `predictions.csv`. Full JSON in `test_paper.json`.
