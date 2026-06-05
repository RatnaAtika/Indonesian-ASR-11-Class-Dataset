# PDF-friendly evidence and provenance summary

This readable summary avoids wide tables in the full-detail PDF. For full audit paths, see `tables/paper_9model_evidence_table.md`, `benchmark/benchmark.json`, and `data/paper_9model_results_normalized.json`.

## m02b-whisper-small-ft
- Timing: train 04:48:29 (4.808 h); observed full-test evaluation 01:12:43.
- Size: params 241,734,912; templates n/a.
- Hardware provenance: Google Colab Linux, NVIDIA A100-SXM4-40GB GPU.
- Evidence sources: time=training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/report.md:24; params=training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/report.md:20; hw=report.md + meta.json/training_meta.environment + Colab audit report.
- Best artifact exists: True.

## m06-conformer-ctc
- Timing: train 06:31:49 (6.530 h); observed full-test evaluation 00:00:52.
- Size: params 11,048,219; templates n/a.
- Hardware provenance: Local Linux laptop, NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM.
- Evidence sources: time=training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/report.md:17; params=training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/report.md:14; hw=report.md + meta.json/training_meta.environment; VRAM label supplied by project run notes/user provenance.
- Best artifact exists: True.

## m12-vit-modified-ID
- Timing: train 03:44:58 (3.749 h); observed full-test evaluation 00:21:44.
- Size: params 4,353,248; templates n/a.
- Hardware provenance: Training log records `Using device: cuda`; exact training OS/GPU model not recorded. Full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU.
- Evidence sources: time=training_conventional/m12_vit_modified/runs/run_full_20260528_223323/Log_Run.txt:698; params=training_conventional/m12_vit_modified/runs/run_full_20260528_223323/Log_Run.txt:58; hw=Log_Run.txt:10 plus test_results/test_paper.json test_environment.
- Best artifact exists: True.

## m07-bilstm-ctc
- Timing: train 07:06:23 (7.106 h); observed full-test evaluation 00:01:10.
- Size: params 32,825,659; templates n/a.
- Hardware provenance: Local Linux laptop, NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM.
- Evidence sources: time=training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/report.md:17; params=training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/report.md:14; hw=report.md + meta.json/training_meta.environment; VRAM label supplied by project run notes/user provenance.
- Best artifact exists: True.

## m11-vanilla-transformer
- Timing: train 02:38:53 (2.648 h); observed full-test evaluation 00:21:33.
- Size: params 4,212,688; templates n/a.
- Hardware provenance: Training log records `Using device: cuda`; exact training OS/GPU model not recorded. Full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU.
- Evidence sources: time=training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328/Log_Run.txt:676; params=training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328/Log_Run.txt:59; hw=Log_Run.txt:10 plus test_results/test_paper.json test_environment.
- Best artifact exists: True.

## m13-wav2letter
- Timing: train 04:10:23 (4.173 h); observed full-test evaluation 00:00:23.
- Size: params 24,840,900; templates n/a.
- Hardware provenance: WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata.
- Evidence sources: time=training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/report.md:17; params=training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/report.md:13; hw=training_meta.environment in test_paper.json/meta.json.
- Best artifact exists: True.

## m08-hmm-gmm
- Timing: train 03:17:11 (3.286 h); observed full-test evaluation 00:54:37.
- Size: params 511,005; templates 209.
- Hardware provenance: WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata.
- Evidence sources: time=training_conventional/m08_hmm_gmm/runs/run_paper_20260530/report.md:16-17; params=.../m08_hmm_gmm/runs/run_paper_20260530/checkpoints/best.pkl arrays; report.md:19 records 209 templates; hw=training_meta.environment in test_paper.json/meta.json.
- Best artifact exists: True.

## m10-gmm-hmm-dnn
- Timing: train 06:29:10 (6.486 h); observed full-test evaluation 00:00:19.
- Size: params 1,448,336; templates 209.
- Hardware provenance: WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata.
- Evidence sources: time=training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/report.md:16-17; params=training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/report.md:18-19; hw=training_meta.environment in test_paper.json/meta.json.
- Best artifact exists: True.

## m09-dnn-hmm
- Timing: train 03:12:11 (3.203 h); observed full-test evaluation 00:00:20.
- Size: params 1,448,336; templates n/a.
- Hardware provenance: WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata.
- Evidence sources: time=training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/report.md:16-17; params=training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/report.md:18; hw=training_meta.environment in test_paper.json/meta.json.
- Best artifact exists: True.
