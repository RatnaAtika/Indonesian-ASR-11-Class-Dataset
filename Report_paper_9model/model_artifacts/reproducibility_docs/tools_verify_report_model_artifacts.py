from __future__ import annotations

import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
OUT = PROJECT / "Report_paper_9model"
ART_ROOT = OUT / "model_artifacts"

REQUIRED_GLOBAL_DOCS = [
    "RUN_GUIDE.md",
    "benchmark.json",
    "paper_9model_results_normalized.json",
    "paper_9model_evidence_table.md",
    "paper_9model_evidence_summary.md",
    "paper_table_9model.md",
    "model_pseudocode_appendix.md",
    "candidate_references.md",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    index_path = ART_ROOT / "artifact_index.json"
    require(index_path.exists(), f"missing {index_path}", errors)
    if errors:
        print("FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    index = load_json(index_path)
    require(index.get("path_base") == "Report_paper_9model", "artifact_index path_base must be Report_paper_9model", errors)
    require(len(index.get("models", [])) == 9, "artifact_index must contain 9 models", errors)

    docs_dir = ART_ROOT / "reproducibility_docs"
    require(docs_dir.is_dir(), "missing reproducibility_docs directory", errors)
    for name in REQUIRED_GLOBAL_DOCS:
        require((docs_dir / name).is_file(), f"missing reproducibility doc {name}", errors)

    for entry in index.get("models", []):
        model_id = entry.get("model_id")
        model_dir = OUT / entry.get("artifact_dir", "")
        require(model_dir.is_dir(), f"{model_id}: missing artifact_dir {model_dir}", errors)
        require((model_dir / "metadata.json").is_file(), f"{model_id}: missing metadata.json", errors)
        require((model_dir / "README.md").is_file(), f"{model_id}: missing README.md", errors)

        source_dir = model_dir / "source_code"
        require(source_dir.is_dir(), f"{model_id}: missing source_code/", errors)
        require((source_dir / "train.py").is_file(), f"{model_id}: missing source_code/train.py", errors)
        require((source_dir / "test.py").is_file(), f"{model_id}: missing source_code/test.py", errors)
        source_manifest = source_dir / "source_manifest.json"
        require(source_manifest.is_file(), f"{model_id}: missing source_manifest.json", errors)
        if source_manifest.is_file():
            sm = load_json(source_manifest)
            copied = sm.get("files", [])
            require(len(copied) >= 4, f"{model_id}: expected >=4 source files, got {len(copied)}", errors)

        pseudo = model_dir / "pseudocode.md"
        require(pseudo.is_file(), f"{model_id}: missing pseudocode.md", errors)
        if pseudo.is_file():
            text = pseudo.read_text(encoding="utf-8")
            require("Algorithm" in text and model_id.split("-")[0] in text, f"{model_id}: pseudocode.md lacks algorithm/model marker", errors)

        arch_dir = model_dir / "architecture"
        require(arch_dir.is_dir(), f"{model_id}: missing architecture/", errors)
        require((arch_dir / "architecture_summary.md").is_file(), f"{model_id}: missing architecture_summary.md", errors)
        require((arch_dir / "architecture_manifest.json").is_file(), f"{model_id}: missing architecture_manifest.json", errors)

    if errors:
        print("FAIL")
        for err in errors:
            print(f"- {err}")
        return 1
    print("OK: model_artifacts includes docs, source code, pseudocode, and architecture summaries for 9 models")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
