"""TUI/stdin adapter yang memakai ControlService sebagai control plane."""

from __future__ import annotations

import sys
from collections.abc import Iterable
from typing import TextIO

from .service import ControlService


class TUI:
    def __init__(self, service: ControlService | None = None) -> None:
        self.service = service or ControlService()

    def run(
        self,
        lines: Iterable[str] | None = None,
        *,
        input_stream: TextIO = sys.stdin,
        output: TextIO = sys.stdout,
    ) -> int:
        self._print_help(output)
        for raw in lines if lines is not None else input_stream:
            line = raw.strip()
            if not line:
                continue
            if line in ("quit", "exit"):
                return 0
            if not self.execute(line, output):
                return 1
        return 0

    def execute(self, line: str, output: TextIO = sys.stdout) -> bool:
        parts = line.split(maxsplit=1)
        command = parts[0].lower()
        argument = parts[1].strip() if len(parts) == 2 else ""
        if command in ("help", "?"):
            self._print_help(output)
        elif command == "list":
            for task in self.service.list_tasks():
                print(f"{task.task_id}\t{task.status.value}\t{task.instruction}", file=output)
        elif command == "task" and argument:
            task = self.service.create_task(argument, source="tui")
            print(f"{task.task_id}\t{task.status.value}", file=output)
        elif command == "status" and argument:
            task = self.service.get_task(argument)
            print(f"{task.task_id}\t{task.status.value}", file=output)
        elif command == "approve" and argument:
            self.service.approve(argument)
            print(f"{argument}\tapproved", file=output)
        elif command == "cancel" and argument:
            self.service.cancel(argument, "tui")
            print(f"{argument}\tcancelled", file=output)
        elif command in ("quit", "exit"):
            return False
        else:
            print("perintah tidak valid", file=output)
            return False
        return True

    @staticmethod
    def _print_help(output: TextIO) -> None:
        print("task <instruksi> | list | status <id> | approve <id> | cancel <id> | quit", file=output)


__all__ = ["TUI"]
