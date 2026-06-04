# A Reproducible Nine-Model Benchmark for an Indonesian 11-Class ASR Dataset

## Highlights

- A full nine-model benchmark was completed on the Indonesian v7 test split containing 15,376 utterances.
- The comparison spans classical HMM-GMM/DNN-HMM, CTC neural baselines, Transformer/ViT-style models, Conformer-CTC, and Whisper-small fine-tuning.
- Whisper-small fine-tuning achieved the best overall result with WER=0.0085 and CER=0.0019.
- The proposed ViT-modified-ID model ranked third overall and second among non-Whisper scratch/specialized models with WER=0.0178 and CER=0.0130.
- All metrics, predictions, run metadata, and model artifacts are organized for Data in Brief-style reproducibility.

## Abstract

This report summarizes the paper-ready benchmark package for an Indonesian automatic speech recognition (ASR) dataset containing 11 utterance classes. Nine ASR model families were evaluated on the same full v7 test split of 15,376 utterances using greedy decoding without an external language model. The benchmark covers HMM-GMM, DNN-HMM, GMM-HMM-DNN, Vanilla Transformer, a proposed ViT-modified-ID architecture, Wav2Letter CNN-CTC, Bi-LSTM CTC, Conformer-CTC, and Whisper-small fine-tuning. The best overall result was obtained by Whisper-small fine-tuning (WER=0.0085, CER=0.0019), followed by Conformer-CTC (WER=0.0119, CER=0.0043) and the proposed ViT-modified-ID model (WER=0.0178, CER=0.0130). Relative to Conformer-CTC, Whisper-small reduced WER by 28.6%. Relative to the proposed ViT-modified-ID model, Whisper-small reduced WER by 52.0%. The results provide a reproducible baseline suite for future Indonesian ASR research and a strong empirical basis for dataset documentation in a Data in Brief submission.

## Keywords

Indonesian ASR; speech recognition dataset; Whisper; Conformer; ViT; CTC; HMM-GMM; Data in Brief; reproducible benchmark

## 1. Introduction

Indonesian ASR resources remain less represented than English in large public benchmarks. A dataset paper therefore benefits from two complementary contributions: (i) a clear description of the data resource and (ii) a reproducible benchmark that helps future users understand expected model behavior. This package evaluates nine model families under a shared test split and a common greedy/no-LM evaluation protocol. The model set intentionally covers classical generative baselines, hybrid acoustic models, neural CTC models, attention-based sequence-to-sequence systems, and pretrained large-scale speech representation models.

## 2. Benchmark design and fairness protocol

All reported test metrics use the same v7 test split with n=15,376 utterances. The benchmark reports WER, CER, MER, WIL, and SER computed from model predictions and references. Decoding was performed greedily without an external language model. Training used best-on-validation checkpoint selection where available. This design controls the test split and decoding protocol. Interpretation must still distinguish pretrained models (e.g., Whisper-small) from from-scratch or task-specific architectures; therefore, the benchmark supports practical model ranking and dataset documentation rather than a purely architecture-only fairness claim.

## 3. Models

The nine evaluated systems are: HMM-GMM template classification (m08), DNN-HMM (m09), GMM-HMM-DNN staged hybrid (m10), Vanilla Transformer (m11), ViT-modified-ID (m12), Wav2Letter CNN-CTC (m13), Bi-LSTM CTC (m07), Conformer-CTC (m06), and Whisper-small fine-tuning (m02b). Pseudocode for each model is provided in `appendices/model_pseudocode_appendix.md`.

## 4. Results

| Rank | Model | Family | WER | CER | MER | WIL | SER | Wall time (s) | Best epoch |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `m02b-whisper-small-ft` | Whisper-small FT (Radford 2022) | 0.0085 | 0.0019 | 0.0085 | 0.0130 | 0.0390 | 4363.1 | 5 |
| 2 | `m06-conformer-ctc` | Conformer-CTC (Gulati 2020) | 0.0119 | 0.0043 | 0.0119 | 0.0205 | 0.0598 | 52.5 | 29 |
| 3 | `m12-vit-modified-ID` | ViT-modified-ID (Ratna 2026) | 0.0178 | 0.0130 | 0.0177 | 0.0315 | 0.0184 | 1304.3 | n/a |
| 4 | `m07-bilstm-ctc` | Bi-LSTM CTC | 0.0401 | 0.0132 | 0.0400 | 0.0721 | 0.1516 | 70.4 | 30 |
| 5 | `m11-vanilla-transformer` | Vanilla Transformer (Vaswani 2017) | 0.0439 | 0.0327 | 0.0438 | 0.0774 | 0.0454 | 1293.3 | n/a |
| 6 | `m13-wav2letter` | Wav2Letter CNN-CTC (Collobert 2016) | 0.0929 | 0.0520 | 0.0920 | 0.1524 | 0.2822 | 22.9 | 27 |
| 7 | `m08-hmm-gmm` | HMM-GMM (classical) | 0.9633 | 0.7205 | 0.8789 | 0.9822 | 0.9192 | 3277.3 | 1 |
| 8 | `m10-gmm-hmm-dnn` | GMM-HMM-DNN (3-stage) | 0.9703 | 0.8516 | 0.9690 | 0.9965 | 1.0000 | 18.9 | 15 |
| 9 | `m09-dnn-hmm` | DNN-HMM (hybrid) | 0.9708 | 0.8437 | 0.9693 | 0.9967 | 1.0000 | 19.8 | 12 |

## 5. Interpretation

Whisper-small fine-tuning is the strongest benchmark model, obtaining WER=0.0085 and CER=0.0019. This is expected because Whisper benefits from large-scale weakly supervised pretraining and is then adapted to the target Indonesian domain. Conformer-CTC is the strongest non-Whisper baseline with WER=0.0119, showing that convolution-augmented self-attention is highly effective for this dataset. The proposed ViT-modified-ID model achieves WER=0.0178, outperforming Bi-LSTM CTC by 55.7% relative WER and Wav2Letter by 80.9% relative WER. Classical HMM-family baselines remain substantially weaker, with WER around 0.96--0.97, indicating that template or frame-level hybrid modeling is insufficient for this dataset's lexical diversity.

## 6. Data in Brief-ready article sections

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

The benchmark uses the full v7 test split with 15,376 utterances. For each model, `test_paper.json` records WER, CER, MER, WIL, SER, decoding method, checkpoint path, sample predictions, and prediction CSV location.

### Experimental Design, Materials and Methods

All systems are evaluated with greedy decoding and no external language model. Best checkpoints are selected on validation performance when available. The Whisper-small result is a pretrained fine-tuning baseline and should be interpreted separately from scratch-trained models.

### Usage Notes

Use `benchmark/benchmark.json` as the single source of truth for paper writing. Use `tables/paper_table_9model.tex` for LaTeX manuscripts and `figures/*.pdf` for vector figure inclusion.

### Limitations

The benchmark is internally reproducible but not an external Indonesian ASR leaderboard. Runtime measurements are not fully normalized across hardware and should not be used as primary efficiency claims.

## 7. Data and reproducibility artifacts

The complete artifact package includes normalized benchmark JSON/CSV, paper table LaTeX, visualizations, pseudocode appendices, candidate references, and the detailed PDF summary. The strongest model artifact is stored in the Whisper run's `best_model/` directory and is directly loadable using Hugging Face Transformers.

## 8. Critical review and limitations

The comparison is strong because all models use the same full test split and no external LM. However, several limitations should be stated transparently. First, Whisper-small benefits from large-scale pretraining, while most other neural models are trained from scratch or smaller task-specific setups; therefore, Whisper is a strong practical upper baseline rather than an architecture-only comparison. Second, the HMM-family models are included for historical and methodological breadth, but their weak performance suggests they should not be framed as competitive SOTA. Third, the ViT-modified-ID model is promising as a dataset-specific architecture but should be presented as outperforming scratch neural baselines except Conformer, not as beating pretrained Whisper.

## 9. Recommended paper claim

The defensible claim is: within this internal nine-model dataset benchmark, Whisper-small fine-tuning provides the strongest overall baseline, while the proposed ViT-modified-ID model is a competitive novel non-Whisper architecture that substantially improves over Bi-LSTM CTC and Wav2Letter CNN-CTC. Avoid claiming external SOTA unless an external Indonesian ASR leaderboard comparison is added.

## 10. Files generated

- `benchmark/benchmark.json`: authoritative benchmark aggregate.
- `tables/paper_9model_results_normalized.csv`: normalized table.
- `tables/paper_table_9model.tex`: LaTeX table for manuscript.
- `figures/*.png` and `figures/*.pdf`: paper-ready visualizations.
- `appendices/model_pseudocode_appendix.md`: pseudocode for all nine models.
- `appendices/candidate_references.md`: candidate literature references to verify before submission.
