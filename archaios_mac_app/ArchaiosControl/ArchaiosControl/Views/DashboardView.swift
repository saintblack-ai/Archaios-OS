// DashboardView.swift
// Summary dashboard with high-level metrics and quick task controls.

import SwiftUI

struct DashboardView: View {
    @EnvironmentObject private var state: AppState

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                Text("Dashboard")
                    .font(.title2)
                    .fontWeight(.semibold)
                Spacer()
                Button("Refresh") { state.refreshDashboard() }
                    .disabled(state.isBusy)
            }

            if let error = state.lastError {
                Text(error)
                    .foregroundColor(.red)
            }

            HStack(spacing: 12) {
                metricCard("Daily Tasks", value: "\(state.metrics.dailyTasksCompleted)")
                metricCard("Music Releases", value: "\(state.metrics.musicReleases)")
                metricCard("Content Posts", value: "\(state.metrics.contentPosts)")
                metricCard("QX Updates", value: "\(state.metrics.qxUpdates)")
            }

            GroupBox("3-Year Progress") {
                VStack(alignment: .leading, spacing: 8) {
                    ProgressView(value: state.metrics.progressPercent / 100.0)
                    Text(String(format: "%.2f%% complete", state.metrics.progressPercent))
                        .foregroundColor(.secondary)
                }
            }

            HStack(spacing: 10) {
                Button("Run Daily Pipeline") { state.runDailyPipeline() }
                    .disabled(state.isBusy)
                Button("Push to GitHub") { state.pushToGitHub() }
                    .disabled(state.isBusy)
                Button("Deploy Cloudflare Worker") { state.deployCloudflareWorker() }
                    .disabled(state.isBusy)
            }

            if state.isBusy {
                ProgressView("Running: \(state.busyLabel)")
            }

            ConsoleView(entries: state.console)
            Spacer()
        }
        .padding(16)
        .task {
            state.refreshDashboard()
        }
    }

    @ViewBuilder
    private func metricCard(_ title: String, value: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value)
                .font(.title3)
                .fontWeight(.bold)
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(nsColor: .windowBackgroundColor))
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color.gray.opacity(0.25), lineWidth: 1)
        )
        .cornerRadius(8)
    }
}
