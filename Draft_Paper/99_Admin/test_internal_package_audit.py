#!/usr/bin/env python3
"""End-to-end test for the internal-only package verifier."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BUILDER=ROOT/"Draft_Paper/99_Admin/build_internal_docx_package.py"
VERIFIER=ROOT/"Draft_Paper/99_Admin/verify_internal_manuscript_package.py"

class InternalPackageAuditTests(unittest.TestCase):
    def test_fresh_package_passes_only_internal_mechanical_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            base=Path(tempdir); package=base/"package"; report_md=base/"report.md"; report_json=base/"report.json"
            subprocess.run([sys.executable,str(BUILDER),"--output-dir",str(package)],cwd=ROOT,check=True,timeout=240)
            subprocess.run([sys.executable,str(VERIFIER),"--package-dir",str(package),"--report-md",str(report_md),"--report-json",str(report_json)],cwd=ROOT,check=True,timeout=240)
            payload=json.loads(report_json.read_text(encoding="utf-8"))
            self.assertEqual("PASS_INTERNAL_ONLY",payload["status"])
            self.assertFalse(payload["submission_authorized"])
            self.assertFalse(payload["public_release_authorized"])
            self.assertEqual(8,len(payload["checks"]))
            self.assertTrue(all(check["status"]=="PASS" for check in payload["checks"]))
            self.assertEqual("NO-GO",payload["residual_gate_status"]["G0"])
            self.assertEqual("NO-GO",payload["residual_gate_status"]["G5"])
            self.assertEqual("UNASSESSED",payload["residual_gate_status"]["G6"])
            text=report_md.read_text(encoding="utf-8")
            self.assertIn("NOT FOR SUBMISSION OR PUBLIC RELEASE",text)
            self.assertIn("Journal submission: **NO-GO**",text)
            self.assertIn("Public release: **NO-GO**",text)

if __name__=="__main__": unittest.main()
