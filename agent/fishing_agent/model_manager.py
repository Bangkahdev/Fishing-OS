"""Manajer model LLM/VLM lokal: manifest, verifikasi checksum, muat/bongkar, dan status OOM/timeout (FR-24, NFR-01/04/05/06).

Manajer ini adalah *registry* model saja; runtime inferensi akhir (nama model, kuantisasi, strategi offload) belum dikunci oleh SRS dan diimplementasikan nanti melalui prototipe.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ModelError(RuntimeError):
    """Kesalahan manajemen model."""


class ModelNotFound(ModelError):
    """Model tidak terdaftar."""


class ModelVerificationFailed(ModelError):
    """Checksum berkas model tidak cocok dengan manifest."""


MANIFEST_FIELDS = (
    "id",
    "version",
    "checksum",
)

OPTIONAL_FIELDS = (
    "checksum_algorithm",
    "size",
    "source",
    "license",
    "quantization",
    "context_length",
)

LOADED = "loaded"
UNLOADED = "unloaded"
MISSING = "missing"
FAILED = "failed"


@dataclass(frozen=True)
class ModelManifest:
    id: str
    version: str
    checksum: str
    checksum_algorithm: str = "sha256"
    size: int | None = None
    source: str = ""
    license: str = ""
    quantization: str = ""
    context_length: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelManifest:
        for field_name in MANIFEST_FIELDS:
            if field_name not in data:
                raise ModelError(f"manifest model harus memiliki field '{field_name}'")
        extra = {
            k: v
            for k, v in data.items()
            if k not in MANIFEST_FIELDS and k not in OPTIONAL_FIELDS
        }
        return cls(
            id=str(data["id"]),
            version=str(data["version"]),
            checksum=str(data["checksum"]),
            checksum_algorithm=str(data.get("checksum_algorithm", "sha256")),
            size=data.get("size"),
            source=str(data.get("source", "")),
            license=str(data.get("license", "")),
            quantization=str(data.get("quantization", "")),
            context_length=data.get("context_length"),
            metadata=extra,
        )

    def verify(self, path: str | Path) -> bool:
        target = Path(path)
        if not target.is_file():
            return False
        algorithm = (self.checksum_algorithm or "sha256").lower()
        try:
            hasher = hashlib.new(algorithm)
        except ValueError:
            raise ModelError(f"algoritma checksum tidak didukung: {algorithm}")
        with target.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(chunk)
        return hasher.hexdigest().lower() == self.checksum.lower()


class ModelManager:
    """Pendaftaran, verifikasi, dan status muatan model lokal."""

    def __init__(self, models_dir: str | Path) -> None:
        self.models_dir = Path(models_dir)
        self._manifests: dict[str, ModelManifest] = {}
        self._status: dict[str, str] = {}
        self._oom = False

    @property
    def oom(self) -> bool:
        return self._oom

    def set_oom(self, value: bool) -> None:
        self._oom = bool(value)

    def register(self, manifest: ModelManifest | dict[str, Any]) -> None:
        if isinstance(manifest, dict):
            manifest = ModelManifest.from_dict(manifest)
        self._manifests[manifest.id] = manifest
        self._status.setdefault(manifest.id, UNLOADED)

    def list_models(self) -> list[str]:
        return sorted(self._manifests)

    def get_model(self, model_id: str) -> ModelManifest | None:
        return self._manifests.get(model_id)

    def model_path(self, model_id: str) -> Path:
        manifest = self.get_model(model_id)
        if manifest is None:
            raise ModelNotFound(model_id)
        return self.models_dir / f"{model_id}-{manifest.version}"

    def verify(self, model_id: str) -> bool:
        manifest = self.get_model(model_id)
        if manifest is None:
            return False
        return manifest.verify(self.model_path(model_id))

    def load(self, model_id: str) -> str:
        if self._oom:
            self._status[model_id] = FAILED
            raise ModelError(f"memuat {model_id} dibatalkan: status OOM")
        manifest = self.get_model(model_id)
        if manifest is None:
            raise ModelNotFound(model_id)
        target = self.model_path(model_id)
        if not target.is_file():
            self._status[model_id] = MISSING
            raise ModelError(f"berkas model tidak ditemukan: {target}")
        if not self.verify(model_id):
            self._status[model_id] = FAILED
            raise ModelVerificationFailed(model_id)
        self._status[model_id] = LOADED
        return LOADED

    def unload(self, model_id: str) -> str:
        if model_id not in self._manifests:
            raise ModelNotFound(model_id)
        self._status[model_id] = UNLOADED
        return UNLOADED

    def status(self, model_id: str) -> str:
        if model_id not in self._manifests:
            raise ModelNotFound(model_id)
        return self._status.get(model_id, UNLOADED)


def load_manifests_from_file(path: str | Path) -> list[ModelManifest]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("models", [])
    if not isinstance(data, list):
        raise ModelError("berkas manifest harus berupa daftar atau objek {'models': [...]}")
    return [ModelManifest.from_dict(item) for item in data]


__all__ = [
    "FAILED",
    "LOADED",
    "MISSING",
    "UNLOADED",
    "ModelError",
    "ModelManifest",
    "ModelManager",
    "ModelNotFound",
    "ModelVerificationFailed",
    "load_manifests_from_file",
]
