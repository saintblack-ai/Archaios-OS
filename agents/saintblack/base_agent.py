"""Base classes and helpers for Saint Black agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseSaintBlackAgent(ABC):
    """Common base for all Saint Black domain agents."""

    agent_name = "saintblack_base"

    @abstractmethod
    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        """Run the agent with the provided task payload."""

    def _base_response(self, task: dict[str, Any], content: dict[str, Any], summary: str) -> dict[str, Any]:
        return {
            "status": "success",
            "agent": self.agent_name,
            "task_id": task.get("id"),
            "task_type": task.get("type"),
            "project": task.get("project"),
            "summary": summary,
            "content": content,
            "requires_human_approval": bool(content.get("approval_required", False)),
        }
