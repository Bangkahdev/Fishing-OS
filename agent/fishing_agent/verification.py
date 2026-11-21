"""Verifikasi pasca-aksi: bandingkan state UI sebelum dan sesudah aksi (FR-18)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class VerificationFailed(RuntimeError):
    """Verifikasi gagal; state UI tidak sesuai harapan setelah aksi."""


@dataclass(frozen=True)
class VerificationResult:
    passed: bool
    before: dict[str, Any]
    after: dict[str, Any]
    note: str = ""
    fields: tuple[str, ...] = ("role", "name", "state")


def verify_elements(
    before: dict[str, Any],
    after: dict[str, Any],
    *,
    fields: tuple[str, ...] = ("role", "name", "state"),
    expected_change: dict[str, Any] | None = None,
) -> VerificationResult:
    """Kembalikan hasil verifikasi.

    ``expected_change`` menandai field yang berubah sengaja (mis. state tombol
    berubah dari "normal" ke "pressed"); selain itu field lain harus sama.
    """
    expected_change = expected_change or {}
    mismatches: list[str] = []
    for field in fields:
        if field in expected_change:
            if before.get(field) == after.get(field):
                mismatches.append(f"{field} tidak berubah meski diharapkan")
            continue
        if before.get(field) != after.get(field):
            mismatches.append(f"{field} berubah tidak terduga: {before.get(field)!r} -> {after.get(field)!r}")
    passed = not mismatches
    note = "; ".join(mismatches) if mismatches else "state diverifikasi sesuai harapan"
    return VerificationResult(
        passed=passed,
        before=dict(before),
        after=dict(after),
        note=note,
        fields=fields,
    )


def require_verified(result: VerificationResult) -> None:
    if not result.passed:
        raise VerificationFailed(result.note)


__all__ = ["VerificationFailed", "VerificationResult", "require_verified", "verify_elements"]
