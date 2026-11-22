import os
import tempfile
import unittest
from pathlib import Path

from fishing_agent.broker import BrokerResult
from fishing_agent.config import LabPaths
from fishing_agent.orchestrator import Orchestrator
from fishing_agent.planner import HeuristicPlanner, Plan, PlanStep
from fishing_agent.policy import AdministratorMode
from fishing_agent.registry import ToolRegistry
from fishing_agent.task import TaskState
from fishing_agent.tools import register_default_tools


class _FixedPlanner:
    name = "fixed"

    def __init__(self, plan):
        self._plan = plan

    def plan(self, instruction, context):
        return self._plan


class _FakeBroker:
    def __init__(self):
        self.requests = []

    def execute(self, request, *, approved=False):
        self.requests.append((request, approved))
        return BrokerResult(ok=True, returncode=0, stdout="0\n", summary="exit=0")


class OrchestratorTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.lab = LabPaths(self.root / "lab").ensure()
        self.registry = ToolRegistry()
        register_default_tools(self.registry)
        self._cwd = os.getcwd()
        os.chdir(self.root)  # agar path relatif planner/tool konsisten

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def _orch(self, planner=None, approved=False, dry_run=False, administrator=None, broker=None):
        return Orchestrator(
            self.registry,
            planner or HeuristicPlanner(),
            lab=self.lab,
            administrator=administrator or AdministratorMode(),
            broker=broker,
            dry_run=dry_run,
        )

    def _plan(self, *steps, summary="uji"):
        return Plan(steps=[PlanStep(tool, args) for tool, args in steps], summary=summary)

    # -- alur sukses ---------------------------------------------------------

    def test_document_markdown_completed(self):
        report = self._orch().run("buat dokumen laporan", task_id="t-md")
        self.assertEqual(report.status, TaskState.COMPLETED)
        produced = list(self.root.glob("*.md"))
        self.assertTrue(produced)

    def test_command_argv_completed(self):
        plan = self._plan(("command.run", {"command": "python", "args": ["-c", "print(1)"]}))
        report = self._orch(_FixedPlanner(plan)).run("uji", task_id="t-cmd")
        self.assertEqual(report.status, TaskState.COMPLETED)
        self.assertTrue(report.steps[0].ok)

    def test_dry_run_valid_tanpa_eksekusi(self):
        plan = self._plan(("file.write", {"path": "dry.txt", "content": "x"}))
        report = self._orch(_FixedPlanner(plan), dry_run=True).run("uji", task_id="t-dry")
        self.assertTrue(report.validated)
        self.assertFalse((self.root / "dry.txt").exists())

    # -- approval / authentication ------------------------------------------

    def test_overwrite_menunggu_approval(self):
        (self.root / "ada.txt").write_text("lama", encoding="utf-8")
        plan = self._plan(("file.write", {"path": "ada.txt", "content": "baru"}))
        report = self._orch(_FixedPlanner(plan)).run("uji", task_id="t-ov")
        self.assertEqual(report.status, TaskState.WAITING_FOR_APPROVAL)
        self.assertEqual((self.root / "ada.txt").read_text(encoding="utf-8"), "lama")

    def test_overwrite_dengan_approval_completed(self):
        (self.root / "ada.txt").write_text("lama", encoding="utf-8")
        plan = self._plan(("file.write", {"path": "ada.txt", "content": "baru"}))
        report = self._orch(_FixedPlanner(plan)).run("uji", task_id="t-ov2", approved=True)
        self.assertEqual(report.status, TaskState.COMPLETED)
        self.assertEqual((self.root / "ada.txt").read_text(encoding="utf-8"), "baru")

    def test_delete_berisiko_tinggi_menunggu_approval(self):
        target = self.root / "hapus.txt"
        target.write_text("x", encoding="utf-8")
        plan = self._plan(("file.delete", {"path": "hapus.txt"}))
        report = self._orch(_FixedPlanner(plan)).run("uji", task_id="t-del")
        self.assertEqual(report.status, TaskState.WAITING_FOR_APPROVAL)
        self.assertTrue(target.exists())

    def test_elevated_tanpa_admin_menunggu_autentikasi(self):
        plan = self._plan(("command.run", {"command": "id", "privilege": "elevated"}))
        report = self._orch(_FixedPlanner(plan)).run("uji", task_id="t-auth")
        self.assertEqual(report.status, TaskState.WAITING_FOR_AUTHENTICATION)

    def test_elevated_tanpa_broker_tetap_menunggu_autentikasi(self):
        administrator = AdministratorMode()
        administrator.enable(60)
        plan = self._plan(("command.run", {"command": "id", "privilege": "elevated"}))
        report = self._orch(_FixedPlanner(plan), administrator=administrator).run("uji", task_id="t-nobroker")
        self.assertEqual(report.status, TaskState.WAITING_FOR_AUTHENTICATION)
        self.assertIn("Privilege Broker", report.summary)

    def test_elevated_lewat_broker_completed(self):
        administrator = AdministratorMode()
        administrator.enable(60)
        broker = _FakeBroker()
        plan = self._plan(("command.run", {"command": "id", "args": ["-u"], "privilege": "elevated"}))
        report = self._orch(_FixedPlanner(plan), administrator=administrator, broker=broker).run(
            "uji", task_id="t-broker"
        )
        self.assertEqual(report.status, TaskState.COMPLETED)
        self.assertEqual(len(broker.requests), 1)
        self.assertEqual(broker.requests[0][0].command, "id")

    # -- kegagalan / pembatalan ---------------------------------------------

    def test_tool_tidak_dikenal_failed(self):
        plan = self._plan(("tool.halusinasi", {}))
        report = self._orch(_FixedPlanner(plan)).run("uji", task_id="t-bad")
        self.assertEqual(report.status, TaskState.FAILED)

    def test_argumen_tidak_valid_failed(self):
        plan = self._plan(("file.read", {}))  # path wajib
        report = self._orch(_FixedPlanner(plan)).run("uji", task_id="t-arg")
        self.assertEqual(report.status, TaskState.FAILED)

    def test_stop_file_membatalkan(self):
        self.lab.stop_file.write_text("stop", encoding="utf-8")
        plan = self._plan(("file.list", {"path": "."}))
        report = self._orch(_FixedPlanner(plan)).run("uji", task_id="t-stop")
        self.assertEqual(report.status, TaskState.CANCELLED)

    def test_needs_input_tidak_eksekusi(self):
        report = self._orch().run("halo dunia", task_id="t-none")
        self.assertEqual(report.status, TaskState.READY)
        self.assertTrue(report.needs_input)
        self.assertTrue(report.clarify)


if __name__ == "__main__":
    unittest.main()