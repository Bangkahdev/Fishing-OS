import json
import tempfile
import unittest
from pathlib import Path

from fishing_agent.executor import (
    Action,
    ActionError,
    ActionExecutor,
    BackendUnavailable,
    DryRunBackend,
    load_actions,
    select_backend,
)
from fishing_agent.stop import StopController, StopRequested
from fishing_agent.trace import TraceWriter


def make_executor(tmp: Path, **kwargs) -> tuple[ActionExecutor, DryRunBackend, TraceWriter]:
    backend = DryRunBackend()
    trace = TraceWriter(tmp / "session.jsonl")
    options = {"pacing": 0.0, "sleep": lambda _s: None, **kwargs}
    return ActionExecutor(backend, trace, StopController(tmp / "stop"), **options), backend, trace


class ActionTest(unittest.TestCase):
    def test_kind_tidak_dikenal_ditolak(self):
        with self.assertRaises(ActionError):
            Action("teleport")

    def test_from_mapping_menggabungkan_field_tambahan(self):
        action = Action.from_mapping({"kind": "click", "button": "right"})
        self.assertEqual(action.params, {"button": "right"})


class ActionExecutorTest(unittest.TestCase):
    def test_dry_run_mencatat_tanpa_input_nyata(self):
        with tempfile.TemporaryDirectory() as tmp:
            executor, backend, trace = make_executor(Path(tmp))
            executed = executor.run(
                [
                    Action("move", {"x": 10, "y": 20}),
                    Action("click"),
                    Action("type", {"text": "halo"}),
                ]
            )
            trace.close()
            self.assertEqual(executed, 3)
            self.assertEqual([name for name, _ in backend.calls], ["move", "click", "type"])
            self.assertEqual(backend.calls[1], ("click", {"button": "left"}))

    def test_batas_max_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            executor, backend, trace = make_executor(Path(tmp), max_steps=2)
            executed = executor.run([Action("wait", {"seconds": 0}) for _ in range(5)])
            last = trace.write(perception="p", action="noop")
            trace.close()
            rows = [json.loads(line) for line in (Path(tmp) / "session.jsonl").read_text().splitlines()]
        self.assertEqual(executed, 2)
        self.assertEqual(len(backend.calls), 0)
        self.assertEqual(rows[-2]["action"], "stop")
        self.assertEqual(rows[-2]["status"], "stopped")
        self.assertIn("max-steps", rows[-2]["note"])
        self.assertEqual(last["step_id"], 4)

    def test_stop_file_menghentikan_sebelum_aksi_pertama(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "stop").write_text("x", encoding="utf-8")
            executor, backend, trace = make_executor(Path(tmp))
            with self.assertRaises(StopRequested):
                executor.run([Action("click")])
            trace.close()
            self.assertEqual(backend.calls, [])
            rows = [json.loads(line) for line in (Path(tmp) / "session.jsonl").read_text().splitlines()]
            self.assertEqual(rows[-1]["action"], "stop")

    def test_aksi_rusak_dicatat_sebagai_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            executor, _backend, trace = make_executor(Path(tmp))
            with self.assertRaises(KeyError):
                executor.run([Action("type", {})])
            trace.close()
            rows = [json.loads(line) for line in (Path(tmp) / "session.jsonl").read_text().splitlines()]
            self.assertEqual(rows[-1]["status"], "error")
            self.assertEqual(rows[-1]["action"], "type")

    def test_load_actions_dari_berkas(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "aksi.json"
            script.write_text(
                json.dumps({"actions": [{"kind": "key", "params": {"keys": "ctrl+s"}}]}),
                encoding="utf-8",
            )
            actions = load_actions(script)
        self.assertEqual(actions[0].kind, "key")
        self.assertEqual(actions[0].params["keys"], "ctrl+s")


class BackendSelectionTest(unittest.TestCase):
    def test_dry_run_dipilih_eksplisit(self):
        self.assertEqual(select_backend("dry-run").name, "dry-run")
        self.assertEqual(select_backend(dry_run=True).name, "dry-run")

    def test_backend_tidak_dikenal(self):
        with self.assertRaises(BackendUnavailable):
            select_backend("quantum")


if __name__ == "__main__":
    unittest.main()
