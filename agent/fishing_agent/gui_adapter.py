"""GUI adapter ringan yang memakai ControlService; tidak memiliki executor sendiri."""

from __future__ import annotations

from typing import Any

from .service import ControlService


class GUIUnavailable(RuntimeError):
    """Toolkit GUI tidak tersedia."""


class GUIAdapter:
    def __init__(self, service: ControlService | None = None) -> None:
        self.service = service or ControlService()
        self.selected_task_id: str | None = None

    def create_task(self, instruction: str, source: str = "gui") -> Any:
        task = self.service.create_task(instruction, source=source)
        self.selected_task_id = task.task_id
        return task

    def approve_selected(self) -> bool:
        if self.selected_task_id is None:
            return False
        self.service.approve(self.selected_task_id)
        return True

    def cancel_selected(self) -> bool:
        if self.selected_task_id is None:
            return False
        self.service.cancel(self.selected_task_id, "gui")
        return True

    def status(self) -> str:
        if self.selected_task_id is None:
            return "ready"
        return self.service.get_task(self.selected_task_id).status.value

    def run(self) -> int:
        try:
            import tkinter as tk
            from tkinter import messagebox
        except ImportError as exc:
            raise GUIUnavailable("Tkinter tidak tersedia pada runtime GUI") from exc

        root = tk.Tk()
        root.title("Fishing OS Assistant")
        entry = tk.Entry(root, width=72)
        entry.pack(padx=12, pady=(12, 6))
        status = tk.Label(root, text="ready")
        status.pack(padx=12, pady=6)

        def create() -> None:
            instruction = entry.get().strip()
            if not instruction:
                messagebox.showerror("Fishing OS Assistant", "Instruksi wajib diisi")
                return
            task = self.create_task(instruction)
            status.config(text=f"{task.task_id}: {task.status.value}")

        def approve() -> None:
            if not self.approve_selected():
                messagebox.showerror("Fishing OS Assistant", "Belum ada task")
                return
            status.config(text=f"{self.selected_task_id}: approved")

        def cancel() -> None:
            if not self.cancel_selected():
                messagebox.showerror("Fishing OS Assistant", "Belum ada task")
                return
            status.config(text=f"{self.selected_task_id}: cancelled")

        tk.Button(root, text="Mulai task", command=create).pack(side=tk.LEFT, padx=(12, 4), pady=12)
        tk.Button(root, text="Setujui", command=approve).pack(side=tk.LEFT, padx=4, pady=12)
        tk.Button(root, text="Hentikan", command=cancel).pack(side=tk.LEFT, padx=4, pady=12)
        root.mainloop()
        return 0


__all__ = ["GUIAdapter", "GUIUnavailable"]
