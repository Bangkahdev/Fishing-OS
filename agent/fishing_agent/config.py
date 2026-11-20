"""Lokasi lab portabel (FR-AI-08 / NFR-AI-04)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

LAB_ENV = "FISHING_AI_LAB"
LAB_SUBDIRS = ("models", "runtime", "workspace", "logs")


class LabError(RuntimeError):
    """Akar lab tidak dapat ditentukan atau tidak valid."""


@dataclass(frozen=True)
class LabPaths:
    """Akar lab beserta empat subdirektori tetapnya."""

    root: Path

    @classmethod
    def from_env(cls, override: str | Path | None = None) -> LabPaths:
        raw = override if override is not None else os.environ.get(LAB_ENV)
        if raw is None or str(raw).strip() == "":
            raise LabError(
                f"{LAB_ENV} belum diset. Contoh: export {LAB_ENV}=/mnt/lab/fishing_ai_lab"
            )
        return cls(Path(raw).expanduser().resolve())

    @property
    def models(self) -> Path:
        return self.root / "models"

    @property
    def runtime(self) -> Path:
        return self.root / "runtime"

    @property
    def workspace(self) -> Path:
        return self.root / "workspace"

    @property
    def logs(self) -> Path:
        return self.root / "logs"

    @property
    def stop_file(self) -> Path:
        return self.logs / "stop"

    def ensure(self) -> LabPaths:
        try:
            self.root.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise LabError(f"tidak dapat membuat akar lab {self.root}: {exc}") from exc
        for name in LAB_SUBDIRS:
            try:
                (self.root / name).mkdir(exist_ok=True)
            except OSError as exc:
                raise LabError(f"tidak dapat membuat {name}: {exc}") from exc
        return self
