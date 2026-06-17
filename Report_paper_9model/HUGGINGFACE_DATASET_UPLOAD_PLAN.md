# Hugging Face Dataset Upload Plan

Purpose: prepare a **private-first Hugging Face dataset repository** for the Indonesian 11-class ASR dataset, final benchmark models, final benchmark outputs, and paper-supporting documents that are too large or unsuitable for GitHub. After the paper is accepted/published, the same HF dataset repo can be switched to public and cited in the paper/Data Availability statement.

Current date: 2026-06-17

## 1. Recommended HF target

Use a **Dataset** repo, not a Model repo, because the goal is to publish one reproducibility package containing audio data, metadata, trained models, predictions, and paper artifacts.

Suggested private repo ID:

```text
RatnaAtika/Indonesian-ASR-11-Class-Dataset
```

Alternative safer staging repo name before publication:

```text
RatnaAtika/indonesian-asr-11class-paper-private
```

Recommended visibility now: **private**. Change to public only after the paper is accepted/published and consent/licensing checks are final.

## 2. Upload scope summary

### Must upload for paper reproducibility

| Package | Local source | Approx. size / count | HF path | Reason |
|---|---:|---:|---|---|
| Final processed ASR dataset | `Processed_Balanced19_v3/Dataset_Balanced19/` | about 16 GB | `data/processed_balanced19_v3/` | Primary public dataset used for paper experiments |
| Final transcripts | `Processed_Balanced19_v3/Transkrip_ASR_Jurnal_Dataset/` | small | `data/transcripts/` | Text references for 11 sentence classes |
| Final metadata CSV/JSON | `metadata/dataset_metadata_clean.csv`, `metadata/dataset_metadata_summary.json`, `metadata/dataset_metadata.csv` | about 40 MB each CSV | `metadata/` | Required for sample-level provenance and reuse |
| Final split files | `splits/split_assignment.csv`, `splits/split_summary.json`, `splits/split_summary.md` | small | `splits/` | Required to reproduce train/dev/test protocol |
| Final benchmark report package | `Report_paper_9model/benchmark/`, `tables/`, `data/`, `manuscript/`, `appendices/` | moderate | `paper/Report_paper_9model/` | Paper evidence and final 9-model benchmark tables |
| Final model artifacts | `Report_paper_9model/model_artifacts/rank*/best_artifact/` | about 1.26 GB total | `models/final_9model_benchmark/rank*/best_artifact/` | Best checkpoints/model files not suitable for GitHub |
| Full run outputs, including skipped large predictions | final run `test_results/predictions.csv` plus existing `model_artifacts/rank*/run_outputs/` | about 23.4 MB for 9 predictions CSVs + small outputs | `models/final_9model_benchmark/rank*/run_outputs/` | Exact per-sample predictions used in benchmark |
| Training diagnostics | `Report_paper_9model/training_diagnostics/` | 120 files / about 4.3 MB | `models/final_9model_benchmark/training_diagnostics/` | Training plots/logs/reports cross-checked with final runs |
| Spectrogram/logat paper assets | `Report_paper_9model/spectrogram_logat/` | small/moderate | `paper/spectrogram_logat/` | Qualitative accent/regional illustration package |
| Reproducibility code snapshots | `Report_paper_9model/model_artifacts/rank*/source_code/`, `pseudocode.md`, `architecture/` | small | `models/final_9model_benchmark/rank*/` | Enables readers to understand model architecture and evaluation |

### Should upload if licensing/consent allows

| Package | Local source | Approx. size | HF path | Note |
|---|---:|---:|---|---|
| Raw/original audio | `Dataset_Ori/` | about 17 GB | `data/raw_original/` | Useful for transparency, but only publish if consent and privacy are confirmed |
| Dataset construction reports | `Processed_Balanced19_v3/reports/`, selected `Whisper_Verification_Sessions/session_20260521_132123_v7_natural_synth_metadata_splits/` files | small/moderate | `provenance/` | Evidence for filtering, balancing, and split construction |
| Dataset statistics reports | `reports/dataset_statistics_v7_paper9/` and related README | small | `paper/dataset_statistics/` | Supports Data in Brief statistics |
| GitHub-safe docs already committed | `README.md`, `README_RUN_WHISPER.md`, `RUN_GUIDE.md` | small | `docs/` | Useful entry points for users |

### Do not upload

- Incomplete/dev/smoke/interrupted training runs.
- Non-best checkpoints already deleted from local cleanup scope.
- Feature caches or temporary preprocessing caches.
- Local notebooks with private credentials or machine-specific paths unless scrubbed.
- `.git/`, `__pycache__/`, `.ipynb_checkpoints/`, logs containing credentials, or OS temp files.
- Duplicate Colab staging folders unless they contain unique final m02b artifacts not already included through `training/m02b...` symlink or `Report_paper_9model/model_artifacts/`.

## 3. Proposed HF repository layout

```text
README.md                              # HF dataset card, private now; publish-ready later
LICENSE                                # final license after consent/legal check
CITATION.cff                           # paper citation placeholder until DOI available
upload_manifest.json                   # generated file manifest with sha256, size, source
upload_manifest.csv

metadata/
  dataset_metadata.csv
  dataset_metadata_clean.csv
  dataset_metadata_summary.json
  dataset_card_supporting_stats.json

splits/
  split_assignment.csv
  split_summary.json
  split_summary.md

data/
  transcripts/
    Kalimat_*.txt
  processed_balanced19_v3/
    Dataset_Balanced19/...
  raw_original/                        # optional until consent confirmed
    Dataset_Ori/...

models/
  final_9model_benchmark/
    artifact_index.json
    run_outputs_upload_manifest.md
    rank01_m02b-whisper-small-ft/
      best_artifact/...
      run_outputs/predictions.csv
      source_code/...
      architecture/...
      pseudocode.md
    rank02_m06-conformer-ctc/...
    ...
    rank09_m09-dnn-hmm/...
    training_diagnostics/...

paper/
  Report_paper_9model/
    benchmark/...
    tables/...
    data/...
    appendices/...
    manuscript/...
  spectrogram_logat/...
  dataset_statistics/...

provenance/
  processed_balanced19_v3_reports/...
  v7_split_construction/...
```

## 4. Critical data consistency requirements

Use these as hard gates before upload:

1. `Report_paper_9model/benchmark/benchmark.json` remains the source of truth for the 9 final model run directories.
2. `Report_paper_9model/model_artifacts/artifact_index.json` and each `rank*/metadata.json` must match those 9 final runs.
3. `Report_paper_9model/training_diagnostics/training_diagnostics_crosscheck_report.md` currently shows cross-check passed:
   - 60 exact byte matches for overlapping run outputs
   - 10 expected skipped files
   - 0 mismatches
   - 0 warnings
4. Upload all 9 `predictions.csv` files that GitHub skipped because each exceeded 1 MB.
5. Upload best artifacts only, not intermediate checkpoints.
6. Preserve checksums for every uploaded file in `upload_manifest.json` and `upload_manifest.csv`.
7. Do not change split assignment: seed 42, train/dev/test speakers exactly as in `splits/split_summary.json`.

## 5. Known dataset facts for HF dataset card

From local metadata:

- Total files: 104,500
- Real files: 104,368
- Synthetic/repair files: 132 (0.1263%)
- Sentence categories/classes: 11
- Speakers/respondents: 20
- Files per category: 9,500
- Files per speaker: 5,225
- Split seed: 42
- Public human split speaker labels after anonymization:
  - train: Af, An, Ar, At, Be, El, Er, Fi, Ha, In, Mu, Na, Ri, Ul
  - dev: Ai, Fa, Pr
  - test: Ba, Jo, Ro
- Public synthetic repair labels append `-s` to the repaired human target label, e.g. `Ai-s` repairs target label `Ai`.
- Synthetic repair labels currently present: Af-s, Ai-s, An-s, Ar-s, At-s, Be-s, El-s, Er-s, Fa-s, Fi-s, Ha-s, In-s, Jo-s, Mu-s, Na-s, Pr-s, Ri-s, Ul-s.
- Files by split:
  - train: 73,150
  - dev: 15,675
  - test: 15,675
- Duration by split:
  - train: 94.9437 h
  - dev: 20.2969 h
  - test: 18.9357 h
- Primary processed package size: about 16 GB
- Raw/original package size: about 17 GB

## 6. Privacy, ethics, and license gates before public release

Before switching HF repo from private to public, confirm:

- Speaker consent covers public release of voice recordings.
- Respondent names must be replaced with short public speaker labels before HF publication. Human labels use deterministic two-character codes; gender remains in the label list CSV instead of being encoded directly in the ID.
- Synthetic repair audio must be separated from human recordings by appending `-s` to the repaired target label, e.g. `Ai-s` for synthetic repair audio targeting `Ai`.
- Use `Report_paper_9model/hf_anonymization/` as the public anonymization preparation package. Do not commit or upload the private original-name crosswalk.
- Any gender, region/logat, or speaker attributes are consented and necessary for the paper.
- License is chosen and compatible with voice data. Recommended options to discuss:
  - `CC BY-NC 4.0` if non-commercial research use only.
  - `CC BY 4.0` if broad reuse is explicitly consented.
  - A custom data-use agreement if identities/voices need stricter control.
- Add a takedown/contact procedure in the dataset card.
- Do not publish raw audio if consent only covers processed/research dataset.

## 7. Technical preparation commands

### 7.1 Confirm HF tooling

Current local check:

```text
hf CLI: available at /home/wayan/.local/bin/hf, version 1.19.0
huggingface_hub: installed, version 1.19.0
python datasets: not installed locally
```

Optional install for dataset validation:

```bash
python3 -m pip install --user "datasets[audio]" soundfile pyarrow pandas
```

### 7.2 Login and create private dataset repo

```bash
hf auth login
hf repo create RatnaAtika/Indonesian-ASR-11-Class-Dataset --repo-type dataset --private --exist-ok
```

If using a staging name:

```bash
hf repo create RatnaAtika/indonesian-asr-11class-paper-private --repo-type dataset --private --exist-ok
```

### 7.3 Prepare speaker anonymization artifacts

Generate/refresh public anonymization inventory before building the HF staging folder:

```bash
python3 tools_prepare_hf_anonymization.py
```

If an internal audit crosswalk is needed, generate it locally only and do not commit/upload it:

```bash
python3 tools_prepare_hf_anonymization.py --private-crosswalk
```

Public committed preparation files:

```text
Report_paper_9model/hf_anonymization/speaker_id_public_inventory.csv
Report_paper_9model/hf_anonymization/speaker_id_public_inventory.json
Report_paper_9model/hf_anonymization/synthetic_repair_targets_public.csv
Report_paper_9model/hf_anonymization/hf_public_metadata_schema.md
Report_paper_9model/hf_anonymization/speaker_anonymization_preparation_report.md
```

Private ignored crosswalk path:

```text
Report_paper_9model/hf_anonymization_private/speaker_crosswalk_PRIVATE_DO_NOT_UPLOAD.csv
```

### 7.4 Build local HF staging folder

Recommended staging folder outside Git worktree:

```bash
mkdir -p /mnt/c/Users/wayandadang/AI/Dataset_ASR_HF_STAGING
mkdir -p /mnt/c/Users/wayandadang/AI/Dataset_ASR_HF_STAGING_SOURCE
```

Use copy mode, not hardlinks, to avoid accidental mutation of source training folders. **Important:** the commands below are source-collection commands; before upload, the staged dataset paths/metadata must be rewritten so respondent folders and `speaker_id` values use only final public labels: two-character codes for human audio and `<target-label>-s` for synthetic repair audio.

```bash
rsync -a --copy-links --info=progress2 \
  Processed_Balanced19_v3/Dataset_Balanced19/ \
  /mnt/c/Users/wayandadang/AI/Dataset_ASR_HF_STAGING_SOURCE/data/processed_balanced19_v3/Dataset_Balanced19/

rsync -a --info=progress2 \
  Processed_Balanced19_v3/Transkrip_ASR_Jurnal_Dataset/ \
  /mnt/c/Users/wayandadang/AI/Dataset_ASR_HF_STAGING/data/transcripts/

rsync -a metadata/dataset_metadata.csv metadata/dataset_metadata_clean.csv metadata/dataset_metadata_summary.json \
  /mnt/c/Users/wayandadang/AI/Dataset_ASR_HF_STAGING_SOURCE/metadata/

rsync -a splits/ \
  /mnt/c/Users/wayandadang/AI/Dataset_ASR_HF_STAGING_SOURCE/splits/
```

For model artifacts:

```bash
rsync -a --copy-links --info=progress2 \
  Report_paper_9model/model_artifacts/ \
  /mnt/c/Users/wayandadang/AI/Dataset_ASR_HF_STAGING/models/final_9model_benchmark/

rsync -a --copy-links --info=progress2 \
  Report_paper_9model/training_diagnostics/ \
  /mnt/c/Users/wayandadang/AI/Dataset_ASR_HF_STAGING/models/final_9model_benchmark/training_diagnostics/
```

Then add the 9 full `predictions.csv` files from their final run directories into the corresponding rank `run_outputs/` folders. These are intentionally skipped by GitHub but should be present in HF.

Before upload, run a final privacy check over the upload staging folder: no original respondent names should appear in uploaded audio paths, metadata rows, split examples, README snippets, or dataset-card examples. Keep any private source staging folder (`Dataset_ASR_HF_STAGING_SOURCE`) local only.

Required public metadata fields after rewrite:

```text
speaker_id               = two-letter code for human rows; <target-label>-s for synthetic rows
speaker_type             = human or synthetic
speaker_gender           = Male/Female
is_synthetic             = True/False
synthetic_voice_id       = <target-label>-s for synthetic rows; blank for human rows
repair_target_speaker_id = target two-letter code for synthetic rows; blank for human rows
```

Human rows keep a two-letter `speaker_id`. Synthetic rows use `speaker_id=<target-label>-s`, while `repair_target_speaker_id` preserves the public human slot repaired by the TTS item. Gender lookup is provided separately in `Report_paper_9model/hf_anonymization/speaker_label_gender_list.csv`.

### 7.5 Generate upload manifest

Create a manifest with path, size, and SHA-256 for every staged file:

```bash
python3 - <<'PY'
from pathlib import Path
import csv, hashlib, json, datetime
root=Path('/mnt/c/Users/wayandadang/AI/Dataset_ASR_HF_STAGING')
rows=[]
for p in sorted(root.rglob('*')):
    if not p.is_file():
        continue
    rel=p.relative_to(root).as_posix()
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    rows.append({'path':rel,'size_bytes':p.stat().st_size,'sha256':h.hexdigest()})
(root/'upload_manifest.json').write_text(json.dumps({'generated_at':datetime.datetime.now().isoformat(),'file_count':len(rows),'files':rows}, indent=2), encoding='utf-8')
with (root/'upload_manifest.csv').open('w', newline='', encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=['path','size_bytes','sha256'])
    w.writeheader(); w.writerows(rows)
print('files',len(rows),'bytes',sum(r['size_bytes'] for r in rows))
PY
```

### 7.6 Upload using resumable large-folder upload

Recommended for this project because there are many files and large audio/model artifacts:

```bash
hf upload-large-folder RatnaAtika/Indonesian-ASR-11-Class-Dataset \
  /mnt/c/Users/wayandadang/AI/Dataset_ASR_HF_STAGING \
  --repo-type dataset \
  --private \
  --num-workers 4
```

If upload is interrupted, rerun the same command. It is resumable.

### 7.7 Post-upload verification

After upload:

```bash
hf repo files RatnaAtika/Indonesian-ASR-11-Class-Dataset --repo-type dataset | tee hf_remote_files.txt
```

Then compare remote file list against `upload_manifest.csv` count. For critical files, download a few and compare SHA-256:

```bash
python3 - <<'PY'
from huggingface_hub import hf_hub_download
from pathlib import Path
import hashlib
repo='RatnaAtika/Indonesian-ASR-11-Class-Dataset'
critical=[
 'metadata/dataset_metadata_summary.json',
 'splits/split_summary.json',
 'models/final_9model_benchmark/artifact_index.json',
 'models/final_9model_benchmark/rank01_m02b-whisper-small-ft/best_artifact/model.safetensors',
]
for f in critical:
    p=Path(hf_hub_download(repo_id=repo, repo_type='dataset', filename=f))
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    print(f, h)
PY
```

## 8. Suggested HF dataset card sections

The HF `README.md` should contain:

1. Dataset title and short description.
2. Private-staging warning while paper is under review.
3. Dataset composition: 104,500 utterances, 11 classes, 20 speakers.
4. Split protocol: speaker-disjoint train/dev/test, seed 42.
5. File structure and how to load audio/metadata.
6. Benchmark summary with link to `paper/Report_paper_9model/benchmark/benchmark.json`.
7. Model artifact section explaining all 9 best checkpoints are under `models/final_9model_benchmark/`.
8. Limitations: controlled phrases, limited speakers, Indonesian regional accents, synthetic repair subset 0.1263%.
9. Ethics/consent statement.
10. License and citation.
11. Contact/takedown procedure.

## 9. Final pre-upload checklist

- [ ] Decide final HF repo ID.
- [ ] Login to HF with account/org permission.
- [ ] Confirm private repo creation.
- [ ] Decide whether raw `Dataset_Ori/` is included now, later, or never.
- [x] Prepare speaker anonymization policy: human public HF labels use short two-character codes; synthetic public labels use `<target-label>-s`; private crosswalk is not committed/uploaded.
- [ ] Confirm license.
- [ ] Build staging folder with processed data, metadata, splits, models, predictions, diagnostics, and paper docs.
- [ ] Generate `upload_manifest.json` and `upload_manifest.csv`.
- [ ] Run local manifest checksum verification.
- [ ] Upload with `hf upload-large-folder`.
- [ ] Compare remote files to manifest.
- [ ] Save HF commit hash/URL into paper Data Availability draft.
- [ ] Keep repo private until paper acceptance/public-release approval.

## 10. Current blockers

Actual upload should wait for these decisions/inputs:

1. HF repo ID / organization confirmed.
2. HF login/token available in this environment.
3. License chosen.
4. Consent decision for publishing gender/region/logat attributes and raw audio.
5. Decision whether to upload `Dataset_Ori/` raw audio in the same private package or only upload final processed data first.
