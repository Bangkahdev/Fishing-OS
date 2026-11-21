import unittest

from fishing_agent.gui_adapter import GUIAdapter
from fishing_agent.service import ControlService


class GUIAdapterTest(unittest.TestCase):
    def test_selected_task_uses_shared_service(self):
        service = ControlService()
        gui = GUIAdapter(service)
        task = gui.create_task("buka aplikasi")
        self.assertEqual(gui.status(), "ready")
        self.assertTrue(gui.approve_selected())
        self.assertTrue(service.policy.is_approved(task.task_id))
        self.assertTrue(gui.cancel_selected())
        self.assertEqual(gui.status(), "cancelled")

    def test_no_selected_task(self):
        gui = GUIAdapter(ControlService())
        self.assertFalse(gui.approve_selected())
        self.assertFalse(gui.cancel_selected())
        self.assertEqual(gui.status(), "ready")


if __name__ == "__main__":
    unittest.main()
