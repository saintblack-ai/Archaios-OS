"""Daily execution pipeline for Archaios OS."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT_BOOTSTRAP = Path(__file__).resolve().parents[2]
if str(ROOT_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(ROOT_BOOTSTRAP))

from archaios_core.config import METRICS_FILE, ROOT_DIR  # noqa: E402
from archaios_core.orchestrator import ArchaiosOrchestrator  # noqa: E402

PLAN_PATH = ROOT_DIR / "jobs" / "daily" / "plans" / "daily_plan_template.json"
LAST_RUN_FILE = ROOT_DIR / "metrics" / "last_run_date.txt"
OUTPUT_PATH = ROOT_DIR / "jobs" / "daily" / "daily_results.json"


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def update_metrics(metrics: dict[str, Any], task_type: str) -> None:
    metrics["daily_tasks_completed"] = int(metrics.get("daily_tasks_completed", 0)) + 1

    if task_type == "music":
        metrics["music_releases"] = int(metrics.get("music_releases", 0)) + 1
    if task_type in {"publish", "pr", "film", "art", "music"}:
        metrics["content_posts"] = int(metrics.get("content_posts", 0)) + 1
    if task_type.startswith("qx_"):
        metrics["qx_updates"] = int(metrics.get("qx_updates", 0)) + 1


def update_days_active(metrics: dict[str, Any]) -> None:
    today = date.today().isoformat()
    last_run = LAST_RUN_FILE.read_text(encoding="utf-8").strip() if LAST_RUN_FILE.exists() else ""
    if last_run != today:
        metrics["days_active"] = int(metrics.get("days_active", 0)) + 1
        LAST_RUN_FILE.write_text(today, encoding="utf-8")


def run_daily() -> dict[str, Any]:
    orchestrator = ArchaiosOrchestrator()
    plan = load_json(PLAN_PATH, {"tasks": []})
    metrics = load_json(
        METRICS_FILE,
        {
            "daily_tasks_completed": 0,
            "music_releases": 0,
            "content_posts": 0,
            "qx_updates": 0,
            "days_active": 0,
            "goal_target_years": 3,
        },
    )

    tasks = plan.get("tasks", [])
    results: list[dict[str, Any]] = []

    for task in tasks:
        run_result = orchestrator.run_task(task)
        results.append(run_result)
        update_metrics(metrics, str(task.get("type", "")))

    update_days_active(metrics)

    save_json(METRICS_FILE, metrics)
    output = {
        "date": date.today().isoformat(),
        "tasks_executed": len(tasks),
        "results": results,
        "metrics": metrics,
    }
    save_json(OUTPUT_PATH, output)
    return output


if __name__ == "__main__":
    result = run_daily()
    print(json.dumps(result, indent=2))
