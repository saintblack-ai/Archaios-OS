"""Streamlit command dashboard for Archaios OS."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import streamlit as st

ROOT_BOOTSTRAP = Path(__file__).resolve().parents[1]
if str(ROOT_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(ROOT_BOOTSTRAP))

from jobs.daily.run_daily import run_daily  # noqa: E402

ROOT_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT_DIR / "logs"
METRICS_FILE = ROOT_DIR / "metrics" / "metrics.json"


def load_json(path: Path, fallback: dict) -> dict:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def list_todays_logs() -> list[dict]:
    today = date.today().isoformat()
    logs = []
    if not LOGS_DIR.exists():
        return logs

    for path in sorted(LOGS_DIR.glob(f"{today}_*.json")):
        try:
            logs.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return logs


def compute_progress(metrics: dict) -> float:
    target_days = int(metrics.get("goal_target_years", 3)) * 365
    days_active = int(metrics.get("days_active", 0))
    if target_days <= 0:
        return 0.0
    return min((days_active / target_days) * 100.0, 100.0)


def render_pr_links() -> None:
    st.subheader("PR Links")
    pr_links = [
        v for k, v in st.secrets.items() if isinstance(v, str) and k.startswith("PR_LINK_") and v.strip()
    ] if hasattr(st, "secrets") else []

    if not pr_links:
        st.info("No PR links configured.")
        return

    for link in pr_links:
        st.markdown(f"- [Pull Request]({link})")


def main() -> None:
    st.set_page_config(page_title="Archaios OS", layout="wide")
    st.title("Archaios OS Command Dashboard")

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

    left, right = st.columns(2)
    with left:
        st.subheader("Metrics")
        st.json(metrics)
    with right:
        progress = compute_progress(metrics)
        st.subheader("3-Year Progress")
        st.progress(progress / 100)
        st.metric("Progress %", f"{progress:.2f}%")

    if st.button("Run Daily Now", type="primary"):
        with st.spinner("Running daily workflow..."):
            result = run_daily()
        st.success("Daily run completed.")
        st.json(result)

    st.subheader("Today's Logs")
    logs = list_todays_logs()
    if not logs:
        st.info("No logs for today yet.")
    else:
        for entry in logs:
            with st.expander(f"{entry.get('agent', 'unknown')} | {entry.get('task_type', 'unknown')}"):
                st.json(entry)

    render_pr_links()


if __name__ == "__main__":
    main()
