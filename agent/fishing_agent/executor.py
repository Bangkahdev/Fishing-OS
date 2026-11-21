"""Executor aksi atomik dengan backend input yang dapat dipilih (FR-AI-01/10/11/12)."""

from __future__ import annotations

import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .atspi import ATSPiReader
from .stop import StopController, StopRequested
from .trace import TraceWriter
from .verification import VerificationFailed

BACKEND_ENV = "FISHING_AGENT_BACKEND"
VALID_KINDS = ("move", "click", "rightclick", "type", "key", "wait", "sh", "notify", "ui_action")


class ActionError(ValueError):
    """Definisi aksi tidak valid."""


class BackendUnavailable(RuntimeError):
    """Backend atau tool input tidak tersedia."""


@dataclass(frozen=True)
class Action:
    kind: str
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.kind not in VALID_KINDS:
            raise ActionError(f"aksi tidak dikenal: {self.kind!r}; pilihan: {', '.join(VALID_KINDS)}")

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> Action:
        if not isinstance(data, dict):
            raise ActionError("aksi harus berupa objek")
        kind = data.get("kind")
        if not isinstance(kind, str):
            raise ActionError("aksi tanpa field 'kind'")
        params = data.get("params") or {}
        if not isinstance(params, dict):
            raise ActionError("field 'params' harus objek")
        extra = {key: value for key, value in data.items() if key not in ("kind", "params")}
        return cls(kind=kind, params={**params, **extra})


class Backend(ABC):
    name = "abstract"

    @abstractmethod
    def move(self, x: int, y: int) -> None: ...

    @abstractmethod
    def click(self, button: str = "left") -> None: ...

    @abstractmethod
    def type_text(self, text: str) -> None: ...

    @abstractmethod
    def key(self, keys: str) -> None: ...

    def command(self, argv: Sequence[str]) -> None:
        subprocess.run(list(argv), check=True)


class DryRunBackend(Backend):
    """Mencatat aksi tanpa menyentuh input nyata."""

    name = "dry-run"

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def move(self, x: int, y: int) -> None:
        self.calls.append(("move", {"x": x, "y": y}))

    def click(self, button: str = "left") -> None:
        self.calls.append(("click", {"button": button}))

    def type_text(self, text: str) -> None:
        self.calls.append(("type", {"text": text}))

    def key(self, keys: str) -> None:
        self.calls.append(("key", {"keys": keys}))

    def command(self, argv: Sequence[str]) -> None:
        self.calls.append(("command", {"argv": list(argv)}))


class X11Backend(Backend):
    name = "x11"

    def __init__(self, binary: str = "xdotool") -> None:
        if shutil.which(binary) is None:
            raise BackendUnavailable(
                f"backend X11 butuh '{binary}'; pasang: sudo pacman -S xdotool"
            )
        self.binary = binary

    def move(self, x: int, y: int) -> None:
        self.command([self.binary, "mousemove", "--sync", str(int(x)), str(int(y))])

    def click(self, button: str = "left") -> None:
        code = "1" if button == "left" else "3"
        self.command([self.binary, "click", code])

    def type_text(self, text: str) -> None:
        self.command([self.binary, "type", "--delay", "20", "--", text])

    def key(self, keys: str) -> None:
        self.command([self.binary, "key", "--", keys])


class WaylandBackend(Backend):
    name = "wayland"

    def __init__(self, pointer: str = "ydotool", typer: str = "wtype") -> None:
        missing = [tool for tool in (pointer, typer) if shutil.which(tool) is None]
        if missing:
            raise BackendUnavailable(
                "backend Wayland butuh "
                + ", ".join(missing)
                + "; pasang: sudo pacman -S ydotool wtype"
            )
        self.pointer = pointer
        self.typer = typer

    def move(self, x: int, y: int) -> None:
        self.command([self.pointer, "mousemove", "--absolute", "-x", str(int(x)), "-y", str(int(y))])

    def click(self, button: str = "left") -> None:
        self.command([self.pointer, "click", "0xC0" if button == "left" else "0xC1"])

    def type_text(self, text: str) -> None:
        self.command([self.typer, "--", text])

    def key(self, keys: str) -> None:
        parts = [part for part in keys.split("+") if part]
        if not parts:
            raise ActionError("kombinasi tombol kosong")
        *modifiers, base = parts
        self.command([self.typer, "-M", *modifiers, base] if modifiers else [self.typer, base])


def select_backend(name: str | None = None, *, dry_run: bool = False) -> Backend:
    if dry_run:
        return DryRunBackend()
    chosen = (name or os.environ.get(BACKEND_ENV) or "").strip().lower()
    if chosen in ("dry-run", "dry_run", "dryrun"):
        return DryRunBackend()
    if chosen in ("", "auto"):
        if shutil.which("xdotool"):
            return X11Backend()
        if shutil.which("ydotool") and shutil.which("wtype"):
            return WaylandBackend()
        raise BackendUnavailable(
            "tidak ada backend input terdeteksi; pasang xdotool (X11) "
            "atau ydotool + wtype (Wayland), atau jalankan --dry-run"
        )
    if chosen in ("x11", "xdotool"):
        return X11Backend()
    if chosen in ("wayland", "wlroots"):
        return WaylandBackend()
    raise BackendUnavailable(f"backend tidak dikenal: {chosen!r}; pilihan: dry-run, x11, wayland")


class ActionExecutor:
    def __init__(
        self,
        backend: Backend,
        trace: TraceWriter,
        stop: StopController,
        *,
        pacing: float = 0.4,
        max_steps: int = 50,
        perception: str = "sesi desktop aktif",
        sleep: Callable[[float], None] | None = None,
        atspi: ATSPiReader | None = None,
    ) -> None:
        if max_steps < 1:
            raise ValueError("max_steps minimal 1")
        self.backend = backend
        self.trace = trace
        self.stop = stop
        self.pacing = max(0.0, float(pacing))
        self.max_steps = int(max_steps)
        self.perception = perception
        self.atspi = atspi
        self._sleep = sleep or stop.sleep

    def run(self, actions: Iterable[Action]) -> int:
        executed = 0
        try:
            for action in actions:
                if executed >= self.max_steps:
                    self._log_stop("batas max-steps tercapai")
                    break
                self.stop.check()
                action_perception = self.perception
                try:
                    action_perception = self._dispatch(action) or self.perception
                except StopRequested:
                    raise
                except Exception as exc:
                    self.trace.write(
                        perception=action_perception,
                        action=action.kind,
                        parameters=action.params,
                        status="error",
                        note=str(exc),
                    )
                    raise
                self.trace.write(
                    perception=action_perception,
                    action=action.kind,
                    parameters=action.params,
                    status="ok",
                )
                executed += 1
                self._sleep(self.pacing)
        except StopRequested as exc:
            self._log_stop(exc.reason)
            raise
        return executed

    def _log_stop(self, note: str) -> None:
        self.trace.write(perception=self.perception, action="stop", status="stopped", note=note)

    def _dispatch(self, action: Action) -> str | None:
        params = action.params
        if action.kind == "move":
            self.backend.move(int(params["x"]), int(params["y"]))
        elif action.kind == "click":
            self.backend.click(str(params.get("button", "left")))
        elif action.kind == "rightclick":
            self.backend.click("right")
        elif action.kind == "type":
            self.backend.type_text(str(params["text"]))
        elif action.kind == "key":
            self.backend.key(str(params["keys"]))
        elif action.kind == "wait":
            self._sleep(float(params.get("seconds", 0.5)))
        elif action.kind == "sh":
            argv = params.get("argv")
            if not argv:
                raise ActionError("aksi 'sh' butuh 'argv' berupa daftar string")
            self.backend.command([str(part) for part in argv])
        elif action.kind == "notify":
            self.backend.command(["notify-send", str(params.get("text", "fishing-agent"))])
        elif action.kind == "ui_action":
            return self._ui_action(params)
        else:  # pragma: no cover - dijaga oleh Action.__post_init__
            raise ActionError(f"aksi tidak dikenal: {action.kind}")
        return None

    def _ui_action(self, params: dict[str, Any]) -> str:
        role = params.get("role")
        name = params.get("name")
        if not role and not name:
            raise ActionError("aksi 'ui_action' butuh 'role' atau 'name'")
        reader = self.atspi or ATSPiReader()
        if not reader.available:
            raise BackendUnavailable(
                "AT-SPI2 tidak tersedia; aktifkan bridge aksesibilitas atau gunakan "
                "aksi pointer/koordinat dengan verifikasi visual"
            )
        expected = params.get("expected_change") or ()
        if isinstance(expected, str):
            expected = (expected,)
        result = reader.perform_action(
            str(role) if role else None,
            str(name) if name else None,
            action=params.get("action"),
            app_id=params.get("app_id"),
            expected_change=tuple(str(field) for field in expected),
        )
        perception = f"atspi: {result['role']} '{result['name']}' via {result['action']}"
        if not result["verified"]:
            perception += f" (belum terverifikasi: {result['note']})"
            if params.get("verify", True):
                raise VerificationFailed(result["note"])
        return perception


def load_actions(path: str | Path) -> list[Action]:
    import json

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("actions", [])
    if not isinstance(data, list):
        raise ActionError("skrip aksi harus berupa daftar atau objek {'actions': [...]}")
    return [Action.from_mapping(item) for item in data]


__all__ = [
    "Action",
    "ActionError",
    "ActionExecutor",
    "Backend",
    "BackendUnavailable",
    "DryRunBackend",
    "WaylandBackend",
    "X11Backend",
    "load_actions",
    "select_backend",
]
