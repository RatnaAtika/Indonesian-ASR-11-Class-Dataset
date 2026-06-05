from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from report_paper_9model_metadata import PROJECT, enrich_benchmark

OUT = PROJECT / "Report_paper_9model"
BENCH = OUT / "benchmark" / "benchmark.json"
ART_ROOT = OUT / "model_artifacts"

GLOBAL_DOC_SOURCES = [
    ("RUN_GUIDE.md", PROJECT / "RUN_GUIDE.md"),
    ("benchmark.json", OUT / "benchmark" / "benchmark.json"),
    ("paper_9model_results_normalized.json", OUT / "data" / "paper_9model_results_normalized.json"),
    ("paper_9model_evidence_table.md", OUT / "tables" / "paper_9model_evidence_table.md"),
    ("paper_table_9model.md", OUT / "tables" / "paper_table_9model.md"),
    ("model_pseudocode_appendix.md", OUT / "appendices" / "model_pseudocode_appendix.md"),
    ("candidate_references.md", OUT / "appendices" / "candidate_references.md"),
    ("aggregate_paper_test_results.py", PROJECT / "aggregate_paper_test_results.py"),
    ("tools_generate_report_paper_9model.py", PROJECT / "tools_generate_report_paper_9model.py"),
    ("tools_package_report_model_artifacts.py", PROJECT / "tools_package_report_model_artifacts.py"),
    ("report_paper_9model_metadata.py", PROJECT / "report_paper_9model_metadata.py"),
    ("tools_verify_report_model_artifacts.py", PROJECT / "tools_verify_report_model_artifacts.py"),
]

DEEP_COMMON = [
    PROJECT / "training" / "common" / "utils.py",
    PROJECT / "training" / "common" / "test_helper.py",
    PROJECT / "training" / "common" / "from_scratch_trainer.py",
    PROJECT / "training" / "common" / "from_scratch_test.py",
]
WHISPER_COMMON = [
    PROJECT / "training" / "common" / "utils.py",
    PROJECT / "training" / "common" / "test_helper.py",
    PROJECT / "training" / "common" / "whisper_trainer.py",
    PROJECT / "Colab_ASR_A100_Training" / "requirements_colab_a100.txt",
    PROJECT / "Colab_ASR_A100_Training" / "scripts" / "colab_bootstrap_a100.sh",
    PROJECT / "Colab_ASR_A100_Training" / "scripts" / "colab_train_m02b_whisper_small_paper_exact.sh",
]
CONVENTIONAL_COMMON = [
    PROJECT / "training_conventional" / "common" / "utils.py",
    PROJECT / "training_conventional" / "common" / "test_helper.py",
    PROJECT / "training_conventional" / "common" / "pkl_hmm_trainer.py",
    PROJECT / "training_conventional" / "common" / "pkl_hmm_test.py",
    PROJECT / "training_conventional" / "common" / "pkl_cnn_ctc_trainer.py",
    PROJECT / "training_conventional" / "common" / "pkl_cnn_ctc_test.py",
]

MODEL_SOURCE_EXTRAS = {
    "m02b-whisper-small-ft": WHISPER_COMMON,
    "m06-conformer-ctc": DEEP_COMMON,
    "m07-bilstm-ctc": DEEP_COMMON,
    "m08-hmm-gmm": CONVENTIONAL_COMMON,
    "m09-dnn-hmm": CONVENTIONAL_COMMON,
    "m10-gmm-hmm-dnn": CONVENTIONAL_COMMON,
    "m11-vanilla-transformer": CONVENTIONAL_COMMON + [PROJECT.parent / "train_model_vanilla.py"],
    "m12-vit-modified-ID": CONVENTIONAL_COMMON + [PROJECT.parent / "train_model_vit.py"],
    "m13-wav2letter": CONVENTIONAL_COMMON,
}



def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_info(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "relative_path": str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def copy_or_hardlink_file(src: Path, dst: Path) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    try:
        os.link(src, dst)
        return "hardlink"
    except OSError:
        shutil.copy2(src, dst)
        return "copy"


TEXT_COPY_SUFFIXES = {".py", ".sh", ".md", ".txt", ".json", ".csv", ".tex"}


def copy_file(src: Path, dst: Path) -> dict[str, Any] | None:
    """Copy a small reproducibility file and return manifest info.

    Text snapshots are normalized to LF and have trailing whitespace stripped so
    Git diff checks stay clean; binary/local run artifacts are handled by
    materialize()/maybe_copy() without normalization.
    """
    if not src.exists() or not src.is_file():
        return None
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() in TEXT_COPY_SUFFIXES:
        text = src.read_text(encoding="utf-8", errors="replace")
        normalized = "\n".join(line.rstrip() for line in text.splitlines()).rstrip() + "\n"
        dst.write_text(normalized, encoding="utf-8")
    else:
        shutil.copy2(src, dst)
    info = file_info(dst, OUT)
    info["source"] = str(src)
    info["operation"] = "copy"
    return info


def safe_rel_source_path(src: Path) -> Path:
    """Preserve useful source layout without escaping destination dirs."""
    try:
        return src.resolve().relative_to(PROJECT.resolve())
    except ValueError:
        return Path("external") / src.name


def write_json(path: Path, data: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def materialize(src: Path, dst: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Hardlink/copy a file or directory and return file manifest."""
    ops = {"hardlink": 0, "copy": 0}
    manifest: list[dict[str, Any]] = []
    if src.is_dir():
        for f in sorted(src.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(src)
            op = copy_or_hardlink_file(f, dst / rel)
            ops[op] += 1
            info = file_info(dst / rel, OUT)
            info["source"] = str(f)
            info["operation"] = op
            manifest.append(info)
    elif src.is_file():
        op = copy_or_hardlink_file(src, dst / src.name)
        ops[op] += 1
        info = file_info(dst / src.name, OUT)
        info["source"] = str(src)
        info["operation"] = op
        manifest.append(info)
    return manifest, ops


def maybe_copy(src: Path, dest_dir: Path, dest_name: str | None = None) -> dict[str, Any] | None:
    if not src.exists() or not src.is_file():
        return None
    dst = dest_dir / (dest_name or src.name)
    op = copy_or_hardlink_file(src, dst)
    info = file_info(dst, OUT)
    info["source"] = str(src)
    info["operation"] = op
    return info


def run_dir_for(model: dict[str, Any]) -> Path:
    if model.get("run_dir"):
        p = Path(model["run_dir"])
        return p if p.is_absolute() else PROJECT / p
    tj = Path(model.get("test_json", ""))
    if tj.exists():
        return tj.parent.parent
    return PROJECT


def source_files_for(model: dict[str, Any]) -> list[Path]:
    run_dir = run_dir_for(model)
    model_dir = run_dir.parent.parent if run_dir.name.startswith("run_") else run_dir.parent
    files = [model_dir / "train.py", model_dir / "test.py"]
    files.extend(MODEL_SOURCE_EXTRAS.get(model["model_id"], []))
    # Keep order stable while removing duplicates and missing files.
    seen: set[str] = set()
    out: list[Path] = []
    for f in files:
        key = str(f.resolve()) if f.exists() else str(f)
        if key in seen or not f.exists() or not f.is_file():
            continue
        seen.add(key)
        out.append(f)
    return out


def copy_source_code(model: dict[str, Any], model_dir: Path) -> list[dict[str, Any]]:
    source_dir = model_dir / "source_code"
    manifest: list[dict[str, Any]] = []
    for src in source_files_for(model):
        rel = safe_rel_source_path(src)
        # Keep train.py/test.py at top level for easy discovery, preserve the
        # original repo layout for shared helper modules.
        if src.name in {"train.py", "test.py"} and model["model_id"].replace("-", "_") not in str(rel):
            dst = source_dir / src.name
        elif src.name in {"train.py", "test.py"}:
            dst = source_dir / src.name
        else:
            dst = source_dir / rel
        info = copy_file(src, dst)
        if info:
            manifest.append(info)
    write_json(source_dir / "source_manifest.json", {
        "model_id": model["model_id"],
        "purpose": "Source code needed to reproduce this model's training and testing entry points.",
        "note": "Data files and model weights are intentionally excluded; see RUN_GUIDE.md and metadata.json for artifact locations.",
        "files": manifest,
    })
    return manifest


def extract_pseudocode(model: dict[str, Any]) -> str:
    appendix = OUT / "appendices" / "model_pseudocode_appendix.md"
    text = appendix.read_text(encoding="utf-8") if appendix.exists() else ""
    slot = model["model_id"].split("-")[0]
    pattern = re.compile(rf"(^## Algorithm .*?\({re.escape(slot)}(?:[,\)]).*?)(?=^## Algorithm |\Z)", re.S | re.M)
    match = pattern.search(text)
    if match:
        body = match.group(1).strip()
    else:
        body = f"## Pseudocode unavailable for {model['model_id']}\n\nSee model_pseudocode_appendix.md."
    return f"# Pseudocode — {model['model_id']}\n\n{body}\n"


def copy_architecture(model: dict[str, Any], model_dir: Path) -> list[dict[str, Any]]:
    arch_dir = model_dir / "architecture"
    arch_dir.mkdir(parents=True, exist_ok=True)
    run_dir = run_dir_for(model)
    image_sources = [
        run_dir / "model_summary.png",
        run_dir / "model_summary_vit.png",
    ]
    manifest: list[dict[str, Any]] = []
    for src in image_sources:
        if src.exists() and src.is_file():
            info = copy_file(src, arch_dir / "model_summary.png")
            if info:
                manifest.append(info)
            break

    summary = [
        f"# Architecture summary — {model['model_id']}",
        "",
        f"- Family: {model.get('family')}",
        f"- WER/CER: {model.get('metrics', {}).get('wer')} / {model.get('metrics', {}).get('cer')}",
        f"- Parameter count: {model.get('n_params') if model.get('n_params') is not None else 'n/a'}",
        f"- Template count: {model.get('n_templates') if model.get('n_templates') is not None else 'n/a'}",
        f"- Parameter note: {model.get('param_count_note') or 'n/a'}",
        f"- Decoding method: {model.get('decoding_method') or model.get('config', {}).get('decoding_method') or 'see test_paper.json'}",
        f"- Training hardware: {((model.get('os_gpu_provenance') or {}).get('training') or {}).get('hardware_label') or 'n/a'}",
        "",
        "## Reproducibility pointers",
        "",
        "- `../source_code/`: copied training/testing entry points and shared helper modules.",
        "- `../pseudocode.md`: algorithm-level pseudocode for this model.",
        "- `../metadata.json`: metrics, timing, parameter, hardware, checksum, and best-artifact provenance.",
        "- `model_summary.png`: architecture diagram/torchinfo image when available from the run.",
    ]
    (arch_dir / "architecture_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    write_json(arch_dir / "architecture_manifest.json", {
        "model_id": model["model_id"],
        "summary": str((arch_dir / "architecture_summary.md").relative_to(OUT)),
        "images": manifest,
        "image_note": "model_summary.png is included when the source run produced one; classical HMM/DNN-HMM runs may only have textual architecture summaries.",
    })
    return manifest


def copy_global_reproducibility_docs() -> list[dict[str, Any]]:
    docs_dir = ART_ROOT / "reproducibility_docs"
    manifest: list[dict[str, Any]] = []
    for name, src in GLOBAL_DOC_SOURCES:
        info = copy_file(src, docs_dir / name)
        if info:
            manifest.append(info)
    write_json(docs_dir / "reproducibility_docs_manifest.json", {
        "purpose": "Global docs/scripts needed to interpret and regenerate the nine-model benchmark package.",
        "files": manifest,
    })
    return manifest


def main() -> int:
    bench = json.loads(BENCH.read_text(encoding="utf-8"))
    enrich_benchmark(bench)
    paper = [m for m in bench.get("paper_models", []) if m.get("status") == "OK"]
    paper = sorted(paper, key=lambda m: m["metrics"]["wer"])

    if ART_ROOT.exists():
        shutil.rmtree(ART_ROOT)
    ART_ROOT.mkdir(parents=True, exist_ok=True)

    index: dict[str, Any] = {
        "generated": datetime.now().isoformat(),
        "purpose": "Per-model best-artifact package for the nine-model Data in Brief benchmark.",
        "path_base": "Report_paper_9model",
        "paths_are_relative_to": "Report_paper_9model",
        "note": "Large binary model files are materialized locally as hardlinks when possible, otherwise copies. Git ignores model weights by policy; source code, pseudocode, architecture summaries, and manifests are Git-trackable.",
        "reproducibility_docs": {},
        "models": [],
    }
    global_doc_files = copy_global_reproducibility_docs()
    index["reproducibility_docs"] = {
        "dir": "model_artifacts/reproducibility_docs",
        "manifest": "model_artifacts/reproducibility_docs/reproducibility_docs_manifest.json",
        "file_count": len(global_doc_files),
    }

    for rank, m in enumerate(paper, 1):
        model_dir = ART_ROOT / f"rank{rank:02d}_{m['model_id']}"
        copied = model_dir / "run_outputs"
        best_dir = model_dir / "best_artifact"
        copied.mkdir(parents=True, exist_ok=True)
        best_dir.mkdir(parents=True, exist_ok=True)
        run_dir = run_dir_for(m)

        copied_files: list[dict[str, Any]] = []
        # Human-readable training/test outputs.  Keep names stable even when source
        # scripts use Log_Run.txt vs log.txt.
        candidates = [
            (run_dir / "report.md", None),
            (run_dir / "Log_Run.txt", "training_log.txt"),
            (run_dir / "log.txt", "training_log.txt"),
            (run_dir / "history.json", None),
            (run_dir / "meta.json", None),
            (run_dir / "BEST_INFO.txt", None),
            (run_dir / "best_model" / "BEST_INFO.txt", "best_model_BEST_INFO.txt"),
            (run_dir / "model_summary.png", None),
            (run_dir / "model_summary.pdf", None),
            (run_dir / "model_summary_vit.png", "model_summary.png"),
            (run_dir / "model_summary_vit.pdf", "model_summary.pdf"),
            (run_dir / "test_results" / "test_paper.json", None),
            (run_dir / "test_results" / "test_summary.md", None),
            (run_dir / "test_results" / "predictions.csv", None),
        ]
        used_dests: set[str] = set()
        for src, dest_name in candidates:
            if not src.exists() or not src.is_file():
                continue
            dest_name = dest_name or src.name
            if dest_name in used_dests:
                # Prefer Log_Run.txt over log.txt only when both map to same name.
                continue
            used_dests.add(dest_name)
            info = maybe_copy(src, copied, dest_name)
            if info:
                copied_files.append(info)

        best_src_raw = m.get("best_artifact") or m.get("checkpoint")
        best_src = Path(best_src_raw) if best_src_raw else None
        if best_src and not best_src.is_absolute():
            best_src = PROJECT / best_src
        best_files: list[dict[str, Any]] = []
        best_ops = {"hardlink": 0, "copy": 0}
        best_exists = bool(best_src and best_src.exists())
        if best_src and best_src.exists():
            best_files, best_ops = materialize(best_src, best_dir)

        source_files = copy_source_code(m, model_dir)
        pseudocode_path = model_dir / "pseudocode.md"
        pseudocode_path.write_text(extract_pseudocode(m), encoding="utf-8")
        architecture_files = copy_architecture(m, model_dir)

        metadata = {
            "rank": rank,
            "model_id": m["model_id"],
            "family": m.get("family"),
            "wer": m["metrics"].get("wer"),
            "cer": m["metrics"].get("cer"),
            "run_dir": str(run_dir),
            "training_time_hhmmss": m.get("training_time_hhmmss"),
            "training_time_hours": m.get("training_time_hours"),
            "inference_time_sec": m.get("inference_time_sec"),
            "inference_time_hhmmss": m.get("inference_time_hhmmss"),
            "n_params": m.get("n_params"),
            "n_templates": m.get("n_templates"),
            "param_count_note": m.get("param_count_note"),
            "os_gpu_provenance": m.get("os_gpu_provenance"),
            "best_artifact_source": str(best_src) if best_src else None,
            "best_artifact_exists": best_exists,
            "best_artifact_type": m.get("best_artifact_type"),
            "best_artifact_files": best_files,
            "best_artifact_operations": best_ops,
            "copied_run_output_files": copied_files,
            "source_code_files": source_files,
            "pseudocode": str(pseudocode_path.relative_to(OUT)),
            "architecture_summary": str((model_dir / "architecture" / "architecture_summary.md").relative_to(OUT)),
            "architecture_files": architecture_files,
            "git_tracking_note": "Model weight extensions (*.pt, *.pth, *.pkl, *.safetensors, etc.) plus run_outputs/ and best_artifact/ are ignored by .gitignore and are local artifacts, not GitHub-tracked files. Source code, pseudocode, architecture summaries, and manifests are Git-trackable.",
        }
        (model_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
        readme = [
            f"# {m['model_id']} artifact package",
            "",
            f"- Rank: {rank}",
            f"- Family: {m.get('family')}",
            f"- WER/CER: {m['metrics'].get('wer')} / {m['metrics'].get('cer')}",
            f"- Training time: {m.get('training_time_hhmmss')} ({m.get('training_time_hours')} h)",
            f"- Full-test inference time: {m.get('inference_time_hhmmss')} ({m.get('inference_time_sec')} s)",
            f"- Params/templates: {m.get('n_params') if m.get('n_params') is not None else 'n/a'} / {m.get('n_templates') or 'n/a'}",
            f"- Training hardware: {((m.get('os_gpu_provenance') or {}).get('training') or {}).get('hardware_label')}",
            f"- Source run: `{run_dir}`",
            f"- Best artifact source: `{best_src}`",
            f"- Best artifact exists locally: {best_exists}",
            "",
            "## Contents",
            "",
            "- `metadata.json`: machine-readable evidence and checksums.",
            "- `source_code/`: copied training/testing entry points and shared helper code needed to reproduce this model.",
            "- `pseudocode.md`: algorithm-level pseudocode excerpt for this model.",
            "- `architecture/`: text architecture summary and `model_summary.png` when available.",
            "- `run_outputs/`: copied/hardlinked reports, logs, summaries, metrics, predictions, and model-summary images where available.",
            "- `best_artifact/`: local hardlink/copy of the selected best testing model artifact.",
            "",
            "Large binary weights are intentionally ignored by Git; keep this local package or upload it to Drive/Zenodo/OSF for submission reproducibility.",
        ]
        (model_dir / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
        index["models"].append({
            "rank": rank,
            "model_id": m["model_id"],
            "artifact_dir": str(model_dir.relative_to(OUT)),
            "metadata": str((model_dir / "metadata.json").relative_to(OUT)),
            "best_artifact_source": str(best_src) if best_src else None,
            "best_artifact_exists": best_exists,
            "best_artifact_file_count": len(best_files),
            "copied_run_output_file_count": len(copied_files),
            "source_code_file_count": len(source_files),
            "source_code_manifest": str((model_dir / "source_code" / "source_manifest.json").relative_to(OUT)),
            "pseudocode": str(pseudocode_path.relative_to(OUT)),
            "architecture_manifest": str((model_dir / "architecture" / "architecture_manifest.json").relative_to(OUT)),
            "architecture_file_count": len(architecture_files),
            "operations": best_ops,
        })

    (ART_ROOT / "artifact_index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    readme = [
        "# Nine-model best-artifact package",
        "",
        "This directory splits the selected best testing model artifacts and final run outputs per model.",
        "It also includes Git-trackable source code snapshots, pseudocode excerpts, architecture summaries, and global reproducibility documents.",
        "Binary model files are local hardlinks/copies and are not Git-tracked because the repository ignores model weights for GitHub safety.",
        "",
        "Use `artifact_index.json` first, then each `rankXX_<model>/metadata.json` for checksums and provenance.",
        "Paths in `artifact_index.json` are relative to `Report_paper_9model/`.",
        "Global reproduction docs are in `reproducibility_docs/`.",
    ]
    (ART_ROOT / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")

    print(ART_ROOT)
    print("models", len(index["models"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
