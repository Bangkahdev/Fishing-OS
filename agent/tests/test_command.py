import tempfile
import unittest
from pathlib import Path

from fishing_agent.command import CommandExecutor, CommandRequest, CommandValidationError, OutputPolicy
from fishing_agent.stop import StopController, StopRequested
from fishing_agent.trace import TraceWriter


class CommandContractTest(unittest.TestCase):
    def test_argv_tidak_memakai_shell_dan_mengembalikan_status(self):
        request = CommandRequest("python", ("-c", "print('halo')"))
        result = CommandExecutor().execute(request)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "halo")

    def test_shell_hanya_aktif_bila_diminta(self):
        request = CommandRequest("python -c \"print('ab', end='')\"", execution_mode="shell")
        result = CommandExecutor().execute(request)
        self.assertEqual(result.stdout, "ab")

    def test_output_dibatasi(self):
        request = CommandRequest(
            "python", ("-c", "print('x' * 1000)"), output_policy=OutputPolicy(max_bytes=20)
        )
        result = CommandExecutor().execute(request)
        self.assertTrue(result.truncated)
        self.assertLessEqual(len(result.stdout.encode()), 20)

    def test_request_invalid_ditolak(self):
        with self.assertRaises(CommandValidationError):
            CommandRequest("", execution_mode="shell")

    def test_stop_menghentikan_process_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            stop = StopController(Path(tmp) / "stop")
            stop.request_stop("uji")
            with self.assertRaises(StopRequested):
                CommandExecutor(stop).execute(CommandRequest("python", ("-c", "print('x')")))

    def test_trace_mencatat_command_tanpa_output_penuh(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.jsonl"
            with TraceWriter(path) as trace:
                result = CommandExecutor(trace=trace).execute(CommandRequest("python", ("-c", "print('ok')")))
            self.assertEqual(result.returncode, 0)
            content = path.read_text(encoding="utf-8")
            self.assertIn('"status": "started"', content)
            self.assertIn('"status": "completed"', content)
            self.assertNotIn('"stdout"', content)


if __name__ == "__main__":
    unittest.main()
