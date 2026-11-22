"""UI grounding: AT-SPI2 dahulu, fallback visual (VLM/Set-of-Mark) (FR-16/17).

Strategi grounding sesuai SRS §3.10 dan FR-16/17:

1. **AT-SPI2** menjadi sumber utama bila metadata aksesibilitas tersedia.
2. Bila AT-SPI2 tidak tersedia atau target tidak ditemukan, **fallback visual**:
   tangkap layar (grim/import) lalu minta :class:`VisualDescriber` mengenali
   kandidat target (mis. Set-of-Mark). Describer adalah protokol pluggable;
   implementasi VLM nyata dipasang kemudian tanpa mengubah alur grounding.

Modul ini tidak menjalankan aksi; ia hanya mengembalikan :class:`GroundingResult`
berisi sumber dan elemen/target terpilih sehingga ActionExecutor dapat
memverifikasi sebelum dan sesudah aksi.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, Sequence


@dataclass(frozen=True)
class VisualTarget:
    """Kandidat target visual hasil grounding (mis. dari VLM/Set-of-Mark)."""

    label: str
    x: int
    y: int
    w: int
    h: int
    role: str = "visual"
    confidence: float = 0.0

    def center(self) -> tuple[int, int]:
        return self.x + self.w // 2, self.y + self.h // 2


@dataclass(frozen=True)
class GroundingResult:
    source: str  # "atspi" | "visual" | "none"
    element: Any = None
    note: str = ""

    @property
    def available(self) -> bool:
        return self.source in ("atspi", "visual") and self.element is not None


class VisualDescriber(Protocol):
    name: str

    def describe(self, image_path: str | Path) -> Sequence[VisualTarget]:
        """Kenali kandidat target pada gambar layar."""


class UnavailableDescriber:
    """Describer default yang melaporkan tidak tersedia (VLM belum terpasang)."""

    name = "unavailable"

    def describe(self, image_path: str | Path) -> Sequence[VisualTarget]:
        raise RuntimeError("tidak ada describer visual (pasang runtime VLM untuk fallback visual)")


class Grounder:
    """Gabungkan AT-SPI2 dan fallback visual menjadi satu hasil grounding."""

    def __init__(
        self,
        atspi: Any | None = None,
        screenshot: Any | None = None,
        describer: VisualDescriber | None = None,
    ) -> None:
        if atspi is None:
            from .atspi import ATSPiReader

            atspi = ATSPiReader()
        if screenshot is None:
            from .screenshot import ScreenshotCapture

            screenshot = ScreenshotCapture()
        self.atspi = atspi
        self.screenshot = screenshot
        self.describer = describer or UnavailableDescriber()

    def set_describer(self, describer: VisualDescriber) -> None:
        self.describer = describer

    @property
    def atspi_available(self) -> bool:
        return bool(getattr(self.atspi, "available", False))

    @property
    def visual_available(self) -> bool:
        available = bool(getattr(self.screenshot, "available", False))
        return available and getattr(self.describer, "name", "unavailable") != "unavailable"

    @property
    def available(self) -> bool:
        return self.atspi_available or self.visual_available

    def ground(
        self,
        role: str | None = None,
        name: str | None = None,
        app_id: str | None = None,
        *,
        allow_visual: bool = True,
    ) -> GroundingResult:
        if not role and not name:
            return GroundingResult("none", None, "grounding membutuhkan 'role' atau 'name'")

        if self.atspi_available:
            try:
                elements = self.atspi.find_elements(role, name, app_id)
            except Exception as exc:  # jangan crash desktop; jatuh ke visual
                elements = []
                atspi_error = str(exc)
            else:
                atspi_error = ""
            if elements:
                first = elements[0]
                return GroundingResult(
                    "atspi",
                    first,
                    f"ditemukan {len(elements)} elemen via AT-SPI2; dipakai '{first.role}' '{first.name}'",
                )
            if not allow_visual:
                return GroundingResult("none", None, atspi_error or "target tidak ditemukan via AT-SPI2")

        if allow_visual and self.visual_available:
            return self._ground_visual(role, name)

        if allow_visual:
            return GroundingResult("none", None, "AT-SPI2 tidak menemukan target dan fallback visual tidak tersedia")
        return GroundingResult("none", None, "target tidak ditemukan via AT-SPI2")

    def _ground_visual(self, role: str | None, name: str | None) -> GroundingResult:
        fd, temporary = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        path = Path(temporary)
        try:
            self.screenshot.capture(path)
            try:
                targets = list(self.describer.describe(path))
            except Exception as exc:
                return GroundingResult("none", None, f"describer visual gagal: {exc}")
        finally:
            try:
                path.unlink()
            except OSError:
                pass
        if not targets:
            return GroundingResult("none", None, "describer visual tidak menemukan kandidat target")
        best = self._best_match(targets, role, name)
        return GroundingResult(
            "visual",
            best,
            f"fallback visual memilih target '{best.label}' (confidence {best.confidence:.2f})",
        )

    @staticmethod
    def _best_match(targets: Sequence[VisualTarget], role: str | None, name: str | None) -> VisualTarget:
        def score(target: VisualTarget) -> tuple[float, float]:
            label = target.label.lower()
            matches = 0.0
            if name and name.lower() in label:
                matches += 2.0
            if role and role.lower() in (target.role.lower() or ""):
                matches += 1.0
            return matches, target.confidence

        return max(targets, key=score)


__all__ = ["Grounder", "GroundingResult", "UnavailableDescriber", "VisualDescriber", "VisualTarget"]