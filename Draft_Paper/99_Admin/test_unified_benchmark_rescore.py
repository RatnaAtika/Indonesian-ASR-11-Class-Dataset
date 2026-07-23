#!/usr/bin/env python3
"""Tests for uniform rescoring of the nine frozen-benchmark prediction files."""

from __future__ import annotations

import csv
import importlib.util
import json
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Draft_Paper" / "99_Admin" / "rescore_nine_model_predictions.py"


def load_module():
    spec = importlib.util.spec_from_file_location("uniform_rescore", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reference_dp(a, b) -> int:
    previous = list(range(len(b) + 1))
    for i, left in enumerate(a, start=1):
        current = [i]
        for j, right in enumerate(b, start=1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (left != right)))
        previous = current
    return previous[-1]


class UniformRescoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def test_normalizer_matches_frozen_project_rule(self) -> None:
        normalize = self.module.normalize_text
        self.assertEqual("apa kabar", normalize("  Apa—kabar?!  "))
        self.assertEqual("robot's status", normalize("ROBOT'S   STATUS"))
        self.assertEqual("wifi ghz", normalize("WiFi 5 GHz"))

    def test_myers_distance_matches_reference_dp(self) -> None:
        distance = self.module.levenshtein_distance
        random.seed(42)
        alphabet = ["a", "b", "c", "d"]
        for _ in range(250):
            a = [random.choice(alphabet) for _ in range(random.randrange(0, 15))]
            b = [random.choice(alphabet) for _ in range(random.randrange(0, 15))]
            self.assertEqual(reference_dp(a, b), distance(a, b), (a, b))
        self.assertEqual(3, distance("kitten", "sitting"))
        self.assertEqual(0, distance([], []))

    def test_integration_writes_scope_safe_comparable_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            output_dir = Path(tempdir)
            subprocess.run(
                [sys.executable, str(SCRIPT), "--output-dir", str(output_dir)],
                cwd=ROOT,
                check=True,
                timeout=300,
            )
            csv_path = output_dir / "unified_nine_model_metrics.csv"
            json_path = output_dir / "unified_nine_model_metrics.json"
            report_path = output_dir / "BENCHMARK_SCORING_COMPARABILITY_AUDIT.md"
            self.assertTrue(csv_path.is_file())
            self.assertTrue(json_path.is_file())
            self.assertTrue(report_path.is_file())
            with csv_path.open(newline="", encoding="utf-8-sig") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(9, len(rows))
            self.assertEqual(9, len({row["model_id"] for row in rows}))
            self.assertTrue(all(row["normalizer_id"] == "nssid_project_uniform_v1" for row in rows))
            self.assertTrue(all(row["n_test_items"] == "15376" for row in rows))
            self.assertTrue(all(row["reference_words"] == "135911" for row in rows))
            self.assertTrue(all(row["reference_characters"] == "942599" for row in rows))
            self.assertTrue(all(row["canonical_reference_match"] == "True" for row in rows))
            self.assertNotIn("rank", rows[0])

            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual("splits/test_clean.tsv", payload["canonical_reference_manifest"])
            self.assertEqual(15376, payload["n_test_items"])
            self.assertEqual(135911, payload["reference_words"])
            self.assertEqual(942599, payload["reference_characters"])
            self.assertEqual(9, len(payload["models"]))
            report = report_path.read_text(encoding="utf-8")
            self.assertIn("NOT FOR SUBMISSION", report)
            self.assertIn("136,211", report)
            self.assertIn("135,911", report)
            self.assertIn("historical run-native ranking", report.lower())
            self.assertIn("0.186", report)


if __name__ == "__main__":
    unittest.main()
