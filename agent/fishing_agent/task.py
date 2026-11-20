"""State machine task bersama untuk interface GUI dan CLI/TUI."""

from __future__ import annotations

from enum import Enum


class TaskState(str, Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    READY = "ready"
    PLANNING = "planning"
    WAITING_FOR_AUTHENTICATION = "waiting_for_authentication"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InvalidTransition(RuntimeError):
    """Perubahan state task tidak valid."""


_TERMINAL = {TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED, TaskState.STOPPED}


class TaskStateMachine:
    _allowed = {
        TaskState.STOPPED: {TaskState.STARTING},
        TaskState.STARTING: {TaskState.READY, TaskState.FAILED, TaskState.CANCELLED},
        TaskState.READY: {TaskState.PLANNING, TaskState.CANCELLED},
        TaskState.PLANNING: {TaskState.WAITING_FOR_AUTHENTICATION, TaskState.WAITING_FOR_APPROVAL, TaskState.EXECUTING, TaskState.FAILED, TaskState.CANCELLED},
        TaskState.WAITING_FOR_AUTHENTICATION: {TaskState.EXECUTING, TaskState.FAILED, TaskState.CANCELLED},
        TaskState.WAITING_FOR_APPROVAL: {TaskState.EXECUTING, TaskState.FAILED, TaskState.CANCELLED},
        TaskState.EXECUTING: {TaskState.VERIFYING, TaskState.FAILED, TaskState.CANCELLED},
        TaskState.VERIFYING: {TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED},
    }

    def __init__(self) -> None:
        self.state = TaskState.STOPPED

    def transition(self, state: TaskState) -> TaskState:
        if self.state in _TERMINAL and self.state != TaskState.STOPPED:
            raise InvalidTransition(f"task terminal: {self.state.value}")
        if state not in self._allowed.get(self.state, set()):
            raise InvalidTransition(f"{self.state.value} -> {state.value} tidak diizinkan")
        self.state = state
        return state


__all__ = ["InvalidTransition", "TaskState", "TaskStateMachine"]
