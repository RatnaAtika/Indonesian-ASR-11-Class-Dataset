# Test Results — m02b-whisper-small-ft

**Family**: Whisper-small FT (Radford 2022)
**Paper model**: yes
**User novel**: no

## Metrics (test set, n=15376, greedy decoding, no LM)

- **WER**: 0.0085
- **CER**: 0.0019
- **MER**: 0.0085
- **WIL**: 0.0130
- **SER**: 0.0390

## Performance

- Wall time: 4363.1 s (72.7 min)
- Throughput: 3.52 samples/sec
- Peak GPU: 549 MB

## Checkpoint

- Path: `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/best_model`
- Best train WER (during training): 0.0014584453561774
- Best epoch: 5
- Total epochs trained: 5

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
