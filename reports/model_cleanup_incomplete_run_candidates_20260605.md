# Laporan kandidat hapus run training tidak selesai / non-final

Status: laporan audit saja; belum ada penghapusan dieksekusi.
Scope: hanya 9 folder model benchmark; tidak menyentuh Report_paper_9model*, Dataset_Ori, Processed_Balanced19*, atau folder dataset besar.

## Ringkasan

- Total folder run yang ditemukan pada 9 model: 80
- Folder final yang wajib disimpan: 9 (29.0 GB)
- Kandidat hapus tahap ini: 51 (5.6 GB)
- Completed old non-final yang sengaja belum dimasukkan kandidat: 20 (17.8 GB)

## Kandidat hapus per model

| Model | Kandidat | Est. reclaim |
|---|---:|---:|
| m02b-whisper-small-ft | 1 | 153.9 KB |
| m06-conformer-ctc | 2 | 564.4 MB |
| m07-bilstm-ctc | 12 | 1.2 GB |
| m08-hmm-gmm | 4 | 1.6 MB |
| m09-dnn-hmm | 6 | 20.6 MB |
| m10-gmm-hmm-dnn | 2 | 3.4 MB |
| m11-vanilla-transformer | 11 | 47.2 MB |
| m12-vit-modified-ID | 8 | 51.6 MB |
| m13-wav2letter | 5 | 3.7 GB |

## Folder final yang harus disimpan

- `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact` — 119 B
- `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux` — 4.7 GB
- `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux` — 13.5 GB
- `training_conventional/m08_hmm_gmm/runs/run_paper_20260530` — 22.9 MB
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634` — 52.7 MB
- `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736` — 41.5 MB
- `training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328` — 62.1 MB
- `training_conventional/m12_vit_modified/runs/run_full_20260528_223323` — 51.1 MB
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637` — 10.7 GB

## Detail kandidat hapus

### m02b-whisper-small-ft
- `training/m02b_whisper_small_ft/runs/run_paper_20260601_100348` — 153.9 KB — tidak ada checkpoint/report/test_paper evidence

### m06-conformer-ctc
- `training/m06_conformer_ctc/runs/run_paper_20260601` — 380.6 MB — terindikasi interrupted/short run (2 epoch evidence)
- `training/m06_conformer_ctc/runs/run_smoke_2ep` — 183.7 MB — smoke/debug/test run; bukan artefak benchmark final

### m07-bilstm-ctc
- `training/m07_bilstm_ctc/runs/run_full_20260525` — 11.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training/m07_bilstm_ctc/runs/run_full_20260525_121542` — 11.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training/m07_bilstm_ctc/runs/run_full_20260525_122317` — 11.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training/m07_bilstm_ctc/runs/run_full_20260525_123247` — 11.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training/m07_bilstm_ctc/runs/run_full_20260525_141349` — 11.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training/m07_bilstm_ctc/runs/run_full_20260525_154119` — 376.0 MB — tidak ada checkpoint/report/test_paper evidence
- `training/m07_bilstm_ctc/runs/run_smoke_2ep` — 150.7 MB — smoke/debug/test run; bukan artefak benchmark final
- `training/m07_bilstm_ctc/runs/run_smoke_acc` — 151.9 MB — smoke/debug/test run; bukan artefak benchmark final
- `training/m07_bilstm_ctc/runs/run_smoke_best` — 202.0 MB — smoke/debug/test run; bukan artefak benchmark final
- `training/m07_bilstm_ctc/runs/run_smoke_chk` — 200.8 MB — smoke/debug/test run; bukan artefak benchmark final
- `training/m07_bilstm_ctc/runs/run_smoke_grad_accum` — 75.5 MB — smoke/debug/test run; bukan artefak benchmark final
- `training/m07_bilstm_ctc/runs/run_smoke_progress` — 75.5 MB — smoke/debug/test run; bukan artefak benchmark final

### m08-hmm-gmm
- `training_conventional/m08_hmm_gmm/runs/run_smoke` — 201.4 KB — smoke/debug/test run; bukan artefak benchmark final
- `training_conventional/m08_hmm_gmm/runs/run_smoke_acc` — 1.0 MB — smoke/debug/test run; bukan artefak benchmark final
- `training_conventional/m08_hmm_gmm/runs/run_test_uniq` — 160.6 KB — smoke/debug/test run; bukan artefak benchmark final
- `training_conventional/m08_hmm_gmm/runs/run_test_uniq_162411` — 167.5 KB — smoke/debug/test run; bukan artefak benchmark final

### m09-dnn-hmm
- `training_conventional/m09_dnn_hmm/runs/run_debug` — 3.1 MB — smoke/debug/test run; bukan artefak benchmark final
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260529` — 7.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training_conventional/m09_dnn_hmm/runs/run_paper_20260529_152145` — 11.3 MB — terindikasi interrupted/short run (1 epoch evidence)
- `training_conventional/m09_dnn_hmm/runs/run_smoke` — 203.4 KB — smoke/debug/test run; bukan artefak benchmark final
- `training_conventional/m09_dnn_hmm/runs/run_smoke_dbg` — 6.1 MB — smoke/debug/test run; bukan artefak benchmark final
- `training_conventional/m09_dnn_hmm/runs/run_smoke_perep` — 11.0 KB — smoke/debug/test run; bukan artefak benchmark final

### m10-gmm-hmm-dnn
- `training_conventional/m10_gmm_hmm_dnn/runs/run_smoke` — 203.6 KB — smoke/debug/test run; bukan artefak benchmark final
- `training_conventional/m10_gmm_hmm_dnn/runs/run_smoke_dbg` — 3.2 MB — smoke/debug/test run; bukan artefak benchmark final

### m11-vanilla-transformer
- `training_conventional/m11_vanilla_transformer/runs/run_full_20260528_220140` — 8.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training_conventional/m11_vanilla_transformer/runs/run_full_20260528_220211` — 8.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training_conventional/m11_vanilla_transformer/runs/run_full_20260528_220243` — 8.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training_conventional/m11_vanilla_transformer/runs/run_full_20260529_035856` — 154.8 KB — tidak ada checkpoint/report/test_paper evidence
- `training_conventional/m11_vanilla_transformer/runs/run_full_20260529_041459` — 8.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training_conventional/m11_vanilla_transformer/runs/run_full_20260529_041527` — 8.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training_conventional/m11_vanilla_transformer/runs/run_full_20260529_041544` — 8.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training_conventional/m11_vanilla_transformer/runs/run_full_20260529_041614` — 8.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training_conventional/m11_vanilla_transformer/runs/run_smoke_1ep` — 15.7 MB — smoke/debug/test run; bukan artefak benchmark final
- `training_conventional/m11_vanilla_transformer/runs/run_smoke_wer` — 15.7 MB — smoke/debug/test run; bukan artefak benchmark final
- `training_conventional/m11_vanilla_transformer/runs/run_smoke_wer_v2` — 15.7 MB — smoke/debug/test run; bukan artefak benchmark final

### m12-vit-modified-ID
- `training_conventional/m12_vit_modified/runs/run_full_20260528_220107` — 8.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training_conventional/m12_vit_modified/runs/run_full_20260528_220113` — 8.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training_conventional/m12_vit_modified/runs/run_full_20260528_220118` — 8.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training_conventional/m12_vit_modified/runs/run_full_20260528_220329` — 8.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training_conventional/m12_vit_modified/runs/run_full_20260528_220402` — 8.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training_conventional/m12_vit_modified/runs/run_full_20260529_041505` — 8.0 KB — tidak ada checkpoint/report/test_paper evidence
- `training_conventional/m12_vit_modified/runs/run_smoke_1ep` — 25.8 MB — smoke/debug/test run; bukan artefak benchmark final
- `training_conventional/m12_vit_modified/runs/run_smoke_wer` — 25.8 MB — smoke/debug/test run; bukan artefak benchmark final

### m13-wav2letter
- `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531` — 1.1 GB — terindikasi interrupted/short run (3 epoch evidence)
- `training_conventional/m13_wav2letter_cnn/runs/run_smoke_2ep` — 569.0 MB — smoke/debug/test run; bukan artefak benchmark final
- `training_conventional/m13_wav2letter_cnn/runs/run_smoke_acc` — 570.2 MB — smoke/debug/test run; bukan artefak benchmark final
- `training_conventional/m13_wav2letter_cnn/runs/run_smoke_best` — 758.8 MB — smoke/debug/test run; bukan artefak benchmark final
- `training_conventional/m13_wav2letter_cnn/runs/run_smoke_chk` — 758.7 MB — smoke/debug/test run; bukan artefak benchmark final

## Catatan

- Completed old non-final berukuran besar belum dimasukkan karena training tampak selesai/berisi checkpoint; ini perlu persetujuan terpisah jika ingin pembersihan agresif.
- Setelah disetujui, penghapusan sebaiknya dilakukan dari daftar kandidat di atas saja, lalu verifikasi ulang `Report_paper_9model/benchmark/benchmark.json` dan `model_artifacts/`.
