#!/usr/bin/env python3
"""Regression tests for the internal Data in Brief editable-table builder."""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Draft_Paper" / "99_Admin" / "build_revised_manuscript_tables.py"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


class RevisedManuscriptTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.output_dir = Path(cls.tempdir.name)
        subprocess.run(
            [sys.executable, str(BUILDER), "--output-dir", str(cls.output_dir)],
            cwd=ROOT,
            check=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tempdir.cleanup()

    def test_expected_editable_tables_exist(self) -> None:
        expected = {
            "Specifications_Table.csv",
            "Table_1_package_inventory.csv",
            "Table_2_scope_bridge.csv",
            "Table_3_release_target_category_composition.csv",
            "Table_4_release_target_split_source_composition.csv",
            "Table_5_synthetic_repair_provenance.csv",
            "Table_S6_frozen_benchmark_validation.csv",
        }
        self.assertEqual(expected, {path.name for path in self.output_dir.glob("*.csv")})

    def test_specifications_table_matches_official_v19_fixed_rows(self) -> None:
        rows = read_csv(self.output_dir / "Specifications_Table.csv")
        self.assertEqual(
            [
                "Subject",
                "Specific subject area",
                "Type of data",
                "Data collection",
                "Data source location",
                "Data accessibility",
                "Related research article",
            ],
            [row["item"] for row in rows],
        )
        self.assertLessEqual(len(rows[1]["description"].replace(" ", "")), 150)
        self.assertLessEqual(len(rows[3]["description"].replace(" ", "")), 600)
        self.assertIn("not publicly accessible", rows[5]["description"].lower())

    def test_scope_bridge_keeps_release_target_and_benchmark_separate(self) -> None:
        rows = {row["field"]: row for row in read_csv(self.output_dir / "Table_2_scope_bridge.csv")}
        self.assertEqual("104500", rows["Files"]["release_target"])
        self.assertEqual("102544", rows["Files"]["frozen_benchmark"])
        self.assertEqual("134.1762", rows["Duration (h)"]["release_target"])
        self.assertEqual("130.6548", rows["Duration (h)"]["frozen_benchmark"])
        self.assertEqual("213", rows["Distinct (category, sentence_id) pairs"]["release_target"])
        self.assertEqual("209", rows["Distinct (category, sentence_id) pairs"]["frozen_benchmark"])
        self.assertEqual("1956", rows["Rows present only in release target"]["release_target"])
        self.assertEqual("15675 items = 15673 human + 2 synthetic", rows["Test composition"]["release_target"])
        self.assertEqual("15376 items = 15374 human + 2 synthetic", rows["Test composition"]["frozen_benchmark"])

    def test_category_table_uses_release_target_values(self) -> None:
        rows = read_csv(self.output_dir / "Table_3_release_target_category_composition.csv")
        self.assertEqual(11, len(rows))
        self.assertEqual(104500, sum(int(row["files"]) for row in rows))
        by_category = {row["category_english"]: row for row in rows}
        self.assertEqual("6.5202", by_category["Persuasive"]["mean_duration_sec"])
        self.assertEqual("6.0519", by_category["Conditional"]["mean_duration_sec"])
        self.assertEqual("5.6065", by_category["Confirmation"]["mean_duration_sec"])
        self.assertIn("19=490", by_category["Conditional"]["sentence_id_note"])
        self.assertIn("20=10", by_category["Conditional"]["sentence_id_note"])

    def test_split_table_discloses_source_and_synthetic_imbalance(self) -> None:
        rows = {row["split"]: row for row in read_csv(self.output_dir / "Table_4_release_target_split_source_composition.csv")}
        self.assertEqual("14", rows["train"]["human_speakers"])
        self.assertEqual("3", rows["dev"]["human_speakers"])
        self.assertEqual("3", rows["test"]["human_speakers"])
        self.assertEqual("0", rows["dev"]["female_source_files"])
        self.assertEqual("2", rows["test"]["female_source_files"])
        self.assertEqual("2", rows["test"]["synthetic_files"])
        self.assertIn("no natural female", rows["test"]["interpretation_note"].lower())

    def test_synthetic_table_preserves_unresolved_mismatch(self) -> None:
        rows = read_csv(self.output_dir / "Table_5_synthetic_repair_provenance.csv")
        keyed = {(row["dimension"], row["value"]): row for row in rows}
        self.assertEqual("132", keyed[("Total", "Synthetic repairs")]["files"])
        self.assertEqual("632.5200", keyed[("Total", "Synthetic repairs")]["duration_sec"])
        self.assertEqual("2", keyed[("Mismatch", "Female-source / male-target")]["files"])
        self.assertIn("MATERIAL GAP", keyed[("Mismatch", "Female-source / male-target")]["note"])

    def test_benchmark_table_reports_uniform_compact_percentages_for_nine_models(self) -> None:
        rows = read_csv(self.output_dir / "Table_S6_frozen_benchmark_validation.csv")
        self.assertEqual(9, len(rows))
        self.assertEqual(
            ["model_family", "wer_percent", "cer_percent", "parameters"],
            list(rows[0]),
        )
        self.assertEqual(sorted(row["model_family"] for row in rows), [row["model_family"] for row in rows])
        by_family = {row["model_family"]: row for row in rows}
        self.assertEqual("0.186", by_family["Whisper-small FT"]["wer_percent"])
        self.assertEqual("0.140", by_family["Whisper-small FT"]["cer_percent"])
        self.assertEqual("1.761", by_family["ViT-modified-ID"]["wer_percent"])
        self.assertEqual("1.298", by_family["ViT-modified-ID"]["cer_percent"])
        self.assertEqual("4353248", by_family["ViT-modified-ID"]["parameters"])

    def test_generated_tables_avoid_prohibited_scope_language(self) -> None:
        text = "\n".join(path.read_text(encoding="utf-8-sig") for path in self.output_dir.glob("*.csv"))
        self.assertNotIn("full public corpus", text.lower())
        self.assertNotIn("anonymous speaker", text.lower())
        self.assertNotIn("stratified sample", text.lower())
        self.assertNotIn("unseen-text", text.lower())


if __name__ == "__main__":
    unittest.main()
