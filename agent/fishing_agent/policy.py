"""Policy gate, approval, dan Administrator Mode tanpa penyimpanan credential."""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum

from .command import CommandRequest


class Risk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ApprovalRequired(PermissionError):
    """Aksi berdampak tinggi belum memperoleh approval eksplisit."""


@dataclass
class AdministratorMode:
    """Otorisasi sementara; token/password tidak pernah disimpan."""

    expires_at: float | None = None

    @property
    def active(self) -> bool:
        return self.expires_at is not None and time.monotonic() < self.expires_at

    def enable(self, duration: float = 900.0) -> None:
        if duration <= 0:
            raise ValueError("durasi Administrator Mode harus positif")
        self.expires_at = time.monotonic() + duration

    def revoke(self) -> None:
        self.expires_at = None


class PolicyGate:
    """Menentukan privilege dan approval sebelum executor dipanggil."""

    _HIGH_MARKERS = ("mkfs", "fdisk", "parted", "userdel", "groupdel", "rm -rf", "chmod 777", "chown -r")

    def __init__(self, administrator: AdministratorMode | None = None) -> None:
        self.administrator = administrator or AdministratorMode()
        self._approved: set[str] = set()

    def risk(self, request: CommandRequest) -> Risk:
        text = " ".join((request.command, *request.args)).lower()
        if any(marker in text for marker in self._HIGH_MARKERS):
            return Risk.HIGH
        if request.privilege == "elevated" or request.execution_mode in ("shell", "script"):
            return Risk.MEDIUM
        return Risk.LOW

    def approve(self, task_id: str) -> None:
        if not task_id.strip():
            raise ValueError("task_id wajib diisi")
        self._approved.add(task_id)

    def is_approved(self, task_id: str) -> bool:
        return task_id in self._approved

    def authorize(self, task_id: str, request: CommandRequest) -> None:
        risk = self.risk(request)
        if request.privilege == "elevated" and not self.administrator.active:
            raise PermissionError("Administrator Mode belum aktif; autentikasi native OS diperlukan")
        if risk == Risk.HIGH and task_id not in self._approved:
            raise ApprovalRequired("approval eksplisit diperlukan untuk operasi berisiko tinggi")


__all__ = ["AdministratorMode", "ApprovalRequired", "PolicyGate", "Risk"]
