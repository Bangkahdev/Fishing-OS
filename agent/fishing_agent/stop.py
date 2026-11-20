"""Penghentian bersih: sinyal, pkill, dan stop file (FR-AI-02 / NFR-AI-03)."""

from __future__ import annotations

import signal
import threading
import time
from pathlib import Path


class StopRequested(RuntimeError):
    """Diminta berhenti; loop tidak boleh menjalankan aksi berikutnya."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class StopController:
    """Status berhenti dari sinyal, stop file, atau permintaan manual."""

    def __init__(self, stop_file: str | Path | None = None) -> None:
        self.stop_file = Path(stop_file) if stop_file is not None else None
        self._event = threading.Event()
        self._reason = ""
        self._previous: dict[int, object] = {}

    def install_handlers(self) -> None:
        for signum in (signal.SIGINT, signal.SIGTERM):
            self._previous[signum] = signal.getsignal(signum)
            signal.signal(signum, self._handle)

    def restore_handlers(self) -> None:
        for signum, handler in self._previous.items():
            signal.signal(signum, handler)
        self._previous.clear()

    def _handle(self, signum: int, _frame: object) -> None:
        self.request_stop(f"sinyal {signal.Signals(signum).name}")

    def request_stop(self, reason: str = "manual") -> None:
        if not self._event.is_set():
            self._reason = reason
        self._event.set()

    @property
    def stopped(self) -> bool:
        return self._event.is_set() or self.stop_file_seen

    @property
    def reason(self) -> str:
        if self._event.is_set():
            return self._reason
        if self.stop_file_seen:
            return f"stop file {self.stop_file}"
        return ""

    @property
    def stop_file_seen(self) -> bool:
        return self.stop_file is not None and self.stop_file.exists()

    def check(self) -> None:
        if self.stopped:
            raise StopRequested(self.reason)

    def clear(self) -> None:
        self._event.clear()
        self._reason = ""
        if self.stop_file is not None and self.stop_file.exists():
            self.stop_file.unlink()

    def sleep(self, seconds: float, chunk: float = 0.05) -> None:
        """Tidur dalam potongan kecil agar penghentian terasa instan."""
        remaining = max(0.0, float(seconds))
        while remaining > 0:
            self.check()
            time.sleep(min(chunk, remaining))
            remaining -= chunk
