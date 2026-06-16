# Test Results — m10-gmm-hmm-dnn

**Family**: GMM-HMM-DNN 3-stage
**Paper model**: yes
**User novel**: no

## Metrics (test set, n=15376, greedy decoding, no LM)

- **WER**: 0.9703
- **CER**: 0.8516
- **MER**: 0.9690
- **WIL**: 0.9965
- **SER**: 1.0000

## Performance

- Wall time: 18.9 s (0.3 min)
- Throughput: 815.12 samples/sec
- Peak GPU: 0 MB

## Checkpoint

- Path: `/mnt/c/Users/wayandadang/AI/Dataset ASR/Paper_Datatset_SOTA/training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/checkpoints/best.pkl`
- Best train WER (during training): 0.9783497661716014
- Best epoch: 15
- Total epochs trained: 30

## Sample predictions (10 evenly-spaced)

- `[0]`
  - PRED: `Jika kam tempat Palembang bisa berk.`
  - LABEL: `Saya membutuhkan rekomendasi tempat wisata di kota Palembang`
  - WER: 0.875 | CER: 0.717

- `[1708]`
  - PRED: `kamastik`
  - LABEL: `Bisakah kamu memastikan apakah ruang kelas yang saya tuju tersedia?`
  - WER: 1.000 | CER: 0.881

- `[3416]`
  - PRED: ``
  - LABEL: `Jika mereka menerapkan metode pengajaran yang interaktif, siswa akan lebih tertarik.`
  - WER: 1.000 | CER: 1.000

- `[5125]`
  - PRED: `al`
  - LABEL: `Apakah kamu sudah memeriksa apakah semua dokumen yang diperlukan sudah saya serahkan?"`
  - WER: 1.000 | CER: 0.977

- `[6833]`
  - PRED: `Jika kammasi kita di meng.`
  - LABEL: `Mahasiswa baru tidak diwajibkan mengenakan jas almamater setiap hari`
  - WER: 1.000 | CER: 0.794

- `[8541]`
  - PRED: `Jika kam sebe lebi ini.`
  - LABEL: `Robot, tolong jelaskan panduan keselamatan sebelum memulai praktikum di lab ini`
  - WER: 1.000 | CER: 0.772

- `[10250]`
  - PRED: `Jika kam l.`
  - LABEL: `Jangan ragu untuk bertanya pada guru jika ada yang tidak kamu mengerti, itu adalah langkah menuju pemahaman yang lebih baik`
  - WER: 0.950 | CER: 0.919

- `[11958]`
  - PRED: `Jika kam ber.`
  - LABEL: `Siapa yang akan menegakkan hukum jika aparat sendiri tidak memberikan contoh?`
  - WER: 0.909 | CER: 0.857

- `[13666]`
  - PRED: `Jika kam ke.`
  - LABEL: `Hebat, kamu berhasil lulus dengan predikat cumlaude!`
  - WER: 1.000 | CER: 0.846

- `[15375]`
  - PRED: `sua`
  - LABEL: `Bagaimana cara mengakses Wi-Fi kampus?`
  - WER: 1.000 | CER: 0.947


Full predictions in `predictions.csv`. Full JSON in `test_paper.json`.
