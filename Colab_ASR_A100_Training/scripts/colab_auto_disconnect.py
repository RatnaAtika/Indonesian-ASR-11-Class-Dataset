#!/usr/bin/env python3
"""Optionally disconnect/unassign a Google Colab runtime after final sync.

Controlled by A100_AUTO_DISCONNECT=1. Best-effort; safe no-op outside Colab.
"""
from __future__ import annotations
import os, time

flag = os.environ.get("A100_AUTO_DISCONNECT", "0").strip().lower()
if flag not in {"1", "true", "yes", "y", "on"}:
    print("[auto-disconnect] disabled (set A100_AUTO_DISCONNECT=1 to enable).")
    raise SystemExit(0)

print("[auto-disconnect] A100_AUTO_DISCONNECT=1; disconnecting runtime after final sync.")
time.sleep(5)
try:
    from google.colab import runtime  # type: ignore
    runtime.unassign()
except Exception as e:
    print(f"[auto-disconnect] warning: could not unassign runtime: {e}")
