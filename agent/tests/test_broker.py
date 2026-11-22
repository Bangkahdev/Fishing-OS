import os
import socket
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

from fishing_agent.broker import (
    BrokerClient,
    BrokerDenied,
    BrokerError,
    BrokerIPCServer,
    PrivilegeBroker,
    PrivilegedRequest,
)
from fishing_agent.policy import AdministratorMode, PolicyGate


class _FakeExecutor:
    def __init__(self, returncode=0, stdout="ok", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return SimpleNamespace(
            returncode=self.returncode,
            stdout=self.stdout,
            stderr=self.stderr,
            timed_out=False,
            truncated=False,
            cancelled=False,
        )


def _admin() -> AdministratorMode:
    administrator = AdministratorMode()
    administrator.enable(60)
    return administrator


class PrivilegedRequestTest(unittest.TestCase):
    def test_payload_valid(self):
        request = PrivilegedRequest.from_mapping(
            {"command": "id", "args": ["-u"], "timeout": 5, "reason": "uji"}
        )
        self.assertEqual(request.args, ("-u",))
        self.assertEqual(request.to_command_request().privilege, "elevated")

    def test_payload_menolak_kunci_asing_dan_nul(self):
        with self.assertRaises(BrokerError):
            PrivilegedRequest.from_mapping({"command": "id", "shell": True})
        with self.assertRaises(BrokerError):
            PrivilegedRequest.from_mapping({"command": "id\x00"})
        with self.assertRaises(BrokerError):
            PrivilegedRequest.from_mapping({"command": "id", "args": "bukan-list"})
        with self.assertRaises(BrokerError):
            PrivilegedRequest.from_mapping({"command": "id", "timeout": 0})


class PrivilegeBrokerTest(unittest.TestCase):
    def test_denied_tanpa_administrator_mode(self):
        executor = _FakeExecutor()
        broker = PrivilegeBroker(executor=executor, sudo_check=lambda: True)
        with self.assertRaises(BrokerDenied):
            broker.execute(PrivilegedRequest(command="id"))
        self.assertEqual(executor.requests, [])

    def test_denied_tanpa_sudo_native(self):
        broker = PrivilegeBroker(administrator=_admin(), executor=_FakeExecutor(), sudo_check=lambda: False)
        with self.assertRaises(BrokerDenied):
            broker.execute(PrivilegedRequest(command="id"))

    def test_eksekusi_elevated_dan_audit(self):
        executor = _FakeExecutor(stdout="0\n")
        with tempfile.TemporaryDirectory() as tmp:
            trace_path = Path(tmp) / "broker.jsonl"
            from fishing_agent.trace import TraceWriter

            with TraceWriter(trace_path) as trace:
                broker = PrivilegeBroker(
                    administrator=_admin(), executor=executor, trace=trace, sudo_check=lambda: True
                )
                result = broker.execute(PrivilegedRequest(command="id", args=("-u",)))
            rows = trace_path.read_text(encoding="utf-8").splitlines()
        self.assertTrue(result.ok)
        self.assertEqual(executor.requests[0].privilege, "elevated")
        self.assertTrue(any('"action": "completed"' in row or '"action":"completed"' in row for row in rows))

    def test_high_risk_butuh_approval(self):
        broker = PrivilegeBroker(
            administrator=_admin(),
            executor=_FakeExecutor(),
            policy=PolicyGate(),
            sudo_check=lambda: True,
        )
        with self.assertRaises(BrokerDenied):
            broker.execute(PrivilegedRequest(command="mkfs.ext4", args=("/dev/sdz",)))
        result = broker.execute(PrivilegedRequest(command="mkfs.ext4", args=("/dev/sdz",)), approved=True)
        self.assertTrue(result.ok)

    def test_handle_mengembalikan_error_json(self):
        broker = PrivilegeBroker(executor=_FakeExecutor(), sudo_check=lambda: True)
        response = broker.handle({"request": {"command": "id"}})
        self.assertFalse(response["ok"])
        self.assertIn("Administrator Mode", response["error"])


@unittest.skipUnless(hasattr(socket, "AF_UNIX"), "AF_UNIX tidak tersedia")
class BrokerIPCTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.socket_path = Path(self._tmp.name) / "broker.sock"
        self.executor = _FakeExecutor()
        self.server = BrokerIPCServer(
            self.socket_path,
            PrivilegeBroker(administrator=_admin(), executor=self.executor, sudo_check=lambda: True),
        )
        self.server.start()
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        for _ in range(50):
            if self.socket_path.exists():
                break
            time.sleep(0.01)

    def tearDown(self):
        self.server.close()
        self.thread.join(timeout=2)
        self._tmp.cleanup()

    def test_roundtrip_client_server(self):
        client = BrokerClient(self.socket_path)
        result = client.execute(PrivilegedRequest(command="id", args=("-u",)))
        self.assertTrue(result.ok)
        self.assertEqual(result.stdout, "ok")
        self.assertEqual(len(self.executor.requests), 1)

    def test_menolak_uid_berbeda(self):
        server = BrokerIPCServer(
            Path(self._tmp.name) / "other.sock",
            PrivilegeBroker(administrator=_admin(), executor=self.executor, sudo_check=lambda: True),
            peer_uid=lambda connection: os.getuid() + 1,
        )
        server.start()
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = BrokerClient(Path(self._tmp.name) / "other.sock")
            with self.assertRaises(BrokerError):
                client.execute(PrivilegedRequest(command="id"))
        finally:
            server.close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
