"""Task router for Archaios OS agents."""

from __future__ import annotations

from typing import Callable

from agents.qx.legacy_agent import LegacyAgent
from agents.qx.nanotech_agent import NanotechAgent
from agents.qx.quantum_agent import QuantumAgent
from agents.qx.security_agent import SecurityAgent
from agents.saintblack.art_agent import ArtAgent
from agents.saintblack.film_agent import FilmAgent
from agents.saintblack.music_agent import MusicAgent
from agents.saintblack.pr_agent import PRAgent
from agents.saintblack.publishing_agent import PublishingAgent

AgentFactory = Callable[[], object]


class TaskRouter:
    """Resolves task types to agent implementations."""

    _agent_map: dict[str, AgentFactory] = {
        "music": MusicAgent,
        "art": ArtAgent,
        "film": FilmAgent,
        "pr": PRAgent,
        "publish": PublishingAgent,
        "qx_quantum": QuantumAgent,
        "qx_nanotech": NanotechAgent,
        "qx_security": SecurityAgent,
        "qx_legacy": LegacyAgent,
    }

    def dispatch(self, task: dict) -> dict:
        task_type = str(task.get("type", "")).strip()
        if task_type not in self._agent_map:
            return {
                "status": "error",
                "agent": "router",
                "task_id": task.get("id"),
                "task_type": task_type,
                "summary": f"Unsupported task type: {task_type}",
                "content": {"supported_types": sorted(self._agent_map.keys())},
            }

        agent = self._agent_map[task_type]()
        return agent.run(task)
