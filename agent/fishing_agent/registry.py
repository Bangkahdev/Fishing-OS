"""Tool registry dengan validasi argumen (SRS §3.2 Tool Registry, FR-09/10/34).

Registry menyimpan :class:`ToolSpec` (nama, deskripsi, schema parameter, kelas
risiko, kebutuhan privilege, dan handler). Orchestrator memanggil
:meth:`ToolRegistry.dispatch` yang **selalu** memvalidasi argumen terhadap
schema sebelum menjalankan handler; handler tidak pernah menerima output model
mentah.

Validator argumen adalah subset JSON Schema yang dipakai untuk tool Assistant:
``type`` (object/array/string/integer/number/boolean), ``properties``,
``required``, ``default``, ``enum``, ``items``, ``minimum``/``maximum``,
``minLength``/``maxLength``, dan ``additionalProperties``. Cukup untuk mengunci
kontrak tool tanpa dependensi pihak ketiga.
"""

from __future__ import annotations

import numbers
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from .policy import Risk

VALID_TYPES = ("object", "array", "string", "integer", "number", "boolean")


class ToolValidationError(ValueError):
    """Argumen tool tidak memenuhi schema."""


class ToolNotFound(KeyError):
    """Tool tidak terdaftar pada registry."""


class ToolError(RuntimeError):
    """Handler tool gagal dijalankan."""


@dataclass(frozen=True)
class StepOutcome:
    """Hasil satu langkah tool yang dikembalikan ke orchestrator."""

    ok: bool
    summary: str = ""
    output: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    returncode: int | None = None
    error: str = ""


@dataclass
class ToolContext:
    """Dependensi runtime yang diberikan orchestrator ke handler tool.

    Handler tidak membuat executor sendiri; semua kapabilitas (command, file,
    system, productivity, policy, trace, cancellation) diinjeksi lewat konteks
    agar registry tetap deterministik dan dapat diuji.
    """

    policy: Any
    administrator: Any
    stop: Any
    trace: Any = None
    executor: Any = None
    broker: Any = None
    file_tool: Any = None
    system_tool: Any = None
    working_directory: str | None = None
    dry_run: bool = False
    approved: bool = False
    task_id: str = "orchestrated"
    lab: Any = None

    def emit(self, action: str, parameters: dict[str, Any] | None = None, *, status: str = "ok", note: str = "", perception: str = "tool") -> None:
        if self.trace is not None:
            self.trace.write(
                perception=perception,
                action=action,
                parameters=dict(parameters or {}),
                status=status,
                note=note,
            )


ToolHandler = Callable[[Mapping[str, Any], ToolContext], StepOutcome]
RiskFn = Callable[[Mapping[str, Any], ToolContext], Risk]


@dataclass(frozen=True)
class ToolSpec:
    """Spesifikasi satu tool: kontrak parameter, risiko, dan handler."""

    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    handler: ToolHandler | None = None
    risk: Risk | RiskFn = Risk.LOW
    privilege: str = "user"
    examples: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ToolValidationError("nama tool wajib diisi")
        if self.privilege not in ("user", "elevated"):
            raise ToolValidationError(f"privilege tidak valid: {self.privilege}")
        schema = self.parameters or {}
        if not isinstance(schema, Mapping):
            raise ToolValidationError("parameters harus berupa objek schema")
        if schema.get("type", "object") != "object":
            raise ToolValidationError("schema tool harus bertipe object")
        for prop_name, prop in (schema.get("properties") or {}).items():
            if not isinstance(prop, Mapping):
                raise ToolValidationError(f"properti '{prop_name}' harus objek schema")
            declared = prop.get("type")
            if declared is not None and declared not in VALID_TYPES:
                raise ToolValidationError(f"tipe properti '{prop_name}' tidak valid: {declared}")
        for required_name in schema.get("required", []) or []:
            if required_name not in (schema.get("properties") or {}):
                raise ToolValidationError(f"field wajib '{required_name}' tidak ada di properties")

    def risk_for(self, arguments: Mapping[str, Any], context: ToolContext) -> Risk:
        if callable(self.risk):
            return self.risk(arguments, context)
        return self.risk

    def validate(self, arguments: Mapping[str, Any] | None) -> dict[str, Any]:
        return validate_arguments(self.parameters or {}, dict(arguments or {}))

    def schema_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "risk_default": (self.risk.value if isinstance(self.risk, Risk) else "callable"),
            "privilege": self.privilege,
            "examples": list(self.examples),
        }


def _coerce_type(value: Any, expected: str, location: str) -> Any:
    if expected == "string":
        if not isinstance(value, str):
            raise ToolValidationError(f"{location} harus string")
        return value
    if expected == "integer":
        if isinstance(value, bool) or not isinstance(value, numbers.Integral):
            raise ToolValidationError(f"{location} harus integer")
        return int(value)
    if expected == "number":
        if isinstance(value, bool) or not isinstance(value, numbers.Real):
            raise ToolValidationError(f"{location} harus number")
        return float(value)
    if expected == "boolean":
        if not isinstance(value, bool):
            raise ToolValidationError(f"{location} harus boolean")
        return value
    if expected == "array":
        if not isinstance(value, (list, tuple)):
            raise ToolValidationError(f"{location} harus array")
        return list(value)
    if expected == "object":
        if not isinstance(value, Mapping):
            raise ToolValidationError(f"{location} harus object")
        return dict(value)
    raise ToolValidationError(f"tipe tidak didukung: {expected}")


def _validate_value(value: Any, schema: Mapping[str, Any], location: str) -> Any:
    expected = schema.get("type")
    if expected is not None:
        value = _coerce_type(value, expected, location)
    if "enum" in schema and value not in schema["enum"]:
        raise ToolValidationError(f"{location} harus salah satu dari {schema['enum']}")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < int(schema["minLength"]):
            raise ToolValidationError(f"{location} minimal {schema['minLength']} karakter")
        if "maxLength" in schema and len(value) > int(schema["maxLength"]):
            raise ToolValidationError(f"{location} maksimal {schema['maxLength']} karakter")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise ToolValidationError(f"{location} minimal {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            raise ToolValidationError(f"{location} maksimal {schema['maximum']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < int(schema["minItems"]):
            raise ToolValidationError(f"{location} minimal {schema['minItems']} item")
        if "maxItems" in schema and len(value) > int(schema["maxItems"]):
            raise ToolValidationError(f"{location} maksimal {schema['maxItems']} item")
        if isinstance(schema.get("items"), Mapping):
            value = [
                _validate_value(item, schema["items"], f"{location}[{index}]")
                for index, item in enumerate(value)
            ]
    if isinstance(value, dict) and isinstance(schema.get("properties"), Mapping):
        value = validate_arguments(dict(schema), value, location=location)
    return value


def validate_arguments(
    schema: Mapping[str, Any],
    arguments: Mapping[str, Any],
    *,
    location: str = "arguments",
) -> dict[str, Any]:
    """Validasi argumen terhadap subset JSON Schema dan kembalikan nilai ternormalisasi."""
    if not isinstance(arguments, Mapping):
        raise ToolValidationError(f"{location} harus berupa objek")
    properties = schema.get("properties") or {}
    additional_allowed = bool(schema.get("additionalProperties", True))
    result: dict[str, Any] = {}
    for key, value in arguments.items():
        if key not in properties:
            if not additional_allowed:
                raise ToolValidationError(f"parameter tak dikenal: {key}")
            result[key] = value
            continue
        result[key] = _validate_value(value, properties[key], f"{location}.{key}")
    for required_name in schema.get("required", []) or []:
        if required_name not in result:
            raise ToolValidationError(f"parameter wajib belum diisi: {required_name}")
    for prop_name, prop_schema in properties.items():
        if prop_name not in result and "default" in prop_schema:
            result[prop_name] = prop_schema["default"]
    return result


class ToolRegistry:
    """Registry tool dengan validasi argumen dan dispatch handler."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> ToolSpec:
        if spec.name in self._tools:
            raise ToolValidationError(f"tool sudah terdaftar: {spec.name}")
        if spec.handler is None:
            raise ToolValidationError(f"tool '{spec.name}' tidak memiliki handler")
        self._tools[spec.name] = spec
        return spec

    def get(self, name: str) -> ToolSpec:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFound(name) from exc

    def has(self, name: str) -> bool:
        return name in self._tools

    def names(self) -> list[str]:
        return sorted(self._tools)

    def specs(self) -> list[ToolSpec]:
        return [self._tools[name] for name in self.names()]

    def schemas(self) -> list[dict[str, Any]]:
        return [spec.schema_json() for spec in self.specs()]

    def dispatch(self, name: str, arguments: Mapping[str, Any] | None, context: ToolContext) -> StepOutcome:
        spec = self.get(name)
        validated = spec.validate(arguments)
        assert spec.handler is not None
        try:
            outcome = spec.handler(validated, context)
        except ToolError:
            raise
        except Exception as exc:  # handler tak terduga -> bungkus agar orchestrator menangani
            raise ToolError(f"tool '{name}' gagal: {exc}") from exc
        if not isinstance(outcome, StepOutcome):
            raise ToolError(f"tool '{name}' mengembalikan tipe yang tidak didukung")
        return outcome


__all__ = [
    "Risk",
    "RiskFn",
    "StepOutcome",
    "ToolContext",
    "ToolError",
    "ToolHandler",
    "ToolNotFound",
    "ToolRegistry",
    "ToolSpec",
    "ToolValidationError",
    "VALID_TYPES",
    "validate_arguments",
]