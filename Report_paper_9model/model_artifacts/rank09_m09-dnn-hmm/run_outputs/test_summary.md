# Test Results — m09-dnn-hmm

**Family**: DNN-HMM hybrid
**Paper model**: yes
**User novel**: no

## Metrics (test set, n=15376, greedy decoding, no LM)

- **WER**: 0.9708
- **CER**: 0.8437
- **MER**: 0.9693
- **WIL**: 0.9967
- **SER**: 1.0000

## Performance

- Wall time: 19.7 s (0.3 min)
- Throughput: 778.66 samples/sec
- Peak GPU: 0 MB

## Checkpoint

- Path: `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/checkpoints/best.pkl`
- Best train WER (during training): 0.9717056625382678
- Best epoch: 12
- Total epochs trained: 30

## Sample predictions (10 evenly-spaced)

- `[0]`
  - PRED: `Jkah kamu tempat Palembang bisa?`
  - LABEL: `Saya membutuhkan rekomendasi tempat wisata di kota Palembang`
  - WER: 0.875 | CER: 0.733

- `[1708]`
  - PRED: `memkah`
  - LABEL: `Bisakah kamu memastikan apakah ruang kelas yang saya tuju tersedia?`
  - WER: 1.000 | CER: 0.910

- `[3416]`
  - PRED: `hari?`
  - LABEL: `Jika mereka menerapkan metode pengajaran yang interaktif, siswa akan lebih tertarik.`
  - WER: 1.000 | CER: 0.952

- `[5125]`
  - PRED: `u se di?`
  - LABEL: `Apakah kamu sudah memeriksa apakah semua dokumen yang diperlukan sudah saya serahkan?"`
  - WER: 1.000 | CER: 0.907

- `[6833]`
  - PRED: `Apakah kamumasi kitaidak mengen?`
  - LABEL: `Mahasiswa baru tidak diwajibkan mengenakan jas almamater setiap hari`
  - WER: 1.000 | CER: 0.750

- `[8541]`
  - PRED: `Apakah kamuebi ini?`
  - LABEL: `Robot, tolong jelaskan panduan keselamatan sebelum memulai praktikum di lab ini`
  - WER: 1.000 | CER: 0.823

- `[10250]`
  - PRED: `Jika kamu?`
  - LABEL: `Jangan ragu untuk bertanya pada guru jika ada yang tidak kamu mengerti, itu adalah langkah menuju pemahaman yang lebih baik`
  - WER: 0.950 | CER: 0.927

- `[11958]`
  - PRED: `Jkah kamu ber?`
  - LABEL: `Siapa yang akan menegakkan hukum jika aparat sendiri tidak memberikan contoh?`
  - WER: 1.000 | CER: 0.857

- `[13666]`
  - PRED: `Apakah kamuengan?`
  - LABEL: `Hebat, kamu berhasil lulus dengan predikat cumlaude!`
  - WER: 1.000 | CER: 0.788

- `[15375]`
  - PRED: `a sesua kampus?`
  - LABEL: `Bagaimana cara mengakses Wi-Fi kampus?`
  - WER: 0.800 | CER: 0.658


Full predictions in `predictions.csv`. Full JSON in `test_paper.json`.
