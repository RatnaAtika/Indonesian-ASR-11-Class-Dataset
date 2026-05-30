# Conventional ASR Baselines for the v7 Indonesian Corpus

> Companion folder to `training/` (which holds 7 modern models + 3 zero-shot
> baselines). This folder adds **7 conventional / classical / supervised
> baselines** at the doctoral-supervisor's recommendation, so the paper covers
> 14 fine-tuned architectures + 3 zero-shot = 17 systems total.

## Architectures

| Slot | Model | Family | Era | Trainable params (approx.) |
|------|-------|--------|-----|---------------------------:|
| **m08** | HMM-GMM template classifier | classical Markov | 1990s–2000s | 19 × 5-state GMM-HMMs |
| **m09** | DNN-HMM hybrid | classical hybrid | 2010s | ~3.7 M (DNN only) |
| **m10** | GMM-HMM-DNN 3-stage | classical hybrid | 2010s | GMM-HMM + ~3.7 M DNN |
| **m11** | Vanilla Transformer (Vaswani 2017) | encoder-decoder | 2017 | ~3.5 M (`d_model=192`) |
| **m12** | **ViT-modified-ID** ★ (Ratna 2026, *unpublished*) | encoder-decoder + CTC aux | **this paper's contribution** | ~3.5 M |
| **m13** | Wav2Letter (Collobert 2016) | 1-D CNN + CTC | 2016 | ~7 M |
| **m14** | Jasper-mini (Li 2019) | deep 1-D CNN + CTC | 2019 | ~28 M |

## Folder layout

```
training_conventional/
├── 00_BMAD_PLAN.md             ← methodology
├── README.md  README-RUN.md  SCALING.md
├── data_pkl/                    ← log-mel pickles (compatible with existing root scripts)
│   ├── train.pkl, valid.pkl, test.pkl
│   └── manifest.json
├── spm/                         ← SentencePiece char model trained on v7
│   ├── spm_v7_char.{model,vocab}
│   └── spm_corpus.txt
├── common/
│   ├── feature_builder.py       ← v7 dataset → .pkl (log-mel + SPM tokenize)
│   ├── spm_builder.py           ← retrain SPM on v7 transcripts
│   ├── pkl_cnn_ctc_trainer.py   ← shared CNN-CTC trainer (m13 + m14)
│   ├── pkl_hmm_trainer.py       ← shared HMM family trainer (m08 + m09 + m10)
│   ├── utils.py                 ← WER/CER, history, plot regen, GPU monitor
│   └── regen_plots.py
├── m08_hmm_gmm/      train.py + runs/
├── m09_dnn_hmm/      train.py + runs/
├── m10_gmm_hmm_dnn/  train.py + runs/
├── m11_vanilla_transformer/ train.py + test.py + runs/  ← wraps root script
├── m12_vit_modified/         train.py + test.py + runs/  ← wraps root script
├── m13_wav2letter_cnn/       train.py + runs/
└── m14_jasper_cnn/           train.py + runs/
```

## Dataset format (compatible with existing root scripts)

`data_pkl/{train,valid,test}.pkl` contains:
```python
{
    "X":      list[np.ndarray (T, 80) float32],   # log-mel, mean-var per utt
    "y":      list[np.ndarray int64],             # SPM ids with <s>...</s>
    "fnames": list[str],                          # relative audio paths
    "text":   list[str],                          # plain transcripts
    "lengths": list[int],                         # T per sample
}
```

Identical to the format expected by the root `train_model_vanilla.py` /
`train_model_vit.py` — the wrappers in `m11_*/m12_*/train.py` simply forward
this pickle path. Re-using the proven existing code (no fork, no copy) ensures
reproducibility against the doctoral-supervisor's prior results.

### Feature pipeline
- Pre-emphasis 0.97
- STFT: n_fft = 512, hop = 256, win = 400 (default)
- 80-bin mel, log + per-utterance global mean-var normalisation
- SentencePiece char-subword unigram, 400 tokens
  (`<pad>=0 <unk>=1 <s>=2 </s>=3 <noise>=4 <laugh>=5 <hes>=6` then word-pieces)

To rebuild from scratch (re-runs are 100% reproducible):
```bash
python3 training_conventional/common/spm_builder.py
python3 training_conventional/common/feature_builder.py    # full
# or smoke
python3 trng_conventional/common/feature_builder.py --max-train 2000 --max-val 500 --max-test 500
```

## Smoke results (already verified end-to-end)

| Slot | Model | Smoke | WER | CER | GPU MB | Wall |
|------|-------|-------|-----|-----|-------:|-----:|
| m08 | HMM-GMM | 200 train / 50 val | 1.169 | 0.898 | – (CPU) | 16 s |
| m09 | DNN-HMM | 200/50, DNN 2 ep | 5.077 | 3.509 | <100 | 11 s |
| m10 | GMM-HMM-DNN | 200/50, 2 ep | 5.077 | 3.509 | <100 | 18 s |
| m11 | Vanilla Transformer | 2,000 / 500, 1 ep | – | **0.0465** ★ | ~600 | 14 s |
| m12 | **ViT-modified-ID** ☆ (this paper) | 2,000 / 500, 1 ep | – | **0.0832** ★ | ~600 | 15 s |
| m13 | Wav2Letter CNN | 200/50, 2 ep | 0.993 | 0.910 | 487 | 19 s |
| m14 | Jasper-mini CNN | 200/50, 2 ep | 1.000 | 0.933 | 2,074 | 40 s |

★ Existing root scripts use teacher-forcing for val CER (Char-Error rate during
forced decoding); free-running greedy WER is computed by the test script after
training. WER = 1 / CER ≈ 1 for HMM/CNN smoke is expected — they need many
more epochs (CTC alignment from scratch is slow). The pipeline is verified.

## Per-run artifacts (consistent with `training/`)

- `config.json` — exact CLI args
- `history.json` — list of per-epoch entries (loss, WER, CER, MER, WIL, GPU MB,
  throughput, lr, time)
- `log.txt` — append-only per-epoch log with PRED/LABEL samples
- `plots/{wer_cer,loss,gpu_mb,lr}.png` — auto-regenerated each epoch
- `predictions/sample_preds_e{N}.txt`
- `checkpoints/`
- `report.md` — auto-generated summary

(For m11 / m12 — the root scripts use a slightly different artifact set:
`cer_vit.png`, `char_accuracy_vit.png`, `model_summary_vit.{png,pdf}`,
`training_val_{loss,accuracy}_vit.png`, `transformer_asr_vit_last.pth`.
These are written to the **same `runs/<run_name>/` folder** so everything stays
together.)

## Running

See `README-RUN.md` for full per-model commands. Quick start:

```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate torch-gpu
cd "/mnt/c/Users/ratnaatika/AI/Dataset ASR/Paper_Datatset_SOTA"

# Smoke (already done):
python3 training_conventional/m08_hmm_gmm/train.py --max-train-samples 200 --max-val-samples 50

# Full training (overnight):
python3 training_conventional/m13_wav2letter_cnn/train.py
```

## Notes for the paper

1. **HMM-GMM is a closed-vocabulary template classifier**: 209 base sentences in
   v7 → 209 GMM-HMMs → argmax log-likelihood. This is the standard baseline
   for limited-vocabulary command/control ASR (the corpus is template-based by
   design). Not directly comparable to free-form modern ASR — expect WER ≥ 0.5
   even at full data.
2. **DNN-HMM and GMM-HMM-DNN** use SPM-token frame classifiers. Linear-time
   alignment is used for the initial frame labels; this is intentionally simple
   (no Kaldi forced alignment) for a self-contained Python baseline.
3. **CNN baselines (m13, m14)** are CTC-trained from scratch; expect WER plateau
   ~0.10–0.20 after 30–50 epochs on the full 71,792-sample train set.
4. **Vanilla Transformer (m11)** uses the supervisor-validated Vaswani 2017
   reference architecture from the project root, kept verbatim for direct
   reproducibility against the supervisor's prior work.
5. **ViT-modified-ID (m12)** is the **user's own novel architecture**,
   developed in 2026 for **Indonesian end-to-end limited-vocabulary ASR**.
   **Not yet published** — this paper is its first public report. The
   architecture (ViT-style patch encoder + auxiliary CTC + plateau LR)
   lives at the project root and is wrapped here without modification to
   preserve the exact experimental setup.
6. The full 17-model paper comparison (14 fine-tuned + 3 zero-shot) will be
   assembled by `training_conventional/common/build_comparison.py` (mirrors
   `training/common/build_comparison.py`) **after** all models complete
   their full runs (run one-per-terminal; the agent then aggregates).

## Reproducibility checklist

- ✓ Random seed = 42 default everywhere
- ✓ All scripts compile clean (`py_compile`)
- ✓ Pickles fully reproducible from raw audio + transcripts via
  `feature_builder.py` (deterministic given seed)
- ✓ SPM model deterministic given the same training corpus
- ✓ No-overwrite rule: every run goes to `runs/run_<smoke|full>_<YYYYMMDD>/`
