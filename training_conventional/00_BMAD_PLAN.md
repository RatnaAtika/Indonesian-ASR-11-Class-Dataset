# 00_BMAD_PLAN — Conventional ASR Models on the v7 Indonesian Corpus

**Owner role**: Grand Master / Professor of ASR & Speech Datasets
**Goal**: Deliver 7 *conventional / classical* ASR baselines as a paper-grade companion
to the 7 modern pretrained / from-scratch models already in `training/`, satisfying
the doctoral-supervisor recommendation:

| # | Slot | Architecture | Era | Why include |
|---|------|--------------|-----|-------------|
| m08 | `hmm_gmm` | HMM with Gaussian-mixture emissions per character class | 1990s–2000s | Pure classical baseline (HTK/Kaldi-equivalent in Python) |
| m09 | `dnn_hmm` | DNN posteriors as HMM emission probabilities (hybrid) | 2010s | The architecture that opened the deep-ASR era (Hinton 2012) |
| m10 | `gmm_hmm_dnn` | GMM-HMM bootstrapped → DNN refined → re-HMM | 2010s | Three-stage hybrid that won early IBM/Microsoft systems |
| m11 | `vanilla_transformer` | Encoder-decoder Transformer ("Attention Is All You Need") | 2017 | Existing code at root — wire to v7 dataset |
| m12 | `vit_modified` | **ViT-modified-ID** (User's novel architecture; ViT-style patch encoder + Transformer decoder + CTC aux) | **2026 (this paper, unpublished)** | Existing user-original code at root — wire to v7 dataset |
| m13 | `wav2letter_cnn` | 1-D convolutional encoder + CTC | 2016–2019 | The seminal CNN-only ASR (Collobert / FAIR) |
| m14 | `jasper_cnn` | Deep stacked 1-D CNN with residual connections + CTC | 2019 | Deeper CNN baseline (NVIDIA Jasper / Quartznet) |

These seven sit alongside (not replacing) the 7 modern models; the paper will report
**all 14 architectures + 3 zero-shot baselines = 17 systems** for a comprehensive
ASR landscape study on the v7 corpus.

## B — Build

### Folder layout
```
training_conventional/
├── README.md, README-RUN.md, SCALING.md
├── 00_BMAD_PLAN.md                       ← this file
├── data_pkl/                              ← v7 → .pkl features (vanilla/vit-compatible)
│   ├── train.pkl, valid.pkl, test.pkl
│   └── manifest.json (statistics + checksum)
├── spm/                                   ← SentencePiece char model
│   ├── spm_v7_char.model, spm_v7_char.vocab
│   └── spm_corpus.txt
├── common/
│   ├── feature_builder.py                 ← log-mel + SPM tokenize → .pkl
│   ├── spm_builder.py                     ← retrain SPM on v7 transcripts
│   ├── utils.py                           ← WER/CER, history, plot regen, GPU monitor
│   └── ctc_utils.py                       ← CTC decode + char-level vocab
├── m08_hmm_gmm/        train.py + runs/
├── m09_dnn_hmm/        train.py + runs/
├── m10_gmm_hmm_dnn/    train.py + runs/
├── m11_vanilla_transformer/ train.py + test.py + runs/  ← wraps existing root scripts
├── m12_vit_modified/   train.py + test.py + runs/        ← wraps existing root scripts
├── m13_wav2letter_cnn/ train.py + runs/
└── m14_jasper_cnn/     train.py + runs/
```

### Dataset adaptation
The existing vanilla / ViT codes expect this pickle format:
```python
{
    "X":      list[np.ndarray (T, 80) float32],   # log-mel, mean-var normalized per utt
    "y":      list[np.ndarray int64],             # token ids with <s> ... </s>
    "fnames": list[str],                          # audio relative path
    "text":   list[str],                          # plain transcript
    "lengths": list[int],                         # T per sample (= X[i].shape[0])
}
```
Existing SPM is char-subword 400-token: `<pad>=0 <unk>=1 <s>=2 </s>=3 <noise>=4 <laugh>=5 <hes>=6 ▁=7 ...`.

`feature_builder.py` will:
1. Read `metadata/dataset_metadata_clean.csv` + `training/data_final/{train,dev,test}.tsv`
2. Load each WAV via `soundfile` (bypass torchcodec / Arrow)
3. Compute log-Mel: pre-emphasis 0.97, n_fft=512, hop=256, n_mels=80, log + per-utt mean-var norm
4. Tokenize transcript via the v7-retrained SPM
5. Pack into pickle in the exact format above
6. Use stratified random subset (default 5,000 train / 1,000 valid / 1,000 test for smoke; full for paper)

### Conventional model choices

#### m08 HMM-GMM (`hmmlearn`)
- One left-right GaussianHMM per character class (24 chars + special)
- 5–7 states each, full covariance
- Per-utterance Viterbi over a meta-HMM that strings character HMMs
- *Or* simpler isolated-utterance classifier: 209-class HMM (one per base sentence) for headline-comparable WER
- Training: EM (Baum-Welch) via `hmmlearn`
- Decoding: greedy Viterbi → reconstruct text from sentence ID

#### m09 DNN-HMM (hybrid)
- Use frame-level character labels from forced alignment (linear interpolation as bootstrap, then iterative)
- DNN: 4-layer feedforward (512–256–256–vocab) on stacked ±5-frame log-Mel context
- HMM: left-right transitions, DNN posteriors as scaled emissions
- Decode: log-posterior summed Viterbi

#### m10 GMM-HMM-DNN (3-stage)
- Stage 1: Train GMM-HMM (m08 init)
- Stage 2: Force-align with GMM-HMM → frame-level char labels
- Stage 3: Train DNN on those alignments → DNN-HMM (m09 architecture)
- Decode: DNN posteriors + HMM transitions (Viterbi)

#### m11 Vanilla Transformer
- Wrapper around `train_model_vanilla.py` at project root with our v7 .pkl
- Auxiliary CTC loss optional
- Eval via existing `test_model_vanilla.py`

#### m12 ViT-modified-ID ★ (User's novel architecture, unpublished)
- The user's **own original modification** developed in 2026 for Indonesian
  end-to-end limited-vocabulary ASR. **Not yet published**; this paper is its
  first public report. One of the paper's primary novel contributions.
- Wraps the user-validated `train_model_vit.py` at project root
- Architecture: ViT-style patch encoder + Transformer decoder + CTC aux
  (`--lambda-ctc 0.1`) + plateau LR scheduler
- Hyperparameters per the user's last-stable run; **do not modify without
  re-validating** the architecture's prior CER trajectory

#### m13 Wav2Letter-style CNN
- 1-D CNN front-end → 11 conv blocks (kernel 7–13, dilations 1–4)
- Final linear → vocab logits
- CTC loss, greedy decode
- ~10–15 M params

#### m14 Jasper-style deeper CNN
- 11 sub-blocks, each = 5 stacked 1-D CNNs with residual + dense skip
- Lighter "Jasper-DR-10x4" variant: 10 blocks × 4 sub-blocks, ~30 M params
- CTC loss, greedy decode

## M — Measure

For every model + run we save the standard artifact set already in use for `training/`:
- `config.json`, `history.json`, `log.txt`, `report.md`
- `plots/{wer_cer,loss,gpu_mb,lr}.png`
- `predictions/sample_preds_e{N}.txt`
- `checkpoints/`

Per-epoch metrics:
- train_loss, val_loss
- WER, CER (and SER = sentence-error-rate where applicable for HMM classifiers)
- Frame accuracy (DNN-HMM, GMM-HMM-DNN)
- Time, GPU MB, throughput, lr

## A — Analyze

After all runs finish (full or smoke), produce a cross-model comparison akin to
`reports/training_smoke_comparison/`:
- `reports/training_conventional_comparison/` with WER/CER bar charts vs era,
  parameter count, GPU footprint
- Combine with the 7 modern models for a final 14-architecture paper plot

## D — Deliver

Each model produces a self-contained `runs/<run_name>/` folder. The pipeline is
**reproducible** (random seed = 42 default, all configs saved). Documentation:
1. `training_conventional/README.md` — architecture overview + folder map
2. `training_conventional/README-RUN.md` — exact full-run commands
3. `training_conventional/SCALING.md` — Colab / RunPod plans (HMMs are CPU-only;
   DNN / Transformer / CNN need GPU)

## Standards

- Random seed: 42 default everywhere
- All scripts compile with `python3 -m py_compile`
- Smoke tests use 200 train / 50 val / 1–2 epochs
- Full runs: 5–30 epochs depending on architecture (HMMs converge in ≤5 EM iter;
  CNN/Transformer need 30–80 epochs)
- No-overwrite rule: `runs/run_<smoke|full>_<YYYYMMDD>` always

## Success criteria

1. All 7 conventional architectures run end-to-end on a 200-sample smoke without errors
2. WER measurements are sensible (HMM-GMM ≫ Transformer ≫ Modern in WER, as expected)
3. Pipeline reproducible from a clean clone
4. Paper-ready cross-comparison report

## Estimated wall time

| Stage | Smoke | Full (paper) |
|-------|-------|--------------|
| feature_builder full | n/a | ~8–12 min on /mnt/c |
| feature_builder smoke (5k samples) | 1–2 min | – |
| spm_builder | 30 s | 1 min |
| m08 HMM-GMM | 2–3 min | ~10–20 min |
| m09 DNN-HMM | 3–5 min | 1–2 h |
| m10 GMM-HMM-DNN | 5 min | 2 h |
| m11 / m12 | 2 min smoke | 12–14 h each |
| m13 / m14 | 3 min smoke | 4–8 h each |

Total smoke: ~25 min. Total full: ~30 h on RTX 4060 Laptop, or ~6 h on Colab Pro+ A100.
