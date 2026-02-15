# Archaios OS System Blueprint

## Purpose
Archaios OS is a unified orchestration platform for Saint Black creative operations and QX Technology technical operations.

## Core Components
- `archaios_core/orchestrator.py`: validates task payloads, routes execution, logs structured runs, and returns handoff-ready envelopes.
- `archaios_core/router.py`: maps task types to domain agents.
- `agents/saintblack/*`: creative production strategy agents.
- `agents/qx/*`: technology research, security, and legacy management agents.
- `jobs/daily/run_daily.py`: daily task automation pipeline with metrics updates.
- `dashboard/streamlit_app.py`: command dashboard for logs, metrics, and manual triggers.
- `cloudflare_worker/*`: external scheduled trigger that can call an API endpoint.

## Task Contract
Every task payload must include:
- `id`
- `type`
- `priority`
- `project`
- `instructions`

## Observability
- Structured logs are persisted per task run in `logs/`.
- Operational metrics are tracked in `metrics/metrics.json`.
- Daily pipeline result snapshots are stored in `jobs/daily/daily_results.json`.

## Governance
- Secrets are environment-based only.
- Public content from agents is always draft-first.
- Major platform changes should be PR-based.
