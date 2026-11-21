"""Audit isi artefak distribusi: Assistant harus tidak ada pada Live ISO (SRS §9.5, AC-01, BB-04).

Audit dilakukan pada direktori yang berisi isi Live ISO (ekstrak terlebih dahulu
dari berkas ISO, mis. dengan xorriso/7z), bukan pada berkas ISO mentah.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AuditFinding:
    path: str
    reason: str


# Pola jalur yang menunjukkan komponen Assistant menurut SRS v1.2 §9.5.
FORBIDDEN_PREFIXES = (
    "usr/bin/fishing-assistant",
    "usr/bin/assistant",
    "usr/lib/fishing-assistant",
    "usr/libexec/fishing-assistant",
    "usr/share/applications/*assistant*",
    "usr/share/fishing-assistant",
    "usr/share/icons/*assistant*",
    "usr/share/models/assistant",
    "usr/share/models/*-assistant",
    "etc/fishing-assistant",
    "var/lib/fishing-assistant",
    "usr/lib/systemd/user/*assistant*",
    "etc/systemd/user/*assistant*",
    "usr/share/dbus-1/services/*assistant*",
)

FORBIDDEN_EXACT_NAMES = (
    "fishing-assistant",
    "assistant",
    "fishing-ai-assistant",
    "fishing-ai",
)


def _matches_prefix(relative: str, prefix: str) -> bool:
    if "*" not in prefix:
        return relative == prefix or relative.startswith(prefix + "/")
    head, _, tail = prefix.partition("*")
    tail = tail.rstrip("*")
    if not tail:
        return relative.startswith(head)
    return relative.startswith(head) and tail in relative[len(head):]


def audit_tree(root: str | Path) -> list[AuditFinding]:
    """Skema berkas di bawah root; kembalikan daftar temuan komponen Assistant."""
    target = Path(root).resolve()
    if not target.is_dir():
        raise FileNotFoundError(f"direktori artefak tidak ditemukan: {target}")
    findings: list[AuditFinding] = []
    for path in sorted(target.rglob("*")):
        relative = path.relative_to(target).as_posix()
        for prefix in FORBIDDEN_PREFIXES:
            if _matches_prefix(relative, prefix):
                findings.append(AuditFinding(relative, f"komponen Assistant terlarang: {relative}"))
                break
        if path.is_file() and path.name in FORBIDDEN_EXACT_NAMES:
            findings.append(AuditFinding(relative, f"berkas Assistant terlarang: {relative}"))
    return findings


def audit_report(root: str | Path) -> str:
    findings = audit_tree(root)
    lines = ["Audit Live ISO - komponen Assistant"]
    lines.append(f"Akar artefak: {Path(root).resolve()}")
    lines.append(f"Jumlah temuan: {len(findings)}")
    if findings:
        lines.append("Hasil: GAGAL - Live ISO ikut membawa komponen Assistant")
        for finding in findings:
            lines.append(f"  - {finding.path}: {finding.reason}")
    else:
        lines.append("Hasil: LULUS - tidak ditemukan komponen Assistant")
    return "\n".join(lines)


__all__ = ["AuditFinding", "audit_report", "audit_tree"]
