"""Structured JSON logger for Archaios OS tasks."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import LOGS_DIR


class ArchaiosLogger:
    """Writes deterministic JSON log files for every task run."""

    def __init__(self, logs_dir: Path | None = None) -> None:
        self.logs_dir = logs_dir or LOGS_DIR
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def log(self, *, agent: str, task: dict[str, Any], result: dict[str, Any]) -> Path:
        """Persist a task result to logs/YYYY-MM-DD_<agent>_<id>.json."""
        now = datetime.now(timezone.utc)
        task_id = str(task.get("id", "unknown"))
        task_type = str(task.get("type", "unknown"))

        log_payload = {
            "timestamp": now.isoformat(),
            "agent": agent,
            "task_id": task_id,
            "task_type": task_type,
            "priority": task.get("priority", "normal"),
            "project": task.get("project", "unknown"),
            "instructions": task.get("instructions", ""),
            "output_summary": result.get("summary", ""),
            "result": result,
        }

        file_name = f"{now.date().isoformat()}_{agent}_{task_id}.json"
        log_path = self.logs_dir / file_name
        log_path.write_text(json.dumps(log_payload, indent=2), encoding="utf-8")
        return log_path
