"""Tangkapan layar untuk verifikasi visual (FR-17).

Metode yang didukung: grim (Wayland/Hyprland), import/ImageMagick (X11).
Jika keduanya tidak tersedia, capture melaporkan tidak tersedia sehingga caller
dapat memilih fallback AT-SPI2 atau melaporkan keterbatasan kepada pengguna.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


class ScreenshotError(RuntimeError):
    """Gagal menangkap layar."""


class ScreenshotUnavailable(RuntimeError):
    """Tidak ada alat tangkapan layar pada sistem."""


class ScreenshotCapture:
    def __init__(self) -> None:
        self.method = self._select_method()

    def _select_method(self) -> str | None:
        if shutil.which("grim"):
            return "grim"
        if shutil.which("import"):
            return "import"
        return None

    @property
    def available(self) -> bool:
        return self.method is not None

    def capture(self, path: str | Path | None = None) -> Path:
        if self.method is None:
            raise ScreenshotUnavailable(
                "tidak ada alat tangkapan layar (grim untuk Wayland/Hyprland atau import untuk X11)"
            )
        target = Path(path) if path is not None else Path(tempfile.mkstemp(suffix=".png")[1])
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            if self.method == "grim":
                subprocess.run(["grim", str(target)], check=True)
            else:
                subprocess.run(["import", "-window", "root", str(target)], check=True)
        except subprocess.CalledProcessError as exc:
            raise ScreenshotError(f"gagal menangkap layar melalui {self.method}: {exc}") from exc
        if not target.is_file() or target.stat().st_size == 0:
            raise ScreenshotError(f"berkas tangkapan layar kosong: {target}")
        return target


__all__ = ["ScreenshotCapture", "ScreenshotError", "ScreenshotUnavailable"]
