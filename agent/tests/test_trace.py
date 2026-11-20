import json
import tempfile
import unittest
from pathlib import Path

from fishing_agent.trace import TraceWriter


class TraceWriterTest(unittest.TestCase):
    def test_credential_diredaksi(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.jsonl"
            with TraceWriter(path) as trace:
                trace.write(perception="p", action="auth", parameters={"token": "rahasia"})
            self.assertNotIn("rahasia", path.read_text(encoding="utf-8"))
            self.assertIn("[REDACTED]", path.read_text(encoding="utf-8"))

    def test_field_wajib_dan_urutan_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "logs" / "session.jsonl"
            with TraceWriter(path) as trace:
                trace.write(perception="layar", action="move", parameters={"x": 1})
                trace.write(perception="layar", action="key", parameters={"keys": "ctrl+b"})
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([row["step_id"] for row in rows], [1, 2])
        for row in rows:
            for field in ("step_id", "timestamp", "perception", "action", "parameters", "status", "note"):
                self.assertIn(field, row)
            self.assertTrue(row["timestamp"].endswith("Z"))
            self.assertEqual(row["status"], "ok")

    def test_tulisan_setelah_close_ditolak(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = TraceWriter(Path(tmp) / "session.jsonl")
            trace.write(perception="p", action="wait")
            trace.close()
            with self.assertRaises(RuntimeError):
                trace.write(perception="p", action="wait")

    def test_parameter_tidak_berbagi_referensi(self):
        with tempfile.TemporaryDirectory() as tmp:
            params = {"text": "halo"}
            with TraceWriter(Path(tmp) / "session.jsonl") as trace:
                record = trace.write(perception="p", action="type", parameters=params)
            params["text"] = "berubah"
            self.assertEqual(record["parameters"]["text"], "halo")


if __name__ == "__main__":
    unittest.main()
