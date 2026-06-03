#!/usr/bin/env python3
"""Write paper-ready Colab result summary to Google Drive Results.

Scans Results/m02b_whisper_* run directories, extracts total training time from
log/report, WER/CER from test_paper.json, and verifies required artifacts.
Always exits 0 so it can be used as a best-effort finalization step.
"""
from __future__ import annotations
import argparse, datetime, json, re
from pathlib import Path

REQUIRED = [
    "config.json", "meta.json", "history.json", "log.txt", "report.md",
    "model_summary.png", "model_summary.pdf", "best_model", "checkpoints",
    "test_results/test_paper.json", "test_results/predictions.csv",
    "test_results/test_summary.md",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def extract_total_time(run: Path) -> tuple[str, str]:
    log = read_text(run / "log.txt")
    report = read_text(run / "report.md")
    total_id = "MISSING"
    report_time = ""
    m = re.findall(r"Total waktu training:\s*(.+)", log)
    if m:
        total_id = m[-1].strip()
    m = re.findall(r"Total training time:\s*([^\n]+)", report)
    if m:
        report_time = m[-1].strip()
    return total_id, report_time


def load_metrics(run: Path) -> tuple[str, dict, str]:
    p = run / "test_results" / "test_paper.json"
    if not p.exists():
        return run.parent.name, {}, "MISSING"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data.get("model_id", run.parent.name), data.get("metrics", {}), str(p)
    except Exception as e:
        return run.parent.name, {"error": str(e)}, str(p)


def summarize_run(run: Path) -> dict:
    total_id, report_time = extract_total_time(run)
    model_id, metrics, test_json = load_metrics(run)
    artifact_status = {}
    for rel in REQUIRED:
        p = run / rel
        artifact_status[rel] = p.exists()
    missing = [k for k, ok in artifact_status.items() if not ok]
    return {
        "model_id": model_id,
        "run": run.name,
        "run_dir": str(run),
        "total_waktu_training": total_id,
        "total_training_time_report": report_time,
        "wer": metrics.get("wer", "MISSING"),
        "cer": metrics.get("cer", "MISSING"),
        "mer": metrics.get("mer", "MISSING"),
        "wil": metrics.get("wil", "MISSING"),
        "ser": metrics.get("ser", "MISSING"),
        "test_json": test_json,
        "artifact_status": artifact_status,
        "missing_artifacts": missing,
        "complete_for_paper": not missing and total_id != "MISSING" and test_json != "MISSING",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-root", type=Path, required=True)
    args = ap.parse_args()
    root = args.results_root
    root.mkdir(parents=True, exist_ok=True)

    runs: list[Path] = []
    for family in ["m02b_whisper_small_ft", "m02b_whisper_medium_ft"]:
        base = root / family
        if base.exists():
            runs.extend([p for p in base.glob("run_paper_*") if p.is_dir()])
    runs = sorted(runs, key=lambda p: p.stat().st_mtime, reverse=True)
    rows = [summarize_run(r) for r in runs]

    out_json = root / "paper_training_time_summary.json"
    out_md = root / "paper_training_time_summary.md"
    payload = {
        "generated": datetime.datetime.now().isoformat(),
        "results_root": str(root),
        "n_runs": len(rows),
        "runs": rows,
    }
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# Paper Training Time Summary - Colab Whisper\n\n")
    lines.append(f"Generated: {payload['generated']}\n\n")
    lines.append(f"Results root: `{root}`\n\n")
    lines.append("| complete | model_id | run | total_waktu_training | report_time | WER | CER | missing_artifacts |\n")
    lines.append("|---:|---|---|---:|---:|---:|---:|---|\n")
    for r in rows:
        miss = ", ".join(r["missing_artifacts"]) if r["missing_artifacts"] else "-"
        lines.append(
            f"| {r['complete_for_paper']} | {r['model_id']} | {r['run']} | "
            f"{r['total_waktu_training']} | {r['total_training_time_report']} | "
            f"{r['wer']} | {r['cer']} | {miss} |\n"
        )
    if not rows:
        lines.append("\nNo Colab Whisper result runs found yet.\n")
    lines.append("\nRequired artifacts checked:\n\n")
    for rel in REQUIRED:
        lines.append(f"- `{rel}`\n")
    out_md.write_text("".join(lines), encoding="utf-8")

    print(f"[colab-summary] wrote {out_md}")
    print(f"[colab-summary] wrote {out_json}")
    if rows:
        latest = rows[0]
        print(
            f"[colab-summary] latest: {latest['model_id']} {latest['run']} "
            f"complete={latest['complete_for_paper']} total={latest['total_waktu_training']} "
            f"WER={latest['wer']} CER={latest['cer']}"
        )
        if latest["missing_artifacts"]:
            print(f"[colab-summary] WARNING missing: {latest['missing_artifacts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
