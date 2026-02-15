"""Creative visual direction agent."""

from __future__ import annotations

from .base_agent import BaseSaintBlackAgent


class ArtAgent(BaseSaintBlackAgent):
    agent_name = "art_agent"

    def run(self, task: dict) -> dict:
        project = task.get("project", "Campaign")
        content = {
            "visual_concept_prompts": [
                f"Create a cinematic portrait series for {project} with dramatic rim lighting.",
                "Design high-contrast editorial layouts with minimalist typography.",
                "Generate motion poster concepts focused on symbolic storytelling.",
            ],
            "cover_direction": {
                "palette": ["charcoal", "silver", "amber"],
                "composition": "Centered subject with asymmetrical negative space.",
                "typography": "Condensed sans serif, uppercase, high tracking.",
            },
            "brand_consistency_checks": [
                "Logo safe area maintained in all formats",
                "Color palette matches official brand tokens",
                "Tone aligns with existing campaign narrative",
            ],
        }
        return self._base_response(task, content, "Prepared visual prompts, cover direction, and brand checks.")
