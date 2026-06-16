# Test Results — m08-hmm-gmm

**Family**: HMM-GMM template classifier
**Paper model**: yes
**User novel**: no

## Metrics (test set, n=15376, greedy decoding, no LM)

- **WER**: 0.9633
- **CER**: 0.7205
- **MER**: 0.8789
- **WIL**: 0.9822
- **SER**: 0.9192

## Performance

- Wall time: 3277.3 s (54.6 min)
- Throughput: 4.69 samples/sec
- Peak GPU: 0 MB

## Checkpoint

- Path: `training_conventional/m08_hmm_gmm/runs/run_paper_20260530/checkpoints/best.pkl`
- Best train WER (during training): 1.0236177694899824
- Best epoch: 1
- Total epochs trained: 1

## Sample predictions (10 evenly-spaced)

- `[0]`
  - PRED: `mahasiswa tidak diperbolehkan membawa kendaraan ke area fakultas.`
  - LABEL: `saya membutuhkan rekomendasi tempat wisata di kota palembang`
  - WER: 1.000 | CER: 0.750

- `[1708]`
  - PRED: `tolong siapkan agenda rapat harian setiap pagi`
  - LABEL: `bisakah kamu memastikan apakah ruang kelas yang saya tuju tersedia?`
  - WER: 1.000 | CER: 0.731

- `[3416]`
  - PRED: `tolong pastikan apakah instruksi yang saya berikan sudah dilaksanakan`
  - LABEL: `jika mereka menerapkan metode pengajaran yang interaktif, siswa akan lebih tertarik.`
  - WER: 0.909 | CER: 0.762

- `[5125]`
  - PRED: `tolong pastikan apakah instruksi yang saya berikan sudah dilaksanakan`
  - LABEL: `apakah kamu sudah memeriksa apakah semua dokumen yang diperlukan sudah saya serahkan?"`
  - WER: 0.833 | CER: 0.593

- `[6833]`
  - PRED: `ya ampun, masih banyak mahasiswa yang belum paham konsep dasar ini!`
  - LABEL: `mahasiswa baru tidak diwajibkan mengenakan jas almamater setiap hari`
  - WER: 1.222 | CER: 0.721

- `[8541]`
  - PRED: `bergabunglah dalam program penghijauan kota, mari kita buat palembang semakin hijau dan nyaman untuk ditinggali!`
  - LABEL: `robot, tolong jelaskan panduan keselamatan sebelum memulai praktikum di lab ini`
  - WER: 1.364 | CER: 1.025

- `[10250]`
  - PRED: `coba deh, ikut program magang di perusahaan ini, banyak pengalaman berharga yang bisa kamu pelajari.`
  - LABEL: `jangan ragu untuk bertanya pada guru jika ada yang tidak kamu mengerti, itu adalah langkah menuju pemahaman yang lebih baik`
  - WER: 1.000 | CER: 0.715

- `[11958]`
  - PRED: `saya ingin berkontribusi untuk kemajuan kota palembang melalui pendidikan`
  - LABEL: `siapa yang akan menegakkan hukum jika aparat sendiri tidak memberikan contoh?`
  - WER: 1.000 | CER: 0.766

- `[13666]`
  - PRED: `tunjukkan dimana penghapus papan tulis berada !`
  - LABEL: `hebat, kamu berhasil lulus dengan predikat cumlaude!`
  - WER: 1.000 | CER: 0.769

- `[15375]`
  - PRED: `bisa kamu pastikan apakah pintu garasi sudah tertutup dengan baik?`
  - LABEL: `bagaimana cara mengakses wi-fi kampus?`
  - WER: 2.000 | CER: 1.263


Full predictions in `predictions.csv`. Full JSON in `test_paper.json`.
