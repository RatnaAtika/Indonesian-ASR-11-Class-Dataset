---
name: notebook-authoring
description: Author, run, review, and ship Jupyter notebooks for analysis, ML demos, reports, and reproducible research. Picks the right kernel, manages dependencies, runs notebooks headlessly in CI, exports to HTML/PDF, and avoids notebook-rot anti-patterns. Wraps the upstream `jupyter-notebook` skill.
provides: notebook-authoring
version: 1.0.0
---

# Notebook Authoring

Notebooks are great for exploration and bad for production. Make them
explorable, reproducible, and shippable.

## When to use

- Quick data analysis or one-off model evaluation.
- Reproducible research artifact.
- Customer-facing demo of an API or model.
- Internal report with charts.

When NOT to use:

- Long-lived production logic (extract into a module + tests).
- Anything with secrets in the cells.

## Picks

- **Kernel manager**: `uv` (fast) or `poetry`. Pin Python with `.python-version`.
- **Notebook runner**: classic Jupyter, JupyterLab, VS Code, Colab,
  Databricks. All read the same `.ipynb`.
- **Headless run + diff**: `papermill` + `nbdime`.
- **Linting**: `nbqa ruff`, `nbqa mypy`.
- **Output stripping**: `nbstripout` pre-commit hook.
- **Reactive notebooks** (alt): `marimo`, `Quarto`.

## Workflow

1. **Scaffold**

   ```bash
   uv init notebook-project && cd notebook-project
   uv add jupyter pandas matplotlib seaborn pyarrow
   uv run jupyter lab
   ```

2. **Reproducibility**
   - One env per project (lockfile committed).
   - Random seeds set at the top.
   - Inputs immutable (Parquet snapshots, not "latest" CSVs).
   - First cell prints versions: `python`, `pandas`, `numpy`, `torch`,
     etc.

3. **Layout convention**
   - Cell 1: title + summary.
   - Cell 2: imports.
   - Cell 3: parameters (papermill-friendly: tagged `parameters`).
   - Cells 4+: load → transform → analyze → visualize → conclude.
   - Last cell: TL;DR for non-technical readers.

4. **Headless run in CI**

   ```bash
   papermill notebook.ipynb out.ipynb -p input_path data/2026q2.parquet
   jupyter nbconvert --to html out.ipynb --output report.html
   ```

5. **Pre-commit**
   - `nbstripout` (strips outputs)
   - `nbqa ruff` (lint code in cells)
   - `nbqa mypy` (typecheck code in cells)

6. **Diffs / review**
   - `nbdime` for human-readable diffs in PRs.
   - GitHub renders notebooks; review the rendered output.

7. **Productionize**
   - When the notebook stops being throwaway, extract:
     - functions to `src/<module>.py` with tests
     - the notebook itself becomes a thin "demo" of the module
   - Tag the notebook with a commit SHA + dataset version.

## Hard rules

- Never commit a notebook with outputs containing secrets, PII, or
  customer data.
- Never run a notebook against production data without a read-only
  credential and `database-safety-guardrail` in the loop.
- Always pin dependencies; "latest" today is breaking change tomorrow.
- Always rerun the entire notebook top-to-bottom before committing
  (kernel restart + run all). Hidden state kills reproducibility.

## Adaptation rules

- For ML demos shown to customers, use Colab or Jupyter on a sandboxed VM
  — not the analyst's laptop.
- For research with public datasets, use Quarto or marimo and publish a
  static HTML.
- For internal reports, run headlessly via papermill nightly and post the
  HTML to the team's docs site.
- For Databricks / Snowflake notebooks, follow the platform's native
  conventions; export `.ipynb` for archival.

## Cross-skill integration

- `media-pipeline` runs notebook-driven training/eval cells.
- `paper-writing` / `research-paper-writing` consume notebook outputs.
- `observability-stack` ingests notebook-emitted metrics for ML monitoring.

## Verification before sign-off

- [ ] Top-to-bottom run is clean
- [ ] Outputs in committed file are stripped (or HTML export only)
- [ ] Dependencies pinned
- [ ] No secrets in cells
- [ ] CI runs the notebook headlessly on every PR touching it
