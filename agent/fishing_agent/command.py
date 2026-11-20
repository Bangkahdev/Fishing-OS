"""Eksekusi command lokal terstruktur dengan cancellation dan output terbatas."""

from __future__ import annotations

import os
import selectors
import signal
import subprocess
import time
from dataclasses import dataclass, field
from typing import Mapping, Sequence

from .stop import StopController, StopRequested
from .trace import TraceWriter

VALID_MODES = ("argv", "shell", "script", "interactive")
VALID_PRIVILEGES = ("user", "elevated")


class CommandValidationError(ValueError):
    """Request command tidak memenuhi kontrak executor."""


@dataclass(frozen=True)
class OutputPolicy:
    max_bytes: int = 1024 * 1024
    redact_secrets: bool = True

    def __post_init__(self) -> None:
        if self.max_bytes < 1:
            raise CommandValidationError("output max_bytes minimal 1")


@dataclass(frozen=True)
class CommandRequest:
    command: str
    args: tuple[str, ...] = ()
    working_directory: str | None = None
    environment: Mapping[str, str] = field(default_factory=dict)
    execution_mode: str = "argv"
    privilege: str = "user"
    timeout: float | None = 60.0
    stdin_policy: str = "closed"
    output_policy: OutputPolicy = field(default_factory=OutputPolicy)

    def __post_init__(self) -> None:
        if not isinstance(self.command, str) or not self.command.strip():
            raise CommandValidationError("command wajib berupa string tidak kosong")
        if self.execution_mode not in VALID_MODES:
            raise CommandValidationError(f"execution_mode tidak valid: {self.execution_mode}")
        if self.privilege not in VALID_PRIVILEGES:
            raise CommandValidationError(f"privilege tidak valid: {self.privilege}")
        if self.timeout is not None and self.timeout <= 0:
            raise CommandValidationError("timeout harus positif atau None")
        if self.stdin_policy not in ("closed", "inherit", "interactive"):
            raise CommandValidationError("stdin_policy harus closed, inherit, atau interactive")
        if any(not isinstance(key, str) or not isinstance(value, str) for key, value in self.environment.items()):
            raise CommandValidationError("environment harus memetakan string ke string")
        if self.execution_mode in ("argv", "script") and any("\x00" in part for part in self.args):
            raise CommandValidationError("argumen tidak boleh mengandung NUL")

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> CommandRequest:
        if not isinstance(data, Mapping):
            raise CommandValidationError("command request harus berupa objek")
        args = data.get("args", ())
        if not isinstance(args, (list, tuple)) or any(not isinstance(item, str) for item in args):
            raise CommandValidationError("args harus berupa daftar string")
        output = data.get("output_policy", {})
        if not isinstance(output, Mapping):
            raise CommandValidationError("output_policy harus berupa objek")
        return cls(
            command=str(data.get("command", "")),
            args=tuple(args),
            working_directory=data.get("working_directory") if isinstance(data.get("working_directory"), str) else None,
            environment=data.get("environment", {}) if isinstance(data.get("environment", {}), Mapping) else {},
            execution_mode=str(data.get("execution_mode", "argv")),
            privilege=str(data.get("privilege", "user")),
            timeout=data.get("timeout", 60.0) if data.get("timeout", 60.0) is None else float(data.get("timeout", 60.0)),
            stdin_policy=str(data.get("stdin_policy", "closed")),
            output_policy=OutputPolicy(
                max_bytes=int(output.get("max_bytes", 1024 * 1024)),
                redact_secrets=bool(output.get("redact_secrets", True)),
            ),
        )


@dataclass(frozen=True)
class CommandResult:
    returncode: int | None
    stdout: str
    stderr: str
    timed_out: bool = False
    cancelled: bool = False
    truncated: bool = False


class CommandExecutor:
    """Menjalankan request melalui user context atau sudo native."""

    def __init__(self, stop: StopController | None = None, trace: TraceWriter | None = None) -> None:
        self.stop = stop or StopController()
        self.trace = trace

    def execute(self, request: CommandRequest) -> CommandResult:
        self.stop.check()
        argv, shell = self._build_command(request)
        if self.trace is not None:
            self.trace.write(
                perception="command executor",
                action="command",
                parameters={
                    "command": request.command,
                    "args": list(request.args),
                    "execution_mode": request.execution_mode,
                    "privilege": request.privilege,
                    "working_directory": request.working_directory or "",
                },
                status="started",
            )
        stdin = None if request.stdin_policy in ("inherit", "interactive") else subprocess.DEVNULL
        if request.stdin_policy == "interactive":
            stdin = None
        env = self._environment(request.environment)
        try:
            process = subprocess.Popen(
                argv if not shell else argv[0],
                cwd=request.working_directory,
                env=env,
                stdin=stdin,
                stdout=None if request.stdin_policy == "interactive" else subprocess.PIPE,
                stderr=None if request.stdin_policy == "interactive" else subprocess.PIPE,
                shell=shell,
                start_new_session=(os.name != "nt"),
                text=False,
            )
        except OSError:
            raise
        try:
            if request.stdin_policy == "interactive":
                result = self._wait_interactive(process, request)
            else:
                result = self._collect(process, request)
        except StopRequested as exc:
            if self.trace is not None:
                self.trace.write(perception="command executor", action="command", status="cancelled", note=exc.reason)
            raise
        if self.trace is not None:
            self.trace.write(
                perception="command executor",
                action="command",
                parameters={"exit_code": result.returncode, "timed_out": result.timed_out, "truncated": result.truncated},
                status="completed" if result.returncode == 0 else "failed",
            )
        return result

    def _build_command(self, request: CommandRequest) -> tuple[list[str], bool]:
        if request.execution_mode == "argv":
            command: list[str] = [request.command, *request.args]
            shell = False
        elif request.execution_mode == "shell":
            command = [request.command]
            shell = True
        elif request.execution_mode == "script":
            interpreter = request.args[0] if request.args else "/bin/sh"
            command = [interpreter, "-c", request.command]
            shell = False
        else:
            command = [request.command, *request.args]
            shell = False
        if request.privilege == "elevated":
            if shell:
                command = ["sudo", "--", "sh", "-c", request.command]
                shell = False
            else:
                command = ["sudo", "--", *command]
        return command, shell

    @staticmethod
    def _environment(extra: Mapping[str, str]) -> dict[str, str]:
        allowed = (
            "PATH", "HOME", "USER", "LOGNAME", "LANG", "LC_ALL", "TERM",
            "DISPLAY", "WAYLAND_DISPLAY", "XDG_RUNTIME_DIR", "SYSTEMROOT",
            "SystemRoot", "SystemDrive", "PATHEXT", "COMSPEC", "TEMP", "TMP",
            "OS", "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS",
        )
        env = {key: value for key, value in os.environ.items() if key in allowed}
        env.update(extra)
        return env

    def _wait_interactive(self, process: subprocess.Popen[bytes], request: CommandRequest) -> CommandResult:
        try:
            returncode = process.wait(timeout=request.timeout)
        except subprocess.TimeoutExpired:
            self._terminate(process)
            return CommandResult(None, "", "", timed_out=True)
        self.stop.check()
        return CommandResult(returncode, "", "")

    def _collect(self, process: subprocess.Popen[bytes], request: CommandRequest) -> CommandResult:
        if os.name == "nt":
            return self._collect_windows(process, request)
        limit = request.output_policy.max_bytes
        started = time.monotonic()
        selector = selectors.DefaultSelector()
        assert process.stdout is not None and process.stderr is not None
        selector.register(process.stdout, selectors.EVENT_READ, "stdout")
        selector.register(process.stderr, selectors.EVENT_READ, "stderr")
        chunks = {"stdout": bytearray(), "stderr": bytearray()}
        truncated = False
        try:
            while selector.get_map():
                self.stop.check()
                remaining = None if request.timeout is None else request.timeout - (time.monotonic() - started)
                if remaining is not None and remaining <= 0:
                    self._terminate(process)
                    return CommandResult(None, self._decode(chunks["stdout"]), self._decode(chunks["stderr"]), timed_out=True, truncated=truncated)
                for key, _ in selector.select(0.05 if remaining is None else min(0.05, remaining)):
                    data = key.fileobj.read1(65536)
                    if not data:
                        selector.unregister(key.fileobj)
                        continue
                    bucket = chunks[key.data]
                    available = limit - sum(len(item) for item in chunks.values())
                    if available <= 0:
                        truncated = True
                    else:
                        bucket.extend(data[:available])
                        truncated = truncated or len(data) > available
            returncode = process.wait(timeout=0.1)
            return CommandResult(returncode, self._decode(chunks["stdout"]), self._decode(chunks["stderr"]), truncated=truncated)
        except StopRequested:
            self._terminate(process)
            raise
        finally:
            selector.close()

    def _collect_windows(self, process: subprocess.Popen[bytes], request: CommandRequest) -> CommandResult:
        """Windows anonymous pipes tidak dapat dipakai oleh selectors.select."""
        started = time.monotonic()
        stdout = stderr = b""
        while True:
            self.stop.check()
            remaining = None if request.timeout is None else request.timeout - (time.monotonic() - started)
            if remaining is not None and remaining <= 0:
                self._terminate(process)
                return self._limited_result(stdout, stderr, request, timed_out=True)
            try:
                stdout, stderr = process.communicate(timeout=0.05 if remaining is None else min(0.05, remaining))
                return self._limited_result(stdout, stderr, request, returncode=process.returncode)
            except subprocess.TimeoutExpired as exc:
                if exc.output:
                    stdout = exc.output
                if exc.stderr:
                    stderr = exc.stderr

    def _limited_result(
        self,
        stdout: bytes,
        stderr: bytes,
        request: CommandRequest,
        *,
        returncode: int | None = None,
        timed_out: bool = False,
    ) -> CommandResult:
        limit = request.output_policy.max_bytes
        combined = stdout + stderr
        truncated = len(combined) > limit
        stdout = stdout[:limit]
        stderr = stderr[: max(0, limit - len(stdout))]
        return CommandResult(
            returncode,
            self._decode(bytearray(stdout)),
            self._decode(bytearray(stderr)),
            timed_out=timed_out,
            truncated=truncated,
        )

    @staticmethod
    def _decode(data: bytearray) -> str:
        return bytes(data).decode("utf-8", errors="replace")

    @staticmethod
    def _terminate(process: subprocess.Popen[bytes]) -> None:
        if process.poll() is not None:
            return
        try:
            if os.name != "nt":
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
            else:
                process.terminate()
        finally:
            if process.poll() is None:
                process.kill()


__all__ = ["CommandExecutor", "CommandRequest", "CommandResult", "CommandValidationError", "OutputPolicy"]
