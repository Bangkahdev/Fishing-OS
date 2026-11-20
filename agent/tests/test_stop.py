import tempfile
import unittest
from pathlib import Path

from fishing_agent.stop import StopController, StopRequested


class StopControllerTest(unittest.TestCase):
    def test_berhenti_dari_stop_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            stop_file = Path(tmp) / "stop"
            controller = StopController(stop_file)
            controller.check()
            stop_file.write_text("stop\n", encoding="utf-8")
            with self.assertRaises(StopRequested) as ctx:
                controller.check()
            self.assertIn("stop", ctx.exception.reason)
            self.assertIn(str(stop_file), ctx.exception.reason)

    def test_request_stop_menghentikan_tidur_cepat(self):
        controller = StopController()
        controller.request_stop("uji")
        self.assertTrue(controller.stopped)
        with self.assertRaises(StopRequested):
            controller.sleep(5.0)

    def test_clear_menghapus_stop_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            stop_file = Path(tmp) / "stop"
            controller = StopController(stop_file)
            stop_file.write_text("x", encoding="utf-8")
            controller.clear()
            self.assertFalse(controller.stopped)
            controller.check()

    def test_sleep_menghormati_durasi(self):
        calls = []
        controller = StopController()

        class FakeTime:
            @staticmethod
            def sleep(seconds):
                calls.append(seconds)

        import fishing_agent.stop as stop_module

        original = stop_module.time.sleep
        stop_module.time.sleep = FakeTime.sleep
        try:
            controller.sleep(0.12, chunk=0.05)
        finally:
            stop_module.time.sleep = original
        self.assertAlmostEqual(sum(calls), 0.12, places=6)


if __name__ == "__main__":
    unittest.main()
