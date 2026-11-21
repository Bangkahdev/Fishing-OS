import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fishing_agent.screenshot import ScreenshotCapture, ScreenshotError, ScreenshotUnavailable


class ScreenshotCaptureTest(unittest.TestCase):
    def test_tidak_tersedia_saat_tanpa_alat(self):
        with mock.patch("shutil.which", return_value=None):
            capture = ScreenshotCapture()
            self.assertFalse(capture.available)
            self.assertIsNone(capture.method)
            with self.assertRaises(ScreenshotUnavailable):
                capture.capture()

    def test_metode_grim_dipilih(self):
        def fake_which(tool):
            return "/usr/bin/grim" if tool == "grim" else None

        with mock.patch("shutil.which", side_effect=fake_which):
            capture = ScreenshotCapture()
            self.assertEqual(capture.method, "grim")
            self.assertTrue(capture.available)

    def test_capture_menulis_berkas(self):
        commands = []

        def fake_run(command, **kwargs):
            commands.append(list(command))
            Path(command[-1]).write_bytes(b"PNG")

        with mock.patch("shutil.which", return_value="/usr/bin/grim"), mock.patch(
            "subprocess.run", side_effect=fake_run
        ):
            capture = ScreenshotCapture()
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "layar.png"
                result = capture.capture(target)
                self.assertEqual(result, target)
                self.assertTrue(target.is_file())
                self.assertEqual(commands[0][0], "grim")

    def test_capture_gagal_saat_berkas_kosong(self):
        with mock.patch("shutil.which", return_value="/usr/bin/grim"), mock.patch(
            "subprocess.run"
        ):
            capture = ScreenshotCapture()
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "layar.png"
                with self.assertRaises(ScreenshotError):
                    capture.capture(target)


if __name__ == "__main__":
    unittest.main()
