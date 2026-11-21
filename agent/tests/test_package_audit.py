import tempfile
import unittest
from pathlib import Path

from fishing_agent.package_audit import audit_report, audit_tree


class AuditTreeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_berkas_biasa_lolos(self):
        (self.root / "usr" / "bin").mkdir(parents=True)
        (self.root / "usr" / "bin" / "fsh").write_text("#!/bin/sh", encoding="utf-8")
        (self.root / "etc").mkdir()
        (self.root / "etc" / "fishing-os.conf").write_text("", encoding="utf-8")
        self.assertEqual(audit_tree(self.root), [])

    def test_launcher_assistant_ditemukan(self):
        (self.root / "usr" / "share" / "applications").mkdir(parents=True)
        (self.root / "usr" / "share" / "applications" / "fishing-assistant.desktop").write_text(
            "", encoding="utf-8"
        )
        findings = audit_tree(self.root)
        self.assertEqual(len(findings), 1)
        self.assertIn("applications", findings[0].path)

    def test_bin_assistant_ditemukan(self):
        (self.root / "usr" / "bin").mkdir(parents=True)
        (self.root / "usr" / "bin" / "fishing-assistant").write_text("", encoding="utf-8")
        findings = audit_tree(self.root)
        self.assertTrue(any("bin/fishing-assistant" in f.path for f in findings))

    def test_systemd_unit_assistant_ditemukan(self):
        (self.root / "usr" / "lib" / "systemd" / "user").mkdir(parents=True)
        (self.root / "usr" / "lib" / "systemd" / "user" / "fishing-assistant.service").write_text(
            "", encoding="utf-8"
        )
        findings = audit_tree(self.root)
        self.assertTrue(any("systemd" in f.path for f in findings))

    def test_model_asset_ditemukan(self):
        (self.root / "usr" / "share" / "models").mkdir(parents=True)
        (self.root / "usr" / "share" / "models" / "assistant").mkdir()
        findings = audit_tree(self.root)
        self.assertTrue(any("models/assistant" in f.path for f in findings))

    def test_root_bukan_direktori(self):
        with self.assertRaises(FileNotFoundError):
            audit_tree(self.root / "tidak-ada")


class AuditReportTest(unittest.TestCase):
    def test_lulus(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = audit_report(tmp)
        self.assertIn("LULUS", report)
        self.assertIn("0", report)

    def test_gagal(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "usr", "bin").mkdir(parents=True)
            Path(tmp, "usr", "bin", "fishing-assistant").write_text("", encoding="utf-8")
            report = audit_report(tmp)
        self.assertIn("GAGAL", report)
        self.assertIn("fishing-assistant", report)


if __name__ == "__main__":
    unittest.main()
