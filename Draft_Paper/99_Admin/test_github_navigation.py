#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import github_navigation as nav
import verify_internal_manuscript_package as verifier

ROOT = Path(__file__).resolve().parents[2]
DRAFT = ROOT / "Draft_Paper"


class GitHubNavigationTests(unittest.TestCase):
    def test_linkifier_uses_relative_url_encoded_targets_and_line_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            source = repo / "Draft_Paper" / "notes" / "review.md"
            target = repo / "Draft_Paper" / "data" / "file with spaces.csv"
            source.parent.mkdir(parents=True)
            target.parent.mkdir(parents=True)
            target.write_text("a\nb\nc\n", encoding="utf-8")
            source.write_text(
                "See `Draft_Paper/data/file with spaces.csv:2-3`.\n",
                encoding="utf-8",
            )

            result = nav.linkify_markdown_text(
                source.read_text(encoding="utf-8"), source, repo, set()
            )

            self.assertIn(
                "[`Draft_Paper/data/file with spaces.csv:2-3`](../data/file%20with%20spaces.csv#L2-L3)",
                result.text,
            )
            self.assertEqual(1, result.linked)
            self.assertEqual([], result.unresolved)

    def test_link_checker_rejects_out_of_range_line_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            draft = repo / "Draft_Paper"
            draft.mkdir()
            (draft / "target.md").write_text("one\ntwo\n", encoding="utf-8")
            (draft / "source.md").write_text("[bad](target.md#L3)\n", encoding="utf-8")
            broken = nav.check_markdown_links(draft, repo)
            self.assertEqual(1, len(broken))
            self.assertEqual("line_anchor_out_of_range:2", broken[0]["reason"])

    def test_source_custody_verification_allows_clean_checkout_without_local_docx(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            missing = Path(td) / "source.docx"
            verifier.check_source_custody(
                {"source_docx_sha256": verifier.SOURCE_DOCX_SHA256}, missing
            )
            with self.assertRaises(AssertionError):
                verifier.check_source_custody({"source_docx_sha256": "0" * 64}, missing)

    def test_current_navigation_is_complete_and_all_markdown_links_resolve(self) -> None:
        readme = DRAFT / "README.md"
        index = DRAFT / "GITHUB_FILE_INDEX.md"
        audit_path = DRAFT / "GITHUB_LINK_AUDIT.json"
        self.assertTrue(readme.is_file())
        self.assertTrue(index.is_file())
        self.assertTrue(audit_path.is_file())

        readme_text = readme.read_text(encoding="utf-8")
        for required in [
            "05_Submission_Package/NSS-ID_INTERNAL_NOT_FOR_SUBMISSION.docx",
            "04_Revised_Draft/06_DATA_IN_BRIEF_TEMPLATE_MANUSCRIPT.md",
            "01_Extraction/template_aligned_internal/rendered_preview.pdf",
            "02_Evidence/AUTHOR_METHODS_EVIDENCE_QUESTIONNAIRE.md",
            "03_Review/16_FINAL_DATA_IN_BRIEF_TEMPLATE_REVIEW.md",
            "GITHUB_FILE_INDEX.md",
        ]:
            self.assertIn(required, readme_text)

        expected = {
            path.relative_to(DRAFT).as_posix()
            for path in nav.publishable_files(DRAFT)
            if path.name != "GITHUB_FILE_INDEX.md"
        }
        indexed = set(nav.indexed_targets(index))
        self.assertEqual(expected, indexed)
        self.assertFalse(any("__pycache__" in path or "/.cache/" in f"/{path}" for path in indexed))
        self.assertTrue(nav.SENSITIVE_DRAFT_PATHS.isdisjoint(indexed))
        self.assertTrue(all((DRAFT / path).stat().st_size < 100 * 1024 * 1024 for path in indexed))

        broken = nav.check_markdown_links(DRAFT, ROOT)
        self.assertEqual([], broken)
        self.assertEqual([], nav.find_resolvable_unlinked_references(DRAFT, ROOT))

        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        self.assertEqual("github_navigation_audit_v1", audit["schema"])
        self.assertEqual(0, audit["broken_link_count"])
        self.assertGreater(audit["linked_reference_count"], 0)

    def test_inventories_use_portable_paths_and_source_privacy_exclusions_are_documented(self) -> None:
        inventories = [
            DRAFT / "01_Extraction" / "document_inventory.json",
            DRAFT / "01_Extraction" / "extraction_stdout.json",
            DRAFT / "01_Extraction" / "official_data_in_brief_template" / "document_inventory.json",
            DRAFT / "01_Extraction" / "template_aligned_internal" / "document_inventory.json",
        ]
        for path in inventories:
            source_path = json.loads(path.read_text(encoding="utf-8"))["source_path"]
            self.assertFalse(Path(source_path).is_absolute(), path)
            self.assertFalse(source_path.startswith(("/mnt/", "/home/")), path)

        custody = (DRAFT / "00_Source" / "README.md").read_text(encoding="utf-8")
        self.assertIn("17214b820dc3b70277541eeba1ca070de1cd2bd538e11ac66896c5957092bd0c", custody)
        self.assertIn("not stored on GitHub", custody)

    def test_package_readme_uses_clickable_relative_links(self) -> None:
        text = (DRAFT / "05_Submission_Package" / "README_INTERNAL_NOT_FOR_SUBMISSION.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "[`NSS-ID_INTERNAL_NOT_FOR_SUBMISSION.docx`](NSS-ID_INTERNAL_NOT_FOR_SUBMISSION.docx)",
            text,
        )
        self.assertIn("[`tables/`](tables/)", text)
        self.assertIn("[`evidence/`](evidence/)", text)


if __name__ == "__main__":
    unittest.main()
