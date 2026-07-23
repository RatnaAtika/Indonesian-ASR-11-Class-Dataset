#!/usr/bin/env python3
"""Regression tests for deterministic release-target manuscript figures."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Draft_Paper" / "99_Admin" / "build_release_target_figures.py"


class ReleaseTargetFigureTests(unittest.TestCase):
    def test_builder_generates_public_safe_scope_qualified_artwork(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            output = Path(tempdir)
            subprocess.run(
                [sys.executable, str(SCRIPT), "--output-dir", str(output)],
                cwd=ROOT,
                check=True,
                timeout=180,
            )
            expected = {
                "Figure_1_construction_package_flow.png",
                "Figure_1_construction_package_flow.svg",
                "Figure_2_release_target_duration_by_category.png",
                "Figure_2_release_target_duration_by_category.svg",
                "Figure_3_release_target_split_source_composition.png",
                "Figure_3_release_target_split_source_composition.svg",
                "figure_manifest.json",
            }
            self.assertEqual(expected, {path.name for path in output.iterdir()})

            for path in output.glob("*.png"):
                with Image.open(path) as image:
                    self.assertGreaterEqual(image.width, 3000)
                    self.assertGreaterEqual(image.height, 2000)
                    dpi = image.info.get("dpi", (0, 0))
                    self.assertGreaterEqual(dpi[0], 590)
                    self.assertGreaterEqual(dpi[1], 590)
                    self.assertEqual("RGB", image.mode)

            combined_svg = "\n".join(path.read_text(encoding="utf-8") for path in output.glob("*.svg"))
            self.assertIn("NOT FOR SUBMISSION", combined_svg)
            self.assertIn("104,500", combined_svg)
            self.assertIn("17.2061 h", combined_svg)
            self.assertIn("73,150", combined_svg)
            self.assertIn("15,374 human + 2 synthetic", combined_svg)
            self.assertIn("Pre-transcript-repair metadata state", combined_svg)
            self.assertIn("transcript repair → release target", combined_svg)
            self.assertIn("blank-row exclusion → frozen benchmark", combined_svg)
            self.assertIn("20 retained human labels", combined_svg)
            self.assertIn("Private staging — release not authorized", combined_svg)
            self.assertNotIn("20 human speakers", combined_svg)
            self.assertNotIn("/mnt/c/", combined_svg)
            self.assertNotIn("/home/", combined_svg)
            self.assertNotIn("full public corpus", combined_svg.lower())
            self.assertNotIn("stratified", combined_svg.lower())
            self.assertNotIn("anonymous", combined_svg.lower())

            manifest = json.loads((output / "figure_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("release_target", manifest["figure_2_scope"])
            self.assertEqual("release_target", manifest["figure_3_scope"])
            self.assertEqual("internal_not_for_submission", manifest["status"])
            self.assertEqual(6, len(manifest["outputs"]))
            self.assertTrue(all(len(item["sha256"]) == 64 for item in manifest["outputs"]))
            self.assertTrue(all(len(item["sha256"]) == 64 for item in manifest["sources"]))


if __name__ == "__main__":
    unittest.main()
