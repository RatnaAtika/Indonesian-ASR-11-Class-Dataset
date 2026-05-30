# Agent Instructions

This project is stored on `/mnt/c` and contains very large audio datasets. Do not run unrestricted recursive scans over the full tree.

## Required scan rules

- Use `rg --files` / `rg` so `.ignore` is respected.
- Do not traverse these paths unless the user explicitly asks for dataset-level work:
  - `Dataset_Ori/`
  - `Processed_Balanced19/`
  - `Processed_Balanced19_v2/`
  - `Processed_Balanced19_v3/Dataset_Balanced19/`
  - `Whisper_Verification/run_*/`
- Prefer targeted commands such as:
  - `find . -maxdepth 3 ...`
  - `rg --files -g '*.py' -g '*.md'`
  - script filters like `--max-files`, `--category`, `--respondent`, and `--take`.

## Whisper verification safety

`verify_paper_dataset_sota_whisper.py` now defaults to a safe `--max-files 20`. For agent debugging, prefer `--list-only`, `--max-files 1`, or `--max-files 5`. Use `--full-run` only for planned full-dataset verification.

## Reason for these rules

The raw/processed audio directories contain large WAV collections on the Windows mount. Full-tree indexing or full Whisper runs can appear stuck even when the machine is only busy scanning/processing very large data.
