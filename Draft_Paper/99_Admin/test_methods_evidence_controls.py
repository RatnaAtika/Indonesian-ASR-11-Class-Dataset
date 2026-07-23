#!/usr/bin/env python3
"""Guardrails for the methods evidence matrix and author questionnaire."""

from __future__ import annotations

import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "Draft_Paper" / "02_Evidence"
MATRIX_PATH = EVIDENCE_DIR / "METHODS_EVIDENCE_MATRIX.csv"
QUESTIONNAIRE_PATH = EVIDENCE_DIR / "AUTHOR_METHODS_EVIDENCE_QUESTIONNAIRE.md"
DRAFT_DIR = ROOT / "Draft_Paper" / "04_Revised_Draft"
LEDGER_PATH = DRAFT_DIR / "03_MATERIAL_GAP_PLACEHOLDERS.md"
FLOW_PATH = DRAFT_DIR / "01_CLAIM_EVIDENCE_FLOW.csv"


class MethodsEvidenceControlsTests(unittest.TestCase):
    def test_matrix_schema_classifications_and_core_conflicts(self) -> None:
        with MATRIX_PATH.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        expected_columns = {
            "method_id",
            "domain",
            "proposed_fact_or_required_detail",
            "classification",
            "evidence_nature",
            "source_artifact",
            "line_or_locator",
            "evidence_safe_wording",
            "publication_action",
            "blocking_level",
            "related_material_gap_token",
        }
        self.assertTrue(expected_columns.issubset(set(rows[0])))
        self.assertGreaterEqual(len(rows), 60)
        self.assertEqual(len(rows), len({row["method_id"] for row in rows}))
        allowed = {"OBSERVED", "INFERRED", "CONFLICTED", "MISSING"}
        self.assertTrue(all(row["classification"] in allowed for row in rows))
        self.assertTrue(all(row["source_artifact"] and row["line_or_locator"] for row in rows))
        matrix_text = MATRIX_PATH.read_text(encoding="utf-8-sig")
        for subgate in ["SG-METADATA-BUILD", "SG-AUDIO-QC", "SG-BENCHMARK-METHODS"]:
            self.assertIn(subgate, matrix_text)

        joined = "\n".join(
            row["proposed_fact_or_required_detail"] + " " + row["evidence_safe_wording"]
            for row in rows
        ).lower()
        for phrase in [
            "room dimensions",
            "participant age",
            "1,956",
            "seed 42",
            "297 sampled files",
            "voice-identifiable",
            "104,500",
            "102,544",
            "nssid_project_uniform_v1",
            "135,911",
            "sentencepiece",
            "per-recipe method cards",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, joined)

    def test_claim_evidence_flow_is_structural_and_uses_canonical_gap_tokens(self) -> None:
        with FLOW_PATH.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
        self.assertEqual(
            [
                "flow_id",
                "section",
                "claim_or_required_statement",
                "scope",
                "evidence_tier",
                "status",
                "primary_evidence",
                "display_or_location",
                "allowed_wording",
                "prohibited_extension",
            ],
            reader.fieldnames,
        )
        self.assertGreaterEqual(len(rows), 60)
        self.assertEqual(len(rows), len({row["flow_id"] for row in rows}))
        self.assertTrue(all(None not in row for row in rows))

        ledger = LEDGER_PATH.read_text(encoding="utf-8")
        canonical = set(re.findall(r"`(\[MATERIAL GAP:[^`]+\])`", ledger))
        flow_text = FLOW_PATH.read_text(encoding="utf-8")
        observed = set(re.findall(r"\[MATERIAL GAP(?::[^]]+)?\]", flow_text))
        self.assertNotIn("[MATERIAL GAP]", observed)
        self.assertTrue(observed.issubset(canonical), sorted(observed - canonical))

    def test_questionnaire_preserves_all_gap_tokens_and_secure_response_rules(self) -> None:
        questionnaire = QUESTIONNAIRE_PATH.read_text(encoding="utf-8")
        ledger = LEDGER_PATH.read_text(encoding="utf-8")
        canonical = []
        for token in re.findall(r"`(\[MATERIAL GAP:[^`]+\])`", ledger):
            if token not in canonical:
                canonical.append(token)
        self.assertEqual(33, len(canonical))
        missing = [token for token in canonical if token not in questionnaire]
        self.assertEqual([], missing)
        for phrase in [
            "NOT FOR SUBMISSION OR PUBLIC RELEASE",
            "Do not place the private respondent crosswalk",
            "Primary artifact",
            "Artifact date",
            "SHA-256",
            "Approved wording",
            "OBSERVED, INFERRED, CONFLICTED, or MISSING",
            "English response",
            "Jawaban Bahasa Indonesia",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, questionnaire)

    def test_questionnaire_does_not_treat_source_draft_as_event_verification(self) -> None:
        questionnaire = QUESTIONNAIRE_PATH.read_text(encoding="utf-8")
        self.assertIn("author-draft assertion is not proof that the event occurred", questionnaire)
        self.assertIn("1 × 1 × 2.5 m", questionnaire)
        self.assertIn("approximately 1.5037 m × 2.5027 m", questionnaire)
        self.assertIn("25–38", questionnaire)
        self.assertIn("22–38", questionnaire)
        self.assertNotIn("fully anonymized", questionnaire.lower())


if __name__ == "__main__":
    unittest.main()
