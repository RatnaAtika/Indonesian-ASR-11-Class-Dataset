#!/usr/bin/env python3
"""Semantic guardrails for the NSS-ID internal working manuscript."""

from __future__ import annotations

import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT_PATH = ROOT / "Draft_Paper" / "04_Revised_Draft" / "04_INTERNAL_WORKING_MANUSCRIPT.md"
LEDGER_PATH = ROOT / "Draft_Paper" / "04_Revised_Draft" / "03_MATERIAL_GAP_PLACEHOLDERS.md"
REFERENCES_PATH = ROOT / "Draft_Paper" / "02_Evidence" / "VERIFIED_REFERENCES.csv"
TABLE_DIR = ROOT / "Draft_Paper" / "04_Revised_Draft" / "tables"


class InternalManuscriptSemanticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manuscript = MANUSCRIPT_PATH.read_text(encoding="utf-8")
        cls.ledger = LEDGER_PATH.read_text(encoding="utf-8")

    def test_status_title_and_length_controls(self) -> None:
        self.assertTrue(self.manuscript.startswith("# INTERNAL WORKING MANUSCRIPT — NOT FOR SUBMISSION"))
        self.assertIn("NSS-ID: An Indonesian read-speech dataset spanning 11 communicative sentence categories", self.manuscript)
        abstract = self.manuscript.split("## Abstract", 1)[1].split("**Keywords:**", 1)[0]
        words = re.findall(r"\b[\w'-]+\b", abstract)
        self.assertGreaterEqual(len(words), 190)
        self.assertLessEqual(len(words), 250)
        keywords = self.manuscript.split("**Keywords:**", 1)[1].split("\n", 1)[0]
        self.assertGreaterEqual(len([item for item in keywords.split(";") if item.strip()]), 1)
        self.assertLessEqual(len([item for item in keywords.split(";") if item.strip()]), 7)

    def test_dataset_article_heading_order_and_methods_depth(self) -> None:
        expected = [
            "# 1. Value of the Data",
            "# 2. Background",
            "# 3. Data description",
            "# 4. Experimental design, materials and methods",
            "# 5. Technical validation",
            "# 6. Limitations and responsible use",
        ]
        positions = [self.manuscript.index(heading) for heading in expected]
        self.assertEqual(sorted(positions), positions)
        self.assertNotIn("# 1. Objective and background", self.manuscript)
        self.assertNotIn("# 3. Experimental design, materials and methods", self.manuscript)

        methods = self.manuscript.split(expected[3], 1)[1].split(expected[4], 1)[0]
        method_words = re.findall(r"\b[\w'-]+\b", methods)
        self.assertGreaterEqual(len(method_words), 1_700)
        for statement in [
            "OBSERVED, INFERRED, CONFLICTED, or MISSING",
            "110,000 source WAV files",
            "5,500 take directories",
            "5,500 omitted files",
            "two-digit sentence filenames",
            "approximately 1.5037 m × 2.5027 m",
            "1,956",
            "seed 42",
            "297 sampled files",
            "Supplementary Table S6",
        ]:
            with self.subTest(statement=statement):
                self.assertIn(statement, methods)

    def test_all_exact_material_gap_tokens_are_preserved(self) -> None:
        tokens: list[str] = []
        for token in re.findall(r"`(\[MATERIAL GAP:[^`]+\])`", self.ledger):
            if token not in tokens:
                tokens.append(token)
        self.assertEqual(33, len(tokens))
        missing = [token for token in tokens if token not in self.manuscript]
        self.assertEqual([], missing)
        self.assertNotIn("[MATERIAL GAP]", self.manuscript)

    def test_release_target_and_benchmark_claims_are_scope_qualified(self) -> None:
        required = [
            "104,500 audio files totaling 134.1762 h",
            "104,368 human recordings and 132 explicitly labelled synthetic repairs (0.1263%)",
            "209 canonical balanced sentence slots",
            "separate, pre-transcript-repair frozen subset of 102,544 files",
            "102,544-file, 130.6548-h frozen benchmark",
            "15,374 human recordings and two synthetic repairs",
            "seen-script held-out-human-speaker recognition",
            "private Hugging Face repository",
            "card licence is `other`",
            "no persistent dataset DOI",
        ]
        for statement in required:
            with self.subTest(statement=statement):
                self.assertIn(statement, self.manuscript)

    def test_prohibited_or_stale_formulations_are_absent(self) -> None:
        prohibited = [
            "full public corpus",
            "213 " + "unique texts",
            "213 " + "distinct `(category, sentence_id)` pairs",
            "0.129%",
            "stratified sample",
            "validated transcription",
            "validated transcripts",
            "anonymous speakers",
            "anonymized speaker metadata",
            "publicly available",
            "freely available",
            "15,376 held-out-speaker human utterances",
            "state of the art",
            "104.500",
            "pre-repair frozen",
            "0.852% WER",
            "1.777% WER",
        ]
        lower = self.manuscript.lower()
        for phrase in prohibited:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase.lower(), lower)
        self.assertIsNone(re.search(r"\banonymous\b", lower))
        self.assertIsNone(re.search(r"\banonymized\b", lower))

    def test_no_private_or_machine_specific_paths_are_embedded(self) -> None:
        self.assertNotIn("/mnt/c/Users/", self.manuscript)
        self.assertNotRegex(self.manuscript, r"/home/[^/\s]+/")
        self.assertNotIn("Dataset_Ori/", self.manuscript)
        self.assertNotIn("Processed_Balanced19", self.manuscript)

    def test_reference_register_and_manuscript_reference_order_match(self) -> None:
        with REFERENCES_PATH.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(16, len(rows))
        self.assertEqual(list(range(1, 17)), [int(row["ref_no"]) for row in rows])
        self.assertEqual(16, len({row["cite_key"] for row in rows}))
        self.assertEqual(16, len({row["url"] for row in rows}))
        self.assertTrue(all(row["verification_status"].startswith("verified") for row in rows))

        references = self.manuscript.split("# References", 1)[1]
        numbered = [int(value) for value in re.findall(r"(?m)^(\d+)\. ", references)]
        self.assertEqual(list(range(1, 17)), numbered)
        for row in rows:
            if row["doi"]:
                self.assertIn(row["doi"].lower(), references.lower())
            else:
                self.assertIn(row["url"], references)

        body = self.manuscript.split("# References", 1)[0]
        first_use: list[int] = []
        for group in re.findall(r"\[((?:\d+,?)+)\]", body):
            for value in group.split(","):
                number = int(value)
                if number not in first_use:
                    first_use.append(number)
        self.assertEqual(list(range(1, 17)), first_use)

    def test_editable_main_tables_exist_and_are_parseable(self) -> None:
        expected = [
            "Specifications_Table.csv",
            "Table_1_package_inventory.csv",
            "Table_2_scope_bridge.csv",
            "Table_3_release_target_category_composition.csv",
            "Table_4_release_target_split_source_composition.csv",
            "Table_5_synthetic_repair_provenance.csv",
            "Table_S6_frozen_benchmark_validation.csv",
        ]
        for name in expected:
            path = TABLE_DIR / name
            with self.subTest(path=path):
                self.assertTrue(path.is_file())
                with path.open(newline="", encoding="utf-8-sig") as handle:
                    rows = list(csv.DictReader(handle))
                self.assertGreater(len(rows), 0)

    def test_benchmark_display_has_one_supplementary_identity(self) -> None:
        self.assertIn("Supplementary Table S6", self.manuscript)
        self.assertNotRegex(self.manuscript, r"(?<!Supplementary )Table 6")
        captions = (ROOT / "Draft_Paper" / "04_Revised_Draft" / "05_TABLE_CAPTIONS_AND_NOTES.md").read_text(encoding="utf-8")
        self.assertIn("## Table S6.", captions)
        self.assertNotIn("## Table 6.", captions)

    def test_editable_tables_use_only_canonical_material_gap_tokens(self) -> None:
        canonical = set(re.findall(r"`(\[MATERIAL GAP:[^`]+\])`", self.ledger))
        table_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in TABLE_DIR.glob("*.csv"))
        observed = set(re.findall(r"\[MATERIAL GAP:[^]]+\]", table_text))
        self.assertTrue(observed.issubset(canonical), sorted(observed - canonical))

    def test_table_caption_companion_contains_scope_and_rounding_controls(self) -> None:
        captions = (ROOT / "Draft_Paper" / "04_Revised_Draft" / "05_TABLE_CAPTIONS_AND_NOTES.md").read_text(encoding="utf-8")
        self.assertIn("NOT FOR SUBMISSION", captions)
        self.assertIn("uniform diagnostic rescore", captions.lower())
        self.assertIn("134.1763 h", captions)
        self.assertIn("authoritative total calculated from unrounded seconds is 134.1762 h", captions)


if __name__ == "__main__":
    unittest.main()
