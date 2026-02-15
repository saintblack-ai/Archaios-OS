# ArchaiosControl (macOS)

Native SwiftUI control dashboard for local Archaios OS operations.

## Location
This app project is generated at:

`archaios_mac_app/ArchaiosControl`

## Integration Assumption
The app assumes Archaios OS root is:

`~/Library/Mobile Documents/com~apple~CloudDocs/QX Technology 2019/Archaios OS`

This path is used when executing all shell tasks.

## Features
- Dashboard
  - Shows high-level metrics
  - Shows 3-year progress
  - Quick action buttons
- System Control Panel
  - Run Daily Pipeline
  - Push to GitHub
  - Deploy Cloudflare Worker
  - View Logs
  - Show Metrics
- Logs & Metrics Viewer
  - Lists log files in `logs/`
  - Shows selected log contents
  - Displays `metrics/metrics.json` (pretty JSON)
- Scrollable command console
  - Captures command text, stdout, stderr, and exit codes

## Shell Commands Triggered
- Run Daily Pipeline:
  - `python3 jobs/daily/run_daily.py`
- Push to GitHub:
  - `git add .`
  - `git commit -m "update" || true`
  - `git push`
- Deploy Cloudflare Worker:
  - `wrangler deploy` in `cloudflare_worker/`
- View Logs:
  - `ls -1 logs`
  - `cat logs/<selected file>`
- Show Metrics:
  - `cat metrics/metrics.json`

## Build and Run
1. Open `ArchaiosControl.xcodeproj` in Xcode.
2. Select `ArchaiosControl` scheme.
3. Build and run on macOS.

Requirements:
- Xcode with macOS SDK 13+
- Swift 5.9+
- Local tools in PATH: `python3`, `git`, `wrangler`

## Folder Structure
```text
archaios_mac_app/
  ArchaiosControl/
    ArchaiosControl.xcodeproj/
    ArchaiosControl/
      ArchaiosControlApp.swift
      ContentView.swift
      Models/
        AppState.swift
        Models.swift
      Services/
        ShellHelper.swift
      Views/
        DashboardView.swift
        SystemControlPanelView.swift
        LogsMetricsView.swift
        ConsoleView.swift
      Assets.xcassets/
    README.md
```

## Error Handling
- Non-zero command exits are reported in the UI.
- stderr and stdout are both shown in the console.
- Busy state prevents overlapping command execution.
