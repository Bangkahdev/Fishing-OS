"""Guard integrasi OS: artefak paket Assistant valid dan Live ISO tetap bersih.

Memastikan (SRS §2.2/§9.5, AC-01, NFR-02):
* artefak di packaging/assistant ada dan berstruktur benar, dan
* profil Live ISO (profile/airootfs) tidak membawa komponen Assistant apa pun.
"""

import unittest
from pathlib import Path

from fishing_agent.package_audit import audit_tree

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGING = REPO_ROOT / "packaging" / "assistant"
AIROOTFS = REPO_ROOT / "profile" / "airootfs"


class PackagingArtifactsTest(unittest.TestCase):
    def test_launcher_valid(self):
        launcher = PACKAGING / "fishing-assistant"
        self.assertTrue(launcher.is_file(), "launcher tidak ditemukan")
        text = launcher.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("#!/usr/bin/env bash"))
        self.assertIn("fishing_agent", text)
        self.assertNotIn("\r", text)

    def test_desktop_entry_valid(self):
        desktop = PACKAGING / "fishing-assistant.desktop"
        self.assertTrue(desktop.is_file(), "entri desktop tidak ditemukan")
        text = desktop.read_text(encoding="utf-8")
        self.assertIn("[Desktop Entry]", text)
        self.assertIn("Type=Application", text)
        self.assertIn("Exec=/usr/bin/fishing-assistant", text)
        self.assertNotIn("\r", text)

    def test_service_unit_valid(self):
        unit = PACKAGING / "fishing-assistant.service"
        self.assertTrue(unit.is_file(), "unit service tidak ditemukan")
        text = unit.read_text(encoding="utf-8")
        self.assertIn("[Unit]", text)
        self.assertIn("[Service]", text)
        self.assertIn("[Install]", text)
        self.assertIn("ipc-server", text)
        # Service tidak boleh berjalan sebagai root.
        self.assertNotIn("User=root", text)

    def test_pkgbuild_and_installer_present(self):
        self.assertTrue((PACKAGING / "PKGBUILD").is_file())
        self.assertIn("pkgname=fishing-assistant", (PACKAGING / "PKGBUILD").read_text(encoding="utf-8"))
        installer = PACKAGING / "install.sh"
        self.assertTrue(installer.is_file())
        self.assertTrue(installer.read_text(encoding="utf-8").startswith("#!/usr/bin/env bash"))


class LiveIsoGuardTest(unittest.TestCase):
    def test_profil_live_iso_tanpa_komponen_assistant(self):
        if not AIROOTFS.is_dir():  # pragma: no cover - profil selalu ada di repo
            self.skipTest("profile/airootfs tidak ditemukan")
        findings = audit_tree(AIROOTFS)
        self.assertEqual(findings, [], f"Live ISO membawa komponen Assistant: {findings}")


if __name__ == "__main__":
    unittest.main()