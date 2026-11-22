import unittest

from fishing_agent.planner import (
    HeuristicPlanner,
    Plan,
    PlanStep,
    PlannerError,
    get_planner,
    plan_from_json,
)
from fishing_agent.registry import ToolContext


def _context() -> ToolContext:
    return ToolContext(policy=object(), administrator=object(), stop=object())


class PlanSchemaTest(unittest.TestCase):
    def test_roundtrip_json(self):
        plan = Plan(steps=[PlanStep("file.read", {"path": "/etc/hostname"})], summary="baca")
        restored = plan_from_json(plan.to_dict())
        self.assertEqual(restored.steps[0].tool, "file.read")
        self.assertEqual(restored.steps[0].arguments["path"], "/etc/hostname")

    def test_plan_dari_list(self):
        plan = Plan.from_mapping([{"tool": "file.list", "arguments": {"path": "."}}])
        self.assertEqual(len(plan.steps), 1)

    def test_plan_invalid(self):
        with self.assertRaises(PlannerError):
            PlanStep("", {})
        with self.assertRaises(PlannerError):
            Plan.from_mapping({"steps": [{"arguments": {}}]})  # tanpa tool
        with self.assertRaises(PlannerError):
            Plan.from_mapping({"steps": "bukan daftar"})


class HeuristicPlannerTest(unittest.TestCase):
    def setUp(self):
        self.planner = HeuristicPlanner()

    def _tools(self, instruction):
        return [step.tool for step in self.planner.plan(instruction, _context()).steps]

    def test_presentasi(self):
        plan = self.planner.plan("buat presentasi tentang Fishing OS", _context())
        self.assertEqual(plan.steps[0].tool, "productivity.pptx")
        self.assertTrue(plan.steps[0].arguments["path"].endswith(".pptx"))

    def test_csv(self):
        plan = self.planner.plan("buat csv penjualan", _context())
        self.assertEqual(plan.steps[0].tool, "productivity.csv")
        self.assertTrue(plan.steps[0].arguments["path"].endswith(".csv"))

    def test_dokumen_markdown(self):
        plan = self.planner.plan("buat dokumen laporan akhir", _context())
        self.assertEqual(plan.steps[0].tool, "productivity.markdown")
        self.assertTrue(plan.steps[0].arguments["path"].endswith(".md"))

    def test_read_path_tanpa_ekstensi(self):
        plan = self.planner.plan("baca file /etc/hostname", _context())
        self.assertEqual(plan.steps[0].tool, "file.read")
        self.assertEqual(plan.steps[0].arguments["path"], "/etc/hostname")

    def test_read_path_md_tidak_salah_sebagai_dokumen(self):
        plan = self.planner.plan("baca file catatan.md", _context())
        self.assertEqual(plan.steps[0].tool, "file.read")

    def test_write_file(self):
        plan = self.planner.plan("tulis file catatan.md isi halo dunia", _context())
        self.assertEqual(plan.steps[0].tool, "file.write")
        self.assertEqual(plan.steps[0].arguments["content"], "halo dunia")

    def test_search(self):
        plan = self.planner.plan('cari file "*.py"', _context())
        self.assertEqual(plan.steps[0].tool, "file.search")
        self.assertEqual(plan.steps[0].arguments["pattern"], "*.py")

    def test_list(self):
        plan = self.planner.plan("daftar isi folder /etc", _context())
        self.assertEqual(plan.steps[0].tool, "file.list")
        self.assertEqual(plan.steps[0].arguments["path"], "/etc")

    def test_system_status(self):
        plan = self.planner.plan("status paket terpasang", _context())
        self.assertEqual(plan.steps[0].tool, "system.inspect")
        self.assertEqual(plan.steps[0].arguments["category"], "packages")
        self.assertEqual(plan.steps[0].arguments["operation"], "list")

    def test_system_jaringan(self):
        plan = self.planner.plan("info jaringan", _context())
        self.assertEqual(plan.steps[0].arguments["category"], "network")

    def test_command(self):
        plan = self.planner.plan("jalankan git status", _context())
        self.assertEqual(plan.steps[0].tool, "command.run")
        self.assertEqual(plan.steps[0].arguments["command"], "git")
        self.assertEqual(list(plan.steps[0].arguments["args"]), ["status"])

    def test_unknown_needs_input(self):
        plan = self.planner.plan("halo dunia", _context())
        self.assertTrue(plan.needs_input)
        self.assertEqual(plan.steps, [])

    def test_empty_needs_input(self):
        plan = self.planner.plan("   ", _context())
        self.assertTrue(plan.needs_input)


class PlannerFactoryTest(unittest.TestCase):
    def test_default_heuristic(self):
        self.assertIsInstance(get_planner(), HeuristicPlanner)
        self.assertIsInstance(get_planner("auto"), HeuristicPlanner)

    def test_unknown_planner(self):
        with self.assertRaises(PlannerError):
            get_planner("tidak-ada")


if __name__ == "__main__":
    unittest.main()