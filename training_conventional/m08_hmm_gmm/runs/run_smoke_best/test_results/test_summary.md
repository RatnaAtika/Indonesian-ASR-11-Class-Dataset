# Test Results — m08-hmm-gmm

**Family**: HMM-GMM template classifier
**Paper model**: yes
**User novel**: no

## Metrics (test set, n=50, greedy decoding, no LM)

- **WER**: 1.1687
- **CER**: 0.8980
- **MER**: 0.9272
- **WIL**: 0.9932
- **SER**: 0.9400

## Performance

- Wall time: 0.5 s (0.0 min)
- Throughput: 92.09 samples/sec
- Peak GPU: 0 MB

## Checkpoint

- Path: `/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA/training_conventional/m08_hmm_gmm/runs/run_smoke_best/checkpoints/best.pkl`
- Best train WER (during training): 1.1687344913151365
- Best epoch: 1
- Total epochs trained: 1

## Sample predictions (10 evenly-spaced)

- `[0]`
  - PRED: `universitas sriwijaya adalah salah satu perguruan tinggi ternama di palembang.`
  - LABEL: `saya membutuhkan rekomendasi tempat wisata di kota palembang`
  - WER: 1.250 | CER: 0.933

- `[5]`
  - PRED: `universitas sriwijaya adalah salah satu perguruan tinggi ternama di palembang.`
  - LABEL: `semua makhluk hidup membutuhkan air untuk bertahan hidup`
  - WER: 1.250 | CER: 1.089

- `[10]`
  - PRED: `universitas sriwijaya adalah salah satu perguruan tinggi ternama di palembang.`
  - LABEL: `universitas sriwijaya adalah salah satu perguruan tinggi ternama di palembang.`
  - WER: 0.000 | CER: 0.000

- `[16]`
  - PRED: `universitas sriwijaya adalah salah satu perguruan tinggi ternama di palembang.`
  - LABEL: `transportasi lrt sangat membantu mobilitas warga`
  - WER: 1.667 | CER: 1.188

- `[21]`
  - PRED: `universitas sriwijaya adalah salah satu perguruan tinggi ternama di palembang.`
  - LABEL: `dosen pembimbing memberikan banyak masukan yang membangun.`
  - WER: 1.429 | CER: 1.000

- `[27]`
  - PRED: `universitas sriwijaya adalah salah satu perguruan tinggi ternama di palembang.`
  - LABEL: `saya percaya bahwa belajar adalah investasi jangka panjang`
  - WER: 1.250 | CER: 0.931

- `[32]`
  - PRED: `universitas sriwijaya adalah salah satu perguruan tinggi ternama di palembang.`
  - LABEL: `perpustakaan kampus menyediakan banyak referensi ilmiah`
  - WER: 1.667 | CER: 1.036

- `[38]`
  - PRED: `universitas sriwijaya adalah salah satu perguruan tinggi ternama di palembang.`
  - LABEL: `saya membutuhkan rekomendasi tempat wisata di kota palembang`
  - WER: 1.250 | CER: 0.933

- `[43]`
  - PRED: `universitas sriwijaya adalah salah satu perguruan tinggi ternama di palembang.`
  - LABEL: `semua makhluk hidup membutuhkan air untuk bertahan hidup`
  - WER: 1.250 | CER: 1.089

- `[49]`
  - PRED: `universitas sriwijaya adalah salah satu perguruan tinggi ternama di palembang.`
  - LABEL: `kampus menyediakan fasilitas laboratorium yang lengkap.`
  - WER: 1.667 | CER: 1.036


Full predictions in `predictions.csv`. Full JSON in `test_paper.json`.
