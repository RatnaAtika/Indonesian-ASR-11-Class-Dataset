"""Canonical validation-split path resolution.

Active pipelines use ``val.tsv``. Historical checkouts may still contain
``dev.tsv``; that legacy filename is accepted temporarily for replay only and
emits a warning so new runs record the compatibility path explicitly.
"""
from __future__ import annotations

import warnings
from pathlib import Path


def resolve_validation_tsv(splits_dir: Path) -> Path:
    """Return ``val.tsv``, falling back to historical ``dev.tsv`` when needed."""
    splits_dir = Path(splits_dir)
    canonical = splits_dir / "val.tsv"
    if canonical.is_file():
        return canonical

    legacy = splits_dir / "dev.tsv"
    if legacy.is_file():
        warnings.warn(
            f"Using legacy validation split path {legacy}; migrate to {canonical}",
            FutureWarning,
            stacklevel=2,
        )
        return legacy

    raise FileNotFoundError(
        f"Validation split not found: expected {canonical} "
        f"(or historical compatibility path {legacy})"
    )
