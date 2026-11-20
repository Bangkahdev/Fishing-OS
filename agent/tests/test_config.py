import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fishing_agent.config import LAB_ENV, LabError, LabPaths


class LabPathsTest(unittest.TestCase):
    def test_override_membuat_empat_subdirektori(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "lab"
            lab = LabPaths.from_env(root).ensure()
            self.assertEqual(lab.root, root.resolve())
            for name in ("models", "runtime", "workspace", "logs"):
                self.assertTrue((root / name).is_dir(), name)

    def test_env_dipakai_bila_tanpa_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {LAB_ENV: tmp}):
                lab = LabPaths.from_env()
            self.assertEqual(lab.root, Path(tmp).resolve())

    def test_tanpa_variabel_menghasilkan_galat_jelas(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(LabError) as ctx:
                LabPaths.from_env()
        self.assertIn(LAB_ENV, str(ctx.exception))

    def test_stop_file_berada_di_logs(self):
        lab = LabPaths.from_env(Path(tempfile.gettempdir()) / "fishing-agent-test-lab")
        self.assertEqual(lab.stop_file, lab.logs / "stop")


if __name__ == "__main__":
    unittest.main()
