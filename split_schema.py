"""Canonical dataset split vocabulary shared by active tooling."""
from __future__ import annotations

CANONICAL_SPLITS = ("train", "val", "test")
_SPLIT_ALIASES = {
    "train": "train",
    "val": "val",
    "dev": "val",
    "valid": "val",
    "validation": "val",
    "test": "test",
}


def canonical_split(value: object) -> str:
    """Return the canonical ``train``/``val``/``test`` token.

    Historical validation aliases remain accepted at ingestion boundaries so
    archived manifests can be replayed without rewriting their provenance.
    """
    token = str(value).strip().lower()
    try:
        return _SPLIT_ALIASES[token]
    except KeyError as exc:
        raise ValueError(f"unsupported split value: {value!r}") from exc
