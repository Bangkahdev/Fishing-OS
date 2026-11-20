import unittest

from fishing_agent.command import CommandRequest, CommandResult
from fishing_agent.system import SystemOperation, SystemTool, SystemToolError


class SystemToolTest(unittest.TestCase):
    def setUp(self):
        self.requests: list[CommandRequest] = []

        def execute(request: CommandRequest) -> CommandResult:
            self.requests.append(request)
            return CommandResult(0, "ok\n", "")

        self.tool = SystemTool(execute)

    def test_read_only_operations_use_argv_and_user_privilege(self):
        result = self.tool.run(SystemOperation("network", "status"))
        self.assertEqual(result.returncode, 0)
        request = self.requests[-1]
        self.assertEqual(request.command, "ip")
        self.assertEqual(request.args, ("-brief", "address"))
        self.assertEqual(request.privilege, "user")
        self.assertEqual(request.execution_mode, "argv")

    def test_package_mutation_requires_elevated_context(self):
        self.tool.run(SystemOperation("packages", "install", ("ripgrep",)))
        request = self.requests[-1]
        self.assertEqual(request.command, "pacman")
        self.assertEqual(request.args, ("-S", "--noconfirm", "ripgrep"))
        self.assertEqual(request.privilege, "elevated")

    def test_service_requires_unit(self):
        with self.assertRaises(SystemToolError):
            self.tool.run(SystemOperation("services", "status"))

    def test_unknown_operation_rejected(self):
        with self.assertRaises(SystemToolError):
            self.tool.run(SystemOperation("storage", "format", ("/dev/sdb",)))


if __name__ == "__main__":
    unittest.main()
