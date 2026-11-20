import unittest

from fishing_agent.command import CommandRequest
from fishing_agent.policy import AdministratorMode, ApprovalRequired, PolicyGate
from fishing_agent.task import InvalidTransition, TaskState, TaskStateMachine


class PolicyTest(unittest.TestCase):
    def test_high_risk_memerlukan_approval(self):
        gate = PolicyGate()
        request = CommandRequest("mkfs.ext4", ("/dev/sdb",))
        with self.assertRaises(ApprovalRequired):
            gate.authorize("task", request)
        gate.approve("task")
        gate.authorize("task", request)

    def test_elevated_memerlukan_administrator_mode(self):
        gate = PolicyGate()
        request = CommandRequest("id", privilege="elevated")
        with self.assertRaises(PermissionError):
            gate.authorize("task", request)
        gate.administrator.enable(1)
        gate.authorize("task", request)
        gate.administrator.revoke()
        with self.assertRaises(PermissionError):
            gate.authorize("task", request)


class TaskStateTest(unittest.TestCase):
    def test_lifecycle_dan_terminal_state(self):
        machine = TaskStateMachine()
        for state in (
            TaskState.STARTING,
            TaskState.READY,
            TaskState.PLANNING,
            TaskState.EXECUTING,
            TaskState.VERIFYING,
            TaskState.COMPLETED,
        ):
            machine.transition(state)
        with self.assertRaises(InvalidTransition):
            machine.transition(TaskState.EXECUTING)


if __name__ == "__main__":
    unittest.main()
