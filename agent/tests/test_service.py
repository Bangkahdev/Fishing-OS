import unittest

from fishing_agent.service import ControlService, ServiceError
from fishing_agent.task import TaskState


class ControlServiceTest(unittest.TestCase):
    def test_task_state_shared_and_cancelled(self):
        service = ControlService()
        task = service.create_task("periksa status sistem", source="gui", task_id="task-1")
        self.assertEqual(task.status, TaskState.READY)
        service.transition("task-1", TaskState.PLANNING)
        service.cancel("task-1", "user stop")
        self.assertEqual(service.get_task("task-1").status, TaskState.CANCELLED)
        self.assertTrue(service.get_task("task-1").stop.stopped)

    def test_approval_disimpan_di_policy_bersama(self):
        service = ControlService()
        service.create_task("hapus output", task_id="task-2")
        service.approve("task-2")
        self.assertTrue(service.policy.is_approved("task-2"))

    def test_duplicate_and_unknown_task_ditolak(self):
        service = ControlService()
        service.create_task("uji", task_id="task-3")
        with self.assertRaises(ServiceError):
            service.create_task("duplikat", task_id="task-3")
        with self.assertRaises(ServiceError):
            service.get_task("missing")


if __name__ == "__main__":
    unittest.main()
