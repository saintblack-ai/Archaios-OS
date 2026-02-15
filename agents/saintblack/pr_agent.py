"""Public relations planning and outreach agent."""

from __future__ import annotations

from .base_agent import BaseSaintBlackAgent


class PRAgent(BaseSaintBlackAgent):
    agent_name = "pr_agent"

    def run(self, task: dict) -> dict:
        project = task.get("project", "New Release")
        content = {
            "press_release_draft": (
                f"FOR IMMEDIATE RELEASE: {project} launches with a bold cross-platform campaign "
                "highlighting innovation, artistry, and audience-first storytelling."
            ),
            "outreach_email_template": {
                "subject": f"Story Opportunity: {project}",
                "body": (
                    "Hi [Name],\n\n"
                    f"We are sharing advance materials for {project}. "
                    "Happy to coordinate interview windows and exclusive assets.\n\n"
                    "Best,\nArchaios OS PR"
                ),
            },
            "media_target_suggestions": [
                "Culture and music editorial outlets",
                "Independent filmmaker publications",
                "Industry newsletters and creator podcasts",
            ],
        }
        return self._base_response(task, content, "Drafted press release, outreach email, and media targets.")
