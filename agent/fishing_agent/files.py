"""Tool filesystem lokal dengan validasi path dan perlindungan symlink."""

from __future__ import annotations

import fnmatch
import os
import shutil
import stat
from pathlib import Path
from typing import Iterator


class PathOutsideWorkspace(ValueError):
    """Path berada di luar workspace lab."""


class FileOperationError(ValueError):
    """Operasi filesystem tidak valid atau membutuhkan approval."""


class FileTool:
    """Operasi filesystem lokal; tidak mengirim isi file ke layanan eksternal."""

    def __init__(self, *, max_read_bytes: int = 4 * 1024 * 1024, max_write_bytes: int = 4 * 1024 * 1024) -> None:
        if max_read_bytes < 1 or max_write_bytes < 1:
            raise ValueError("batas ukuran file harus positif")
        self.max_read_bytes = max_read_bytes
        self.max_write_bytes = max_write_bytes

    @staticmethod
    def resolve(path: str | Path, *, base: str | Path | None = None) -> Path:
        candidate = Path(path).expanduser()
        if not candidate.is_absolute():
            candidate = (Path(base) if base is not None else Path.cwd()) / candidate
        # Jangan resolve symlink terakhir: caller harus dapat mendeteksi dan
        # menolak operasi yang tanpa sengaja mengikuti link.
        return Path(os.path.abspath(candidate))

    @staticmethod
    def _reject_symlink(path: Path) -> None:
        if path.is_symlink():
            raise FileOperationError(f"operasi pada symlink ditolak: {path}")

    def _check_size(self, path: Path, limit: int) -> None:
        if path.stat().st_size > limit:
            raise FileOperationError(f"file melebihi batas {limit} byte: {path}")

    def metadata(self, path: str | Path) -> dict[str, object]:
        target = self.resolve(path)
        info = target.lstat()
        return {
            "path": str(target),
            "type": "symlink" if stat.S_ISLNK(info.st_mode) else "directory" if stat.S_ISDIR(info.st_mode) else "file",
            "size": info.st_size,
            "mode": stat.filemode(info.st_mode),
            "modified": info.st_mtime,
        }

    def list(self, path: str | Path = ".") -> list[dict[str, object]]:
        target = self.resolve(path)
        if not target.is_dir():
            raise FileOperationError(f"bukan direktori: {target}")
        return [self.metadata(child) for child in sorted(target.iterdir(), key=lambda item: item.name)]

    def search(self, root: str | Path, pattern: str, *, limit: int = 100) -> list[Path]:
        if not pattern or pattern in (".", "..") or limit < 1:
            raise ValueError("pattern atau limit tidak valid")
        base = self.resolve(root)
        if not base.is_dir():
            raise FileNotFoundError(base)
        result: list[Path] = []
        for path in self._walk(base):
            if fnmatch.fnmatch(path.name, pattern):
                result.append(path)
                if len(result) >= limit:
                    break
        return result

    def read(self, path: str | Path, *, encoding: str = "utf-8") -> str:
        target = self.resolve(path)
        self._reject_symlink(target)
        self._check_size(target, self.max_read_bytes)
        return target.read_text(encoding=encoding)

    def write(self, path: str | Path, content: str, *, overwrite: bool = False, encoding: str = "utf-8") -> Path:
        target = self.resolve(path)
        if len(content.encode(encoding)) > self.max_write_bytes:
            raise FileOperationError("content melebihi batas ukuran write")
        if target.exists() and not overwrite:
            raise FileOperationError(f"target sudah ada; approval overwrite diperlukan: {target}")
        if target.exists():
            self._reject_symlink(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding=encoding)
        return target

    def copy(self, source: str | Path, destination: str | Path, *, overwrite: bool = False) -> Path:
        src, dst = self.resolve(source), self.resolve(destination)
        self._reject_symlink(src)
        if dst.exists() and not overwrite:
            raise FileOperationError(f"target sudah ada; approval overwrite diperlukan: {dst}")
        if dst.exists():
            self._reject_symlink(dst)
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=overwrite)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        return dst

    def move(self, source: str | Path, destination: str | Path, *, overwrite: bool = False) -> Path:
        src, dst = self.resolve(source), self.resolve(destination)
        self._reject_symlink(src)
        if dst.exists() and not overwrite:
            raise FileOperationError(f"target sudah ada; approval overwrite diperlukan: {dst}")
        if dst.exists():
            self._reject_symlink(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return dst

    def delete(self, path: str | Path, *, approved: bool = False) -> None:
        target = self.resolve(path)
        if not approved:
            raise FileOperationError("delete membutuhkan approval eksplisit")
        self._reject_symlink(target)
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()

    @staticmethod
    def _walk(root: Path) -> Iterator[Path]:
        for current, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [name for name in dirs if not (Path(current) / name).is_symlink()]
            yield from (Path(current) / name for name in files if not (Path(current) / name).is_symlink())


def resolve_within(workspace: str | Path, candidate: str | Path) -> Path:
    root = Path(workspace).resolve()
    target = (root / candidate).resolve() if not Path(candidate).is_absolute() else Path(candidate).resolve()
    if target != root and root not in target.parents:
        raise PathOutsideWorkspace(f"{target} berada di luar workspace {root}")
    return target


def search(
    workspace: str | Path,
    pattern: str,
    *,
    limit: int = 100,
    include_dirs: bool = False,
) -> list[Path]:
    if limit < 1:
        raise ValueError("limit minimal 1")
    if not pattern or pattern in (".", ".."):
        raise ValueError("pola pencarian tidak valid")
    root = Path(workspace).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"workspace tidak ditemukan: {root}")
    results: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not include_dirs and not path.is_file():
            continue
        if path.is_symlink():
            continue
        if fnmatch.fnmatch(path.name, pattern):
            results.append(path.relative_to(root))
            if len(results) >= limit:
                break
    return results
