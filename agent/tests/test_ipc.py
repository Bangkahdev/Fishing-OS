import tempfile
import threading
import time
import unittest
from pathlib import Path

from fishing_agent.ipc import ControlIPCClient, ControlIPCServer
from fishing_agent.service import ControlService


class IPCTest(unittest.TestCase):
    def test_create_get_and_cancel_task(self):
        if not hasattr(__import__("socket"), "AF_UNIX"):
            self.skipTest("Unix socket tidak tersedia")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "control.sock"
            server = ControlIPCServer(path, ControlService())
            thread = threading.Thread(target=server.serve_once)
            thread.start()
            for _ in range(50):
                if path.exists():
                    break
                time.sleep(0.01)
            client = ControlIPCClient(path)
            created = client.request("create_task", {"task_id": "ipc-1", "instruction": "cek sistem"})
            self.assertTrue(created["ok"])
            self.assertEqual(created["state"], "ready")
            server.stop()
            thread.join(timeout=2)

