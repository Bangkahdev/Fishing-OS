"""Task Orchestrator: instruksi -> rencana -> validasi -> eksekusi -> verifikasi.

Orchestrator adalah komponen inti SRS §3.2 yang sebelumnya belum ada. Ia:

1. Membuat task pada :class:`~fishing_agent.service.ControlService` (state tunggal).
2. Meminta :class:`~fishing_agent.planner.Planner` menghasilkan rencana tool call.
3. **Memvalidasi** setiap langkah terhadap schema :class:`ToolRegistry` dan
   mengecek policy (privilege/approval) **sebelum** ada aksi dijalankan.
4. Mengeksekusi lewat handler tool (command/file/system/productivity) dengan
   konteks runtime yang sama, lalu memverifikasi hasil.
5. Mencatat audit (trace) dan transisi state (planning/executing/verifying/
   completed/failed/cancelled/waiting_for_*), serta menghormati cancellation.

Tidak ada eksekusi langsung dari output model: planner hanya menghasilkan rencana,
dan registry memvalidasi argumen sebelum handler dijalankan (FR-09/FR-10).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .command import CommandExecutor
from .files import FileTool
from .planner import Plan, PlanStep, PlannerError
from .policy import AdministratorMode, ApprovalRequired, Risk
from .registry import StepOutcome, ToolContext, ToolError, ToolNotFound, ToolRegistry, ToolSpec, ToolValidationError
from .service import ControlService, ServiceError
from .stop import StopRequested
from .system import SystemTool
from .task import TaskState


class OrchestratorError(RuntimeError):
    """Orchestrator tidak dapat menjalankan task."""


# Tool yang memerlukan approval bila menimpa berkas yang sudah ada.
_OVERWRITE_TOOLS = {"file.write", "productivity.markdown", "productivity.pptx", "productivity.csv"}
# Tool yang menghasilkan berkas; hasilnya diverifikasi ada setelah eksekusi.
_FILE_PRODUCING = {"file.write", "productivity.markdown", "productivity.pptx", "productivity.csv"}


@dataclass(frozen=True)
class StepResult:
    tool: str
    ok: bool
    summary: str = ""
    output: str = ""
    returncode: int | None = None
    risk: str = Risk.LOW.value
    error: str = ""


@dataclass(frozen=True)
class RunReport:
    task_id: str
    status: TaskState
    plan: Plan | None = None
    steps: list[StepResult] = field(default_factory=list)
    summary: str = ""
    needs_input: bool = False
    clarify: str = ""
    validated: bool = False

    @property
    def ok(self) -> bool:
        return self.status == TaskState.COMPLETED


class _Blocked:
    """Hasil preflight ketika langkah diblokir sebelum eksekusi."""

    def __init__(self, kind: str, message: str) -> None:
        self.kind = kind
        self.message = message


class Orchestrator:
    def __init__(
        self,
        registry: ToolRegistry,
        planner: Any,
        *,
        service: ControlService | None = None,
        lab: Any = None,
        administrator: AdministratorMode | None = None,
        broker: Any = None,
        working_directory: str | None = None,
        dry_run: bool = False,
    ) -> None:
        self.registry = registry
        self.planner = planner
        self.service = service or ControlService()
        self.policy = self.service.policy
        self.administrator = administrator or self.policy.administrator
        self.broker = broker
        self.lab = lab
        self.working_directory = working_directory
        self.dry_run = dry_run

    # -- konteks runtime ------------------------------------------------------

    def _build_context(self, task_id: str, approved: bool, dry_run: bool) -> ToolContext:
        task = self.service.get_task(task_id)
        stop = task.stop
        if self.lab is not None and getattr(stop, "stop_file", None) is None:
            # Gabungkan pembatalan via ControlService dengan stop file lab.
            stop.stop_file = Path(self.lab.stop_file)
        trace = getattr(self.service, "trace", None)
        executor = CommandExecutor(stop, trace)
        return ToolContext(
            policy=self.policy,
            administrator=self.administrator,
            stop=stop,
            trace=trace,
            executor=executor,
            broker=self.broker,
            file_tool=FileTool(),
            system_tool=SystemTool(executor.execute),
            working_directory=self.working_directory,
            dry_run=dry_run,
            approved=approved,
            task_id=task_id,
            lab=self.lab,
        )

    # -- transisi & audit -----------------------------------------------------

    def _transition(self, task_id: str, state: TaskState) -> None:
        try:
            self.service.transition(task_id, state)
        except ServiceError:
            # transisi tidak valid (mis. dari state terminal) -> jangan crash
            pass

    def _audit(self, context: ToolContext, action: str, parameters: dict[str, Any] | None = None, *, status: str = "ok", note: str = "", perception: str = "orchestrator") -> None:
        context.emit(action, parameters, status=status, note=note, perception=perception)

    # -- preflight ------------------------------------------------------------

    def _effective_privilege(self, spec: ToolSpec, arguments: dict[str, Any]) -> str:
        if spec.name == "command.run":
            return str(arguments.get("privilege", "user"))
        return spec.privilege

    def _target_of(self, spec: ToolSpec, arguments: dict[str, Any]) -> Path | None:
        raw = arguments.get("path")
        if not isinstance(raw, str) or not raw:
            return None
        candidate = Path(raw).expanduser()
        if not candidate.is_absolute():
            # Selaraskan dengan FileTool.resolve/produktivitas yang memakai CWD.
            candidate = Path.cwd() / candidate
        return candidate

    def _preflight(self, task_id: str, plan: Plan, context: ToolContext) -> _Blocked | PlanStep | None:
        """Validasi + policy seluruh langkah. Kembalikan _Blocked bila perlu approval/auth."""
        for step in plan.steps:
            try:
                spec = self.registry.get(step.tool)
            except ToolNotFound as exc:
                raise OrchestratorError(f"tool tidak terdaftar: {step.tool}") from exc
            try:
                arguments = spec.validate(step.arguments)
            except ToolValidationError as exc:
                raise OrchestratorError(f"langkah '{step.tool}' tidak valid: {exc}") from exc
            privilege = self._effective_privilege(spec, arguments)
            if privilege == "elevated":
                if self.broker is None:
                    return _Blocked("authentication", f"langkah '{step.tool}' butuh Privilege Broker (jalankan broker-serve dan hubungkan socket)")
                if not self.administrator.active:
                    return _Blocked("authentication", f"langkah '{step.tool}' butuh Administrator Mode (autentikasi native OS)")
            risk = spec.risk_for(arguments, context)
            needs_approval = risk == Risk.HIGH
            reasons: list[str] = []
            if needs_approval:
                reasons.append("operasi berisiko tinggi")
            if spec.name in _OVERWRITE_TOOLS:
                target = self._target_of(spec, arguments)
                if target is not None and target.exists() and not context.approved:
                    needs_approval = True
                    reasons.append(f"menimpa berkas yang sudah ada: {target}")
            if needs_approval and not context.approved:
                detail = ", ".join(reasons)
                return _Blocked("approval", f"langkah '{step.tool}' memerlukan approval ({detail})")
        return None

    # -- eksekusi -------------------------------------------------------------

    def run(
        self,
        instruction: str,
        *,
        task_id: str | None = None,
        approved: bool = False,
        dry_run: bool | None = None,
    ) -> RunReport:
        if dry_run is None:
            dry_run = self.dry_run
        task = self.service.create_task(instruction, source="orchestrator", task_id=task_id)
        tid = task.task_id
        if approved:
            self.service.approve(tid)
        context = self._build_context(tid, approved, dry_run)

        # 1) Perencanaan (task masih READY)
        try:
            plan = self.planner.plan(instruction, context)
        except PlannerError as exc:
            self._transition(tid, TaskState.FAILED)
            return RunReport(task_id=tid, status=TaskState.FAILED, summary=f"perencanaan gagal: {exc}")

        self._audit(context, "plan", plan.to_dict(), perception="planner")
        if plan.needs_input or not plan.steps:
            return RunReport(
                task_id=tid,
                status=TaskState.READY,
                plan=plan,
                summary=plan.summary or "instruksi belum dapat dipetakan",
                needs_input=True,
                clarify=plan.clarify,
            )

        self._transition(tid, TaskState.PLANNING)

        # 2) Preflight: validasi + policy sebelum aksi apa pun
        try:
            blocked = self._preflight(tid, plan, context)
        except OrchestratorError as exc:
            self._transition(tid, TaskState.FAILED)
            self._audit(context, "plan_rejected", {"error": str(exc)}, status="error", note=str(exc))
            return RunReport(task_id=tid, status=TaskState.FAILED, plan=plan, summary=str(exc))

        if blocked is not None:
            if blocked.kind == "approval":
                self._transition(tid, TaskState.WAITING_FOR_APPROVAL)
            else:
                self._transition(tid, TaskState.WAITING_FOR_AUTHENTICATION)
            self._audit(context, "blocked", {"kind": blocked.kind, "reason": blocked.message}, status="blocked", note=blocked.message)
            return RunReport(task_id=tid, status=task.status, plan=plan, summary=blocked.message)

        if dry_run:
            self._audit(context, "dry_run", {"steps": len(plan.steps)}, note="rencana valid, tidak dieksekusi")
            return RunReport(task_id=tid, status=TaskState.PLANNING, plan=plan, summary="dry-run: rencana valid, tidak dieksekusi", validated=True)

        # 3) Eksekusi
        self._transition(tid, TaskState.EXECUTING)
        results: list[StepResult] = []
        produced: list[Path] = []
        try:
            for step in plan.steps:
                context.stop.check()
                spec = self.registry.get(step.tool)
                arguments = spec.validate(step.arguments)
                risk = spec.risk_for(arguments, context)
                try:
                    outcome: StepOutcome = self.registry.dispatch(step.tool, step.arguments, context)
                except StopRequested:
                    raise
                except (ToolError, ApprovalRequired, PermissionError, FileNotFoundError, OSError, ValueError) as exc:
                    self._transition(tid, TaskState.FAILED)
                    self._audit(context, step.tool, {"arguments": arguments}, status="error", note=str(exc))
                    results.append(StepResult(step.tool, False, summary=f"gagal: {exc}", error=str(exc), risk=risk.value))
                    return RunReport(task_id=tid, status=TaskState.FAILED, plan=plan, steps=results, summary=f"langkah '{step.tool}' gagal: {exc}")
                results.append(
                    StepResult(
                        tool=step.tool,
                        ok=outcome.ok,
                        summary=outcome.summary,
                        output=outcome.output,
                        returncode=outcome.returncode,
                        risk=risk.value,
                    )
                )
                self._audit(context, step.tool, {"arguments": arguments, "ok": outcome.ok, "summary": outcome.summary}, status="ok" if outcome.ok else "failed")
                if not outcome.ok:
                    self._transition(tid, TaskState.FAILED)
                    return RunReport(task_id=tid, status=TaskState.FAILED, plan=plan, steps=results, summary=f"langkah '{step.tool}' tidak berhasil: {outcome.summary}")
                target = self._target_of(spec, arguments)
                if spec.name in _FILE_PRODUCING and target is not None:
                    produced.append(target)
        except StopRequested as exc:
            self._transition(tid, TaskState.CANCELLED)
            self._audit(context, "stop", {"reason": exc.reason}, status="stopped", note=exc.reason)
            return RunReport(task_id=tid, status=TaskState.CANCELLED, plan=plan, steps=results, summary=f"dihentikan: {exc.reason}")

        # 4) Verifikasi
        self._transition(tid, TaskState.VERIFYING)
        missing = [str(path) for path in produced if not path.exists()]
        if missing:
            self._transition(tid, TaskState.FAILED)
            self._audit(context, "verify", {"missing": missing}, status="error", note="berkas hasil tidak ditemukan")
            return RunReport(task_id=tid, status=TaskState.FAILED, plan=plan, steps=results, summary=f"verifikasi gagal, berkas tidak ada: {missing}")
        self._transition(tid, TaskState.COMPLETED)
        summary = self._summarize(results)
        self._audit(context, "completed", {"steps": len(results)}, note=summary)
        return RunReport(task_id=tid, status=TaskState.COMPLETED, plan=plan, steps=results, summary=summary, validated=True)

    @staticmethod
    def _summarize(results: list[StepResult]) -> str:
        if not results:
            return "tidak ada langkah dijalankan"
        return "; ".join(f"{item.tool}: {item.summary}" for item in results)


__all__ = ["Orchestrator", "OrchestratorError", "RunReport", "StepResult"]