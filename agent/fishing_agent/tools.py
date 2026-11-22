"""Tool bawaan Assistant yang membungkus modul command/file/system/productivity.

Setiap handler menerima argumen **tervalidasi** dari :class:`ToolRegistry` dan
konteks runtime (:class:`ToolContext`); handler tidak pernah menerima output
model mentah dan tidak membuat executor sendiri. Risiko tiap tool diturunkan
dari :class:`~fishing_agent.policy.PolicyGate` yang sama agar klasifikasi
berdampak tinggi (mis. ``mkfs``, ``rm -rf``) tetap konsisten lintas jalur.
"""

from __future__ import annotations

import json
from typing import Any, Mapping

from .broker import BrokerError, PrivilegedRequest
from .command import CommandRequest
from .policy import Risk
from .productivity import create_csv, create_markdown, create_pptx
from .registry import StepOutcome, ToolContext, ToolError, ToolRegistry, ToolSpec
from .system import SystemOperation


def _require(value: Any, name: str) -> Any:
    if value is None:
        raise ToolError(f"tool membutuhkan konteks '{name}' yang tidak tersedia")
    return value


def _command_risk(arguments: Mapping[str, Any], context: ToolContext) -> Risk:
    request = _build_command_request(arguments)
    return context.policy.risk(request)


def _build_command_request(arguments: Mapping[str, Any]) -> CommandRequest:
    args = arguments.get("args") or []
    return CommandRequest(
        command=str(arguments["command"]),
        args=tuple(str(item) for item in args),
        execution_mode=str(arguments.get("execution_mode", "argv")),
        privilege=str(arguments.get("privilege", "user")),
        timeout=arguments.get("timeout", 60.0),
    )


def _cmd_command(arguments: Mapping[str, Any], context: ToolContext) -> StepOutcome:
    request = _build_command_request(arguments)
    if request.privilege == "elevated":
        broker = _require(context.broker, "broker")
        try:
            result = broker.execute(
                PrivilegedRequest(
                    command=request.command,
                    args=tuple(request.args),
                    working_directory=request.working_directory,
                    timeout=request.timeout,
                    reason="tool command.run elevated",
                    task_id=context.task_id,
                ),
                approved=context.approved,
            )
        except BrokerError as exc:
            raise ToolError(str(exc)) from exc
        summary = result.summary or f"exit={result.returncode} cancelled={result.cancelled}"
        return StepOutcome(
            ok=result.ok,
            summary=summary,
            output="\n".join(part for part in (result.stdout, result.stderr) if part),
            data={
                "returncode": result.returncode,
                "timed_out": result.timed_out,
                "cancelled": result.cancelled,
                "command": request.command,
                "args": list(request.args),
                "via": "privilege-broker",
            },
            returncode=result.returncode,
        )
    executor = _require(context.executor, "executor")
    result = executor.execute(request)
    summary = f"exit={result.returncode} timed_out={result.timed_out} truncated={result.truncated}"
    return StepOutcome(
        ok=result.returncode == 0,
        summary=summary,
        output="\n".join(part for part in (result.stdout, result.stderr) if part),
        data={
            "returncode": result.returncode,
            "timed_out": result.timed_out,
            "truncated": result.truncated,
            "cancelled": result.cancelled,
            "command": request.command,
            "args": list(request.args),
        },
        returncode=result.returncode,
    )


def _cmd_file_list(arguments: Mapping[str, Any], context: ToolContext) -> StepOutcome:
    tool = _require(context.file_tool, "file_tool")
    entries = tool.list(str(arguments.get("path", ".")))
    return StepOutcome(ok=True, summary=f"{len(entries)} entri", data={"entries": entries}, output=json.dumps(entries, ensure_ascii=False))


def _cmd_file_read(arguments: Mapping[str, Any], context: ToolContext) -> StepOutcome:
    tool = _require(context.file_tool, "file_tool")
    content = tool.read(str(arguments["path"]))
    return StepOutcome(ok=True, summary=f"{len(content)} karakter", output=content, data={"path": str(arguments["path"])})


def _cmd_file_search(arguments: Mapping[str, Any], context: ToolContext) -> StepOutcome:
    tool = _require(context.file_tool, "file_tool")
    hits = [str(path) for path in tool.search(str(arguments.get("root", ".")), str(arguments["pattern"]), limit=int(arguments.get("limit", 100)))]
    return StepOutcome(ok=True, summary=f"{len(hits)} berkas cocok", data={"matches": hits}, output="\n".join(hits))


def _cmd_file_write(arguments: Mapping[str, Any], context: ToolContext) -> StepOutcome:
    tool = _require(context.file_tool, "file_tool")
    target = tool.write(str(arguments["path"]), str(arguments["content"]), overwrite=context.approved)
    return StepOutcome(ok=True, summary=f"tersimpan: {target}", data={"path": str(target)})


def _cmd_file_delete(arguments: Mapping[str, Any], context: ToolContext) -> StepOutcome:
    tool = _require(context.file_tool, "file_tool")
    tool.delete(str(arguments["path"]), approved=context.approved)
    return StepOutcome(ok=True, summary=f"dihapus: {arguments['path']}", data={"path": str(arguments["path"])})


_SYSTEM_READ_OPS = {
    "packages": {"list", "search"},
    "services": {"status"},
    "processes": {"list", "inspect"},
    "network": {"status", "routes", "interfaces"},
    "storage": {"devices", "mounts"},
    "hardware": {"summary", "usb"},
}


def _cmd_system_inspect(arguments: Mapping[str, Any], context: ToolContext) -> StepOutcome:
    system = _require(context.system_tool, "system_tool")
    category = str(arguments["category"])
    operation = str(arguments["operation"])
    allowed = _SYSTEM_READ_OPS.get(category)
    if allowed is None:
        raise ToolError(f"kategori sistem tidak didukung: {category}")
    if operation not in allowed:
        raise ToolError(f"operasi '{operation}' bukan operasi baca; gunakan tool command untuk mutasi")
    extra = tuple(str(item) for item in (arguments.get("args") or []))
    result = system.run(SystemOperation(category, operation, extra, privilege="user"))
    return StepOutcome(
        ok=result.returncode == 0,
        summary=f"{category}.{operation} exit={result.returncode}",
        output=result.stdout or result.stderr,
        data={"category": category, "operation": operation, "returncode": result.returncode},
        returncode=result.returncode,
    )


def _cmd_productivity_markdown(arguments: Mapping[str, Any], context: ToolContext) -> StepOutcome:
    heading = str(arguments.get("heading", "Ringkasan"))
    content = str(arguments.get("content", ""))
    target = create_markdown(
        str(arguments["path"]),
        str(arguments.get("title", "Fishing OS")),
        [(heading, content)],
        overwrite=context.approved,
    )
    return StepOutcome(ok=True, summary=f"dokumen dibuat: {target}", data={"path": str(target)})


def _cmd_productivity_pptx(arguments: Mapping[str, Any], context: ToolContext) -> StepOutcome:
    slides = arguments.get("slides") or []
    normalized = [
        {"title": str(item.get("title", f"Slide {index}")), "body": str(item.get("body", ""))}
        if isinstance(item, Mapping)
        else {"title": f"Slide {index}", "body": str(item)}
        for index, item in enumerate(slides, start=1)
    ]
    target = create_pptx(str(arguments["path"]), normalized, overwrite=context.approved)
    return StepOutcome(ok=True, summary=f"presentasi dibuat: {target}", data={"path": str(target), "slides": len(normalized)})


def _cmd_productivity_csv(arguments: Mapping[str, Any], context: ToolContext) -> StepOutcome:
    headers = [str(item) for item in (arguments.get("headers") or [])]
    rows = [list(row) for row in (arguments.get("rows") or [])]
    target = create_csv(str(arguments["path"]), headers, rows, overwrite=context.approved)
    return StepOutcome(ok=True, summary=f"csv dibuat: {target}", data={"path": str(target)})


def _risk_medium(arguments: Mapping[str, Any], context: ToolContext) -> Risk:
    return Risk.MEDIUM


def _risk_high(arguments: Mapping[str, Any], context: ToolContext) -> Risk:
    return Risk.HIGH


def _string_array(**schema: Any) -> dict[str, Any]:
    return {"type": "array", "items": {"type": "string"}, **schema}


def register_default_tools(registry: ToolRegistry) -> ToolRegistry:
    """Daftarkan tool bawaan command/file/system/productivity ke registry."""
    registry.register(
        ToolSpec(
            name="command.run",
            description="Jalankan command lokal melalui executor (argv default; shell/script/interactive bila diminta).",
            parameters={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "minLength": 1},
                    "args": _string_array(),
                    "execution_mode": {"type": "string", "enum": ["argv", "shell", "script", "interactive"], "default": "argv"},
                    "privilege": {"type": "string", "enum": ["user", "elevated"], "default": "user"},
                    "timeout": {"type": "number", "minimum": 0.1, "default": 60.0},
                },
                "required": ["command"],
                "additionalProperties": False,
            },
            handler=_cmd_command,
            risk=_command_risk,
            examples=("command.run {command: 'git', args: ['status']}",),
        )
    )
    registry.register(
        ToolSpec(
            name="file.list",
            description="Daftar isi direktori lokal.",
            parameters={"type": "object", "properties": {"path": {"type": "string", "default": "."}}, "additionalProperties": False},
            handler=_cmd_file_list,
            risk=Risk.LOW,
        )
    )
    registry.register(
        ToolSpec(
            name="file.read",
            description="Baca berkas teks lokal.",
            parameters={"type": "object", "properties": {"path": {"type": "string", "minLength": 1}}, "required": ["path"], "additionalProperties": False},
            handler=_cmd_file_read,
            risk=Risk.LOW,
        )
    )
    registry.register(
        ToolSpec(
            name="file.search",
            description="Cari berkas berdasarkan pola (fnmatch) di bawah root.",
            parameters={
                "type": "object",
                "properties": {"root": {"type": "string", "default": "."}, "pattern": {"type": "string", "minLength": 1}, "limit": {"type": "integer", "minimum": 1, "default": 100}},
                "required": ["pattern"],
                "additionalProperties": False,
            },
            handler=_cmd_file_search,
            risk=Risk.LOW,
        )
    )
    registry.register(
        ToolSpec(
            name="file.write",
            description="Tulis berkas teks (overwrite butuh approval).",
            parameters={
                "type": "object",
                "properties": {"path": {"type": "string", "minLength": 1}, "content": {"type": "string"}},
                "required": ["path", "content"],
                "additionalProperties": False,
            },
            handler=_cmd_file_write,
            risk=_risk_medium,
        )
    )
    registry.register(
        ToolSpec(
            name="file.delete",
            description="Hapus berkas/direktori (berisiko tinggi; wajib approval).",
            parameters={"type": "object", "properties": {"path": {"type": "string", "minLength": 1}}, "required": ["path"], "additionalProperties": False},
            handler=_cmd_file_delete,
            risk=_risk_high,
        )
    )
    registry.register(
        ToolSpec(
            name="system.inspect",
            description="Periksa kapabilitas sistem (paket, service, proses, jaringan, storage, hardware) tanpa mutasi.",
            parameters={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["packages", "services", "processes", "network", "storage", "hardware"]},
                    "operation": {"type": "string"},
                    "args": _string_array(),
                },
                "required": ["category", "operation"],
                "additionalProperties": False,
            },
            handler=_cmd_system_inspect,
            risk=Risk.LOW,
        )
    )
    registry.register(
        ToolSpec(
            name="productivity.markdown",
            description="Buat dokumen Markdown lokal.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "minLength": 1},
                    "title": {"type": "string", "default": "Fishing OS"},
                    "heading": {"type": "string", "default": "Ringkasan"},
                    "content": {"type": "string", "default": ""},
                },
                "required": ["path"],
                "additionalProperties": False,
            },
            handler=_cmd_productivity_markdown,
            risk=_risk_medium,
        )
    )
    registry.register(
        ToolSpec(
            name="productivity.pptx",
            description="Buat presentasi PPTX (OOXML) lokal.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "minLength": 1},
                    "slides": {"type": "array", "items": {"type": "object"}, "minItems": 1},
                },
                "required": ["path", "slides"],
                "additionalProperties": False,
            },
            handler=_cmd_productivity_pptx,
            risk=_risk_medium,
        )
    )
    registry.register(
        ToolSpec(
            name="productivity.csv",
            description="Buat berkas CSV lokal.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "minLength": 1},
                    "headers": _string_array(),
                    "rows": {"type": "array", "items": {"type": "array"}},
                },
                "required": ["path", "headers"],
                "additionalProperties": False,
            },
            handler=_cmd_productivity_csv,
            risk=_risk_medium,
        )
    )
    return registry


__all__ = ["register_default_tools"]