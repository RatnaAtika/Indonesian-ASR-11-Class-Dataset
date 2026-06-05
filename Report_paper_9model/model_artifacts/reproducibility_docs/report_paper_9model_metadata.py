"""Evidence-backed metadata for the nine-model paper benchmark.

This module intentionally separates measured metadata from prose generation.
Every hard-coded value below is tied to a local source artifact listed in the
``*_source`` fields.  Values should not be changed unless the source run artifact
is also updated or a new run is selected.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

PROJECT = Path(__file__).resolve().parent


def hhmmss_to_seconds(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    parts = str(value).strip().split(":")
    if len(parts) != 3:
        return None
    try:
        h, m, s = [int(p) for p in parts]
    except ValueError:
        return None
    return h * 3600 + m * 60 + s


def seconds_to_hhmmss(value: Optional[float]) -> str:
    if value is None:
        return "n/a"
    try:
        total = int(round(float(value)))
    except (TypeError, ValueError):
        return "n/a"
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def rel(path: Path | str) -> str:
    p = Path(path)
    if p.is_absolute():
        try:
            return str(p.relative_to(PROJECT))
        except ValueError:
            return str(p)
    return str(p)


# Canonical per-model evidence and provenance.  Keep model ids aligned with
# aggregate_paper_test_results.PAPER_MODELS.
MODEL_EVIDENCE: Dict[str, Dict[str, Any]] = {
    "m08-hmm-gmm": {
        "run_dir": "training_conventional/m08_hmm_gmm/runs/run_paper_20260530",
        "training_time_hhmmss": "03:17:11",
        "training_eval_time_hhmmss": "00:58:05",
        "training_time_source": "training_conventional/m08_hmm_gmm/runs/run_paper_20260530/report.md:16-17",
        "n_params": 511_005,
        "n_templates": 209,
        "param_count_note": "Classical HMM-GMM numeric parameter count computed from the selected best.pkl template bank: 209 templates x (5 start probabilities + 25 transitions + 5x3x80 means + 5x3x80 diagonal covariances + 5x3 mixture weights) = 511,005. This is not a neural trainable-parameter count.",
        "param_count_source": "training_conventional/m08_hmm_gmm/runs/run_paper_20260530/checkpoints/best.pkl arrays; report.md:19 records 209 templates",
        "training_os": "Linux-6.6.114.1-microsoft-standard-WSL2-x86_64-with-glibc2.35",
        "training_gpu": "NVIDIA GeForce RTX 4060 Laptop GPU",
        "training_vram_gb": None,
        "hardware_label": "WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata",
        "provenance_source": "training_meta.environment in test_paper.json/meta.json",
        "best_artifact": "training_conventional/m08_hmm_gmm/runs/run_paper_20260530/checkpoints/best.pkl",
        "best_artifact_type": "pickle_hmm_gmm",
    },
    "m09-dnn-hmm": {
        "run_dir": "training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634",
        "training_time_hhmmss": "03:12:11",
        "training_eval_time_hhmmss": "00:00:00",
        "training_time_source": "training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/report.md:16-17",
        "n_params": 1_448_336,
        "param_count_note": "DNN acoustic model parameters.",
        "param_count_source": "training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/report.md:18",
        "training_os": "Linux-6.6.114.1-microsoft-standard-WSL2-x86_64-with-glibc2.35",
        "training_gpu": "NVIDIA GeForce RTX 4060 Laptop GPU",
        "training_vram_gb": None,
        "hardware_label": "WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata",
        "provenance_source": "training_meta.environment in test_paper.json/meta.json",
        "best_artifact": "training_conventional/m09_dnn_hmm/runs/run_paper_20260530_133634/checkpoints/best.pkl",
        "best_artifact_type": "pickle_dnn_hmm",
    },
    "m10-gmm-hmm-dnn": {
        "run_dir": "training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736",
        "training_time_hhmmss": "06:29:10",
        "training_eval_time_hhmmss": "00:54:04",
        "training_time_source": "training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/report.md:16-17",
        "n_params": 1_448_336,
        "n_templates": 209,
        "param_count_note": "Stage-3 DNN parameters; Stage-1 trained 209 GMM-HMM templates.",
        "param_count_source": "training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/report.md:18-19",
        "training_os": "Linux-6.6.114.1-microsoft-standard-WSL2-x86_64-with-glibc2.35",
        "training_gpu": "NVIDIA GeForce RTX 4060 Laptop GPU",
        "training_vram_gb": None,
        "hardware_label": "WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata",
        "provenance_source": "training_meta.environment in test_paper.json/meta.json",
        "best_artifact": "training_conventional/m10_gmm_hmm_dnn/runs/run_paper_20260531_071736/checkpoints/best.pkl",
        "best_artifact_type": "pickle_gmm_hmm_dnn",
    },
    "m11-vanilla-transformer": {
        "run_dir": "training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328",
        "training_time_hhmmss": "02:38:53",
        "training_eval_time_hhmmss": None,
        "training_time_source": "training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328/Log_Run.txt:676",
        "n_params": 4_212_688,
        "param_count_note": "Total model parameters from torchinfo/log summary.",
        "param_count_source": "training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328/Log_Run.txt:59",
        "training_os": "not recorded in source training log",
        "training_gpu": "CUDA device used; exact GPU model not recorded in source training log",
        "training_vram_gb": None,
        "hardware_label": "Training log records `Using device: cuda`; exact training OS/GPU model not recorded. Full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU.",
        "provenance_source": "Log_Run.txt:10 plus test_results/test_paper.json test_environment",
        "best_artifact": "training_conventional/m11_vanilla_transformer/runs/run_full_20260529_042328/checkpoints/best.pth",
        "best_artifact_type": "pytorch_state_dict",
    },
    "m12-vit-modified-ID": {
        "run_dir": "training_conventional/m12_vit_modified/runs/run_full_20260528_223323",
        "training_time_hhmmss": "03:44:58",
        "training_eval_time_hhmmss": None,
        "training_time_source": "training_conventional/m12_vit_modified/runs/run_full_20260528_223323/Log_Run.txt:698",
        "n_params": 4_353_248,
        "param_count_note": "Total model parameters from torchinfo/log summary.",
        "param_count_source": "training_conventional/m12_vit_modified/runs/run_full_20260528_223323/Log_Run.txt:58",
        "training_os": "not recorded in source training log",
        "training_gpu": "CUDA device used; exact GPU model not recorded in source training log",
        "training_vram_gb": None,
        "hardware_label": "Training log records `Using device: cuda`; exact training OS/GPU model not recorded. Full-test evaluation metadata records WSL2 Linux + RTX 4060 Laptop GPU.",
        "provenance_source": "Log_Run.txt:10 plus test_results/test_paper.json test_environment",
        "best_artifact": "training_conventional/m12_vit_modified/runs/run_full_20260528_223323/checkpoints/best.pth",
        "best_artifact_type": "pytorch_state_dict",
    },
    "m13-wav2letter": {
        "run_dir": "training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637",
        "training_time_hhmmss": "04:10:23",
        "training_eval_time_hhmmss": None,
        "training_time_source": "training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/report.md:17",
        "n_params": 24_840_900,
        "param_count_note": "Total CNN-CTC model parameters.",
        "param_count_source": "training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/report.md:13",
        "training_os": "Linux-6.6.114.1-microsoft-standard-WSL2-x86_64-with-glibc2.35",
        "training_gpu": "NVIDIA GeForce RTX 4060 Laptop GPU",
        "training_vram_gb": None,
        "hardware_label": "WSL2 Linux, NVIDIA GeForce RTX 4060 Laptop GPU; VRAM not recorded in run metadata",
        "provenance_source": "training_meta.environment in test_paper.json/meta.json",
        "best_artifact": "training_conventional/m13_wav2letter_cnn/runs/run_paper_20260531_230637/checkpoints/best.pt",
        "best_artifact_type": "pytorch_checkpoint",
    },
    "m07-bilstm-ctc": {
        "run_dir": "training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux",
        "training_time_hhmmss": "07:06:23",
        "training_eval_time_hhmmss": None,
        "training_time_source": "training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/report.md:17",
        "n_params": 32_825_659,
        "param_count_note": "Total Bi-LSTM CTC model parameters.",
        "param_count_source": "training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/report.md:14",
        "training_os": "Linux-6.17.0-35-generic-x86_64-with-glibc2.39",
        "training_gpu": "NVIDIA GeForce RTX 4060 Laptop GPU",
        "training_vram_gb": 8,
        "hardware_label": "Local Linux laptop, NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM",
        "provenance_source": "report.md + meta.json/training_meta.environment; VRAM label supplied by project run notes/user provenance",
        "best_artifact": "training/m07_bilstm_ctc/runs/run_paper_20260602_133815_linux/checkpoints/best.pt",
        "best_artifact_type": "pytorch_checkpoint",
    },
    "m06-conformer-ctc": {
        "run_dir": "training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux",
        "training_time_hhmmss": "06:31:49",
        "training_eval_time_hhmmss": None,
        "training_time_source": "training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/report.md:17",
        "n_params": 11_048_219,
        "param_count_note": "Total Conformer-CTC model parameters.",
        "param_count_source": "training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/report.md:14",
        "training_os": "Linux-6.17.0-35-generic-x86_64-with-glibc2.39",
        "training_gpu": "NVIDIA GeForce RTX 4060 Laptop GPU",
        "training_vram_gb": 8,
        "hardware_label": "Local Linux laptop, NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM",
        "provenance_source": "report.md + meta.json/training_meta.environment; VRAM label supplied by project run notes/user provenance",
        "best_artifact": "training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/checkpoints/best.pt",
        "best_artifact_type": "pytorch_checkpoint",
        "checkpoint_override": "training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/checkpoints/best.pt",
        "predictions_csv_override": "training/m06_conformer_ctc/runs/run_paper_20260601_213050_linux/test_results/predictions.csv",
    },
    "m02b-whisper-small-ft": {
        "run_dir": "training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact",
        "training_time_hhmmss": "04:48:29",
        "training_eval_time_hhmmss": None,
        "training_time_source": "training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/report.md:24",
        "n_params": 241_734_912,
        "param_count_note": "Total fine-tuned Whisper-small model parameters from run report. The original Whisper paper lists small as approximately 244M parameters; this run reports the exact HF model count used here.",
        "param_count_source": "training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/report.md:20",
        "training_os": "Linux-6.6.122+-x86_64-with-glibc2.35",
        "training_gpu": "NVIDIA A100-SXM4-40GB",
        "training_vram_gb": 40,
        "hardware_label": "Google Colab Linux, NVIDIA A100-SXM4-40GB GPU",
        "provenance_source": "report.md + meta.json/training_meta.environment + Colab audit report",
        "best_artifact": "training/m02b_whisper_small_ft/runs/run_paper_20260604_005100_colab_a100_paper_exact/best_model",
        "best_artifact_type": "huggingface_transformers_directory",
    },
}


def _path_exists(path_str: Optional[str]) -> bool:
    if not path_str:
        return False
    p = Path(path_str)
    if not p.is_absolute():
        p = PROJECT / p
    return p.exists()


def enrich_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Add evidence-backed fields to a benchmark/test result dict in place."""
    model_id = result.get("model_id")
    evidence = MODEL_EVIDENCE.get(model_id)
    if not evidence:
        return result

    train_sec = hhmmss_to_seconds(evidence.get("training_time_hhmmss"))
    train_eval_sec = hhmmss_to_seconds(evidence.get("training_eval_time_hhmmss"))
    infer_sec = result.get("wall_time_sec")
    try:
        infer_hours = float(infer_sec) / 3600 if infer_sec is not None else None
    except (TypeError, ValueError):
        infer_hours = None

    result["run_dir"] = evidence.get("run_dir")
    result["training_time_sec"] = train_sec
    result["training_time_hhmmss"] = evidence.get("training_time_hhmmss")
    result["training_time_hours"] = round(train_sec / 3600, 6) if train_sec is not None else None
    result["training_eval_time_sec"] = train_eval_sec
    result["training_eval_time_hhmmss"] = evidence.get("training_eval_time_hhmmss")
    result["training_time_source"] = evidence.get("training_time_source")
    result["inference_time_sec"] = infer_sec
    result["inference_time_hhmmss"] = seconds_to_hhmmss(infer_sec)
    result["inference_time_hours"] = round(infer_hours, 6) if infer_hours is not None else None
    result["inference_time_source"] = result.get("test_json") or "test_paper.json:wall_time_sec"

    result["n_params"] = evidence.get("n_params")
    result["params_millions"] = round(evidence["n_params"] / 1_000_000, 6) if evidence.get("n_params") is not None else None
    result["n_templates"] = evidence.get("n_templates")
    result["param_count_note"] = evidence.get("param_count_note")
    result["param_count_source"] = evidence.get("param_count_source")

    train_env = {
        "os": evidence.get("training_os"),
        "gpu": evidence.get("training_gpu"),
        "vram_gb": evidence.get("training_vram_gb"),
        "hardware_label": evidence.get("hardware_label"),
        "source": evidence.get("provenance_source"),
    }
    test_env_raw = result.get("test_environment") or {}
    result["os_gpu_provenance"] = {
        "training": train_env,
        "test": {
            "platform": test_env_raw.get("platform"),
            "cuda_device": test_env_raw.get("cuda_device"),
            "cuda_version": test_env_raw.get("cuda_version"),
            "torch_version": test_env_raw.get("torch_version"),
            "timestamp": test_env_raw.get("timestamp"),
            "source": result.get("test_json") or "test_paper.json:test_environment",
        },
    }

    result["best_artifact"] = evidence.get("best_artifact")
    result["best_artifact_type"] = evidence.get("best_artifact_type")
    result["best_artifact_exists"] = _path_exists(evidence.get("best_artifact"))
    if evidence.get("checkpoint_override"):
        result["checkpoint"] = evidence["checkpoint_override"]
        result["checkpoint_note"] = "Corrected to canonical selected run; older test JSON had a stale sibling-run path."
    elif result.get("checkpoint") and not _path_exists(result.get("checkpoint")) and evidence.get("best_artifact"):
        result["checkpoint"] = evidence["best_artifact"]
        result["checkpoint_note"] = "Corrected to existing evidence-backed best artifact path."
    if evidence.get("predictions_csv_override"):
        result["predictions_csv"] = evidence["predictions_csv_override"]
        result["predictions_csv_note"] = "Corrected to canonical selected run; older test JSON had a stale sibling-run path."

    return result


def enrich_benchmark(benchmark: Dict[str, Any]) -> Dict[str, Any]:
    for key in ("paper_models", "secondary_models"):
        for item in benchmark.get(key, []) or []:
            if isinstance(item, dict):
                enrich_result(item)

    # Ranked records need only compact fields.
    ranked = []
    valid = [r for r in benchmark.get("paper_models", []) if r.get("status") == "OK" and r.get("metrics")]
    for i, r in enumerate(sorted(valid, key=lambda x: x["metrics"]["wer"]), 1):
        ranked.append({
            "rank": i,
            "model_id": r["model_id"],
            "family": r.get("family"),
            "wer": r["metrics"].get("wer"),
            "cer": r["metrics"].get("cer"),
            "is_user_novel": r.get("is_user_novel", False),
            "training_time_hhmmss": r.get("training_time_hhmmss"),
            "training_time_hours": r.get("training_time_hours"),
            "inference_time_sec": r.get("inference_time_sec"),
            "n_params": r.get("n_params"),
            "params_millions": r.get("params_millions"),
            "hardware_label": (r.get("os_gpu_provenance") or {}).get("training", {}).get("hardware_label"),
        })
    if ranked:
        benchmark["paper_models_ranked_by_wer"] = ranked
        top = valid[0] if len(valid) == 1 else sorted(valid, key=lambda x: x["metrics"]["wer"])[0]
        benchmark["best_paper_model"] = {
            "model_id": top["model_id"],
            "family": top.get("family"),
            "wer": top["metrics"].get("wer"),
            "cer": top["metrics"].get("cer"),
            "is_user_novel": top.get("is_user_novel", False),
            "test_json": top.get("test_json"),
            "training_time_hhmmss": top.get("training_time_hhmmss"),
            "inference_time_sec": top.get("inference_time_sec"),
            "n_params": top.get("n_params"),
            "hardware_label": (top.get("os_gpu_provenance") or {}).get("training", {}).get("hardware_label"),
        }
    return benchmark


def evidence_table_rows(records: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    """Return compact rows for report tables."""
    rows = []
    for r in records:
        rows.append({
            "model_id": r.get("model_id"),
            "training_time_hhmmss": r.get("training_time_hhmmss"),
            "training_time_hours": r.get("training_time_hours"),
            "inference_time_sec": r.get("inference_time_sec"),
            "inference_time_hhmmss": r.get("inference_time_hhmmss"),
            "n_params": r.get("n_params"),
            "params_millions": r.get("params_millions"),
            "n_templates": r.get("n_templates"),
            "hardware_label": (r.get("os_gpu_provenance") or {}).get("training", {}).get("hardware_label"),
            "training_time_source": r.get("training_time_source"),
            "param_count_source": r.get("param_count_source"),
            "provenance_source": (r.get("os_gpu_provenance") or {}).get("training", {}).get("source"),
            "best_artifact": r.get("best_artifact"),
            "best_artifact_exists": r.get("best_artifact_exists"),
        })
    return rows
