# Paper Table: 9-model ASR comparison

All rows are evaluated on the same full v7 test split (15,376 utterances), greedy decoding, and no external language model.
Training time, parameter count, and hardware provenance are evidence-backed from local run artifacts; see `tables/paper_9model_evidence_table.md`.

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
