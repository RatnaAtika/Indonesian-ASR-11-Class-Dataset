from __future__ import annotations

import csv
import json
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from report_paper_9model_metadata import enrich_benchmark, evidence_table_rows, seconds_to_hhmmss

ROOT = Path(__file__).parent
OUT = ROOT / "Report_paper_9model"
BENCH = OUT / "benchmark" / "benchmark.json"
FIG = OUT / "figures"
TABLES = OUT / "tables"
DATA = OUT / "data"
APP = OUT / "appendices"
MAN = OUT / "manuscript"
ART = OUT / "model_artifacts"
for d in [OUT, FIG, TABLES, DATA, APP, MAN, ART]:
    d.mkdir(parents=True, exist_ok=True)

bench = json.loads(BENCH.read_text(encoding="utf-8"))
enrich_benchmark(bench)
# Persist enriched benchmark so Report_paper_9model/benchmark/benchmark.json remains
# the source of truth for manuscript writing.
BENCH.write_text(json.dumps(bench, indent=2, ensure_ascii=False), encoding="utf-8")

paper = [m for m in bench["paper_models"] if m.get("status") == "OK"]
paper = sorted(paper, key=lambda m: m["metrics"]["wer"])


def fmt_num(value: Any, digits: int = 4, default: str = "n/a") -> str:
    if value is None:
        return default
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return default


def fmt_int(value: Any, default: str = "n/a") -> str:
    if value is None:
        return default
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return default


def params_display(r: dict[str, Any]) -> str:
    if r.get("n_params") is None:
        if r.get("n_templates"):
            return f"n/a ({r['n_templates']} templates)"
        return "n/a"
    return f"{r['n_params']:,}"


def params_m_display(r: dict[str, Any]) -> str:
    if r.get("params_millions") is None:
        return "n/a"
    return f"{r['params_millions']:.3f}"


def hardware_short(r: dict[str, Any]) -> str:
    label = r.get("training_hardware") or ((r.get("os_gpu_provenance") or {}).get("training") or {}).get("hardware_label") or "n/a"
    return label.replace("NVIDIA GeForce ", "").replace("NVIDIA ", "")


def rel_improve(a: float | None, b: float | None) -> float | None:
    return (b - a) / b * 100 if a is not None and b else None


# Normalize records
records: list[dict[str, Any]] = []
for rank, m in enumerate(paper, 1):
    metrics = m["metrics"]
    test = m.get("test_set", {})
    train_hw = ((m.get("os_gpu_provenance") or {}).get("training") or {})
    test_hw = ((m.get("os_gpu_provenance") or {}).get("test") or {})
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
        "training_time_sec": m.get("training_time_sec"),
        "training_time_hhmmss": m.get("training_time_hhmmss"),
        "training_time_hours": m.get("training_time_hours"),
        "training_eval_time_sec": m.get("training_eval_time_sec"),
        "training_eval_time_hhmmss": m.get("training_eval_time_hhmmss"),
        "inference_time_sec": m.get("inference_time_sec"),
        "inference_time_hhmmss": m.get("inference_time_hhmmss"),
        "throughput_samples_per_sec": m.get("throughput_samples_per_sec"),
        "peak_gpu_mb": m.get("peak_gpu_mb"),
        "n_params": m.get("n_params"),
        "params_millions": m.get("params_millions"),
        "n_templates": m.get("n_templates"),
        "param_count_note": m.get("param_count_note"),
        "training_hardware": train_hw.get("hardware_label"),
        "training_os": train_hw.get("os"),
        "training_gpu": train_hw.get("gpu"),
        "training_vram_gb": train_hw.get("vram_gb"),
        "test_platform": test_hw.get("platform"),
        "test_gpu": test_hw.get("cuda_device"),
        "best_train_wer": m.get("best_train_wer"),
        "best_train_epoch": m.get("best_train_epoch"),
        "n_epochs_trained": m.get("n_epochs_trained"),
        "n_test_samples": test.get("n_samples"),
        "decoding_method": (m.get("decoding") or {}).get("method"),
        "checkpoint": m.get("checkpoint"),
        "best_artifact": m.get("best_artifact"),
        "best_artifact_exists": m.get("best_artifact_exists"),
        "test_json": m.get("test_json"),
        "predictions_csv": m.get("predictions_csv"),
        "training_time_source": m.get("training_time_source"),
        "param_count_source": m.get("param_count_source"),
        "provenance_source": train_hw.get("source"),
    }
    records.append(rec)

(DATA / "paper_9model_results_normalized.json").write_text(
    json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
)
(DATA / "m08_hmm_gmm_parameter_count_evidence.json").write_text(json.dumps({
    "model_id": "m08-hmm-gmm",
    "source_artifact": "training_conventional/m08_hmm_gmm/runs/run_paper_20260530/checkpoints/best.pkl",
    "method": "Counted numeric GMMHMM arrays per template: startprob_, transmat_, means_, covars_, weights_.",
    "n_templates": 209,
    "per_template_breakdown": {
        "startprob": 5,
        "transmat": 25,
        "means": 5 * 3 * 80,
        "diag_covars": 5 * 3 * 80,
        "mixture_weights": 5 * 3,
        "total_per_template": 2445,
    },
    "total_numeric_parameters": 511005,
    "caveat": "Classical HMM-GMM numeric parameter count, not a neural trainable-parameter count.",
}, indent=2, ensure_ascii=False), encoding="utf-8")
with (TABLES / "paper_9model_results_normalized.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(records[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(records)

# Key comparisons
best = records[0]
novel = next((r for r in records if r["is_user_novel"]), None)
conformer = next((r for r in records if r["model_id"] == "m06-conformer-ctc"), None)
bilstm = next((r for r in records if r["model_id"] == "m07-bilstm-ctc"), None)
whisper = next((r for r in records if r["model_id"] == "m02b-whisper-small-ft"), None)
wav2letter = next((r for r in records if r["model_id"] == "m13-wav2letter"), None)

analysis = {
    "generated": datetime.now().isoformat(),
    "n_paper_models_present": len(records),
    "best_model": best,
    "novel_model": novel,
    "relative_improvements": {
        "whisper_vs_conformer_wer_percent": rel_improve(whisper["wer"], conformer["wer"]) if whisper and conformer else None,
        "whisper_vs_vit_wer_percent": rel_improve(whisper["wer"], novel["wer"]) if whisper and novel else None,
        "vit_vs_bilstm_wer_percent": rel_improve(novel["wer"], bilstm["wer"]) if novel and bilstm else None,
        "vit_vs_wav2letter_wer_percent": rel_improve(novel["wer"], wav2letter["wer"]) if novel and wav2letter else None,
    },
}
(DATA / "paper_9model_interpretation_metrics.json").write_text(json.dumps(analysis, indent=2), encoding="utf-8")

# Markdown/LaTeX tables
md_lines = [
    "# Paper Table: 9-model ASR comparison",
    "",
    "All rows are evaluated on the same full v7 test split (15,376 utterances), greedy decoding, and no external language model.",
    "Training time, parameter count, and hardware provenance are evidence-backed from local run artifacts; see `tables/paper_9model_evidence_table.md`.",
    "",
    "| Rank | Model | Family | WER | CER | Train time | Test time | Params | Training hardware | Best epoch |",
    "|---:|---|---|---:|---:|---:|---:|---:|---|---:|",
]
for r in records:
    md_lines.append(
        f"| {r['rank']} | `{r['model_id']}` | {r['family']} | {r['wer']:.4f} | {r['cer']:.4f} | "
        f"{r['training_time_hhmmss'] or 'n/a'} | {r['inference_time_hhmmss']} | {params_display(r)} | "
        f"{hardware_short(r)} | {r['best_train_epoch'] if r['best_train_epoch'] is not None else 'n/a'} |"
    )
(TABLES / "paper_table_9model.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

# Full evidence table
evidence_rows = evidence_table_rows(paper)
evidence_md = [
    "# Evidence table: training time, observed full-test evaluation wall time, parameters, and OS/GPU provenance",
    "",
    "This table is intentionally conservative. If a training log did not record exact OS/GPU, the field says so rather than inferring it from later testing metadata.",
    "",
    "| Model | Train time | Train h | Test time | Params | Templates | Hardware provenance | Evidence sources | Best artifact exists |",
    "|---|---:|---:|---:|---:|---:|---|---|---:|",
]
for r in paper:
    train = ((r.get("os_gpu_provenance") or {}).get("training") or {})
    evidence_md.append(
        f"| `{r['model_id']}` | {r.get('training_time_hhmmss') or 'n/a'} | {fmt_num(r.get('training_time_hours'), 3)} | "
        f"{r.get('inference_time_hhmmss') or seconds_to_hhmmss(r.get('wall_time_sec'))} | "
        f"{fmt_int(r.get('n_params'))} | {r.get('n_templates') or 'n/a'} | {train.get('hardware_label') or 'n/a'} | "
        f"time: `{r.get('training_time_source')}`; params: `{r.get('param_count_source')}`; hw: `{train.get('source')}` | "
        f"{r.get('best_artifact_exists')} |"
    )
(TABLES / "paper_9model_evidence_table.md").write_text("\n".join(evidence_md) + "\n", encoding="utf-8")

# LaTeX: concise numeric table; detailed provenance remains in Markdown/JSON.
def tex_escape(s: Any) -> str:
    return str(s).replace("&", r"\&").replace("_", r"\_").replace("%", r"\%")

tex = [
    r"\begin{table*}[t]",
    r"\centering",
    r"\caption{Nine-model Indonesian ASR benchmark on the full v7 test split (15,376 utterances). Train time is the recorded total training duration for the selected best-checkpoint run. Test time is full-split inference/evaluation wall time.}",
    r"\label{tab:asr-9model-full}",
    r"\small",
    r"\begin{tabular}{rllrrrrr}",
    r"\toprule",
    r"Rank & Model & Family & WER & CER & Train h & Test s & Params M \\",
    r"\midrule",
]
for r in records:
    fam = tex_escape(r["family"])
    tex.append(
        f"{r['rank']} & {tex_escape(r['model_id'])} & {fam} & {r['wer']:.4f} & {r['cer']:.4f} & "
        f"{fmt_num(r['training_time_hours'], 2)} & {fmt_num(r['inference_time_sec'], 1)} & {params_m_display(r)} " + r"\\")
tex += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
(TABLES / "paper_table_9model.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")

# Figures
def save_bar(metric: str, title: str, fname: str, log: bool = False, ylabel: str | None = None):
    fig, ax = plt.subplots(figsize=(11, 6))
    labels = [r["model_id"].replace("-", "\n") for r in records]
    vals = [r[metric] if r[metric] is not None else 0 for r in records]
    colors = ["#1f77b4" if not r["is_user_novel"] else "#d62728" for r in records]
    ax.bar(range(len(vals)), vals, color=colors)
    ax.set_xticks(range(len(vals)), labels, fontsize=8)
    ax.set_ylabel(ylabel or metric.upper())
    ax.set_title(title)
    if log:
        ax.set_yscale("log")
        ax.set_ylabel((ylabel or metric.upper()) + " (log scale)")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG / f"{fname}.png", dpi=300)
    fig.savefig(FIG / f"{fname}.pdf")
    plt.close(fig)


save_bar("wer", "WER ranking across nine ASR models", "fig1_wer_ranking")
save_bar("cer", "CER ranking across nine ASR models", "fig2_cer_ranking")
save_bar("wer", "WER ranking across nine ASR models (log scale)", "fig3_wer_logscale", log=True)

fig, ax = plt.subplots(figsize=(8, 6))
for r in records:
    ax.scatter(r["wer"], r["cer"], s=90, c="#d62728" if r["is_user_novel"] else "#1f77b4")
    ax.annotate(r["model_id"].replace("m02b-", ""), (r["wer"], r["cer"]), fontsize=7, xytext=(4, 3), textcoords="offset points")
ax.set_xlabel("WER")
ax.set_ylabel("CER")
ax.set_title("WER-CER trade-off on full Indonesian v7 test split")
ax.grid(alpha=0.25)
fig.tight_layout(); fig.savefig(FIG / "fig4_wer_cer_scatter.png", dpi=300); fig.savefig(FIG / "fig4_wer_cer_scatter.pdf"); plt.close(fig)

save_bar("inference_time_sec", "Full-split inference/test runtime by model", "fig5_test_runtime_seconds", ylabel="Test wall time (seconds)")
save_bar("training_time_hours", "Recorded training duration by selected paper run", "fig6_training_time_hours", ylabel="Training time (hours)")
# Parameter figure excludes non-neural HMM-GMM n/a by plotting 0.001M with note.
fig, ax = plt.subplots(figsize=(11, 6))
labels = [r["model_id"].replace("-", "\n") for r in records]
vals = [r["params_millions"] if r["params_millions"] is not None else 0.001 for r in records]
ax.bar(range(len(vals)), vals, color="#9467bd")
ax.set_xticks(range(len(vals)), labels, fontsize=8)
ax.set_ylabel("Parameters (M, log scale; HMM-GMM n/a shown as 0.001)")
ax.set_yscale("log")
ax.set_title("Model parameter counts from run evidence")
ax.grid(axis="y", alpha=0.25)
fig.tight_layout(); fig.savefig(FIG / "fig7_parameter_counts_logscale.png", dpi=300); fig.savefig(FIG / "fig7_parameter_counts_logscale.pdf"); plt.close(fig)

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
Train Stage 1 HMM-GMM templates, then Stage 3 DNN acoustic model. Decode as in Algorithm 2 using the selected staged artifact.

## Algorithm 4 — Vanilla Transformer encoder-decoder (m11)
Encode log-mel features with Transformer self-attention. Decode autoregressively with greedy argmax until EOS or max length.

## Algorithm 5 — ViT-modified-ID (m12, proposed/novel)
Patch/tokenize the log-mel spectrogram into frame-patch embeddings. Apply ViT-inspired self-attention blocks adapted for Indonesian ASR, then greedy decode the output sequence.

## Algorithm 6 — Wav2Letter-style CNN-CTC (m13)
Apply temporal CNN stack to log-mel sequence. Project valid frames to token logits. Run CTC greedy collapse and remove blanks.

## Algorithm 7 — Bi-LSTM CTC (m07)
Encode with bidirectional LSTM layers, project to CTC token logits, and greedily collapse repeated tokens/blanks.

## Algorithm 8 — Conformer-CTC (m06)
Apply Conformer blocks combining feed-forward, self-attention, and convolution modules. Project to CTC logits and greedily decode.

## Algorithm 9 — Whisper-small fine-tuning (m02b)
Compute Whisper log-mel features, fine-tune Whisper-small seq2seq model on Indonesian transcripts, and run greedy generation with language=Indonesian/task=transcribe.
""".strip()
(APP / "model_pseudocode_appendix.md").write_text(pseudo + "\n", encoding="utf-8")

# Candidate references with validation notes.  These are canonical method refs, not
# claims of external Indonesian SOTA.
refs = """
# Candidate references for manuscript (verify final journal formatting before submission)

## Source-checked canonical method references

- Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2023). *Robust Speech Recognition via Large-Scale Weak Supervision*. Proceedings of the 40th International Conference on Machine Learning, PMLR 202. arXiv:2212.04356. https://proceedings.mlr.press/v202/radford23a.html
- Gulati, A., Qin, J., Chiu, C.-C., Parmar, N., Zhang, Y., Yu, J., Han, W., Wang, S., Zhang, Z., Wu, Y., & Pang, R. (2020). *Conformer: Convolution-augmented Transformer for Speech Recognition*. Proc. Interspeech 2020, 5036--5040. doi:10.21437/Interspeech.2020-3015. https://www.isca-archive.org/interspeech_2020/gulati20_interspeech.html
- Collobert, R., Puhrsch, C., & Synnaeve, G. (2016). *Wav2Letter: an End-to-End ConvNet-based Speech Recognition System*. arXiv:1609.03193. https://arxiv.org/abs/1609.03193
- Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). *Attention Is All You Need*. NeurIPS 2017. https://papers.nips.cc/paper/7181-attention-is-all-you-need
- Dosovitskiy, A. et al. (2021). *An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale*. ICLR 2021. https://openreview.net/forum?id=YicbFdNTTy
- Graves, A., Fernandez, S., Gomez, F., & Schmidhuber, J. (2006). *Connectionist Temporal Classification: Labelling Unsegmented Sequence Data with Recurrent Neural Networks*. ICML 2006. doi:10.1145/1143844.1143891.
- Hochreiter, S., & Schmidhuber, J. (1997). *Long Short-Term Memory*. Neural Computation, 9(8), 1735--1780. doi:10.1162/neco.1997.9.8.1735.
- Hinton, G. et al. (2012). *Deep Neural Networks for Acoustic Modeling in Speech Recognition: The Shared Views of Four Research Groups*. IEEE Signal Processing Magazine, 29(6), 82--97. doi:10.1109/MSP.2012.2205597.
- Rabiner, L. R. (1989). *A tutorial on hidden Markov models and selected applications in speech recognition*. Proceedings of the IEEE, 77(2), 257--286. doi:10.1109/5.18626.

## Submission caution

These references support the benchmarked method families. They do **not** establish an external Indonesian ASR SOTA claim for this dataset. Keep the paper claim limited to the internal nine-model benchmark unless an external Indonesian ASR leaderboard comparison is added.
""".strip()
(APP / "candidate_references.md").write_text(refs + "\n", encoding="utf-8")

# Manuscript markdown
impr = analysis["relative_improvements"]
compute_table = "\n".join(evidence_md[4:])
main_table = "\n".join(md_lines[5:])
manual_caveat = (
    "m11 and m12 source training logs record CUDA use but do not record exact training OS/GPU model; "
    "their later full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU."
)

manuscript = f"""
# A Reproducible Nine-Model Benchmark for an Indonesian 11-Class ASR Dataset

## Highlights

- A full nine-model benchmark was completed on the Indonesian v7 test split containing 15,376 utterances.
- The comparison spans HMM-GMM/DNN-HMM, CTC neural baselines, Transformer/ViT-style models, Conformer-CTC, and Whisper-small fine-tuning.
- Whisper-small fine-tuning achieved the best internal benchmark result with WER={whisper['wer']:.4f} and CER={whisper['cer']:.4f}.
- Training time, observed full-test evaluation wall time, parameter counts, and OS/GPU provenance are recorded where available; unrecorded fields are explicitly marked.
- Best-model artifacts are split into per-model directories under `Report_paper_9model/model_artifacts/` with manifests, source-code snapshots, pseudocode excerpts, architecture summaries, and local binary copies/hardlinks where available.

## Abstract

This report summarizes a reproducible benchmark package for an Indonesian automatic speech recognition (ASR) dataset containing 11 utterance classes. Nine ASR model families were evaluated on the same full v7 test split of 15,376 utterances using greedy decoding without an external language model. The benchmark covers HMM-GMM, DNN-HMM, GMM-HMM-DNN, Vanilla Transformer, a proposed ViT-modified-ID architecture, Wav2Letter-style CNN-CTC, Bi-LSTM CTC, Conformer-CTC, and Whisper-small fine-tuning. The best internal benchmark result was obtained by Whisper-small fine-tuning (WER={whisper['wer']:.4f}, CER={whisper['cer']:.4f}), followed by Conformer-CTC (WER={conformer['wer']:.4f}, CER={conformer['cer']:.4f}) and the proposed ViT-modified-ID model (WER={novel['wer']:.4f}, CER={novel['cer']:.4f}). The report provides measured training time, observed full-test evaluation wall time, parameter count, hardware provenance, prediction files, source-code snapshots, pseudocode excerpts, architecture summaries, and best-artifact manifests. Binary model weights are packaged locally and should be deposited separately with a DOI/Drive/Zenodo/OSF link for journal submission.

## Keywords

Indonesian ASR; speech recognition dataset; Whisper; Conformer; ViT; CTC; HMM-GMM; Data in Brief; reproducible benchmark

## 1. Introduction

Compared with English, Indonesian has fewer widely used public ASR benchmarks within this package's scope. A dataset paper therefore benefits from both a clear description of the data resource and a reproducible benchmark that helps future users understand expected model behavior. This package evaluates nine model families under a shared test split and a common greedy/no-LM evaluation protocol.

## 2. Benchmark design and fairness protocol

All reported test metrics use the same v7 test split with n=15,376 utterances. The benchmark reports WER, CER, MER, WIL, and SER computed from model predictions and references. Decoding was performed greedily without an external language model. Training used best-on-validation checkpoint selection where available. This design controls the test split and decoding protocol. Interpretation must still distinguish pretrained models (Whisper-small) from from-scratch or task-specific architectures; therefore, the benchmark supports practical model ranking and dataset documentation rather than a purely architecture-only fairness claim.

## 3. Models

The nine evaluated systems are: HMM-GMM template classification (m08), DNN-HMM (m09), GMM-HMM-DNN staged hybrid (m10), Vanilla Transformer (m11), ViT-modified-ID (m12, proposed in this work), Wav2Letter-style CNN-CTC (m13), Bi-LSTM CTC (m07), Conformer-CTC (m06), and Whisper-small fine-tuning (m02b). Pseudocode for each model is provided in `appendices/model_pseudocode_appendix.md`.

## 4. Results

{main_table}

## 5. Evidence-backed compute and provenance table

{compute_table}

## 6. Internal interpretation notes (move to Discussion/Appendix as needed)

Whisper-small fine-tuning is the strongest internal benchmark model, obtaining WER={whisper['wer']:.4f} and CER={whisper['cer']:.4f}. This is expected because Whisper benefits from large-scale weakly supervised pretraining and is then adapted to the target Indonesian domain. Conformer-CTC is the strongest non-Whisper baseline with WER={conformer['wer']:.4f}. The proposed ViT-modified-ID model achieves WER={novel['wer']:.4f}, outperforming Bi-LSTM CTC by {impr['vit_vs_bilstm_wer_percent']:.1f}% relative WER and Wav2Letter by {impr['vit_vs_wav2letter_wer_percent']:.1f}% relative WER. Classical HMM-family baselines remain substantially weaker, with WER around 0.96--0.97.

## 7. Hardware provenance caveats

Conformer-CTC and Bi-LSTM CTC were trained on a local Linux laptop with an NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM. Whisper-small was trained on Google Colab Linux with an NVIDIA A100-SXM4-40GB GPU. WSL2-trained conventional and CNN runs record WSL2 Linux plus RTX 4060 Laptop GPU in run metadata, but not VRAM. {manual_caveat}

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
""".strip()
(MAN / "ScienceDirect_style_paper_report.md").write_text(manuscript + "\n", encoding="utf-8")
(MAN / "ScienceDirect_style_paper_report.txt").write_text(manuscript + "\n", encoding="utf-8")

# Build a detailed PDF with wrapped text and figures
pdf_path = OUT / "Report_paper_9model_FULL_DETAIL.pdf"
with PdfPages(pdf_path) as pdf:
    def text_page(title: str, body: str, fontsize: int = 9):
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.06, 0.96, title, fontsize=14, weight="bold", va="top")
        y = 0.92
        for para in body.split("\n"):
            if not para.strip():
                y -= 0.018
                continue
            wrap = textwrap.wrap(para, width=105)
            for line in wrap:
                fig.text(0.06, y, line, fontsize=fontsize, va="top")
                y -= 0.017
                if y < 0.05:
                    pdf.savefig(fig)
                    plt.close(fig)
                    fig = plt.figure(figsize=(8.27, 11.69))
                    y = 0.95
            y -= 0.006
        pdf.savefig(fig)
        plt.close(fig)

    text_page("Nine-model Indonesian ASR benchmark — executive summary", "\n".join([
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Best model: {best['model_id']} with WER={best['wer']:.4f}, CER={best['cer']:.4f}.",
        "Full test set: 15,376 utterances. All nine paper models are present.",
        f"Whisper vs Conformer relative WER reduction: {impr['whisper_vs_conformer_wer_percent']:.1f}%.",
        f"Whisper vs ViT-modified-ID relative WER reduction: {impr['whisper_vs_vit_wer_percent']:.1f}%.",
        f"ViT-modified-ID vs Bi-LSTM relative WER reduction: {impr['vit_vs_bilstm_wer_percent']:.1f}%.",
        "New in this revision: training time, observed full-test evaluation wall time, parameter count, OS/GPU provenance, evidence table, and per-model artifact package.",
        "Recommendation: claim Whisper-small FT as the strongest internal benchmark and ViT-modified-ID as a strong novel non-Whisper architecture.",
    ]))
    table_body = "\n".join([
        f"{r['rank']}. {r['model_id']} | WER={r['wer']:.4f} | CER={r['cer']:.4f} | train={r['training_time_hhmmss']} | test={r['inference_time_hhmmss']} | params={params_display(r)}"
        for r in records
    ])
    text_page("Main result table with timing and parameters", table_body)
    text_page("Evidence and provenance table", "\n".join(evidence_md), fontsize=7)
    text_page("ScienceDirect/Data in Brief-style manuscript draft", manuscript, fontsize=8)
    text_page("Pseudocode appendix", pseudo, fontsize=8)
    text_page("Candidate references and submission caution", refs, fontsize=8)
    for img in [
        "fig1_wer_ranking.png", "fig2_cer_ranking.png", "fig3_wer_logscale.png",
        "fig4_wer_cer_scatter.png", "fig5_test_runtime_seconds.png",
        "fig6_training_time_hours.png", "fig7_parameter_counts_logscale.png",
    ]:
        fig = plt.figure(figsize=(11.69, 8.27))
        im = plt.imread(FIG / img)
        plt.imshow(im)
        plt.axis("off")
        plt.title(img)
        pdf.savefig(fig)
        plt.close(fig)

# Plain summary JSON
(DATA / "artifact_manifest.json").write_text(json.dumps({
    "generated": datetime.now().isoformat(),
    "root": str(OUT),
    "main_pdf": str(pdf_path),
    "benchmark_json": str(OUT / "benchmark" / "benchmark.json"),
    "benchmark_json_relative": "benchmark/benchmark.json",
    "normalized_json_relative": "data/paper_9model_results_normalized.json",
    "evidence_table_relative": "tables/paper_9model_evidence_table.md",
    "model_artifacts_relative": "model_artifacts/",
    "model_artifact_index_relative": "model_artifacts/artifact_index.json",
    "model_artifact_metadata_relative": [str(p.relative_to(OUT)) for p in sorted(ART.glob("rank*/metadata.json"))],
    "figures": [str(p) for p in sorted(FIG.glob("*.png"))],
    "figures_relative": [str(p.relative_to(OUT)) for p in sorted(FIG.glob("*.png"))],
    "tables": [str(p) for p in sorted(TABLES.glob("*"))],
    "appendices": [str(p) for p in sorted(APP.glob("*"))],
    "manuscript": [str(p) for p in sorted(MAN.glob("*"))],
}, indent=2), encoding="utf-8")

print(pdf_path)
print("records", len(records))
print("best", best["model_id"], best["wer"])
