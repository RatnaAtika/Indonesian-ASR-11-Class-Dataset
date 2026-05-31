"""Aggregate 9 paper-model test results into single benchmark report.

Reads test_paper.json from each of the 9 paper models + secondary models
(if present), produces:
  - reports/paper_benchmark/benchmark.json    \u2014 SINGLE source of truth for AI agent
  - reports/paper_benchmark/benchmark.md      \u2014 human-readable
  - reports/paper_benchmark/benchmark_table.csv \u2014 paper Table 1 raw data
  - reports/paper_benchmark/paper_table.tex   \u2014 LaTeX \\input{}-able
  - reports/paper_benchmark/sample_predictions.md \u2014 per-model 10 samples
                                                  for paper Appendix
  - reports/paper_benchmark/training_summary.md \u2014 hyperparameters + env
                                                  per model

The benchmark.json adalah file utama untuk AI agent menulis paper. Schema:
{
  "generated": "ISO timestamp",
  "n_paper_models": 9,
  "n_total_models": <int>,
  "missing_paper_models": [...],
  "models": [<TestResult>, ...],
  "paper_table": [...],
  "best_model": {"model_id": ..., "wer": ..., "cer": ...},
  "ranked_by_wer": [...]
}

Usage:
    python3 aggregate_paper_test_results.py
    python3 aggregate_paper_test_results.py --out-dir reports/paper_benchmark
"""
from __future__ import annotations
import argparse, csv, json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

PROJECT = Path(__file__).parent
TRAINING = PROJECT / "training"
TC = PROJECT / "training_conventional"


# 9 paper models + 5 secondary (already-trained / ready-to-train)
PAPER_MODELS = [
    # (slot_id, search_paths_for_test_paper.json, family, paper_position, is_user_novel)
    ("m08-hmm-gmm",            [TC/"m08_hmm_gmm/runs"],            "HMM-GMM (classical)",                1, False),
    ("m09-dnn-hmm",            [TC/"m09_dnn_hmm/runs"],            "DNN-HMM (hybrid)",                   2, False),
    ("m10-gmm-hmm-dnn",        [TC/"m10_gmm_hmm_dnn/runs"],        "GMM-HMM-DNN (3-stage)",              3, False),
    ("m11-vanilla-transformer",[TC/"m11_vanilla_transformer/runs"],"Vanilla Transformer (Vaswani 2017)", 4, False),
    ("m12-vit-modified-ID",    [TC/"m12_vit_modified/runs"],       "ViT-modified-ID (Ratna 2026)",       5, True),  # \u2606 NOVEL
    ("m13-wav2letter",         [TC/"m13_wav2letter_cnn/runs"],     "Wav2Letter CNN-CTC (Collobert 2016)",6, False),
    ("m07-bilstm-ctc",         [TRAINING/"m07_bilstm_ctc/runs"],   "Bi-LSTM CTC",                        7, False),
    ("m06-conformer-ctc",      [TRAINING/"m06_conformer_ctc/runs"],"Conformer-CTC (Gulati 2020)",        8, False),
    ("m02b-whisper-small-ft", [TRAINING/"m02b_whisper_medium_ft/runs"],"Whisper-small FT (Radford 2022)", 9, False),
]

SECONDARY_MODELS = [
    ("m01-whisper-tiny",   [TRAINING/"m01_whisper_tiny/runs"],    "Whisper-tiny FT",          False),
    ("m02-whisper-small",  [TRAINING/"m02_whisper_small/runs"],   "Whisper-small FT",         False),
    ("m03-w2v2-xlsr-300m", [TRAINING/"m03_wav2vec2_xlsr_300m/runs"], "wav2vec2-XLS-R-300M FT", False),
    ("m04-cahya-w2v2-id",  [TRAINING/"m04_cahya_wav2vec2_id/runs"],"cahya-w2v2-id FT",        False),
    ("m05-mms-1b-adapter", [TRAINING/"m05_mms_1b_adapter/runs"],  "MMS-1B adapter FT",        False),
    ("m14-jasper-mini",    [TC/"m14_jasper_cnn/runs"],            "Jasper-mini CNN-CTC",      False),
]


def find_latest_test_json(search_paths: List[Path]) -> Optional[Path]:
    """Pick the latest test_paper.json across run_paper_* / run_full_* / run_smoke_*."""
    candidates = []
    for sp in search_paths:
        if not sp.exists():
            continue
        for child in sp.iterdir():
            if not child.is_dir():
                continue
            tj = child / "test_results" / "test_paper.json"
            if tj.exists():
                candidates.append(tj)
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def load_test_result(path: Path) -> Optional[Dict]:
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"  [warn] cannot load {path}: {e}")
        return None


def fmt(v, p=4, default="n/a"):
    if v is None:
        return default
    try:
        return f"{float(v):.{p}f}"
    except Exception:
        return default


def aggregate(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    
    paper_results = []
    secondary_results = []
    missing_paper = []
    missing_secondary = []
    
    print("[aggregate] scanning paper models ...")
    for slot_id, paths, family, pos, is_novel in PAPER_MODELS:
        tj = find_latest_test_json(paths)
        if tj is None:
            print(f"  \u26a0 missing: {slot_id}")
            missing_paper.append(slot_id)
            paper_results.append({
                "model_id": slot_id, "family": family, "paper_position": pos,
                "is_user_novel": is_novel, "is_paper_model": True,
                "status": "MISSING", "test_json": None,
                "metrics": None, "checkpoint": None,
            })
        else:
            r = load_test_result(tj)
            if r:
                r["model_id"] = slot_id
                r["family"] = family
                r["paper_position"] = pos
                r["is_user_novel"] = is_novel
                r["status"] = "OK"
                r["test_json"] = str(tj)
                paper_results.append(r)
                print(f"  \u2713 {slot_id}: WER={r.get('metrics', {}).get('wer'):.4f}")
    
    print("\n[aggregate] scanning secondary models ...")
    for slot_id, paths, family, is_novel in SECONDARY_MODELS:
        tj = find_latest_test_json(paths)
        if tj is None:
            missing_secondary.append(slot_id)
            secondary_results.append({
                "model_id": slot_id, "family": family,
                "is_paper_model": False, "is_user_novel": is_novel,
                "status": "MISSING", "test_json": None,
                "metrics": None,
            })
        else:
            r = load_test_result(tj)
            if r:
                r["is_paper_model"] = False
                r["is_user_novel"] = is_novel
                r["status"] = "OK"
                r["test_json"] = str(tj)
                secondary_results.append(r)
                print(f"  \u2713 {slot_id}")
    
    # Find best paper model
    valid_paper = [r for r in paper_results
                   if r.get("metrics") and r["metrics"].get("wer") is not None]
    best_model = None
    if valid_paper:
        best = min(valid_paper, key=lambda r: r["metrics"]["wer"])
        best_model = {
            "model_id": best["model_id"], "family": best.get("family"),
            "wer": best["metrics"]["wer"], "cer": best["metrics"]["cer"],
            "is_user_novel": best.get("is_user_novel", False),
            "test_json": best.get("test_json"),
        }
    
    ranked = sorted(valid_paper, key=lambda r: r["metrics"]["wer"])
    
    # Master JSON (single source for AI agent)
    benchmark = {
        "generated": datetime.now().isoformat(),
        "scope": "Paper Section 5 (Results) + Table 1 + Appendix B",
        "target_journal": "Data in Brief (Elsevier, ISSN 2352-3409)",
        "n_paper_models": 9,
        "n_paper_models_present": len(valid_paper),
        "n_secondary_models": len(SECONDARY_MODELS),
        "n_secondary_models_present": len([r for r in secondary_results
                                            if r.get("metrics") and r["metrics"].get("wer") is not None]),
        "missing_paper_models": missing_paper,
        "missing_secondary_models": missing_secondary,
        "best_paper_model": best_model,
        "paper_models_ranked_by_wer": [
            {"rank": i + 1, "model_id": r["model_id"], "family": r.get("family"),
             "wer": r["metrics"]["wer"], "cer": r["metrics"]["cer"],
             "is_user_novel": r.get("is_user_novel", False)}
            for i, r in enumerate(ranked)
        ],
        "paper_models": paper_results,
        "secondary_models": secondary_results,
    }
    
    bench_json = out_dir / "benchmark.json"
    bench_json.write_text(json.dumps(benchmark, indent=2, default=str, ensure_ascii=False),
                          encoding="utf-8")
    print(f"\n  \u2713 {bench_json}")
    
    # Markdown report
    md = [
        "# Paper Benchmark Report \u2014 9-Model Comparison on Indonesian v7 Test Set",
        "",
        f"**Generated**: {benchmark['generated']}",
        f"**Target journal**: {benchmark['target_journal']}",
        f"**Scope**: {benchmark['scope']}",
        f"**Test set**: 15,376 utterances (full v7 test split)",
        "",
        "## Status",
        "",
        f"- Paper models present: **{benchmark['n_paper_models_present']} / 9**",
        f"- Secondary models present: {benchmark['n_secondary_models_present']} / {benchmark['n_secondary_models']}",
    ]
    if missing_paper:
        md.append(f"- \u26a0 **Missing paper models**: {', '.join(missing_paper)}")
    md.append("")
    
    if best_model:
        md += [
            "## Best Paper Model",
            "",
            f"- **{best_model['model_id']}** \u2014 {best_model.get('family', '')}",
            f"  - WER: **{best_model['wer']:.4f}**",
            f"  - CER: **{best_model['cer']:.4f}**",
            f"  - User novel architecture: " + ("YES ☆" if best_model['is_user_novel'] else "no"),
            "",
        ]
    
    md += [
        "## Paper Table 1 \u2014 9-Model Comparison (greedy decoding, no LM, full test set)",
        "",
        "| Rank | Slot | Family | Params (M) | WER | CER | MER | WIL | SER | Wall (s) | GPU MB | Best train epoch | Status |",
        "|-----:|------|--------|-----------:|----:|----:|----:|----:|----:|---------:|-------:|-----------------:|--------|",
    ]
    for i, r in enumerate(paper_results):
        m = r.get("metrics") or {}
        cfg = r.get("config") or {}
        params_m = "n/a"
        # Try to extract params count from training_meta or known defaults
        rank_str = "-"
        for j, rr in enumerate(ranked):
            if rr["model_id"] == r["model_id"]:
                rank_str = str(j + 1)
                break
        novel_marker = " \u2606" if r.get("is_user_novel") else ""
        md.append(
            f"| {rank_str} | `{r['model_id']}{novel_marker}` | {r.get('family', '')} | {params_m} "
            f"| {fmt(m.get('wer'))} | {fmt(m.get('cer'))} | {fmt(m.get('mer'))} "
            f"| {fmt(m.get('wil'))} | {fmt(m.get('ser'))} "
            f"| {fmt(r.get('wall_time_sec'), 1)} | {fmt(r.get('peak_gpu_mb'), 0)} "
            f"| {r.get('best_train_epoch') or 'n/a'} | {r.get('status')} |"
        )
    
    md += [
        "",
        "\u2606 = User's novel architecture (Ratna 2026, this paper's first public report)",
        "",
        "## Per-Model Hyperparameter Summary",
        "",
        "| Model | Epochs trained | Best train epoch | Best train WER | Test WER | Test CER |",
        "|-------|---------------:|-----------------:|--------------:|---------:|---------:|",
    ]
    for r in paper_results:
        m = r.get("metrics") or {}
        md.append(
            f"| `{r['model_id']}` | {r.get('n_epochs_trained', 'n/a')} "
            f"| {r.get('best_train_epoch') or 'n/a'} "
            f"| {fmt(r.get('best_train_wer'))} "
            f"| {fmt(m.get('wer'))} | {fmt(m.get('cer'))} |"
        )
    
    md += [
        "",
        "## How AI Agent Should Read This",
        "",
        "1. `benchmark.json` adalah single source of truth.",
        "2. Untuk paper Section 5 (Results), gunakan `paper_models_ranked_by_wer` dan `best_paper_model`.",
        "3. Untuk paper Table 1, gunakan field `paper_models[*].metrics` + `paper_models[*].family`.",
        "4. Untuk paper Appendix A (sample predictions), gunakan `paper_models[*].sample_predictions`.",
        "5. Untuk paper Section 4.2 (Experimental Setup), gunakan `paper_models[*].config` + `paper_models[*].training_meta`.",
        "6. Setiap model punya `predictions_csv` path untuk full predictions.",
        "7. Status `MISSING` artinya model belum di-test. Re-run testing per RUN_GUIDE.md PAPER-GRADE section.",
        "",
        "## Files",
        "",
        "- `benchmark.json` \u2014 master file (all data + metadata)",
        "- `benchmark.md` \u2014 this file (human-readable)",
        "- `benchmark_table.csv` \u2014 paper Table 1 raw data",
        "- `paper_table.tex` \u2014 LaTeX `\\input{}` ready",
        "- `sample_predictions.md` \u2014 per-model 10 samples for Appendix",
        "- `training_summary.md` \u2014 hyperparameters + env per-model",
    ]
    
    (out_dir / "benchmark.md").write_text("\n".join(md), encoding="utf-8")
    print(f"  \u2713 {out_dir / 'benchmark.md'}")
    
    # Paper table CSV
    csv_path = out_dir / "benchmark_table.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rank", "slot", "family", "wer", "cer", "mer", "wil", "ser",
                    "wall_time_sec", "peak_gpu_mb", "n_epochs_trained",
                    "best_train_epoch", "best_train_wer", "is_user_novel", "status"])
        for r in paper_results:
            m = r.get("metrics") or {}
            rank_str = ""
            for j, rr in enumerate(ranked):
                if rr["model_id"] == r["model_id"]:
                    rank_str = str(j + 1); break
            w.writerow([
                rank_str, r["model_id"], r.get("family", ""),
                m.get("wer"), m.get("cer"), m.get("mer"), m.get("wil"), m.get("ser"),
                r.get("wall_time_sec"), r.get("peak_gpu_mb"),
                r.get("n_epochs_trained"), r.get("best_train_epoch"),
                r.get("best_train_wer"), r.get("is_user_novel"), r.get("status"),
            ])
    print(f"  \u2713 {csv_path}")
    
    # LaTeX paper Table 1
    tex = [
        r"% Paper Table 1 \u2014 9-model benchmark on Indonesian v7 test set",
        r"% Generated by aggregate_paper_test_results.py",
        r"\begin{table*}[t]",
        r"  \centering",
        r"  \caption{Word Error Rate (WER) and Character Error Rate (CER) on the Indonesian v7 test split (n=15{,}376) for the nine ASR systems studied in this paper. All systems use greedy decoding without language model rescoring. Best result in \textbf{bold}. m12 ViT-modified-ID is the user's own novel architecture (this paper's first public report).}",
        r"  \label{tab:paper_benchmark}",
        r"  \small",
        r"  \begin{tabular}{rllrrrr}",
        r"  \hline",
        r"  Rank & Slot & Family & WER & CER & MER & WIL \\",
        r"  \hline",
    ]
    if best_model:
        for i, r in enumerate(paper_results):
            m = r.get("metrics") or {}
            rank_str = ""
            for j, rr in enumerate(ranked):
                if rr["model_id"] == r["model_id"]:
                    rank_str = str(j + 1); break
            slot = r["model_id"].replace("_", r"\_")
            if r.get("is_user_novel"):
                slot += r" $\star$"
            family = r.get("family", "").replace("_", r"\_")
            wer_s = fmt(m.get("wer"))
            cer_s = fmt(m.get("cer"))
            # Bold the best model
            if r["model_id"] == best_model["model_id"]:
                wer_s = r"\textbf{" + wer_s + r"}"
                cer_s = r"\textbf{" + cer_s + r"}"
            tex.append(
                f"  {rank_str} & {slot} & {family} & {wer_s} & {cer_s} "
                f"& {fmt(m.get('mer'))} & {fmt(m.get('wil'))} \\\\"
            )
    tex += [
        r"  \hline",
        r"  \end{tabular}",
        r"\end{table*}",
    ]
    (out_dir / "paper_table.tex").write_text("\n".join(tex), encoding="utf-8")
    print(f"  \u2713 {out_dir / 'paper_table.tex'}")
    
    # Sample predictions per-model
    sp_md = ["# Sample Predictions per Model (Paper Appendix A)\n"]
    for r in paper_results:
        sp_md.append(f"## {r['model_id']} \u2014 {r.get('family', '')}\n")
        if r.get("status") != "OK":
            sp_md.append(f"_Status: {r.get('status')}_\n")
            continue
        for i, sp in enumerate(r.get("sample_predictions") or []):
            sp_md.append(
                f"{i+1}. `[{sp.get('idx')}]` (WER={sp.get('per_sample_wer'):.3f}, "
                f"CER={sp.get('per_sample_cer'):.3f})\n"
                f"    - PRED: `{sp.get('pred', '')[:140]}`\n"
                f"    - LABEL: `{sp.get('label', '')[:140]}`\n"
            )
        sp_md.append("")
    (out_dir / "sample_predictions.md").write_text("\n".join(sp_md), encoding="utf-8")
    print(f"  \u2713 {out_dir / 'sample_predictions.md'}")
    
    # Training summary per-model
    ts_md = ["# Training Summary per Paper Model (Paper Section 4.2)\n"]
    for r in paper_results:
        ts_md.append(f"## {r['model_id']} \u2014 {r.get('family', '')}\n")
        if r.get("status") != "OK":
            ts_md.append(f"_Status: {r.get('status')}_\n")
            continue
        cfg = r.get("config") or {}
        meta = r.get("training_meta") or {}
        env = meta.get("environment", {}) if isinstance(meta, dict) else {}
        ts_md += [
            f"- Checkpoint: `{r.get('checkpoint_filename', '?')}` \u2192 best epoch {r.get('best_train_epoch')}",
            f"- Training epochs: {r.get('n_epochs_trained')}",
            f"- Best train WER: {fmt(r.get('best_train_wer'))}",
            f"- Test WER: {fmt(r.get('metrics', {}).get('wer'))}, CER: {fmt(r.get('metrics', {}).get('cer'))}",
            f"- Training meta:",
            f"  - Python: {env.get('python', '?')}",
            f"  - Torch: {env.get('torch_version', '?')}",
            f"  - CUDA device: {env.get('cuda_device', '?')}",
            f"  - Timestamp: {env.get('timestamp', '?')}",
            f"- Hyperparameters: `{json.dumps({k: v for k, v in cfg.items() if k not in ('run_dir', 'data_root', 'data_final', 'spm_model', 'data_pkl_dir')}, default=str)[:300]}...`",
            "",
        ]
    (out_dir / "training_summary.md").write_text("\n".join(ts_md), encoding="utf-8")
    print(f"  \u2713 {out_dir / 'training_summary.md'}")
    
    # Final stats
    print(f"\n[aggregate] DONE. Output: {out_dir}")
    print(f"  Paper models: {benchmark['n_paper_models_present']}/9")
    if best_model:
        print(f"  Best model: {best_model['model_id']} (WER={best_model['wer']:.4f})")
    return 0 if not missing_paper else 1


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=PROJECT / "reports" / "paper_benchmark")
    return p.parse_args()


def main():
    args = parse_args()
    return aggregate(args.out_dir)


if __name__ == "__main__":
    raise SystemExit(main())
