"""Tool system-management berbasis command contract Fishing OS."""

from __future__ import annotations

import platform
from collections.abc import Callable
from dataclasses import dataclass

from .command import CommandRequest, CommandResult


class SystemToolError(RuntimeError):
    """Operasi system-management tidak didukung atau gagal."""


@dataclass(frozen=True)
class SystemOperation:
    category: str
    operation: str
    args: tuple[str, ...] = ()
    privilege: str = "user"


class SystemTool:
    """Adapter eksplisit untuk kemampuan OS; tidak menjalankan shell implisit."""

    def __init__(
        self,
        execute: Callable[[CommandRequest], CommandResult],
        *,
        distro: str | None = None,
    ) -> None:
        self._execute = execute
        self.distro = distro or "arch"

    def run(self, operation: SystemOperation) -> CommandResult:
        command, args, privilege = self._map(operation)
        return self._execute(
            CommandRequest(
                command=command,
                args=args,
                execution_mode="argv",
                privilege=privilege,
            )
        )

    def _map(self, operation: SystemOperation) -> tuple[str, tuple[str, ...], str]:
        category, action = operation.category, operation.operation
        args = operation.args
        privilege = operation.privilege
        if category == "packages":
            command = "pacman"
            mapping = {
                "list": ("-Q", ()),
                "search": ("-Ss", args),
                "install": ("-S", ("--noconfirm", *args)),
                "remove": ("-R", ("--noconfirm", *args)),
                "upgrade": ("-Syu", ("--noconfirm",)),
            }
            if action not in mapping:
                raise SystemToolError(f"operasi package tidak dikenal: {action}")
            prefix, mapped_args = mapping[action]
            return command, (prefix, *mapped_args), "elevated" if action in ("install", "remove", "upgrade") else privilege
        if category == "services":
            if action not in ("status", "start", "stop", "restart", "enable", "disable"):
                raise SystemToolError(f"operasi service tidak dikenal: {action}")
            if not args:
                raise SystemToolError("service membutuhkan nama unit")
            return "systemctl", (action, *args), "elevated" if action != "status" else privilege
        if category == "processes":
            if action == "list":
                return "ps", ("-eo", "pid,ppid,user,stat,etime,cmd"), privilege
            if action == "inspect":
                return "ps", ("-fp", *args), privilege
            if action == "stop" and args:
                return "kill", ("--", *args), privilege
            raise SystemToolError(f"operasi proses tidak dikenal atau argumen kurang: {action}")
        if category == "network":
            if action == "status":
                return "ip", ("-brief", "address"), privilege
            if action == "routes":
                return "ip", ("route", "show"), privilege
            if action == "interfaces":
                return "ip", ("link", "show"), privilege
            raise SystemToolError(f"operasi network tidak dikenal: {action}")
        if category == "storage":
            if action == "devices":
                return "lsblk", ("-o", "NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS", "--json"), privilege
            if action == "mounts":
                return "findmnt", ("--json",), privilege
            raise SystemToolError(f"operasi storage tidak dikenal: {action}")
        if category == "hardware":
            if action == "summary":
                return "lspci", (), privilege
            if action == "usb":
                return "lsusb", (), privilege
            raise SystemToolError(f"operasi hardware tidak dikenal: {action}")
        raise SystemToolError(f"kategori system tidak dikenal: {category}")


def default_system_tool(execute: Callable[[CommandRequest], CommandResult]) -> SystemTool:
    """Buat tool hanya pada platform Linux Fishing OS."""
    if platform.system() != "Linux":
        raise SystemToolError("SystemTool hanya didukung pada Fishing OS/Linux")
    return SystemTool(execute)


__all__ = ["SystemOperation", "SystemTool", "SystemToolError", "default_system_tool"]
