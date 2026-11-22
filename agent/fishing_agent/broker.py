"""Privilege Broker minimal dengan IPC Unix terautentikasi (SRS NFR-19/FR-27/32).

Broker adalah komponen kecil yang menerima permintaan operasi privileged dari
Control Service, memvalidasi payload, memastikan Administrator Mode aktif serta
autentikasi sudo native tersedia, menjalankan perintah via ``sudo``, dan menulis
audit tanpa pernah menyimpan password/token.

Batas keamanan:
* Server hanya menerima koneksi dari UID yang sama (``SO_PEERCRED``) dan socket
  dibuat dengan permission 0600.
* Payload divalidasi ketat (kunci dikenal, tipe benar, tanpa NUL, timeout dan
  ukuran pesan dibatasi).
* ``sudo -n true`` wajib berhasil sebelum eksekusi; broker tidak pernah
  menyediakan root shell tanpa autentikasi.
* Broker tidak berjalan sebagai root; perintah elevated dijalankan via sudo.

Di Windows modul inti tetap dapat diuji, tetapi IPC broker hanya tersedia pada
platform dengan ``AF_UNIX`` dan ``SO_PEERCRED`` (Linux/Fishing OS).
"""

from __future__ import annotations

import json
import os
import socket
import struct
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from .command import CommandExecutor, CommandRequest
from .policy import AdministratorMode, PolicyGate, Risk
from .stop import StopRequested

MAX_MESSAGE_BYTES = 64 * 1024
_ALLOWED_KEYS = {"command", "args", "working_directory", "timeout", "reason", "task_id"}


class BrokerError(RuntimeError):
    """Permintaan broker gagal diproses."""


class BrokerDenied(BrokerError):
    """Permintaan broker ditolak oleh kebijakan atau autentikasi."""


class BrokerUnavailable(BrokerError):
    """Broker tidak tersedia pada platform/path ini."""


def _no_nul(value: str, name: str) -> str:
    if "\x00" in value:
        raise BrokerError(f"{name} mengandung karakter NUL")
    return value


@dataclass(frozen=True)
class PrivilegedRequest:
    """Permintaan operasi privileged yang telah divalidasi."""

    command: str
    args: tuple[str, ...] = ()
    working_directory: str | None = None
    timeout: float = 60.0
    reason: str = ""
    task_id: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.command, str) or not self.command.strip():
            raise BrokerError("command wajib diisi")
        _no_nul(self.command, "command")
        if not isinstance(self.args, tuple) or any(not isinstance(item, str) for item in self.args):
            raise BrokerError("args harus tuple string")
        for item in self.args:
            _no_nul(item, "args")
        if self.working_directory is not None:
            _no_nul(str(self.working_directory), "working_directory")
        try:
            timeout = float(self.timeout)
        except (TypeError, ValueError) as exc:
            raise BrokerError("timeout harus angka") from exc
        if timeout <= 0:
            raise BrokerError("timeout harus positif")
        object.__setattr__(self, "timeout", timeout)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "PrivilegedRequest":
        if not isinstance(data, Mapping):
            raise BrokerError("permintaan harus berupa objek")
        unknown = set(data) - _ALLOWED_KEYS
        if unknown:
            raise BrokerError(f"kunci tidak dikenal: {', '.join(sorted(unknown))}")
        command = data.get("command")
        if not isinstance(command, str):
            raise BrokerError("command harus string")
        raw_args = data.get("args", [])
        if not isinstance(raw_args, (list, tuple)) or any(not isinstance(item, str) for item in raw_args):
            raise BrokerError("args harus daftar string")
        working_directory = data.get("working_directory")
        if working_directory is not None and not isinstance(working_directory, str):
            raise BrokerError("working_directory harus string atau null")
        reason = data.get("reason", "")
        task_id = data.get("task_id", "")
        if not isinstance(reason, str) or not isinstance(task_id, str):
            raise BrokerError("reason/task_id harus string")
        return cls(
            command=command,
            args=tuple(raw_args),
            working_directory=working_directory,
            timeout=data.get("timeout", 60.0),
            reason=reason,
            task_id=task_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "args": list(self.args),
            "working_directory": self.working_directory,
            "timeout": self.timeout,
            "reason": self.reason,
            "task_id": self.task_id,
        }

    def to_command_request(self) -> CommandRequest:
        return CommandRequest(
            command=self.command,
            args=self.args,
            execution_mode="argv",
            privilege="elevated",
            timeout=self.timeout,
            working_directory=self.working_directory,
        )


@dataclass(frozen=True)
class BrokerResult:
    ok: bool
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    cancelled: bool = False
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "timed_out": self.timed_out,
            "cancelled": self.cancelled,
            "summary": self.summary,
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "BrokerResult":
        if not isinstance(data, Mapping):
            raise BrokerError("respons broker tidak valid")
        result = data.get("result")
        if not isinstance(result, Mapping):
            raise BrokerError("respons broker tidak memuat result")
        return cls(
            ok=bool(result.get("ok")),
            returncode=result.get("returncode"),
            stdout=str(result.get("stdout", "")),
            stderr=str(result.get("stderr", "")),
            timed_out=bool(result.get("timed_out", False)),
            cancelled=bool(result.get("cancelled", False)),
            summary=str(result.get("summary", "")),
        )


class PrivilegeBroker:
    """Validasi, otorisasi, eksekusi sudo, dan audit untuk operasi privileged."""

    def __init__(
        self,
        administrator: AdministratorMode | None = None,
        *,
        executor: CommandExecutor | None = None,
        trace: Any = None,
        policy: PolicyGate | None = None,
        sudo_check: Callable[[], bool] | None = None,
    ) -> None:
        self.administrator = administrator or AdministratorMode()
        self.executor = executor or CommandExecutor(trace=trace)
        self.trace = trace
        self.policy = policy
        self._sudo_check = sudo_check or self._default_sudo_check

    @staticmethod
    def _default_sudo_check() -> bool:
        try:
            completed = subprocess.run(
                ["sudo", "-n", "true"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return False
        return completed.returncode == 0

    def _audit(self, action: str, request: PrivilegedRequest, *, status: str, note: str = "") -> None:
        if self.trace is None:
            return
        self.trace.write(
            perception="privilege broker",
            action=action,
            parameters={
                "command": request.command,
                "args": list(request.args),
                "working_directory": request.working_directory or "",
                "task_id": request.task_id,
                "reason": request.reason,
            },
            status=status,
            note=note,
        )

    def authorize(self, request: PrivilegedRequest, *, approved: bool) -> None:
        if not self.administrator.active:
            raise BrokerDenied("Administrator Mode belum aktif; autentikasi native OS diperlukan")
        if self.policy is not None and self.policy.risk(request.to_command_request()) == Risk.HIGH and not approved:
            raise BrokerDenied("operasi berisiko tinggi memerlukan approval eksplisit")
        if not self._sudo_check():
            raise BrokerDenied("autentikasi sudo native tidak tersedia; jalankan sudo -v terlebih dahulu")

    def execute(self, request: PrivilegedRequest, *, approved: bool = False) -> BrokerResult:
        self._audit("request", request, status="pending")
        try:
            self.authorize(request, approved=approved)
        except BrokerDenied as exc:
            self._audit("denied", request, status="denied", note=str(exc))
            raise
        self._audit("authorized", request, status="started")
        try:
            result = self.executor.execute(request.to_command_request())
        except StopRequested as exc:
            self._audit("completed", request, status="cancelled", note=exc.reason)
            return BrokerResult(ok=False, cancelled=True, summary=f"dibatalkan: {exc.reason}")
        except Exception as exc:
            self._audit("completed", request, status="failed", note=str(exc))
            raise BrokerError(f"eksekusi privileged gagal: {exc}") from exc
        summary = f"exit={result.returncode} timed_out={result.timed_out} truncated={result.truncated}"
        reply = BrokerResult(
            ok=result.returncode == 0,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            timed_out=result.timed_out,
            cancelled=result.cancelled,
            summary=summary,
        )
        self._audit("completed", request, status="ok" if reply.ok else "failed", note=summary)
        return reply

    def handle(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """Proses satu payload JSON dari IPC dan kembalikan respons aman."""
        try:
            request = PrivilegedRequest.from_mapping(payload.get("request", {}))
            approved = bool(payload.get("approved", False))
            result = self.execute(request, approved=approved)
        except BrokerError as exc:
            return {"ok": False, "error": str(exc)}
        return {"ok": True, "result": result.to_dict()}


def _default_peer_uid(connection: socket.socket) -> int:
    if not hasattr(socket, "SO_PEERCRED"):
        raise BrokerUnavailable("SO_PEERCRED tidak tersedia pada platform ini")
    raw = connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
    _pid, uid, _gid = struct.unpack("3i", raw)
    return uid


class BrokerIPCServer:
    """Server Unix-domain socket yang hanya melayani UID yang sama."""

    def __init__(
        self,
        path: str | Path,
        broker: PrivilegeBroker,
        *,
        peer_uid: Callable[[socket.socket], int] | None = None,
    ) -> None:
        self.path = Path(path)
        self.broker = broker
        self.peer_uid = peer_uid or _default_peer_uid
        self._socket: socket.socket | None = None
        self._stop = threading.Event()

    def start(self) -> None:
        if not hasattr(socket, "AF_UNIX"):
            raise BrokerUnavailable("AF_UNIX tidak tersedia pada platform ini")
        if self.path.exists():
            self.path.unlink()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(self.path))
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass
        server.listen(4)
        server.settimeout(0.2)
        self._socket = server

    def close(self) -> None:
        self._stop.set()
        if self._socket is not None:
            try:
                self._socket.close()
            finally:
                self._socket = None
        try:
            if self.path.exists():
                self.path.unlink()
        except OSError:
            pass

    def serve_forever(self) -> None:
        if self._socket is None:
            self.start()
        assert self._socket is not None
        while not self._stop.is_set():
            try:
                connection, _address = self._socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            with connection:
                connection.settimeout(10)
                try:
                    if self.peer_uid(connection) != os.getuid():
                        self._send(connection, {"ok": False, "error": "UID pemanggil tidak diizinkan"})
                        continue
                    payload = self._receive(connection)
                    if payload is None:
                        continue
                    self._send(connection, self.broker.handle(payload))
                except BrokerError as exc:
                    self._send(connection, {"ok": False, "error": str(exc)})
                except (OSError, ValueError):
                    continue

    @staticmethod
    def _receive(connection: socket.socket) -> dict[str, Any] | None:
        chunks = bytearray()
        while True:
            data = connection.recv(4096)
            if not data:
                return None
            chunks.extend(data)
            if len(chunks) > MAX_MESSAGE_BYTES:
                raise BrokerError("pesan melebihi batas")
            if b"\n" in data:
                break
        line = bytes(chunks).split(b"\n", 1)[0]
        if not line:
            return None
        try:
            payload = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BrokerError(f"payload JSON tidak valid: {exc}") from exc
        if not isinstance(payload, dict):
            raise BrokerError("payload harus berupa objek")
        return payload

    @staticmethod
    def _send(connection: socket.socket, payload: Mapping[str, Any]) -> None:
        connection.sendall(json.dumps(dict(payload), ensure_ascii=False).encode("utf-8") + b"\n")


class BrokerClient:
    """Klien IPC untuk meminta operasi privileged ke broker."""

    def __init__(self, path: str | Path, *, timeout: float = 30.0) -> None:
        self.path = Path(path)
        self.timeout = timeout

    def available(self) -> bool:
        return hasattr(socket, "AF_UNIX") and self.path.exists()

    def execute(self, request: PrivilegedRequest, *, approved: bool = False) -> BrokerResult:
        if not hasattr(socket, "AF_UNIX"):
            raise BrokerUnavailable("AF_UNIX tidak tersedia pada platform ini")
        if not self.path.exists():
            raise BrokerUnavailable(f"socket broker tidak ditemukan: {self.path}")
        payload = {"request": request.to_dict(), "approved": bool(approved)}
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(self.timeout)
        try:
            client.connect(str(self.path))
            client.sendall(json.dumps(payload, ensure_ascii=False).encode("utf-8") + b"\n")
            response = BrokerIPCServer._receive(client)
        except OSError as exc:
            raise BrokerUnavailable(f"gagal menghubungi broker: {exc}") from exc
        finally:
            client.close()
        if response is None:
            raise BrokerError("broker tidak mengirim respons")
        if not response.get("ok"):
            error = str(response.get("error", "broker menolak permintaan"))
            if "Administrator Mode" in error or "sudo" in error or "approval" in error:
                raise BrokerDenied(error)
            raise BrokerError(error)
        return BrokerResult.from_mapping(response)


__all__ = [
    "BrokerClient",
    "BrokerDenied",
    "BrokerError",
    "BrokerIPCServer",
    "BrokerResult",
    "BrokerUnavailable",
    "MAX_MESSAGE_BYTES",
    "PrivilegeBroker",
    "PrivilegedRequest",
]
