"""Configuration helpers for Archaios OS."""

from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT_DIR / "logs"
METRICS_FILE = ROOT_DIR / "metrics" / "metrics.json"


class Settings:
    """Runtime settings loaded from environment variables."""

    archaios_endpoint: str = os.getenv("ARCHAIOS_ENDPOINT", "")
    archaios_token: str = os.getenv("ARCHAIOS_TOKEN", "")
    github_repo_url: str = os.getenv("GITHUB_REPO_URL", "")


settings = Settings()
