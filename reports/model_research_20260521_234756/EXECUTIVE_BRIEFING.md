# 🎯 EXECUTIVE BRIEFING — Model Selection for Paper

## TL;DR

**Pertanyaan**: Model apa saja untuk train dataset 102 544 file Indonesian ASR ini?

**Jawaban Grand Master**: 9-architecture multi-tier comparison

| Tier | Model | Role | Expected WER (FT) |
|:----:|-------|------|:----:|
| T0 | Whisper-large-v3 zero-shot | upper-bound | 8-13% |
| T0 | MMS-1B-all zero-shot | multilingual | 12-18% |
| **T1** | **Whisper-small FT** | **PRIMARY** | **8-12%** |
| T1 | MMS-1B adapter FT | param-efficient | 8-12% |
| T2 | wav2vec2-XLS-R-300M FT | CTC alt | 9-13% |
| T3 | cahya/wav2vec2-xlsr-id FT | Indonesian-spec | 6-10% |
| T3 | Conformer-CTC small | modern from-scratch | 15-20% |
| T4-A | Kaldi TDNN-HMM | hybrid baseline | 15-25% |
| T4-B | Bi-LSTM CTC | legacy E2E | 25-35% |

## Bi-LSTM verdict: ✅ KEEP (legacy baseline)

DeepSpeech-2 style (5x BiLSTM 1024 + CNN frontend + CTC). Cite Amodei et al. 2015.
Position: "pre-Transformer ASR baseline" — shows progression to modern.

## T-RCNN verdict: ❌ EXCLUDE

Non-standard term, no reference implementation, low reproducibility.
**Replace with**: Conformer-CTC small (modern) atau Bi-LSTM CTC (legacy).

## Modern SOTA terkini cocok

✅ Whisper-large-v3 (2023), Whisper-large-v3-turbo (Oct 2024)
✅ MMS-1B-all (2023)
⚠️ SeamlessM4T-v2 (Dec 2023) — optional zero-shot only
⚠️ Parakeet-TDT-1.1B (2024) — optional, NeMo
❌ Voxtral (Mistral, 2024), Canary (no Indonesian)

## Sprint Plan (22-36 days)

1. Sprint 1 (1-2 days): Zero-shot baselines (T0)
2. Sprint 2 (3-5 days): Whisper-small FT (PRIMARY)
3. Sprint 3 (3-5 days): Alternative FT (XLS-R, MMS, cahya)
4. Sprint 4 (5-7 days): Architectural baselines (Conformer, Bi-LSTM, Kaldi)
5. Sprint 5 (5-7 days): Ablations (synth, augment, data efficiency)
6. Sprint 6 (5-10 days): Paper writing

## Reviewer-anticipated concerns

- 0.13% synth → honest disclosure + ablation
- 20 speakers → speaker-disjoint splits + future work
- Bi-LSTM in 2026 → legacy baseline showing progression
- T-RCNN excluded → cited reasoning (non-standard)

## Status

✅ 3 critique iterations completed
✅ Citations: 12+ peer-reviewed references
✅ Methodology: bootstrap CI + McNemar + per-error
✅ Reproducibility: open-source, Docker, HF Hub
✅ READY FOR EXECUTION

**Tunggu approval USER untuk kick off Sprint 1.**
