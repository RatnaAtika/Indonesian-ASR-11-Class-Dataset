# Validation split migration: `dev` → `val`

## Canonical convention

Active NSS-ID pipelines use:

```text
machine tokens: train / val / test
reader labels:  Train / Validation / Test
```

`dev`, `valid`, and `validation` are accepted only at ingestion boundaries and normalize to `val`. Historical run bundles, archived source packages, prior verification sessions, and pinned repository revisions are not rewritten.

## Scope-specific counts

| Scope | Train | Val | Test |
|---|---:|---:|---:|
| Release target | 73,150 | 15,675 | 15,675 |
| Frozen nine-model benchmark | 71,792 | 15,376 | 15,376 |

The scopes remain distinct. Renaming does not alter row membership, speaker assignment, audio, synthetic flags, or benchmark metrics.

## Compatibility behavior

Active training loaders prefer `training/data_final/val.tsv`. For replay of an older local checkout, they temporarily fall back to `training/data_final/dev.tsv` and emit a `FutureWarning`. Conventional cached features retain the historical filename `valid.pkl`; this cache name is not a split-schema value.

Because `training/data_final/` is intentionally ignored, existing local workspaces must rename their manifest explicitly:

```bash
mv training/data_final/dev.tsv training/data_final/val.tsv
```

Before renaming, verify that `val.tsv` does not already exist and that the source contains 15,376 data rows plus its header. Do not modify archived run directories or packaged historical source.

## Historical boundary

The following remain historical and may still contain `dev`:

- `**/runs/**`
- `Report_paper_9model/model_artifacts/**/source_code/**`
- `Whisper_Verification_Sessions/**`
- `Draft_Paper/01_Extraction/**`
- pinned HF snapshots and prior review/evidence records
- legacy statistical reports whose filenames and hashes are part of prior evidence

When citing these artifacts, interpret historical `dev` as the validation partition for the frozen benchmark or the development partition for the release target, according to the artifact scope.

## Consumer migration

Replace filters such as:

```python
df[df["split"] == "dev"]
```

with:

```python
df[df["split"] == "val"]
```

Pin the pre-migration Hugging Face revision when exact historical replay is required.
