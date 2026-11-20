"""Action trace per langkah (FR-AI-09)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


_SECRET_KEYS = {"password", "passwd", "token", "secret", "api_key", "authorization", "credential"}


def redact(value: Any, key: str = "") -> Any:
    """Redact field yang lazim berisi credential sebelum ditulis ke disk."""
    if key.lower() in _SECRET_KEYS:
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(item_key): redact(item_value, str(item_key)) for item_key, item_value in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return [redact(item) for item in value]
    return value


class TraceWriter:
    """Menulis satu objek JSON per baris ke berkas sesi."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._step = 0
        self._closed = False

    @property
    def step(self) -> int:
        return self._step

    def write(
        self,
        *,
        perception: str,
        action: str,
        parameters: dict[str, Any] | None = None,
        status: str = "ok",
        note: str = "",
    ) -> dict[str, Any]:
        if self._closed:
            raise RuntimeError("TraceWriter sudah ditutup")
        if perception is None or action is None:
            raise ValueError("perception dan action wajib diisi")
        self._step += 1
        record: dict[str, Any] = {
            "step_id": self._step,
            "timestamp": utc_now(),
            "perception": perception,
            "action": action,
            "parameters": redact(dict(parameters or {})),
            "status": status,
            "note": note,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return record

    def close(self) -> None:
        self._closed = True

    def __enter__(self) -> TraceWriter:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
