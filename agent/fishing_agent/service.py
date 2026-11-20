"""Control plane lokal bersama untuk CLI, TUI, dan GUI Fishing OS."""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .policy import PolicyGate
from .stop import StopController
from .task import InvalidTransition, TaskState, TaskStateMachine
from .trace import TraceWriter


class ServiceError(RuntimeError):
    """Operasi control service tidak valid."""


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


@dataclass
class TaskRecord:
    task_id: str
    source: str
    instruction: str
    state: TaskStateMachine = field(default_factory=TaskStateMachine)
    stop: StopController = field(default_factory=StopController)
    events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def status(self) -> TaskState:
        return self.state.state


class ControlService:
    """State tunggal task dan policy; executor tetap dipanggil oleh service."""

    def __init__(
        self,
        trace: TraceWriter | None = None,
        policy: PolicyGate | None = None,
    ) -> None:
        self.trace = trace
        self.policy = policy or PolicyGate()
        self._tasks: dict[str, TaskRecord] = {}
        self._lock = threading.RLock()

    def create_task(self, instruction: str, *, source: str = "cli", task_id: str | None = None) -> TaskRecord:
        if not instruction.strip():
            raise ServiceError("instruction wajib diisi")
        with self._lock:
            identifier = task_id or str(uuid.uuid4())
            if identifier in self._tasks:
                raise ServiceError(f"task sudah ada: {identifier}")
            task = TaskRecord(identifier, source, instruction)
            task.stop = StopController()
            task.state.transition(TaskState.STARTING)
            task.state.transition(TaskState.READY)
            self._tasks[identifier] = task
            self._event(task, "created", {"instruction": instruction})
            return task

    def get_task(self, task_id: str) -> TaskRecord:
        with self._lock:
            try:
                return self._tasks[task_id]
            except KeyError as exc:
                raise ServiceError(f"task tidak ditemukan: {task_id}") from exc

    def list_tasks(self) -> list[TaskRecord]:
        with self._lock:
            return list(self._tasks.values())

    def transition(self, task_id: str, state: TaskState) -> TaskState:
        with self._lock:
            task = self.get_task(task_id)
            try:
                result = task.state.transition(state)
            except InvalidTransition as exc:
                raise ServiceError(str(exc)) from exc
            self._event(task, "state", {"state": result.value})
            return result

    def approve(self, task_id: str) -> None:
        self.get_task(task_id)
        self.policy.approve(task_id)
        self._event(self.get_task(task_id), "approval", {})

    def cancel(self, task_id: str, reason: str = "manual") -> None:
        with self._lock:
            task = self.get_task(task_id)
            task.stop.request_stop(reason)
            if task.status not in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED, TaskState.STOPPED):
                try:
                    task.state.transition(TaskState.CANCELLED)
                except InvalidTransition:
                    pass
            self._event(task, "cancellation", {"reason": reason})

    def _event(self, task: TaskRecord, action: str, parameters: dict[str, Any]) -> None:
        event = {"timestamp": _timestamp(), "task_id": task.task_id, "action": action, "parameters": parameters}
        task.events.append(event)
        if self.trace is not None:
            self.trace.write(perception="control service", action=action, parameters=event)


__all__ = ["ControlService", "ServiceError", "TaskRecord"]
