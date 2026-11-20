"""IPC Unix-domain socket berformat JSON line untuk ControlService."""

from __future__ import annotations

import json
import os
import socket
import stat
import threading
from pathlib import Path
from typing import Any

from .service import ControlService, ServiceError


class IPCError(RuntimeError):
    """Kesalahan transport atau payload IPC."""


class ControlIPCServer:
    """Server lokal single-user; tidak membuka endpoint TCP atau root shell."""

    def __init__(self, path: str | Path, service: ControlService) -> None:
        if not hasattr(socket, "AF_UNIX"):
            raise IPCError("Unix-domain socket tidak tersedia pada platform ini")
        self.path = Path(path)
        self.service = service
        self._server: socket.socket | None = None
        self._stop = threading.Event()

    def serve_once(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(self.path.parent, stat.S_IRWXU)
        if self.path.exists():
            self.path.unlink()
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server = server
        server.bind(str(self.path))
        os.chmod(self.path, stat.S_IRUSR | stat.S_IWUSR)
        server.listen(1)
        try:
            server.settimeout(0.2)
            while not self._stop.is_set():
                try:
                    connection, _ = server.accept()
                except socket.timeout:
                    continue
                with connection:
                    self._handle(connection)
                break
        finally:
            server.close()
            self._server = None
            if self.path.exists():
                self.path.unlink()

    def stop(self) -> None:
        self._stop.set()
        if self._server is not None:
            self._server.close()

    def _handle(self, connection: socket.socket) -> None:
        payload = connection.makefile("rwb")
        for line in payload:
            try:
                request = json.loads(line.decode("utf-8"))
                response = self._dispatch(request)
            except (ValueError, ServiceError, IPCError) as exc:
                response = {"ok": False, "error": str(exc)}
            payload.write((json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8"))
            payload.flush()

    def _dispatch(self, request: Any) -> dict[str, Any]:
        if not isinstance(request, dict):
            raise IPCError("request harus berupa object JSON")
        method = request.get("method")
        params = request.get("params", {})
        if not isinstance(method, str) or not isinstance(params, dict):
            raise IPCError("method dan params tidak valid")
        if method == "create_task":
            task = self.service.create_task(
                str(params.get("instruction", "")),
                source=str(params.get("source", "ipc")),
                task_id=params.get("task_id"),
            )
            return {"ok": True, "task_id": task.task_id, "state": task.status.value}
        if method == "get_task":
            task = self.service.get_task(str(params.get("task_id", "")))
            return {"ok": True, "task_id": task.task_id, "state": task.status.value, "events": task.events}
        if method == "approve":
            self.service.approve(str(params.get("task_id", "")))
            return {"ok": True}
        if method == "cancel":
            self.service.cancel(str(params.get("task_id", "")), str(params.get("reason", "ipc")))
            return {"ok": True}
        raise IPCError(f"method tidak didukung: {method}")


class ControlIPCClient:
    def __init__(self, path: str | Path, *, timeout: float = 5.0) -> None:
        self.path = str(path)
        self.timeout = timeout

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if not hasattr(socket, "AF_UNIX"):
            raise IPCError("Unix-domain socket tidak tersedia pada platform ini")
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(self.timeout)
            client.connect(self.path)
            stream = client.makefile("rwb")
            stream.write((json.dumps({"method": method, "params": params or {}}) + "\n").encode("utf-8"))
            stream.flush()
            response = json.loads(stream.readline().decode("utf-8"))
        if not isinstance(response, dict):
            raise IPCError("response IPC tidak valid")
        return response


__all__ = ["ControlIPCClient", "ControlIPCServer", "IPCError"]
