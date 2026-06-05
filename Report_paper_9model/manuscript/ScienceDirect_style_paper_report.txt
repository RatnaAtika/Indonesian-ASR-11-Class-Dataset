# A Reproducible Nine-Model Benchmark for an Indonesian 11-Class ASR Dataset

## Highlights

- A full nine-model benchmark was completed on the Indonesian v7 test split containing 15,376 utterances.
- The comparison spans HMM-GMM/DNN-HMM, CTC neural baselines, Transformer/ViT-style models, Conformer-CTC, and Whisper-small fine-tuning.
- Whisper-small fine-tuning achieved the best internal benchmark result with WER=0.0085 and CER=0.0019.
- Training time, observed full-test evaluation wall time, parameter counts, and OS/GPU provenance are recorded where available; unrecorded fields are explicitly marked.
- Best-model artifacts are split into per-model directories under `Report_paper_9model/model_artifacts/` with manifests, source-code snapshots, pseudocode excerpts, architecture summaries, and local binary copies/hardlinks where available.

## Abstract

This report summarizes a reproducible benchmark package for an Indonesian automatic speech recognition (ASR) dataset containing 11 utterance classes. Nine ASR model families were evaluated on the same full v7 test split of 15,376 utterances using greedy decoding without an external language model. The benchmark covers HMM-GMM, DNN-HMM, GMM-HMM-DNN, Vanilla Transformer, a proposed ViT-modified-ID architecture, Wav2Letter-style CNN-CTC, Bi-LSTM CTC, Conformer-CTC, and Whisper-small fine-tuning. The best internal benchmark result was obtained by Whisper-small fine-tuning (WER=0.0085, CER=0.0019), followed by Conformer-CTC (WER=0.0119, CER=0.0043) and the proposed ViT-modified-ID model (WER=0.0178, CER=0.0130). The report provides measured training time, observed full-test evaluation wall time, parameter count, hardware provenance, prediction files, source-code snapshots, pseudocode excerpts, architecture summaries, and best-artifact manifests. Binary model weights are packaged locally and should be deposited separately with a DOI/Drive/Zenodo/OSF link for journal submission.

## Keywords

Indonesian ASR; speech recognition dataset; Whisper; Conformer; ViT; CTC; HMM-GMM; Data in Brief; reproducible benchmark

## 1. Introduction

Compared with English, Indonesian has fewer widely used public ASR benchmarks within this package's scope. A dataset paper therefore benefits from both a clear description of the data resource and a reproducible benchmark that helps future users understand expected model behavior. This package evaluates nine model families under a shared test split and a common greedy/no-LM evaluation protocol.

## 2. Benchmark design and fairness protocol

All reported test metrics use the same v7 test split with n=15,376 utterances. The benchmark reports WER, CER, MER, WIL, and SER computed from model predictions and references. Decoding was performed greedily without an external language model. Training used best-on-validation checkpoint selection where available. This design controls the test split and decoding protocol. Interpretation must still distinguish pretrained models (Whisper-small) from from-scratch or task-specific architectures; therefore, the benchmark supports practical model ranking and dataset documentation rather than a purely architecture-only fairness claim.

## 3. Models

The nine evaluated systems are: HMM-GMM template classification (m08), DNN-HMM (m09), GMM-HMM-DNN staged hybrid (m10), Vanilla Transformer (m11), ViT-modified-ID (m12, proposed in this work), Wav2Letter-style CNN-CTC (m13), Bi-LSTM CTC (m07), Conformer-CTC (m06), and Whisper-small fine-tuning (m02b). Pseudocode for each model is provided in `appendices/model_pseudocode_appendix.md`.

## 4. Results

| Rank | Model | Family | WER | CER | Train time | Test time | Params | Training hardware | Best epoch |
|---:|---|---|---:|---:|---:|---:|---:|---|---:|
| 1 | `m02b-whisper-small-ft` | Whisper-small FT (Radford et al. 2023; arXiv 2022) | 0.0085 | 0.0019 | 04:48:29 | 01:12:43 | 241,734,912 | Google Colab Linux, A100-SXM4-40GB GPU | 5 |
| 2 | `m06-conformer-ctc` | Conformer-CTC (Gulati 2020) | 0.0119 | 0.0043 | 06:31:49 | 00:00:52 | 11,048,219 | Local Linux laptop, RTX 4060 Laptop GPU, 8 GB VRAM | 29 |
| 3 | `m12-vit-modified-ID` | ViT-modified-ID (proposed in this work) | 0.0178 | 0.0130 | 03:44:58 | 00:21:44 | 4,353,248 | Training log records `Using device: cuda`; exact training OS/GPU model not recorded. Full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU. | n/a |
| 4 | `m07-bilstm-ctc` | Bi-LSTM CTC | 0.0401 | 0.0132 | 07:06:23 | 00:01:10 | 32,825,659 | Local Linux laptop, RTX 4060 Laptop GPU, 8 GB VRAM | 30 |
| 5 | `m11-vanilla-transformer` | Vanilla Transformer (Vaswani 2017) | 0.0439 | 0.0327 | 02:38:53 | 00:21:33 | 4,212,688 | Training log records `Using device: cuda`; exact training OS/GPU model not recorded. Full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU. | n/a |
| 6 | `m13-wav2letter` | Wav2Letter-style CNN-CTC (Collobert 2016) | 0.0929 | 0.0520 | 04:10:23 | 00:00:23 | 24,840,900 | WSL2 Linux, RTX 4060 Laptop GPU; VRAM not recorded in run metadata | 27 |
| 7 | `m08-hmm-gmm` | HMM-GMM (classical) | 0.9633 | 0.7205 | 03:17:11 | 00:54:37 | 511,005 | WSL2 Linux, RTX 4060 Laptop GPU; VRAM not recorded in run metadata | 1 |
| 8 | `m10-gmm-hmm-dnn` | GMM-HMM-DNN (3-stage) | 0.9703 | 0.8516 | 06:29:10 | 00:00:19 | 1,448,336 | WSL2 Linux, RTX 4060 Laptop GPU; VRAM not recorded in run metadata | 15 |
| 9 | `m09-dnn-hmm` | DNN-HMM (hybrid) | 0.9708 | 0.8437 | 03:12:11 | 00:00:20 | 1,448,336 | WSL2 Linux, RTX 4060 Laptop GPU; VRAM not recorded in run metadata | 12 |

## 5. Evidence-backed compute and provenance table

| Model | Train time | Train h | Test time | Params | Templates | Hardware provenance | Evidence sources | Best artifact exists |
|---|---:|---:|---:|---:|---:|---|---|---:|
| `m02b-whisper-small-ft` | 04:48:29 | 4.808 | 01:12:43 | 241,734,912 | n/a | Google Colab Linux, NVIDIA A100-SXM4-40GB GPU | time: `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/report.md:24`; params: `training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/report.md:20`; hw: `report.md + meta.json/training_meta.environment + Colab audit report` | True |
| `m06-conformer-ctc` | 06:31:49 | 6.530 | 00:00:52 | 11,048,219 | n/a | Local Linux laptop, NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM | time: `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/report.md:17`; params: `training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/report.md:14`; hw: `report.md + meta.json/training_meta.environment; VRAM label supplied by project run notes/user provenance` | True |
| `m12-vit-modified-ID` | 03:44:58 | 3.749 | 00:21:44 | 4,353,248 | n/a | Training log records `Using device: cuda`; exact training OS/GPU model not recorded. Full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU. | time: `training_conventional/m12_vit_modified/runs/run_full_20260528_223323/Log_Run.txt:698`; params: `training_conventional/m12_vit_modified/runs/run_full_20260528_223323/Log_Run.txt:58`; hw: `Log_Run.txt:10 plus test_results/test_paper.json test_environment` | True |
| `m07-bilstm-ctc` | 07:06:23 | 7.106 | 00:01:10 | 32,825,659 | n/a | Local Linux laptop, NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM | time: `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/report.md:17`; params: `training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/report.md:14`; hw: `report.md + meta.json/training_meta.environment; VRAM label supplied by project run notes/user provenance` | True |
| `m11-vanilla-transformer` | 02:38:53 | 2.648 | 00:21:33 | 4,212,688 | n/a | Training log records `Using device: cuda`; exact training OS/GPU model not recorded. Full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU. | time: `training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328/Log_Run.txt:676`; params: `training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328/Log_Run.txt:59`; hw: `Log_Run.txt:10 plus test_results/test_paper.json test_environment` | True |
| `m13-wav2letter` | 04:10:23 | 4.173 | 00:00:23 | 24,840,900 | n/a | WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata | time: `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/report.md:17`; params: `training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/report.md:13`; hw: `training_meta.environment in test_paper.json/meta.json` | True |
| `m08-hmm-gmm` | 03:17:11 | 3.286 | 00:54:37 | 511,005 | 209 | WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata | time: `training_conventional/m08_hmm_gmm/runs/run_paper_20260530/report.md:16-17`; params: `training_conventional/m08_hmm_gmm/runs/run_paper_20260530/checkpoints/best.pkl arrays; report.md:19 records 209 templates`; hw: `training_meta.environment in test_paper.json/meta.json` | True |
| `m10-gmm-hmm-dnn` | 06:29:10 | 6.486 | 00:00:19 | 1,448,336 | 209 | WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata | time: `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/report.md:16-17`; params: `training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/report.md:18-19`; hw: `training_meta.environment in test_paper.json/meta.json` | True |
| `m09-dnn-hmm` | 03:12:11 | 3.203 | 00:00:20 | 1,448,336 | n/a | WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata | time: `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/report.md:16-17`; params: `training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/report.md:18`; hw: `training_meta.environment in test_paper.json/meta.json` | True |

## 6. Internal interpretation notes (move to Discussion/Appendix as needed)

Whisper-small fine-tuning is the strongest internal benchmark model, obtaining WER=0.0085 and CER=0.0019. This is expected because Whisper benefits from large-scale weakly supervised pretraining and is then adapted to the target Indonesian domain. Conformer-CTC is the strongest non-Whisper baseline with WER=0.0119. The proposed ViT-modified-ID model achieves WER=0.0178, outperforming Bi-LSTM CTC by 55.7% relative WER and Wav2Letter by 80.9% relative WER. Classical HMM-family baselines remain substantially weaker, with WER around 0.96--0.97.

## 7. Hardware provenance caveats

Conformer-CTC and Bi-LSTM CTC were trained on a local Linux laptop with an NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM. Whisper-small was trained on Google Colab Linux with an NVIDIA A100-SXM4-40GB GPU. WSL2-trained conventional and CNN runs record WSL2 Linux plus RTX 4060 Laptop GPU in run metadata, but not VRAM. m11 and m12 source training logs record CUDA use but do not record exact training OS/GPU model; their later full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU.

## 8. Data in Brief-ready article sections

### Specifications Table

- Subject area: Computer Science / Speech and Audio Processing.
- Specific subject area: Indonesian automatic speech recognition dataset and benchmark.
- Data type: WAV audio, transcript text, split manifests, benchmark metrics, model predictions, trained model artifacts.
- Data format: raw audio, TSV/CSV/JSON/Markdown/LaTeX/PDF.
- Experimental factors: full v7 train/validation/test splits, greedy decoding, no external language model.
- Experimental features: 9-model benchmark over classical, hybrid, CTC, Transformer, ViT-style, Conformer, and Whisper fine-tuning families.

### Value of the Data

The dataset and benchmark provide a reusable Indonesian ASR testbed, a strong pretrained Whisper baseline, and multiple non-pretrained architectural baselines for future comparative studies. The released predictions and metrics support error analysis, reproducibility checks, and method development.

### Data Description

For each model, `test_paper.json` records WER, CER, MER, WIL, SER, decoding method, checkpoint path, sample predictions, and prediction CSV location. The final benchmark package additionally records total training time, observed full-test evaluation wall time, parameter count, OS/GPU provenance where available, and best-artifact manifests.

### Experimental Design, Materials and Methods

All systems are evaluated with greedy decoding and no external language model. Best checkpoints are selected on validation performance when available. The Whisper-small result is a pretrained fine-tuning baseline and should be interpreted separately from scratch-trained models.

### Usage Notes

Use `benchmark/benchmark.json` as the single source of truth for paper writing. Use `tables/paper_table_9model.tex` for LaTeX manuscripts and `figures/*.pdf` for vector figure inclusion. Use `model_artifacts/artifact_index.json` to locate source-code snapshots, pseudocode excerpts, architecture summaries, local best-artifact manifests, and local hardlinks/copies. Binary weights must be deposited separately for submission-scale reproducibility.

### Limitations

The benchmark is internally reproducible but not an external Indonesian ASR leaderboard. Runtime measurements are not fully normalized across hardware and should not be used as primary efficiency claims. External SOTA claims should be avoided unless an external Indonesian ASR comparison is added.

## 9. Internal recommended paper claim (not a required Data in Brief section)

The defensible claim is: within this internal nine-model dataset benchmark, Whisper-small fine-tuning provides the strongest overall baseline, while the proposed ViT-modified-ID model is a competitive novel non-Whisper architecture that substantially improves over Bi-LSTM CTC and Wav2Letter-style CNN-CTC. Avoid claiming external SOTA unless an external Indonesian ASR leaderboard comparison is added.

## 10. Files generated

- `benchmark/benchmark.json`: authoritative enriched benchmark aggregate.
- `tables/paper_9model_results_normalized.csv`: normalized table with timing, parameters, and provenance.
- `tables/paper_9model_evidence_table.md`: evidence-source table for timings/parameters/provenance.
- `tables/paper_table_9model.tex`: LaTeX table for manuscript.
- `figures/*.png` and `figures/*.pdf`: paper-ready visualizations.
- `appendices/model_pseudocode_appendix.md`: pseudocode for all nine models.
- `appendices/candidate_references.md`: candidate literature references and caution notes.
- `model_artifacts/`: per-model artifact manifests, source-code snapshots, pseudocode excerpts, architecture summaries, global reproducibility docs, and local best-model artifact package; binary weights are local and should be separately deposited for submission.

## 11. Submission statements to complete before journal upload

- Data repository DOI/URL/accession: **TODO**.
- Data availability statement: **TODO**; include dataset and best-artifact deposition links.
- Ethics/consent statement: **TODO**; confirm speaker consent/recording protocol or state not applicable with justification.
- CRediT author statement: **TODO**.
- Declaration of competing interests: **TODO**.
