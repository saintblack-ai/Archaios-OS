"""Music strategy and release planning agent."""

from __future__ import annotations

from .base_agent import BaseSaintBlackAgent


class MusicAgent(BaseSaintBlackAgent):
    agent_name = "music_agent"

    def run(self, task: dict) -> dict:
        title = task.get("project", "Untitled Release")
        instructions = task.get("instructions", "")

        content = {
            "release_plan": [
                f"Week 1: Finalize master for {title} and align distribution metadata.",
                "Week 2: Deliver teaser assets and pre-save campaign.",
                "Week 3: Release single and monitor fan feedback loops.",
                "Week 4: Publish remix or acoustic follow-up content.",
            ],
            "hook_ideas": [
                "15-second emotional chorus cut with narrative on-screen text.",
                "Behind-the-scenes creative process mini-series.",
                "Fan duet/stitch call to action around signature lyric.",
            ],
            "social_captions": [
                f"This is chapter one of {title}. The signal is live.",
                "Built this for the late-night dreamers. Pre-save now.",
                "New frequency loaded. Tell me where this track takes you.",
            ],
            "metadata_checklist": [
                "ISRC and UPC confirmed",
                "Primary/featured artist roles verified",
                "Lyrics and explicit flag validated",
                "DSP genre and mood tags reviewed",
            ],
            "notes": instructions,
        }

        return self._base_response(task, content, "Generated release, hooks, captions, and metadata checklist.")
