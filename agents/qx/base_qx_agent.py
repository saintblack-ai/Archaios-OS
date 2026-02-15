"""Base classes and helpers for QX Technology agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseQXAgent(ABC):
    """Base class for QX technical agents."""

    agent_name = "qx_base"

    @abstractmethod
    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        """Run the QX agent with the provided task."""

    def _base_response(self, task: dict[str, Any], content: dict[str, Any], summary: str) -> dict[str, Any]:
        return {
            "status": "success",
            "agent": self.agent_name,
            "task_id": task.get("id"),
            "task_type": task.get("type"),
            "project": task.get("project"),
            "summary": summary,
            "content": content,
            "requires_human_approval": False,
        }
