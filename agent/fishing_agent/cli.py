"""CLI fishing-agent: control plane, kapabilitas, dan model lokal."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from .config import LAB_ENV, LabError, LabPaths
from .command import CommandExecutor, CommandRequest
from .executor import (
    ActionError,
    ActionExecutor,
    BackendUnavailable,
    load_actions,
    select_backend,
)
from .files import FileOperationError, FileTool, PathOutsideWorkspace, search
from .model_manager import ModelError, ModelManager, load_manifests_from_file
from .stop import StopController, StopRequested
from .trace import TraceWriter
from .policy import AdministratorMode, PolicyGate
from .system import SystemOperation, SystemTool, SystemToolError
from .productivity import ProductivityError, create_csv, create_markdown, create_pptx

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_STOPPED = 130


def _lab(args: argparse.Namespace) -> LabPaths:
    return LabPaths.from_env(args.lab)


def _cmd_init(args: argparse.Namespace) -> int:
    lab = _lab(args).ensure()
    print(f"lab: {lab.root}")
    for name in ("models", "runtime", "workspace", "logs"):
        print(f"  {name}/")
    return EXIT_OK


def _cmd_search(args: argparse.Namespace) -> int:
    lab = _lab(args)
    hits = search(lab.workspace, args.pattern, limit=args.limit)
    for hit in hits:
        print(hit)
    if not hits:
        print("tidak ada berkas cocok", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK


def _cmd_stop(args: argparse.Namespace) -> int:
    lab = _lab(args).ensure()
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lab.stop_file.write_text(f"stop requested at {stamp}\n", encoding="utf-8")
    print(f"stop file ditulis: {lab.stop_file}")
    return EXIT_OK


def _cmd_run(args: argparse.Namespace) -> int:
    lab = _lab(args).ensure()
    actions = load_actions(args.script)
    backend = select_backend(args.backend, dry_run=args.dry_run)
    stop = StopController(lab.stop_file)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    trace_path = lab.logs / f"session-{stamp}.jsonl"
    with TraceWriter(trace_path) as trace:
        executor = ActionExecutor(
            backend,
            trace,
            stop,
            pacing=args.pacing,
            max_steps=args.max_steps,
            perception=args.perception,
        )
        stop.install_handlers()
        print(f"backend: {backend.name} | trace: {trace_path}")
        try:
            executed = executor.run(actions)
        finally:
            stop.restore_handlers()
    print(f"selesai: {executed} aksi")
    return EXIT_OK


def _cmd_command(args: argparse.Namespace) -> int:
    """Jalankan command terstruktur; password selalu ditangani native sudo."""
    lab = _lab(args).ensure()
    request_data = json.loads(args.request) if args.request else {
        "command": args.command,
        "args": args.args,
        "execution_mode": args.mode,
        "privilege": args.privilege,
        "timeout": args.timeout,
    }
    request = CommandRequest.from_mapping(request_data)
    administrator = AdministratorMode()
    if args.enable_admin:
        import subprocess

        result = subprocess.run(["sudo", "-v"], check=False)
        if result.returncode != 0:
            print("autentikasi Administrator Mode gagal", file=sys.stderr)
            return EXIT_ERROR
        administrator.enable(args.admin_duration)
    gate = PolicyGate(administrator)
    task_id = args.task_id
    if args.approve:
        gate.approve(task_id)
    gate.authorize(task_id, request)
    stop = StopController(lab.stop_file)
    executor = CommandExecutor(stop)
    result = executor.execute(request)
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    print(
        f"exit={result.returncode} timed_out={result.timed_out} "
        f"cancelled={result.cancelled} truncated={result.truncated}",
        file=sys.stderr,
    )
    return EXIT_OK if result.returncode == 0 else EXIT_ERROR


def _cmd_file(args: argparse.Namespace) -> int:
    """Expose filesystem operations with explicit overwrite/delete approval."""
    tool = FileTool(max_read_bytes=args.max_bytes, max_write_bytes=args.max_bytes)
    if args.operation == "list":
        print(json.dumps(tool.list(args.path), ensure_ascii=False, indent=2))
    elif args.operation == "metadata":
        print(json.dumps(tool.metadata(args.path), ensure_ascii=False, indent=2))
    elif args.operation == "search":
        if not args.pattern:
            raise ValueError("file search membutuhkan --pattern")
        for path in tool.search(args.path, args.pattern, limit=args.limit):
            print(path)
    elif args.operation == "read":
        print(tool.read(args.path), end="")
    elif args.operation == "write":
        if args.content is None:
            raise ValueError("file write membutuhkan content")
        print(tool.write(args.path, args.content, overwrite=args.approved))
    elif args.operation == "copy":
        if not args.source or not args.destination:
            raise ValueError("file copy membutuhkan --source dan --destination")
        print(tool.copy(args.source, args.destination, overwrite=args.approved))
    elif args.operation == "move":
        if not args.source or not args.destination:
            raise ValueError("file move membutuhkan --source dan --destination")
        print(tool.move(args.source, args.destination, overwrite=args.approved))
    elif args.operation == "delete":
        tool.delete(args.path, approved=args.approved)
    else:  # pragma: no cover - argparse membatasi pilihan
        raise ValueError(f"operasi file tidak dikenal: {args.operation}")
    return EXIT_OK


def _cmd_system(args: argparse.Namespace) -> int:
    lab = _lab(args).ensure()
    administrator = AdministratorMode()
    if args.enable_admin:
        import subprocess

        if subprocess.run(["sudo", "-v"], check=False).returncode != 0:
            print("autentikasi Administrator Mode gagal", file=sys.stderr)
            return EXIT_ERROR
        administrator.enable(args.admin_duration)
    gate = PolicyGate(administrator)
    if args.approve:
        gate.approve(args.task_id)
    stop = StopController(lab.stop_file)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    trace_path = lab.logs / f"system-{stamp}.jsonl"
    with TraceWriter(trace_path) as trace:
        executor = CommandExecutor(stop, trace)

        def execute(request: CommandRequest):
            gate.authorize(args.task_id, request)
            return executor.execute(request)

        result = SystemTool(execute).run(
            SystemOperation(args.category, args.operation, tuple(args.args))
        )
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    print(f"exit={result.returncode} trace={trace_path}", file=sys.stderr)
    return EXIT_OK if result.returncode == 0 else EXIT_ERROR


def _cmd_productivity(args: argparse.Namespace) -> int:
    if args.kind == "markdown":
        sections = [(args.heading, args.content)]
        target = create_markdown(args.path, args.title, sections, overwrite=args.approved)
    elif args.kind == "csv":
        rows = json.loads(args.rows)
        if not isinstance(rows, list):
            raise ProductivityError("--rows harus berupa JSON array")
        target = create_csv(
            args.path,
            [item.strip() for item in args.headers.split(",")],
            rows,
            overwrite=args.approved,
        )
    else:
        slides = json.loads(args.slides)
        if not isinstance(slides, list):
            raise ProductivityError("--slides harus berupa JSON array")
        target = create_pptx(args.path, slides, overwrite=args.approved)
    print(target)
    return EXIT_OK


def _cmd_model(args: argparse.Namespace) -> int:
    lab = _lab(args).ensure()
    manager = ModelManager(lab.models)
    for manifest in load_manifests_from_file(args.manifest):
        manager.register(manifest)
    if args.operation == "list":
        for model_id in manager.list_models():
            print(f"{model_id}\t{manager.status(model_id)}")
        return EXIT_OK
    if not args.model_id:
        raise ValueError(f"model {args.operation} membutuhkan model_id")
    if args.operation == "verify":
        ok = manager.verify(args.model_id)
        print("checksum cocok" if ok else "checksum tidak cocok")
        return EXIT_OK if ok else EXIT_ERROR
    if args.operation == "load":
        print(manager.load(args.model_id))
    elif args.operation == "unload":
        print(manager.unload(args.model_id))
    else:
        print(manager.status(args.model_id))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fishing-agent",
        description="Asisten computer-use lokal Fishing OS.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="buat struktur lab portabel")
    init.add_argument("--lab", help=f"akar lab (default: ${LAB_ENV})")
    init.set_defaults(func=_cmd_init)

    find = sub.add_parser("search", help="cari berkas di workspace lab")
    find.add_argument("pattern", help="pola nama berkas, mis. '*.md'")
    find.add_argument("--lab", help=f"akar lab (default: ${LAB_ENV})")
    find.add_argument("--limit", type=int, default=50)
    find.set_defaults(func=_cmd_search)

    run = sub.add_parser("run", help="jalankan skrip aksi dengan trace")
    run.add_argument("--script", required=True, help="berkas JSON berisi daftar aksi")
    run.add_argument("--lab", help=f"akar lab (default: ${LAB_ENV})")
    run.add_argument("--backend", help="x11 | wayland | dry-run (default: env/auto)")
    run.add_argument("--dry-run", action="store_true", help="jangan sentuh input nyata")
    run.add_argument("--pacing", type=float, default=0.4, help="jeda antar aksi (detik)")
    run.add_argument("--max-steps", type=int, default=50)
    run.add_argument("--perception", default="sesi desktop aktif")
    run.set_defaults(func=_cmd_run)

    command = sub.add_parser("command", help="jalankan command lokal melalui kontrak executor")
    command.add_argument("command", nargs="?", help="executable atau command shell")
    command.add_argument("args", nargs="*", help="argumen terpisah (mode argv)")
    command.add_argument("--request", help="objek JSON CommandRequest")
    command.add_argument("--lab", help=f"akar lab (default: ${LAB_ENV})")
    command.add_argument("--mode", choices=("argv", "shell", "script", "interactive"), default="argv")
    command.add_argument("--privilege", choices=("user", "elevated"), default="user")
    command.add_argument("--timeout", type=float, default=60.0)
    command.add_argument("--task-id", default="cli-task")
    command.add_argument("--approve", action="store_true", help="setujui task untuk operasi berisiko tinggi")
    command.add_argument("--enable-admin", action="store_true", help="autentikasi melalui sudo -v")
    command.add_argument("--admin-duration", type=float, default=900.0)
    command.set_defaults(func=_cmd_command)

    file_parser = sub.add_parser("file", help="kelola filesystem lokal melalui FileTool")
    file_parser.add_argument(
        "operation",
        choices=("list", "metadata", "search", "read", "write", "copy", "move", "delete"),
    )
    file_parser.add_argument("path", nargs="?", default=".")
    file_parser.add_argument("content", nargs="?")
    file_parser.add_argument("--source")
    file_parser.add_argument("--destination")
    file_parser.add_argument("--pattern")
    file_parser.add_argument("--limit", type=int, default=100)
    file_parser.add_argument("--max-bytes", type=int, default=4 * 1024 * 1024)
    file_parser.add_argument(
        "--approved",
        action="store_true",
        help="setujui overwrite atau delete sesuai operasi",
    )
    file_parser.set_defaults(func=_cmd_file)

    system = sub.add_parser("system", help="kelola package, service, proses, network, storage, hardware")
    system.add_argument("category", choices=("packages", "services", "processes", "network", "storage", "hardware"))
    system.add_argument("operation")
    system.add_argument("args", nargs="*")
    system.add_argument("--lab", help=f"akar lab (default: ${LAB_ENV})")
    system.add_argument("--task-id", default="system-task")
    system.add_argument("--approve", action="store_true")
    system.add_argument("--enable-admin", action="store_true")
    system.add_argument("--admin-duration", type=float, default=900.0)
    system.set_defaults(func=_cmd_system)

    productivity = sub.add_parser("productivity", help="buat dokumen, CSV, atau PPTX lokal")
    productivity.add_argument("kind", choices=("markdown", "csv", "pptx"))
    productivity.add_argument("path")
    productivity.add_argument("--approved", action="store_true", help="setujui overwrite")
    productivity.add_argument("--title", default="Fishing OS")
    productivity.add_argument("--heading", default="Ringkasan")
    productivity.add_argument("--content", default="")
    productivity.add_argument("--headers", default="")
    productivity.add_argument("--rows", default="[]")
    productivity.add_argument("--slides", default="[]")
    productivity.set_defaults(func=_cmd_productivity)

    model = sub.add_parser("model", help="kelola manifest dan status model lokal")
    model.add_argument("operation", choices=("list", "verify", "load", "unload", "status"))
    model.add_argument("model_id", nargs="?")
    model.add_argument("--manifest", required=True, help="berkas manifest JSON model")
    model.add_argument("--lab", help=f"akar lab (default: ${LAB_ENV})")
    model.set_defaults(func=_cmd_model)

    stop = sub.add_parser("stop", help="tulis stop file agar loop berhenti")
    stop.add_argument("--lab", help=f"akar lab (default: ${LAB_ENV})")
    stop.set_defaults(func=_cmd_stop)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except StopRequested as exc:
        print(f"dihentikan: {exc.reason}", file=sys.stderr)
        return EXIT_STOPPED
    except (
        LabError,
        ActionError,
        BackendUnavailable,
        FileOperationError,
        ModelError,
        SystemToolError,
        ProductivityError,
        PathOutsideWorkspace,
        ValueError,
        PermissionError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except FileNotFoundError as exc:
        print(f"error: berkas tidak ditemukan: {exc.filename or exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
