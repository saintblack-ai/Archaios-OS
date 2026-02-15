"""Central orchestrator for Archaios OS task execution."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .logger import ArchaiosLogger
from .router import TaskRouter


class ArchaiosOrchestrator:
    """Coordinates task validation, routing, and structured logging.

    The returned schema is intentionally explicit so it can be extended
    for future OpenAI Agents SDK multi-agent handoffs.
    """

    REQUIRED_FIELDS = ("id", "type", "priority", "project", "instructions")

    def __init__(self, router: TaskRouter | None = None, logger: ArchaiosLogger | None = None) -> None:
        self.router = router or TaskRouter()
        self.logger = logger or ArchaiosLogger()

    def run_task(self, task: dict[str, Any]) -> dict[str, Any]:
        validation_error = self._validate_task(task)
        if validation_error:
            error_result = {
                "status": "error",
                "agent": "orchestrator",
                "task_id": task.get("id"),
                "task_type": task.get("type"),
                "summary": validation_error,
                "content": {},
            }
            self.logger.log(agent="orchestrator", task=task, result=error_result)
            return self._envelope(task, error_result)

        agent_result = self.router.dispatch(task)
        log_agent = str(agent_result.get("agent", "unknown"))
        log_path = self.logger.log(agent=log_agent, task=task, result=agent_result)
        return self._envelope(task, agent_result, str(log_path))

    def _validate_task(self, task: dict[str, Any]) -> str | None:
        missing = [field for field in self.REQUIRED_FIELDS if field not in task]
        if missing:
            return f"Missing required fields: {', '.join(missing)}"
        return None

    def _envelope(self, task: dict[str, Any], result: dict[str, Any], log_path: str = "") -> dict[str, Any]:
        return {
            "orchestrator": "ArchaiosOrchestrator",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task": {
                "id": task.get("id"),
                "type": task.get("type"),
                "priority": task.get("priority"),
                "project": task.get("project"),
            },
            "result": result,
            "log_path": log_path,
            "handoff_ready": {
                "compatible_with_openai_agents_sdk": True,
                "handoff_candidates": [],
            },
        }
