#!/usr/bin/env python3
"""Regression tests for publication-safe evidence-registry wording and scope."""
from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "Draft_Paper" / "02_Evidence"


class EvidenceRegistrySemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads((EVIDENCE / "evidence_registry.json").read_text(encoding="utf-8"))
        with (EVIDENCE / "claim_evidence_matrix.csv").open(encoding="utf-8", newline="") as handle:
            cls.claims = {row["claim_id"]: row for row in csv.DictReader(handle)}
        cls.summary = (EVIDENCE / "EVIDENCE_REGISTRY.md").read_text(encoding="utf-8")

    def test_private_staging_is_not_named_public_corpus(self) -> None:
        self.assertIn("release_target_dataset", self.registry)
        self.assertNotIn("full_public_dataset", self.registry)
        self.assertNotIn("public corpus", self.claims["C001"]["claim"].lower())
        self.assertIn("release-target", self.claims["C001"]["claim"].lower())
        self.assertIn("Release-target corpus and private HF staging", self.summary)

    def test_pre_repair_and_repaired_transcript_states_are_separate(self) -> None:
        release = self.registry["release_target_dataset"]
        self.assertEqual(release["local_pre_repair_metadata_snapshot"]["blank_transcripts"], 1956)
        self.assertNotIn("local_source_validation", release)
        self.assertEqual(self.registry["hf_repository"]["blank_transcripts_after_repair"], 0)
        self.assertTrue(self.registry["hf_repository"]["private"])
        self.assertFalse(self.registry["hf_repository"]["persistent_dataset_doi_available"])

    def test_pair_count_does_not_claim_unique_texts(self) -> None:
        claim = self.claims["C005"]["claim"].lower()
        self.assertIn("213 distinct (category, sentence_id) pairs", claim)
        self.assertNotIn("213 unique", claim)
        self.assertNotIn("213 templates", claim)

    def test_test_set_claim_discloses_human_and_synthetic_items(self) -> None:
        claim = self.claims["C010"]["claim"]
        self.assertIn("15,376-item", claim)
        self.assertIn("15,374 human", claim)
        self.assertIn("2 synthetic", claim)
        self.assertNotIn("15,376 held-out-speaker utterances", claim)

    def test_sample_claim_does_not_assert_unattached_stratification(self) -> None:
        claim = self.claims["C014"]["claim"].lower()
        self.assertIn("297 sampled", claim)
        self.assertNotIn("stratified", claim)
        self.assertIn("sampling design pending", self.claims["C014"]["status"].lower())

    def test_template_overlap_claim_remains_attachment_gated(self) -> None:
        claim = self.claims["C013"]
        self.assertIn("seen scripts", claim["claim"].lower())
        self.assertIn("attachment required", claim["status"].lower())
        self.assertNotIn("OOD", claim["evidence"])

    def test_uniform_rescore_replaces_run_native_ranking_for_publication(self) -> None:
        benchmark = self.registry["benchmark_subset"]
        self.assertEqual(
            "Draft_Paper/02_Evidence/unified_benchmark_rescore/unified_nine_model_metrics.json",
            benchmark["publication_metric_source"],
        )
        self.assertEqual(9, len(benchmark["models"]))
        self.assertTrue(all("rank" not in model for model in benchmark["models"]))
        self.assertEqual(9, len(benchmark["models_run_native"]))
        self.assertIn("not comparable", benchmark["run_native_metric_comparability"].lower())
        by_id = {model["model_id"]: model for model in benchmark["models"]}
        self.assertAlmostEqual(0.00186151231320497, by_id["m02b-whisper-small-ft"]["wer"])
        self.assertAlmostEqual(0.00140144430452398, by_id["m02b-whisper-small-ft"]["cer"])
        self.assertAlmostEqual(0.0176144682917497, by_id["m12-vit-modified-ID"]["wer"])
        self.assertIn("uniform", self.claims["C011"]["claim"].lower())
        self.assertIn("run-native ranking must not be used", self.summary.lower())


if __name__ == "__main__":
    unittest.main()
