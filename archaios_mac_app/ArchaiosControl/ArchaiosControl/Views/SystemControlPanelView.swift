// SystemControlPanelView.swift
// Operational controls to execute daily pipeline, git push, worker deploy, and data refresh actions.

import SwiftUI

struct SystemControlPanelView: View {
    @EnvironmentObject private var state: AppState

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("System Control Panel")
                .font(.title2)
                .fontWeight(.semibold)

            Text("Archaios root: \(state.expandedRootPath)")
                .font(.system(size: 12, design: .monospaced))
                .foregroundColor(.secondary)

            HStack(spacing: 10) {
                Button("Run Daily Pipeline") { state.runDailyPipeline() }
                    .disabled(state.isBusy)
                Button("Push to GitHub") { state.pushToGitHub() }
                    .disabled(state.isBusy)
                Button("Deploy Cloudflare Worker") { state.deployCloudflareWorker() }
                    .disabled(state.isBusy)
            }

            HStack(spacing: 10) {
                Button("View Logs") { state.viewLogsButton() }
                .disabled(state.isBusy)

                Button("Show Metrics") { state.loadMetricsButton() }
                    .disabled(state.isBusy)
            }

            if state.isBusy {
                ProgressView("Running: \(state.busyLabel)")
            }

            if let error = state.lastError {
                Text(error)
                    .foregroundColor(.red)
            }

            ConsoleView(entries: state.console)
            Spacer()
        }
        .padding(16)
    }
}
