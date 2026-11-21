"""Pembaca pohon aksesibilitas AT-SPI2 dengan fallback saat tidak tersedia (FR-16/17).

Implementasi memakai pyatspi bila terpasang dan *bridge* aksesibilitas desktop aktif.
Bila tidak tersedia, reader melaporkan status itu sehingga caller dapat memilih
fallback VLM. Pemetaan accessible -> UIElement dipisah dari penelusuran agar dapat
diuji tanpa sesi desktop nyata.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator

from .verification import verify_elements


@dataclass(frozen=True)
class UIElement:
    role: str
    name: str
    state: tuple[str, ...]
    x: int
    y: int
    w: int
    h: int
    app_id: str | None = None


class ATSPiUnavailable(RuntimeError):
    """AT-SPI2 tidak tersedia pada sesi saat ini."""


class ATSPiActionFailed(RuntimeError):
    """Aksi AT-SPI2 gagal dijalankan atau target tidak mendukung Action."""


PREFERRED_ACTIONS = ("click", "press", "activate", "open", "toggle")


_STATE_NAMES = (
    "active",
    "focused",
    "enabled",
    "visible",
    "showing",
    "checked",
    "pressed",
    "sensitive",
    "editable",
    "selected",
    "expanded",
)

MAX_WALK = 4000


class ATSPiReader:
    def __init__(self, available: bool | None = None, module: Any | None = None) -> None:
        self._module = module if module is not None else self._load_pyatspi()
        self._available = bool(self._module) if available is None else bool(available)

    @staticmethod
    def _load_pyatspi() -> Any | None:
        try:
            import pyatspi  # type: ignore
        except ImportError:
            return None
        return pyatspi

    @property
    def available(self) -> bool:
        return self._available

    def require_available(self) -> None:
        if not self._available:
            raise ATSPiUnavailable(
                "AT-SPI2 tidak tersedia; pasang bridge aksesibilitas desktop atau gunakan fallback VLM"
            )
        if self._module is None:
            raise ATSPiUnavailable("modul pyatspi tidak tersedia")

    # -- pemetaan accessible -> UIElement -------------------------------------

    def _state_names(self, accessible: Any) -> tuple[str, ...]:
        try:
            state_set = accessible.getState()
        except Exception:
            return ()
        result: list[str] = []
        for name in _STATE_NAMES:
            try:
                if state_set.contains(getattr(self._module.StateType, name.upper())):
                    result.append(name)
            except Exception:
                continue
        return tuple(result)

    def _extents(self, accessible: Any) -> tuple[int, int, int, int]:
        desk_coords = getattr(self._module, "DESKTOP_COORDS", 0)
        try:
            x, y, w, h = accessible.getExtents(desk_coords)
        except Exception:
            try:
                x, y, w, h = accessible.getExtents()
            except Exception:
                return 0, 0, 0, 0
        return int(x), int(y), int(w), int(h)

    def element_from(self, accessible: Any, app_id: str | None = None) -> UIElement:
        self.require_available()
        role = getattr(accessible.getRole(), "name", "unknown")
        name = getattr(accessible, "name", "") or ""
        x, y, w, h = self._extents(accessible)
        return UIElement(
            role=str(role).lower(),
            name=str(name),
            state=self._state_names(accessible),
            x=x,
            y=y,
            w=w,
            h=h,
            app_id=app_id,
        )

    # -- penelusuran ---------------------------------------------------------

    def _children(self, accessible: Any) -> list[Any]:
        try:
            return list(accessible)
        except Exception:
            return []

    def _walk(self, root: Any, limit: int = MAX_WALK) -> Iterator[Any]:
        stack = [root]
        seen = 0
        while stack and seen < limit:
            node = stack.pop()
            seen += 1
            yield node
            stack.extend(self._children(node))

    def _desktop(self) -> Any:
        self.require_available()
        registry = getattr(self._module, "Registry", None)
        if registry is None:
            raise ATSPiUnavailable("pyatspi.Registry tidak tersedia")
        return registry.getDesktop(0)

    def _active_frame(self) -> tuple[Any, str | None] | None:
        desktop = self._desktop()
        for app in self._children(desktop):
            app_name = getattr(app, "name", None)
            if not self._children(app):
                continue
            for frame in self._children(app):
                if "active" in self._state_names(frame):
                    return frame, app_name
        return None

    def get_active_window(self) -> UIElement | None:
        found = self._active_frame()
        if found is None:
            return None
        frame, app_name = found
        return self.element_from(frame, app_id=app_name)

    def find_elements(
        self,
        role: str | None = None,
        name: str | None = None,
        app_id: str | None = None,
        *,
        limit: int = MAX_WALK,
    ) -> list[UIElement]:
        found = self._active_frame()
        if found is None:
            return []
        frame, frame_app = found
        if app_id is not None and app_id != frame_app:
            return []
        role_filter = role.lower() if role else None
        name_filter = name.lower() if name else None
        results: list[UIElement] = []
        for node in self._walk(frame, limit=limit):
            element = self.element_from(node, app_id=frame_app)
            if role_filter is not None and element.role != role_filter:
                continue
            if name_filter is not None and name_filter not in element.name.lower():
                continue
            results.append(element)
        return results

    # -- aksi ----------------------------------------------------------------

    def _locate(self, role: str | None, name: str | None, app_id: str | None) -> tuple[Any, str | None] | None:
        found = self._active_frame()
        if found is None:
            return None
        frame, frame_app = found
        if app_id is not None and app_id != frame_app:
            return None
        role_filter = role.lower() if role else None
        name_filter = name.lower() if name else None
        for node in self._walk(frame):
            element = self.element_from(node, app_id=frame_app)
            if role_filter is not None and element.role != role_filter:
                continue
            if name_filter is not None and name_filter not in element.name.lower():
                continue
            return node, frame_app
        return None

    def _action_names(self, interface: Any) -> list[str]:
        names: list[str] = []
        try:
            count = int(getattr(interface, "nActions", 0))
        except Exception:
            count = 0
        for index in range(count):
            try:
                names.append(str(interface.getName(index)))
            except Exception:
                names.append("")
        return names

    def _action_interface(self, node: Any) -> Any:
        query = getattr(node, "queryAction", None)
        if query is None:
            raise ATSPiActionFailed("elemen tidak mendukung antarmuka Action")
        try:
            return query()
        except Exception as exc:
            raise ATSPiActionFailed(f"antarmuka Action tidak tersedia: {exc}") from exc

    def perform_action(
        self,
        role: str | None = None,
        name: str | None = None,
        *,
        action: str | None = None,
        app_id: str | None = None,
        expected_change: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        """Jalankan Action pada elemen, lalu bandingkan state sebelum/sesudah (FR-18)."""
        located = self._locate(role, name, app_id)
        if located is None:
            raise ATSPiActionFailed("target tidak ditemukan pada window aktif")
        node, frame_app = located
        before = self.element_from(node, frame_app)
        interface = self._action_interface(node)
        names = self._action_names(interface)
        if not names:
            raise ATSPiActionFailed("elemen tidak memiliki aksi yang tersedia")
        if action is None:
            index = next(
                (i for i, candidate in enumerate(names) if candidate.lower() in PREFERRED_ACTIONS),
                0,
            )
        else:
            index = next((i for i, candidate in enumerate(names) if candidate.lower() == action.lower()), None)
            if index is None:
                raise ATSPiActionFailed(f"aksi tidak tersedia: {action}; pilihan: {', '.join(names)}")
        try:
            interface.doAction(index)
        except Exception as exc:
            raise ATSPiActionFailed(f"aksi {names[index]} gagal: {exc}") from exc

        after: dict[str, Any] | None
        try:
            after_element = self.element_from(node, frame_app)
            after = {
                "role": after_element.role,
                "name": after_element.name,
                "state": list(after_element.state),
            }
        except Exception:
            after = None
            after_element = None

        if after_element is None:
            return {
                "ok": True,
                "grounding": "atspi",
                "action": names[index],
                "before": {"role": before.role, "name": before.name, "state": list(before.state)},
                "after": None,
                "verified": False,
                "note": "target hilang setelah aksi; verifikasi visual diperlukan",
            }
        result = verify_elements(
            {"role": before.role, "name": before.name, "state": list(before.state)},
            after,
            expected_change={field: True for field in expected_change},
        )
        return {
            "ok": True,
            "grounding": "atspi",
            "action": names[index],
            "before": {"role": before.role, "name": before.name, "state": list(before.state)},
            "after": after,
            "verified": result.passed,
            "note": result.note,
        }

    def element_at(self, x: int, y: int) -> UIElement | None:
        found = self._active_frame()
        if found is None:
            return None
        frame, frame_app = found
        best: UIElement | None = None
        best_area = None
        for node in self._walk(frame):
            element = self.element_from(node, app_id=frame_app)
            if element.w <= 0 or element.h <= 0:
                continue
            if not (element.x <= x <= element.x + element.w and element.y <= y <= element.y + element.h):
                continue
            area = element.w * element.h
            if best_area is None or area < best_area:
                best, best_area = element, area
        return best

    def describe(self, element: UIElement) -> dict[str, Any]:
        return {
            "role": element.role,
            "name": element.name,
            "state": list(element.state),
            "position": {"x": element.x, "y": element.y},
            "size": {"w": element.w, "h": element.h},
            "app_id": element.app_id,
            "source": "atspi" if self._available else "stub",
        }


__all__ = ["ATSPiActionFailed", "ATSPiReader", "ATSPiUnavailable", "PREFERRED_ACTIONS", "UIElement"]
