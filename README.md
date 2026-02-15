# Archaios OS

Archaios OS is a production-oriented monorepo for creative + technical agent orchestration, daily automation, and command dashboard visibility.

## Repository Structure
- `archaios_core/`: orchestrator, router, logger, config.
- `agents/`: Saint Black and QX agent implementations.
- `jobs/daily/`: scheduled run pipeline and task plans.
- `dashboard/`: Streamlit command UI.
- `cloudflare_worker/`: cron-triggered remote invocation worker.
- `metrics/`: progress tracking.
- `logs/`: structured run logs.

## Local Setup
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install streamlit
   ```
3. Copy env file and configure values:
   ```bash
   cp .env.example .env
   ```

## Environment Variables
- `ARCHAIOS_ENDPOINT`: endpoint for daily trigger integration.
- `ARCHAIOS_TOKEN`: bearer token for secure calls.
- `GITHUB_REPO_URL`: repository URL for system metadata.
- `PR_LINK_*`: optional PR URLs rendered in dashboard.

## Run Dashboard
```bash
streamlit run dashboard/streamlit_app.py
```

## Run Daily Job Manually
```bash
python jobs/daily/run_daily.py
```

## Automation Flow
1. Daily runner loads `jobs/daily/plans/daily_plan_template.json`.
2. `ArchaiosOrchestrator` validates + routes each task.
3. Agents generate structured draft outputs.
4. Logger writes one JSON file per task to `logs/`.
5. Metrics are updated in `metrics/metrics.json`.
6. GitHub Action commits log + metric deltas.

## Cloudflare Worker Deployment
1. Install Wrangler and authenticate:
   ```bash
   npm install -g wrangler
   wrangler login
   ```
2. From `cloudflare_worker/`, set secure secret:
   ```bash
   wrangler secret put ARCHAIOS_TOKEN
   ```
3. Update `ARCHAIOS_ENDPOINT` in `wrangler.toml`.
4. Deploy:
   ```bash
   wrangler deploy
   ```

## GitHub Workflows
- `archaios_daily.yml`: runs daily at 05:00 UTC and on manual dispatch.
- `codex_pr_review.yml`: runs Codex review on pull requests and posts summary comment.
