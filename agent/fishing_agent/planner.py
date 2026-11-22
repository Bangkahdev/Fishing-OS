"""Perencana (LLM Planner) yang mengubah instruksi menjadi rencana tool call.

SRS §3.2/§3.5 memisahkan peran *LLM Planner* dari eksekusi: model hanya
menghasilkan rencana terstruktur yang **divalidasi** orchestrator terhadap
schema tool registry sebelum dijalankan. Modul ini menyediakan:

* :class:`Plan` / :class:`PlanStep` — struktur rencana yang stabil dan dapat
  di-serialize ke JSON (dipakai juga oleh opsi ``--plan`` pada CLI).
* :class:`Planner` — protokol perencana.
* :class:`HeuristicPlanner` — perencana deterministik (tanpa model, untuk uji,
  demo, dan fallback offline). Dipetakan dari kata kunci dwibahasa (ID/EN).
* :func:`get_planner` — pabrik perencana; titik pasang runtime LLM nyata nanti.

Perencana **tidak** mengeksekusi apa pun. Ia hanya menghasilkan rencana;
orchestrator-lah yang memvalidasi, memeriksa policy, dan mengeksekusi.
"""

from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence

from .registry import ToolContext


class PlannerError(ValueError):
    """Rencana atau input perencana tidak valid."""


@dataclass(frozen=True)
class PlanStep:
    tool: str
    arguments: dict[str, Any] = field(default_factory=dict)
    note: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.tool, str) or not self.tool.strip():
            raise PlannerError("langkah rencana wajib memiliki nama tool")
        if not isinstance(self.arguments, Mapping):
            raise PlannerError("arguments langkah rencana harus berupa objek")

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "PlanStep":
        if not isinstance(data, Mapping):
            raise PlannerError("langkah rencana harus berupa objek")
        tool = data.get("tool")
        if not isinstance(tool, str):
            raise PlannerError("langkah rencana wajib memiliki field 'tool'")
        arguments = data.get("arguments", {})
        if not isinstance(arguments, Mapping):
            raise PlannerError("field 'arguments' harus objek")
        return cls(tool=tool, arguments=dict(arguments), note=str(data.get("note", "")))

    def to_dict(self) -> dict[str, Any]:
        return {"tool": self.tool, "arguments": dict(self.arguments), "note": self.note}


@dataclass(frozen=True)
class Plan:
    steps: list[PlanStep] = field(default_factory=list)
    summary: str = ""
    planner: str = "heuristic"
    needs_input: bool = False
    clarify: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.steps, list) or any(not isinstance(step, PlanStep) for step in self.steps):
            raise PlannerError("steps harus berupa daftar PlanStep")

    @classmethod
    def from_mapping(cls, data: Any) -> "Plan":
        if isinstance(data, list):
            data = {"steps": data}
        if not isinstance(data, Mapping):
            raise PlannerError("rencana JSON harus berupa objek atau daftar langkah")
        steps_raw = data.get("steps", [])
        if not isinstance(steps_raw, list):
            raise PlannerError("field 'steps' harus berupa daftar")
        steps = [PlanStep.from_mapping(item) for item in steps_raw]
        return cls(
            steps=steps,
            summary=str(data.get("summary", "")),
            planner=str(data.get("planner", "json")),
            needs_input=bool(data.get("needs_input", False)),
            clarify=str(data.get("clarify", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "planner": self.planner,
            "needs_input": self.needs_input,
            "clarify": self.clarify,
            "steps": [step.to_dict() for step in self.steps],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class Planner(Protocol):
    name: str

    def plan(self, instruction: str, context: ToolContext) -> Plan: ...


def plan_from_json(data: Any) -> Plan:
    """Bangun Plan dari objek JSON (dipakai CLI ``--plan`` dan pengujian)."""
    return Plan.from_mapping(data)


# ---------------------------------------------------------------------------
# Heuristic planner (deterministik, dwibahasa ID/EN)
# ---------------------------------------------------------------------------

_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:[\\/](?:[\w.\-]+[\\/])*[\w.\-]+"),   # path absolut Windows
    re.compile(r"/(?:[\w.\-]+/)*[\w.\-]+"),                      # path absolut POSIX
    re.compile(r"(?:\.{0,2}/)?(?:[\w.\-]+/)+[\w.\-]+"),          # path relatif dengan garis miring
    re.compile(r"[\w.\-]+\.[\w]{1,8}"),                          # nama berkas dengan ekstensi
)
_PATTERNS = re.compile(r"\"[^\"]*\"|'[^']*'|\S+")

_SYSTEM_KEYWORDS = (
    ("usb", "hardware", "usb"),
    ("paket", "packages", "list"),
    ("package", "packages", "list"),
    ("pacman", "packages", "list"),
    ("service", "services", "status"),
    ("systemd", "services", "status"),
    ("unit", "services", "status"),
    ("proses", "processes", "list"),
    ("process", "processes", "list"),
    ("ps", "processes", "list"),
    ("jaringan", "network", "status"),
    ("network", "network", "status"),
    ("mount", "storage", "mounts"),
    ("storage", "storage", "devices"),
    ("disk", "storage", "devices"),
    ("hardware", "hardware", "summary"),
    ("perangkat", "hardware", "summary"),
    ("lspci", "hardware", "summary"),
    ("lsusb", "hardware", "usb"),
)

_COMMAND_TRIGGERS = ("jalankan", "eksekusi", "run", "execute")
_WRITE_TRIGGERS = ("tulis", "buat file", "create file", "write")
_READ_TRIGGERS = ("baca", "read")
_SEARCH_TRIGGERS = ("cari", "search", "temukan", "find")
_LIST_TRIGGERS = ("daftar", "list", "isi folder", "isi direktori", "ls")


def _tokens(text: str) -> list[str]:
    return _PATTERNS.findall(text)


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _first_path(text: str) -> str | None:
    for pattern in _PATH_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(0)
    return None


def _contains(text: str, *words: str) -> bool:
    lowered = text.lower()
    return any(re.search(rf"\b{re.escape(word)}\b", lowered) for word in words)


class HeuristicPlanner:
    """Perencana deterministik berbasis kata kunci (ID/EN) untuk demo dan offline."""

    name = "heuristic"

    def plan(self, instruction: str, context: ToolContext) -> Plan:
        text = instruction.strip()
        if not text:
            return Plan(summary="instruksi kosong", needs_input=True, clarify="instruksi belum diisi", planner=self.name)
        lowered = text.lower()
        tokens = _tokens(text)

        # 1) Perintah/kommando eksplisit: "jalankan git status"
        for trigger in _COMMAND_TRIGGERS:
            match = re.search(rf"\b{re.escape(trigger)}\b\s+(.+)$", lowered)
            if match:
                return self._command_plan(match.group(1).strip())

        # 2) Inspeksi sistem: "status paket", "info jaringan"
        if _contains(lowered, "status", "info", "periksa", "cek", "check") or any(
            re.search(rf"\b{re.escape(word)}\b", lowered) for word, _c, _o in _SYSTEM_KEYWORDS
        ):
            for word, category, operation in _SYSTEM_KEYWORDS:
                if re.search(rf"\b{re.escape(word)}\b", lowered):
                    step = PlanStep(tool="system.inspect", arguments={"category": category, "operation": operation}, note=f"deteksi kata kunci '{word}'")
                    return Plan(steps=[step], summary=f"periksa {category}.{operation}", planner=self.name)

        # 3) Presentasi
        if _contains(lowered, "presentasi", "pptx", "slide", "presentation"):
            path = _first_path(text) or "presentasi.pptx"
            path = path if path.lower().endswith(".pptx") else path + ".pptx"
            slides = [{"title": self._slide_title(text), "body": ""}]
            step = PlanStep(tool="productivity.pptx", arguments={"path": path, "slides": slides})
            return Plan(steps=[step], summary="buat presentasi", planner=self.name)

        # 4) CSV / spreadsheet
        if _contains(lowered, "csv", "spreadsheet"):
            path = _first_path(text) or "data.csv"
            path = path if path.lower().endswith(".csv") else path + ".csv"
            headers = self._csv_headers(text)
            step = PlanStep(tool="productivity.csv", arguments={"path": path, "headers": headers, "rows": []})
            return Plan(steps=[step], summary="buat csv", planner=self.name)

        # 5) Baca berkas (dicek sebelum pembuatan dokumen agar path .md tidak salah tebak)
        if _contains(lowered, *_READ_TRIGGERS):
            path = _first_path(text)
            if path:
                step = PlanStep(tool="file.read", arguments={"path": path})
                return Plan(steps=[step], summary=f"baca {path}", planner=self.name)

        # 6) Cari berkas
        if _contains(lowered, *_SEARCH_TRIGGERS):
            pattern = self._search_pattern(text, tokens)
            if pattern:
                step = PlanStep(tool="file.search", arguments={"pattern": pattern, "root": "."})
                return Plan(steps=[step], summary=f"cari {pattern}", planner=self.name)

        # 7) Daftar isi direktori
        if _contains(lowered, *_LIST_TRIGGERS):
            path = _first_path(text) or "."
            step = PlanStep(tool="file.list", arguments={"path": path})
            return Plan(steps=[step], summary=f"daftar {path}", planner=self.name)

        # 8) Tulis berkas
        if _contains(lowered, *_WRITE_TRIGGERS):
            return self._write_plan(text)

        # 9) Dokumen markdown (fallback setelah aksi file eksplisit)
        if _contains(lowered, "dokumen", "document", "markdown", "catatan", "laporan", "report", "md"):
            path = _first_path(text) or "dokumen.md"
            path = path if path.lower().endswith(".md") else path + ".md"
            step = PlanStep(
                tool="productivity.markdown",
                arguments={"path": path, "title": self._doc_title(text), "heading": "Ringkasan", "content": text},
            )
            return Plan(steps=[step], summary="buat dokumen markdown", planner=self.name)

        # 10) Tidak dikenali -> minta klarifikasi tanpa eksekusi
        return Plan(
            summary="instruksi belum dapat dipetakan ke tool",
            needs_input=True,
            clarify="coba sebutkan tindakan konkret (mis. 'buat presentasi', 'baca file /etc/hostname', 'jalankan git status')",
            planner=self.name,
        )

    # -- helper ---------------------------------------------------------------

    @staticmethod
    def _command_plan(remainder: str) -> Plan:
        try:
            parts = shlex.split(remainder)
        except ValueError:
            parts = remainder.split()
        if not parts:
            return Plan(summary="perintah kosong", needs_input=True, clarify="perintah belum diisi", planner="heuristic")
        command, args = parts[0], parts[1:]
        step = PlanStep(tool="command.run", arguments={"command": command, "args": args, "execution_mode": "argv"}, note="perintah argv")
        return Plan(steps=[step], summary=f"jalankan {command}", planner="heuristic")

    def _write_plan(self, text: str) -> Plan:
        path = _first_path(text)
        if not path:
            return Plan(summary="path berkas tidak ditemukan", needs_input=True, clarify="sebutkan path berkas yang akan ditulis", planner=self.name)
        content = self._content_after(text, path)
        step = PlanStep(tool="file.write", arguments={"path": path, "content": content})
        return Plan(steps=[step], summary=f"tulis {path}", planner=self.name)

    @staticmethod
    def _content_after(text: str, path: str) -> str:
        index = text.find(path)
        remainder = text[index + len(path):] if index >= 0 else ""
        remainder = re.sub(r"^\s*(berisi|isi|dengan isi|berkaitan|dengan)\s*", "", remainder, flags=re.IGNORECASE)
        return remainder.strip().strip(":-")

    @staticmethod
    def _search_pattern(text: str, tokens: Sequence[str]) -> str | None:
        quoted = re.findall(r"\"([^\"]+)\"|'([^']+)'", text)
        if quoted:
            return next(part for pair in quoted for part in pair if part)
        for token in tokens:
            cleaned = _strip_quotes(token)
            if any(ch in cleaned for ch in "*?") or "." in cleaned:
                return cleaned
        for token in tokens:
            cleaned = _strip_quotes(token)
            if cleaned and not re.search(rf"\b{re.escape(cleaned.lower())}\b", " ".join(_SEARCH_TRIGGERS)):
                return cleaned
        return None

    @staticmethod
    def _slide_title(text: str) -> str:
        candidate = text.strip()
        for prefix in ("buat presentasi", "buat pptx", "presentasi", "pptx", "create presentation", "presentation"):
            candidate = re.sub(rf"^.*?\b{re.escape(prefix)}\b\s*", "", candidate, count=1, flags=re.IGNORECASE)
        return (candidate.strip() or "Slide 1")[:80]

    @staticmethod
    def _doc_title(text: str) -> str:
        candidate = text.strip()
        for prefix in ("buat dokumen", "buat markdown", "buat catatan", "buat laporan", "create document", "document", "markdown"):
            candidate = re.sub(rf"^.*?\b{re.escape(prefix)}\b\s*", "", candidate, count=1, flags=re.IGNORECASE)
        return (candidate.strip() or "Dokumen")[:80]

    @staticmethod
    def _csv_headers(text: str) -> list[str]:
        match = re.search(r"(?:headers?|kolom|columns?)\s*[:=]?\s*([^.;]+)", text, flags=re.IGNORECASE)
        if match:
            parts = [part.strip() for part in re.split(r"[,;]", match.group(1)) if part.strip()]
            if parts:
                return parts
        return ["kolom1", "kolom2"]


_PLANNERS: dict[str, Any] = {"heuristic": HeuristicPlanner}


def get_planner(name: str = "heuristic"):
    """Pabrik perencana. Menjadi titik pasang runtime LLM nyata (mis. 'llm')."""
    key = (name or "heuristic").strip().lower()
    if key in ("", "auto", "heuristic", "stub", "offline"):
        return HeuristicPlanner()
    factory = _PLANNERS.get(key)
    if factory is None:
        raise PlannerError(f"perencana tidak dikenal: {name}; pilihan: {', '.join(sorted(_PLANNERS))}")
    return factory()


def register_planner(name: str, factory: Any) -> None:
    """Daftarkan implementasi perencana baru (mis. runtime LLM) tanpa mengubah CLI."""
    _PLANNERS[name.strip().lower()] = factory


__all__ = [
    "HeuristicPlanner",
    "Plan",
    "PlanStep",
    "Planner",
    "PlannerError",
    "get_planner",
    "plan_from_json",
    "register_planner",
]