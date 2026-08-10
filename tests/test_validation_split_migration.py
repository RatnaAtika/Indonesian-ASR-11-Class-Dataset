from __future__ import annotations

import csv
import importlib.util
import re
import tempfile
import unittest
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidationSplitMigrationTests(unittest.TestCase):
    def test_canonical_split_maps_legacy_aliases_and_rejects_unknown_values(self):
        module = load_module(ROOT / "split_schema.py", "split_schema")
        for value in ("val", "dev", "valid", "validation"):
            with self.subTest(value=value):
                self.assertEqual("val", module.canonical_split(value))
        self.assertEqual("train", module.canonical_split("train"))
        self.assertEqual("test", module.canonical_split("test"))
        with self.assertRaises(ValueError):
            module.canonical_split("evaluation")

    def test_ignored_local_validation_manifest_is_never_committed_as_dev(self):
        val_path = ROOT / "training" / "data_final" / "val.tsv"
        legacy_path = ROOT / "training" / "data_final" / "dev.tsv"
        self.assertFalse(legacy_path.exists())
        if val_path.is_file():
            with val_path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter="\t"))
            self.assertEqual(15_376, len(rows))

    def test_modern_resolver_prefers_val_and_supports_legacy_fallback(self):
        module = load_module(
            ROOT / "training" / "common" / "split_compat.py",
            "modern_split_compat",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            legacy = root / "dev.tsv"
            canonical = root / "val.tsv"
            legacy.write_text("legacy\n", encoding="utf-8")
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                self.assertEqual(legacy, module.resolve_validation_tsv(root))
            self.assertEqual(1, len(caught))
            self.assertIn("legacy", str(caught[0].message).lower())
            canonical.write_text("canonical\n", encoding="utf-8")
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                self.assertEqual(canonical, module.resolve_validation_tsv(root))
            self.assertEqual([], caught)

    def test_conventional_resolver_prefers_val_and_supports_legacy_fallback(self):
        module = load_module(
            ROOT / "training_conventional" / "common" / "split_compat.py",
            "conventional_split_compat",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            legacy = root / "dev.tsv"
            canonical = root / "val.tsv"
            legacy.write_text("legacy\n", encoding="utf-8")
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                self.assertEqual(legacy, module.resolve_validation_tsv(root))
            self.assertEqual(1, len(caught))
            canonical.write_text("canonical\n", encoding="utf-8")
            self.assertEqual(canonical, module.resolve_validation_tsv(root))

    def test_active_training_sources_do_not_open_dev_directly(self):
        paths = [
            ROOT / "training/common/from_scratch_trainer.py",
            ROOT / "training/common/wav2vec2_trainer.py",
            ROOT / "training/common/whisper_trainer.py",
            ROOT / "training_conventional/common/feature_builder.py",
            ROOT / "training_conventional/common/spm_builder.py",
            ROOT / "training/zero_shot_baselines/run_inference.py",
            ROOT / "Colab_ASR_A100_Training/scripts/colab_verify_dataset.py",
        ]
        pattern = re.compile(r"(?i)\bdev\b|dev\.tsv")
        failures = []
        for path in paths:
            matches = pattern.findall(path.read_text(encoding="utf-8"))
            if matches:
                failures.append(f"{path.relative_to(ROOT)}: {len(matches)}")
        self.assertEqual([], failures)

    def test_active_public_split_tables_use_val_with_unchanged_counts(self):
        paths = [
            ROOT / "Report_paper_9model/hf_dataset_information_public/per_split_public.csv",
            ROOT / "Report_paper_9model/hf_upload_small_files/paper/dataset_information/per_split_public.csv",
            ROOT / "Draft_Paper/04_Revised_Draft/tables/Table_4_release_target_split_source_composition.csv",
        ]
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                with path.open(encoding="utf-8-sig", newline="") as handle:
                    rows = list(csv.DictReader(handle))
                by_split = {row["split"]: row for row in rows if row["split"] != "Total"}
                self.assertEqual({"train", "val", "test"}, set(by_split))
                count_key = "file_count" if "file_count" in by_split["val"] else "files"
                self.assertEqual(15_675, int(by_split["val"][count_key]))

    def test_active_tables_use_lf_without_trailing_carriage_returns(self):
        paths = [
            ROOT / "Draft_Paper/04_Revised_Draft/tables/Table_4_release_target_split_source_composition.csv",
            ROOT / "Draft_Paper/04_Revised_Draft/tables/Table_5_synthetic_repair_provenance.csv",
        ]
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertNotIn(b"\r\n", path.read_bytes())

    def test_split_migration_never_rewrites_unix_dev_null(self):
        paths = [ROOT / "RUN_GUIDE.md", ROOT / "note_prompt_linux.md"]
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("/val/null", text)

    def test_root_readme_uses_val_for_frozen_split(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("train 71,792 / val 15,376 / test 15,376", text)
        self.assertNotRegex(text, re.compile(r"(?i)train\s+71,792\s*/\s*dev\b"))


if __name__ == "__main__":
    unittest.main()
