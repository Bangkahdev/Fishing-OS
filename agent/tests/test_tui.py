import io
import unittest

from fishing_agent.service import ControlService
from fishing_agent.tui import TUI


class TUITest(unittest.TestCase):
    def test_task_approve_cancel_flow(self):
        service = ControlService()
        tui = TUI(service)
        output = io.StringIO()
        code = tui.run(["task cek status", "list", "quit"], output=output)
        self.assertEqual(code, 0)
        self.assertIn("cek status", output.getvalue())

    def test_execute_task_commands(self):
        service = ControlService()
        tui = TUI(service)
        output = io.StringIO()
        task = service.create_task("cek", task_id="task-1")
        self.assertTrue(tui.execute("status task-1", output))
        self.assertIn("ready", output.getvalue())
        self.assertTrue(tui.execute("approve task-1", output))
        self.assertTrue(service.policy.is_approved("task-1"))
        self.assertTrue(tui.execute("cancel task-1", output))
        self.assertEqual(task.status.value, "cancelled")


if __name__ == "__main__":
    unittest.main()
