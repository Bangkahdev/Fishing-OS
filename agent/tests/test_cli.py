import contextlib
import hashlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fishing_agent.cli import main


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.lab = Path(self._tmp.name) / "lab"

    def tearDown(self):
        self._tmp.cleanup()

    def test_init_membuat_struktur(self):
        code, out, _err = run_cli(["init", "--lab", str(self.lab)])
        self.assertEqual(code, 0)
        self.assertIn("workspace/", out)
        for name in ("models", "runtime", "workspace", "logs"):
            self.assertTrue((self.lab / name).is_dir(), name)

    def test_run_dry_run_menulis_trace(self):
        script = Path(self._tmp.name) / "aksi.json"
        script.write_text(json.dumps([{"kind": "move", "x": 5, "y": 6}]), encoding="utf-8")
        code, out, err = run_cli(
            ["run", "--lab", str(self.lab), "--script", str(script), "--dry-run", "--pacing", "0"]
        )
        self.assertEqual(code, 0, err)
        self.assertIn("backend: dry-run", out)
        traces = list((self.lab / "logs").glob("session-*.jsonl"))
        self.assertEqual(len(traces), 1)
        rows = [json.loads(line) for line in traces[0].read_text(encoding="utf-8").splitlines()]
        self.assertEqual(rows[0]["action"], "move")
        self.assertEqual(rows[0]["parameters"], {"x": 5, "y": 6})

    def test_run_berhenti_karena_stop_file(self):
        script = Path(self._tmp.name) / "aksi.json"
        script.write_text(json.dumps([{"kind": "click"}]), encoding="utf-8")
        run_cli(["init", "--lab", str(self.lab)])
        run_cli(["stop", "--lab", str(self.lab)])
        code, _out, err = run_cli(
            ["run", "--lab", str(self.lab), "--script", str(script), "--dry-run", "--pacing", "0"]
        )
        self.assertEqual(code, 130)
        self.assertIn("dihentikan", err)

    def test_search_menemukan_berkas(self):
        run_cli(["init", "--lab", str(self.lab)])
        (self.lab / "workspace" / "materi.md").write_text("isi", encoding="utf-8")
        code, out, _err = run_cli(["search", "--lab", str(self.lab), "*.md"])
        self.assertEqual(code, 0)
        self.assertIn("materi.md", out)

    def test_model_list_load_dan_verify(self):
        content = b"model uji"
        digest = hashlib.sha256(content).hexdigest()
        manifest = Path(self._tmp.name) / "models.json"
        manifest.write_text(
            json.dumps({"models": [{"id": "m1", "version": "1", "checksum": digest}]}),
            encoding="utf-8",
        )
        run_cli(["init", "--lab", str(self.lab)])
        (self.lab / "models" / "m1-1").write_bytes(content)

        code, out, err = run_cli(
            ["model", "list", "--lab", str(self.lab), "--manifest", str(manifest)]
        )
        self.assertEqual(code, 0, err)
        self.assertIn("m1", out)

        code, out, err = run_cli(
            ["model", "load", "m1", "--lab", str(self.lab), "--manifest", str(manifest)]
        )
        self.assertEqual(code, 0, err)
        self.assertIn("loaded", out)

        code, out, _err = run_cli(
            ["model", "verify", "m1", "--lab", str(self.lab), "--manifest", str(manifest)]
        )
        self.assertEqual(code, 0)
        self.assertIn("cocok", out)

    def test_model_verify_checksum_salah(self):
        manifest = Path(self._tmp.name) / "models.json"
        manifest.write_text(
            json.dumps({"models": [{"id": "m1", "version": "1", "checksum": "salah"}]}),
            encoding="utf-8",
        )
        run_cli(["init", "--lab", str(self.lab)])
        (self.lab / "models" / "m1-1").write_bytes(b"isi")
        code, _out, _err = run_cli(
            ["model", "verify", "m1", "--lab", str(self.lab), "--manifest", str(manifest)]
        )
        self.assertEqual(code, 1)

    def test_tanpa_lab_menghasilkan_exit_1(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            code, _out, err = run_cli(["init"])
        self.assertEqual(code, 1)
        self.assertIn("FISHING_AI_LAB", err)

    def test_file_write_read_dan_delete_approval(self):
        target = self.lab / "hasil.txt"
        code, _out, err = run_cli(["file", "write", str(target), "halo"])
        self.assertEqual(code, 0, err)
        code, out, err = run_cli(["file", "read", str(target)])
        self.assertEqual(code, 0, err)
        self.assertEqual(out, "halo")
        code, _out, err = run_cli(["file", "delete", str(target)])
        self.assertEqual(code, 1)
        self.assertIn("approval", err)
        code, _out, err = run_cli(["file", "delete", str(target), "--approved"])
        self.assertEqual(code, 0, err)

    def test_productivity_pptx(self):
        target = self.lab / "presentasi.pptx"
        code, _out, err = run_cli(
            [
                "productivity",
                "pptx",
                str(target),
                "--slides",
                '[{"title":"Demo","body":"Fishing OS"}]',
            ]
        )
        self.assertEqual(code, 0, err)
        self.assertTrue(target.is_file())


if __name__ == "__main__":
    unittest.main()
