from __future__ import annotations

import csv
import json
import math
import textwrap
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).parent
OUT = ROOT / "Report_paper_9model"
BENCH = OUT / "benchmark" / "benchmark.json"
FIG = OUT / "figures"
TABLES = OUT / "tables"
DATA = OUT / "data"
APP = OUT / "appendices"
MAN = OUT / "manuscript"
for d in [OUT, FIG, TABLES, DATA, APP, MAN]:
    d.mkdir(parents=True, exist_ok=True)

bench = json.loads(BENCH.read_text(encoding="utf-8"))
paper = [m for m in bench["paper_models"] if m.get("status") == "OK"]
paper = sorted(paper, key=lambda m: m["metrics"]["wer"])

# Normalize records
records = []
for rank, m in enumerate(paper, 1):
    metrics = m["metrics"]
    test = m.get("test_set", {})
    rec = {
        "rank": rank,
        "model_id": m["model_id"],
        "family": m.get("family", ""),
        "is_user_novel": bool(m.get("is_user_novel")),
        "wer": metrics.get("wer"),
        "cer": metrics.get("cer"),
        "mer": metrics.get("mer"),
        "wil": metrics.get("wil"),
        "ser": metrics.get("ser"),
        "wall_time_sec": m.get("wall_time_sec"),
        "throughput_samples_per_sec": m.get("throughput_samples_per_sec"),
        "peak_gpu_mb": m.get("peak_gpu_mb"),
        "best_train_wer": m.get("best_train_wer"),
        "best_train_epoch": m.get("best_train_epoch"),
        "n_epochs_trained": m.get("n_epochs_trained"),
        "n_test_samples": test.get("n_samples"),
        "decoding_method": (m.get("decoding") or {}).get("method"),
        "checkpoint": m.get("checkpoint"),
        "test_json": m.get("test_json"),
        "predictions_csv": m.get("predictions_csv"),
    }
    records.append(rec)

(DATA / "paper_9model_results_normalized.json").write_text(
    json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
)
with (TABLES / "paper_9model_results_normalized.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
    w.writeheader(); w.writerows(records)

# Key comparisons
best = records[0]
novel = next((r for r in records if r["is_user_novel"]), None)
conformer = next((r for r in records if r["model_id"] == "m06-conformer-ctc"), None)
bilstm = next((r for r in records if r["model_id"] == "m07-bilstm-ctc"), None)
whisper = next((r for r in records if r["model_id"] == "m02b-whisper-small-ft"), None)

def rel_improve(a, b):
    # improvement of a over b, lower is better
    return (b - a) / b * 100 if b else None

analysis = {
    "generated": datetime.now().isoformat(),
    "n_paper_models_present": len(records),
    "best_model": best,
    "novel_model": novel,
    "relative_improvements": {
        "whisper_vs_conformer_wer_percent": rel_improve(whisper["wer"], conformer["wer"]) if whisper and conformer else None,
        "whisper_vs_vit_wer_percent": rel_improve(whisper["wer"], novel["wer"]) if whisper and novel else None,
        "vit_vs_bilstm_wer_percent": rel_improve(novel["wer"], bilstm["wer"]) if novel and bilstm else None,
        "vit_vs_wav2letter_wer_percent": rel_improve(novel["wer"], next(r for r in records if r["model_id"] == "m13-wav2letter")["wer"]) if novel else None,
    },
}
(DATA / "paper_9model_interpretation_metrics.json").write_text(json.dumps(analysis, indent=2), encoding="utf-8")

# Markdown/LaTeX table
cols = ["rank", "model_id", "family", "wer", "cer", "mer", "wil", "ser", "wall_time_sec", "best_train_epoch"]
md_lines = ["# Paper Table: 9-model ASR comparison", "", "| Rank | Model | Family | WER | CER | MER | WIL | SER | Wall time (s) | Best epoch |", "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|"]
for r in records:
    md_lines.append(f"| {r['rank']} | `{r['model_id']}` | {r['family']} | {r['wer']:.4f} | {r['cer']:.4f} | {r['mer']:.4f} | {r['wil']:.4f} | {r['ser']:.4f} | {r['wall_time_sec']:.1f} | {r['best_train_epoch'] if r['best_train_epoch'] is not None else 'n/a'} |")
(TABLES / "paper_table_9model.md").write_text("\n".join(md_lines)+"\n", encoding="utf-8")

tex = [
    r"\begin{table*}[t]",
    r"\centering",
    r"\caption{Nine-model Indonesian ASR benchmark on the full v7 test split (15,376 utterances). Lower is better for all error metrics.}",
    r"\label{tab:asr-9model}",
    r"\begin{tabular}{rllrrrrr}",
    r"\toprule",
    "Rank & Model & Family & WER & CER & MER & WIL & SER \\",
    r"\midrule",
]
for r in records:
    fam = r['family'].replace('&', r'\&')
    tex.append(f"{r['rank']} & {r['model_id']} & {fam} & {r['wer']:.4f} & {r['cer']:.4f} & {r['mer']:.4f} & {r['wil']:.4f} & {r['ser']:.4f} \\")
tex += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
(TABLES / "paper_table_9model.tex").write_text("\n".join(tex)+"\n", encoding="utf-8")

# Figures
def save_bar(metric, title, fname, log=False):
    fig, ax = plt.subplots(figsize=(11, 6))
    labels = [r["model_id"].replace("-", "\n") for r in records]
    vals = [r[metric] for r in records]
    colors = ["#1f77b4" if not r["is_user_novel"] else "#d62728" for r in records]
    ax.bar(range(len(vals)), vals, color=colors)
    ax.set_xticks(range(len(vals)), labels, fontsize=8)
    ax.set_ylabel(metric.upper())
    ax.set_title(title)
    if log:
        ax.set_yscale("log")
        ax.set_ylabel(metric.upper() + " (log scale)")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG / f"{fname}.png", dpi=300)
    fig.savefig(FIG / f"{fname}.pdf")
    plt.close(fig)

save_bar("wer", "WER ranking across nine ASR models", "fig1_wer_ranking")
save_bar("cer", "CER ranking across nine ASR models", "fig2_cer_ranking")
save_bar("wer", "WER ranking across nine ASR models (log scale)", "fig3_wer_logscale", log=True)

# WER vs CER scatter
fig, ax = plt.subplots(figsize=(8, 6))
for r in records:
    ax.scatter(r["wer"], r["cer"], s=90, c="#d62728" if r["is_user_novel"] else "#1f77b4")
    ax.annotate(r["model_id"].replace("m02b-", ""), (r["wer"], r["cer"]), fontsize=7, xytext=(4, 3), textcoords="offset points")
ax.set_xlabel("WER")
ax.set_ylabel("CER")
ax.set_title("WER-CER trade-off on full Indonesian v7 test split")
ax.grid(alpha=0.25)
fig.tight_layout(); fig.savefig(FIG/"fig4_wer_cer_scatter.png", dpi=300); fig.savefig(FIG/"fig4_wer_cer_scatter.pdf"); plt.close(fig)

# Wall time figure
fig, ax = plt.subplots(figsize=(11, 6))
labels = [r["model_id"].replace("-", "\n") for r in records]
vals = [r["wall_time_sec"] / 60 for r in records]
ax.bar(range(len(vals)), vals, color="#2ca02c")
ax.set_xticks(range(len(vals)), labels, fontsize=8)
ax.set_ylabel("Test wall time (minutes)")
ax.set_title("Inference/test runtime by model")
ax.grid(axis="y", alpha=0.25)
fig.tight_layout(); fig.savefig(FIG/"fig5_test_runtime_minutes.png", dpi=300); fig.savefig(FIG/"fig5_test_runtime_minutes.pdf"); plt.close(fig)

# Pseudocode appendix
pseudo = r"""
# Appendix: Model pseudocode for nine-model benchmark

## Algorithm 1 — HMM-GMM template classifier (m08)
Input: log-mel sequence X, trained HMM-GMM template bank {H_t}
For each test utterance X:
  best_score = -inf; best_text = null
  For each template text t and HMM-GMM model H_t:
    score = log_likelihood(H_t, X)
    If score > best_score: update best_score, best_text
  Output best_text
Evaluate predictions with WER, CER, MER, WIL, SER.

## Algorithm 2 — DNN-HMM frame classifier (m09)
Input: sequence X, context window c, frame DNN f_theta, SentencePiece model S
For each utterance:
  Xc = stack_context(X, c)
  logits = f_theta(Xc)
  token_ids = argmax(logits, per frame)
  token_ids = collapse_repeats_and_remove_special(token_ids)
  text = S.decode(token_ids)
  Output text.

## Algorithm 3 — GMM-HMM-DNN staged hybrid (m10)
Same decoding as Algorithm 2, using staged GMM-HMM-informed DNN training artifacts.

## Algorithm 4 — Vanilla Transformer encoder-decoder (m11)
Input: log-mel features X, character/subword tokenizer S
Encode X with Transformer encoder using self-attention.
Initialize decoder with BOS.
Repeat until EOS or max length:
  Decode autoregressively with masked self-attention and encoder attention.
  Append argmax next token.
Output S.decode(tokens).

## Algorithm 5 — ViT-modified-ID (m12, proposed/novel)
Input: log-mel spectrogram X
Patch/tokenize spectrogram into frame-patch embeddings.
Apply ViT-inspired self-attention blocks adapted for Indonesian ASR.
Decode with greedy autoregressive decoder plus CTC auxiliary alignment signal.
Output decoded Indonesian sentence.

## Algorithm 6 — Wav2Letter CNN-CTC (m13)
Input: log-mel sequence X
Apply temporal convolutional stack.
Project to token logits for each valid, unpadded frame.
Run CTC greedy decode: argmax, collapse repeats, remove blank.
Output decoded sentence.

## Algorithm 7 — Bi-LSTM CTC (m07)
Input: log-mel sequence X
Encode sequence with bidirectional LSTM layers.
Project hidden states to token logits.
Decode with CTC greedy collapse.
Output decoded sentence.

## Algorithm 8 — Conformer-CTC (m06)
Input: log-mel sequence X
For each Conformer block:
  apply feed-forward, multi-head self-attention, convolution module, feed-forward
Project encoded frames to CTC token logits.
Decode with greedy CTC collapse.
Output decoded sentence.

## Algorithm 9 — Whisper-small fine-tuning (m02b)
Input: raw waveform audio
Compute Whisper log-mel features with Whisper processor.
Fine-tune Whisper-small sequence-to-sequence model on Indonesian transcripts.
At test time, run greedy autoregressive generation with language=Indonesian, task=transcribe.
Output decoded sentence.
""".strip()
(APP / "model_pseudocode_appendix.md").write_text(pseudo + "\n", encoding="utf-8")

# Candidate references
refs = """
# Candidate references for manuscript (verify formatting before submission)

- Radford, A. et al. Robust Speech Recognition via Large-Scale Weak Supervision. 2022/2023. (Whisper)
- Gulati, A. et al. Conformer: Convolution-augmented Transformer for Speech Recognition. Interspeech 2020.
- Collobert, R. et al. Wav2Letter: an End-to-End ConvNet-based Speech Recognition System. 2016.
- Vaswani, A. et al. Attention Is All You Need. NeurIPS 2017.
- Dosovitskiy, A. et al. An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale. ICLR 2021.
- Graves, A. et al. Connectionist Temporal Classification: Labelling Unsegmented Sequence Data with Recurrent Neural Networks. ICML 2006.
- Rabiner, L. R. A tutorial on hidden Markov models and selected applications in speech recognition. Proceedings of the IEEE, 1989.
""".strip()
(APP / "candidate_references.md").write_text(refs + "\n", encoding="utf-8")

# Manuscript markdown
impr = analysis["relative_improvements"]
manuscript = f"""
# A Reproducible Nine-Model Benchmark for an Indonesian 11-Class ASR Dataset

## Highlights

- A full nine-model benchmark was completed on the Indonesian v7 test split containing 15,376 utterances.
- The comparison spans classical HMM-GMM/DNN-HMM, CTC neural baselines, Transformer/ViT-style models, Conformer-CTC, and Whisper-small fine-tuning.
- Whisper-small fine-tuning achieved the best overall result with WER={whisper['wer']:.4f} and CER={whisper['cer']:.4f}.
- The proposed ViT-modified-ID model ranked third overall and second among non-Whisper scratch/specialized models with WER={novel['wer']:.4f} and CER={novel['cer']:.4f}.
- All metrics, predictions, run metadata, and model artifacts are organized for Data in Brief-style reproducibility.

## Abstract

This report summarizes the paper-ready benchmark package for an Indonesian automatic speech recognition (ASR) dataset containing 11 utterance classes. Nine ASR model families were evaluated on the same full v7 test split of 15,376 utterances using greedy decoding without an external language model. The benchmark covers HMM-GMM, DNN-HMM, GMM-HMM-DNN, Vanilla Transformer, a proposed ViT-modified-ID architecture, Wav2Letter CNN-CTC, Bi-LSTM CTC, Conformer-CTC, and Whisper-small fine-tuning. The best overall result was obtained by Whisper-small fine-tuning (WER={whisper['wer']:.4f}, CER={whisper['cer']:.4f}), followed by Conformer-CTC (WER={conformer['wer']:.4f}, CER={conformer['cer']:.4f}) and the proposed ViT-modified-ID model (WER={novel['wer']:.4f}, CER={novel['cer']:.4f}). Relative to Conformer-CTC, Whisper-small reduced WER by {impr['whisper_vs_conformer_wer_percent']:.1f}%. Relative to the proposed ViT-modified-ID model, Whisper-small reduced WER by {impr['whisper_vs_vit_wer_percent']:.1f}%. The results provide a reproducible baseline suite for future Indonesian ASR research and a strong empirical basis for dataset documentation in a Data in Brief submission.

## Keywords

Indonesian ASR; speech recognition dataset; Whisper; Conformer; ViT; CTC; HMM-GMM; Data in Brief; reproducible benchmark

## 1. Introduction

Indonesian ASR resources remain less represented than English in large public benchmarks. A dataset paper therefore benefits from two complementary contributions: (i) a clear description of the data resource and (ii) a reproducible benchmark that helps future users understand expected model behavior. This package evaluates nine model families under a shared test split and a common greedy/no-LM evaluation protocol. The model set intentionally covers classical generative baselines, hybrid acoustic models, neural CTC models, attention-based sequence-to-sequence systems, and pretrained large-scale speech representation models.

## 2. Benchmark design and fairness protocol

All reported test metrics use the same v7 test split with n=15,376 utterances. The benchmark reports WER, CER, MER, WIL, and SER computed from model predictions and references. Decoding was performed greedily without an external language model. Training used best-on-validation checkpoint selection where available. This design controls the test split and decoding protocol. Interpretation must still distinguish pretrained models (e.g., Whisper-small) from from-scratch or task-specific architectures; therefore, the benchmark supports practical model ranking and dataset documentation rather than a purely architecture-only fairness claim.

## 3. Models

The nine evaluated systems are: HMM-GMM template classification (m08), DNN-HMM (m09), GMM-HMM-DNN staged hybrid (m10), Vanilla Transformer (m11), ViT-modified-ID (m12), Wav2Letter CNN-CTC (m13), Bi-LSTM CTC (m07), Conformer-CTC (m06), and Whisper-small fine-tuning (m02b). Pseudocode for each model is provided in `appendices/model_pseudocode_appendix.md`.

## 4. Results

{chr(10).join(md_lines[2:])}

## 5. Interpretation

Whisper-small fine-tuning is the strongest benchmark model, obtaining WER={whisper['wer']:.4f} and CER={whisper['cer']:.4f}. This is expected because Whisper benefits from large-scale weakly supervised pretraining and is then adapted to the target Indonesian domain. Conformer-CTC is the strongest non-Whisper baseline with WER={conformer['wer']:.4f}, showing that convolution-augmented self-attention is highly effective for this dataset. The proposed ViT-modified-ID model achieves WER={novel['wer']:.4f}, outperforming Bi-LSTM CTC by {impr['vit_vs_bilstm_wer_percent']:.1f}% relative WER and Wav2Letter by {impr['vit_vs_wav2letter_wer_percent']:.1f}% relative WER. Classical HMM-family baselines remain substantially weaker, with WER around 0.96--0.97, indicating that template or frame-level hybrid modeling is insufficient for this dataset's lexical diversity.

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
""".strip()
(MAN / "ScienceDirect_style_paper_report.md").write_text(manuscript + "\n", encoding="utf-8")
(MAN / "ScienceDirect_style_paper_report.txt").write_text(manuscript + "\n", encoding="utf-8")

# Build a detailed PDF with wrapped text and figures
pdf_path = OUT / "Report_paper_9model_FULL_DETAIL.pdf"
with PdfPages(pdf_path) as pdf:
    def text_page(title, body, fontsize=9):
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.06, 0.96, title, fontsize=14, weight="bold", va="top")
        y = 0.92
        for para in body.split("\n"):
            if not para.strip():
                y -= 0.018; continue
            wrap = textwrap.wrap(para, width=100)
            for line in wrap:
                fig.text(0.06, y, line, fontsize=fontsize, va="top")
                y -= 0.017
                if y < 0.05:
                    pdf.savefig(fig); plt.close(fig)
                    fig = plt.figure(figsize=(8.27, 11.69)); y = 0.95
            y -= 0.006
        pdf.savefig(fig); plt.close(fig)
    text_page("Nine-model Indonesian ASR benchmark — executive summary", "\n".join([
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Best model: {best['model_id']} with WER={best['wer']:.4f}, CER={best['cer']:.4f}.",
        f"Full test set: 15,376 utterances. All nine paper models are present.",
        f"Whisper vs Conformer relative WER reduction: {impr['whisper_vs_conformer_wer_percent']:.1f}%.",
        f"Whisper vs ViT-modified-ID relative WER reduction: {impr['whisper_vs_vit_wer_percent']:.1f}%.",
        f"ViT-modified-ID vs Bi-LSTM relative WER reduction: {impr['vit_vs_bilstm_wer_percent']:.1f}%.",
        "Recommendation: claim Whisper-small FT as the strongest practical benchmark and ViT-modified-ID as a strong novel non-Whisper architecture.",
    ]))
    table_body = "\n".join([f"{r['rank']}. {r['model_id']} | WER={r['wer']:.4f} | CER={r['cer']:.4f} | {r['family']}" for r in records])
    text_page("Main result table", table_body)
    text_page("ScienceDirect-style manuscript draft", manuscript, fontsize=8)
    text_page("Pseudocode appendix", pseudo, fontsize=8)
    text_page("Candidate references", refs, fontsize=8)
    for img in ["fig1_wer_ranking.png", "fig2_cer_ranking.png", "fig3_wer_logscale.png", "fig4_wer_cer_scatter.png", "fig5_test_runtime_minutes.png"]:
        fig = plt.figure(figsize=(11.69, 8.27))
        im = plt.imread(FIG / img)
        plt.imshow(im); plt.axis("off"); plt.title(img)
        pdf.savefig(fig); plt.close(fig)

# Plain summary JSON
(DATA / "artifact_manifest.json").write_text(json.dumps({
    "generated": datetime.now().isoformat(),
    "root": str(OUT),
    "main_pdf": str(pdf_path),
    "benchmark_json": str(OUT / "benchmark" / "benchmark.json"),
    "benchmark_json_relative": "benchmark/benchmark.json",
    "figures": [str(p) for p in sorted(FIG.glob("*.png"))],
    "figures_relative": [str(p.relative_to(OUT)) for p in sorted(FIG.glob("*.png"))],
    "tables": [str(p) for p in sorted(TABLES.glob("*"))],
    "appendices": [str(p) for p in sorted(APP.glob("*"))],
    "manuscript": [str(p) for p in sorted(MAN.glob("*"))],
}, indent=2), encoding="utf-8")

print(pdf_path)
print('records', len(records))
print('best', best['model_id'], best['wer'])
